from __future__ import annotations

import pandas as pd

from scripts.make_dataset_report import _events_coverable_by_predictions, _prediction_metadata_table


def test_events_coverable_by_predictions_uses_selected_horizon() -> None:
    base = pd.Timestamp("2026-01-01 00:00:00")
    preds = pd.DataFrame(
        {
            "patient_id": ["p1", "p1"],
            "recording_id": ["r1", "r1"],
            "window_start": [base, base + pd.Timedelta(hours=10)],
            "window_end": [base + pd.Timedelta(hours=1), base + pd.Timedelta(hours=11)],
            "risk_score": [0.1, 0.9],
            "alarm": [False, True],
            "is_excluded": [False, False],
        }
    )
    events = pd.DataFrame(
        {
            "patient_id": ["p1", "p1"],
            "recording_id": ["r1", "r1"],
            "seizure_start": [base + pd.Timedelta(hours=3), base + pd.Timedelta(days=2)],
            "seizure_end": [base + pd.Timedelta(hours=3, minutes=1), base + pd.Timedelta(days=2, minutes=1)],
        }
    )

    covered = _events_coverable_by_predictions(preds, events, sph_minutes=60, sop_minutes=180)

    assert len(covered) == 1
    assert covered.loc[0, "seizure_start"] == base + pd.Timedelta(hours=3)


def test_prediction_metadata_table_reports_fit_and_threshold_scope() -> None:
    predictions = pd.DataFrame(
        {
            "split": ["test", "test"],
            "alarm": [True, False],
            "is_excluded": [False, True],
            "score_fit_split": ["train", "train"],
            "threshold_source_split": ["val", "val"],
            "alarm_threshold": [0.4, 0.4],
        }
    )

    metadata = _prediction_metadata_table(predictions)

    assert metadata.loc[0, "prediction_rows"] == 2
    assert metadata.loc[0, "valid_prediction_rows"] == 1
    assert metadata.loc[0, "alarms"] == 1
    assert metadata.loc[0, "score_fit_split"] == "train"
    assert metadata.loc[0, "threshold_source_split"] == "val"
