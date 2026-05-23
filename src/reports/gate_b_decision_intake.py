from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import re
from typing import Any

import pandas as pd

from src.reports.gate_b_closeout import (
    ALLOWED_HUMAN_DECISIONS,
    CLOSED_DECISIONS,
    HUMAN_REVIEW_COLUMNS,
    LEDGER_COLUMNS,
)


CLAIM_STATUS = "gate_b_real_decision_intake_not_citable_pre_gate_c"
SHA256_RE = re.compile(r"^sha256:[0-9a-fA-F]{64}$")
SIMULATION_MARKERS = (
    "simulation",
    "simulated",
    "not_real_gate_b_evidence",
)
REQUIRED_INTAKE_COLUMNS = ["ledger_id", "required_evidence", *HUMAN_REVIEW_COLUMNS]


@dataclass(frozen=True)
class GateBDecisionIntakeReport:
    rows: pd.DataFrame
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


def _text(value: Any) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()


def _normalize_decision(value: Any) -> str:
    return _text(value).upper()


def _contains_simulation_marker(value: Any) -> bool:
    text = _text(value).lower()
    return any(marker in text for marker in SIMULATION_MARKERS)


def _row_contains_simulation_marker(row: pd.Series) -> bool:
    return any(_contains_simulation_marker(value) for value in row.tolist())


def _present(value: Any) -> bool:
    text = _text(value)
    return bool(text) and text.upper() != "N/A"


def _is_yes(value: Any) -> bool:
    return _text(value).lower() in {"yes", "true", "1"}


def _is_no(value: Any) -> bool:
    return _text(value).lower() in {"no", "false", "0"}


def _missing_core_fields(row: pd.Series) -> list[str]:
    missing = []
    for column in (
        "human_decision",
        "reviewer_name",
        "review_date",
        "evidence_uri",
        "evidence_hash",
        "resolution_notes",
        "rerun_required",
    ):
        if not _present(row.get(column, "")):
            missing.append(column)
    return missing


def _evidence_hash_status(value: Any) -> str:
    text = _text(value)
    if not text:
        return "missing"
    if SHA256_RE.fullmatch(text):
        return "valid_sha256"
    return "invalid_sha256_format"


def _rerun_artifact_status(row: pd.Series) -> str:
    rerun_required = row.get("rerun_required", "")
    if _is_yes(rerun_required):
        return "present" if _present(row.get("rerun_artifact_uri", "")) else "missing_required"
    if _is_no(rerun_required):
        return "not_required"
    return "invalid_rerun_required"


def _decision_status(row: pd.Series | None) -> tuple[str, str]:
    if row is None:
        return "missing_required_decision", "Supply a real decision row for this ledger_id."
    if _row_contains_simulation_marker(row):
        return "blocked_simulation_marker", "Replace simulation language with real evidence notes."
    missing = _missing_core_fields(row)
    if missing:
        return (
            "incomplete_decision_metadata",
            f"Fill required fields: {', '.join(missing)}.",
        )
    decision = _normalize_decision(row.get("human_decision", ""))
    if decision not in ALLOWED_HUMAN_DECISIONS:
        return "invalid_human_decision", "Use an allowed human_decision value."
    hash_status = _evidence_hash_status(row.get("evidence_hash", ""))
    if hash_status != "valid_sha256":
        return "invalid_evidence_hash", "Use evidence_hash format sha256:<64 hex>."
    rerun_status = _rerun_artifact_status(row)
    if rerun_status == "missing_required":
        return "missing_rerun_artifact", "Provide rerun_artifact_uri because rerun_required is yes."
    if rerun_status == "invalid_rerun_required":
        return "invalid_rerun_required", "Use rerun_required as yes or no."
    if decision in CLOSED_DECISIONS:
        return "accepted_closing_decision", "Ready to apply to the real closeout ledger."
    return (
        "accepted_human_blocker_decision",
        "Ready to apply, but this decision keeps Gate B blocked.",
    )


def _decision_lookup(decisions: pd.DataFrame) -> dict[str, pd.Series]:
    duplicate_mask = decisions["ledger_id"].astype(str).duplicated(keep=False)
    if duplicate_mask.any():
        duplicates = decisions.loc[duplicate_mask, "ledger_id"].astype(str).unique().tolist()
        raise ValueError(f"decisions contains duplicate ledger_id values: {duplicates}")
    return {str(row["ledger_id"]): row for _, row in decisions.iterrows()}


def build_gate_b_decision_intake_report(
    *,
    closeout_ledger: pd.DataFrame,
    required_decisions: pd.DataFrame,
    decisions: pd.DataFrame,
    run_id: str = "gate_b_real_decision_intake_2026-05-23",
    source_uri: str = "gate_b_real_decision_intake",
) -> GateBDecisionIntakeReport:
    """Preflight real Gate B decisions before applying them to the closeout ledger."""
    _require_columns(closeout_ledger, set(LEDGER_COLUMNS), "closeout_ledger")
    _require_columns(required_decisions, set(REQUIRED_INTAKE_COLUMNS), "required_decisions")
    _require_columns(decisions, {"ledger_id", *HUMAN_REVIEW_COLUMNS}, "decisions")
    closeout_ids = set(closeout_ledger["ledger_id"].astype(str))
    required_ids = required_decisions["ledger_id"].astype(str).tolist()
    unknown_required = sorted(set(required_ids) - closeout_ids)
    if unknown_required:
        raise ValueError(f"required_decisions contains unknown ledger_id values: {unknown_required}")
    decision_by_id = _decision_lookup(decisions)
    unknown_decisions = sorted(set(decision_by_id) - set(required_ids))
    rows: list[dict[str, Any]] = []
    for _, required in required_decisions.iterrows():
        ledger_id = str(required["ledger_id"])
        decision = decision_by_id.get(ledger_id)
        status, next_action = _decision_status(decision)
        decision_text = "" if decision is None else _normalize_decision(decision.get("human_decision", ""))
        rows.append(
            {
                "ledger_id": ledger_id,
                "required_evidence": required["required_evidence"],
                "decision_status": status,
                "human_decision": decision_text,
                "reviewer_name": "" if decision is None else decision.get("reviewer_name", ""),
                "review_date": "" if decision is None else decision.get("review_date", ""),
                "evidence_uri": "" if decision is None else decision.get("evidence_uri", ""),
                "evidence_hash_status": "missing"
                if decision is None
                else _evidence_hash_status(decision.get("evidence_hash", "")),
                "rerun_required": "" if decision is None else decision.get("rerun_required", ""),
                "rerun_artifact_status": "missing"
                if decision is None
                else _rerun_artifact_status(decision),
                "next_action": next_action,
                "claim_status": CLAIM_STATUS,
            }
        )
    for ledger_id in unknown_decisions:
        rows.append(
            {
                "ledger_id": ledger_id,
                "required_evidence": "",
                "decision_status": "unknown_decision_row",
                "human_decision": _normalize_decision(decision_by_id[ledger_id].get("human_decision", "")),
                "reviewer_name": decision_by_id[ledger_id].get("reviewer_name", ""),
                "review_date": decision_by_id[ledger_id].get("review_date", ""),
                "evidence_uri": decision_by_id[ledger_id].get("evidence_uri", ""),
                "evidence_hash_status": _evidence_hash_status(
                    decision_by_id[ledger_id].get("evidence_hash", "")
                ),
                "rerun_required": decision_by_id[ledger_id].get("rerun_required", ""),
                "rerun_artifact_status": _rerun_artifact_status(decision_by_id[ledger_id]),
                "next_action": "Remove this row or add it to the required decisions template.",
                "claim_status": CLAIM_STATUS,
            }
        )
    intake_rows = pd.DataFrame(rows)
    status_counts = intake_rows["decision_status"].value_counts()
    accepted_mask = intake_rows["decision_status"].isin(
        {"accepted_closing_decision", "accepted_human_blocker_decision"}
    )
    issue_mask = ~accepted_mask
    human_blocker_rows = int(
        intake_rows["decision_status"].eq("accepted_human_blocker_decision").sum()
    )
    if int(issue_mask.sum()) > 0:
        intake_status = "blocked_invalid_or_incomplete_decisions"
    elif human_blocker_rows > 0:
        intake_status = "ready_for_closeout_application_with_human_blockers"
    else:
        intake_status = "ready_for_closeout_application"
    summary = pd.DataFrame(
        [
            {
                "run_id": run_id,
                "source_uri": source_uri,
                "required_rows": int(len(required_decisions)),
                "decision_rows": int(len(decisions)),
                "accepted_rows": int(accepted_mask.sum()),
                "closing_rows": int(
                    intake_rows["decision_status"].eq("accepted_closing_decision").sum()
                ),
                "human_blocker_rows": human_blocker_rows,
                "issue_rows": int(issue_mask.sum()),
                "missing_rows": int(status_counts.get("missing_required_decision", 0)),
                "incomplete_rows": int(status_counts.get("incomplete_decision_metadata", 0)),
                "invalid_decision_rows": int(status_counts.get("invalid_human_decision", 0)),
                "simulation_marker_rows": int(status_counts.get("blocked_simulation_marker", 0)),
                "invalid_hash_rows": int(
                    intake_rows["evidence_hash_status"].eq("invalid_sha256_format").sum()
                ),
                "rerun_artifact_issue_rows": int(
                    intake_rows["rerun_artifact_status"]
                    .isin({"missing_required", "invalid_rerun_required"})
                    .sum()
                ),
                "unknown_decision_rows": int(status_counts.get("unknown_decision_row", 0)),
                "intake_status": intake_status,
                "gate_b_next_status": "ready_to_apply_closeout_and_run_validation"
                if intake_status == "ready_for_closeout_application"
                else "blocked_by_real_decision_intake",
                "claim_status": CLAIM_STATUS,
            }
        ]
    )
    manifest = {
        "run_id": run_id,
        "source_uri": source_uri,
        "claim_status": CLAIM_STATUS,
        "intake_status": intake_status,
        "gate_b_next_status": str(summary.loc[0, "gate_b_next_status"]),
        "rows_hash": _dataframe_hash(intake_rows),
        "summary_hash": _dataframe_hash(summary),
        "closeout_ledger_hash": _dataframe_hash(closeout_ledger),
        "required_decisions_hash": _dataframe_hash(required_decisions),
        "decisions_hash": _dataframe_hash(decisions),
    }
    markdown = gate_b_decision_intake_markdown(intake_rows, summary, manifest)
    return GateBDecisionIntakeReport(
        rows=intake_rows,
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


def gate_b_decision_intake_markdown(
    rows: pd.DataFrame,
    summary: pd.DataFrame,
    manifest: dict[str, Any],
) -> str:
    visible = rows[
        [
            "ledger_id",
            "decision_status",
            "human_decision",
            "evidence_hash_status",
            "rerun_artifact_status",
            "next_action",
        ]
    ]
    return f"""# Gate B Real Decision Intake

**Status:** `{manifest["intake_status"]}`

This preflight validates reviewer-supplied real decisions before they are
applied to the Gate B closeout ledger. It does not close Gate B and does not make
benchmark rows citable.

## Summary

{_markdown_table(summary)}

## Decision Rows

{_markdown_table(visible)}

## Rules

- Every required ledger row must have a real decision.
- Simulation markers block intake.
- `evidence_hash` must use `sha256:<64 hex>`.
- `rerun_required=yes` requires a non-empty rerun artifact URI.
- `BLOCKED` and `NEEDS_SOURCE_REVIEW` are valid human decisions, but they keep
  Gate B blocked after application.
- Claim status: `{manifest["claim_status"]}`

## Manifest

- Run ID: `{manifest["run_id"]}`
- Source URI: `{manifest["source_uri"]}`
- Rows hash: `{manifest["rows_hash"]}`
- Summary hash: `{manifest["summary_hash"]}`
"""
