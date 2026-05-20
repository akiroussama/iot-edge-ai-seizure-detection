from __future__ import annotations

import pandas as pd


def _markdown_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "_No rows._"
    headers = [str(c) for c in df.columns]
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for _, row in df.iterrows():
        lines.append("| " + " | ".join(str(row[col]) for col in df.columns) + " |")
    return "\n".join(lines)


def build_label_audit_packet(
    audit_df: pd.DataFrame,
    max_events: int = 10,
    title: str = "Label Audit Packet",
) -> str:
    """Build a compact Markdown packet for manual seizure-centered label review."""
    if audit_df.empty:
        return f"# {title}\n\nNo audit rows were available.\n"
    required = {
        "event_index",
        "patient_id",
        "recording_id",
        "seizure_start",
        "seizure_end",
        "window_end",
        "minutes_to_seizure",
        "forecast_label",
        "is_ictal",
        "is_postictal",
        "is_excluded",
        "audit_state",
    }
    missing = required - set(audit_df.columns)
    if missing:
        raise ValueError(f"audit_df missing columns: {sorted(missing)}")

    df = audit_df.copy()
    for col in ("seizure_start", "seizure_end", "window_end"):
        df[col] = pd.to_datetime(df[col])
    df = df.sort_values(["patient_id", "seizure_start", "event_index", "window_end"])
    event_keys = (
        df[["event_index", "patient_id", "recording_id", "seizure_start"]]
        .drop_duplicates()
        .head(max_events)
    )

    lines = [
        f"# {title}",
        "",
        "This packet is for manual label audit only. It is not a clinical result.",
        "",
        "Checklist for each event:",
        "",
        "- Confirm source seizure onset/end.",
        "- Confirm forecast positives satisfy `[window_end + SPH, window_end + SPH + SOP)`.",
        "- Confirm ictal windows are excluded.",
        "- Confirm postictal windows are excluded.",
        "- Record any parser or annotation issue before training.",
        "",
    ]
    for _, key in event_keys.iterrows():
        mask = df["event_index"].eq(key["event_index"])
        event_rows = df.loc[mask].sort_values("window_end")
        first = event_rows.iloc[0]
        counts = event_rows["audit_state"].value_counts().sort_index().rename_axis("audit_state").reset_index(name="rows")
        display_cols = [
            "window_end",
            "minutes_to_seizure",
            "forecast_label",
            "is_ictal",
            "is_postictal",
            "is_excluded",
            "audit_state",
        ]
        display = event_rows[display_cols].copy()
        display["minutes_to_seizure"] = display["minutes_to_seizure"].round(2)

        lines.extend(
            [
                f"## Event {first['event_index']}",
                "",
                f"- Patient: `{first['patient_id']}`",
                f"- Recording: `{first['recording_id']}`",
                f"- Seizure start: `{first['seizure_start']}`",
                f"- Seizure end: `{first['seizure_end']}`",
                "",
                "State counts:",
                "",
                _markdown_table(counts),
                "",
                "Timeline rows:",
                "",
                _markdown_table(display),
                "",
            ]
        )
    return "\n".join(lines)
