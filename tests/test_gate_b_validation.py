from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pandas as pd

from src.reports.gate_b_closeout import (
    apply_gate_b_closeout_decisions,
    build_gate_b_closeout_ledger,
)
from src.reports.gate_b_validation import (
    CLAIM_STATUS,
    build_gate_b_validation_rerun_report,
)
from src.utils.io import read_table, write_table


def _actions() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "gate": ["Gate B", "Gate B", "Gate C"],
            "priority": ["P0", "P1", "P0"],
            "domain": [
                "MSG source-data coverage",
                "MSG denominator integrity",
                "Freeze prerequisite",
            ],
            "blocker_source": [
                "msg_gap_patient_triage",
                "msg_gap_patient_triage",
                "combined_guardrails",
            ],
            "action": [
                "Recover or explicitly document exclusion for zero-recording patients.",
                "Resolve unmatched events or lock a matched-event-only denominator policy.",
                "Do not freeze splits or citable rows until Gate B closes.",
            ],
            "evidence": [
                "Patients: p0; events_unmatched=3.",
                "Patients: p1; events_unmatched=2.",
                "MSG blockers=1 P0 patient; SeizeIT2 blockers=1.",
            ],
            "owner": ["human_clinical_audit", "human_clinical_audit", "project_lead"],
            "exit_criterion": [
                "Rerun MSG triage has zero p0_blocker rows.",
                "All denominators are declared.",
                "Gate C dry-run reports ready_for_gate_c_review.",
            ],
            "claim_status": ["gate_bc_action_checklist_pre_gate_c_not_citable"] * 3,
        }
    )


def _msg_summary() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "patients_p0_blocker": [1],
            "events_unmatched": [5],
            "horizons_not_main_table_ready": [2],
            "horizons_source_review_required": [1],
        }
    )


def _seizeit2_summary() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "readiness_status": ["blocked"],
            "blockers": [3],
            "warnings": [1],
        }
    )


def _decisions(ids: list[str], *, decision: str = "RESOLVED", note: str = "real") -> pd.DataFrame:
    return pd.DataFrame(
        {
            "ledger_id": ids,
            "human_decision": [decision] * len(ids),
            "reviewer_name": ["O. Akir"] * len(ids),
            "review_date": ["2026-05-22"] * len(ids),
            "evidence_uri": [f"s3://audit/{ledger_id}.pdf" for ledger_id in ids],
            "evidence_hash": [f"sha256:{ledger_id.lower()}" for ledger_id in ids],
            "resolution_notes": [note] * len(ids),
            "rerun_required": ["no"] * len(ids),
            "rerun_artifact_uri": ["N/A"] * len(ids),
        }
    )


def test_gate_b_validation_blocks_pending_real_closeout() -> None:
    ledger = build_gate_b_closeout_ledger(_actions(), source_uri="actions.csv")
    partial = apply_gate_b_closeout_decisions(
        ledger.ledger,
        _decisions(["GB-001"]),
        source_uri="partial.csv",
        run_id="partial",
    )
    closeout_summary = pd.DataFrame(
        {
            "real_open_rows": [1],
            "gate_b_real_closeout_status": ["blocked_pending_real_evidence"],
        }
    )

    report = build_gate_b_validation_rerun_report(
        closeout_ledger=partial.ledger,
        action_checklist=_actions(),
        msg_summary=_msg_summary(),
        seizeit2_summary=_seizeit2_summary(),
        closeout_summary=closeout_summary,
    )

    assert report.summary.loc[0, "gate_b_validation_status"] == "blocked_pending_real_closeout"
    assert bool(report.summary.loc[0, "gate_b_passed"]) is False
    assert report.summary.loc[0, "gate_b_open_actions"] == 1
    assert report.summary.loc[0, "gate_b_p0_open_actions"] == 0
    assert report.summary.loc[0, "claim_status"] == CLAIM_STATUS
    assert "not a Gate C pass" in report.markdown


def test_gate_b_validation_passes_when_gate_b_actions_are_closed() -> None:
    ledger = build_gate_b_closeout_ledger(_actions(), source_uri="actions.csv")
    closed = apply_gate_b_closeout_decisions(
        ledger.ledger,
        _decisions(["GB-001", "GB-002"]),
        source_uri="closed.csv",
        run_id="closed",
    )
    closeout_summary = pd.DataFrame(
        {
            "real_open_rows": [0],
            "gate_b_real_closeout_status": ["ready_for_gate_b_validation_rerun"],
        }
    )

    report = build_gate_b_validation_rerun_report(
        closeout_ledger=closed.ledger,
        action_checklist=_actions(),
        msg_summary=_msg_summary(),
        seizeit2_summary=_seizeit2_summary(),
        closeout_summary=closeout_summary,
    )

    assert report.summary.loc[0, "gate_b_validation_status"] == "passed_ready_for_gate_c_dry_run"
    assert bool(report.summary.loc[0, "gate_b_passed"]) is True
    assert report.summary.loc[0, "gate_c_next_status"] == "ready_for_gate_c_dry_run"


def test_gate_b_validation_detects_source_review_blocker() -> None:
    ledger = build_gate_b_closeout_ledger(_actions(), source_uri="actions.csv")
    closed = apply_gate_b_closeout_decisions(
        ledger.ledger,
        _decisions(["GB-001"], decision="NEEDS_SOURCE_REVIEW", note="needs reviewer"),
        source_uri="blocked.csv",
        run_id="blocked",
    )

    report = build_gate_b_validation_rerun_report(
        closeout_ledger=closed.ledger,
        action_checklist=_actions(),
        msg_summary=_msg_summary(),
        seizeit2_summary=_seizeit2_summary(),
    )

    assert report.summary.loc[0, "gate_b_validation_status"] == "needs_source_review"
    assert report.matrix.loc[0, "validation_status"] == "needs_source_review"


def test_gate_b_validation_blocks_simulation_markers_in_real_ledger() -> None:
    ledger = build_gate_b_closeout_ledger(_actions(), source_uri="actions.csv")
    simulated = apply_gate_b_closeout_decisions(
        ledger.ledger,
        _decisions(["GB-001", "GB-002"], note="simulated positive decision"),
        source_uri="simulation.csv",
        run_id="simulation",
        decision_evidence_status="simulation_positive_not_real_gate_b_evidence",
    )

    report = build_gate_b_validation_rerun_report(
        closeout_ledger=simulated.ledger,
        action_checklist=_actions(),
        msg_summary=_msg_summary(),
        seizeit2_summary=_seizeit2_summary(),
    )

    assert report.summary.loc[0, "gate_b_validation_status"] == "blocked_simulation_marker_detected"
    assert bool(report.summary.loc[0, "simulation_marker_detected"]) is True


def test_gate_b_validation_cli_writes_outputs(tmp_path: Path) -> None:
    guardrails = tmp_path / "guardrails"
    out_dir = tmp_path / "validation"
    ledger = build_gate_b_closeout_ledger(_actions(), source_uri="actions.csv")
    partial = apply_gate_b_closeout_decisions(
        ledger.ledger,
        _decisions(["GB-001"]),
        source_uri="partial.csv",
        run_id="partial",
    )
    ledger_path = tmp_path / "closeout_ledger.csv"
    closeout_summary_path = tmp_path / "closeout_summary.csv"
    write_table(partial.ledger, ledger_path)
    write_table(
        pd.DataFrame(
            {
                "real_open_rows": [1],
                "gate_b_real_closeout_status": ["blocked_pending_real_evidence"],
            }
        ),
        closeout_summary_path,
    )
    write_table(_actions(), guardrails / "gate_bc_action_checklist.csv")
    write_table(_msg_summary(), guardrails / "msg_gap_summary.csv")
    write_table(_seizeit2_summary(), guardrails / "seizeit2_cohort_readiness_summary.csv")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_gate_b_validation_rerun.py",
            "--closeout-ledger",
            str(ledger_path),
            "--closeout-summary",
            str(closeout_summary_path),
            "--guardrails-dir",
            str(guardrails),
            "--out-dir",
            str(out_dir),
            "--run-id",
            "validation",
        ],
        check=True,
        cwd=Path(__file__).resolve().parents[1],
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    matrix = read_table(out_dir / "gate_b_validation_matrix.csv")
    summary = read_table(out_dir / "gate_b_validation_summary.csv")
    manifest = json.loads((out_dir / "gate_b_validation_manifest.json").read_text())
    markdown = (out_dir / "gate_b_validation_rerun.md").read_text(encoding="utf-8")
    assert payload["gate_b_validation_status"] == "blocked_pending_real_closeout"
    assert len(matrix) == 3
    assert summary.loc[0, "gate_b_open_actions"] == 1
    assert manifest["run_id"] == "validation"
    assert "Gate B Validation Rerun" in markdown
