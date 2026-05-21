from __future__ import annotations

import json
import subprocess
import sys

import pandas as pd
import pytest

from src.reports.failure_taxonomy import (
    FailureTaxonomyConfig,
    build_failure_taxonomy_report,
    build_failure_taxonomy_rows,
)
from src.utils.io import read_table, write_table


def _predictions(include_observability: bool = True) -> pd.DataFrame:
    base = pd.Timestamp("2026-01-01 00:00:00")
    rows = [
        ("p1", 0.9, True, True, False, True, False),
        ("p1", 0.2, False, True, False, True, False),
        ("p1", 0.8, True, False, False, True, False),
        ("p1", 0.1, False, False, False, True, False),
        ("p2", 0.6, True, False, True, True, False),
        ("p2", 0.4, False, False, False, False, False),
        ("p2", 0.5, False, True, False, True, True),
    ]
    records = []
    for idx, (patient, risk, alarm, label, excluded, observable, abstain) in enumerate(rows):
        start = base + pd.Timedelta(hours=idx)
        record = {
            "patient_id": patient,
            "recording_id": f"{patient}_r1",
            "window_start": start,
            "window_end": start + pd.Timedelta(hours=1),
            "risk_score": risk,
            "alarm": alarm,
            "forecast_label": label,
            "is_excluded": excluded,
        }
        if include_observability:
            record["is_observable"] = observable
            record["abstain_for_observability"] = abstain
        records.append(record)
    return pd.DataFrame(records)


def test_failure_taxonomy_assigns_expected_categories() -> None:
    rows = build_failure_taxonomy_rows(_predictions())

    assert rows["failure_category"].tolist() == [
        "true_positive_alarm",
        "missed_low_risk_positive",
        "false_alarm_high_risk_negative",
        "true_negative",
        "excluded_alarm",
        "observability_deficient",
        "observability_abstained",
    ]
    assert rows["failure_taxonomy_status"].eq("post_hoc_descriptive_not_causal").all()
    assert rows.loc[1, "failure_severity"] > rows.loc[0, "failure_severity"]


def test_failure_taxonomy_report_summarizes_by_category_and_patient() -> None:
    report = build_failure_taxonomy_report(
        _predictions(),
        config=FailureTaxonomyConfig(high_risk_threshold=0.7, low_risk_threshold=0.3),
        model_name="toy_model",
    )

    assert report.metadata["model_name"] == "toy_model"
    assert report.metadata["n_failure_categories"] == 7
    assert set(report.patient_summary["patient_id"]) == {"p1", "p2"}
    assert "observability_abstained" in report.summary["failure_category"].tolist()
    assert report.warnings.empty


def test_failure_taxonomy_warns_when_observability_columns_missing() -> None:
    report = build_failure_taxonomy_report(_predictions(include_observability=False))

    assert set(report.warnings["warning_code"]) == {
        "observability_not_available",
        "observability_abstention_not_available",
    }


def test_failure_taxonomy_rejects_bad_thresholds() -> None:
    with pytest.raises(ValueError, match="risk thresholds"):
        build_failure_taxonomy_rows(
            _predictions(),
            config=FailureTaxonomyConfig(low_risk_threshold=0.8, high_risk_threshold=0.3),
        )


def test_make_failure_taxonomy_report_cli_writes_outputs(tmp_path) -> None:
    predictions_path = tmp_path / "predictions.csv"
    out_dir = tmp_path / "failure"
    write_table(_predictions(), predictions_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/make_failure_taxonomy_report.py",
            "--predictions",
            str(predictions_path),
            "--out-dir",
            str(out_dir),
            "--model-name",
            "toy_model",
        ],
        check=True,
        text=True,
        capture_output=True,
    )

    assert '"model_name": "toy_model"' in result.stdout
    rows = read_table(out_dir / "failure_taxonomy_rows.csv")
    summary = read_table(out_dir / "failure_taxonomy_summary.csv")
    patient_summary = read_table(out_dir / "failure_taxonomy_patient_summary.csv")
    manifest = read_table(out_dir / "failure_taxonomy_manifest.csv")
    payload = json.loads((out_dir / "failure_taxonomy_report.json").read_text(encoding="utf-8"))
    assert "missed_low_risk_positive" in rows["failure_category"].tolist()
    assert "excluded_alarm" in summary["failure_category"].tolist()
    assert set(patient_summary["patient_id"]) == {"p1", "p2"}
    assert manifest.loc[0, "model_name"] == "toy_model"
    assert payload["metadata"]["taxonomy_status"] == "post_hoc_descriptive_not_causal"
    assert "not citable" in (out_dir / "failure_taxonomy_report.md").read_text(encoding="utf-8")
