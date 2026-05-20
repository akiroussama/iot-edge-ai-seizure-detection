from __future__ import annotations

from io import BytesIO
from pathlib import Path
from zipfile import BadZipFile, ZipFile

import numpy as np
import pandas as pd

from src.datasets.msg_loader import (
    _is_valid_zip,
    _nested_zip_patient_id,
    _recording_id_for_nested_zip,
)
from src.features.window_features import _safe_stats
from src.utils.time import ensure_datetime

EMPATICA_FEATURE_FILES = {
    "hr": "HR.csv",
    "acc": "ACC.csv",
}
FEATURE_SUFFIXES = ("mean", "std", "min", "max", "median", "mad", "slope", "energy")


def _read_empatica_stream(
    nested: ZipFile,
    modality: str,
) -> tuple[pd.Timestamp, float, np.ndarray] | None:
    filename = EMPATICA_FEATURE_FILES[modality]
    if filename not in nested.namelist():
        return None
    with nested.open(filename) as handle:
        start_line = handle.readline().decode("utf-8").strip()
        rate_line = handle.readline().decode("utf-8").strip()
        if not start_line or not rate_line:
            return None
        start = pd.to_datetime(float(start_line.split(",")[0]), unit="s", utc=True).tz_convert(None)
        sample_rate = float(rate_line.split(",")[0])
        table = pd.read_csv(handle, header=None)
    if table.empty or sample_rate <= 0:
        return start, sample_rate, np.asarray([], dtype=float)
    values = table.apply(pd.to_numeric, errors="coerce").to_numpy(dtype=float)
    if modality == "acc":
        if values.shape[1] < 3:
            return start, sample_rate, np.asarray([], dtype=float)
        signal = np.linalg.norm(values[:, :3], axis=1)
    else:
        signal = values[:, 0]
    signal = signal[np.isfinite(signal)]
    return start, sample_rate, signal.astype(float)


def _initialize_feature_columns(features: pd.DataFrame, modalities: list[str]) -> None:
    for modality in modalities:
        for suffix in FEATURE_SUFFIXES:
            features[f"{modality}_{suffix}"] = np.nan


def _fill_window_stats(
    features: pd.DataFrame,
    indices: pd.Index,
    stream_start: pd.Timestamp,
    sample_rate: float,
    values: np.ndarray,
    modality: str,
) -> None:
    if sample_rate <= 0:
        return
    n = len(values)
    for idx in indices:
        win = features.loc[idx]
        start_offset = (win["window_start"] - stream_start).total_seconds()
        end_offset = (win["window_end"] - stream_start).total_seconds()
        lo = max(0, int(np.floor(start_offset * sample_rate)))
        hi = min(n, int(np.ceil(end_offset * sample_rate)))
        chunk = values[lo:hi] if hi > lo else np.asarray([], dtype=float)
        for key, value in _safe_stats(chunk, modality).items():
            features.at[idx, key] = value


def extract_msg_empatica_window_features(
    raw_root: str | Path,
    windows_df: pd.DataFrame,
    modalities: tuple[str, ...] | list[str] = ("hr", "acc"),
    max_recordings: int | None = None,
) -> pd.DataFrame:
    """Extract simple HR/ACC statistics for MSG windows from nested Empatica ZIP files.

    The function streams one nested Empatica archive at a time and writes per-window summary
    statistics. It intentionally avoids materializing all raw wearable samples into one long table.
    """
    selected = [m.lower() for m in modalities]
    unsupported = sorted(set(selected) - set(EMPATICA_FEATURE_FILES))
    if unsupported:
        raise ValueError(f"unsupported MSG Empatica modalities: {unsupported}")
    if "recording_id" not in windows_df.columns:
        raise ValueError("windows_df must contain recording_id for MSG Empatica feature extraction")
    if not {"window_start", "window_end"}.issubset(windows_df.columns):
        raise ValueError("windows_df must contain window_start and window_end")

    root = Path(raw_root)
    if not root.exists():
        raise FileNotFoundError(f"MSG raw root does not exist: {root}")

    features = windows_df.copy()
    features["window_start"] = ensure_datetime(features["window_start"])
    features["window_end"] = ensure_datetime(features["window_end"])
    _initialize_feature_columns(features, selected)

    by_recording = {
        str(recording_id): group.index
        for recording_id, group in features.groupby("recording_id", sort=False)
    }
    processed_recordings = 0
    for outer_path in sorted(root.glob("*.zip")):
        if not _is_valid_zip(outer_path):
            continue
        with ZipFile(outer_path) as outer:
            nested_zip_names = sorted(name for name in outer.namelist() if name.lower().endswith(".zip"))
            for nested_name in nested_zip_names:
                patient_id = _nested_zip_patient_id(outer_path, nested_name)
                recording_id = _recording_id_for_nested_zip(patient_id, nested_name)
                indices = by_recording.get(recording_id)
                if indices is None or len(indices) == 0:
                    continue
                try:
                    nested_bytes = outer.read(nested_name)
                    with ZipFile(BytesIO(nested_bytes)) as nested:
                        for modality in selected:
                            stream = _read_empatica_stream(nested, modality)
                            if stream is None:
                                continue
                            stream_start, sample_rate, values = stream
                            _fill_window_stats(features, indices, stream_start, sample_rate, values, modality)
                except BadZipFile as exc:
                    raise ValueError(f"{outer_path.name}:{nested_name} is not a valid nested ZIP") from exc
                processed_recordings += 1
                if max_recordings is not None and processed_recordings >= max_recordings:
                    features["feature_recordings_processed"] = processed_recordings
                    return features
    features["feature_recordings_processed"] = processed_recordings
    return features
