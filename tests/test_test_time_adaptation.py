from __future__ import annotations

import json
import subprocess
import sys

import pandas as pd
import pytest

from src.adaptation.test_time import (
    TestTimeAdaptationConfig,
    apply_test_time_adaptation,
    build_test_time_adaptation_report,
)
from src.utils.io import read_table, write_table


def _predictions() -> pd.DataFrame:
    base = pd.Timestamp("2026-01-01 00:00:00")
    rows = []
    for patient_idx, patient in enumerate(["p1", "p2"]):
        for row_idx in range(24):
            split = "train" if row_idx < 10 else "val" if row_idx < 16 else "test"
            start = base + pd.Timedelta(hours=row_idx + patient_idx * 100)
            risk = (row_idx % 12) / 11
            if patient == "p2":
                risk = 1.0 - risk
            rows.append(
                {
                    "patient_id": patient,
                    "recording_id": f"{patient}_r1",
                    "window_start": start,
                    "window_end": start + pd.Timedelta(hours=1),
                    "split": split,
                    "forecast_label": row_idx in {5, 14, 20},
                    "is_excluded": False,
                    "risk_score": risk,
                    "alarm": risk >= 0.5,
                }
            )
    return pd.DataFrame(rows)


def _config() -> TestTimeAdaptationConfig:
    return TestTimeAdaptationConfig(
        threshold_split="val",
        target_tiw=0.5,
        history_window=6,
        min_history=3,
        blend_alpha=0.6,
    )


def test_tta_adds_standard_columns_and_uses_history() -> None:
    adapted = apply_test_time_adaptation(_predictions(), config=_config())

    assert "pre_tta_risk_score" in adapted.columns
    assert "tta_adapted_risk_score" in adapted.columns
    assert "tta_history_count" in adapted.columns
    assert "tta_leakage_status" in adapted.columns
    assert adapted["risk_score"].between(0, 1).all()
    assert adapted["alarm_threshold"].nunique() == 1
    assert adapted["tta_used_history"].sum() > 0
    assert adapted["tta_leakage_status"].eq("rolling_origin_past_unlabeled_scores_only").all()


def test_label_flip_does_not_change_tta_scores() -> None:
    predictions = _predictions()
    mutated = predictions.copy()
    mutated["forecast_label"] = ~mutated["forecast_label"].astype(bool)

    base = apply_test_time_adaptation(predictions, config=_config())
    changed = apply_test_time_adaptation(mutated, config=_config())

    pd.testing.assert_series_equal(base["risk_score"], changed["risk_score"])
    pd.testing.assert_series_equal(base["alarm"], changed["alarm"])
    pd.testing.assert_series_equal(base["tta_history_count"], changed["tta_history_count"])


def test_future_scores_do_not_change_past_adapted_scores() -> None:
    predictions = _predictions()
    mutated = predictions.copy()
    future_mask = mutated["window_start"] >= pd.Timestamp("2026-01-01 18:00:00")
    mutated.loc[future_mask, "risk_score"] = 1.0 - mutated.loc[future_mask, "risk_score"]

    base = apply_test_time_adaptation(predictions, config=_config())
    changed = apply_test_time_adaptation(mutated, config=_config())
    past_mask = predictions["window_start"] < pd.Timestamp("2026-01-01 18:00:00")

    pd.testing.assert_series_equal(
        base.loc[past_mask, "risk_score"].reset_index(drop=True),
        changed.loc[past_mask, "risk_score"].reset_index(drop=True),
    )


def test_tta_report_manifest_records_hashes() -> None:
    report = build_test_time_adaptation_report(
        _predictions(),
        config=_config(),
        model_name="toy_tta",
    )

    assert report.metadata["model_name"] == "toy_tta"
    assert report.metadata["tta_used_rows"] > 0
    assert report.metadata["training_artifact_hash"] == report.manifest.loc[0, "training_artifact_hash"]
    assert set(report.summary["patient_id"]) == {"p1", "p2"}


def test_tta_rejects_duplicate_alignment_keys() -> None:
    predictions = pd.concat([_predictions(), _predictions().head(1)], ignore_index=True)

    with pytest.raises(ValueError, match="duplicate alignment keys"):
        apply_test_time_adaptation(predictions, config=_config())


def test_test_time_adaptation_cli_writes_outputs(tmp_path) -> None:
    predictions_path = tmp_path / "predictions.csv"
    out_dir = tmp_path / "tta"
    write_table(_predictions(), predictions_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_test_time_adaptation.py",
            "--predictions",
            str(predictions_path),
            "--out-dir",
            str(out_dir),
            "--model-name",
            "toy_tta",
            "--target-tiw",
            "0.5",
            "--history-window",
            "6",
            "--min-history",
            "3",
            "--blend-alpha",
            "0.6",
        ],
        check=True,
        text=True,
        capture_output=True,
    )

    assert '"model_name": "toy_tta"' in result.stdout
    predictions = read_table(out_dir / "tta_predictions.csv")
    summary = read_table(out_dir / "tta_summary.csv")
    manifest = read_table(out_dir / "tta_manifest.csv")
    payload = json.loads((out_dir / "tta_report.json").read_text(encoding="utf-8"))
    assert predictions["risk_score"].between(0, 1).all()
    assert set(summary["patient_id"]) == {"p1", "p2"}
    assert manifest.loc[0, "model_name"] == "toy_tta"
    assert payload["metadata"]["leakage_status"] == "rolling_origin_past_unlabeled_scores_only"
    assert "not citable" in (out_dir / "tta_report.md").read_text(encoding="utf-8")
