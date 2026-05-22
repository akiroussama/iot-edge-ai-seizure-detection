from __future__ import annotations

import json
import subprocess
import sys

import pandas as pd

from src.artifacts.registry import build_artifact_record, build_gate_c_registry
from src.reports.gate_c_dry_run import build_gate_c_dry_run_report
from src.utils.io import read_table, write_table


def _write_artifacts(tmp_path) -> dict[str, str]:
    events_path = tmp_path / "events.csv"
    labels_path = tmp_path / "labels.csv"
    splits_path = tmp_path / "splits.csv"
    write_table(
        pd.DataFrame(
            {
                "patient_id": ["p1", "p2"],
                "recording_id": ["r1", "r2"],
                "seizure_start": ["2026-01-01 00:00:00", "2026-01-02 00:00:00"],
                "seizure_end": ["2026-01-01 00:01:00", "2026-01-02 00:01:00"],
            }
        ),
        events_path,
    )
    write_table(
        pd.DataFrame(
            {
                "patient_id": ["p1", "p1", "p2"],
                "recording_id": ["r1", "r1", "r2"],
                "split": ["train", "val", "test"],
                "forecast_label": [False, True, False],
                "is_excluded": [False, False, False],
            }
        ),
        labels_path,
    )
    write_table(
        pd.DataFrame(
            {
                "patient_id": ["p1", "p2"],
                "split": ["train", "test"],
            }
        ),
        splits_path,
    )
    return {
        "events": str(events_path),
        "labels": str(labels_path),
        "splits": str(splits_path),
    }


def _registry(tmp_path, *, gate_c_status: str, freeze_status: str, doi: str | None = None) -> dict:
    paths = _write_artifacts(tmp_path)
    artifacts = [
        build_artifact_record(name=name, role=name, path=path)
        for name, path in paths.items()
    ]
    return build_gate_c_registry(
        registry_id="synthetic_gate_c_dry_run",
        dataset="synthetic",
        dataset_version="v1",
        source_uri="tests/test_gate_c_dry_run.py",
        generation_command="pytest tests/test_gate_c_dry_run.py",
        artifacts=artifacts,
        split_manifest={
            "split_policy": "synthetic",
            "split_ids": ["train", "val", "test"],
            "split_ref": "tests/synthetic_split_manifest",
            "horizon_name": "SPH5_SOP30",
            "sph_minutes": 5.0,
            "sop_minutes": 30.0,
        },
        gate_c_status=gate_c_status,
        freeze_status=freeze_status,
        doi_or_prereg_uri=doi,
    )


def test_gate_c_dry_run_reports_blockers_without_claiming_pass(tmp_path) -> None:
    registry = _registry(tmp_path, gate_c_status="partial", freeze_status="pending_human_audit")

    report = build_gate_c_dry_run_report(
        registry,
        gate_b_status="partial",
    )

    assert report.diagnostics["structural_ok"] is True
    assert report.diagnostics["citable_ready"] is False
    assert report.diagnostics["readiness_status"] == "blocked"
    assert any("gate_b_status" in blocker for blocker in report.diagnostics["blockers"])
    assert any("gate_c_status" in blocker for blocker in report.diagnostics["blockers"])
    assert any("freeze_status" in blocker for blocker in report.diagnostics["blockers"])
    assert any("doi_or_prereg_uri" in blocker for blocker in report.diagnostics["blockers"])
    assert "not a Gate C pass" in report.markdown


def test_gate_c_dry_run_accepts_clean_frozen_registry(tmp_path) -> None:
    registry = _registry(
        tmp_path,
        gate_c_status="passed",
        freeze_status="frozen",
        doi="doi:10.0000/synthetic",
    )

    report = build_gate_c_dry_run_report(
        registry,
        gate_b_status="passed",
    )

    assert report.diagnostics["structural_ok"] is True
    assert report.diagnostics["frozen_verification_ok"] is True
    assert report.diagnostics["citable_ready"] is True
    assert report.diagnostics["blockers"] == []
    assert set(report.diagnostics["present_roles"]) >= {"events", "labels", "splits"}
    assert report.artifact_summary["role"].tolist() == ["events", "labels", "splits"]


def test_gate_c_dry_run_cli_writes_diagnostics(tmp_path) -> None:
    registry = _registry(tmp_path, gate_c_status="partial", freeze_status="pending_human_audit")
    registry_path = tmp_path / "registry.json"
    out_json = tmp_path / "dry_run.json"
    out_md = tmp_path / "dry_run.md"
    summary_path = tmp_path / "artifact_summary.csv"
    registry_path.write_text(json.dumps(registry, indent=2), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/make_gate_c_dry_run_report.py",
            "--registry",
            str(registry_path),
            "--out-json",
            str(out_json),
            "--out-md",
            str(out_md),
            "--artifact-summary-out",
            str(summary_path),
            "--gate-b-status",
            "partial",
        ],
        check=True,
        text=True,
        capture_output=True,
    )

    stdout = json.loads(result.stdout)
    payload = json.loads(out_json.read_text(encoding="utf-8"))
    markdown = out_md.read_text(encoding="utf-8")
    artifact_summary = read_table(summary_path)
    assert stdout["readiness_status"] == "blocked"
    assert payload["citable_ready"] is False
    assert "Gate C Dry-Run Diagnostics" in markdown
    assert len(artifact_summary) == 3
