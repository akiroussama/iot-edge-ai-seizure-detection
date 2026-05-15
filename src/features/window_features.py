from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class FeatureConfig:
    """Feature extraction configuration for fast, interpretable baselines.

    This module intentionally uses simple statistics. It is not meant to be the final model;
    it gives reviewers and clinicians transparent baselines before deep models are trained.
    """

    signal_column: str = "value"
    time_column: str = "timestamp"
    patient_column: str = "patient_id"
    window_start_column: str = "window_start"
    window_end_column: str = "window_end"


def _safe_stats(values: np.ndarray, prefix: str) -> dict[str, float]:
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    if values.size == 0:
        return {
            f"{prefix}_mean": np.nan,
            f"{prefix}_std": np.nan,
            f"{prefix}_min": np.nan,
            f"{prefix}_max": np.nan,
            f"{prefix}_median": np.nan,
            f"{prefix}_mad": np.nan,
            f"{prefix}_slope": np.nan,
            f"{prefix}_energy": np.nan,
        }
    x = np.arange(values.size, dtype=float)
    slope = np.polyfit(x, values, 1)[0] if values.size > 1 else 0.0
    med = float(np.median(values))
    return {
        f"{prefix}_mean": float(np.mean(values)),
        f"{prefix}_std": float(np.std(values)),
        f"{prefix}_min": float(np.min(values)),
        f"{prefix}_max": float(np.max(values)),
        f"{prefix}_median": med,
        f"{prefix}_mad": float(np.median(np.abs(values - med))),
        f"{prefix}_slope": float(slope),
        f"{prefix}_energy": float(np.mean(values * values)),
    }


def extract_window_features(
    samples: pd.DataFrame,
    windows: pd.DataFrame,
    modalities: Iterable[str] | None = None,
    config: FeatureConfig | None = None,
) -> pd.DataFrame:
    """Extract simple per-window features from long-form samples.

    Expected samples columns:
    - patient_id
    - timestamp
    - modality
    - value

    Expected windows columns:
    - patient_id
    - window_start
    - window_end

    The function is deliberately conservative and CPU-friendly. It supports synthetic demos and
    simple HR/steps/ACC features while the raw SeizeIT2 parser is being connected.
    """
    cfg = config or FeatureConfig()
    required_samples = {cfg.patient_column, cfg.time_column, "modality", cfg.signal_column}
    required_windows = {cfg.patient_column, cfg.window_start_column, cfg.window_end_column}
    missing_s = required_samples - set(samples.columns)
    missing_w = required_windows - set(windows.columns)
    if missing_s:
        raise ValueError(f"samples missing columns: {sorted(missing_s)}")
    if missing_w:
        raise ValueError(f"windows missing columns: {sorted(missing_w)}")

    samples = samples.copy()
    windows = windows.copy()
    samples[cfg.time_column] = pd.to_datetime(samples[cfg.time_column])
    windows[cfg.window_start_column] = pd.to_datetime(windows[cfg.window_start_column])
    windows[cfg.window_end_column] = pd.to_datetime(windows[cfg.window_end_column])
    selected_modalities = list(modalities) if modalities is not None else sorted(samples["modality"].dropna().unique())

    rows: list[dict[str, object]] = []
    samples_by_patient = {p: g.sort_values(cfg.time_column) for p, g in samples.groupby(cfg.patient_column)}
    for _, win in windows.iterrows():
        row = win.to_dict()
        patient_samples = samples_by_patient.get(win[cfg.patient_column])
        if patient_samples is None:
            for m in selected_modalities:
                row.update(_safe_stats(np.array([]), m))
            rows.append(row)
            continue
        mask_time = (patient_samples[cfg.time_column] >= win[cfg.window_start_column]) & (
            patient_samples[cfg.time_column] < win[cfg.window_end_column]
        )
        chunk = patient_samples.loc[mask_time]
        for modality in selected_modalities:
            values = chunk.loc[chunk["modality"].eq(modality), cfg.signal_column].to_numpy(dtype=float)
            row.update(_safe_stats(values, modality))
        rows.append(row)
    return pd.DataFrame(rows)


def make_feature_matrix(df: pd.DataFrame, id_columns: Iterable[str] | None = None) -> tuple[np.ndarray, list[str]]:
    """Return numeric feature matrix and feature names."""
    ids = set(id_columns or ["patient_id", "recording_id", "window_start", "window_end"])
    feature_cols = [c for c in df.columns if c not in ids and pd.api.types.is_numeric_dtype(df[c])]
    X = df[feature_cols].replace([np.inf, -np.inf], np.nan).fillna(0.0).to_numpy(dtype=np.float32)
    return X, feature_cols
