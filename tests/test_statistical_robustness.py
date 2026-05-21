from __future__ import annotations

import json
import subprocess
import sys

import pandas as pd
import pytest

from src.reports.statistical_robustness import (
    adjust_p_values,
    bootstrap_brier_skill_score_intervals,
    build_statistical_robustness_report,
    paired_brier_permutation_test,
)
from src.utils.io import read_table, write_table


def _strong_predictions(patient_count: int = 8, windows_per_patient: int = 6) -> pd.DataFrame:
    base = pd.Timestamp("2026-01-01 00:00:00")
    rows = []
    for patient_idx in range(patient_count):
        patient = f"p{patient_idx + 1}"
        for window_idx in range(windows_per_patient):
            row_idx = len(rows)
            label = window_idx % 2 == 0
            risk = 0.9 if label else 0.1
            start = base + pd.Timedelta(hours=row_idx)
            rows.append(
                {
                    "patient_id": patient,
                    "recording_id": f"{patient}_r1",
                    "event_id": f"{patient}_e{window_idx // 2}",
                    "split": "test",
                    "window_start": start.isoformat(),
                    "window_end": (start + pd.Timedelta(hours=1)).isoformat(),
                    "forecast_label": label,
                    "is_excluded": False,
                    "risk_score": risk,
                    "alarm": risk >= 0.5,
                }
            )
    return pd.DataFrame(rows)


def _constant_reference(predictions: pd.DataFrame, risk: float = 0.5) -> pd.DataFrame:
    reference = predictions.copy()
    reference["risk_score"] = risk
    reference["alarm"] = False
    return reference


def test_bootstrap_intervals_and_permutation_detect_known_effect() -> None:
    predictions = _strong_predictions()
    reference = _constant_reference(predictions)
    references = {"split_prevalence_prior": reference}

    intervals = bootstrap_brier_skill_score_intervals(
        predictions,
        references,
        scope="patient",
        group_col="patient_id",
        n_bootstrap=50,
        seed=7,
    )
    permutation = paired_brier_permutation_test(
        predictions,
        reference,
        reference_name="split_prevalence_prior",
        n_permutations=500,
        seed=7,
    )

    assert intervals.loc[0, "ci_low"] > 0.8
    assert permutation["observed_mean_delta"] > 0
    assert permutation["observed_brier_skill_score"] > 0.8
    assert permutation["p_value"] < 0.05
    assert permutation["permutation_unit"] == "patient_id"


def test_adjust_p_values_benjamini_hochberg_known_values() -> None:
    results = pd.DataFrame({"reference_name": ["a", "b", "c"], "p_value": [0.01, 0.02, 0.2]})

    adjusted = adjust_p_values(results, method="benjamini_hochberg")

    assert adjusted["p_value_adjusted"].tolist() == pytest.approx([0.03, 0.03, 0.2])
    assert adjusted["reject_adjusted_alpha"].tolist() == [True, True, False]


def test_report_marks_tiny_group_warning() -> None:
    predictions = _strong_predictions(patient_count=2, windows_per_patient=4)

    report = build_statistical_robustness_report(
        predictions,
        {"split_prevalence_prior": _constant_reference(predictions)},
        model_name="toy_model",
        n_bootstrap=30,
        n_permutations=30,
        min_groups=5,
        event_col=None,
        result_status="synthetic_smoke_test_not_citable",
        citation_status="synthetic_not_citable",
    )

    assert "tiny_n_groups" in report.warnings["warning_code"].tolist()
    assert report.metadata["citation_status"] == "synthetic_not_citable"


def test_citable_robustness_report_requires_gate_c_passed() -> None:
    predictions = _strong_predictions()

    with pytest.raises(ValueError, match="gate_c_status='passed'"):
        build_statistical_robustness_report(
            predictions,
            {"split_prevalence_prior": _constant_reference(predictions)},
            model_name="toy_model",
            n_bootstrap=10,
            n_permutations=10,
            citation_status="citable_after_gate_c",
            gate_c_status="not_started",
        )


def test_make_statistical_robustness_cli_writes_outputs(tmp_path) -> None:
    predictions = _strong_predictions()
    reference = _constant_reference(predictions)
    predictions_path = tmp_path / "predictions.csv"
    reference_path = tmp_path / "split_prevalence_prior.csv"
    out_dir = tmp_path / "robustness"
    write_table(predictions, predictions_path)
    write_table(reference, reference_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/make_statistical_robustness_report.py",
            "--predictions",
            str(predictions_path),
            "--reference-predictions",
            f"split_prevalence_prior={reference_path}",
            "--out-dir",
            str(out_dir),
            "--model-name",
            "toy_model",
            "--prediction-filter",
            "split=test",
            "--bootstrap-samples",
            "30",
            "--permutations",
            "100",
            "--result-status",
            "synthetic_smoke_test_not_citable",
            "--citation-status",
            "synthetic_not_citable",
        ],
        check=True,
        text=True,
        capture_output=True,
    )

    assert '"model_name": "toy_model"' in result.stdout
    intervals = read_table(out_dir / "robustness_intervals.csv")
    permutation = read_table(out_dir / "robustness_permutation.csv")
    multiplicity = read_table(out_dir / "robustness_multiplicity.csv")
    assert {"patient", "event"} == set(intervals["scope"])
    assert permutation.loc[0, "observed_mean_delta"] > 0
    assert multiplicity.loc[0, "p_value_adjusted"] <= 0.1
    payload = json.loads((out_dir / "robustness_report.json").read_text(encoding="utf-8"))
    assert payload["metadata"]["citation_status"] == "synthetic_not_citable"
    assert "not citable" in (out_dir / "robustness_report.md").read_text(encoding="utf-8")
