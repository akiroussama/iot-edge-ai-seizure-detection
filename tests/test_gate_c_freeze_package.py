from __future__ import annotations

import json
import subprocess
import sys

import pandas as pd
import pytest

from src.artifacts.gate_c_freeze_package import (
    build_gate_c_freeze_package,
    validate_gate_c_freeze_inputs,
    write_gate_c_freeze_package,
)
from src.artifacts.registry import load_registry, verify_gate_c_registry
from src.utils.io import read_table, write_table


def _events(base: pd.Timestamp) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "patient_id": ["p1", "p2", "p3"],
            "recording_id": ["r1", "r2", "r3"],
            "seizure_start": [
                base + pd.Timedelta(hours=1),
                base + pd.Timedelta(days=1, hours=1),
                base + pd.Timedelta(days=2, hours=1),
            ],
            "seizure_end": [
                base + pd.Timedelta(hours=1, minutes=1),
                base + pd.Timedelta(days=1, hours=1, minutes=1),
                base + pd.Timedelta(days=2, hours=1, minutes=1),
            ],
        }
    )


def _labels(base: pd.Timestamp) -> pd.DataFrame:
    rows = []
    spec = (("p1", "r1", "train"), ("p2", "r2", "val"), ("p3", "r3", "test"))
    for idx, (patient, recording, split) in enumerate(spec):
        start = base + pd.Timedelta(days=idx)
        for window_idx in range(2):
            rows.append(
                {
                    "patient_id": patient,
                    "recording_id": recording,
                    "window_start": start + pd.Timedelta(hours=window_idx),
                    "window_end": start + pd.Timedelta(hours=window_idx + 1),
                    "split": split,
                    "forecast_label": window_idx == 1,
                    "is_excluded": False,
                }
            )
    return pd.DataFrame(rows)


def _splits(labels: pd.DataFrame) -> pd.DataFrame:
    return labels[["patient_id", "recording_id", "window_start", "window_end", "split"]].copy()


def _write_inputs(tmp_path) -> tuple[str, str, str]:
    base = pd.Timestamp("2026-01-01 00:00:00")
    events_path = tmp_path / "events.csv"
    labels_path = tmp_path / "labels.csv"
    splits_path = tmp_path / "splits.csv"
    labels = _labels(base)
    write_table(_events(base), events_path)
    write_table(labels, labels_path)
    write_table(_splits(labels), splits_path)
    return str(events_path), str(labels_path), str(splits_path)


def _build_package(tmp_path):
    events_path, labels_path, splits_path = _write_inputs(tmp_path)
    return build_gate_c_freeze_package(
        events_path=events_path,
        labels_path=labels_path,
        splits_path=splits_path,
        registry_id="synthetic_gate_c_freeze",
        dataset="synthetic",
        dataset_version="v1",
        source_uri="tests/test_gate_c_freeze_package.py",
        generation_command="pytest tests/test_gate_c_freeze_package.py",
        split_policy="synthetic_temporal",
        split_ref="tests/synthetic_split_manifest",
        split_ids=("train", "val", "test"),
        horizon_name="SPH5_SOP30",
        sph_minutes=5.0,
        sop_minutes=30.0,
        doi_or_prereg_uri="doi:10.0000/synthetic-gate-c-freeze",
        notes="synthetic freeze package for tests",
    )


def test_gate_c_freeze_package_builds_citable_registry(tmp_path) -> None:
    package = _build_package(tmp_path)

    assert package.dry_run_diagnostics["readiness_status"] == "ready_for_gate_c_review"
    assert package.dry_run_diagnostics["citable_ready"] is True
    assert package.dry_run_diagnostics["blockers"] == []
    assert package.registry["gate_c_status"] == "passed"
    assert package.registry["freeze_status"] == "frozen"
    assert {artifact["role"] for artifact in package.registry["artifacts"]} == {
        "events",
        "labels",
        "splits",
    }
    assert verify_gate_c_registry(package.registry, require_frozen=True)["ok"] is True


def test_gate_c_freeze_package_writes_outputs(tmp_path) -> None:
    package = write_gate_c_freeze_package(_build_package(tmp_path), tmp_path / "out")

    registry = load_registry(package.output_paths["registry"])
    dry_run = json.loads(open(package.output_paths["dry_run_json"], encoding="utf-8").read())
    manifest = json.loads(open(package.output_paths["manifest"], encoding="utf-8").read())
    artifact_summary = read_table(package.output_paths["artifact_summary"])
    assert registry["freeze_status"] == "frozen"
    assert dry_run["citable_ready"] is True
    assert manifest["freeze_package_status"] == "gate_c_frozen_citable"
    assert artifact_summary["role"].tolist() == ["events", "labels", "splits"]


def test_gate_c_freeze_inputs_reject_missing_label_contract() -> None:
    base = pd.Timestamp("2026-01-01 00:00:00")
    labels = _labels(base).drop(columns=["forecast_label"])

    with pytest.raises(ValueError, match="labels missing required columns"):
        validate_gate_c_freeze_inputs(
            events=_events(base),
            labels=labels,
            splits=_splits(_labels(base)),
            expected_split_ids=("train", "val", "test"),
        )


def test_gate_c_freeze_inputs_reject_split_mismatch() -> None:
    base = pd.Timestamp("2026-01-01 00:00:00")
    labels = _labels(base)
    splits = _splits(labels)
    splits.loc[0, "split"] = "test"

    with pytest.raises(ValueError, match="splits disagrees with labels"):
        validate_gate_c_freeze_inputs(
            events=_events(base),
            labels=labels,
            splits=splits,
            expected_split_ids=("train", "val", "test"),
        )


def test_gate_c_freeze_package_cli_writes_citable_package(tmp_path) -> None:
    events_path, labels_path, splits_path = _write_inputs(tmp_path)
    out_dir = tmp_path / "cli_out"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/build_gate_c_freeze_package.py",
            "--events",
            events_path,
            "--labels",
            labels_path,
            "--splits",
            splits_path,
            "--out-dir",
            str(out_dir),
            "--registry-id",
            "cli_synthetic_gate_c_freeze",
            "--dataset",
            "synthetic",
            "--dataset-version",
            "v1",
            "--source-uri",
            "tests/test_gate_c_freeze_package.py",
            "--generation-command",
            "pytest tests/test_gate_c_freeze_package.py",
            "--split-policy",
            "synthetic_temporal",
            "--split-ref",
            "tests/synthetic_split_manifest",
            "--split-id",
            "train",
            "--split-id",
            "val",
            "--split-id",
            "test",
            "--horizon-name",
            "SPH5_SOP30",
            "--sph-minutes",
            "5",
            "--sop-minutes",
            "30",
            "--doi-or-prereg-uri",
            "doi:10.0000/synthetic-gate-c-freeze",
        ],
        check=True,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    dry_run = json.loads((out_dir / "gate_c_dry_run.json").read_text(encoding="utf-8"))
    assert payload["readiness_status"] == "ready_for_gate_c_review"
    assert payload["citable_ready"] is True
    assert dry_run["blockers"] == []
