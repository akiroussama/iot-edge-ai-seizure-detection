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
from src.reports.gate_b_decision_intake import (
    CLAIM_STATUS,
    build_gate_b_decision_intake_report,
)
from src.utils.io import read_table, write_table


def _actions() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "gate": ["Gate B", "Gate B", "Gate B"],
            "priority": ["P0", "P1", "P2"],
            "domain": [
                "MSG source-data coverage",
                "MSG denominator integrity",
                "MSG horizon source review",
            ],
            "blocker_source": [
                "msg_gap_patient_triage",
                "msg_gap_patient_triage",
                "msg_gap_horizon_triage",
            ],
            "action": [
                "Recover or explicitly document exclusion for zero-recording patients.",
                "Resolve unmatched events or lock a matched-event-only denominator policy.",
                "Keep source-review-required horizons out of citable tables until event gaps close.",
            ],
            "evidence": [
                "Patients: p0; events_unmatched=3.",
                "Patients: p1; events_unmatched=2.",
                "Horizons needing source review: SPH5/SOP360.",
            ],
            "owner": ["human_clinical_audit"] * 3,
            "exit_criterion": [
                "Rerun MSG triage has zero p0_blocker rows.",
                "All denominators are declared.",
                "Rerun horizon triage has no source_review_required rows.",
            ],
            "claim_status": ["gate_bc_action_checklist_pre_gate_c_not_citable"] * 3,
        }
    )


def _base_ledger() -> pd.DataFrame:
    package = build_gate_b_closeout_ledger(_actions(), source_uri="actions.csv")
    partial = apply_gate_b_closeout_decisions(
        package.ledger,
        _decisions(["GB-001"]),
        source_uri="partial.csv",
        run_id="partial",
    )
    return partial.ledger


def _required_template() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "ledger_id": ["GB-002", "GB-003"],
            "required_evidence": [
                "Denominator policy signed off.",
                "Source-review decision for source-review-required horizons.",
            ],
            "human_decision": ["", ""],
            "reviewer_name": ["", ""],
            "review_date": ["", ""],
            "evidence_uri": ["", ""],
            "evidence_hash": ["", ""],
            "resolution_notes": ["", ""],
            "rerun_required": ["", ""],
            "rerun_artifact_uri": ["", ""],
        }
    )


def _decisions(
    ids: list[str],
    *,
    decision: str = "RESOLVED",
    note: str = "real decision",
    evidence_hash: str = "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    rerun_required: str = "no",
    rerun_artifact_uri: str = "N/A",
) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "ledger_id": ids,
            "human_decision": [decision] * len(ids),
            "reviewer_name": ["O. Akir"] * len(ids),
            "review_date": ["2026-05-23"] * len(ids),
            "evidence_uri": [f"s3://audit/{ledger_id}.pdf" for ledger_id in ids],
            "evidence_hash": [evidence_hash] * len(ids),
            "resolution_notes": [note] * len(ids),
            "rerun_required": [rerun_required] * len(ids),
            "rerun_artifact_uri": [rerun_artifact_uri] * len(ids),
        }
    )


def test_gate_b_decision_intake_blocks_blank_template() -> None:
    report = build_gate_b_decision_intake_report(
        closeout_ledger=_base_ledger(),
        required_decisions=_required_template(),
        decisions=_required_template(),
    )

    assert report.summary.loc[0, "intake_status"] == "blocked_invalid_or_incomplete_decisions"
    assert report.summary.loc[0, "missing_rows"] == 0
    assert report.summary.loc[0, "incomplete_rows"] == 2
    assert report.summary.loc[0, "accepted_rows"] == 0
    assert report.summary.loc[0, "claim_status"] == CLAIM_STATUS
    assert "does not close Gate B" in report.markdown


def test_gate_b_decision_intake_accepts_complete_closing_decisions() -> None:
    report = build_gate_b_decision_intake_report(
        closeout_ledger=_base_ledger(),
        required_decisions=_required_template(),
        decisions=_decisions(["GB-002", "GB-003"]),
    )

    assert report.summary.loc[0, "intake_status"] == "ready_for_closeout_application"
    assert report.summary.loc[0, "gate_b_next_status"] == (
        "ready_to_apply_closeout_and_run_validation"
    )
    assert report.summary.loc[0, "accepted_rows"] == 2
    assert report.rows["decision_status"].tolist() == [
        "accepted_closing_decision",
        "accepted_closing_decision",
    ]


def test_gate_b_decision_intake_detects_simulation_marker() -> None:
    report = build_gate_b_decision_intake_report(
        closeout_ledger=_base_ledger(),
        required_decisions=_required_template(),
        decisions=_decisions(["GB-002", "GB-003"], note="simulated positive decision"),
    )

    assert report.summary.loc[0, "simulation_marker_rows"] == 2
    assert report.summary.loc[0, "intake_status"] == "blocked_invalid_or_incomplete_decisions"


def test_gate_b_decision_intake_detects_hash_and_rerun_issues() -> None:
    report = build_gate_b_decision_intake_report(
        closeout_ledger=_base_ledger(),
        required_decisions=_required_template(),
        decisions=_decisions(
            ["GB-002", "GB-003"],
            evidence_hash="sha256:not-a-real-hash",
            rerun_required="yes",
            rerun_artifact_uri="N/A",
        ),
    )

    assert report.summary.loc[0, "invalid_hash_rows"] == 2
    assert report.summary.loc[0, "rerun_artifact_issue_rows"] == 2
    assert report.rows["decision_status"].tolist() == [
        "invalid_evidence_hash",
        "invalid_evidence_hash",
    ]


def test_gate_b_decision_intake_accepts_human_blocker_decision() -> None:
    report = build_gate_b_decision_intake_report(
        closeout_ledger=_base_ledger(),
        required_decisions=_required_template(),
        decisions=_decisions(["GB-002", "GB-003"], decision="NEEDS_SOURCE_REVIEW"),
    )

    assert report.summary.loc[0, "intake_status"] == (
        "ready_for_closeout_application_with_human_blockers"
    )
    assert report.summary.loc[0, "human_blocker_rows"] == 2
    assert report.summary.loc[0, "gate_b_next_status"] == "blocked_by_real_decision_intake"


def test_gate_b_decision_intake_cli_writes_outputs(tmp_path: Path) -> None:
    ledger_path = tmp_path / "ledger.csv"
    required_path = tmp_path / "required.csv"
    decisions_path = tmp_path / "decisions.csv"
    out_dir = tmp_path / "out"
    write_table(_base_ledger(), ledger_path)
    write_table(_required_template(), required_path)
    write_table(_decisions(["GB-002", "GB-003"]), decisions_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_gate_b_real_decision_intake.py",
            "--closeout-ledger",
            str(ledger_path),
            "--required-decisions",
            str(required_path),
            "--decisions",
            str(decisions_path),
            "--out-dir",
            str(out_dir),
            "--run-id",
            "intake",
        ],
        check=True,
        cwd=Path(__file__).resolve().parents[1],
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    rows = read_table(out_dir / "gate_b_real_decision_intake_rows.csv")
    summary = read_table(out_dir / "gate_b_real_decision_intake_summary.csv")
    manifest = json.loads((out_dir / "gate_b_real_decision_intake_manifest.json").read_text())
    markdown = (out_dir / "gate_b_real_decision_intake.md").read_text(encoding="utf-8")
    assert payload["intake_status"] == "ready_for_closeout_application"
    assert len(rows) == 2
    assert summary.loc[0, "accepted_rows"] == 2
    assert manifest["run_id"] == "intake"
    assert "Gate B Real Decision Intake" in markdown
