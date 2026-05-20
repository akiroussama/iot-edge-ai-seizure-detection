from __future__ import annotations

import argparse
import json
import subprocess
import sys

import pandas as pd

from scripts.make_leaderboard_row import build_leaderboard_row, write_outputs
from src.utils.io import read_table, write_table


def _sample_predictions(base: pd.Timestamp) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "patient_id": ["p1", "p1", "p1"],
            "recording_id": ["r1", "r1", "r1"],
            "split": ["test", "test", "test"],
            "window_start": [base, base + pd.Timedelta(hours=1), base + pd.Timedelta(hours=10)],
            "window_end": [
                base + pd.Timedelta(hours=1),
                base + pd.Timedelta(hours=2),
                base + pd.Timedelta(hours=11),
            ],
            "risk_score": [0.9, 0.2, 0.1],
            "alarm": [True, False, False],
            "forecast_label": [True, True, False],
            "is_excluded": [False, False, False],
        }
    )


def _sample_events(base: pd.Timestamp) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "patient_id": ["p1", "p1"],
            "recording_id": ["r1", "r1"],
            "seizure_start": [base + pd.Timedelta(hours=2, minutes=30), base + pd.Timedelta(days=5)],
            "seizure_end": [
                base + pd.Timedelta(hours=2, minutes=31),
                base + pd.Timedelta(days=5, minutes=1),
            ],
        }
    )


def _args(**overrides) -> argparse.Namespace:
    values = {
        "result_id": "synthetic_runner_check",
        "result_status": "pre_gate_c_exploratory_not_citable",
        "citation_status": "not_citable_pre_gate_c",
        "task_type": "forecasting",
        "dataset": "synthetic",
        "cohort": "unit-test",
        "modality": "risk_score",
        "model_name": "toy",
        "model_family": "unit",
        "split_name": "test",
        "split_policy": "synthetic",
        "split_ref": "tests",
        "horizon_name": "SPH30_SOP120",
        "sph_minutes": 30.0,
        "sop_minutes": 120.0,
        "window_seconds": 3600.0,
        "stride_seconds": 3600.0,
        "event_unit": "seizure",
        "cluster_gap_minutes": None,
        "event_filter": None,
        "prediction_filter": "split=test",
        "acknowledge_event_filter_bias": False,
        "restrict_events_to_prediction_coverage": True,
        "bss_reference": None,
        "label_audit_status": "not_applicable",
        "gate_b_status": "not_applicable_external",
        "gate_c_status": "not_started",
        "leakage_status": "not_run",
        "split_frozen_status": "not_frozen",
        "doi_or_prereg_uri": None,
        "edge_target": "unit-test",
        "quantization": None,
        "model_size_kb": None,
        "ram_kb": None,
        "flash_kb": None,
        "latency_ms": None,
        "energy_mj_per_inference": None,
        "repo_commit": "unit-test",
        "evidence_uri": "tests/test_leaderboard_runner.py",
        "notes": "synthetic unit-test row; not citable",
    }
    values.update(overrides)
    return argparse.Namespace(**values)


def test_build_leaderboard_row_from_predictions_and_events() -> None:
    base = pd.Timestamp("2026-01-01 00:00:00")
    row = build_leaderboard_row(
        predictions=_sample_predictions(base),
        events=_sample_events(base),
        reference_predictions=None,
        args=_args(),
    )

    assert row["schema_version"] == "leaderboard.v1"
    assert row["citation_status"] == "not_citable_pre_gate_c"
    assert row["events_source_total"] == 2
    assert row["events_used_for_metrics"] == 1
    assert row["prediction_rows"] == 3
    assert row["valid_prediction_rows"] == 3
    assert row["positive_windows"] == 2
    assert row["n_forecasted_or_detected"] == 1
    assert row["sensitivity"] == 1.0
    assert row["time_in_warning"] == 1 / 3
    assert row["brier_score"] is not None
    assert row["auroc"] == 1.0


def test_leaderboard_row_brier_skill_score_uses_reference_predictions() -> None:
    base = pd.Timestamp("2026-01-01 00:00:00")
    predictions = _sample_predictions(base)
    reference = predictions.copy()
    reference["risk_score"] = [0.5, 0.5, 0.5]

    row = build_leaderboard_row(
        predictions=predictions,
        events=_sample_events(base),
        reference_predictions=reference,
        args=_args(bss_reference="constant_0_5"),
    )

    assert row["bss_reference"] == "constant_0_5"
    assert row["brier_skill_score"] is not None
    assert row["brier_skill_score"] > 0


def test_write_outputs_uses_schema_header_and_not_citable_markdown(tmp_path) -> None:
    base = pd.Timestamp("2026-01-01 00:00:00")
    row = build_leaderboard_row(
        predictions=_sample_predictions(base),
        events=_sample_events(base),
        reference_predictions=None,
        args=_args(),
    )
    out_csv = tmp_path / "leaderboard.csv"
    out_json = tmp_path / "leaderboard.json"
    out_md = tmp_path / "leaderboard.md"

    write_outputs(row, out_csv, out_json, out_md)

    written = read_table(out_csv)
    assert written.loc[0, "result_id"] == "synthetic_runner_check"
    assert json.loads(out_json.read_text(encoding="utf-8"))["result_id"] == "synthetic_runner_check"
    assert "not citable" in out_md.read_text(encoding="utf-8")


def test_make_leaderboard_row_cli_writes_all_outputs(tmp_path) -> None:
    base = pd.Timestamp("2026-01-01 00:00:00")
    predictions_path = tmp_path / "predictions.csv"
    events_path = tmp_path / "events.csv"
    out_csv = tmp_path / "row.csv"
    out_json = tmp_path / "row.json"
    out_md = tmp_path / "row.md"
    write_table(_sample_predictions(base), predictions_path)
    write_table(_sample_events(base), events_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/make_leaderboard_row.py",
            "--predictions",
            str(predictions_path),
            "--events",
            str(events_path),
            "--out-csv",
            str(out_csv),
            "--out-json",
            str(out_json),
            "--out-md",
            str(out_md),
            "--result-id",
            "cli_check",
            "--dataset",
            "synthetic",
            "--model-name",
            "toy",
            "--split-policy",
            "synthetic",
            "--split-name",
            "test",
            "--prediction-filter",
            "split=test",
            "--restrict-events-to-prediction-coverage",
            "--sph-minutes",
            "30",
            "--sop-minutes",
            "120",
            "--label-audit-status",
            "not_applicable",
            "--gate-b-status",
            "not_applicable_external",
            "--repo-commit",
            "unit-test",
        ],
        check=True,
        cwd=".",
        text=True,
        capture_output=True,
    )

    assert '"result_id": "cli_check"' in result.stdout
    assert read_table(out_csv).loc[0, "result_id"] == "cli_check"
    assert out_json.exists()
    assert out_md.exists()
