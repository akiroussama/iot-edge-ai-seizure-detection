from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Any

import pandas as pd


CLAIM_STATUS = "gate_b_closeout_ledger_pending_human_review_not_citable"
HUMAN_REVIEW_COLUMNS = [
    "human_decision",
    "reviewer_name",
    "review_date",
    "evidence_uri",
    "evidence_hash",
    "resolution_notes",
    "rerun_required",
    "rerun_artifact_uri",
]
LEDGER_COLUMNS = [
    "ledger_id",
    "gate",
    "priority",
    "domain",
    "blocker_source",
    "action",
    "evidence",
    "required_evidence",
    "owner",
    "exit_criterion",
    "closeout_status",
    *HUMAN_REVIEW_COLUMNS,
    "claim_status",
]
ALLOWED_HUMAN_DECISIONS = {
    "RESOLVED",
    "APPROVED_EXCLUSION",
    "DEFERRED",
    "NEEDS_SOURCE_REVIEW",
    "BLOCKED",
}
CLOSED_DECISIONS = {"RESOLVED", "APPROVED_EXCLUSION", "DEFERRED"}


@dataclass(frozen=True)
class GateBCloseoutLedger:
    ledger: pd.DataFrame
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


def _required_evidence_for(row: pd.Series) -> str:
    domain = str(row.get("domain", "")).lower()
    blocker_source = str(row.get("blocker_source", "")).lower()
    if "msg source-data" in domain:
        return (
            "Per-patient source decision for each P0 MSG patient: recovered wearable segment "
            "manifest or advisor-approved exclusion record; rerun MSG triage showing zero "
            "p0_blocker rows."
        )
    if "msg denominator" in domain:
        return (
            "Denominator policy signed off for source, matched, and prediction-coverable events; "
            "regenerated leaderboard rows expose all denominator fields."
        )
    if "msg horizon feasibility" in domain:
        return (
            "Advisor-approved main horizon choice or documented demotion to feasibility-negative "
            "analysis; regenerated horizon triage for chosen horizons."
        )
    if "msg horizon source" in domain:
        return (
            "Source-review decision for each source-review-required horizon and evidence that chosen "
            "main horizons no longer depend on unresolved event gaps."
        )
    if "seizeit2 full-cohort" in domain:
        return (
            "Official SeizeIT2 split manifest, expected-count source citations, full-cohort artifact "
            "coverage, and rerun cohort readiness with no P0 blockers."
        )
    if "seizeit2 track" in domain:
        return (
            "Ready track matrix covering required splits, tasks, and modality tracks; count summary "
            "matching documented expected counts."
        )
    if "seizeit2 negative" in domain:
        return (
            "Paper-table or appendix plan preserving non-ready tracks as explicit negative readiness "
            "findings."
        )
    if "freeze" in domain or "combined_guardrails" in blocker_source:
        return (
            "Completed Gate B ledger, clean guardrail rerun, and Gate C dry-run reporting "
            "ready_for_gate_c_review before split freeze."
        )
    return "Human reviewer evidence URI, decision, notes, and rerun artifact if required."


def _normalize_decision(value: Any) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip().upper()


def _closeout_status(row: pd.Series) -> str:
    decision = _normalize_decision(row.get("human_decision", ""))
    evidence_uri = "" if pd.isna(row.get("evidence_uri", "")) else str(row.get("evidence_uri", "")).strip()
    reviewer = "" if pd.isna(row.get("reviewer_name", "")) else str(row.get("reviewer_name", "")).strip()
    review_date = "" if pd.isna(row.get("review_date", "")) else str(row.get("review_date", "")).strip()
    if not decision:
        return "pending_human_decision"
    if decision not in ALLOWED_HUMAN_DECISIONS:
        return "invalid_human_decision"
    if decision in {"BLOCKED", "NEEDS_SOURCE_REVIEW"}:
        return "blocked_after_human_review"
    missing = []
    if not evidence_uri:
        missing.append("evidence_uri")
    if not reviewer:
        missing.append("reviewer_name")
    if not review_date:
        missing.append("review_date")
    if missing:
        return "incomplete_closeout_metadata"
    return "closed_by_human_review"


def build_gate_b_closeout_ledger(
    action_checklist: pd.DataFrame,
    *,
    source_uri: str,
    run_id: str = "gate_b_closeout_2026-05-22",
    decision_evidence_status: str = "pending_human_review",
) -> GateBCloseoutLedger:
    """Create a human-fillable Gate B closeout ledger from guardrail actions."""
    _require_columns(
        action_checklist,
        {
            "gate",
            "priority",
            "domain",
            "blocker_source",
            "action",
            "evidence",
            "owner",
            "exit_criterion",
        },
        "action_checklist",
    )
    rows: list[dict[str, Any]] = []
    for index, (_, action) in enumerate(action_checklist.reset_index(drop=True).iterrows(), start=1):
        row = {
            "ledger_id": f"GB-{index:03d}",
            "gate": action["gate"],
            "priority": action["priority"],
            "domain": action["domain"],
            "blocker_source": action["blocker_source"],
            "action": action["action"],
            "evidence": action["evidence"],
            "required_evidence": _required_evidence_for(action),
            "owner": action["owner"],
            "exit_criterion": action["exit_criterion"],
            "closeout_status": "pending_human_decision",
            "human_decision": "",
            "reviewer_name": "",
            "review_date": "",
            "evidence_uri": "",
            "evidence_hash": "",
            "resolution_notes": "",
            "rerun_required": "",
            "rerun_artifact_uri": "",
            "claim_status": CLAIM_STATUS,
        }
        rows.append(row)
    ledger = pd.DataFrame(rows, columns=LEDGER_COLUMNS)
    return package_gate_b_closeout_ledger(
        ledger,
        source_uri=source_uri,
        run_id=run_id,
        decision_evidence_status=decision_evidence_status,
    )


def package_gate_b_closeout_ledger(
    ledger: pd.DataFrame,
    *,
    source_uri: str,
    run_id: str = "gate_b_closeout_2026-05-22",
    decision_evidence_status: str = "human_attested_not_independently_verified",
) -> GateBCloseoutLedger:
    """Build summary, manifest, and Markdown for an existing closeout ledger."""
    _require_columns(ledger, set(LEDGER_COLUMNS), "ledger")
    packaged = ledger.copy()
    summary = summarize_gate_b_closeout_ledger(
        packaged,
        run_id=run_id,
        source_uri=source_uri,
        decision_evidence_status=decision_evidence_status,
    )
    manifest = {
        "run_id": run_id,
        "source_uri": source_uri,
        "claim_status": CLAIM_STATUS,
        "decision_evidence_status": decision_evidence_status,
        "gate_b_status": str(summary.loc[0, "gate_b_status"]),
        "ledger_rows": int(len(packaged)),
        "open_rows": int(summary.loc[0, "open_rows"]),
        "ledger_hash": _dataframe_hash(packaged),
        "summary_hash": _dataframe_hash(summary),
        "allowed_human_decisions": sorted(ALLOWED_HUMAN_DECISIONS),
        "review_columns": HUMAN_REVIEW_COLUMNS,
    }
    markdown = gate_b_closeout_markdown(packaged, summary, manifest)
    return GateBCloseoutLedger(ledger=packaged, summary=summary, manifest=manifest, markdown=markdown)


def apply_gate_b_closeout_decisions(
    ledger: pd.DataFrame,
    decisions: pd.DataFrame,
    *,
    source_uri: str,
    run_id: str = "gate_b_closeout_2026-05-22",
    decision_evidence_status: str = "human_attested_not_independently_verified",
) -> GateBCloseoutLedger:
    """Apply human-supplied decisions to a Gate B closeout ledger.

    The function records decisions as supplied evidence. It validates shape and
    decision vocabulary, but it does not verify external evidence URIs or hashes.
    """
    _require_columns(ledger, set(LEDGER_COLUMNS), "ledger")
    _require_columns(decisions, {"ledger_id", *HUMAN_REVIEW_COLUMNS}, "decisions")
    duplicate_decisions = decisions["ledger_id"].duplicated(keep=False)
    if duplicate_decisions.any():
        examples = decisions.loc[duplicate_decisions, "ledger_id"].astype(str).unique().tolist()
        raise ValueError(f"decisions contains duplicate ledger_id values: {examples}")
    out = ledger.copy()
    valid_ids = set(out["ledger_id"].astype(str))
    unknown = sorted(set(decisions["ledger_id"].astype(str)) - valid_ids)
    if unknown:
        raise ValueError(f"decisions contains unknown ledger_id values: {unknown}")
    for column in HUMAN_REVIEW_COLUMNS:
        out[column] = out[column].fillna("").astype("object")
    indexed_decisions = decisions.set_index(decisions["ledger_id"].astype(str))
    for ledger_id, decision in indexed_decisions.iterrows():
        row_mask = out["ledger_id"].astype(str).eq(str(ledger_id))
        normalized_decision = _normalize_decision(decision["human_decision"])
        if normalized_decision and normalized_decision not in ALLOWED_HUMAN_DECISIONS:
            raise ValueError(
                f"invalid human_decision for {ledger_id}: {decision['human_decision']!r}"
            )
        for column in HUMAN_REVIEW_COLUMNS:
            value = decision[column]
            if column == "human_decision":
                value = normalized_decision
            elif pd.isna(value):
                value = ""
            out.loc[row_mask, column] = value
    return package_gate_b_closeout_ledger(
        out,
        source_uri=source_uri,
        run_id=run_id,
        decision_evidence_status=decision_evidence_status,
    )


def summarize_gate_b_closeout_ledger(
    ledger: pd.DataFrame,
    *,
    run_id: str,
    source_uri: str,
    decision_evidence_status: str = "human_attested_not_independently_verified",
) -> pd.DataFrame:
    """Summarize closeout state without silently passing Gate B."""
    if ledger.empty:
        open_rows = 0
        closed_rows = 0
        blocked_rows = 0
        invalid_rows = 0
    else:
        statuses = ledger.apply(_closeout_status, axis=1)
        ledger.loc[:, "closeout_status"] = statuses
        closed_rows = int(statuses.eq("closed_by_human_review").sum())
        blocked_rows = int(statuses.eq("blocked_after_human_review").sum())
        invalid_rows = int(statuses.isin({"invalid_human_decision", "incomplete_closeout_metadata"}).sum())
        open_rows = int(len(ledger) - closed_rows)
    is_simulation = "simulation" in decision_evidence_status.lower()
    if is_simulation and len(ledger) > 0:
        gate_b_status = "simulation_complete_not_gate_b_evidence"
    elif open_rows == 0 and invalid_rows == 0 and blocked_rows == 0 and len(ledger) > 0:
        gate_b_status = "ready_for_gate_b_validation_rerun"
    else:
        gate_b_status = "blocked_pending_human_closeout"
    return pd.DataFrame(
        [
            {
                "run_id": run_id,
                "source_uri": source_uri,
                "ledger_rows": int(len(ledger)),
                "closed_rows": closed_rows,
                "open_rows": open_rows,
                "blocked_rows": blocked_rows,
                "invalid_rows": invalid_rows,
                "p0_open_rows": int(
                    ledger["priority"].eq("P0").sum()
                    - ledger.loc[ledger["priority"].eq("P0")].apply(_closeout_status, axis=1).eq(
                        "closed_by_human_review"
                    ).sum()
                )
                if not ledger.empty
                else 0,
                "gate_b_status": gate_b_status,
                "decision_evidence_status": decision_evidence_status,
                "claim_status": CLAIM_STATUS,
            }
        ]
    )


def _markdown_table(frame: pd.DataFrame, max_rows: int = 12) -> str:
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


def gate_b_closeout_markdown(
    ledger: pd.DataFrame,
    summary: pd.DataFrame,
    manifest: dict[str, Any],
) -> str:
    visible_columns = [
        "ledger_id",
        "gate",
        "priority",
        "domain",
        "action",
        "required_evidence",
        "closeout_status",
    ]
    visible = ledger[[column for column in visible_columns if column in ledger.columns]]
    decisions = ", ".join(manifest["allowed_human_decisions"])
    review_columns = ", ".join(manifest["review_columns"])
    decision_evidence_status = manifest.get("decision_evidence_status", "not recorded")
    return f"""# Gate B Closeout Ledger

**Status:** pending human closeout; this is not a Gate B pass.

This ledger converts guardrail actions into human-review rows. It does not mark
any blocker as resolved. Reviewers must fill the human decision columns and
attach evidence before Gate B can be rerun.

## Summary

{_markdown_table(summary)}

## Ledger Preview

{_markdown_table(visible)}

## Human Review Instructions

Fill these columns for every row:

`{review_columns}`

Allowed `human_decision` values:

`{decisions}`

Rows with `BLOCKED` or `NEEDS_SOURCE_REVIEW` keep Gate B blocked. Rows marked
`RESOLVED`, `APPROVED_EXCLUSION`, or `DEFERRED` must also include reviewer,
date, and evidence URI before the ledger can advance to Gate B validation rerun.

## Guardrails

- This ledger is an audit instrument, not clinical evidence.
- Blank human decision columns mean Gate B remains blocked.
- Gate C remains blocked until this ledger is closed and guardrails are rerun.
- Claim status: `{manifest["claim_status"]}`
- Decision evidence status: `{decision_evidence_status}`

## Manifest

- Run ID: `{manifest["run_id"]}`
- Source URI: `{manifest["source_uri"]}`
- Decision evidence status: `{decision_evidence_status}`
- Ledger hash: `{manifest["ledger_hash"]}`
"""
