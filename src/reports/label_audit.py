from __future__ import annotations

import pandas as pd

from src.utils.time import ensure_datetime


def build_label_audit_table(
    labels_df: pd.DataFrame,
    events_df: pd.DataFrame,
    minutes_before: float = 60,
    minutes_after: float = 60,
) -> pd.DataFrame:
    """Build seizure-centered window timeline rows for human label audits."""
    if events_df.empty:
        return pd.DataFrame()
    labels = labels_df.copy()
    events = events_df.copy()
    for col in ("window_start", "window_end"):
        labels[col] = ensure_datetime(labels[col])
    for col in ("seizure_start", "seizure_end"):
        events[col] = ensure_datetime(events[col])

    rows = []
    before = pd.Timedelta(minutes=minutes_before)
    after = pd.Timedelta(minutes=minutes_after)
    for event_idx, event in events.sort_values(["patient_id", "seizure_start"]).iterrows():
        mask = labels["patient_id"].eq(event["patient_id"])
        if "recording_id" in labels.columns and "recording_id" in events.columns:
            mask &= labels["recording_id"].eq(event["recording_id"])
        mask &= labels["window_end"].between(event["seizure_start"] - before, event["seizure_start"] + after)
        context = labels.loc[mask].sort_values("window_end")
        for _, win in context.iterrows():
            state = "valid_negative"
            if bool(win.get("is_ictal", False)):
                state = "ictal_excluded" if bool(win.get("is_excluded", False)) else "ictal_not_excluded"
            elif bool(win.get("is_postictal", False)):
                state = (
                    "postictal_excluded"
                    if bool(win.get("is_excluded", False))
                    else "postictal_not_excluded"
                )
            elif bool(win.get("forecast_label", False)):
                state = "forecast_positive"
            rows.append(
                {
                    "event_index": event_idx,
                    "patient_id": event["patient_id"],
                    "recording_id": event.get("recording_id"),
                    "seizure_start": event["seizure_start"],
                    "seizure_end": event["seizure_end"],
                    "window_start": win["window_start"],
                    "window_end": win["window_end"],
                    "minutes_to_seizure": (
                        event["seizure_start"] - win["window_end"]
                    ).total_seconds()
                    / 60.0,
                    "forecast_label": bool(win.get("forecast_label", False)),
                    "is_ictal": bool(win.get("is_ictal", False)),
                    "is_postictal": bool(win.get("is_postictal", False)),
                    "is_excluded": bool(win.get("is_excluded", False)),
                    "audit_state": state,
                }
            )
    return pd.DataFrame(rows)
