from __future__ import annotations

import pandas as pd

from src.forecasting.alarm_controller import AlarmControllerConfig, apply_alarm_threshold, choose_threshold_under_budget


def test_apply_alarm_threshold_with_quality_uncertainty() -> None:
    df = pd.DataFrame(
        {
            "patient_id": ["p1", "p1", "p1"],
            "window_start": pd.date_range("2026-01-01", periods=3, freq="10min"),
            "window_end": pd.date_range("2026-01-01 00:01", periods=3, freq="10min"),
            "risk_score": [0.9, 0.9, 0.1],
            "uncertainty": [0.2, 0.9, 0.1],
            "signal_quality": [0.9, 0.9, 0.9],
            "forecast_label": [False, False, False],
        }
    )
    out = apply_alarm_threshold(df, 0.5, config=AlarmControllerConfig(max_uncertainty=0.5))
    assert out["alarm"].tolist() == [True, False, False]


def test_choose_threshold_under_budget_returns_dict() -> None:
    preds = pd.DataFrame(
        {
            "patient_id": ["p1"] * 10,
            "window_start": pd.date_range("2026-01-01", periods=10, freq="10min"),
            "window_end": pd.date_range("2026-01-01 00:01", periods=10, freq="10min"),
            "risk_score": [0.1] * 9 + [0.9],
            "forecast_label": [False] * 9 + [True],
            "is_excluded": [False] * 10,
        }
    )
    events = pd.DataFrame(
        {
            "patient_id": ["p1"],
            "seizure_start": [pd.Timestamp("2026-01-01 01:45")],
            "seizure_end": [pd.Timestamp("2026-01-01 01:46")],
        }
    )
    result = choose_threshold_under_budget(preds, events, 5, 30, config=AlarmControllerConfig(max_far_per_day=999, max_time_in_warning=1.0), thresholds=[0.5, 0.8])
    assert set(result) == {"threshold", "sensitivity", "far_per_day", "time_in_warning"}
