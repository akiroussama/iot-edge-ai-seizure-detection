from __future__ import annotations

from dataclasses import dataclass
from html import escape
from typing import Any

import numpy as np
import pandas as pd

from src.reports.label_audit import build_label_audit_review_sheet
from src.utils.time import ensure_datetime


@dataclass(frozen=True)
class ClinicalAuditWorkbenchReport:
    timeline_geometry: pd.DataFrame
    review_sheet: pd.DataFrame
    summary: pd.DataFrame
    metadata: dict[str, Any]


GEOMETRY_COLUMNS = [
    "event_index",
    "patient_id",
    "recording_id",
    "element_type",
    "layer",
    "label",
    "start_minutes",
    "end_minutes",
    "x_pct",
    "width_pct",
    "audit_state",
    "forecast_label",
    "is_ictal",
    "is_postictal",
    "is_excluded",
    "is_right_censored",
    "risk_score",
    "alarm",
]


def _bool_series(df: pd.DataFrame, column: str, default: bool = False) -> pd.Series:
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


def _require_columns(df: pd.DataFrame, required: set[str], name: str) -> None:
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"{name} missing required columns: {missing}")


def _prepare_audit(audit_df: pd.DataFrame) -> pd.DataFrame:
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
    _require_columns(audit_df, required, "audit_df")
    audit = audit_df.copy()
    for column in ("seizure_start", "seizure_end", "window_start", "window_end"):
        if column in audit.columns:
            audit[column] = ensure_datetime(audit[column])
    if "window_start" not in audit.columns:
        audit["window_start"] = audit["window_end"]
    if "is_right_censored" not in audit.columns:
        audit["is_right_censored"] = False
    if "risk_score" not in audit.columns:
        audit["risk_score"] = np.nan
    if "alarm" not in audit.columns:
        audit["alarm"] = False
    return audit.sort_values(
        ["patient_id", "recording_id", "seizure_start", "event_index", "window_end"]
    ).reset_index(drop=True)


def _relative_minutes(ts: pd.Timestamp, origin: pd.Timestamp) -> float:
    return float((ts - origin).total_seconds() / 60.0)


def _scaled(start: float, end: float, low: float, high: float) -> tuple[float, float]:
    span = max(high - low, 1.0)
    x_pct = 100.0 * (start - low) / span
    width_pct = 100.0 * max(end - start, 0.0) / span
    return float(np.clip(x_pct, 0.0, 100.0)), float(np.clip(width_pct, 0.6, 100.0))


def _intervals_for_event(
    event: pd.Series,
    *,
    sph_minutes: float,
    sop_minutes: float,
    postictal_exclusion_minutes: float | None,
) -> list[dict[str, Any]]:
    seizure_start = event["seizure_start"]
    seizure_end = event["seizure_end"]
    seizure_end_min = _relative_minutes(seizure_end, seizure_start)
    intervals = [
        {
            "element_type": "interval",
            "layer": "sph_sop_positive_zone",
            "label": "SPH/SOP positive-zone window_end range",
            "start_minutes": float(-(sph_minutes + sop_minutes)),
            "end_minutes": float(-sph_minutes),
        },
        {
            "element_type": "interval",
            "layer": "ictal_interval",
            "label": "Seizure interval",
            "start_minutes": 0.0,
            "end_minutes": max(float(seizure_end_min), 0.6),
        },
    ]
    if postictal_exclusion_minutes is not None and postictal_exclusion_minutes > 0:
        intervals.append(
            {
                "element_type": "interval",
                "layer": "postictal_exclusion",
                "label": "Postictal exclusion interval",
                "start_minutes": max(float(seizure_end_min), 0.0),
                "end_minutes": max(float(seizure_end_min), 0.0)
                + float(postictal_exclusion_minutes),
            }
        )
    return intervals


def _event_bounds(
    group: pd.DataFrame,
    interval_rows: list[dict[str, Any]],
) -> tuple[float, float]:
    seizure_start = group.iloc[0]["seizure_start"]
    starts = [
        _relative_minutes(value, seizure_start)
        for value in group["window_start"]
    ]
    ends = [
        _relative_minutes(value, seizure_start)
        for value in group["window_end"]
    ]
    starts.extend(float(row["start_minutes"]) for row in interval_rows)
    ends.extend(float(row["end_minutes"]) for row in interval_rows)
    low = min(starts + ends)
    high = max(starts + ends)
    pad = max((high - low) * 0.04, 1.0)
    return low - pad, high + pad


def build_timeline_geometry(
    audit_df: pd.DataFrame,
    *,
    sph_minutes: float,
    sop_minutes: float,
    postictal_exclusion_minutes: float | None = None,
    event_indices: list[Any] | None = None,
) -> pd.DataFrame:
    """Build machine-readable geometry for static seizure-timeline rendering."""
    if sph_minutes < 0 or sop_minutes <= 0:
        raise ValueError("sph_minutes must be non-negative and sop_minutes must be positive")
    audit = _prepare_audit(audit_df)
    if event_indices is not None:
        audit = audit.loc[audit["event_index"].isin(event_indices)].copy()
    if audit.empty:
        return pd.DataFrame(columns=GEOMETRY_COLUMNS)

    rows = []
    for event_index, group in audit.groupby("event_index", sort=False, dropna=False):
        group = group.sort_values("window_end").reset_index(drop=True)
        first = group.iloc[0]
        interval_rows = _intervals_for_event(
            first,
            sph_minutes=sph_minutes,
            sop_minutes=sop_minutes,
            postictal_exclusion_minutes=postictal_exclusion_minutes,
        )
        low, high = _event_bounds(group, interval_rows)
        common = {
            "event_index": event_index,
            "patient_id": first["patient_id"],
            "recording_id": first["recording_id"],
        }
        for interval in interval_rows:
            x_pct, width_pct = _scaled(
                interval["start_minutes"],
                interval["end_minutes"],
                low,
                high,
            )
            rows.append(
                {
                    **common,
                    **interval,
                    "x_pct": x_pct,
                    "width_pct": width_pct,
                    "audit_state": "",
                    "forecast_label": False,
                    "is_ictal": False,
                    "is_postictal": False,
                    "is_excluded": False,
                    "is_right_censored": False,
                    "risk_score": np.nan,
                    "alarm": False,
                }
            )

        forecast = _bool_series(group, "forecast_label")
        ictal = _bool_series(group, "is_ictal")
        postictal = _bool_series(group, "is_postictal")
        excluded = _bool_series(group, "is_excluded")
        right_censored = _bool_series(group, "is_right_censored")
        alarm = _bool_series(group, "alarm")
        risks = pd.to_numeric(group["risk_score"], errors="coerce")
        for row_idx, win in group.iterrows():
            start_min = _relative_minutes(win["window_start"], first["seizure_start"])
            end_min = _relative_minutes(win["window_end"], first["seizure_start"])
            x_pct, width_pct = _scaled(start_min, end_min, low, high)
            rows.append(
                {
                    **common,
                    "element_type": "window",
                    "layer": "audit_window",
                    "label": f"Window {row_idx}",
                    "start_minutes": start_min,
                    "end_minutes": end_min,
                    "x_pct": x_pct,
                    "width_pct": width_pct,
                    "audit_state": win["audit_state"],
                    "forecast_label": bool(forecast.iloc[row_idx]),
                    "is_ictal": bool(ictal.iloc[row_idx]),
                    "is_postictal": bool(postictal.iloc[row_idx]),
                    "is_excluded": bool(excluded.iloc[row_idx]),
                    "is_right_censored": bool(right_censored.iloc[row_idx]),
                    "risk_score": float(risks.iloc[row_idx])
                    if pd.notna(risks.iloc[row_idx])
                    else np.nan,
                    "alarm": bool(alarm.iloc[row_idx]),
                }
            )
    return pd.DataFrame(rows, columns=GEOMETRY_COLUMNS)


def build_audit_workbench_summary(
    audit_df: pd.DataFrame,
    review_sheet: pd.DataFrame,
    timeline_geometry: pd.DataFrame,
    *,
    result_status: str,
    citation_status: str,
    gate_c_status: str,
) -> pd.DataFrame:
    audit = _prepare_audit(audit_df)
    selected_events = (
        review_sheet["event_index"].nunique()
        if not review_sheet.empty and "event_index" in review_sheet.columns
        else 0
    )
    forecast = _bool_series(audit, "forecast_label")
    excluded = _bool_series(audit, "is_excluded")
    ictal = _bool_series(audit, "is_ictal")
    postictal = _bool_series(audit, "is_postictal")
    right_censored = _bool_series(audit, "is_right_censored")
    row = {
        "events_in_audit": int(audit["event_index"].nunique()),
        "events_in_workbench": int(selected_events),
        "timeline_rows_in_audit": int(len(audit)),
        "timeline_geometry_rows": int(len(timeline_geometry)),
        "review_sheet_rows": int(len(review_sheet)),
        "forecast_positive_rows": int(forecast.sum()),
        "valid_forecast_positive_rows": int((forecast & ~excluded).sum()),
        "ictal_excluded_rows": int((ictal & excluded).sum()),
        "postictal_excluded_rows": int((postictal & excluded).sum()),
        "right_censored_rows": int(right_censored.sum()),
        "unexpected_ictal_not_excluded_rows": int((ictal & ~excluded).sum()),
        "unexpected_postictal_not_excluded_rows": int((postictal & ~excluded).sum()),
        "result_status": result_status,
        "citation_status": citation_status,
        "gate_c_status": gate_c_status,
    }
    return pd.DataFrame([row])


def build_clinical_audit_workbench(
    audit_df: pd.DataFrame,
    *,
    sph_minutes: float,
    sop_minutes: float,
    postictal_exclusion_minutes: float | None = None,
    max_events: int | None = 20,
    selection_strategy: str = "patient_spread",
    result_status: str = "pre_gate_c_audit_artifact_not_citable",
    citation_status: str = "not_citable_pre_gate_c",
    gate_c_status: str = "not_started",
) -> ClinicalAuditWorkbenchReport:
    if citation_status == "citable_after_gate_c" and gate_c_status != "passed":
        raise ValueError("citable audit workbench reports require gate_c_status='passed'")
    if max_events is not None and max_events <= 0:
        raise ValueError("max_events must be positive or None")
    audit = _prepare_audit(audit_df)
    review_sheet = build_label_audit_review_sheet(
        audit,
        max_events=max_events,
        selection_strategy=selection_strategy,
    )
    selected_event_indices = (
        review_sheet["event_index"].tolist()
        if not review_sheet.empty
        else []
    )
    timeline_geometry = build_timeline_geometry(
        audit,
        sph_minutes=sph_minutes,
        sop_minutes=sop_minutes,
        postictal_exclusion_minutes=postictal_exclusion_minutes,
        event_indices=selected_event_indices,
    )
    summary = build_audit_workbench_summary(
        audit,
        review_sheet,
        timeline_geometry,
        result_status=result_status,
        citation_status=citation_status,
        gate_c_status=gate_c_status,
    )
    metadata = {
        "sph_minutes": float(sph_minutes),
        "sop_minutes": float(sop_minutes),
        "postictal_exclusion_minutes": postictal_exclusion_minutes,
        "max_events": max_events,
        "selection_strategy": selection_strategy,
        "result_status": result_status,
        "citation_status": citation_status,
        "gate_c_status": gate_c_status,
    }
    return ClinicalAuditWorkbenchReport(
        timeline_geometry=timeline_geometry,
        review_sheet=review_sheet,
        summary=summary,
        metadata=metadata,
    )


def clinical_audit_workbench_html(
    report: ClinicalAuditWorkbenchReport,
    *,
    title: str = "Clinical Timeline Audit Workbench",
) -> str:
    timeline = report.timeline_geometry
    review = report.review_sheet
    warning = ""
    if report.metadata["citation_status"] != "citable_after_gate_c":
        warning = "<p class=\"warning\">Citation status: not citable as a benchmark result.</p>"
    event_sections = []
    for event_index, group in timeline.groupby("event_index", sort=False, dropna=False):
        first = group.iloc[0]
        intervals = group.loc[group["element_type"].eq("interval")]
        windows = group.loc[group["element_type"].eq("window")]
        interval_html = "\n".join(_bar_html(row) for _, row in intervals.iterrows())
        window_html = "\n".join(_bar_html(row) for _, row in windows.iterrows())
        review_rows = review.loc[review["event_index"].eq(event_index)]
        event_sections.append(
            f"""
<section class="event-card">
  <h2>Event {escape(str(event_index))}</h2>
  <p>Patient <code>{escape(str(first["patient_id"]))}</code> | Recording
  <code>{escape(str(first["recording_id"]))}</code></p>
  <div class="timeline">
    <div class="axis-label left">before seizure</div>
    <div class="axis-label center">seizure onset</div>
    <div class="axis-label right">after seizure</div>
    {interval_html}
    {window_html}
  </div>
  <h3>Reviewer data row</h3>
  {_html_table(review_rows)}
</section>
"""
        )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <style>
    :root {{
      --ink: #172026;
      --muted: #5d6b76;
      --line: #d8dee4;
      --panel: #f7f9fb;
      --forecast: #2364aa;
      --ictal: #b23a48;
      --postictal: #c77d00;
      --excluded: #687078;
      --zone: #6a994e;
      --alarm: #7b2cbf;
    }}
    body {{
      margin: 0;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: var(--ink);
      background: #ffffff;
    }}
    header, main {{
      max-width: 1180px;
      margin: 0 auto;
      padding: 24px;
    }}
    h1, h2, h3 {{
      letter-spacing: 0;
    }}
    .warning {{
      padding: 10px 12px;
      border-left: 4px solid var(--postictal);
      background: #fff8e8;
      color: #5f4100;
    }}
    .event-card {{
      border-top: 1px solid var(--line);
      padding: 22px 0 28px;
    }}
    .timeline {{
      position: relative;
      height: 180px;
      border: 1px solid var(--line);
      background: linear-gradient(#ffffff, var(--panel));
      overflow: hidden;
    }}
    .axis-label {{
      position: absolute;
      top: 8px;
      font-size: 12px;
      color: var(--muted);
    }}
    .axis-label.left {{ left: 12px; }}
    .axis-label.center {{ left: 50%; transform: translateX(-50%); }}
    .axis-label.right {{ right: 12px; }}
    .bar {{
      position: absolute;
      min-width: 4px;
      border-radius: 4px;
      border: 1px solid rgba(0, 0, 0, 0.15);
    }}
    .interval {{ top: 38px; height: 16px; opacity: 0.65; }}
    .window {{ top: 88px; height: 42px; }}
    .sph_sop_positive_zone {{ background: color-mix(in srgb, var(--zone) 55%, white); }}
    .ictal_interval {{ background: color-mix(in srgb, var(--ictal) 60%, white); }}
    .postictal_exclusion {{ background: color-mix(in srgb, var(--postictal) 55%, white); }}
    .forecast_positive {{ background: color-mix(in srgb, var(--forecast) 65%, white); }}
    .ictal_excluded {{ background: color-mix(in srgb, var(--ictal) 45%, white); }}
    .postictal_excluded {{ background: color-mix(in srgb, var(--postictal) 45%, white); }}
    .valid_negative {{ background: #eef2f6; }}
    .alarm {{ box-shadow: 0 0 0 3px color-mix(in srgb, var(--alarm) 35%, transparent); }}
    .excluded {{ opacity: 0.55; }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
      margin-top: 12px;
    }}
    th, td {{
      border: 1px solid var(--line);
      padding: 6px 8px;
      text-align: left;
      vertical-align: top;
    }}
    th {{ background: var(--panel); }}
    code {{
      background: #eef2f6;
      padding: 1px 4px;
      border-radius: 3px;
    }}
  </style>
</head>
<body>
  <header>
    <h1>{escape(title)}</h1>
    {warning}
    <p>This workbench is for human label review. It visualizes seizure-centered
    audit rows and stores reviewer decisions in the companion CSV; it does not
    infer clinical correctness automatically.</p>
    {_html_table(report.summary)}
  </header>
  <main>
    {"".join(event_sections) if event_sections else "<p>No events selected.</p>"}
  </main>
</body>
</html>
"""


def _bar_html(row: pd.Series) -> str:
    classes = [
        "bar",
        str(row["element_type"]),
        _safe_class(str(row["layer"])),
        _safe_class(str(row["audit_state"])) if row["audit_state"] else "",
        "alarm" if bool(row["alarm"]) else "",
        "excluded" if bool(row["is_excluded"]) else "",
    ]
    classes = [item for item in classes if item]
    label = (
        f"{row['label']} | {row['start_minutes']:.2f} to {row['end_minutes']:.2f} min"
    )
    if pd.notna(row["risk_score"]):
        label += f" | risk={float(row['risk_score']):.3f}"
    return (
        f'<div class="{" ".join(classes)}" '
        f'style="left:{row["x_pct"]:.3f}%;width:{row["width_pct"]:.3f}%;" '
        f'title="{escape(label)}"></div>'
    )


def _safe_class(value: str) -> str:
    safe = "".join(ch.lower() if ch.isalnum() else "_" for ch in value.strip())
    safe = "_".join(part for part in safe.split("_") if part)
    return safe or "unknown"


def _html_table(df: pd.DataFrame, max_rows: int = 12) -> str:
    if df.empty:
        return "<p><em>No rows.</em></p>"
    view = df.head(max_rows)
    headers = "".join(f"<th>{escape(str(column))}</th>" for column in view.columns)
    body_rows = []
    for _, row in view.iterrows():
        cells = "".join(f"<td>{escape(str(row[column]))}</td>" for column in view.columns)
        body_rows.append(f"<tr>{cells}</tr>")
    suffix = f"<p><em>Showing {max_rows} of {len(df)} rows.</em></p>" if len(df) > max_rows else ""
    return f"<table><thead><tr>{headers}</tr></thead><tbody>{''.join(body_rows)}</tbody></table>{suffix}"


def clinical_audit_workbench_markdown(
    report: ClinicalAuditWorkbenchReport,
    *,
    title: str = "Clinical Timeline Audit Workbench",
) -> str:
    warning = ""
    if report.metadata["citation_status"] != "citable_after_gate_c":
        warning = "\n**Citation status:** not citable as a benchmark result.\n"
    return f"""# {title}
{warning}
This workbench is for human label review only. Reviewer decisions must be stored
in the companion review sheet; this report does not infer clinical correctness.

## Metadata

- SPH minutes: `{report.metadata["sph_minutes"]}`
- SOP minutes: `{report.metadata["sop_minutes"]}`
- Postictal exclusion minutes: `{report.metadata["postictal_exclusion_minutes"]}`
- Result status: `{report.metadata["result_status"]}`
- Citation status: `{report.metadata["citation_status"]}`
- Gate C status: `{report.metadata["gate_c_status"]}`

## Summary

{_markdown_table(report.summary)}

## Review Sheet Preview

{_markdown_table(report.review_sheet)}
"""


def _markdown_table(df: pd.DataFrame, max_rows: int = 20) -> str:
    if df.empty:
        return "_No rows._"
    view = df.head(max_rows)
    headers = [str(column) for column in view.columns]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for _, row in view.iterrows():
        lines.append("| " + " | ".join(str(row[column]) for column in view.columns) + " |")
    if len(df) > max_rows:
        lines.append(f"\n_Showing {max_rows} of {len(df)} rows._")
    return "\n".join(lines)


def table_records(df: pd.DataFrame) -> list[dict[str, Any]]:
    records = []
    for record in df.to_dict(orient="records"):
        clean = {}
        for key, value in record.items():
            if isinstance(value, float) and (np.isnan(value) or np.isinf(value)):
                clean[key] = None
            elif value is pd.NA or value is pd.NaT:
                clean[key] = None
            elif isinstance(value, pd.Timestamp):
                clean[key] = value.isoformat()
            elif isinstance(value, np.integer):
                clean[key] = int(value)
            elif isinstance(value, np.floating):
                clean[key] = float(value)
            else:
                clean[key] = value
        records.append(clean)
    return records
