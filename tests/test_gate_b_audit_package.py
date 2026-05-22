from __future__ import annotations

import json
import subprocess
import sys

import pandas as pd

from src.reports.gate_b_audit_package import build_gate_b_audit_package
from src.reports.label_audit import REVIEW_DECISION_COLUMNS
from src.utils.io import read_table, write_table


def _synthetic_audit_inputs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rows = []
    prediction_rows = []
    reference_rows = []
    starts = [
        pd.Timestamp("2026-01-01 01:00:00"),
        pd.Timestamp("2026-01-02 01:00:00"),
        pd.Timestamp("2026-01-03 01:00:00"),
    ]
    patients = ["p1", "p2", "p3"]
    risks = {
        0: [0.05, 0.05, 0.05, 0.05],
        1: [0.49, 0.52, 0.50, 0.51],
        2: [0.90, 0.92, 0.91, 0.93],
    }
    reference_risks = {
        0: [0.05, 0.05, 0.05, 0.05],
        1: [0.04, 0.05, 0.04, 0.05],
        2: [0.85, 0.86, 0.85, 0.86],
    }
    for event_index, seizure_start in enumerate(starts):
        for offset, minutes_to_seizure in enumerate([45, 20, 5, -5]):
            window_end = seizure_start - pd.Timedelta(minutes=minutes_to_seizure)
            window_start = window_end - pd.Timedelta(minutes=5)
            row = {
                "event_index": event_index,
                "patient_id": patients[event_index],
                "recording_id": f"rec_{event_index}",
                "seizure_start": seizure_start,
                "seizure_end": seizure_start + pd.Timedelta(minutes=1),
                "window_start": window_start,
                "window_end": window_end,
                "minutes_to_seizure": minutes_to_seizure,
                "forecast_label": event_index == 1 and offset in {1, 2},
                "is_ictal": minutes_to_seizure < 0,
                "is_postictal": event_index == 1 and minutes_to_seizure < 0,
                "is_right_censored": event_index == 1 and offset == 2,
                "is_excluded": minutes_to_seizure < 0 and event_index != 1,
            }
            rows.append(row)
            prediction_rows.append(
                {
                    "patient_id": row["patient_id"],
                    "recording_id": row["recording_id"],
                    "window_start": window_start,
                    "window_end": window_end,
                    "forecast_label": row["forecast_label"],
                    "is_excluded": row["is_excluded"],
                    "risk_score": risks[event_index][offset],
                    "alarm": event_index == 1 and offset in {1, 2},
                }
            )
            reference_rows.append(
                {
                    "patient_id": row["patient_id"],
                    "recording_id": row["recording_id"],
                    "window_start": window_start,
                    "window_end": window_end,
                    "forecast_label": row["forecast_label"],
                    "is_excluded": row["is_excluded"],
                    "risk_score": reference_risks[event_index][offset],
                    "alarm": False,
                }
            )
    return pd.DataFrame(rows), pd.DataFrame(prediction_rows), pd.DataFrame(reference_rows)


def test_gate_b_audit_package_marks_pending_human_review() -> None:
    audit, predictions, reference = _synthetic_audit_inputs()

    package = build_gate_b_audit_package(
        audit,
        dataset="synthetic",
        predictions_df=predictions,
        reference_predictions={"split_prior": reference},
        budget=2,
        selection_strategy="top_score",
        min_events_required=2,
        audit_source="audit.csv",
        prediction_source="predictions.csv",
    )

    assert package.manifest["package_status"] == "pending_human_review_not_gate_b_pass"
    assert package.manifest["gate_b_status"] == "not_passed_pending_human_review"
    assert package.manifest["selected_events"] == 2
    assert package.manifest["minimum_event_budget_met"] is True
    assert set(REVIEW_DECISION_COLUMNS).issubset(package.review_sheet.columns)
    assert package.review_sheet.loc[0, "decision"] == ""
    assert "pending human review" in package.markdown
    assert "check_label_audit_review.py" in package.markdown
    assert "not a Gate B pass" in package.markdown


def test_gate_b_audit_package_records_under_budget_status() -> None:
    audit, predictions, _ = _synthetic_audit_inputs()

    package = build_gate_b_audit_package(
        audit,
        dataset="synthetic",
        predictions_df=predictions,
        budget=1,
        min_events_required=5,
    )

    assert package.manifest["selected_events"] == 1
    assert package.manifest["minimum_event_budget_met"] is False
    assert package.manifest["selected_unique_patients"] == 1


def test_build_gate_b_audit_package_cli_writes_outputs(tmp_path) -> None:
    audit, predictions, reference = _synthetic_audit_inputs()
    audit_path = tmp_path / "audit.csv"
    predictions_path = tmp_path / "predictions.csv"
    reference_path = tmp_path / "reference.csv"
    out_dir = tmp_path / "gate_b_package"
    write_table(audit, audit_path)
    write_table(predictions, predictions_path)
    write_table(reference, reference_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/build_gate_b_audit_package.py",
            "--audit",
            str(audit_path),
            "--predictions",
            str(predictions_path),
            "--reference-predictions",
            f"split_prior={reference_path}",
            "--dataset",
            "synthetic",
            "--budget",
            "2",
            "--selection-strategy",
            "top_score",
            "--out-dir",
            str(out_dir),
        ],
        check=True,
        text=True,
        capture_output=True,
    )

    stdout = json.loads(result.stdout)
    review = read_table(out_dir / "gate_b_audit_review_sheet.csv")
    candidates = read_table(out_dir / "gate_b_audit_candidates.csv")
    manifest = json.loads((out_dir / "gate_b_audit_manifest.json").read_text(encoding="utf-8"))
    markdown = (out_dir / "gate_b_audit_package.md").read_text(encoding="utf-8")
    assert stdout["selected_events"] == 2
    assert len(review) == 2
    assert len(candidates) == 3
    assert manifest["reference_prediction_names"] == ["split_prior"]
    assert "Gate C remains blocked" in markdown
