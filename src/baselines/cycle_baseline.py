from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from src.utils.time import ensure_datetime


@dataclass(frozen=True)
class CyclePriorModel:
    """Empirical circadian risk prior fitted on labeled training windows only."""

    global_prior: float
    global_hour: pd.DataFrame
    patient_prior: pd.DataFrame
    patient_hour: pd.DataFrame
    smoothing: float


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
