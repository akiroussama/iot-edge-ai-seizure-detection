from __future__ import annotations

import json
import subprocess
import sys

import pandas as pd
import pytest

from src.reports.edge_ablation import (
    EdgeAblationConfig,
    build_edge_ablation_report,
    validate_edge_profiles,
)
from src.utils.io import read_table, write_table


def _clinical_rows() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "model_name": "linear",
                "model_family": "linear",
                "brier_skill_score": 0.18,
                "auroc": 0.64,
                "sensitivity": 0.55,
                "result_status": "pre_gate_c_exploratory_not_citable",
                "citation_status": "not_citable_pre_gate_c",
                "gate_c_status": "not_started",
            },
            {
                "model_name": "tiny_mlp",
                "model_family": "tabular_mlp",
                "brier_skill_score": 0.24,
                "auroc": 0.68,
                "sensitivity": 0.60,
                "result_status": "pre_gate_c_exploratory_not_citable",
                "citation_status": "not_citable_pre_gate_c",
                "gate_c_status": "not_started",
            },
            {
                "model_name": "large_tcn",
                "model_family": "tcn",
                "brier_skill_score": 0.25,
                "auroc": 0.69,
                "sensitivity": 0.62,
                "result_status": "pre_gate_c_exploratory_not_citable",
                "citation_status": "not_citable_pre_gate_c",
                "gate_c_status": "not_started",
            },
        ]
    )


def _edge_profiles() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "model_name": "linear",
                "edge_target": "esp32_s3",
                "quantization": "float32",
                "parameter_count": 500,
                "model_size_kb": 4.0,
                "ram_kb": 8.0,
                "flash_kb": 16.0,
                "latency_ms": 2.0,
                "energy_mj_per_inference": 0.02,
                "profiling_method": "static_estimate_v1",
                "evidence_uri": "docs/edge/linear_estimate.md",
            },
            {
                "model_name": "tiny_mlp",
                "edge_target": "esp32_s3",
                "quantization": "float32",
                "parameter_count": 5000,
                "model_size_kb": 24.0,
                "ram_kb": 40.0,
                "flash_kb": 80.0,
                "latency_ms": 7.0,
                "energy_mj_per_inference": 0.07,
                "profiling_method": "static_estimate_v1",
                "evidence_uri": "docs/edge/tiny_mlp_estimate.md",
            },
            {
                "model_name": "tiny_mlp",
                "edge_target": "esp32_s3",
                "quantization": "int8_static",
                "parameter_count": 5000,
                "model_size_kb": 7.0,
                "ram_kb": 18.0,
                "flash_kb": 32.0,
                "latency_ms": 3.0,
                "energy_mj_per_inference": 0.03,
                "profiling_method": "static_estimate_v1",
                "evidence_uri": "docs/edge/tiny_mlp_int8_estimate.md",
            },
            {
                "model_name": "large_tcn",
                "edge_target": "esp32_s3",
                "quantization": "float32",
                "parameter_count": 80_000,
                "model_size_kb": 340.0,
                "ram_kb": 280.0,
                "flash_kb": 420.0,
                "latency_ms": 60.0,
                "energy_mj_per_inference": 0.45,
                "profiling_method": "static_estimate_v1",
                "evidence_uri": "docs/edge/large_tcn_estimate.md",
            },
        ]
    )


def test_edge_ablation_builds_pareto_frontier_and_warnings() -> None:
    report = build_edge_ablation_report(
        _clinical_rows(),
        _edge_profiles(),
        config=EdgeAblationConfig(skill_metric="brier_skill_score"),
        report_name="toy_edge",
    )

    assert report.metadata["n_models"] == 3
    assert report.metadata["skill_metric"] == "brier_skill_score"
    assert report.table["edge_cost_index"].gt(0).all()
    assert report.table["clinical_score"].tolist() == [0.18, 0.24, 0.24, 0.25]
    int8_row = report.table.loc[
        report.table["model_name"].eq("tiny_mlp")
        & report.table["quantization"].eq("int8_static")
    ].iloc[0]
    fp32_row = report.table.loc[
        report.table["model_name"].eq("tiny_mlp")
        & report.table["quantization"].eq("float32")
    ].iloc[0]
    assert bool(int8_row["pareto_efficient"]) is True
    assert bool(fp32_row["pareto_efficient"]) is False
    assert "clinical_score_not_citable" in report.warnings["warning_code"].tolist()
    assert "edge_cost_estimated" in report.warnings["warning_code"].tolist()


def test_edge_profiles_require_traceable_evidence() -> None:
    edge = _edge_profiles()
    edge.loc[0, "evidence_uri"] = ""

    with pytest.raises(ValueError, match="require non-empty profiling_method and evidence_uri"):
        validate_edge_profiles(edge)


def test_edge_profiles_reject_negative_costs() -> None:
    edge = _edge_profiles()
    edge.loc[0, "latency_ms"] = -1

    with pytest.raises(ValueError, match="contains negative values"):
        validate_edge_profiles(edge)


def test_edge_ablation_rejects_unmatched_clinical_rows() -> None:
    edge = _edge_profiles()
    edge.loc[0, "model_name"] = "unknown"

    with pytest.raises(ValueError, match="without matching clinical_rows"):
        build_edge_ablation_report(_clinical_rows(), edge)


def test_make_edge_ablation_report_cli_writes_outputs(tmp_path) -> None:
    clinical_path = tmp_path / "clinical.csv"
    edge_path = tmp_path / "edge.csv"
    out_dir = tmp_path / "edge_report"
    write_table(_clinical_rows(), clinical_path)
    write_table(_edge_profiles(), edge_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/make_edge_ablation_report.py",
            "--clinical-rows",
            str(clinical_path),
            "--edge-profiles",
            str(edge_path),
            "--out-dir",
            str(out_dir),
            "--report-name",
            "toy_edge",
            "--skill-metric",
            "brier_skill_score",
        ],
        check=True,
        text=True,
        capture_output=True,
    )

    assert '"report_name": "toy_edge"' in result.stdout
    table = read_table(out_dir / "edge_ablation_table.csv")
    pareto = read_table(out_dir / "edge_pareto_frontier.csv")
    warnings = read_table(out_dir / "edge_ablation_warnings.csv")
    manifest = read_table(out_dir / "edge_ablation_manifest.csv")
    payload = json.loads((out_dir / "edge_ablation_report.json").read_text(encoding="utf-8"))
    assert len(table) == 4
    assert set(pareto["pareto_efficient"]) == {True}
    assert "edge_cost_estimated" in warnings["warning_code"].tolist()
    assert manifest.loc[0, "report_name"] == "toy_edge"
    assert payload["metadata"]["claim_scope"] == "clinical_score_and_edge_cost_are_reported_separately"
    assert "not citable" in (out_dir / "edge_ablation_report.md").read_text(encoding="utf-8")
