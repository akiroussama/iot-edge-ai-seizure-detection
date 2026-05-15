from __future__ import annotations

import numpy as np
import pandas as pd


def robust_zscore(series: pd.Series) -> pd.Series:
    """Robust z-score using median absolute deviation."""
    x = series.astype(float)
    med = x.median()
    mad = (x - med).abs().median()
    if mad == 0 or np.isnan(mad):
        std = x.std(ddof=0)
        return (x - x.mean()) / (std if std else 1.0)
    return 0.6745 * (x - med) / mad


def ecg_tachycardia_score(features_df: pd.DataFrame, hr_col: str = "hr_mean") -> pd.Series:
    """Relative tachycardia score per patient if HR features are available."""
    if hr_col not in features_df.columns:
        return pd.Series(0.0, index=features_df.index)
    return features_df.groupby("patient_id")[hr_col].transform(robust_zscore).clip(lower=0)


def acc_energy_score(features_df: pd.DataFrame, energy_col: str = "acc_energy") -> pd.Series:
    """Motion energy anomaly score per patient."""
    if energy_col not in features_df.columns:
        return pd.Series(0.0, index=features_df.index)
    return features_df.groupby("patient_id")[energy_col].transform(robust_zscore).clip(lower=0)


def generic_zscore_anomaly(features_df: pd.DataFrame, feature_cols: list[str]) -> pd.Series:
    """Average positive robust z-score across available feature columns."""
    available = [c for c in feature_cols if c in features_df.columns]
    if not available:
        return pd.Series(0.0, index=features_df.index)
    scores = []
    for col in available:
        scores.append(features_df.groupby("patient_id")[col].transform(robust_zscore).clip(lower=0))
    return pd.concat(scores, axis=1).mean(axis=1)


def normalize_score(score: pd.Series) -> pd.Series:
    """Map an arbitrary non-negative score to [0, 1] using a rank transform."""
    if len(score) == 0:
        return score
    return score.rank(pct=True).fillna(0.0)
