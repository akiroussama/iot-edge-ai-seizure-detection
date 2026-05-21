from __future__ import annotations

import json
import subprocess
import sys

import pandas as pd
import pytest

from scripts.make_leaderboard_row import build_leaderboard_row
from src.features.observability import (
    ObservabilityConfig,
    add_observability_features,
    apply_observability_abstention,
    observability_metric_strata,
    observability_summary,
)
from tests.test_leaderboard_runner import _args, _sample_events
from src.utils.io import read_table, write_table


def _feature_table() -> pd.DataFrame:
    base = pd.Timestamp("2026-01-01 00:00:00")
    return pd.DataFrame(
        {
            "patient_id": ["p1", "p1", "p1", "p1"],
            "recording_id": ["r1", "r1", "r1", "r1"],
            "split": ["test", "test", "test", "test"],
            "window_start": [base + pd.Timedelta(minutes=30 * i) for i in range(4)],
            "window_end": [base + pd.Timedelta(minutes=30 * (i + 1)) for i in range(4)],
            "hr_sample_count": [30, 2, 30, 0],
            "hr_expected_samples": [30, 30, 30, 30],
            "acc_sample_count": [90, 90, 10, 0],
            "acc_expected_samples": [90, 90, 90, 90],
            "hr_mean": [72.0, 73.0, 310.0, float("nan")],
            "hr_min": [65.0, 70.0, 300.0, float("nan")],
            "hr_max": [85.0, 90.0, 320.0, float("nan")],
            "acc_energy": [0.3, 0.2, 0.1, float("nan")],
            "risk_score": [0.8, 0.7, 0.2, 0.1],
            "alarm": [True, True, False, False],
            "forecast_label": [True, False, False, False],
            "is_excluded": [False, False, False, False],
        }
    )


def test_observability_scores_bad_quality_windows_lower() -> None:
    enriched = add_observability_features(
        _feature_table(),
        config=ObservabilityConfig(observable_threshold=0.65),
    )

    assert enriched.loc[0, "is_observable"]
    assert not enriched.loc[3, "is_observable"]
    assert enriched.loc[0, "observable_score"] > enriched.loc[3, "observable_score"]
    assert "low_sensor_coverage" in enriched.loc[3, "deficiency_reason"]
    assert enriched.loc[3, "deficiency_time_minutes"] == pytest.approx(30.0)


def test_observability_does_not_depend_on_labels() -> None:
    features = _feature_table()
    flipped = features.copy()
    flipped["forecast_label"] = ~flipped["forecast_label"].astype(bool)

    base = add_observability_features(features)
    changed = add_observability_features(flipped)

    assert base["observable_score"].tolist() == pytest.approx(changed["observable_score"].tolist())
    assert base["is_observable"].tolist() == changed["is_observable"].tolist()


def test_abstention_budget_selects_worst_deficient_windows() -> None:
    enriched = add_observability_features(_feature_table())
    out = apply_observability_abstention(enriched, max_abstention_fraction=0.25)

    assert out["abstain_for_observability"].sum() == 1
    abstained = out.loc[out["abstain_for_observability"]].iloc[0]
    assert abstained["observable_score"] == out["observable_score"].min()


def test_observability_summary_and_metric_strata() -> None:
    enriched = apply_observability_abstention(add_observability_features(_feature_table()))

    summary = observability_summary(enriched, group_cols=("split",))
    strata = observability_metric_strata(enriched)

    assert summary.loc[0, "rows"] == 4
    assert summary.loc[0, "deficient_rows"] > 0
    assert {"observable", "deficient"} == set(strata["stratum"])
    assert strata["brier_score"].notna().all()


def test_leaderboard_row_records_observability_fields() -> None:
    base = pd.Timestamp("2026-01-01 00:00:00")
    predictions = apply_observability_abstention(add_observability_features(_feature_table()))

    row = build_leaderboard_row(
        predictions=predictions,
        events=_sample_events(base),
        reference_predictions=None,
        args=_args(prediction_filter="split=test"),
    )

    assert row["observable_prediction_rows"] is not None
    assert row["deficient_prediction_rows"] > 0
    assert row["abstained_prediction_rows"] == row["deficient_prediction_rows"]
    assert row["deficiency_time_minutes"] > 0
    assert 0 <= row["mean_observable_score"] <= 1


def test_compute_observability_report_cli_writes_outputs(tmp_path) -> None:
    features_path = tmp_path / "features.csv"
    out_dir = tmp_path / "observability"
    write_table(_feature_table(), features_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/compute_observability_report.py",
            "--features",
            str(features_path),
            "--out-dir",
            str(out_dir),
            "--modalities",
            "hr,acc",
            "--observable-threshold",
            "0.65",
            "--max-abstention-fraction",
            "0.25",
            "--group-cols",
            "split",
            "--citation-status",
            "synthetic_not_citable",
        ],
        check=True,
        text=True,
        capture_output=True,
    )

    assert '"rows": 4' in result.stdout
    enriched = read_table(out_dir / "observability_enriched.csv")
    summary = read_table(out_dir / "observability_summary.csv")
    payload = json.loads((out_dir / "observability_report.json").read_text(encoding="utf-8"))
    assert "observable_score" in enriched.columns
    assert summary.loc[0, "deficient_rows"] > 0
    assert payload["metadata"]["citation_status"] == "synthetic_not_citable"
    assert "not citable" in (out_dir / "observability_report.md").read_text(encoding="utf-8")
