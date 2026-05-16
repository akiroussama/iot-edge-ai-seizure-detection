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


def _validate_reference_scope(reference_scope: str) -> None:
    if reference_scope not in ("patient", "population"):
        raise ValueError(
            f"reference_scope must be 'patient' or 'population', got {reference_scope!r}"
        )


def _scored_column(
    features_df: pd.DataFrame,
    col: str,
    reference_mask: pd.Series | None,
    reference_scope: str,
) -> pd.Series:
    """Positive robust z-score for one feature column, per patient or population.

    ``population`` pools every reference row into one robust reference and
    applies it to all patients, so a held-out patient with no reference rows
    of its own is still scorable (Phase R audit C3 Gap 2). ``patient`` fits a
    separate reference per patient and fails closed on a patient that has none.
    """
    if reference_scope == "population":
        return robust_zscore(features_df[col], reference_mask).clip(lower=0)
    scores = [
        robust_zscore(group[col], _patient_reference_mask(group, reference_mask)).clip(lower=0)
        for _, group in features_df.groupby("patient_id", sort=False)
    ]
    return pd.concat(scores).sort_index()


def ecg_tachycardia_score(
    features_df: pd.DataFrame,
    hr_col: str = "hr_mean",
    reference_mask: pd.Series | None = None,
    reference_scope: str = "patient",
) -> pd.Series:
    """Relative tachycardia score from a per-patient or population reference."""
    _validate_reference_scope(reference_scope)
    if hr_col not in features_df.columns:
        raise ValueError(f"missing required HR feature column for tachycardia rule: {hr_col}")
    return _scored_column(features_df, hr_col, reference_mask, reference_scope)


def acc_energy_score(
    features_df: pd.DataFrame,
    energy_col: str = "acc_energy",
    reference_mask: pd.Series | None = None,
    reference_scope: str = "patient",
) -> pd.Series:
    """Motion energy anomaly score from a per-patient or population reference."""
    _validate_reference_scope(reference_scope)
    if energy_col not in features_df.columns:
        raise ValueError(f"missing required ACC feature column for energy rule: {energy_col}")
    return _scored_column(features_df, energy_col, reference_mask, reference_scope)


def generic_zscore_anomaly(
    features_df: pd.DataFrame,
    feature_cols: list[str],
    reference_mask: pd.Series | None = None,
    reference_scope: str = "patient",
) -> pd.Series:
    """Average positive robust z-score across available feature columns."""
    _validate_reference_scope(reference_scope)
    available = [c for c in feature_cols if c in features_df.columns]
    missing = sorted(set(feature_cols) - set(available))
    if missing:
        raise ValueError(f"missing requested feature columns for generic z-score rule: {missing}")
    if not available:
        raise ValueError("generic z-score rule requires at least one numeric feature column")
    scores = [
        _scored_column(features_df, col, reference_mask, reference_scope)
        for col in available
    ]
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
