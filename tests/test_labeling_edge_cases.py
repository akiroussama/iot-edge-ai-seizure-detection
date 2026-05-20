from __future__ import annotations

import subprocess
import sys

import pandas as pd

from src.labeling.sph_sop import label_forecast_windows
from src.utils.io import write_table


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

    labeled = label_forecast_windows(windows, events, 5, 30, require_recording_end=False)

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

    labeled = label_forecast_windows(windows, events, 5, 30, require_recording_end=False)

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

    labeled = label_forecast_windows(
        windows, events, 5, 30, postictal_exclusion_minutes=5, require_recording_end=False
    )

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

    labeled = label_forecast_windows(
        windows, events, 5, 30, postictal_exclusion_minutes=10, require_recording_end=False
    )

    assert labeled.loc[0, "forecast_label"]
    assert labeled.loc[0, "is_postictal"]
    assert labeled.loc[0, "is_excluded"]


def test_postictal_anchor_can_use_onset_for_onset_only_events():
    base = pd.Timestamp("2026-01-01 00:00:00")
    windows = pd.DataFrame(
        {
            "patient_id": ["p1"],
            "recording_id": ["r1"],
            "window_start": [base + pd.Timedelta(minutes=11, seconds=15)],
            "window_end": [base + pd.Timedelta(minutes=11, seconds=45)],
        }
    )
    events = _events(
        [
            {
                "patient_id": "p1",
                "recording_id": "r1",
                "seizure_start": base + pd.Timedelta(minutes=10),
                "seizure_end": base + pd.Timedelta(minutes=11),
            }
        ]
    )

    end_anchor = label_forecast_windows(
        windows, events, 5, 30, postictal_exclusion_minutes=1, require_recording_end=False
    )
    start_anchor = label_forecast_windows(
        windows,
        events,
        5,
        30,
        postictal_exclusion_minutes=1,
        postictal_anchor="seizure_start",
        require_recording_end=False,
    )

    assert end_anchor.loc[0, "is_postictal"]
    assert not start_anchor.loc[0, "is_postictal"]


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


def test_right_censored_confirmed_positive_is_not_excluded():
    base = pd.Timestamp("2026-01-01 00:00:00")
    windows = pd.DataFrame(
        {
            "patient_id": ["p1"],
            "recording_id": ["r1"],
            "recording_end": [base + pd.Timedelta(minutes=20)],
            "window_start": [base],
            "window_end": [base + pd.Timedelta(minutes=1)],
        }
    )
    events = _events(
        [
            {
                "patient_id": "p1",
                "recording_id": "r1",
                "seizure_start": base + pd.Timedelta(minutes=10),
                "seizure_end": base + pd.Timedelta(minutes=11),
            }
        ]
    )

    labeled = label_forecast_windows(windows, events, sph_minutes=5, sop_minutes=30)

    assert labeled.loc[0, "forecast_label"]
    assert labeled.loc[0, "is_right_censored"]
    assert not labeled.loc[0, "is_excluded"]


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
        # require_recording_end defaults to True (Phase R audit C2 item 7), so a
        # windows table with no recording_end must fail loudly with no override.
        label_forecast_windows(windows, events, 5, 30)
    except ValueError as exc:
        assert "recording_end" in str(exc)
    else:
        raise AssertionError("expected missing recording_end to fail")


def test_label_windows_cli_refuses_imputed_end_postictal_without_policy(tmp_path):
    base = pd.Timestamp("2026-01-01 00:00:00")
    windows = pd.DataFrame(
        {
            "patient_id": ["p1"],
            "recording_id": ["r1"],
            "recording_end": [base + pd.Timedelta(hours=2)],
            "window_start": [base],
            "window_end": [base + pd.Timedelta(minutes=1)],
        }
    )
    events = pd.DataFrame(
        {
            "patient_id": ["p1"],
            "recording_id": ["r1"],
            "seizure_start": [base + pd.Timedelta(minutes=30)],
            "seizure_end": [base + pd.Timedelta(minutes=31)],
            "seizure_end_imputed": [True],
        }
    )
    windows_path = tmp_path / "windows.parquet"
    events_path = tmp_path / "events.parquet"
    out_path = tmp_path / "labels.parquet"
    write_table(windows, windows_path)
    write_table(events, events_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/label_windows.py",
            "--windows",
            str(windows_path),
            "--events",
            str(events_path),
            "--output",
            str(out_path),
            "--postictal-exclusion-minutes",
            "60",
        ],
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode != 0
    assert "imputed seizure_end" in result.stderr


def test_right_censoring_applied_column_stamps_whether_censoring_ran():
    """Phase R audit C2: labels carry a right_censoring_applied stamp so a
    downstream report cannot mistake un-censored labels for censored ones.

    Fails if the stamp is absent or does not reflect recording_end presence.
    """
    base = pd.Timestamp("2026-01-01 00:00:00")
    with_end = pd.DataFrame(
        {
            "patient_id": ["p1"],
            "recording_id": ["r1"],
            "recording_end": [base + pd.Timedelta(minutes=30)],
            "window_start": [base],
            "window_end": [base + pd.Timedelta(minutes=1)],
        }
    )
    without_end = with_end.drop(columns=["recording_end"])
    events = _events([])

    censored = label_forecast_windows(with_end, events, 5, 30)
    uncensored = label_forecast_windows(
        without_end, events, 5, 30, require_recording_end=False
    )

    assert censored["right_censoring_applied"].all()
    assert not uncensored["right_censoring_applied"].any()
