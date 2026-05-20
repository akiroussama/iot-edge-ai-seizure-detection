from __future__ import annotations

from collections.abc import Iterable
from hashlib import blake2b

import numpy as np
import pandas as pd

from src.utils.time import ensure_datetime

NULL_MODELS = {
    "split_prevalence_prior",
    "rate_matched_random",
    "patient_prior",
    "cycle_preserving_random",
}

APPENDED_COLUMNS = [
    "risk_score",
    "alarm",
    "null_model",
    "null_model_variant",
    "score_fit_split",
    "threshold_source_split",
    "target_tiw",
    "seed",
]

FORBIDDEN_SIGNAL_COLUMNS = {
    "time_to_next_seizure_seconds",
    "time_since_last_seizure_seconds",
    "is_right_censored",
    "right_censoring_applied",
}

REQUIRED_COLUMNS = {
    "patient_id",
    "recording_id",
    "window_start",
    "window_end",
    "forecast_label",
    "is_excluded",
}


def derive_model_seed(seed: int, null_model: str) -> int:
    """Derive a stable per-model RNG seed from a user seed.

    If a future wrapper runs several null models with the same CLI ``--seed``,
    each model still receives an independent deterministic stream. This avoids
    accidental RNG coupling across model outputs.
    """
    if null_model not in NULL_MODELS:
        raise ValueError(f"unknown null model: {null_model}")
    digest = blake2b(f"{int(seed)}:{null_model}".encode("utf-8"), digest_size=8).digest()
    return int.from_bytes(digest, "little") % (2**32)


def _validate_common_inputs(
    labels: pd.DataFrame,
    fit_split: str,
    threshold_split: str,
    target_tiw: float,
    split_col: str,
) -> None:
    missing = sorted(REQUIRED_COLUMNS - set(labels.columns))
    if missing:
        raise ValueError(f"labels table missing required columns: {missing}")
    if split_col not in labels.columns:
        raise ValueError(f"labels table must contain split column {split_col!r}")
    collisions = [col for col in APPENDED_COLUMNS if col in labels.columns]
    if collisions:
        raise ValueError(f"labels table already contains output columns: {collisions}")
    if not 0 <= target_tiw <= 1:
        raise ValueError("target_tiw must be in [0, 1]")
    valid = _valid_mask(labels)
    if not (valid & labels[split_col].astype(str).eq(fit_split)).any():
        raise ValueError(f"fit split {fit_split!r} has no valid non-excluded rows")
    if not (valid & labels[split_col].astype(str).eq(threshold_split)).any():
        raise ValueError(f"threshold split {threshold_split!r} has no valid non-excluded rows")


def _valid_mask(df: pd.DataFrame) -> pd.Series:
    return ~df["is_excluded"].fillna(False).astype(bool)


def _split_mask(df: pd.DataFrame, split_col: str, split: str) -> pd.Series:
    return df[split_col].astype(str).eq(split)


def _fit_rows(labels: pd.DataFrame, split_col: str, fit_split: str) -> pd.DataFrame:
    return labels.loc[_valid_mask(labels) & _split_mask(labels, split_col, fit_split)].copy()


def _threshold_rows(preds: pd.DataFrame, split_col: str, threshold_split: str) -> pd.DataFrame:
    return preds.loc[_valid_mask(preds) & _split_mask(preds, split_col, threshold_split)].copy()


def _positive_rate(rows: pd.DataFrame) -> float:
    if rows.empty:
        raise ValueError("cannot compute positive rate from empty rows")
    return float(rows["forecast_label"].fillna(False).astype(bool).mean())


def _append_metadata(
    labels: pd.DataFrame,
    *,
    risk_score: pd.Series,
    alarm: pd.Series,
    null_model: str,
    null_model_variant: pd.Series | str,
    fit_split: str,
    threshold_split: str,
    target_tiw: float,
    model_seed: int,
) -> pd.DataFrame:
    out = labels.copy()
    out["risk_score"] = risk_score.reindex(out.index).fillna(0.0).astype(float).clip(0.0, 1.0)
    out["alarm"] = alarm.reindex(out.index).fillna(False).astype(bool)
    out.loc[~_valid_mask(out), "alarm"] = False
    out["null_model"] = null_model
    if isinstance(null_model_variant, str):
        out["null_model_variant"] = null_model_variant
    else:
        out["null_model_variant"] = null_model_variant.reindex(out.index).fillna(null_model).astype(str)
    out["score_fit_split"] = fit_split
    out["threshold_source_split"] = threshold_split
    out["target_tiw"] = float(target_tiw)
    out["seed"] = int(model_seed)
    return out


def _target_alarm_count(n_rows: int, target_tiw: float) -> int:
    if n_rows <= 0:
        return 0
    if target_tiw <= 0:
        return 0
    if target_tiw >= 1:
        return n_rows
    return int(round(target_tiw * n_rows))


def _target_tiw_alarm_mask(
    labels: pd.DataFrame,
    risk_score: pd.Series,
    *,
    split_col: str,
    threshold_split: str,
    target_tiw: float,
    model_seed: int,
    allow_zero_score_alarms: bool,
) -> pd.Series:
    """Select alarms using only the threshold split to set the warning budget.

    Sorting is lexicographic: higher risk first, then deterministic random
    tie-breakers from the model-specific RNG stream. This makes constant-risk
    null models useful for alarm-rate comparisons without corrupting their
    probability score.
    """
    valid = _valid_mask(labels)
    calibration = _threshold_rows(labels, split_col, threshold_split)
    if calibration.empty:
        raise ValueError(f"threshold split {threshold_split!r} has no valid non-excluded rows")

    finite_risk = pd.to_numeric(risk_score, errors="coerce").astype(float).replace([np.inf, -np.inf], np.nan)
    if finite_risk.loc[calibration.index].isna().any():
        raise ValueError("risk_score contains non-finite values on threshold split")
    candidates = calibration.index
    if not allow_zero_score_alarms:
        candidates = candidates[finite_risk.loc[candidates].to_numpy(dtype=float) > 0]
    n_alarm = _target_alarm_count(len(calibration), target_tiw)
    if n_alarm <= 0 or len(candidates) == 0:
        return pd.Series(False, index=labels.index)
    n_alarm = min(n_alarm, len(candidates))

    rng = np.random.default_rng(model_seed)
    tie_break = pd.Series(rng.random(len(labels)), index=labels.index)
    calibration_rank = pd.DataFrame(
        {
            "risk_score": finite_risk.loc[candidates].to_numpy(dtype=float),
            "tie_break": tie_break.loc[candidates].to_numpy(dtype=float),
        },
        index=candidates,
    ).sort_values(["risk_score", "tie_break"], ascending=[False, False])
    cutoff = calibration_rank.iloc[n_alarm - 1]
    alarm = pd.Series(False, index=labels.index)
    eligible = valid & finite_risk.notna()
    if not allow_zero_score_alarms:
        eligible &= finite_risk > 0
    alarm.loc[eligible] = (
        finite_risk.loc[eligible] > float(cutoff["risk_score"])
    ) | (
        finite_risk.loc[eligible].eq(float(cutoff["risk_score"]))
        & (tie_break.loc[eligible] >= float(cutoff["tie_break"]))
    )
    return alarm


def _split_prevalence_scores(
    labels: pd.DataFrame,
    *,
    fit_split: str,
    split_col: str,
) -> tuple[pd.Series, float]:
    prevalence = _positive_rate(_fit_rows(labels, split_col, fit_split))
    risk = pd.Series(prevalence, index=labels.index, dtype=float)
    return risk, prevalence


def split_prevalence_prior(
    labels: pd.DataFrame,
    *,
    fit_split: str = "train",
    threshold_split: str = "val",
    target_tiw: float = 0.1,
    split_col: str = "split",
    seed: int = 42,
) -> pd.DataFrame:
    _validate_common_inputs(labels, fit_split, threshold_split, target_tiw, split_col)
    model_seed = derive_model_seed(seed, "split_prevalence_prior")
    risk, prevalence = _split_prevalence_scores(labels, fit_split=fit_split, split_col=split_col)
    alarm = _target_tiw_alarm_mask(
        labels,
        risk,
        split_col=split_col,
        threshold_split=threshold_split,
        target_tiw=target_tiw,
        model_seed=model_seed,
        allow_zero_score_alarms=prevalence > 0,
    )
    return _append_metadata(
        labels,
        risk_score=risk,
        alarm=alarm,
        null_model="split_prevalence_prior",
        null_model_variant="split_prevalence_prior",
        fit_split=fit_split,
        threshold_split=threshold_split,
        target_tiw=target_tiw,
        model_seed=model_seed,
    )


def rate_matched_random(
    labels: pd.DataFrame,
    *,
    fit_split: str = "train",
    threshold_split: str = "val",
    target_tiw: float = 0.1,
    split_col: str = "split",
    seed: int = 42,
) -> pd.DataFrame:
    _validate_common_inputs(labels, fit_split, threshold_split, target_tiw, split_col)
    model_seed = derive_model_seed(seed, "rate_matched_random")
    risk, prevalence = _split_prevalence_scores(labels, fit_split=fit_split, split_col=split_col)
    alarm = _target_tiw_alarm_mask(
        labels,
        risk,
        split_col=split_col,
        threshold_split=threshold_split,
        target_tiw=target_tiw,
        model_seed=model_seed,
        allow_zero_score_alarms=prevalence > 0,
    )
    return _append_metadata(
        labels,
        risk_score=risk,
        alarm=alarm,
        null_model="rate_matched_random",
        null_model_variant="rate_matched_random",
        fit_split=fit_split,
        threshold_split=threshold_split,
        target_tiw=target_tiw,
        model_seed=model_seed,
    )


def patient_prior(
    labels: pd.DataFrame,
    *,
    fit_split: str = "train",
    threshold_split: str = "val",
    target_tiw: float = 0.1,
    split_col: str = "split",
    seed: int = 42,
    patient_min_events: int = 3,
) -> pd.DataFrame:
    _validate_common_inputs(labels, fit_split, threshold_split, target_tiw, split_col)
    if patient_min_events < 0:
        raise ValueError("patient_min_events must be non-negative")
    model_seed = derive_model_seed(seed, "patient_prior")
    fit = _fit_rows(labels, split_col, fit_split)
    population_risk = _positive_rate(fit)
    grouped = fit.groupby("patient_id")["forecast_label"].agg(["sum", "mean"])
    patient_positive_counts = grouped["sum"].astype(int)
    patient_risks = grouped["mean"].astype(float)

    risk = pd.Series(population_risk, index=labels.index, dtype=float)
    variant = pd.Series("patient_prior_fallback_population", index=labels.index, dtype=object)
    for patient, patient_index in labels.groupby("patient_id", sort=False).groups.items():
        if patient in patient_risks.index and patient_positive_counts.loc[patient] >= patient_min_events:
            risk.loc[patient_index] = float(patient_risks.loc[patient])
            variant.loc[patient_index] = "patient_prior"

    alarm = _target_tiw_alarm_mask(
        labels,
        risk,
        split_col=split_col,
        threshold_split=threshold_split,
        target_tiw=target_tiw,
        model_seed=model_seed,
        allow_zero_score_alarms=population_risk > 0,
    )
    return _append_metadata(
        labels,
        risk_score=risk,
        alarm=alarm,
        null_model="patient_prior",
        null_model_variant=variant,
        fit_split=fit_split,
        threshold_split=threshold_split,
        target_tiw=target_tiw,
        model_seed=model_seed,
    )


def _hour_column(labels: pd.DataFrame, cycle_bin: str) -> pd.Series:
    if cycle_bin != "hour_of_day":
        raise ValueError("only cycle_bin='hour_of_day' is supported in Task 4")
    if "window_start" not in labels.columns:
        raise ValueError("labels table must contain window_start for hour_of_day bins")
    return ensure_datetime(labels["window_start"]).dt.hour.astype(int)


def cycle_preserving_random(
    labels: pd.DataFrame,
    *,
    fit_split: str = "train",
    threshold_split: str = "val",
    target_tiw: float = 0.1,
    split_col: str = "split",
    seed: int = 42,
    cycle_bin: str = "hour_of_day",
) -> pd.DataFrame:
    _validate_common_inputs(labels, fit_split, threshold_split, target_tiw, split_col)
    model_seed = derive_model_seed(seed, "cycle_preserving_random")
    fit = _fit_rows(labels, split_col, fit_split)
    fit_hours = _hour_column(fit, cycle_bin)
    fit = fit.assign(hour_of_day=fit_hours)
    hour_rate = fit.groupby("hour_of_day")["forecast_label"].mean().astype(float).to_dict()
    risk = _hour_column(labels, cycle_bin).map(lambda hour: float(hour_rate.get(int(hour), 0.0)))
    risk = pd.Series(risk.to_numpy(dtype=float), index=labels.index)
    alarm = _target_tiw_alarm_mask(
        labels,
        risk,
        split_col=split_col,
        threshold_split=threshold_split,
        target_tiw=target_tiw,
        model_seed=model_seed,
        allow_zero_score_alarms=False,
    )
    return _append_metadata(
        labels,
        risk_score=risk,
        alarm=alarm,
        null_model="cycle_preserving_random",
        null_model_variant="cycle_preserving_random",
        fit_split=fit_split,
        threshold_split=threshold_split,
        target_tiw=target_tiw,
        model_seed=model_seed,
    )


def generate_forecast_null(
    labels: pd.DataFrame,
    *,
    null_model: str,
    fit_split: str = "train",
    threshold_split: str = "val",
    target_tiw: float = 0.1,
    split_col: str = "split",
    patient_min_events: int = 3,
    cycle_bin: str = "hour_of_day",
    seed: int = 42,
) -> pd.DataFrame:
    if null_model == "split_prevalence_prior":
        return split_prevalence_prior(
            labels,
            fit_split=fit_split,
            threshold_split=threshold_split,
            target_tiw=target_tiw,
            split_col=split_col,
            seed=seed,
        )
    if null_model == "rate_matched_random":
        return rate_matched_random(
            labels,
            fit_split=fit_split,
            threshold_split=threshold_split,
            target_tiw=target_tiw,
            split_col=split_col,
            seed=seed,
        )
    if null_model == "patient_prior":
        return patient_prior(
            labels,
            fit_split=fit_split,
            threshold_split=threshold_split,
            target_tiw=target_tiw,
            split_col=split_col,
            seed=seed,
            patient_min_events=patient_min_events,
        )
    if null_model == "cycle_preserving_random":
        return cycle_preserving_random(
            labels,
            fit_split=fit_split,
            threshold_split=threshold_split,
            target_tiw=target_tiw,
            split_col=split_col,
            seed=seed,
            cycle_bin=cycle_bin,
        )
    raise ValueError(f"unknown null_model {null_model!r}; expected one of {sorted(NULL_MODELS)}")


def variant_counts(predictions: pd.DataFrame) -> dict[str, int]:
    if "null_model_variant" not in predictions.columns:
        raise ValueError("predictions must contain null_model_variant")
    return {
        str(key): int(value)
        for key, value in predictions["null_model_variant"].value_counts().sort_index().items()
    }


def appended_columns() -> Iterable[str]:
    return tuple(APPENDED_COLUMNS)
