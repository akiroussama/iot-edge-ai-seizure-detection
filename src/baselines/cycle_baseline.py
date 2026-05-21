from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from src.features.cycle_features import period_key
from src.utils.time import ensure_datetime


@dataclass(frozen=True)
class CyclePriorModel:
    """Empirical circadian risk prior fitted on labeled training windows only."""

    global_prior: float
    global_hour: pd.DataFrame
    patient_prior: pd.DataFrame
    patient_hour: pd.DataFrame
    smoothing: float


@dataclass(frozen=True)
class MultiCyclePriorModel:
    """Empirical patient-aware priors over fixed circadian/weekly/multiday bins."""

    global_prior: float
    period_hours: tuple[float, ...]
    n_phase_bins: int
    global_cycle: pd.DataFrame
    patient_prior: pd.DataFrame
    patient_cycle: pd.DataFrame
    smoothing: float
    patient_col: str


def _valid_rows(df: pd.DataFrame) -> pd.DataFrame:
    if "forecast_label" not in df.columns:
        raise ValueError("df must contain forecast_label")
    out = df.copy()
    excluded = out.get("is_excluded", pd.Series(False, index=out.index)).fillna(False).astype(bool)
    out = out.loc[~excluded].copy()
    if out.empty:
        raise ValueError("no valid non-excluded rows available")
    out["forecast_label"] = out["forecast_label"].astype(bool)
    out["window_end"] = ensure_datetime(out["window_end"])
    out["hour_of_day"] = out["window_end"].dt.hour.astype(int)
    return out


def _cycle_bin_columns(
    df: pd.DataFrame,
    period_hours: tuple[float, ...],
    n_phase_bins: int,
) -> pd.DataFrame:
    if n_phase_bins <= 0:
        raise ValueError("n_phase_bins must be positive")
    if "window_end" not in df.columns:
        raise ValueError("df must contain window_end")
    out = df.copy()
    out["window_end"] = ensure_datetime(out["window_end"])
    epoch_seconds = (out["window_end"] - pd.Timestamp("1970-01-01")).dt.total_seconds()
    for period in period_hours:
        if period <= 0:
            raise ValueError("period_hours values must be positive")
        key = period_key(period)
        phase = np.mod(epoch_seconds, float(period) * 3600.0) / (float(period) * 3600.0)
        out[f"cycle_{key}_bin"] = np.floor(phase * n_phase_bins).clip(0, n_phase_bins - 1).astype(int)
    return out


def _smoothed_rate(pos: pd.Series, n: pd.Series, prior: float, smoothing: float) -> pd.Series:
    return (pos.astype(float) + smoothing * prior) / (n.astype(float) + smoothing)


def fit_cycle_prior(
    labels_df: pd.DataFrame,
    smoothing: float = 10.0,
    patient_col: str = "patient_id",
) -> CyclePriorModel:
    """Fit patient/hour-of-day empirical risk from training labels.

    This is a transparent baseline for longitudinal forecasting. It intentionally uses only
    historical labels from the fit split and no signal features.
    """
    if patient_col not in labels_df.columns:
        raise ValueError(f"labels_df must contain {patient_col}")
    if smoothing < 0:
        raise ValueError("smoothing must be non-negative")

    train = _valid_rows(labels_df)
    global_prior = float(train["forecast_label"].mean())

    global_hour_counts = train.groupby("hour_of_day")["forecast_label"].agg(["sum", "count"]).reset_index()
    global_hour_counts["risk_score"] = _smoothed_rate(
        global_hour_counts["sum"],
        global_hour_counts["count"],
        global_prior,
        smoothing,
    )
    global_hour = global_hour_counts[["hour_of_day", "risk_score"]].rename(
        columns={"risk_score": "global_hour_risk"}
    )

    patient_counts = train.groupby(patient_col)["forecast_label"].agg(["sum", "count"]).reset_index()
    patient_counts["risk_score"] = _smoothed_rate(
        patient_counts["sum"],
        patient_counts["count"],
        global_prior,
        smoothing,
    )
    patient_prior = patient_counts[[patient_col, "risk_score"]].rename(
        columns={"risk_score": "patient_prior_risk"}
    )

    patient_hour_counts = (
        train.groupby([patient_col, "hour_of_day"])["forecast_label"].agg(["sum", "count"]).reset_index()
    )
    patient_hour_counts = patient_hour_counts.merge(patient_prior, on=patient_col, how="left")
    patient_hour_counts["risk_score"] = _smoothed_rate(
        patient_hour_counts["sum"],
        patient_hour_counts["count"],
        patient_hour_counts["patient_prior_risk"],
        smoothing,
    )
    patient_hour = patient_hour_counts[[patient_col, "hour_of_day", "risk_score"]].rename(
        columns={"risk_score": "patient_hour_risk"}
    )

    return CyclePriorModel(
        global_prior=global_prior,
        global_hour=global_hour,
        patient_prior=patient_prior,
        patient_hour=patient_hour,
        smoothing=smoothing,
    )


def predict_cycle_prior(
    labels_df: pd.DataFrame,
    model: CyclePriorModel,
    patient_col: str = "patient_id",
) -> pd.DataFrame:
    """Apply a fitted cycle prior to labeled windows."""
    if patient_col not in labels_df.columns:
        raise ValueError(f"labels_df must contain {patient_col}")
    if "window_end" not in labels_df.columns:
        raise ValueError("labels_df must contain window_end")

    out = labels_df.copy()
    out["window_end"] = ensure_datetime(out["window_end"])
    out["hour_of_day"] = out["window_end"].dt.hour.astype(int)
    out = out.merge(model.global_hour, on="hour_of_day", how="left")
    out = out.merge(model.patient_prior, on=patient_col, how="left")
    out = out.merge(model.patient_hour, on=[patient_col, "hour_of_day"], how="left")
    out["risk_score"] = (
        out["patient_hour_risk"]
        .fillna(out["patient_prior_risk"])
        .fillna(out["global_hour_risk"])
        .fillna(model.global_prior)
        .astype(float)
    )
    out["cycle_global_prior"] = float(model.global_prior)
    return out


def fit_multiday_cycle_prior(
    labels_df: pd.DataFrame,
    *,
    period_hours: tuple[float, ...] = (24.0, 168.0),
    n_phase_bins: int = 8,
    smoothing: float = 10.0,
    patient_col: str = "patient_id",
) -> MultiCyclePriorModel:
    """Fit empirical priors for multiple deterministic cycle periods."""
    if patient_col not in labels_df.columns:
        raise ValueError(f"labels_df must contain {patient_col}")
    if smoothing < 0:
        raise ValueError("smoothing must be non-negative")
    train = _cycle_bin_columns(_valid_rows(labels_df), period_hours, n_phase_bins)
    global_prior = float(train["forecast_label"].mean())
    patient_counts = train.groupby(patient_col)["forecast_label"].agg(["sum", "count"]).reset_index()
    patient_counts["risk_score"] = _smoothed_rate(
        patient_counts["sum"],
        patient_counts["count"],
        global_prior,
        smoothing,
    )
    patient_prior = patient_counts[[patient_col, "risk_score"]].rename(
        columns={"risk_score": "patient_prior_risk"}
    )

    global_frames = []
    patient_frames = []
    for period in period_hours:
        key = period_key(period)
        bin_col = f"cycle_{key}_bin"
        global_counts = train.groupby(bin_col)["forecast_label"].agg(["sum", "count"]).reset_index()
        global_counts["period_hours"] = float(period)
        global_counts["phase_bin"] = global_counts[bin_col].astype(int)
        global_counts["global_cycle_risk"] = _smoothed_rate(
            global_counts["sum"],
            global_counts["count"],
            global_prior,
            smoothing,
        )
        global_frames.append(
            global_counts[["period_hours", "phase_bin", "global_cycle_risk"]]
        )

        patient_counts = (
            train.groupby([patient_col, bin_col])["forecast_label"].agg(["sum", "count"]).reset_index()
        )
        patient_counts = patient_counts.merge(patient_prior, on=patient_col, how="left")
        patient_counts["period_hours"] = float(period)
        patient_counts["phase_bin"] = patient_counts[bin_col].astype(int)
        patient_counts["patient_cycle_risk"] = _smoothed_rate(
            patient_counts["sum"],
            patient_counts["count"],
            patient_counts["patient_prior_risk"],
            smoothing,
        )
        patient_frames.append(
            patient_counts[[patient_col, "period_hours", "phase_bin", "patient_cycle_risk"]]
        )

    return MultiCyclePriorModel(
        global_prior=global_prior,
        period_hours=tuple(float(period) for period in period_hours),
        n_phase_bins=int(n_phase_bins),
        global_cycle=pd.concat(global_frames, ignore_index=True),
        patient_prior=patient_prior,
        patient_cycle=pd.concat(patient_frames, ignore_index=True),
        smoothing=float(smoothing),
        patient_col=patient_col,
    )


def predict_multiday_cycle_prior(
    labels_df: pd.DataFrame,
    model: MultiCyclePriorModel,
) -> pd.DataFrame:
    """Apply a fitted multicycle prior to labeled windows."""
    patient_col = model.patient_col
    if patient_col not in labels_df.columns:
        raise ValueError(f"labels_df must contain {patient_col}")
    out = _cycle_bin_columns(labels_df, model.period_hours, model.n_phase_bins)
    out = out.merge(model.patient_prior, on=patient_col, how="left")
    risk_columns = []
    for period in model.period_hours:
        key = period_key(period)
        bin_col = f"cycle_{key}_bin"
        period_global = model.global_cycle.loc[model.global_cycle["period_hours"].eq(float(period))]
        period_patient = model.patient_cycle.loc[model.patient_cycle["period_hours"].eq(float(period))]
        out = out.merge(
            period_global[["phase_bin", "global_cycle_risk"]],
            left_on=bin_col,
            right_on="phase_bin",
            how="left",
        ).drop(columns=["phase_bin"])
        out = out.rename(columns={"global_cycle_risk": f"global_cycle_{key}_risk"})
        out = out.merge(
            period_patient[[patient_col, "phase_bin", "patient_cycle_risk"]],
            left_on=[patient_col, bin_col],
            right_on=[patient_col, "phase_bin"],
            how="left",
        ).drop(columns=["phase_bin"])
        out = out.rename(columns={"patient_cycle_risk": f"patient_cycle_{key}_risk"})
        risk_col = f"cycle_{key}_risk"
        out[risk_col] = (
            out[f"patient_cycle_{key}_risk"]
            .fillna(out["patient_prior_risk"])
            .fillna(out[f"global_cycle_{key}_risk"])
            .fillna(model.global_prior)
            .astype(float)
        )
        risk_columns.append(risk_col)
    out["risk_score"] = out[risk_columns].mean(axis=1).astype(float)
    out["cycle_global_prior"] = float(model.global_prior)
    out["cycle_model_variant"] = "multiday_cycle_prior"
    return out


def rolling_origin_multiday_cycle_predictions(
    labels_df: pd.DataFrame,
    *,
    period_hours: tuple[float, ...] = (24.0, 168.0),
    n_phase_bins: int = 8,
    smoothing: float = 10.0,
    min_history_rows: int = 10,
    patient_col: str = "patient_id",
) -> pd.DataFrame:
    """Predict each row from strictly earlier labels only."""
    if min_history_rows < 0:
        raise ValueError("min_history_rows must be non-negative")
    if patient_col not in labels_df.columns:
        raise ValueError(f"labels_df must contain {patient_col}")
    labels = labels_df.copy()
    labels["window_end"] = ensure_datetime(labels["window_end"])
    sorted_index = labels.sort_values(["window_end", patient_col]).index
    risks: dict[object, float] = {}
    variants: dict[object, str] = {}
    for idx in sorted_index:
        row_end = labels.loc[idx, "window_end"]
        history = labels.loc[labels["window_end"] < row_end].copy()
        valid_history = history.loc[
            ~history.get("is_excluded", pd.Series(False, index=history.index)).fillna(False).astype(bool)
        ]
        if len(valid_history) < min_history_rows:
            risks[idx] = float(valid_history["forecast_label"].mean()) if len(valid_history) else 0.0
            variants[idx] = "rolling_origin_insufficient_history"
            continue
        model = fit_multiday_cycle_prior(
            valid_history,
            period_hours=period_hours,
            n_phase_bins=n_phase_bins,
            smoothing=smoothing,
            patient_col=patient_col,
        )
        pred = predict_multiday_cycle_prior(labels.loc[[idx]], model)
        risks[idx] = float(pred["risk_score"].iloc[0])
        variants[idx] = "rolling_origin_multiday_cycle_prior"
    out = labels_df.copy()
    out["risk_score"] = pd.Series(risks)
    out["cycle_model_variant"] = pd.Series(variants)
    return out


def permute_cycle_labels_within_patient(
    labels_df: pd.DataFrame,
    *,
    seed: int = 42,
    patient_col: str = "patient_id",
    label_col: str = "forecast_label",
) -> pd.DataFrame:
    """Negative control: preserve patient prevalence while destroying phase alignment."""
    if patient_col not in labels_df.columns or label_col not in labels_df.columns:
        raise ValueError(f"labels_df must contain {patient_col} and {label_col}")
    rng = np.random.default_rng(seed)
    out = labels_df.copy()
    out["cycle_negative_control"] = "label_permutation_within_patient"
    for _, group in out.groupby(patient_col, sort=False):
        values = group[label_col].to_numpy()
        out.loc[group.index, label_col] = rng.permutation(values)
    return out


def apply_validation_quantile_alarm(
    predictions: pd.DataFrame,
    threshold_split: str = "val",
    target_tiw: float = 0.1,
    split_col: str = "split",
) -> tuple[pd.DataFrame, float]:
    """Select one threshold on a validation split and apply it to all rows."""
    from src.calibration.thresholding import quantile_threshold

    if split_col not in predictions.columns:
        raise ValueError(f"predictions must contain {split_col}")
    if not 0 <= target_tiw <= 1:
        raise ValueError("target_tiw must be in [0, 1]")
    out = predictions.copy()
    valid = ~out.get("is_excluded", pd.Series(False, index=out.index)).fillna(False).astype(bool)
    calibration = out.loc[valid & out[split_col].eq(threshold_split), "risk_score"]
    threshold = quantile_threshold(calibration, target_tiw)
    if not np.isfinite(threshold):
        out["alarm"] = False
    else:
        out["alarm"] = out["risk_score"].astype(float) >= threshold
    out.loc[~valid, "alarm"] = False
    out["alarm_threshold"] = threshold
    out["threshold_fit_split"] = threshold_split
    return out, float(threshold)
