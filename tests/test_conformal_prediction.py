from __future__ import annotations

import json
import subprocess
import sys

import pandas as pd
import pytest

from src.calibration.conformal import (
    apply_conformal_intervals,
    build_conformal_report,
    conformal_coverage_summary,
    fit_split_conformal,
    split_conformal_radius,
)
from src.utils.io import read_table, write_table


def _toy_predictions() -> pd.DataFrame:
    rows = []
    base = pd.Timestamp("2026-01-01")
    for split in ["val", "test"]:
        for patient in ["p1", "p2"]:
            for idx in range(6):
                label = idx % 2 == 0
                if patient == "p1":
                    risk = 0.85 if label else 0.15
                else:
                    risk = 0.65 if label else 0.35
                rows.append(
                    {
                        "patient_id": patient,
                        "recording_id": f"{patient}_r1",
                        "window_start": base + pd.Timedelta(hours=len(rows)),
                        "window_end": base + pd.Timedelta(hours=len(rows) + 1),
                        "split": split,
                        "forecast_label": label,
                        "is_excluded": False,
                        "risk_score": risk,
                    }
                )
    return pd.DataFrame(rows)


def test_split_conformal_radius_uses_finite_sample_quantile() -> None:
    calibration = pd.DataFrame(
        {
            "risk_score": [0.9, 0.8, 0.3, 0.1],
            "forecast_label": [True, True, False, False],
            "is_excluded": [False, False, False, False],
        }
    )

    radius = split_conformal_radius(calibration, alpha=0.25)

    assert radius == pytest.approx(0.3)


def test_global_conformal_intervals_cover_synthetic_labels() -> None:
    predictions = _toy_predictions()
    calibration = predictions.loc[predictions["split"].eq("val")]
    evaluation = predictions.loc[predictions["split"].eq("test")]

    report = build_conformal_report(
        calibration,
        evaluation,
        alpha=0.1,
        method="global",
        result_status="synthetic_smoke_test_not_citable",
        citation_status="synthetic_not_citable",
    )

    assert report.summary.loc[0, "empirical_coverage"] >= 0.9
    assert report.metadata["citation_status"] == "synthetic_not_citable"
    assert {"risk_lower", "risk_upper", "conformal_radius"}.issubset(report.intervals.columns)


def test_patient_conformal_marks_global_fallback() -> None:
    predictions = _toy_predictions()
    calibration = predictions.loc[
        predictions["split"].eq("val") & predictions["patient_id"].eq("p1")
    ]
    evaluation = predictions.loc[predictions["split"].eq("test")]

    fitted = fit_split_conformal(
        calibration,
        alpha=0.1,
        method="patient",
        min_patient_calibration=3,
    )
    intervals = apply_conformal_intervals(evaluation, fitted)

    variants = intervals.groupby("patient_id")["conformal_variant"].unique().to_dict()
    assert variants["p1"].tolist() == ["patient_calibrated"]
    assert variants["p2"].tolist() == ["global_fallback"]
    assert intervals.loc[intervals["patient_id"].eq("p2"), "conformal_calibration_n"].eq(0).all()


def test_conformal_coverage_summary_excludes_excluded_rows() -> None:
    intervals = pd.DataFrame(
        {
            "risk_lower": [0.0, 0.8, 0.0],
            "risk_upper": [0.2, 1.0, 0.2],
            "conformal_interval_width": [0.2, 0.2, 0.2],
            "forecast_label": [False, True, True],
            "is_excluded": [False, False, True],
        }
    )

    summary = conformal_coverage_summary(intervals)

    assert summary.loc[0, "rows"] == 2
    assert summary.loc[0, "empirical_coverage"] == pytest.approx(1.0)


def test_citable_conformal_report_requires_gate_c_passed() -> None:
    predictions = _toy_predictions()

    with pytest.raises(ValueError, match="gate_c_status='passed'"):
        build_conformal_report(
            predictions.loc[predictions["split"].eq("val")],
            predictions.loc[predictions["split"].eq("test")],
            citation_status="citable_after_gate_c",
            gate_c_status="not_started",
        )


def test_run_conformal_calibration_cli_writes_outputs(tmp_path) -> None:
    predictions = _toy_predictions()
    predictions_path = tmp_path / "predictions.csv"
    out_dir = tmp_path / "conformal"
    write_table(predictions, predictions_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_conformal_calibration.py",
            "--predictions",
            str(predictions_path),
            "--out-dir",
            str(out_dir),
            "--calibration-filter",
            "split=val",
            "--evaluation-filter",
            "split=test",
            "--method",
            "patient",
            "--min-patient-calibration",
            "3",
            "--result-status",
            "synthetic_smoke_test_not_citable",
            "--citation-status",
            "synthetic_not_citable",
        ],
        check=True,
        text=True,
        capture_output=True,
    )

    assert '"method": "patient"' in result.stdout
    intervals = read_table(out_dir / "conformal_intervals.csv")
    summary = read_table(out_dir / "conformal_summary.csv")
    patient_summary = read_table(out_dir / "conformal_patient_summary.csv")
    assert {"risk_lower", "risk_upper", "conformal_variant"}.issubset(intervals.columns)
    assert summary.loc[0, "empirical_coverage"] >= 0.9
    assert set(patient_summary["patient_id"]) == {"p1", "p2"}
    payload = json.loads((out_dir / "conformal_report.json").read_text(encoding="utf-8"))
    assert payload["metadata"]["citation_status"] == "synthetic_not_citable"
    assert "not citable" in (out_dir / "conformal_report.md").read_text(encoding="utf-8")
