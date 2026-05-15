from __future__ import annotations

import pandas as pd


def _require_columns(frame: pd.DataFrame, required: set[str], name: str) -> None:
    missing = sorted(required.difference(frame.columns))
    if missing:
        raise ValueError(f"{name} is missing required columns: {missing}")


def event_coverage_summary(events: pd.DataFrame, recordings: pd.DataFrame | None = None) -> pd.DataFrame:
    """Summarize per-patient seizure event coverage by available wearable recordings.

    This is an audit aid. A low matched fraction means events exist in the seizure-time file but
    cannot currently be associated with a parsed wearable recording interval, so those events should
    not silently enter model denominators.
    """
    if events.empty:
        return pd.DataFrame()
    _require_columns(events, {"patient_id", "seizure_start"}, "events")
    ev = events.copy()
    if "recording_match_status" not in ev.columns:
        ev["recording_match_status"] = "unknown"
    ev["seizure_start"] = pd.to_datetime(ev["seizure_start"])
    rows = []
    recording_counts = {}
    recording_hours = {}
    if recordings is not None and not recordings.empty:
        _require_columns(recordings, {"patient_id", "recording_id", "recording_start", "recording_end"}, "recordings")
        rec = recordings.copy()
        rec["recording_start"] = pd.to_datetime(rec["recording_start"])
        rec["recording_end"] = pd.to_datetime(rec["recording_end"])
        recording_counts = rec.groupby("patient_id")["recording_id"].nunique().to_dict()
        recording_hours = (
            ((rec["recording_end"] - rec["recording_start"]).dt.total_seconds() / 3600.0)
            .groupby(rec["patient_id"])
            .sum()
            .to_dict()
        )
    for patient, group in ev.groupby("patient_id"):
        statuses = group["recording_match_status"].value_counts().to_dict()
        total = len(group)
        matched = int(statuses.get("matched", 0))
        unmatched = int(statuses.get("unmatched", 0))
        unknown = total - matched - unmatched
        matched_fraction = matched / total if total else float("nan")
        rows.append(
            {
                "patient_id": patient,
                "events_total": total,
                "events_matched": matched,
                "events_unmatched": unmatched,
                "events_unknown": unknown,
                "matched_fraction": matched_fraction,
                "recordings": int(recording_counts.get(patient, 0)),
                "recording_hours": float(recording_hours.get(patient, 0.0)),
                "first_seizure_start": group["seizure_start"].min(),
                "last_seizure_start": group["seizure_start"].max(),
                "manual_review_priority": "high" if matched_fraction < 0.8 or unmatched > 0 else "routine",
            }
        )
    return pd.DataFrame(rows).sort_values("patient_id").reset_index(drop=True)


def event_cluster_summary(events: pd.DataFrame, cluster_gap_minutes: float = 240) -> pd.DataFrame:
    """Summarize seizure clusters per patient using onset-to-onset gaps.

    Two seizures are treated as part of the same cluster when the onset-to-onset gap is less than or
    equal to ``cluster_gap_minutes``. The summary is used to flag cases where event-level metrics may
    be sensitive to postictal exclusion and cluster handling.
    """
    if events.empty:
        return pd.DataFrame()
    _require_columns(events, {"patient_id", "seizure_start"}, "events")
    ev = events.copy()
    ev["seizure_start"] = pd.to_datetime(ev["seizure_start"])
    rows = []
    gap = pd.Timedelta(minutes=cluster_gap_minutes)
    for patient, group in ev.sort_values(["patient_id", "seizure_start"]).groupby("patient_id"):
        cluster_ids = []
        cluster_id = 0
        prev_start = None
        for start in group["seizure_start"]:
            if prev_start is not None and start - prev_start > gap:
                cluster_id += 1
            cluster_ids.append(cluster_id)
            prev_start = start
        sizes = pd.Series(cluster_ids).value_counts()
        rows.append(
            {
                "patient_id": patient,
                "events_total": len(group),
                "clusters": int(sizes.size),
                "clustered_events": int(sizes.loc[sizes > 1].sum()) if not sizes.empty else 0,
                "max_cluster_size": int(sizes.max()) if not sizes.empty else 0,
                "mean_events_per_cluster": float(sizes.mean()) if not sizes.empty else 0.0,
                "cluster_gap_minutes": cluster_gap_minutes,
                "manual_review_priority": "high" if int(sizes.max()) > 3 else "routine",
            }
        )
    return pd.DataFrame(rows).sort_values("patient_id").reset_index(drop=True)


def event_coverage_markdown(
    coverage: pd.DataFrame,
    clusters: pd.DataFrame,
    title: str = "Event Coverage And Cluster Summary",
) -> str:
    """Render a human-readable Markdown event coverage report."""

    def cell(value: object) -> str:
        if pd.isna(value):
            return ""
        if isinstance(value, pd.Timestamp):
            return value.isoformat(sep=" ")
        if isinstance(value, float):
            return f"{value:.3f}"
        return str(value)

    def table(df: pd.DataFrame) -> str:
        if df.empty:
            return "_No rows._"
        headers = [str(c) for c in df.columns]
        lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
        for _, row in df.iterrows():
            lines.append("| " + " | ".join(cell(row[col]) for col in df.columns) + " |")
        return "\n".join(lines)

    return "\n".join(
        [
            f"# {title}",
            "",
            "This report is an audit aid, not a clinical result.",
            "",
            "Interpretation rules:",
            "",
            "- Events with no matched wearable recording must not silently enter final metric denominators.",
            "- Patients with zero parsed recordings require source-data review before being treated as evaluable.",
            "- Large seizure clusters require manual review of postictal exclusions and event-level association.",
            "",
            "## Event Coverage",
            "",
            table(coverage),
            "",
            "## Seizure Cluster Summary",
            "",
            table(clusters),
            "",
            "Manual review should prioritize patients with low matched fractions and large clusters.",
        ]
    )
