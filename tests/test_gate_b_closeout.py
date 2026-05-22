from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pandas as pd

from src.reports.gate_b_closeout import (
    CLAIM_STATUS,
    HUMAN_REVIEW_COLUMNS,
    build_gate_b_closeout_ledger,
    summarize_gate_b_closeout_ledger,
)
from src.utils.io import read_table, write_table


def _actions() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "gate": ["Gate B", "Gate C"],
            "priority": ["P0", "P0"],
            "domain": ["MSG source-data coverage", "Freeze prerequisite"],
            "blocker_source": ["msg_gap_patient_triage", "combined_guardrails"],
            "action": [
                "Recover or explicitly document exclusion for zero-recording patients.",
                "Do not freeze splits or citable rows until Gate B closes.",
            ],
            "evidence": [
                "Patients: 1942, 1219, 1675; events_unmatched=131.",
                "MSG blockers=3 P0 patients; SeizeIT2 blockers=20.",
            ],
            "owner": ["human_clinical_audit", "project_lead"],
            "exit_criterion": [
                "Rerun MSG triage has zero p0_blocker rows.",
                "Gate C dry-run reports ready_for_gate_c_review.",
            ],
            "claim_status": ["gate_bc_action_checklist_pre_gate_c_not_citable"] * 2,
        }
    )


def test_gate_b_closeout_ledger_keeps_human_fields_blank() -> None:
    package = build_gate_b_closeout_ledger(
        _actions(),
        source_uri="reports/local_gate_guardrails_2026-05-22/gate_bc_action_checklist.csv",
    )

    assert package.manifest["gate_b_status"] == "blocked_pending_human_closeout"
    assert package.manifest["open_rows"] == 2
    assert package.summary.loc[0, "p0_open_rows"] == 2
    assert package.ledger["claim_status"].eq(CLAIM_STATUS).all()
    for column in HUMAN_REVIEW_COLUMNS:
        assert package.ledger[column].eq("").all()
    assert "pending human closeout" in package.markdown
    assert "not a Gate B pass" in package.markdown


def test_gate_b_closeout_summary_requires_evidence_for_closed_rows() -> None:
    package = build_gate_b_closeout_ledger(_actions(), source_uri="actions.csv")
    ledger = package.ledger.copy()
    ledger.loc[:, "human_decision"] = "RESOLVED"
    ledger.loc[:, "reviewer_name"] = "reviewer"
    ledger.loc[:, "review_date"] = "2026-05-22"

    missing_evidence = summarize_gate_b_closeout_ledger(
        ledger,
        run_id="test",
        source_uri="actions.csv",
    )
    assert missing_evidence.loc[0, "gate_b_status"] == "blocked_pending_human_closeout"
    assert missing_evidence.loc[0, "invalid_rows"] == 2

    ledger.loc[:, "evidence_uri"] = "docs/evidence.md"
    closed = summarize_gate_b_closeout_ledger(
        ledger,
        run_id="test",
        source_uri="actions.csv",
    )
    assert closed.loc[0, "gate_b_status"] == "ready_for_gate_b_validation_rerun"
    assert closed.loc[0, "closed_rows"] == 2


def test_build_gate_b_closeout_ledger_cli_writes_outputs(tmp_path: Path) -> None:
    actions_path = tmp_path / "actions.csv"
    out_dir = tmp_path / "ledger"
    write_table(_actions(), actions_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/build_gate_b_closeout_ledger.py",
            "--action-checklist",
            str(actions_path),
            "--out-dir",
            str(out_dir),
            "--run-id",
            "test-ledger",
        ],
        check=True,
        cwd=Path(__file__).resolve().parents[1],
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    ledger = read_table(out_dir / "gate_b_closeout_ledger.csv")
    manifest = json.loads((out_dir / "gate_b_closeout_manifest.json").read_text(encoding="utf-8"))
    markdown = (out_dir / "gate_b_closeout_ledger.md").read_text(encoding="utf-8")
    assert payload["gate_b_status"] == "blocked_pending_human_closeout"
    assert len(ledger) == 2
    assert manifest["run_id"] == "test-ledger"
    assert "Human Review Instructions" in markdown
