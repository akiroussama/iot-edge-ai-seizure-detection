from __future__ import annotations

import numpy as np
import pandas as pd


def quantile_threshold(scores: pd.Series | np.ndarray, warning_fraction: float) -> float:
    """Threshold that produces approximately warning_fraction alarms on calibration data."""
    if not 0 <= warning_fraction <= 1:
        raise ValueError("warning_fraction must be in [0, 1]")
    values = np.asarray(scores, dtype=float)
    values = values[np.isfinite(values)]
    if values.size == 0:
        return float("nan")
    if warning_fraction == 0:
        return float(np.nextafter(np.max(values), np.inf))
    if warning_fraction == 1:
        return float(np.min(values))
    return float(np.quantile(values, 1.0 - warning_fraction))


def patient_specific_quantile_thresholds(
    predictions: pd.DataFrame,
    warning_fraction: float,
    patient_col: str = "patient_id",
    score_col: str = "risk_score",
) -> dict[object, float]:
    """Compute one score threshold per patient from calibration predictions."""
    if patient_col not in predictions.columns or score_col not in predictions.columns:
        raise ValueError(f"predictions must contain {patient_col} and {score_col}")
    return {
        patient: quantile_threshold(group[score_col], warning_fraction)
        for patient, group in predictions.groupby(patient_col)
    }


def apply_patient_thresholds(
    predictions: pd.DataFrame,
    thresholds: dict[object, float],
    patient_col: str = "patient_id",
    score_col: str = "risk_score",
) -> pd.DataFrame:
    df = predictions.copy()
    df["patient_threshold"] = df[patient_col].map(thresholds).astype(float)
    df["alarm"] = df[score_col].astype(float) >= df["patient_threshold"]
    return df
