from __future__ import annotations

import pandas as pd

from src.baselines.random_rate_matched import generate_random_rate_matched_alarms
from src.metrics.alarm_metrics import time_in_warning


def test_random_rate_matched_baseline_ignores_excluded_windows():
    windows = pd.DataFrame(
        {
            "patient_id": ["p1"] * 3,
            "window_start": pd.date_range("2026-01-01", periods=3, freq="1min"),
            "window_end": pd.date_range("2026-01-01 00:01", periods=3, freq="1min"),
            "is_excluded": [False, True, False],
        }
    )

    preds = generate_random_rate_matched_alarms(windows, 1.0, seed=1)

    assert preds.loc[preds["is_excluded"], "alarm"].sum() == 0
    assert preds.loc[~preds["is_excluded"], "alarm"].all()


def test_random_rate_matched_baseline_targets_time_in_warning_with_overlap():
    base = pd.Timestamp("2026-01-01")
    windows = pd.DataFrame(
        {
            "patient_id": ["p1"] * 6,
            "window_start": [base + pd.Timedelta(minutes=i) for i in range(6)],
            "window_end": [base + pd.Timedelta(minutes=i + 2) for i in range(6)],
            "is_excluded": [False] * 6,
        }
    )

    preds = generate_random_rate_matched_alarms(windows, 0.5, seed=3)

    assert abs(time_in_warning(preds) - 0.5) <= 0.25
