from __future__ import annotations

import pandas as pd

from src.preprocessing.windowing import generate_fixed_windows


def test_generate_fixed_windows_datetime_boundaries():
    recordings = pd.DataFrame(
        [
            {
                "patient_id": "p1",
                "recording_id": "r1",
                "center_id": "c1",
                "recording_start": pd.Timestamp("2026-01-01 00:00:00"),
                "recording_end": pd.Timestamp("2026-01-01 00:05:00"),
            }
        ]
    )

    windows = generate_fixed_windows(recordings, window_duration="2min", stride="1min")

    assert len(windows) == 4
    assert windows["window_start"].iloc[0] == pd.Timestamp("2026-01-01 00:00:00")
    assert windows["window_end"].iloc[-1] == pd.Timestamp("2026-01-01 00:05:00")
    assert (windows["window_end"] <= recordings.iloc[0]["recording_end"]).all()
    assert set(windows["center_id"]) == {"c1"}


def test_generate_fixed_windows_numeric_seconds():
    recordings = pd.DataFrame(
        [
            {
                "patient_id": "p2",
                "recording_id": "r2",
                "recording_start": 10.0,
                "recording_end": 20.0,
            }
        ]
    )

    windows = generate_fixed_windows(recordings, window_duration="4s", stride="3s")

    assert windows[["window_start", "window_end"]].to_dict("records") == [
        {"window_start": 10.0, "window_end": 14.0},
        {"window_start": 13.0, "window_end": 17.0},
        {"window_start": 16.0, "window_end": 20.0},
    ]


def test_generate_fixed_windows_skips_short_recordings():
    recordings = pd.DataFrame(
        [
            {
                "patient_id": "p3",
                "recording_id": "r3",
                "recording_start": pd.Timestamp("2026-01-01 00:00:00"),
                "recording_end": pd.Timestamp("2026-01-01 00:00:30"),
            }
        ]
    )

    windows = generate_fixed_windows(recordings, window_duration="2min", stride="1min")

    assert windows.empty
