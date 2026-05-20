from __future__ import annotations

import pandas as pd

from src.labeling.sph_sop import label_forecast_windows


def _require_columns(frame: pd.DataFrame, required: set[str], name: str) -> None:
    missing = sorted(required.difference(frame.columns))
    if missing:
        raise ValueError(f"{name} is missing required columns: {missing}")


def _events_coverable_by_valid_windows(
    labels: pd.DataFrame,
    events: pd.DataFrame,
    sph_minutes: float,
    sop_minutes: float,
) -> int:
    if labels.empty or events.empty:
        return 0
    valid = labels.loc[~labels["is_excluded"].fillna(False).astype(bool)].copy()
    if valid.empty:
        return 0
    valid["window_end"] = pd.to_datetime(valid["window_end"])
    ev = events.copy()
    ev["seizure_start"] = pd.to_datetime(ev["seizure_start"])
    sph = pd.Timedelta(minutes=sph_minutes)
    sop = pd.Timedelta(minutes=sop_minutes)

    coverable = 0
    for _, event in ev.iterrows():
        candidates = valid.loc[valid["patient_id"].astype(str).eq(str(event["patient_id"]))]
        if "recording_id" in valid.columns and "recording_id" in ev.columns:
            candidates = candidates.loc[
                candidates["recording_id"].astype(str).eq(str(event["recording_id"]))
            ]
        if candidates.empty:
            continue
        horizon_start = candidates["window_end"] + sph
        horizon_end = candidates["window_end"] + sph + sop
        if ((event["seizure_start"] >= horizon_start) & (event["seizure_start"] < horizon_end)).any():
            coverable += 1
    return coverable


def horizon_viability_summary(
    windows: pd.DataFrame,
    events: pd.DataFrame,
    sph_minutes_values: list[float],
    sop_minutes_values: list[float],
    postictal_exclusion_minutes: float = 60,
    postictal_anchor: str = "seizure_end",
) -> pd.DataFrame:
    """Summarize label and event coverage viability for candidate SPH/SOP horizons."""
    _require_columns(windows, {"patient_id", "window_start", "window_end", "recording_end"}, "windows")
    _require_columns(events, {"patient_id", "seizure_start", "seizure_end"}, "events")
    rows = []
    for sph_minutes in sph_minutes_values:
        for sop_minutes in sop_minutes_values:
            labels = label_forecast_windows(
                windows,
                events,
                sph_minutes=sph_minutes,
                sop_minutes=sop_minutes,
                postictal_exclusion_minutes=postictal_exclusion_minutes,
                require_recording_end=True,
                postictal_anchor=postictal_anchor,
            )
            excluded = labels["is_excluded"].fillna(False).astype(bool)
            forecast = labels["forecast_label"].fillna(False).astype(bool)
            right_censored = labels["is_right_censored"].fillna(False).astype(bool)
            valid = ~excluded
            events_coverable = _events_coverable_by_valid_windows(
                labels,
                events,
                sph_minutes=sph_minutes,
                sop_minutes=sop_minutes,
            )
            row: dict[str, object] = {
                "sph_minutes": sph_minutes,
                "sop_minutes": sop_minutes,
                "windows_total": len(labels),
                "valid_windows": int(valid.sum()),
                "valid_window_fraction": float(valid.mean()) if len(valid) else float("nan"),
                "excluded_windows": int(excluded.sum()),
                "positive_windows_total": int(forecast.sum()),
                "valid_positive_windows": int((forecast & valid).sum()),
                "right_censored_windows": int(right_censored.sum()),
                "right_censored_unknown_windows": int((right_censored & ~forecast).sum()),
                "right_censored_confirmed_positive_windows": int((right_censored & forecast).sum()),
                "events_total": len(events),
                "events_coverable_by_valid_windows": events_coverable,
                "event_coverable_fraction": (
                    events_coverable / len(events) if len(events) else float("nan")
                ),
            }
            if "recording_match_status" in events.columns:
                statuses = events["recording_match_status"].value_counts().to_dict()
                row["events_recording_matched"] = int(statuses.get("matched", 0))
                row["events_recording_unmatched"] = int(statuses.get("unmatched", 0))
            rows.append(row)
    return pd.DataFrame(rows)


def horizon_viability_markdown(
    summary: pd.DataFrame,
    title: str = "Horizon Viability Summary",
) -> str:
    """Render a horizon viability summary with explicit non-claim language."""

    def cell(value: object) -> str:
        if pd.isna(value):
            return ""
        if isinstance(value, float):
            if value.is_integer():
                return str(int(value))
            return f"{value:.3f}"
        return str(value)

    if summary.empty:
        table = "_No rows._"
    else:
        headers = [str(c) for c in summary.columns]
        lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
        for _, row in summary.iterrows():
            lines.append("| " + " | ".join(cell(row[col]) for col in summary.columns) + " |")
        table = "\n".join(lines)

    return "\n".join(
        [
            f"# {title}",
            "",
            "This is a feasibility audit for candidate SPH/SOP horizons, not a model result.",
            "",
            "Interpretation rules:",
            "",
            "- Low valid-window fraction means the horizon is poorly supported by recording duration.",
            "- Low event-coverable fraction means many annotated seizures cannot enter event metrics.",
            "- Right-censored unknown windows must not be silently treated as negatives.",
            "- Confirmed positives that are right-censored are counted separately for manual review.",
            "",
            table,
            "",
            "A horizon with poor coverage can still be useful as a documented negative or exploratory",
            "analysis, but it should not anchor the main paper table without advisor approval.",
        ]
    )
