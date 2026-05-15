from __future__ import annotations

import pandas as pd

from src.metrics.alarm_metrics import _valid_predictions
from src.utils.time import ensure_datetime


def assign_event_clusters(
    events_df: pd.DataFrame,
    cluster_gap_minutes: float,
    preserve_recording_scope: bool = True,
) -> pd.DataFrame:
    """Assign seizure events to onset-gap clusters.

    Cluster IDs are computed within each patient, and within recording when ``recording_id`` is
    available and ``preserve_recording_scope`` is true. Preserving recording scope is the safer
    default because event metrics use ``recording_id`` to associate alarms with seizures.
    """
    if cluster_gap_minutes < 0:
        raise ValueError("cluster_gap_minutes must be non-negative")
    if events_df.empty:
        out = events_df.copy()
        out["cluster_id"] = pd.Series(dtype="string")
        out["cluster_position"] = pd.Series(dtype="int64")
        out["cluster_size"] = pd.Series(dtype="int64")
        return out
    required = {"patient_id", "seizure_start", "seizure_end"}
    missing = required - set(events_df.columns)
    if missing:
        raise ValueError(f"events_df missing required columns for clustering: {sorted(missing)}")
    events = events_df.copy()
    events["seizure_start"] = ensure_datetime(events["seizure_start"])
    events["seizure_end"] = ensure_datetime(events["seizure_end"])
    group_cols = ["patient_id"]
    if preserve_recording_scope and "recording_id" in events.columns:
        group_cols.append("recording_id")
    gap = pd.Timedelta(minutes=cluster_gap_minutes)
    frames = []
    for group_key, group in events.sort_values(group_cols + ["seizure_start"]).groupby(group_cols, sort=False):
        g = group.copy()
        cluster_numbers = []
        cluster_number = 0
        prev_start = None
        for start in g["seizure_start"]:
            if prev_start is not None and start - prev_start > gap:
                cluster_number += 1
            cluster_numbers.append(cluster_number)
            prev_start = start
        if not isinstance(group_key, tuple):
            group_key = (group_key,)
        prefix = "|".join(str(value) for value in group_key)
        g["cluster_id"] = [f"{prefix}|cluster-{number}" for number in cluster_numbers]
        g["cluster_position"] = g.groupby("cluster_id").cumcount()
        g["cluster_size"] = g.groupby("cluster_id")["cluster_id"].transform("size")
        frames.append(g)
    return pd.concat(frames).sort_index()


def collapse_event_clusters(
    events_df: pd.DataFrame,
    cluster_gap_minutes: float,
    preserve_recording_scope: bool = True,
) -> pd.DataFrame:
    """Collapse onset-gap seizure clusters to one metric event per cluster.

    The metric onset is the first seizure onset in the cluster. This makes cluster-level
    sensitivity a first-event forecasting metric and keeps later seizures in a cluster out of the
    event denominator.
    """
    clustered = assign_event_clusters(events_df, cluster_gap_minutes, preserve_recording_scope)
    if clustered.empty:
        return clustered
    rows = []
    base_cols = ["patient_id"] + (["recording_id"] if "recording_id" in clustered.columns else [])
    for cluster_id, group in clustered.sort_values(base_cols + ["seizure_start"]).groupby("cluster_id", sort=False):
        first = group.iloc[0].copy()
        first["seizure_start"] = group["seizure_start"].min()
        first["seizure_end"] = group["seizure_end"].max()
        first["cluster_id"] = cluster_id
        first["cluster_size"] = len(group)
        first["cluster_last_seizure_start"] = group["seizure_start"].max()
        first["event_unit"] = "cluster"
        rows.append(first)
    return pd.DataFrame(rows).reset_index(drop=True)


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
