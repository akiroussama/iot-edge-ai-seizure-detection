from __future__ import annotations

import numpy as np
import pandas as pd

from src.utils.time import ensure_datetime

REVIEW_SHEET_COLUMNS = [
    "event_index",
    "patient_id",
    "recording_id",
    "seizure_start",
    "seizure_end",
    "timeline_rows",
    "min_minutes_to_seizure",
    "max_minutes_to_seizure",
    "forecast_positive_rows",
    "valid_forecast_positive_rows",
    "ictal_excluded_rows",
    "postictal_excluded_rows",
    "right_censored_rows",
    "right_censoring_field_present",
    "unexpected_ictal_not_excluded_rows",
    "unexpected_postictal_not_excluded_rows",
    "reviewer",
    "source_onset_verified",
    "source_recording_verified",
    "sph_sop_labels_pass",
    "ictal_exclusion_pass",
    "postictal_exclusion_pass",
    "right_censoring_pass",
    "decision",
    "notes",
]


def _bool_series(df: pd.DataFrame, column: str, default: bool = False) -> pd.Series:
    """Return a robust boolean series for CSV/parquet audit inputs."""
    if column not in df.columns:
        return pd.Series(default, index=df.index, dtype=bool)
    series = df[column]
    if pd.api.types.is_bool_dtype(series):
        return series.fillna(default).astype(bool)
    if pd.api.types.is_numeric_dtype(series):
        return series.fillna(int(default)).astype(bool)
    normalized = series.astype("string").str.strip().str.lower()
    out = pd.Series(default, index=df.index, dtype=bool)
    out[normalized.isin({"true", "1", "yes", "y"})] = True
    out[normalized.isin({"false", "0", "no", "n", "", "nan", "<na>"})] = False
    return out


def _select_event_keys(
    event_keys: pd.DataFrame,
    max_events: int | None,
    strategy: str,
) -> pd.DataFrame:
    if max_events is None:
        return event_keys
    if strategy == "first":
        return event_keys.head(max_events)
    if strategy != "patient_spread":
        raise ValueError("selection_strategy must be 'patient_spread' or 'first'")

    grouped = {patient_id: group for patient_id, group in event_keys.groupby("patient_id", sort=True)}
    positions = {patient_id: 0 for patient_id in grouped}
    selected = []
    while len(selected) < max_events:
        progressed = False
        for patient_id, group in grouped.items():
            pos = positions[patient_id]
            if pos >= len(group):
                continue
            selected.append(group.iloc[pos])
            positions[patient_id] = pos + 1
            progressed = True
            if len(selected) >= max_events:
                break
        if not progressed:
            break
    return pd.DataFrame(selected).reset_index(drop=True)


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
                    "is_right_censored": bool(win.get("is_right_censored", False)),
                    "is_excluded": bool(win.get("is_excluded", False)),
                    "audit_state": state,
                }
            )
    return pd.DataFrame(rows)


def build_label_audit_review_sheet(
    audit_df: pd.DataFrame,
    max_events: int | None = 10,
    selection_strategy: str = "patient_spread",
) -> pd.DataFrame:
    """Summarize timeline audit rows into one human-review checklist row per event.

    The sheet is deliberately not an automated pass/fail gate. It precomputes obvious
    anomaly counts while leaving the clinical source checks and final decision blank for
    a reviewer to fill after comparing each timeline with the raw annotation source.
    """
    if max_events is not None and max_events <= 0:
        raise ValueError("max_events must be positive or None")
    if audit_df.empty:
        return pd.DataFrame(columns=REVIEW_SHEET_COLUMNS)

    required = {"event_index", "patient_id", "seizure_start", "seizure_end", "minutes_to_seizure"}
    missing = required - set(audit_df.columns)
    if missing:
        raise ValueError(f"audit_df missing required columns: {sorted(missing)}")

    audit = audit_df.copy()
    audit["seizure_start"] = ensure_datetime(audit["seizure_start"])
    audit["seizure_end"] = ensure_datetime(audit["seizure_end"])
    if "window_end" in audit.columns:
        audit["window_end"] = ensure_datetime(audit["window_end"])
    if "recording_id" not in audit.columns:
        audit["recording_id"] = pd.NA

    sort_cols = ["patient_id", "recording_id", "seizure_start", "event_index"]
    if "window_end" in audit.columns:
        sort_cols.append("window_end")
    audit = audit.sort_values(sort_cols).reset_index(drop=True)

    event_keys = audit[["event_index", "patient_id", "recording_id", "seizure_start"]].drop_duplicates()
    event_keys = _select_event_keys(event_keys, max_events, selection_strategy)

    rows = []
    right_censoring_field_present = "is_right_censored" in audit.columns
    for _, event_key in event_keys.iterrows():
        group = audit[audit["event_index"].eq(event_key["event_index"])].copy()
        forecast = _bool_series(group, "forecast_label")
        excluded = _bool_series(group, "is_excluded")
        ictal = _bool_series(group, "is_ictal")
        postictal = _bool_series(group, "is_postictal")
        right_censored = _bool_series(group, "is_right_censored")
        minutes_to_seizure = pd.to_numeric(group["minutes_to_seizure"], errors="coerce")

        first = group.iloc[0]
        rows.append(
            {
                "event_index": first["event_index"],
                "patient_id": first["patient_id"],
                "recording_id": first.get("recording_id"),
                "seizure_start": first["seizure_start"],
                "seizure_end": first["seizure_end"],
                "timeline_rows": int(len(group)),
                "min_minutes_to_seizure": (
                    float(minutes_to_seizure.min()) if not minutes_to_seizure.isna().all() else np.nan
                ),
                "max_minutes_to_seizure": (
                    float(minutes_to_seizure.max()) if not minutes_to_seizure.isna().all() else np.nan
                ),
                "forecast_positive_rows": int(forecast.sum()),
                "valid_forecast_positive_rows": int((forecast & ~excluded).sum()),
                "ictal_excluded_rows": int((ictal & excluded).sum()),
                "postictal_excluded_rows": int((postictal & excluded).sum()),
                "right_censored_rows": (
                    int(right_censored.sum()) if right_censoring_field_present else np.nan
                ),
                "right_censoring_field_present": bool(right_censoring_field_present),
                "unexpected_ictal_not_excluded_rows": int((ictal & ~excluded).sum()),
                "unexpected_postictal_not_excluded_rows": int((postictal & ~excluded).sum()),
                "reviewer": "",
                "source_onset_verified": "",
                "source_recording_verified": "",
                "sph_sop_labels_pass": "",
                "ictal_exclusion_pass": "",
                "postictal_exclusion_pass": "",
                "right_censoring_pass": "",
                "decision": "",
                "notes": "",
            }
        )

    return pd.DataFrame(rows, columns=REVIEW_SHEET_COLUMNS)
