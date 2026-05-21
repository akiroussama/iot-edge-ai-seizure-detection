from __future__ import annotations

import json
import subprocess
import sys

import pandas as pd
import pytest

from src.interpretability.counterfactual import (
    CounterfactualConfig,
    build_counterfactual_report,
    select_counterfactual_feature_columns,
)
from src.utils.io import read_table, write_table


FEATURE_COLS = ("hr_mean", "acc_energy")


def _features() -> pd.DataFrame:
    base = pd.Timestamp("2026-01-01 00:00:00")
    rows = []
    for idx in range(60):
        split = "train" if idx < 36 else "val" if idx < 48 else "test"
        hr = 55.0 + idx
        acc = (idx % 10) / 10
        risk = min(max((hr - 55.0) / 60.0 + 0.15 * acc, 0.01), 0.99)
        start = base + pd.Timedelta(hours=idx)
        rows.append(
            {
                "patient_id": f"p{idx % 4}",
                "recording_id": f"r{idx // 12}",
                "window_start": start,
                "window_end": start + pd.Timedelta(hours=1),
                "split": split,
                "forecast_label": idx % 11 == 0,
                "is_excluded": False,
                "risk_score": risk,
                "alarm": risk >= 0.5,
                "alarm_threshold": 0.5,
                "time_to_next_seizure_seconds": 10.0 if idx % 11 == 0 else 1000.0,
                "hr_mean": hr,
                "acc_energy": acc,
            }
        )
    return pd.DataFrame(rows)


def test_counterfactual_feature_selection_excludes_leakage_and_outputs() -> None:
    columns = select_counterfactual_feature_columns(_features())

    assert "hr_mean" in columns
    assert "acc_energy" in columns
    assert "risk_score" not in columns
    assert "forecast_label" not in columns
    assert "time_to_next_seizure_seconds" not in columns


def test_counterfactual_report_computes_local_changes() -> None:
    report = build_counterfactual_report(
        _features(),
        config=CounterfactualConfig(
            feature_cols=FEATURE_COLS,
            top_k_features=2,
            margin=0.02,
            ridge_alpha=1e-4,
        ),
        model_name="toy_counterfactual",
    )

    assert len(report.rows) == 60
    assert len(report.feature_changes) == 120
    computed = report.rows.loc[report.rows["counterfactual_status"].eq("computed")]
    assert not computed.empty
    assert (
        computed["counterfactual_surrogate_risk_score"]
        <= computed["target_risk_threshold"]
    ).all()
    assert report.summary.loc[0, "surrogate_fit_mse"] < 0.02
    assert report.metadata["explanation_status"] == "surrogate_post_hoc_not_causal"


def test_label_flip_does_not_change_counterfactuals() -> None:
    features = _features()
    mutated = features.copy()
    mutated["forecast_label"] = ~mutated["forecast_label"].astype(bool)
    config = CounterfactualConfig(feature_cols=FEATURE_COLS, ridge_alpha=1e-4)

    base = build_counterfactual_report(features, config=config)
    changed = build_counterfactual_report(mutated, config=config)

    comparable = [
        "counterfactual_status",
        "surrogate_risk_score",
        "counterfactual_surrogate_risk_score",
        "required_l2_shift",
        "top_counterfactual_feature",
        "top_feature_delta",
    ]
    pd.testing.assert_frame_equal(base.rows[comparable], changed.rows[comparable])
    pd.testing.assert_frame_equal(base.feature_changes, changed.feature_changes)
    assert base.metadata["training_artifact_hash"] == changed.metadata["training_artifact_hash"]


def test_counterfactual_rejects_duplicate_keys() -> None:
    features = pd.concat([_features(), _features().head(1)], ignore_index=True)

    with pytest.raises(ValueError, match="duplicate alignment keys"):
        build_counterfactual_report(
            features,
            config=CounterfactualConfig(feature_cols=FEATURE_COLS),
        )


def test_counterfactual_cli_writes_outputs(tmp_path) -> None:
    features_path = tmp_path / "features.csv"
    out_dir = tmp_path / "counterfactual"
    write_table(_features(), features_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_counterfactual_probing.py",
            "--features",
            str(features_path),
            "--out-dir",
            str(out_dir),
            "--model-name",
            "toy_counterfactual",
            "--feature-cols",
            ",".join(FEATURE_COLS),
            "--top-k-features",
            "2",
            "--margin",
            "0.02",
            "--ridge-alpha",
            "0.0001",
        ],
        check=True,
        text=True,
        capture_output=True,
    )

    assert '"model_name": "toy_counterfactual"' in result.stdout
    rows = read_table(out_dir / "counterfactual_rows.csv")
    changes = read_table(out_dir / "counterfactual_feature_changes.csv")
    summary = read_table(out_dir / "counterfactual_summary.csv")
    manifest = read_table(out_dir / "counterfactual_manifest.csv")
    payload = json.loads((out_dir / "counterfactual_report.json").read_text(encoding="utf-8"))
    assert len(rows) == 60
    assert len(changes) == 120
    assert summary.loc[0, "computed_rows"] > 0
    assert manifest.loc[0, "model_name"] == "toy_counterfactual"
    assert payload["metadata"]["result_status"] == "counterfactual_probe_pre_gate_c_not_citable"
    assert "not citable" in (out_dir / "counterfactual_report.md").read_text(encoding="utf-8")
