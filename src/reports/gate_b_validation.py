from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Any

import pandas as pd

from src.reports.gate_b_closeout import LEDGER_COLUMNS


CLAIM_STATUS = "gate_b_validation_rerun_not_citable_pre_gate_c"
ACTION_KEY_COLUMNS = ["gate", "priority", "domain", "blocker_source", "action"]
ACTION_COLUMNS = [
    *ACTION_KEY_COLUMNS,
    "evidence",
    "owner",
    "exit_criterion",
]
MSG_SUMMARY_COLUMNS = [
    "patients_p0_blocker",
    "events_unmatched",
    "horizons_not_main_table_ready",
    "horizons_source_review_required",
]
SEIZEIT2_SUMMARY_COLUMNS = ["readiness_status", "blockers", "warnings"]
SIMULATION_MARKERS = (
    "simulation",
    "simulated",
    "not_real_gate_b_evidence",
)


@dataclass(frozen=True)
class GateBValidationRerunReport:
    matrix: pd.DataFrame
    summary: pd.DataFrame
    manifest: dict[str, Any]
    markdown: str


def _require_columns(frame: pd.DataFrame, required: set[str], name: str) -> None:
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"{name} missing required columns: {missing}")


def _dataframe_hash(frame: pd.DataFrame) -> str:
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
    records = []
    for record in frame.to_dict(orient="records"):
        records.append({key: _clean_value(value) for key, value in record.items()})
    return records


def _contains_simulation_marker(value: Any) -> bool:
    if pd.isna(value):
        return False
    text = str(value).lower()
    return any(marker in text for marker in SIMULATION_MARKERS)


def _frame_contains_simulation_markers(frame: pd.DataFrame) -> bool:
    if frame.empty:
        return False
    for column in frame.columns:
        if frame[column].map(_contains_simulation_marker).any():
            return True
    return False


def _as_int(frame: pd.DataFrame, column: str, default: int = 0) -> int:
    if frame.empty or column not in frame.columns:
        return default
    value = frame.loc[0, column]
    if pd.isna(value):
        return default
    return int(float(value))


def _as_str(frame: pd.DataFrame, column: str, default: str = "") -> str:
    if frame.empty or column not in frame.columns:
        return default
    value = frame.loc[0, column]
    if pd.isna(value):
        return default
    return str(value)


def _action_key(row: pd.Series) -> tuple[str, str, str, str, str]:
    return tuple(str(row[column]) for column in ACTION_KEY_COLUMNS)


def _ledger_lookup(closeout_ledger: pd.DataFrame) -> dict[tuple[str, str, str, str, str], pd.Series]:
    lookup: dict[tuple[str, str, str, str, str], pd.Series] = {}
    duplicate_keys: set[tuple[str, str, str, str, str]] = set()
    for _, row in closeout_ledger.iterrows():
        key = _action_key(row)
        if key in lookup:
            duplicate_keys.add(key)
        lookup[key] = row
    if duplicate_keys:
        examples = ["/".join(key[:4]) for key in sorted(duplicate_keys)[:3]]
        raise ValueError(f"closeout_ledger contains duplicate action keys: {examples}")
    return lookup


def _validation_status(closeout_row: pd.Series | None) -> str:
    if closeout_row is None:
        return "missing_closeout_row"
    status = str(closeout_row.get("closeout_status", "")).strip()
    if status == "closed_by_human_review":
        return "closed_by_real_attestation"
    if status == "blocked_after_human_review":
        return "needs_source_review"
    if status in {"invalid_human_decision", "incomplete_closeout_metadata"}:
        return "invalid_real_closeout"
    return "pending_real_closeout"


def _next_action(validation_status: str, action: pd.Series, closeout_row: pd.Series | None) -> str:
    if validation_status == "closed_by_real_attestation":
        return "No real-closeout action; keep rerun evidence attached to the ledger."
    if validation_status == "missing_closeout_row":
        return "Add a matching closeout ledger row before Gate B validation can pass."
    if validation_status == "needs_source_review":
        decision = "" if closeout_row is None else str(closeout_row.get("human_decision", ""))
        return f"Resolve the human-review blocker ({decision}) or mark the row non-citable."
    if validation_status == "invalid_real_closeout":
        return "Fix invalid or incomplete human-review metadata and rerun validation."
    return (
        "Complete real human closeout for this guardrail action with reviewer, date, "
        "evidence URI, and rerun artifact when required."
    )


def _build_matrix(
    *,
    closeout_ledger: pd.DataFrame,
    action_checklist: pd.DataFrame,
) -> pd.DataFrame:
    lookup = _ledger_lookup(closeout_ledger)
    rows: list[dict[str, Any]] = []
    for _, action in action_checklist.iterrows():
        closeout_row = lookup.get(_action_key(action))
        validation_status = _validation_status(closeout_row)
        rows.append(
            {
                "gate": action["gate"],
                "priority": action["priority"],
                "domain": action["domain"],
                "blocker_source": action["blocker_source"],
                "action": action["action"],
                "guardrail_evidence": action["evidence"],
                "ledger_id": "" if closeout_row is None else closeout_row.get("ledger_id", ""),
                "closeout_status": ""
                if closeout_row is None
                else closeout_row.get("closeout_status", ""),
                "human_decision": ""
                if closeout_row is None
                else closeout_row.get("human_decision", ""),
                "evidence_uri": "" if closeout_row is None else closeout_row.get("evidence_uri", ""),
                "rerun_required": ""
                if closeout_row is None
                else closeout_row.get("rerun_required", ""),
                "rerun_artifact_uri": ""
                if closeout_row is None
                else closeout_row.get("rerun_artifact_uri", ""),
                "validation_status": validation_status,
                "next_action": _next_action(validation_status, action, closeout_row),
                "claim_status": CLAIM_STATUS,
            }
        )
    return pd.DataFrame(rows)


def _summary_status(
    *,
    matrix: pd.DataFrame,
    closeout_summary: pd.DataFrame | None,
    simulation_detected: bool,
) -> str:
    if simulation_detected:
        return "blocked_simulation_marker_detected"
    gate_b = matrix.loc[matrix["gate"].eq("Gate B")]
    if closeout_summary is not None and not closeout_summary.empty:
        if _as_int(closeout_summary, "real_open_rows") > 0:
            return "blocked_pending_real_closeout"
        closeout_status = _as_str(closeout_summary, "gate_b_real_closeout_status")
        if closeout_status == "blocked_pending_real_evidence":
            return "blocked_pending_real_closeout"
    if gate_b["validation_status"].eq("needs_source_review").any():
        return "needs_source_review"
    if gate_b["validation_status"].isin({"invalid_real_closeout", "missing_closeout_row"}).any():
        return "blocked_invalid_real_closeout"
    if gate_b["validation_status"].ne("closed_by_real_attestation").any():
        return "blocked_pending_real_closeout"
    return "passed_ready_for_gate_c_dry_run"


def build_gate_b_validation_rerun_report(
    *,
    closeout_ledger: pd.DataFrame,
    action_checklist: pd.DataFrame,
    msg_summary: pd.DataFrame,
    seizeit2_summary: pd.DataFrame,
    run_id: str = "gate_b_validation_rerun_2026-05-22",
    source_uri: str = "local_gate_guardrail_rerun",
    closeout_summary: pd.DataFrame | None = None,
) -> GateBValidationRerunReport:
    """Validate real Gate B closeout against the current guardrail rerun outputs."""
    _require_columns(closeout_ledger, set(LEDGER_COLUMNS), "closeout_ledger")
    _require_columns(action_checklist, set(ACTION_COLUMNS), "action_checklist")
    _require_columns(msg_summary, set(MSG_SUMMARY_COLUMNS), "msg_summary")
    _require_columns(seizeit2_summary, set(SEIZEIT2_SUMMARY_COLUMNS), "seizeit2_summary")
    matrix = _build_matrix(closeout_ledger=closeout_ledger, action_checklist=action_checklist)
    gate_b = matrix.loc[matrix["gate"].eq("Gate B")]
    simulation_detected = _frame_contains_simulation_markers(closeout_ledger)
    gate_b_validation_status = _summary_status(
        matrix=matrix,
        closeout_summary=closeout_summary,
        simulation_detected=simulation_detected,
    )
    gate_b_passed = gate_b_validation_status == "passed_ready_for_gate_c_dry_run"
    summary = pd.DataFrame(
        [
            {
                "run_id": run_id,
                "source_uri": source_uri,
                "guardrail_actions": int(len(matrix)),
                "gate_b_actions": int(len(gate_b)),
                "gate_b_closed_actions": int(
                    gate_b["validation_status"].eq("closed_by_real_attestation").sum()
                ),
                "gate_b_open_actions": int(
                    gate_b["validation_status"].ne("closed_by_real_attestation").sum()
                ),
                "gate_b_p0_open_actions": int(
                    gate_b.loc[gate_b["priority"].eq("P0"), "validation_status"]
                    .ne("closed_by_real_attestation")
                    .sum()
                ),
                "gate_b_source_review_actions": int(
                    gate_b["validation_status"].eq("needs_source_review").sum()
                ),
                "msg_p0_patients": _as_int(msg_summary, "patients_p0_blocker"),
                "msg_unmatched_events": _as_int(msg_summary, "events_unmatched"),
                "msg_not_main_horizons": _as_int(msg_summary, "horizons_not_main_table_ready"),
                "msg_source_review_horizons": _as_int(
                    msg_summary,
                    "horizons_source_review_required",
                ),
                "seizeit2_readiness_status": _as_str(seizeit2_summary, "readiness_status"),
                "seizeit2_blockers": _as_int(seizeit2_summary, "blockers"),
                "seizeit2_warnings": _as_int(seizeit2_summary, "warnings"),
                "simulation_marker_detected": bool(simulation_detected),
                "gate_b_validation_status": gate_b_validation_status,
                "gate_b_passed": bool(gate_b_passed),
                "gate_c_next_status": "ready_for_gate_c_dry_run"
                if gate_b_passed
                else "blocked_by_gate_b_validation",
                "claim_status": CLAIM_STATUS,
            }
        ]
    )
    manifest = {
        "run_id": run_id,
        "source_uri": source_uri,
        "claim_status": CLAIM_STATUS,
        "gate_b_validation_status": gate_b_validation_status,
        "gate_b_passed": bool(gate_b_passed),
        "matrix_hash": _dataframe_hash(matrix),
        "summary_hash": _dataframe_hash(summary),
        "closeout_ledger_hash": _dataframe_hash(closeout_ledger),
        "action_checklist_hash": _dataframe_hash(action_checklist),
        "msg_summary_hash": _dataframe_hash(msg_summary),
        "seizeit2_summary_hash": _dataframe_hash(seizeit2_summary),
    }
    markdown = gate_b_validation_rerun_markdown(matrix, summary, manifest)
    return GateBValidationRerunReport(
        matrix=matrix,
        summary=summary,
        manifest=manifest,
        markdown=markdown,
    )


def _markdown_table(frame: pd.DataFrame, max_rows: int = 16) -> str:
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
            text = "" if pd.isna(value) else str(value)
            cells.append(text.replace("|", "\\|"))
        lines.append("| " + " | ".join(cells) + " |")
    if len(frame) > max_rows:
        lines.append(f"\n_Showing {max_rows} of {len(frame)} rows._")
    return "\n".join(lines)


def gate_b_validation_rerun_markdown(
    matrix: pd.DataFrame,
    summary: pd.DataFrame,
    manifest: dict[str, Any],
) -> str:
    visible = matrix[
        [
            "ledger_id",
            "gate",
            "priority",
            "domain",
            "validation_status",
            "human_decision",
            "next_action",
        ]
    ]
    return f"""# Gate B Validation Rerun

**Status:** `{manifest["gate_b_validation_status"]}`

This report validates real Gate B closeout decisions against the current local
guardrail rerun. It is not a Gate C pass and it does not make benchmark rows
citable.

## Summary

{_markdown_table(summary)}

## Validation Matrix

{_markdown_table(visible)}

## Rules

- Simulation markers in a real closeout ledger block validation.
- Current Gate B guardrail actions must have real closed attestations.
- Rows needing source review or invalid metadata block Gate B.
- A passing Gate B validation only enables Gate C dry-run; it is not a citable
  benchmark result.
- Claim status: `{manifest["claim_status"]}`

## Manifest

- Run ID: `{manifest["run_id"]}`
- Source URI: `{manifest["source_uri"]}`
- Matrix hash: `{manifest["matrix_hash"]}`
- Summary hash: `{manifest["summary_hash"]}`
"""
