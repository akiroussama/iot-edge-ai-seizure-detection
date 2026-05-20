from __future__ import annotations

import pandas as pd


def mark_postictal_windows(
    windows_df: pd.DataFrame,
    events_df: pd.DataFrame,
    postictal_exclusion_minutes: float,
) -> pd.Series:
    """Return a boolean series indicating windows overlapping the postictal exclusion zone."""
    if windows_df.empty:
        return pd.Series(dtype=bool, index=windows_df.index)
    if events_df.empty:
        return pd.Series(False, index=windows_df.index)

    postictal = pd.Series(False, index=windows_df.index)
    duration = pd.Timedelta(minutes=postictal_exclusion_minutes)

    group_cols = ["patient_id"] + (["recording_id"] if "recording_id" in windows_df.columns and "recording_id" in events_df.columns else [])
    for _, event in events_df.iterrows():
        mask = windows_df["patient_id"].eq(event["patient_id"])
        if "recording_id" in group_cols:
            mask &= windows_df["recording_id"].eq(event["recording_id"])
        post_start = event["seizure_end"]
        post_end = event["seizure_end"] + duration
        overlaps = windows_df["window_start"].lt(post_end) & windows_df["window_end"].gt(post_start)
        postictal |= mask & overlaps
    return postictal
