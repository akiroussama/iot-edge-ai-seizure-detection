from __future__ import annotations

import subprocess
import sys

import pandas as pd
import pytest

from src.reports.federated_benchmark import (
    FederatedBenchmarkConfig,
    federated_benchmark_summary,
    validate_federated_site_results,
)
from src.utils.io import read_table, write_table


def _site_rows() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "site_id": ["site_a", "site_b"],
            "dataset": ["synthetic", "synthetic"],
            "task_type": ["forecasting", "forecasting"],
            "model_name": ["model_x", "model_x"],
            "horizon_name": ["SPH30_SOP120", "SPH30_SOP120"],
            "events_used_for_metrics": [10, 30],
            "prediction_rows": [100, 300],
            "valid_prediction_rows": [90, 270],
            "sensitivity": [0.5, 0.9],
            "false_alarm_rate_per_day": [1.0, 0.2],
            "time_in_warning": [0.2, 0.1],
            "brier_score": [0.20, 0.10],
            "brier_skill_score": [0.1, 0.3],
            "expected_calibration_error": [0.05, 0.03],
            "auroc": [0.65, 0.85],
            "auprc": [0.20, 0.40],
            "citation_status": ["not_citable_pre_gate_c", "not_citable_pre_gate_c"],
            "gate_c_status": ["not_started", "not_started"],
            "leakage_status": ["clean", "clean"],
            "split_frozen_status": ["not_frozen", "not_frozen"],
            "evidence_uri": ["site_a.json", "site_b.json"],
        }
    )


def test_federated_summary_aggregates_site_level_rows() -> None:
    report = federated_benchmark_summary(_site_rows())
    row = report.summary.iloc[0]

    assert row["site_count"] == 2
    assert row["total_events_used_for_metrics"] == 40
    assert row["weighted_sensitivity"] == pytest.approx(0.8)
    assert row["site_range_sensitivity"] == pytest.approx(0.4)
    assert row["federated_claim_status"] == "not_citable_until_all_sites_gate_c_clean"


def test_federated_validation_rejects_raw_window_columns() -> None:
    rows = _site_rows()
    rows["patient_id"] = ["p1", "p2"]

    with pytest.raises(ValueError, match="raw row-level columns"):
        validate_federated_site_results(rows)


def test_federated_citable_summary_requires_clean_site_rows() -> None:
    config = FederatedBenchmarkConfig(citation_status="citable_after_gate_c", gate_c_status="passed")

    with pytest.raises(ValueError, match="non-citable or dirty site rows"):
        federated_benchmark_summary(_site_rows(), config=config)


def test_federated_citable_summary_accepts_all_clean_gate_c_rows() -> None:
    rows = _site_rows()
    rows["citation_status"] = "citable_after_gate_c"
    rows["gate_c_status"] = "passed"
    rows["split_frozen_status"] = "frozen_git_tag"
    config = FederatedBenchmarkConfig(citation_status="citable_after_gate_c", gate_c_status="passed")

    report = federated_benchmark_summary(rows, config=config)

    assert report.summary.loc[0, "federated_claim_status"] == "citable_federated_summary"
    assert report.summary.loc[0, "citation_status"] == "citable_after_gate_c"


def test_make_federated_benchmark_report_cli_writes_outputs(tmp_path) -> None:
    site_results = tmp_path / "site_results.csv"
    out_dir = tmp_path / "federated"
    write_table(_site_rows(), site_results)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/make_federated_benchmark_report.py",
            "--site-results",
            str(site_results),
            "--out-dir",
            str(out_dir),
        ],
        check=True,
        text=True,
        capture_output=True,
    )

    assert '"aggregate_rows": 1' in result.stdout
    summary = read_table(out_dir / "federated_benchmark_summary.csv")
    manifest = read_table(out_dir / "federated_benchmark_manifest.csv")
    assert summary.loc[0, "weighted_sensitivity"] == pytest.approx(0.8)
    assert manifest.loc[0, "analysis_status"] == "site_level_federated_benchmark_summary"
    assert "not citable" in (out_dir / "federated_benchmark_report.md").read_text(encoding="utf-8")
