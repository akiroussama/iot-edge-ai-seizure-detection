from __future__ import annotations

import json
import subprocess
import sys
from argparse import Namespace

import pandas as pd
import pytest

from scripts.make_leaderboard_row import build_leaderboard_row
from src.artifacts.registry import (
    build_artifact_record,
    build_gate_c_registry,
    load_registry,
    verify_gate_c_registry,
)
from src.utils.io import write_table


def _predictions(base: pd.Timestamp) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "patient_id": ["p1", "p1", "p1"],
            "recording_id": ["r1", "r1", "r1"],
            "split": ["test", "test", "test"],
            "window_start": [base, base + pd.Timedelta(hours=1), base + pd.Timedelta(hours=2)],
            "window_end": [
                base + pd.Timedelta(hours=1),
                base + pd.Timedelta(hours=2),
                base + pd.Timedelta(hours=3),
            ],
            "risk_score": [0.9, 0.2, 0.1],
            "alarm": [True, False, False],
            "forecast_label": [True, False, False],
            "is_excluded": [False, False, False],
        }
    )


def _events(base: pd.Timestamp) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "patient_id": ["p1"],
            "recording_id": ["r1"],
            "seizure_start": [base + pd.Timedelta(hours=1, minutes=30)],
            "seizure_end": [base + pd.Timedelta(hours=1, minutes=31)],
        }
    )


def _leaderboard_args(**overrides) -> Namespace:
    values = {
        "result_id": "synthetic_gate_c_row",
        "result_status": "gate_c_frozen_citable",
        "citation_status": "citable_after_gate_c",
        "task_type": "forecasting",
        "dataset": "synthetic_gate_c",
        "cohort": "unit-test",
        "modality": "risk_score",
        "model_name": "toy",
        "model_family": "unit",
        "split_name": "test",
        "split_policy": "synthetic",
        "split_ref": "tests/gate_c_split",
        "horizon_name": "SPH0_SOP60",
        "sph_minutes": 0.0,
        "sop_minutes": 60.0,
        "window_seconds": 3600.0,
        "stride_seconds": 3600.0,
        "event_unit": "seizure",
        "cluster_gap_minutes": None,
        "event_filter": None,
        "prediction_filter": "split=test",
        "acknowledge_event_filter_bias": False,
        "restrict_events_to_prediction_coverage": True,
        "bss_reference": None,
        "artifact_registry": None,
        "label_audit_status": "full_human_audited",
        "gate_b_status": "passed",
        "gate_c_status": "passed",
        "leakage_status": "clean",
        "split_frozen_status": "frozen_git_tag",
        "doi_or_prereg_uri": "doi:10.0000/synthetic",
        "edge_target": "unit-test",
        "quantization": None,
        "model_size_kb": None,
        "ram_kb": None,
        "flash_kb": None,
        "latency_ms": None,
        "energy_mj_per_inference": None,
        "repo_commit": "unit-test",
        "evidence_uri": "tests/test_gate_c_registry.py",
        "notes": "synthetic citable row for registry guardrail tests",
    }
    values.update(overrides)
    return Namespace(**values)


def _frozen_registry(tmp_path, predictions_path, events_path) -> dict:
    artifacts = [
        build_artifact_record(
            name="predictions",
            role="predictions",
            path=predictions_path,
        ),
        build_artifact_record(
            name="events",
            role="events",
            path=events_path,
        ),
    ]
    return build_gate_c_registry(
        registry_id="synthetic_gate_c_registry",
        dataset="synthetic_gate_c",
        dataset_version="v1",
        source_uri="tests/test_gate_c_registry.py",
        generation_command="pytest tests/test_gate_c_registry.py",
        artifacts=artifacts,
        split_manifest={
            "split_policy": "synthetic",
            "split_ids": ["test"],
            "split_ref": "tests/gate_c_split",
            "horizon_name": "SPH0_SOP60",
            "sph_minutes": 0.0,
            "sop_minutes": 60.0,
        },
        gate_c_status="passed",
        freeze_status="frozen",
        doi_or_prereg_uri="doi:10.0000/synthetic",
        notes="synthetic registry for tests",
    )


def test_registry_verification_detects_tampering(tmp_path) -> None:
    path = tmp_path / "predictions.csv"
    write_table(_predictions(pd.Timestamp("2026-01-01")), path)
    record = build_artifact_record(name="predictions", role="predictions", path=path)
    registry = build_gate_c_registry(
        registry_id="tamper_check",
        dataset="synthetic_gate_c",
        dataset_version="v1",
        source_uri="tests",
        generation_command="pytest",
        artifacts=[record],
        split_manifest={
            "split_policy": "synthetic",
            "split_ids": ["test"],
            "split_ref": "tests/gate_c_split",
        },
    )

    assert verify_gate_c_registry(registry)["ok"]

    path.write_text(path.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    result = verify_gate_c_registry(registry)

    assert not result["ok"]
    assert any("sha256 mismatch" in error for error in result["errors"])


def test_make_and_verify_gate_c_registry_cli(tmp_path) -> None:
    base = pd.Timestamp("2026-01-01")
    predictions_path = tmp_path / "predictions.csv"
    events_path = tmp_path / "events.csv"
    registry_path = tmp_path / "registry.json"
    write_table(_predictions(base), predictions_path)
    write_table(_events(base), events_path)

    subprocess.run(
        [
            sys.executable,
            "scripts/make_gate_c_registry.py",
            "--out",
            str(registry_path),
            "--registry-id",
            "cli_registry",
            "--dataset",
            "synthetic_gate_c",
            "--dataset-version",
            "v1",
            "--source-uri",
            "tests/test_gate_c_registry.py",
            "--generation-command",
            "pytest tests/test_gate_c_registry.py",
            "--artifact",
            f"predictions=predictions:{predictions_path}",
            "--artifact",
            f"events=events:{events_path}",
            "--split-policy",
            "synthetic",
            "--split-ref",
            "tests/gate_c_split",
            "--split-id",
            "test",
            "--gate-c-status",
            "passed",
            "--freeze-status",
            "frozen",
        ],
        check=True,
        text=True,
        capture_output=True,
    )

    verify = subprocess.run(
        [
            sys.executable,
            "scripts/verify_gate_c_registry.py",
            "--registry",
            str(registry_path),
            "--require-frozen",
        ],
        check=True,
        text=True,
        capture_output=True,
    )

    payload = json.loads(verify.stdout)
    assert payload["ok"] is True
    assert load_registry(registry_path)["artifacts"][1]["event_count"] == 1


def test_leaderboard_citable_row_requires_registry() -> None:
    base = pd.Timestamp("2026-01-01")

    with pytest.raises(ValueError, match="artifact-registry"):
        build_leaderboard_row(
            predictions=_predictions(base),
            events=_events(base),
            args=_leaderboard_args(),
        )


def test_leaderboard_accepts_citable_row_with_frozen_clean_registry(tmp_path) -> None:
    base = pd.Timestamp("2026-01-01")
    predictions = _predictions(base)
    events = _events(base)
    predictions_path = tmp_path / "predictions.csv"
    events_path = tmp_path / "events.csv"
    registry_path = tmp_path / "registry.json"
    write_table(predictions, predictions_path)
    write_table(events, events_path)
    registry_path.write_text(
        json.dumps(_frozen_registry(tmp_path, predictions_path, events_path), indent=2),
        encoding="utf-8",
    )

    row = build_leaderboard_row(
        predictions=predictions,
        events=events,
        args=_leaderboard_args(artifact_registry=str(registry_path)),
    )

    assert row["citation_status"] == "citable_after_gate_c"
    assert row["gate_c_status"] == "passed"
