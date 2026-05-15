from __future__ import annotations

import pandas as pd
import pytest

from src.datasets.schemas import (
    validate_events,
    validate_metadata,
    validate_modality_availability,
    validate_predictions,
    validate_recordings,
    validate_windows,
)


def test_event_schema_rejects_non_positive_seizure_interval() -> None:
    events = pd.DataFrame(
        {
            "patient_id": ["p1"],
            "recording_id": ["r1"],
            "seizure_start": [pd.Timestamp("2026-01-01 00:02:00")],
            "seizure_end": [pd.Timestamp("2026-01-01 00:01:00")],
        }
    )

    with pytest.raises(ValueError, match="non-positive"):
        validate_events(events)


def test_metadata_schema_rejects_missing_required_column() -> None:
    metadata = pd.DataFrame({"patient_id": ["p1"]})

    with pytest.raises(ValueError, match="missing required columns"):
        validate_metadata(metadata)


def test_prediction_schema_rejects_out_of_range_risk_score() -> None:
    preds = pd.DataFrame(
        {
            "patient_id": ["p1"],
            "recording_id": ["r1"],
            "window_start": [pd.Timestamp("2026-01-01")],
            "window_end": [pd.Timestamp("2026-01-01 00:01:00")],
            "risk_score": [1.2],
            "alarm": [True],
        }
    )

    with pytest.raises(ValueError, match="risk_score"):
        validate_predictions(preds)


def test_canonical_schema_accepts_minimal_valid_tables() -> None:
    metadata = pd.DataFrame({"patient_id": ["p1"], "recording_id": ["r1"]})
    recordings = pd.DataFrame(
        {
            "patient_id": ["p1"],
            "recording_id": ["r1"],
            "recording_start": [pd.Timestamp("2026-01-01")],
            "recording_end": [pd.Timestamp("2026-01-01 01:00:00")],
        }
    )
    windows = pd.DataFrame(
        {
            "patient_id": ["p1"],
            "recording_id": ["r1"],
            "window_start": [pd.Timestamp("2026-01-01")],
            "window_end": [pd.Timestamp("2026-01-01 00:01:00")],
        }
    )
    availability = pd.DataFrame(
        {
            "patient_id": ["p1"],
            "recording_id": ["r1"],
            "modality": ["hr"],
            "available": [True],
        }
    )

    validate_metadata(metadata)
    validate_recordings(recordings)
    validate_windows(windows)
    validate_modality_availability(availability)
