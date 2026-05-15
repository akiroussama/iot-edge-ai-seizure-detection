from __future__ import annotations

import pandas as pd

from src.datasets.seizeit2_loader import make_synthetic_seizeit2_tables
from src.labeling.sph_sop import label_forecast_windows
from src.metrics.alarm_metrics import (
    false_alarm_count,
    false_alarm_rate_per_day,
    monitored_time_seconds,
    time_in_warning,
)


def test_time_in_warning_fraction():
    _, windows, events = make_synthetic_seizeit2_tables()
    preds = label_forecast_windows(windows, events, 5, 30, postictal_exclusion_minutes=5)
    preds["risk_score"] = 0.0
    preds["alarm"] = False
    valid = preds.loc[~preds["is_excluded"]]
    alarm_idx = valid.head(5).index
    preds.loc[alarm_idx, "alarm"] = True
    assert abs(time_in_warning(preds) - 5 / len(valid)) < 1e-9


def test_false_alarm_rate_counts_non_associated_episode():
    _, windows, events = make_synthetic_seizeit2_tables()
    preds = label_forecast_windows(windows, events, 5, 30, postictal_exclusion_minutes=5)
    preds["risk_score"] = 0.0
    preds["alarm"] = False
    # Very early alarm not associated with seizure at 10:40 for SPH 5/SOP 30.
    preds.loc[preds["window_end"].eq(pd.Timestamp("2026-01-01 10:02:00")), "alarm"] = True
    assert false_alarm_count(preds, events, 5, 30) == 1
    assert false_alarm_rate_per_day(preds, events, 5, 30) > 0


def test_monitored_time_sums_simultaneous_patients():
    preds = pd.DataFrame(
        {
            "patient_id": ["p1", "p2"],
            "recording_id": ["r1", "r2"],
            "window_start": [pd.Timestamp("2026-01-01 00:00:00")] * 2,
            "window_end": [pd.Timestamp("2026-01-01 01:00:00")] * 2,
            "alarm": [True, False],
            "is_excluded": [False, False],
        }
    )

    assert monitored_time_seconds(preds) == 2 * 3600
    assert time_in_warning(preds) == 0.5


def test_false_alarm_episodes_are_separate_by_recording():
    preds = pd.DataFrame(
        {
            "patient_id": ["p1", "p1"],
            "recording_id": ["r1", "r2"],
            "window_start": [
                pd.Timestamp("2026-01-01 00:00:00"),
                pd.Timestamp("2026-01-01 00:00:00"),
            ],
            "window_end": [
                pd.Timestamp("2026-01-01 00:10:00"),
                pd.Timestamp("2026-01-01 00:10:00"),
            ],
            "alarm": [True, True],
            "is_excluded": [False, False],
        }
    )
    events = pd.DataFrame(columns=["patient_id", "recording_id", "seizure_start", "seizure_end"])

    assert false_alarm_count(preds, events, 5, 30) == 2


def test_false_alarm_episodes_use_valid_window_stride_not_alarm_stride():
    starts = pd.date_range("2026-01-01 00:00:00", periods=5, freq="10min")
    preds = pd.DataFrame(
        {
            "patient_id": ["p1"] * 5,
            "recording_id": ["r1"] * 5,
            "window_start": starts,
            "window_end": starts + pd.Timedelta(minutes=10),
            "alarm": [True, False, False, True, False],
            "is_excluded": [False] * 5,
        }
    )
    events = pd.DataFrame(columns=["patient_id", "recording_id", "seizure_start", "seizure_end"])

    assert false_alarm_count(preds, events, 5, 30) == 2


def test_time_in_warning_merges_overlapping_alarm_windows():
    preds = pd.DataFrame(
        {
            "patient_id": ["p1", "p1", "p1"],
            "recording_id": ["r1", "r1", "r1"],
            "window_start": [
                pd.Timestamp("2026-01-01 00:00:00"),
                pd.Timestamp("2026-01-01 00:05:00"),
                pd.Timestamp("2026-01-01 00:15:00"),
            ],
            "window_end": [
                pd.Timestamp("2026-01-01 00:10:00"),
                pd.Timestamp("2026-01-01 00:15:00"),
                pd.Timestamp("2026-01-01 00:25:00"),
            ],
            "alarm": [True, True, False],
            "is_excluded": [False, False, False],
        }
    )

    assert monitored_time_seconds(preds) == 25 * 60
    assert time_in_warning(preds) == (15 * 60) / (25 * 60)
