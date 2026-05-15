from __future__ import annotations

import pandas as pd


def dataset_summary(windows_df: pd.DataFrame, events_df: pd.DataFrame) -> pd.DataFrame:
    """Return a compact dataset summary table."""
    hours = 0.0
    if not windows_df.empty:
        starts = pd.to_datetime(windows_df["window_start"])
        ends = pd.to_datetime(windows_df["window_end"])
        hours = float(((ends - starts).dt.total_seconds().sum()) / 3600.0)
    return pd.DataFrame(
        [
            {
                "patients": windows_df["patient_id"].nunique() if "patient_id" in windows_df else 0,
                "recordings": windows_df["recording_id"].nunique() if "recording_id" in windows_df else 0,
                "windows": len(windows_df),
                "events": len(events_df),
                "window_hours_sum": hours,
            }
        ]
    )


def label_distribution(labeled_windows_df: pd.DataFrame) -> pd.DataFrame:
    valid = labeled_windows_df.loc[~labeled_windows_df.get("is_excluded", False)]
    return pd.DataFrame(
        [
            {
                "total_windows": len(labeled_windows_df),
                "valid_windows": len(valid),
                "excluded_windows": int(labeled_windows_df.get("is_excluded", pd.Series(False)).sum()),
                "positive_windows": int(valid.get("forecast_label", pd.Series(False)).sum()),
                "positive_fraction_valid": float(valid.get("forecast_label", pd.Series(dtype=bool)).mean()) if len(valid) else float("nan"),
            }
        ]
    )
