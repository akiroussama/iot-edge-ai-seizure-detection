from __future__ import annotations

import pandas as pd

from src.metrics.alarm_metrics import _valid_predictions
from src.utils.time import ensure_datetime


def event_forecast_details(
    predictions_df: pd.DataFrame,
    events_df: pd.DataFrame,
    sph_minutes: float,
    sop_minutes: float,
) -> list[dict]:
    """Return per-event forecast status and lead time.

    An event is forecasted if at least one alarm window end t satisfies:
    seizure_start in [t + SPH, t + SPH + SOP)
    """
    preds = _valid_predictions(predictions_df)
    events = events_df.copy()
    if events.empty:
        return []
    events["seizure_start"] = ensure_datetime(events["seizure_start"])
    events["seizure_end"] = ensure_datetime(events["seizure_end"])
    sph = pd.Timedelta(minutes=sph_minutes)
    sop = pd.Timedelta(minutes=sop_minutes)

    details: list[dict] = []
    alarms = preds.loc[preds["alarm"]].copy()
    for event_idx, event in events.sort_values(["patient_id", "seizure_start"]).iterrows():
        ev_alarms = alarms.loc[alarms["patient_id"].eq(event["patient_id"])]
        if "recording_id" in alarms.columns and "recording_id" in events.columns:
            ev_alarms = ev_alarms.loc[ev_alarms["recording_id"].eq(event["recording_id"])]
        valid = []
        for _, row in ev_alarms.iterrows():
            h0 = row["window_end"] + sph
            h1 = row["window_end"] + sph + sop
            if event["seizure_start"] >= h0 and event["seizure_start"] < h1:
                valid.append(row)
        if valid:
            # First alarm = largest lead time; this is clinically meaningful advance warning.
            first_alarm = min(valid, key=lambda r: r["window_end"])
            lead = (event["seizure_start"] - first_alarm["window_end"]).total_seconds()
            forecasted = True
        else:
            lead = None
            forecasted = False
        details.append(
            {
                "event_index": event_idx,
                "patient_id": event["patient_id"],
                "recording_id": event.get("recording_id"),
                "seizure_start": event["seizure_start"],
                "forecasted": forecasted,
                "lead_time_seconds": lead,
            }
        )
    return details


def event_level_sensitivity(
    predictions_df: pd.DataFrame,
    events_df: pd.DataFrame,
    sph_minutes: float,
    sop_minutes: float,
) -> dict[str, float | int]:
    details = event_forecast_details(predictions_df, events_df, sph_minutes, sop_minutes)
    n_events = len(details)
    n_forecasted = sum(1 for d in details if d["forecasted"])
    sensitivity = n_forecasted / n_events if n_events else float("nan")
    return {"n_events": n_events, "n_forecasted": n_forecasted, "sensitivity": sensitivity}
