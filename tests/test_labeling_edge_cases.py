from __future__ import annotations

import pandas as pd

from src.labeling.sph_sop import label_forecast_windows


def _events(rows: list[dict]) -> pd.DataFrame:
    return pd.DataFrame(
        rows,
        columns=["patient_id", "recording_id", "seizure_start", "seizure_end"],
    )


def test_no_seizure_patient_has_negative_unexcluded_labels():
    windows = pd.DataFrame(
        {
            "patient_id": ["p1"],
            "recording_id": ["r1"],
            "window_start": [pd.Timestamp("2026-01-01 00:00:00")],
            "window_end": [pd.Timestamp("2026-01-01 00:01:00")],
        }
    )
    events = _events([])

    labeled = label_forecast_windows(windows, events, 5, 30)

    assert not labeled["forecast_label"].any()
    assert not labeled["is_excluded"].any()
    assert pd.isna(labeled.loc[0, "time_to_next_seizure_seconds"])


def test_recording_scope_prevents_cross_recording_event_labeling():
    windows = pd.DataFrame(
        {
            "patient_id": ["p1"],
            "recording_id": ["r1"],
            "window_start": [pd.Timestamp("2026-01-01 00:00:00")],
            "window_end": [pd.Timestamp("2026-01-01 00:10:00")],
        }
    )
    events = _events(
        [
            {
                "patient_id": "p1",
                "recording_id": "r2",
                "seizure_start": pd.Timestamp("2026-01-01 00:20:00"),
                "seizure_end": pd.Timestamp("2026-01-01 00:21:00"),
            }
        ]
    )

    labeled = label_forecast_windows(windows, events, 5, 30)

    assert not labeled.loc[0, "forecast_label"]


def test_multiple_seizures_use_next_event_and_any_forecast_event():
    base = pd.Timestamp("2026-01-01 00:00:00")
    windows = pd.DataFrame(
        {
            "patient_id": ["p1", "p1"],
            "recording_id": ["r1", "r1"],
            "window_start": [base, base + pd.Timedelta(minutes=45)],
            "window_end": [base + pd.Timedelta(minutes=1), base + pd.Timedelta(minutes=46)],
        }
    )
    events = _events(
        [
            {
                "patient_id": "p1",
                "recording_id": "r1",
                "seizure_start": base + pd.Timedelta(minutes=10),
                "seizure_end": base + pd.Timedelta(minutes=12),
            },
            {
                "patient_id": "p1",
                "recording_id": "r1",
                "seizure_start": base + pd.Timedelta(minutes=60),
                "seizure_end": base + pd.Timedelta(minutes=62),
            },
        ]
    )

    labeled = label_forecast_windows(windows, events, 5, 30, postictal_exclusion_minutes=5)

    assert labeled.loc[0, "time_to_next_seizure_seconds"] == 9 * 60
    assert labeled["forecast_label"].tolist() == [True, True]


def test_postictal_preictal_overlap_remains_excluded():
    base = pd.Timestamp("2026-01-01 00:00:00")
    windows = pd.DataFrame(
        {
            "patient_id": ["p1"],
            "recording_id": ["r1"],
            "window_start": [base + pd.Timedelta(minutes=13)],
            "window_end": [base + pd.Timedelta(minutes=14)],
        }
    )
    events = _events(
        [
            {
                "patient_id": "p1",
                "recording_id": "r1",
                "seizure_start": base + pd.Timedelta(minutes=10),
                "seizure_end": base + pd.Timedelta(minutes=12),
            },
            {
                "patient_id": "p1",
                "recording_id": "r1",
                "seizure_start": base + pd.Timedelta(minutes=20),
                "seizure_end": base + pd.Timedelta(minutes=21),
            },
        ]
    )

    labeled = label_forecast_windows(windows, events, 5, 30, postictal_exclusion_minutes=10)

    assert labeled.loc[0, "forecast_label"]
    assert labeled.loc[0, "is_postictal"]
    assert labeled.loc[0, "is_excluded"]


def test_right_censored_forecast_horizon_is_excluded():
    base = pd.Timestamp("2026-01-01 00:00:00")
    windows = pd.DataFrame(
        {
            "patient_id": ["p1", "p1"],
            "recording_id": ["r1", "r1"],
            "recording_end": [base + pd.Timedelta(minutes=40), base + pd.Timedelta(minutes=40)],
            "window_start": [base, base + pd.Timedelta(minutes=20)],
            "window_end": [base + pd.Timedelta(minutes=1), base + pd.Timedelta(minutes=21)],
        }
    )
    events = _events([])

    labeled = label_forecast_windows(windows, events, sph_minutes=5, sop_minutes=30)

    assert labeled["is_right_censored"].tolist() == [False, True]
    assert labeled["is_excluded"].tolist() == [False, True]


def test_require_recording_end_for_right_censoring_fails_loudly():
    windows = pd.DataFrame(
        {
            "patient_id": ["p1"],
            "recording_id": ["r1"],
            "window_start": [pd.Timestamp("2026-01-01 00:00:00")],
            "window_end": [pd.Timestamp("2026-01-01 00:01:00")],
        }
    )
    events = _events([])

    try:
        label_forecast_windows(windows, events, 5, 30, require_recording_end=True)
    except ValueError as exc:
        assert "recording_end" in str(exc)
    else:
        raise AssertionError("expected missing recording_end to fail")
