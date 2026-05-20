from __future__ import annotations

import math
from collections.abc import Iterable

import pandas as pd

from src.utils.time import ensure_datetime

REQUIRED_RECORDING_COLUMNS = {"patient_id", "recording_id", "recording_start", "recording_end"}


def _validate_recordings(recordings_df: pd.DataFrame) -> None:
    missing = REQUIRED_RECORDING_COLUMNS - set(recordings_df.columns)
    if missing:
        raise ValueError(f"recordings_df missing required columns: {sorted(missing)}")


def _infer_time_unit(series: pd.Series) -> str:
    if pd.api.types.is_datetime64_any_dtype(series) or pd.api.types.is_object_dtype(series):
        converted = pd.to_datetime(series, errors="coerce")
        if converted.notna().all():
            return "datetime"
    if pd.api.types.is_numeric_dtype(series):
        return "seconds"
    raise ValueError("recording_start/recording_end must be datetimes or numeric seconds")


def _copy_metadata(row: pd.Series, columns: Iterable[str]) -> dict:
    return {col: row[col] for col in columns if col in row.index}


def generate_fixed_windows(
    recordings_df: pd.DataFrame,
    window_duration: str | pd.Timedelta = "2min",
    stride: str | pd.Timedelta = "30s",
    carry_columns: Iterable[str] = (
        "recording_start",
        "recording_end",
        "center_id",
        "source_dataset",
        "modalities_available",
    ),
) -> pd.DataFrame:
    """Generate deterministic fixed windows within each recording.

    Required input columns are ``patient_id``, ``recording_id``, ``recording_start`` and
    ``recording_end``. Times may be pandas-compatible datetimes or numeric seconds, but a single
    call must not mix the two. Generated windows never cross recording boundaries.
    """
    _validate_recordings(recordings_df)
    if recordings_df.empty:
        return pd.DataFrame(
            columns=["patient_id", "recording_id", "window_start", "window_end", *carry_columns]
        )

    unit = _infer_time_unit(recordings_df["recording_start"])
    out = recordings_df.copy()
    duration = pd.Timedelta(window_duration)
    step = pd.Timedelta(stride)
    if duration <= pd.Timedelta(0) or step <= pd.Timedelta(0):
        raise ValueError("window_duration and stride must be positive")

    if unit == "datetime":
        out["recording_start"] = ensure_datetime(out["recording_start"])
        out["recording_end"] = ensure_datetime(out["recording_end"])
        duration_value = duration
        step_value = step
    else:
        out["recording_start"] = out["recording_start"].astype(float)
        out["recording_end"] = out["recording_end"].astype(float)
        duration_value = duration.total_seconds()
        step_value = step.total_seconds()

    rows: list[dict] = []
    sort_cols = ["patient_id", "recording_id", "recording_start", "recording_end"]
    for _, rec in out.sort_values(sort_cols).iterrows():
        start = rec["recording_start"]
        end = rec["recording_end"]
        if end <= start:
            raise ValueError(
                f"recording {rec['patient_id']}/{rec['recording_id']} has non-positive duration"
            )
        span = end - start
        if span < duration_value:
            continue
        if unit == "datetime":
            n_windows = math.floor((span - duration_value) / step_value) + 1
        else:
            n_windows = math.floor((float(span) - duration_value) / step_value) + 1
        base = {
            "patient_id": rec["patient_id"],
            "recording_id": rec["recording_id"],
            **_copy_metadata(rec, carry_columns),
        }
        for i in range(n_windows):
            window_start = start + i * step_value
            window_end = window_start + duration_value
            if window_end > end:
                break
            rows.append({**base, "window_start": window_start, "window_end": window_end})

    columns = ["patient_id", "recording_id", "window_start", "window_end"]
    seen = set(columns)
    for col in carry_columns:
        if col not in seen and col in recordings_df.columns:
            columns.append(col)
            seen.add(col)
    return pd.DataFrame(rows, columns=columns).sort_values(columns[:4]).reset_index(drop=True)
