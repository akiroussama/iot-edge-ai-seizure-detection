from __future__ import annotations

from dataclasses import dataclass
from hashlib import blake2b
from typing import Any

import numpy as np
import pandas as pd

from src.utils.time import ensure_datetime


@dataclass(frozen=True)
class PatientAdaptiveConfig:
    baseline: str = "empirical_bayes"
    evaluation_mode: str = "warm_start"
    split_col: str = "split"
    fit_split: str = "train"
    threshold_split: str = "val"
    patient_col: str = "patient_id"
    min_patient_observations: int = 3
    prior_strength: float = 8.0
    target_tiw: float = 0.1
    seed: int = 42


APPENDED_COLUMNS = [
    "risk_score",
    "alarm",
    "patient_adaptive_model",
    "patient_adaptive_variant",
    "adaptive_evaluation_mode",
    "score_fit_split",
    "threshold_source_split",
    "target_tiw",
    "empirical_bayes_prior_strength",
    "patient_min_observations",
    "seed",
    "population_prior_rate",
]

REQUIRED_COLUMNS = {
    "patient_id",
    "recording_id",
    "window_start",
    "window_end",
    "forecast_label",
    "is_excluded",
}


def _valid_mask(df: pd.DataFrame) -> pd.Series:
    return ~df["is_excluded"].fillna(False).astype(bool)


def _validate_inputs(labels: pd.DataFrame, config: PatientAdaptiveConfig) -> None:
    missing = sorted(REQUIRED_COLUMNS - set(labels.columns))
    if missing:
        raise ValueError(f"labels table missing required columns: {missing}")
    if config.split_col not in labels.columns:
        raise ValueError(f"labels table must contain split column {config.split_col!r}")
    if config.baseline not in {"population", "patient", "empirical_bayes"}:
        raise ValueError("baseline must be population, patient, or empirical_bayes")
    if config.evaluation_mode not in {"cold_start", "warm_start", "rolling_origin"}:
        raise ValueError("evaluation_mode must be cold_start, warm_start, or rolling_origin")
    if config.min_patient_observations < 0:
        raise ValueError("min_patient_observations must be non-negative")
    if config.prior_strength < 0:
        raise ValueError("prior_strength must be non-negative")
    if not 0 <= config.target_tiw <= 1:
        raise ValueError("target_tiw must be in [0, 1]")
    collisions = [column for column in APPENDED_COLUMNS if column in labels.columns]
    if collisions:
        raise ValueError(f"labels table already contains output columns: {collisions}")
    valid = _valid_mask(labels)
    if not (valid & labels[config.split_col].astype(str).eq(config.fit_split)).any():
        raise ValueError(f"fit split {config.fit_split!r} has no valid non-excluded rows")
    if not (valid & labels[config.split_col].astype(str).eq(config.threshold_split)).any():
        raise ValueError(
            f"threshold split {config.threshold_split!r} has no valid non-excluded rows"
        )


def _model_seed(config: PatientAdaptiveConfig) -> int:
    token = f"{config.seed}:{config.baseline}:{config.evaluation_mode}".encode("utf-8")
    return int.from_bytes(blake2b(token, digest_size=8).digest(), "little") % (2**32)


def _fit_rows(labels: pd.DataFrame, config: PatientAdaptiveConfig) -> pd.DataFrame:
    valid = _valid_mask(labels)
    return labels.loc[valid & labels[config.split_col].astype(str).eq(config.fit_split)].copy()


def _population_rate(rows: pd.DataFrame) -> float:
    if rows.empty:
        raise ValueError("cannot compute population rate from empty rows")
    return float(rows["forecast_label"].fillna(False).astype(bool).mean())


def _patient_stats(rows: pd.DataFrame, patient_col: str) -> pd.DataFrame:
    return rows.groupby(patient_col)["forecast_label"].agg(["sum", "count", "mean"])


def _adaptive_rate(
    *,
    positives: float,
    count: int,
    population_rate: float,
    config: PatientAdaptiveConfig,
) -> tuple[float, str]:
    if config.baseline == "population":
        return population_rate, "population_prior"
    if count < config.min_patient_observations:
        return population_rate, f"{config.baseline}_fallback_population"
    if config.baseline == "patient":
        return float(positives / count), "patient_prior"
    numerator = positives + config.prior_strength * population_rate
    denominator = count + config.prior_strength
    return float(numerator / denominator), "empirical_bayes_shrinkage"


def _warm_start_scores(
    labels: pd.DataFrame,
    config: PatientAdaptiveConfig,
) -> tuple[pd.Series, pd.Series, float]:
    fit = _fit_rows(labels, config)
    population_rate = _population_rate(fit)
    stats = _patient_stats(fit, config.patient_col)
    risk = pd.Series(population_rate, index=labels.index, dtype=float)
    variant = pd.Series(f"{config.baseline}_fallback_population", index=labels.index, dtype=object)
    if config.baseline == "population" or config.evaluation_mode == "cold_start":
        variant.loc[:] = f"{config.baseline}_{config.evaluation_mode}_population"
        return risk, variant, population_rate

    for patient, index in labels.groupby(config.patient_col, sort=False).groups.items():
        if patient not in stats.index:
            continue
        rate, patient_variant = _adaptive_rate(
            positives=float(stats.loc[patient, "sum"]),
            count=int(stats.loc[patient, "count"]),
            population_rate=population_rate,
            config=config,
        )
        risk.loc[index] = rate
        variant.loc[index] = patient_variant
    return risk, variant, population_rate


def _rolling_origin_scores(
    labels: pd.DataFrame,
    config: PatientAdaptiveConfig,
) -> tuple[pd.Series, pd.Series, float]:
    prepared = labels.copy()
    prepared["window_start"] = ensure_datetime(prepared["window_start"])
    prepared["window_end"] = ensure_datetime(prepared["window_end"])
    fit = _fit_rows(prepared, config)
    population_rate = _population_rate(fit)
    risk = pd.Series(population_rate, index=prepared.index, dtype=float)
    variant = pd.Series(f"{config.baseline}_fallback_population", index=prepared.index, dtype=object)
    if config.baseline == "population":
        variant.loc[:] = "population_rolling_origin"
        return risk, variant, population_rate

    valid = _valid_mask(prepared)
    sorted_index = prepared.sort_values(["window_end", config.patient_col]).index
    for idx in sorted_index:
        row = prepared.loc[idx]
        history = prepared.loc[
            valid
            & prepared[config.patient_col].eq(row[config.patient_col])
            & (prepared["window_end"] < row["window_start"])
        ]
        if history.empty:
            continue
        positives = float(history["forecast_label"].fillna(False).astype(bool).sum())
        count = int(len(history))
        rate, patient_variant = _adaptive_rate(
            positives=positives,
            count=count,
            population_rate=population_rate,
            config=config,
        )
        risk.loc[idx] = rate
        variant.loc[idx] = f"{patient_variant}_rolling_origin"
    return risk, variant, population_rate


def _target_alarm_count(n_rows: int, target_tiw: float) -> int:
    if n_rows <= 0 or target_tiw <= 0:
        return 0
    if target_tiw >= 1:
        return n_rows
    return int(round(target_tiw * n_rows))


def _target_tiw_alarm_mask(
    labels: pd.DataFrame,
    risk_score: pd.Series,
    config: PatientAdaptiveConfig,
    *,
    model_seed: int,
) -> pd.Series:
    valid = _valid_mask(labels)
    threshold_rows = labels.loc[
        valid & labels[config.split_col].astype(str).eq(config.threshold_split)
    ].copy()
    if threshold_rows.empty:
        raise ValueError(f"threshold split {config.threshold_split!r} has no valid rows")
    n_alarm = _target_alarm_count(len(threshold_rows), config.target_tiw)
    if n_alarm <= 0:
        return pd.Series(False, index=labels.index)

    finite_risk = pd.to_numeric(risk_score, errors="coerce").replace([np.inf, -np.inf], np.nan)
    if finite_risk.loc[threshold_rows.index].isna().any():
        raise ValueError("risk_score contains non-finite values on threshold split")
    rng = np.random.default_rng(model_seed)
    tie_break = pd.Series(rng.random(len(labels)), index=labels.index)
    ranked = pd.DataFrame(
        {
            "risk_score": finite_risk.loc[threshold_rows.index],
            "tie_break": tie_break.loc[threshold_rows.index],
        },
        index=threshold_rows.index,
    ).sort_values(["risk_score", "tie_break"], ascending=[False, False])
    cutoff = ranked.iloc[min(n_alarm, len(ranked)) - 1]
    eligible = valid & finite_risk.notna()
    alarm = pd.Series(False, index=labels.index)
    alarm.loc[eligible] = (
        finite_risk.loc[eligible] > float(cutoff["risk_score"])
    ) | (
        finite_risk.loc[eligible].eq(float(cutoff["risk_score"]))
        & (tie_break.loc[eligible] >= float(cutoff["tie_break"]))
    )
    return alarm


def patient_adaptive_predictions(
    labels: pd.DataFrame,
    *,
    config: PatientAdaptiveConfig | None = None,
) -> pd.DataFrame:
    """Return leakage-safe patient-adaptive probabilistic baseline predictions."""
    cfg = config or PatientAdaptiveConfig()
    _validate_inputs(labels, cfg)
    model_seed = _model_seed(cfg)
    if cfg.evaluation_mode == "rolling_origin":
        risk, variant, population_rate = _rolling_origin_scores(labels, cfg)
    else:
        risk, variant, population_rate = _warm_start_scores(labels, cfg)
    alarm = _target_tiw_alarm_mask(labels, risk, cfg, model_seed=model_seed)

    out = labels.copy()
    out["risk_score"] = risk.astype(float).clip(0.0, 1.0)
    out["alarm"] = alarm.fillna(False).astype(bool)
    out.loc[~_valid_mask(out), "alarm"] = False
    out["patient_adaptive_model"] = cfg.baseline
    out["patient_adaptive_variant"] = variant.astype(str)
    out["adaptive_evaluation_mode"] = cfg.evaluation_mode
    out["score_fit_split"] = cfg.fit_split
    out["threshold_source_split"] = cfg.threshold_split
    out["target_tiw"] = float(cfg.target_tiw)
    out["empirical_bayes_prior_strength"] = float(cfg.prior_strength)
    out["patient_min_observations"] = int(cfg.min_patient_observations)
    out["seed"] = int(model_seed)
    out["population_prior_rate"] = float(population_rate)
    return out


def patient_adaptive_summary(predictions: pd.DataFrame) -> pd.DataFrame:
    _require_prediction_columns(predictions)
    rows = []
    for (mode, model, variant), group in predictions.groupby(
        ["adaptive_evaluation_mode", "patient_adaptive_model", "patient_adaptive_variant"],
        dropna=False,
    ):
        valid = _valid_mask(group)
        rows.append(
            {
                "adaptive_evaluation_mode": mode,
                "patient_adaptive_model": model,
                "patient_adaptive_variant": variant,
                "rows": int(len(group)),
                "valid_rows": int(valid.sum()),
                "mean_risk_score": float(group.loc[valid, "risk_score"].mean()),
                "alarm_rows": int(group.loc[valid, "alarm"].fillna(False).astype(bool).sum()),
            }
        )
    return pd.DataFrame(rows)


def _require_prediction_columns(predictions: pd.DataFrame) -> None:
    missing = sorted(set(APPENDED_COLUMNS) - set(predictions.columns))
    if missing:
        raise ValueError(f"predictions missing patient-adaptive columns: {missing}")


def table_records(df: pd.DataFrame) -> list[dict[str, Any]]:
    records = []
    for record in df.to_dict(orient="records"):
        clean = {}
        for key, value in record.items():
            if isinstance(value, float) and (np.isnan(value) or np.isinf(value)):
                clean[key] = None
            elif value is pd.NA or value is pd.NaT:
                clean[key] = None
            elif isinstance(value, pd.Timestamp):
                clean[key] = value.isoformat()
            elif isinstance(value, np.integer):
                clean[key] = int(value)
            elif isinstance(value, np.floating):
                clean[key] = float(value)
            else:
                clean[key] = value
        records.append(clean)
    return records
