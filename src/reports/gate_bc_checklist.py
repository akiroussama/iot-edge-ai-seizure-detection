from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Any

import pandas as pd


CLAIM_STATUS = "gate_bc_action_checklist_pre_gate_c_not_citable"


@dataclass(frozen=True)
class GateBCActionChecklist:
    actions: pd.DataFrame
    summary: pd.DataFrame
    metadata: dict[str, Any]


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


def _append_action(
    rows: list[dict[str, Any]],
    *,
    gate: str,
    priority: str,
    domain: str,
    blocker_source: str,
    action: str,
    evidence: str,
    owner: str = "human_clinical_audit",
    exit_criterion: str,
) -> None:
    rows.append(
        {
            "gate": gate,
            "priority": priority,
            "domain": domain,
            "blocker_source": blocker_source,
            "action": action,
            "evidence": evidence,
            "owner": owner,
            "exit_criterion": exit_criterion,
            "claim_status": CLAIM_STATUS,
        }
    )


def _list_values(frame: pd.DataFrame, column: str, *, limit: int = 12) -> str:
    if frame.empty or column not in frame.columns:
        return "none"
    values = [str(value) for value in frame[column].dropna().tolist()]
    if len(values) <= limit:
        return ", ".join(values) if values else "none"
    return ", ".join(values[:limit]) + f", ... ({len(values)} total)"


def _list_horizons(frame: pd.DataFrame, *, limit: int = 12) -> str:
    if frame.empty or not {"sph_minutes", "sop_minutes"}.issubset(frame.columns):
        return "none"
    values = [
        f"SPH{float(row['sph_minutes']):g}/SOP{float(row['sop_minutes']):g}"
        for _, row in frame.iterrows()
    ]
    if len(values) <= limit:
        return ", ".join(values)
    return ", ".join(values[:limit]) + f", ... ({len(values)} total)"


def build_gate_bc_action_checklist(
    msg_patient_triage: pd.DataFrame,
    msg_horizon_triage: pd.DataFrame,
    msg_summary: pd.DataFrame,
    seizeit2_summary: pd.DataFrame,
    seizeit2_blockers: pd.DataFrame,
    seizeit2_warnings: pd.DataFrame,
    *,
    source_label: str = "local_committed_reports_2026-05-22",
) -> GateBCActionChecklist:
    """Convert guardrail outputs into a human-executable Gate B/Gate C checklist."""
    rows: list[dict[str, Any]] = []

    msg_p0 = msg_patient_triage.loc[msg_patient_triage["triage_priority"].eq("p0_blocker")]
    if not msg_p0.empty:
        _append_action(
            rows,
            gate="Gate B",
            priority="P0",
            domain="MSG source-data coverage",
            blocker_source="msg_gap_patient_triage",
            action="Recover or explicitly document exclusion for zero-recording/zero-matched patients.",
            evidence=(
                f"Patients: {_list_values(msg_p0, 'patient_id')}; "
                f"events_unmatched={int(msg_p0['events_unmatched'].sum())}."
            ),
            exit_criterion=(
                "Each P0 patient has recovered wearable segments or an advisor-approved exclusion "
                "record, and rerun MSG triage has zero p0_blocker rows."
            ),
        )

    msg_p1_source = msg_patient_triage.loc[
        msg_patient_triage["triage_priority"].eq("p1_source_review_required")
    ]
    if not msg_p1_source.empty:
        _append_action(
            rows,
            gate="Gate B",
            priority="P1",
            domain="MSG denominator integrity",
            blocker_source="msg_gap_patient_triage",
            action="Resolve unmatched events or lock a matched-event-only denominator policy.",
            evidence=(
                f"Patients: {_list_values(msg_p1_source, 'patient_id')}; "
                f"events_unmatched={int(msg_p1_source['events_unmatched'].sum())}."
            ),
            exit_criterion=(
                "All unmatched events have source-review decisions and every leaderboard row "
                "declares source, matched, and prediction-coverable denominators."
            ),
        )

    msg_p1_timeline = msg_patient_triage.loc[
        msg_patient_triage["triage_priority"].eq("p1_timeline_review_required")
    ]
    if not msg_p1_timeline.empty:
        _append_action(
            rows,
            gate="Gate B",
            priority="P1",
            domain="MSG clinical timeline audit",
            blocker_source="msg_gap_patient_triage",
            action="Review large seizure clusters and low-margin timeline cases before freeze.",
            evidence=(
                f"Patients: {_list_values(msg_p1_timeline, 'patient_id')}; "
                f"max_cluster_size={int(msg_p1_timeline['max_cluster_size'].max())}."
            ),
            exit_criterion=(
                "Cluster policy, postictal anchor, and event grouping are approved and reflected "
                "in regenerated audit artifacts."
            ),
        )

    msg_not_main = msg_horizon_triage.loc[msg_horizon_triage["horizon_status"].eq("not_main_table_ready")]
    if not msg_not_main.empty:
        _append_action(
            rows,
            gate="Gate B",
            priority="P1",
            domain="MSG horizon feasibility",
            blocker_source="msg_gap_horizon_triage",
            action="Demote failing SPH/SOP horizons or document them as feasibility-negative analyses.",
            evidence=(
                f"Horizons: {_list_horizons(msg_not_main)}; "
                f"min_valid_window_fraction={float(msg_not_main['valid_window_fraction'].min()):.3f}; "
                f"min_event_coverable_fraction={float(msg_not_main['event_coverable_fraction'].min()):.3f}."
            ),
            exit_criterion=(
                "Main-paper horizon choice is advisor-approved and any failing horizons are excluded "
                "from main claims or labeled as negative feasibility findings."
            ),
        )

    msg_source_horizons = msg_horizon_triage.loc[
        msg_horizon_triage["horizon_status"].eq("source_review_required")
    ]
    if not msg_source_horizons.empty:
        _append_action(
            rows,
            gate="Gate B",
            priority="P2",
            domain="MSG horizon source review",
            blocker_source="msg_gap_horizon_triage",
            action="Keep source-review-required horizons out of citable tables until event gaps close.",
            evidence=f"Horizons needing source review: {_list_horizons(msg_source_horizons)}.",
            exit_criterion="Rerun horizon triage has no source_review_required rows for chosen main horizons.",
        )

    if not seizeit2_blockers.empty:
        p0_codes = {
            "gate_b_not_passed",
            "gate_c_not_passed",
            "patients_below_full_cohort_threshold",
            "events_below_full_cohort_threshold",
            "official_split_manifest_not_clean",
        }
        p0 = seizeit2_blockers.loc[seizeit2_blockers["issue_code"].isin(p0_codes)]
        p1 = seizeit2_blockers.loc[~seizeit2_blockers["issue_code"].isin(p0_codes)]
        if not p0.empty:
            _append_action(
                rows,
                gate="Gate B",
                priority="P0",
                domain="SeizeIT2 full-cohort evidence",
                blocker_source="seizeit2_cohort_readiness_blockers",
                action="Stop full-cohort wording until official split/count/source coverage is complete.",
                evidence=f"Blockers: {_list_values(p0, 'issue_code')}.",
                exit_criterion=(
                    "SeizeIT2 readiness rerun reports Gate B/Gate C passed, expected counts verified, "
                    "official splits clean, and no P0 cohort blockers."
                ),
            )
        if not p1.empty:
            _append_action(
                rows,
                gate="Gate B",
                priority="P1",
                domain="SeizeIT2 track completeness",
                blocker_source="seizeit2_cohort_readiness_blockers",
                action="Complete required split/task/modality readiness rows before benchmark claims.",
                evidence=f"Blockers: {_list_values(p1, 'issue_code')}.",
                exit_criterion="All required split/task/modality combinations have ready track rows.",
            )

    if not seizeit2_warnings.empty:
        _append_action(
            rows,
            gate="Gate B",
            priority="P2",
            domain="SeizeIT2 negative readiness rows",
            blocker_source="seizeit2_cohort_readiness_warnings",
            action="Preserve non-ready track rows as explicit negative readiness findings.",
            evidence=f"Warnings: {_list_values(seizeit2_warnings, 'issue_code')}.",
            exit_criterion="Paper tables and text disclose non-ready tracks instead of hiding them.",
        )

    _append_action(
        rows,
        gate="Gate C",
        priority="P0",
        domain="Freeze prerequisite",
        blocker_source="combined_guardrails",
        action="Do not freeze splits or citable rows until Gate B checklist items are closed.",
        evidence=(
            f"MSG blockers={int(msg_summary.loc[0, 'patients_p0_blocker']) if not msg_summary.empty else 'unknown'} P0 patients; "
            f"SeizeIT2 blockers={len(seizeit2_blockers)}."
        ),
        owner="project_lead",
        exit_criterion=(
            "Gate B audit log is complete, guardrails rerun cleanly, and Gate C dry-run reports "
            "ready_for_gate_c_review."
        ),
    )

    actions = pd.DataFrame(rows)
    if not actions.empty:
        priority_order = {"P0": 0, "P1": 1, "P2": 2}
        gate_order = {"Gate B": 0, "Gate C": 1}
        actions = (
            actions.assign(
                _priority_rank=actions["priority"].map(priority_order).fillna(9),
                _gate_rank=actions["gate"].map(gate_order).fillna(9),
            )
            .sort_values(["_priority_rank", "_gate_rank", "domain"])
            .drop(columns=["_priority_rank", "_gate_rank"])
            .reset_index(drop=True)
        )

    summary = pd.DataFrame(
        [
            {
                "source_label": source_label,
                "actions_total": int(len(actions)),
                "p0_actions": int(actions["priority"].eq("P0").sum()) if not actions.empty else 0,
                "p1_actions": int(actions["priority"].eq("P1").sum()) if not actions.empty else 0,
                "p2_actions": int(actions["priority"].eq("P2").sum()) if not actions.empty else 0,
                "gate_b_actions": int(actions["gate"].eq("Gate B").sum()) if not actions.empty else 0,
                "gate_c_actions": int(actions["gate"].eq("Gate C").sum()) if not actions.empty else 0,
                "claim_status": CLAIM_STATUS,
            }
        ]
    )
    metadata = {
        "claim_status": CLAIM_STATUS,
        "source_label": source_label,
        "actions_hash": _dataframe_hash(actions),
        "summary_hash": _dataframe_hash(summary),
    }
    return GateBCActionChecklist(actions=actions, summary=summary, metadata=metadata)


def _markdown_table(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "_No rows._"
    headers = [str(column) for column in frame.columns]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for _, row in frame.iterrows():
        cells = []
        for column in frame.columns:
            value = row[column]
            cells.append("" if pd.isna(value) else str(value))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def gate_bc_action_checklist_markdown(checklist: GateBCActionChecklist) -> str:
    return f"""# Gate B/C Action Checklist

**Citation status:** not citable as a benchmark result before Gate C.

This checklist is generated from local guardrail outputs. It is an operational
audit plan, not a model result and not clinical evidence.

## Summary

{_markdown_table(checklist.summary)}

## Actions

{_markdown_table(checklist.actions)}

## Interpretation Rules

- P0 actions block any claim of full evaluation readiness.
- P1 actions block main-paper tables until resolved or explicitly demoted.
- P2 actions should be completed before submission packaging.
- Gate C freeze can start only after Gate B actions are closed and the Gate C
  dry-run reports `ready_for_gate_c_review`.

## Manifest

- Claim status: `{checklist.metadata["claim_status"]}`
- Source label: `{checklist.metadata["source_label"]}`
- Actions hash: `{checklist.metadata["actions_hash"]}`
"""
