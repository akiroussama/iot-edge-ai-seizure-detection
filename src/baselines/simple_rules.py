from __future__ import annotations

import numpy as np
import pandas as pd


def robust_zscore(series: pd.Series, reference_mask: pd.Series | None = None) -> pd.Series:
    """Robust z-score using median absolute deviation fitted on reference rows."""
    x = series.astype(float)
    reference = x.loc[reference_mask.reindex(x.index, fill_value=False)] if reference_mask is not None else x
    reference = reference.dropna()
    if reference.empty:
        raise ValueError("empty reference rows for robust z-score; refusing silent zero-score fallback")
    med = reference.median()
    mad = (reference - med).abs().median()
    if mad == 0 or np.isnan(mad):
        std = reference.std(ddof=0)
        return (x - reference.mean()) / (std if std else 1.0)
    return 0.6745 * (x - med) / mad


def _patient_reference_mask(group: pd.DataFrame, reference_mask: pd.Series | None) -> pd.Series | None:
    if reference_mask is None:
        return None
    return reference_mask.reindex(group.index, fill_value=False)


def ecg_tachycardia_score(
    features_df: pd.DataFrame,
    hr_col: str = "hr_mean",
    reference_mask: pd.Series | None = None,
) -> pd.Series:
    """Relative tachycardia score per patient if HR features are available."""
    if hr_col not in features_df.columns:
        return pd.Series(0.0, index=features_df.index)
    scores = []
    for _, group in features_df.groupby("patient_id", sort=False):
        score = robust_zscore(group[hr_col], _patient_reference_mask(group, reference_mask)).clip(lower=0)
        scores.append(score)
    return pd.concat(scores).sort_index()


def acc_energy_score(
    features_df: pd.DataFrame,
    energy_col: str = "acc_energy",
    reference_mask: pd.Series | None = None,
) -> pd.Series:
    """Motion energy anomaly score per patient."""
    if energy_col not in features_df.columns:
        return pd.Series(0.0, index=features_df.index)
    scores = []
    for _, group in features_df.groupby("patient_id", sort=False):
        score = robust_zscore(group[energy_col], _patient_reference_mask(group, reference_mask)).clip(lower=0)
        scores.append(score)
    return pd.concat(scores).sort_index()


def generic_zscore_anomaly(
    features_df: pd.DataFrame,
    feature_cols: list[str],
    reference_mask: pd.Series | None = None,
) -> pd.Series:
    """Average positive robust z-score across available feature columns."""
    available = [c for c in feature_cols if c in features_df.columns]
    if not available:
        return pd.Series(0.0, index=features_df.index)
    scores = []
    for col in available:
        column_scores = []
        for _, group in features_df.groupby("patient_id", sort=False):
            score = robust_zscore(group[col], _patient_reference_mask(group, reference_mask)).clip(lower=0)
            column_scores.append(score)
        scores.append(pd.concat(column_scores).sort_index())
    return pd.concat(scores, axis=1).mean(axis=1)


def normalize_score(score: pd.Series, reference_mask: pd.Series | None = None) -> pd.Series:
    """Map an arbitrary non-negative score to [0, 1] using a reference empirical CDF."""
    if len(score) == 0:
        return score
    x = pd.to_numeric(score, errors="coerce").astype(float)
    if reference_mask is None:
        reference = x.dropna()
    else:
        reference = x.loc[reference_mask.reindex(x.index, fill_value=False)].dropna()
    if reference.empty:
        raise ValueError("empty reference rows for score normalization; refusing silent zero-score fallback")
    sorted_reference = np.sort(reference.to_numpy(dtype=float))
    out = pd.Series(0.0, index=score.index)
    finite = np.isfinite(x.to_numpy(dtype=float))
    out.loc[finite] = np.searchsorted(sorted_reference, x.loc[finite].to_numpy(dtype=float), side="right") / len(
        sorted_reference
    )
    return out.clip(0.0, 1.0)
