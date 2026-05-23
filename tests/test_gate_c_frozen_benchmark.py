from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

from src.artifacts.gate_c_frozen_benchmark import (
    GateCFrozenBenchmarkConfig,
    run_gate_c_frozen_benchmark,
)
from src.artifacts.registry import build_artifact_record, build_gate_c_registry
from src.utils.io import read_table, write_table


def _frozen_tables() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    base = pd.Timestamp("2026-01-01 00:00:00")
    rows = []
    for split_idx, split in enumerate(("train", "val", "test")):
        for patient_idx, patient in enumerate(("p1", "p2")):
            for hour in range(8):
                start = base + pd.Timedelta(days=split_idx * 3 + patient_idx, hours=hour)
                rows.append(
                    {
                        "patient_id": patient,
                        "recording_id": f"{patient}_{split}",
                        "window_start": start,
                        "window_end": start + pd.Timedelta(hours=1),
                        "split": split,
                        "forecast_label": hour in {2, 5},
                        "is_excluded": False,
                    }
                )
    labels = pd.DataFrame(rows)
    events = pd.DataFrame(
        [
            {
                "patient_id": "p1",
                "recording_id": "p1_test",
                "seizure_start": base + pd.Timedelta(days=6, hours=4, minutes=30),
                "seizure_end": base + pd.Timedelta(days=6, hours=4, minutes=31),
                "recording_match_status": "matched",
            },
            {
                "patient_id": "p2",
                "recording_id": "p2_test",
                "seizure_start": base + pd.Timedelta(days=7, hours=7, minutes=30),
                "seizure_end": base + pd.Timedelta(days=7, hours=7, minutes=31),
                "recording_match_status": "matched",
            },
        ]
    )
    splits = labels[["patient_id", "recording_id", "window_start", "window_end", "split"]].copy()
    return events, labels, splits


def _write_registry(tmp_path: Path, *, use_data_path: bool = False) -> Path:
    artifact_dir = tmp_path / ("data" if use_data_path else "reports") / "frozen" / "artifacts"
    artifact_dir.mkdir(parents=True)
    events, labels, splits = _frozen_tables()
    write_table(events, artifact_dir / "events.csv")
    write_table(labels, artifact_dir / "labels.csv")
    write_table(splits, artifact_dir / "splits.csv")
    rel_events = (artifact_dir / "events.csv").relative_to(tmp_path)
    rel_labels = (artifact_dir / "labels.csv").relative_to(tmp_path)
    rel_splits = (artifact_dir / "splits.csv").relative_to(tmp_path)
    registry = build_gate_c_registry(
        registry_id="synthetic_gate_c",
        dataset="synthetic",
        dataset_version="v1",
        source_uri=str(rel_labels),
        generation_command="pytest synthetic",
        artifacts=[
            build_artifact_record(name="events", role="events", path=rel_events, root=tmp_path),
            build_artifact_record(name="labels", role="labels", path=rel_labels, root=tmp_path),
            build_artifact_record(name="splits", role="splits", path=rel_splits, root=tmp_path),
        ],
        split_manifest={
            "split_policy": "temporal_recording_elapsed_time",
            "split_ids": ["train", "val", "test"],
            "split_ref": str(rel_splits),
            "horizon_name": "SPH60_SOP1440",
            "sph_minutes": 60.0,
            "sop_minutes": 1440.0,
        },
        gate_c_status="passed",
        freeze_status="frozen",
        doi_or_prereg_uri="doi:10.0000/synthetic",
    )
    registry_path = tmp_path / "reports" / "frozen" / "gate_c_registry.json"
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    registry_path.write_text(json.dumps(registry, indent=2), encoding="utf-8")
    return registry_path


def test_gate_c_frozen_benchmark_writes_null_results(tmp_path) -> None:
    registry = _write_registry(tmp_path)
    out_dir = tmp_path / "reports" / "benchmark"

    result = run_gate_c_frozen_benchmark(
        GateCFrozenBenchmarkConfig(
            registry_path=registry.relative_to(tmp_path),
            out_dir=out_dir,
            root=tmp_path,
            bootstrap_samples=5,
        )
    )

    assert result.manifest["benchmark_status"] == "gate_c_frozen_null_benchmark_complete"
    assert len(result.leaderboard) == 4
    assert result.leaderboard["citation_status"].eq("citable_after_gate_c").all()
    assert "split_prevalence_prior" in set(result.leaderboard["model_name"])
    self_row = result.leaderboard.loc[
        result.leaderboard["model_name"].eq("split_prevalence_prior")
    ].iloc[0]
    assert self_row["brier_skill_score"] == pytest.approx(0.0)
    assert (out_dir / "forecastability_atlas.csv").exists()
    assert (out_dir / "frozen_benchmark_audit.md").exists()


def test_gate_c_frozen_benchmark_refuses_data_artifacts(tmp_path) -> None:
    registry = _write_registry(tmp_path, use_data_path=True)

    with pytest.raises(ValueError, match=r"refuses non-frozen data/\* inputs"):
        run_gate_c_frozen_benchmark(
            GateCFrozenBenchmarkConfig(
                registry_path=registry.relative_to(tmp_path),
                out_dir=tmp_path / "out",
                root=tmp_path,
                bootstrap_samples=5,
            )
        )


def test_gate_c_frozen_benchmark_cli(tmp_path) -> None:
    registry = _write_registry(tmp_path)
    out_dir = tmp_path / "reports" / "benchmark_cli"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_gate_c_frozen_benchmark.py",
            "--registry",
            str(registry.relative_to(tmp_path)),
            "--root",
            str(tmp_path),
            "--out-dir",
            str(out_dir),
            "--bootstrap-samples",
            "5",
        ],
        check=True,
        text=True,
        capture_output=True,
    )

    assert "gate_c_frozen_null_benchmark_complete" in result.stdout
    leaderboard = read_table(out_dir / "leaderboard_rows.csv")
    assert len(leaderboard) == 4
