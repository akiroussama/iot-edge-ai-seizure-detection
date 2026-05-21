from __future__ import annotations

import subprocess
import sys

import pandas as pd
import pytest

from src.reports.forecastability_atlas import (
    ForecastabilityThresholds,
    build_forecastability_atlas,
    forecastability_atlas_markdown,
    reliability_slope_table,
)
from src.utils.io import read_table, write_table


def _leaderboard_rows() -> pd.DataFrame:
    base = {
        "dataset": "synthetic",
        "cohort": "pooled",
        "modality": "hr",
        "model_family": "unit",
        "split_name": "test",
        "horizon_name": "SPH30_SOP120",
        "sph_minutes": 30.0,
        "sop_minutes": 120.0,
        "events_used_for_metrics": 20,
        "valid_prediction_rows": 500,
        "sensitivity": 0.7,
        "false_alarm_rate_per_day": 0.5,
        "time_in_warning": 0.1,
        "bss_reference": "split_prevalence_prior",
        "expected_calibration_error": 0.05,
        "citation_status": "citable_after_gate_c",
        "gate_c_status": "passed",
    }
    return pd.DataFrame(
        [
            {
                **base,
                "model_name": "good_model",
                "brier_skill_score": 0.24,
                "brier_skill_score_ci_low": 0.08,
                "brier_skill_score_ci_high": 0.40,
            },
            {
                **base,
                "model_name": "overlap_model",
                "brier_skill_score": 0.05,
                "brier_skill_score_ci_low": -0.04,
                "brier_skill_score_ci_high": 0.16,
            },
            {
                **base,
                "model_name": "underpowered_model",
                "events_used_for_metrics": 2,
                "brier_skill_score": 0.30,
                "brier_skill_score_ci_low": 0.10,
                "brier_skill_score_ci_high": 0.50,
            },
            {
                **base,
                "model_name": "pre_gate_c_model",
                "citation_status": "not_citable_pre_gate_c",
                "gate_c_status": "not_started",
                "brier_skill_score": 0.30,
                "brier_skill_score_ci_low": 0.10,
                "brier_skill_score_ci_high": 0.50,
            },
        ]
    )


def test_forecastability_atlas_labels_positive_overlap_underpowered_and_precite() -> None:
    atlas = build_forecastability_atlas(
        _leaderboard_rows(),
        thresholds=ForecastabilityThresholds(min_events=5, min_valid_prediction_rows=100),
        gate_c_required=True,
    )

    labels = dict(zip(atlas["model_name"], atlas["forecastability_label"], strict=True))
    ready = dict(zip(atlas["model_name"], atlas["paper_table_ready"], strict=True))
    assert labels["good_model"] == "forecastable_above_null"
    assert bool(ready["good_model"]) is True
    assert labels["overlap_model"] == "unforecastable_null_overlap"
    assert labels["underpowered_model"] == "underpowered"
    assert labels["pre_gate_c_model"] == "not_citable_pre_gate_c"
    assert bool(ready["pre_gate_c_model"]) is False


def test_forecastability_atlas_marks_patient_scope() -> None:
    rows = _leaderboard_rows().head(1).copy()
    rows["patient_id"] = "p1"

    atlas = build_forecastability_atlas(rows, gate_c_required=True)

    assert atlas.loc[0, "atlas_scope"] == "per_patient"
    assert atlas.loc[0, "patient_id"] == "p1"


def test_reliability_slope_table_uses_weighted_bins() -> None:
    reliability = pd.DataFrame(
        {
            "series_name": ["good_model", "good_model", "flat_model", "flat_model"],
            "mean_score": [0.2, 0.8, 0.4, 0.4],
            "empirical_rate": [0.1, 0.7, 0.2, 0.3],
            "count": [10, 10, 5, 5],
        }
    )

    slopes = reliability_slope_table(reliability)

    good = slopes.loc[slopes["model_name"].eq("good_model"), "reliability_slope"].iloc[0]
    flat = slopes.loc[slopes["model_name"].eq("flat_model"), "reliability_slope"].iloc[0]
    assert good == pytest.approx(1.0)
    assert pd.isna(flat)


def test_forecastability_atlas_attaches_reliability_slope_and_markdown() -> None:
    reliability = pd.DataFrame(
        {
            "series_name": ["good_model", "good_model"],
            "mean_score": [0.2, 0.8],
            "empirical_rate": [0.1, 0.7],
            "count": [10, 10],
        }
    )

    atlas = build_forecastability_atlas(_leaderboard_rows().head(1), reliability_df=reliability)
    text = forecastability_atlas_markdown(atlas)

    assert atlas.loc[0, "reliability_slope"] == pytest.approx(1.0)
    assert "forecastable_above_null" in text
    assert "paper_table_ready" in text


def test_citable_atlas_row_requires_gate_c_passed() -> None:
    rows = _leaderboard_rows().head(1).copy()
    rows["gate_c_status"] = "not_started"

    with pytest.raises(ValueError, match="gate_c_status='passed'"):
        build_forecastability_atlas(rows)


def test_make_forecastability_atlas_cli_writes_outputs(tmp_path) -> None:
    leaderboard_path = tmp_path / "leaderboard.csv"
    reliability_path = tmp_path / "reliability.csv"
    out_csv = tmp_path / "atlas.csv"
    out_md = tmp_path / "atlas.md"
    write_table(_leaderboard_rows(), leaderboard_path)
    write_table(
        pd.DataFrame(
            {
                "series_name": ["good_model", "good_model"],
                "mean_score": [0.2, 0.8],
                "empirical_rate": [0.1, 0.7],
                "count": [10, 10],
            }
        ),
        reliability_path,
    )

    result = subprocess.run(
        [
            sys.executable,
            "scripts/make_forecastability_atlas.py",
            "--leaderboard",
            str(leaderboard_path),
            "--reliability-table",
            str(reliability_path),
            "--out-csv",
            str(out_csv),
            "--out-md",
            str(out_md),
            "--min-events",
            "5",
            "--min-valid-prediction-rows",
            "100",
        ],
        check=True,
        text=True,
        capture_output=True,
    )

    atlas = read_table(out_csv)
    assert '"paper_table_ready_rows": 1' in result.stdout
    assert atlas.loc[atlas["model_name"].eq("good_model"), "paper_table_ready"].iloc[0]
    assert "unforecastable_null_overlap" in out_md.read_text(encoding="utf-8")
