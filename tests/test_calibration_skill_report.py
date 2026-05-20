from __future__ import annotations

import json
import subprocess
import sys

import pandas as pd
import pytest

from src.reports.calibration_skill import (
    align_reference_predictions,
    build_calibration_skill_report,
)
from src.utils.io import read_table, write_table


def _base_predictions() -> pd.DataFrame:
    base = pd.Timestamp("2026-01-01 00:00:00")
    labels = [True, False, True, False, False, True, False, True]
    risks = [0.9, 0.1, 0.8, 0.2, 0.2, 0.7, 0.3, 0.8]
    rows = []
    for idx, (label, risk) in enumerate(zip(labels, risks, strict=True)):
        patient = "p1" if idx < 4 else "p2"
        start = base + pd.Timedelta(hours=idx)
        rows.append(
            {
                "patient_id": patient,
                "recording_id": f"{patient}_r1",
                "event_id": f"e{idx // 2}",
                "split": "test",
                "window_start": start,
                "window_end": start + pd.Timedelta(hours=1),
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


def test_brier_skill_score_against_self_is_zero() -> None:
    predictions = _base_predictions()

    report = build_calibration_skill_report(
        predictions,
        {"self": predictions.copy()},
        model_name="toy_model",
        n_bootstrap=20,
    )

    bss = report.skill.loc[report.skill["reference_name"].eq("self"), "brier_skill_score"].iloc[0]
    assert bss == pytest.approx(0.0)
    assert {"patient", "event"} == set(report.bootstrap["scope"])


def test_deliberately_uninformative_model_is_not_better_than_null() -> None:
    predictions = _base_predictions()
    random_model = predictions.copy()
    random_model["risk_score"] = [0.9, 0.9, 0.1, 0.1, 0.8, 0.2, 0.7, 0.3]
    reference = _constant_reference(predictions, risk=0.5)

    report = build_calibration_skill_report(
        random_model,
        {"split_prevalence_prior": reference},
        model_name="bad_random_model",
        n_bootstrap=20,
    )

    assert report.skill.loc[0, "brier_skill_score"] <= 0


def test_reference_row_mismatch_raises_explicit_error() -> None:
    predictions = _base_predictions()
    reference = _constant_reference(predictions).iloc[:-1]

    with pytest.raises(ValueError, match="row mismatch"):
        align_reference_predictions(
            predictions,
            reference,
            reference_name="split_prevalence_prior",
        )


def test_reference_label_mismatch_raises_explicit_error() -> None:
    predictions = _base_predictions()
    reference = _constant_reference(predictions)
    reference.loc[0, "forecast_label"] = False

    with pytest.raises(ValueError, match="forecast_label"):
        align_reference_predictions(
            predictions,
            reference,
            reference_name="split_prevalence_prior",
        )


def test_missing_event_column_raises_when_event_bootstrap_requested() -> None:
    predictions = _base_predictions().drop(columns=["event_id"])
    reference = _constant_reference(predictions)

    with pytest.raises(ValueError, match="event bootstrap requested"):
        build_calibration_skill_report(
            predictions,
            {"split_prevalence_prior": reference},
            model_name="toy_model",
            n_bootstrap=20,
        )


def test_citable_report_requires_gate_c_passed() -> None:
    predictions = _base_predictions()

    with pytest.raises(ValueError, match="gate_c_status='passed'"):
        build_calibration_skill_report(
            predictions,
            {"split_prevalence_prior": _constant_reference(predictions)},
            model_name="toy_model",
            n_bootstrap=20,
            citation_status="citable_after_gate_c",
            gate_c_status="not_started",
        )


def test_make_calibration_report_cli_writes_outputs(tmp_path) -> None:
    predictions = _base_predictions()
    reference = _constant_reference(predictions)
    predictions_path = tmp_path / "predictions.csv"
    reference_path = tmp_path / "split_prevalence_prior.csv"
    out_dir = tmp_path / "calibration"
    write_table(predictions, predictions_path)
    write_table(reference, reference_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/make_calibration_report.py",
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
            "20",
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
    skill = read_table(out_dir / "calibration_skill.csv")
    assert skill.loc[0, "reference_name"] == "split_prevalence_prior"
    assert skill.loc[0, "brier_skill_score"] > 0
    bootstrap = read_table(out_dir / "calibration_bootstrap.csv")
    assert {"patient", "event"} == set(bootstrap["scope"])
    payload = json.loads((out_dir / "calibration_report.json").read_text(encoding="utf-8"))
    assert payload["metadata"]["citation_status"] == "synthetic_not_citable"
    assert "not citable" in (out_dir / "calibration_report.md").read_text(encoding="utf-8")
