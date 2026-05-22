from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pandas as pd

from src.reports.gate_bc_checklist import (
    CLAIM_STATUS,
    build_gate_bc_action_checklist,
    gate_bc_action_checklist_markdown,
)


def _msg_patient_triage() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "patient_id": ["p0", "p1"],
            "triage_priority": ["p0_blocker", "p1_source_review_required"],
            "events_unmatched": [3, 2],
            "max_cluster_size": [1, 5],
        }
    )


def _msg_horizon_triage() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "sph_minutes": [60],
            "sop_minutes": [1440],
            "horizon_status": ["not_main_table_ready"],
            "valid_window_fraction": [0.16],
            "event_coverable_fraction": [0.56],
        }
    )


def _msg_summary() -> pd.DataFrame:
    return pd.DataFrame({"patients_p0_blocker": [1], "events_unmatched": [5]})


def _seizeit2_summary() -> pd.DataFrame:
    return pd.DataFrame({"blockers": [3]})


def _seizeit2_blockers() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "issue_code": [
                "gate_b_not_passed",
                "patients_below_full_cohort_threshold",
                "required_tasks_missing",
            ]
        }
    )


def _seizeit2_warnings() -> pd.DataFrame:
    return pd.DataFrame({"issue_code": ["non_ready_track_rows_present"]})


def test_gate_bc_checklist_converts_guardrails_to_actions() -> None:
    checklist = build_gate_bc_action_checklist(
        _msg_patient_triage(),
        _msg_horizon_triage(),
        _msg_summary(),
        _seizeit2_summary(),
        _seizeit2_blockers(),
        _seizeit2_warnings(),
    )

    assert checklist.summary.loc[0, "claim_status"] == CLAIM_STATUS
    assert checklist.summary.loc[0, "p0_actions"] >= 2
    assert set(checklist.actions["gate"]) == {"Gate B", "Gate C"}
    assert checklist.actions.iloc[0]["priority"] == "P0"
    text = gate_bc_action_checklist_markdown(checklist)
    assert "not citable as a benchmark result before Gate C" in text
    assert "P0 actions block" in text


def test_run_local_gate_guardrails_cli_from_markdown_reports(tmp_path: Path) -> None:
    coverage_md = tmp_path / "coverage.md"
    horizon_md = tmp_path / "horizon.md"
    seizeit2_md = tmp_path / "seizeit2.md"
    out_dir = tmp_path / "out"
    coverage_md.write_text(
        """# Coverage

## Event Coverage

| patient_id | events_total | events_matched | events_unmatched | matched_fraction | recordings | recording_hours |
| --- | --- | --- | --- | --- | --- | --- |
| p0 | 3 | 0 | 3 | 0.0 | 0 | 0.0 |

## Seizure Cluster Summary

| patient_id | clusters | clustered_events | max_cluster_size |
| --- | --- | --- | --- |
| p0 | 1 | 0 | 1 |
""",
        encoding="utf-8",
    )
    horizon_md.write_text(
        """# Horizon

| sph_minutes | sop_minutes | windows_total | valid_windows | valid_window_fraction | positive_windows_total | valid_positive_windows | right_censored_unknown_windows | events_total | events_coverable_by_valid_windows | event_coverable_fraction | events_recording_matched | events_recording_unmatched |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 60 | 1440 | 100 | 10 | 0.1 | 5 | 3 | 80 | 3 | 1 | 0.333 | 0 | 3 |
""",
        encoding="utf-8",
    )
    seizeit2_md.write_text(
        """# Dataset

## Dataset Summary

| patients | recordings | windows | events |
| --- | --- | --- | --- |
| 1 | 2 | 100 | 1 |
""",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_local_gate_guardrails.py",
            "--msg-coverage-md",
            str(coverage_md),
            "--msg-horizon-md",
            str(horizon_md),
            "--seizeit2-dataset-md",
            str(seizeit2_md),
            "--out-dir",
            str(out_dir),
        ],
        check=True,
        cwd=Path(__file__).resolve().parents[1],
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    assert payload["msg_p0_patients"] == 1
    assert payload["seizeit2_blockers"] > 0
    assert (out_dir / "gate_bc_action_checklist.md").exists()
    assert "Gate B/C Action Checklist" in (out_dir / "gate_bc_action_checklist.md").read_text(
        encoding="utf-8"
    )
