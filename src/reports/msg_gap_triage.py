from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
from typing import Any

import pandas as pd


CLAIM_STATUS = "msg_gap_triage_pre_gate_c_not_citable"
PATIENT_TRIAGE_COLUMNS = [
    "patient_id",
    "triage_priority",
    "evaluable_status",
    "issue_flags",
    "recommended_action",
    "events_total",
    "events_matched",
    "events_unmatched",
    "matched_fraction",
    "recordings",
    "recording_hours",
    "clusters",
    "clustered_events",
    "max_cluster_size",
    "claim_status",
]
HORIZON_TRIAGE_COLUMNS = [
    "sph_minutes",
    "sop_minutes",
    "horizon_status",
    "issue_flags",
    "recommended_action",
    "windows_total",
    "valid_windows",
    "valid_window_fraction",
    "positive_windows_total",
    "valid_positive_windows",
    "right_censored_unknown_windows",
    "right_censored_unknown_fraction",
    "events_total",
    "events_coverable_by_valid_windows",
    "event_coverable_fraction",
    "events_recording_matched",
    "events_recording_unmatched",
    "claim_status",
]


@dataclass(frozen=True)
class MSGGapTriageConfig:
    min_matched_fraction: float = 0.8
    max_cluster_size_for_routine: int = 3
    min_valid_window_fraction: float = 0.5
    min_event_coverable_fraction: float = 0.5
    max_right_censored_unknown_fraction: float = 0.25


@dataclass(frozen=True)
class MSGGapTriageReport:
    patient_triage: pd.DataFrame
    horizon_triage: pd.DataFrame
    summary: pd.DataFrame
    manifest: pd.DataFrame
    metadata: dict[str, Any]


def _require_columns(frame: pd.DataFrame, required: set[str], name: str) -> None:
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"{name} missing required columns: {missing}")


def _validate_config(config: MSGGapTriageConfig) -> None:
    if not 0 <= config.min_matched_fraction <= 1:
        raise ValueError("min_matched_fraction must be between 0 and 1")
    if config.max_cluster_size_for_routine < 1:
        raise ValueError("max_cluster_size_for_routine must be >= 1")
    if not 0 <= config.min_valid_window_fraction <= 1:
        raise ValueError("min_valid_window_fraction must be between 0 and 1")
    if not 0 <= config.min_event_coverable_fraction <= 1:
        raise ValueError("min_event_coverable_fraction must be between 0 and 1")
    if not 0 <= config.max_right_censored_unknown_fraction <= 1:
        raise ValueError("max_right_censored_unknown_fraction must be between 0 and 1")


def _numeric(frame: pd.DataFrame, column: str, default: float = 0.0) -> pd.Series:
    if column not in frame.columns:
        return pd.Series(default, index=frame.index, dtype="float64")
    return pd.to_numeric(frame[column], errors="coerce").fillna(default)


def _join_flags(flags: list[str]) -> str:
    return ";".join(flags) if flags else "none"


def _join_actions(actions: list[str]) -> str:
    return ";".join(dict.fromkeys(actions)) if actions else "routine_gate_b_sampling"


def _dataframe_hash(frame: pd.DataFrame | None) -> str | None:
    if frame is None:
        return None
    return sha256(frame.to_csv(index=False).encode("utf-8")).hexdigest()


def _clean_value(value: Any) -> Any:
    if value is pd.NA or value is pd.NaT:
        return None
    if isinstance(value, float) and pd.isna(value):
        return None
    if hasattr(value, "item"):
        try:
            return value.item()
        except ValueError:
            return value
    return value


def table_records(frame: pd.DataFrame) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for record in frame.to_dict(orient="records"):
        records.append({key: _clean_value(value) for key, value in record.items()})
    return records


def build_patient_gap_triage(
    coverage: pd.DataFrame,
    clusters: pd.DataFrame | None = None,
    *,
    config: MSGGapTriageConfig | None = None,
) -> pd.DataFrame:
    """Turn per-patient event coverage into an explicit source-data triage table."""
    cfg = config or MSGGapTriageConfig()
    _validate_config(cfg)
    _require_columns(
        coverage,
        {
            "patient_id",
            "events_total",
            "events_matched",
            "events_unmatched",
            "matched_fraction",
            "recordings",
            "recording_hours",
        },
        "coverage",
    )
    cov = coverage.copy()
    for column in [
        "events_total",
        "events_matched",
        "events_unmatched",
        "matched_fraction",
        "recordings",
        "recording_hours",
    ]:
        cov[column] = _numeric(cov, column)

    if clusters is None or clusters.empty:
        merged = cov.copy()
        merged["clusters"] = 0
        merged["clustered_events"] = 0
        merged["max_cluster_size"] = 0
    else:
        _require_columns(
            clusters,
            {"patient_id", "clusters", "clustered_events", "max_cluster_size"},
            "clusters",
        )
        clu = clusters[["patient_id", "clusters", "clustered_events", "max_cluster_size"]].copy()
        for column in ["clusters", "clustered_events", "max_cluster_size"]:
            clu[column] = _numeric(clu, column)
        clu = clu.drop_duplicates("patient_id", keep="last")
        merged = cov.merge(clu, on="patient_id", how="left")
        for column in ["clusters", "clustered_events", "max_cluster_size"]:
            merged[column] = _numeric(merged, column)

    rows: list[dict[str, Any]] = []
    for _, row in merged.iterrows():
        events_total = int(row["events_total"])
        events_matched = int(row["events_matched"])
        events_unmatched = int(row["events_unmatched"])
        matched_fraction = float(row["matched_fraction"])
        recordings = int(row["recordings"])
        max_cluster_size = int(row["max_cluster_size"])
        flags: list[str] = []
        actions: list[str] = []

        if events_total > 0 and recordings == 0:
            flags.append("zero_parsed_recordings")
            actions.append("recover_or_document_missing_wearable_segments_before_gate_c")
        if events_total > 0 and events_matched == 0:
            flags.append("zero_matched_events")
            actions.append("exclude_from_evaluable_denominators_until_source_review")
        if events_unmatched > 0:
            flags.append("unmatched_events")
            actions.append("resolve_unmatched_events_or_restrict_denominator_explicitly")
        if matched_fraction < cfg.min_matched_fraction:
            flags.append("low_matched_fraction")
            actions.append("audit_patient_manifest_and_event_timestamps")
        if max_cluster_size > cfg.max_cluster_size_for_routine:
            flags.append("large_seizure_cluster")
            actions.append("review_cluster_definition_and_postictal_policy")

        if "zero_parsed_recordings" in flags or "zero_matched_events" in flags:
            priority = "p0_blocker"
            status = "not_evaluable_without_source_review"
        elif events_unmatched > 0:
            priority = "p1_source_review_required"
            status = "partially_evaluable_matched_only"
        elif "large_seizure_cluster" in flags or "low_matched_fraction" in flags:
            priority = "p1_timeline_review_required"
            status = "evaluable_after_timeline_review"
        else:
            priority = "p2_routine"
            status = "routine_gate_b_sampling"

        rows.append(
            {
                "patient_id": row["patient_id"],
                "triage_priority": priority,
                "evaluable_status": status,
                "issue_flags": _join_flags(flags),
                "recommended_action": _join_actions(actions),
                "events_total": events_total,
                "events_matched": events_matched,
                "events_unmatched": events_unmatched,
                "matched_fraction": matched_fraction,
                "recordings": recordings,
                "recording_hours": float(row["recording_hours"]),
                "clusters": int(row["clusters"]),
                "clustered_events": int(row["clustered_events"]),
                "max_cluster_size": max_cluster_size,
                "claim_status": CLAIM_STATUS,
            }
        )
    out = pd.DataFrame(rows, columns=PATIENT_TRIAGE_COLUMNS)
    if out.empty:
        return out
    priority_order = {"p0_blocker": 0, "p1_source_review_required": 1, "p1_timeline_review_required": 2}
    return (
        out.assign(_priority_rank=out["triage_priority"].map(priority_order).fillna(9))
        .sort_values(
            ["_priority_rank", "events_unmatched", "max_cluster_size", "patient_id"],
            ascending=[True, False, False, True],
        )
        .drop(columns=["_priority_rank"])
        .reset_index(drop=True)
    )


def build_horizon_gap_triage(
    viability: pd.DataFrame | None,
    *,
    config: MSGGapTriageConfig | None = None,
) -> pd.DataFrame:
    """Classify candidate SPH/SOP horizons by feasibility blockers."""
    cfg = config or MSGGapTriageConfig()
    _validate_config(cfg)
    if viability is None or viability.empty:
        return pd.DataFrame(columns=HORIZON_TRIAGE_COLUMNS)
    _require_columns(
        viability,
        {
            "sph_minutes",
            "sop_minutes",
            "windows_total",
            "valid_windows",
            "valid_window_fraction",
            "right_censored_unknown_windows",
            "events_total",
            "events_coverable_by_valid_windows",
            "event_coverable_fraction",
        },
        "viability",
    )
    frame = viability.copy()
    for column in [
        "sph_minutes",
        "sop_minutes",
        "windows_total",
        "valid_windows",
        "valid_window_fraction",
        "positive_windows_total",
        "valid_positive_windows",
        "right_censored_unknown_windows",
        "events_total",
        "events_coverable_by_valid_windows",
        "event_coverable_fraction",
        "events_recording_matched",
        "events_recording_unmatched",
    ]:
        frame[column] = _numeric(frame, column)
    windows_total = frame["windows_total"].replace(0, pd.NA)
    frame["right_censored_unknown_fraction"] = (
        frame["right_censored_unknown_windows"] / windows_total
    ).fillna(0.0)

    rows: list[dict[str, Any]] = []
    for _, row in frame.iterrows():
        flags: list[str] = []
        actions: list[str] = []
        if float(row["valid_window_fraction"]) < cfg.min_valid_window_fraction:
            flags.append("low_valid_window_fraction")
            actions.append("demote_horizon_or_mark_as_feasibility_negative")
        if float(row["event_coverable_fraction"]) < cfg.min_event_coverable_fraction:
            flags.append("low_event_coverable_fraction")
            actions.append("do_not_anchor_main_table_until_event_coverage_improves")
        if float(row["right_censored_unknown_fraction"]) > cfg.max_right_censored_unknown_fraction:
            flags.append("high_right_censored_unknown_fraction")
            actions.append("document_right_censoring_before_split_freeze")
        if int(row["events_recording_unmatched"]) > 0:
            flags.append("unmatched_events_present")
            actions.append("resolve_unmatched_events_or_restrict_denominator_explicitly")

        hard_feasibility_flags = {
            "low_valid_window_fraction",
            "low_event_coverable_fraction",
            "high_right_censored_unknown_fraction",
        }
        if hard_feasibility_flags.intersection(flags):
            status = "not_main_table_ready"
        elif "unmatched_events_present" in flags:
            status = "source_review_required"
        else:
            status = "candidate_after_gate_b_c"

        rows.append(
            {
                "sph_minutes": float(row["sph_minutes"]),
                "sop_minutes": float(row["sop_minutes"]),
                "horizon_status": status,
                "issue_flags": _join_flags(flags),
                "recommended_action": _join_actions(actions),
                "windows_total": int(row["windows_total"]),
                "valid_windows": int(row["valid_windows"]),
                "valid_window_fraction": float(row["valid_window_fraction"]),
                "positive_windows_total": int(row["positive_windows_total"]),
                "valid_positive_windows": int(row["valid_positive_windows"]),
                "right_censored_unknown_windows": int(row["right_censored_unknown_windows"]),
                "right_censored_unknown_fraction": float(row["right_censored_unknown_fraction"]),
                "events_total": int(row["events_total"]),
                "events_coverable_by_valid_windows": int(row["events_coverable_by_valid_windows"]),
                "event_coverable_fraction": float(row["event_coverable_fraction"]),
                "events_recording_matched": int(row["events_recording_matched"]),
                "events_recording_unmatched": int(row["events_recording_unmatched"]),
                "claim_status": CLAIM_STATUS,
            }
        )
    out = pd.DataFrame(rows, columns=HORIZON_TRIAGE_COLUMNS)
    status_order = {"not_main_table_ready": 0, "source_review_required": 1}
    return (
        out.assign(_status_rank=out["horizon_status"].map(status_order).fillna(9))
        .sort_values(["_status_rank", "sop_minutes", "sph_minutes"], ascending=[True, False, True])
        .drop(columns=["_status_rank"])
        .reset_index(drop=True)
    )


def summarize_msg_gap_triage(
    patient_triage: pd.DataFrame,
    horizon_triage: pd.DataFrame,
    *,
    dataset: str = "MSG",
) -> pd.DataFrame:
    """Build a one-row manifest-style summary for the gap triage report."""
    patient_counts = patient_triage["triage_priority"].value_counts().to_dict()
    horizon_counts = (
        horizon_triage["horizon_status"].value_counts().to_dict()
        if not horizon_triage.empty
        else {}
    )
    row = {
        "dataset": dataset,
        "patients_total": int(len(patient_triage)),
        "patients_p0_blocker": int(patient_counts.get("p0_blocker", 0)),
        "patients_p1_source_review_required": int(
            patient_counts.get("p1_source_review_required", 0)
        ),
        "patients_p1_timeline_review_required": int(
            patient_counts.get("p1_timeline_review_required", 0)
        ),
        "patients_p2_routine": int(patient_counts.get("p2_routine", 0)),
        "events_total": int(patient_triage["events_total"].sum()) if not patient_triage.empty else 0,
        "events_matched": int(patient_triage["events_matched"].sum())
        if not patient_triage.empty
        else 0,
        "events_unmatched": int(patient_triage["events_unmatched"].sum())
        if not patient_triage.empty
        else 0,
        "horizons_total": int(len(horizon_triage)),
        "horizons_not_main_table_ready": int(horizon_counts.get("not_main_table_ready", 0)),
        "horizons_source_review_required": int(horizon_counts.get("source_review_required", 0)),
        "horizons_candidate_after_gate_b_c": int(
            horizon_counts.get("candidate_after_gate_b_c", 0)
        ),
        "claim_status": CLAIM_STATUS,
        "gate_c_implication": "blocked_until_source_review_audit_and_freeze",
    }
    return pd.DataFrame([row])


def build_msg_gap_triage_report(
    coverage: pd.DataFrame,
    clusters: pd.DataFrame | None = None,
    viability: pd.DataFrame | None = None,
    *,
    dataset: str = "MSG",
    config: MSGGapTriageConfig | None = None,
) -> MSGGapTriageReport:
    cfg = config or MSGGapTriageConfig()
    _validate_config(cfg)
    patient_triage = build_patient_gap_triage(coverage, clusters, config=cfg)
    horizon_triage = build_horizon_gap_triage(viability, config=cfg)
    summary = summarize_msg_gap_triage(patient_triage, horizon_triage, dataset=dataset)
    metadata: dict[str, Any] = {
        "dataset": dataset,
        "claim_status": CLAIM_STATUS,
        "config": asdict(cfg),
        "coverage_hash": _dataframe_hash(coverage),
        "clusters_hash": _dataframe_hash(clusters),
        "viability_hash": _dataframe_hash(viability),
        "patient_triage_hash": _dataframe_hash(patient_triage),
        "horizon_triage_hash": _dataframe_hash(horizon_triage),
        "summary_hash": _dataframe_hash(summary),
        "result_status": "feasibility_gap_triage_not_model_result",
    }
    manifest = pd.DataFrame([metadata])
    return MSGGapTriageReport(
        patient_triage=patient_triage,
        horizon_triage=horizon_triage,
        summary=summary,
        manifest=manifest,
        metadata=metadata,
    )


def _markdown_table(frame: pd.DataFrame, max_rows: int = 20) -> str:
    if frame.empty:
        return "_No rows._"
    view = frame.head(max_rows)
    headers = [str(column) for column in view.columns]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for _, row in view.iterrows():
        cells = []
        for column in view.columns:
            value = row[column]
            if isinstance(value, float):
                cells.append(f"{value:.3f}")
            elif pd.isna(value):
                cells.append("")
            else:
                cells.append(str(value))
        lines.append("| " + " | ".join(cells) + " |")
    if len(frame) > max_rows:
        lines.append(f"\n_Showing {max_rows} of {len(frame)} rows._")
    return "\n".join(lines)


def msg_gap_triage_markdown(
    report: MSGGapTriageReport,
    *,
    title: str = "MSG Data-Gap Triage",
) -> str:
    """Render the MSG gap triage as a human-facing audit report."""
    return f"""# {title}

**Citation status:** not citable as a benchmark result before Gate C.

This report is a source-data and feasibility triage. It does not train a model,
does not report sensitivity, false alarms, Brier score, BSS, or clinical utility,
and does not mark any split or artifact as frozen.

## Summary

{_markdown_table(report.summary)}

## Patient Triage

{_markdown_table(report.patient_triage)}

## Horizon Triage

{_markdown_table(report.horizon_triage)}

## Interpretation Rules

- `p0_blocker` patients require source-data recovery or explicit exclusion before Gate C.
- `p1_source_review_required` patients can only be used with explicit matched-event denominators.
- `not_main_table_ready` horizons should be demoted to feasibility or negative findings until the
  source-data and right-censoring issues are resolved.
- No row in this report upgrades any current MSG pipeline check into a citable clinical result.

## Manifest

- Dataset: `{report.metadata["dataset"]}`
- Claim status: `{report.metadata["claim_status"]}`
- Result status: `{report.metadata["result_status"]}`
- Patient triage hash: `{report.metadata["patient_triage_hash"]}`
- Horizon triage hash: `{report.metadata["horizon_triage_hash"]}`
"""
