from __future__ import annotations

import numpy as np
import pandas as pd


def _valid(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if "is_excluded" in out.columns:
        out = out.loc[~out["is_excluded"].fillna(False)]
    return out


def brier_score(predictions_df: pd.DataFrame) -> float:
    """Mean squared error between risk_score and forecast_label on valid windows."""
    df = _valid(predictions_df)
    if df.empty:
        return float("nan")
    if "risk_score" not in df.columns or "forecast_label" not in df.columns:
        raise ValueError("predictions_df must contain risk_score and forecast_label")
    y = df["forecast_label"].astype(float).to_numpy()
    p = df["risk_score"].astype(float).clip(0, 1).to_numpy()
    return float(np.mean((p - y) ** 2))


def brier_skill_score(predictions_df: pd.DataFrame, reference_predictions_df: pd.DataFrame) -> float:
    """Brier Skill Score against a reference forecast.

    The reference must be aligned by the caller. A zero reference Brier score
    means the reference is perfect, so the skill ratio is undefined and should
    not be silently reported.
    """
    model_brier = brier_score(predictions_df)
    reference_brier = brier_score(reference_predictions_df)
    if reference_brier == 0:
        raise ValueError("reference Brier score is zero; Brier Skill Score is undefined")
    return float(1.0 - model_brier / reference_brier)


def expected_calibration_error(predictions_df: pd.DataFrame, n_bins: int = 10) -> float:
    """Expected calibration error for binary forecasting risk scores."""
    df = _valid(predictions_df)
    if df.empty:
        return float("nan")
    y = df["forecast_label"].astype(float).to_numpy()
    p = df["risk_score"].astype(float).clip(0, 1).to_numpy()
    bins = np.linspace(0.0, 1.0, n_bins + 1)
    ece = 0.0
    for i in range(n_bins):
        lo, hi = bins[i], bins[i + 1]
        mask = (p >= lo) & (p < hi if i < n_bins - 1 else p <= hi)
        if not np.any(mask):
            continue
        conf = float(np.mean(p[mask]))
        acc = float(np.mean(y[mask]))
        ece += float(np.mean(mask)) * abs(acc - conf)
    return float(ece)


def reliability_table(predictions_df: pd.DataFrame, n_bins: int = 10) -> pd.DataFrame:
    """Return calibration bins for reliability plots/tables on valid windows."""
    df = _valid(predictions_df)
    if df.empty:
        return pd.DataFrame(
            columns=["bin", "bin_start", "bin_end", "count", "mean_score", "empirical_rate"]
        )
    if "risk_score" not in df.columns or "forecast_label" not in df.columns:
        raise ValueError("predictions_df must contain risk_score and forecast_label")
    y = df["forecast_label"].astype(float).to_numpy()
    p = df["risk_score"].astype(float).clip(0, 1).to_numpy()
    bins = np.linspace(0.0, 1.0, n_bins + 1)
    rows = []
    for i in range(n_bins):
        lo, hi = bins[i], bins[i + 1]
        mask = (p >= lo) & (p < hi if i < n_bins - 1 else p <= hi)
        rows.append(
            {
                "bin": i,
                "bin_start": float(lo),
                "bin_end": float(hi),
                "count": int(mask.sum()),
                "mean_score": float(np.mean(p[mask])) if np.any(mask) else float("nan"),
                "empirical_rate": float(np.mean(y[mask])) if np.any(mask) else float("nan"),
            }
        )
    return pd.DataFrame(rows)
