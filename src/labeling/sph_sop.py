from __future__ import annotations

import numpy as np
import pandas as pd

from src.utils.time import ensure_datetime

REQUIRED_WINDOW_COLUMNS = {"patient_id", "window_start", "window_end"}
REQUIRED_EVENT_COLUMNS = {"patient_id", "seizure_start", "seizure_end"}


def _validate_columns(df: pd.DataFrame, required: set[str], name: str) -> None:
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"{name} missing required columns: {sorted(missing)}")


def _has_recording_scope(windows_df: pd.DataFrame, events_df: pd.DataFrame) -> bool:
    return "recording_id" in windows_df.columns and "recording_id" in events_df.columns


def label_forecast_windows(
    windows_df: pd.DataFrame,
    events_df: pd.DataFrame,
    sph_minutes: float,
    sop_minutes: float,
    postictal_exclusion_minutes: float = 60,
    ictal_exclusion: bool = True,
) -> pd.DataFrame:
    """Label windows for seizure forecasting using SPH/SOP.

    A window ending at time t is positive if a seizure onset falls in:
    [t + SPH, t + SPH + SOP)

    Ictal and postictal windows are marked with ``is_excluded`` so downstream metrics can
    ignore them. The raw forecast label is still computed for transparency.
    """
    _validate_columns(windows_df, REQUIRED_WINDOW_COLUMNS, "windows_df")
    _validate_columns(events_df, REQUIRED_EVENT_COLUMNS, "events_df")

    out = windows_df.copy()
    events = events_df.copy()

    for col in ("window_start", "window_end"):
        out[col] = ensure_datetime(out[col])
    for col in ("seizure_start", "seizure_end"):
        events[col] = ensure_datetime(events[col])

    out = out.sort_values(["patient_id", "window_start", "window_end"]).reset_index(drop=True)
    events = events.sort_values(["patient_id", "seizure_start"]).reset_index(drop=True)

    sph = pd.Timedelta(minutes=sph_minutes)
    sop = pd.Timedelta(minutes=sop_minutes)
    postictal = pd.Timedelta(minutes=postictal_exclusion_minutes)

    out["time_to_next_seizure_seconds"] = np.nan
    out["time_since_last_seizure_seconds"] = np.nan
    out["is_ictal"] = False
    out["is_postictal"] = False
    out["forecast_label"] = False

    use_recording = _has_recording_scope(out, events)
    group_cols = ["patient_id"] + (["recording_id"] if use_recording else [])

    for _, group in out.groupby(group_cols, sort=False):
        idx = group.index
        mask = events["patient_id"].eq(group.iloc[0]["patient_id"])
        if use_recording:
            mask &= events["recording_id"].eq(group.iloc[0]["recording_id"])
        ev = events.loc[mask].sort_values("seizure_start")
        if ev.empty:
            continue

        starts = ev["seizure_start"].to_numpy(dtype="datetime64[ns]")
        ends = ev["seizure_end"].to_numpy(dtype="datetime64[ns]")
        window_starts = group["window_start"].to_numpy(dtype="datetime64[ns]")
        window_ends = group["window_end"].to_numpy(dtype="datetime64[ns]")

        # Time to next seizure onset after the window end.
        next_pos = np.searchsorted(starts, window_ends, side="left")
        valid_next = next_pos < len(starts)
        ttn = np.full(len(group), np.nan, dtype=float)
        ttn[valid_next] = (starts[next_pos[valid_next]] - window_ends[valid_next]) / np.timedelta64(1, "s")
        out.loc[idx, "time_to_next_seizure_seconds"] = ttn

        # Time since last completed seizure end.
        prev_end_pos = np.searchsorted(ends, window_ends, side="right") - 1
        valid_prev = prev_end_pos >= 0
        tsl = np.full(len(group), np.nan, dtype=float)
        tsl[valid_prev] = (window_ends[valid_prev] - ends[prev_end_pos[valid_prev]]) / np.timedelta64(1, "s")
        out.loc[idx, "time_since_last_seizure_seconds"] = tsl

        # Ictal windows: overlap any seizure interval.
        ictal = np.zeros(len(group), dtype=bool)
        post = np.zeros(len(group), dtype=bool)
        label = np.zeros(len(group), dtype=bool)

        for s, e in zip(starts, ends, strict=True):
            ictal |= (window_starts < e) & (window_ends > s)
            post_start = e
            post_end = e + postictal.to_timedelta64()
            post |= (window_starts < post_end) & (window_ends > post_start)
            horizon_start = window_ends + sph.to_timedelta64()
            horizon_end = window_ends + sph.to_timedelta64() + sop.to_timedelta64()
            label |= (s >= horizon_start) & (s < horizon_end)

        out.loc[idx, "is_ictal"] = ictal
        out.loc[idx, "is_postictal"] = post
        out.loc[idx, "forecast_label"] = label

    out["is_excluded"] = out["is_postictal"] | (out["is_ictal"] if ictal_exclusion else False)
    # Keep booleans as bool dtype.
    for col in ("is_ictal", "is_postictal", "forecast_label", "is_excluded"):
        out[col] = out[col].astype(bool)
    return out
