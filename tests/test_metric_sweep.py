from __future__ import annotations

import pandas as pd

from src.metrics.sweep import (
    select_threshold_under_constraints,
    sensitivity_at_fixed_time_in_warning,
    threshold_sweep_table,
)


def test_sensitivity_at_fixed_time_in_warning_returns_budgeted_threshold():
    base = pd.Timestamp("2026-01-01 00:00:00")
    preds = pd.DataFrame(
        {
            "patient_id": ["p1"] * 4,
            "recording_id": ["r1"] * 4,
            "window_start": [base + pd.Timedelta(minutes=i) for i in range(4)],
            "window_end": [base + pd.Timedelta(minutes=i + 1) for i in range(4)],
            "risk_score": [0.9, 0.1, 0.8, 0.2],
            "forecast_label": [True, False, True, False],
            "is_excluded": [False] * 4,
            "split": ["val"] * 4,
        }
    )
    events = pd.DataFrame(
        [
            {
                "patient_id": "p1",
                "recording_id": "r1",
                "seizure_start": base + pd.Timedelta(minutes=6),
                "seizure_end": base + pd.Timedelta(minutes=7),
            }
        ]
    )

    result = sensitivity_at_fixed_time_in_warning(
        preds,
        events,
        2,
        5,
        0.5,
        thresholds=[0.0, 0.5],
        sweep_filter="split=val",
    )

    assert result["threshold"] == 0.5
    assert result["time_in_warning"] <= 0.5
    assert result["publishable_threshold_tuning"]


def test_threshold_sweep_table_and_constraint_selection():
    base = pd.Timestamp("2026-01-01 00:00:00")
    preds = pd.DataFrame(
        {
            "patient_id": ["p1"] * 4,
            "recording_id": ["r1"] * 4,
            "window_start": [base + pd.Timedelta(minutes=i) for i in range(4)],
            "window_end": [base + pd.Timedelta(minutes=i + 1) for i in range(4)],
            "risk_score": [0.95, 0.7, 0.2, 0.1],
            "forecast_label": [True, True, False, False],
            "is_excluded": [False] * 4,
            "split": ["val"] * 4,
        }
    )
    events = pd.DataFrame(
        [
            {
                "patient_id": "p1",
                "recording_id": "r1",
                "seizure_start": base + pd.Timedelta(minutes=6),
                "seizure_end": base + pd.Timedelta(minutes=7),
            }
        ]
    )

    sweep = threshold_sweep_table(
        preds,
        events,
        2,
        5,
        thresholds=[0.0, 0.5, 0.9, 1.0],
        sweep_filter="split=val",
    )
    selected = select_threshold_under_constraints(sweep, max_time_in_warning=0.5)

    assert list(sweep["threshold"]) == [0.0, 0.5, 0.9, 1.0]
    assert {"brier_score", "ece", "far_per_day", "time_in_warning"}.issubset(sweep.columns)
    assert set(sweep["sweep_filter"]) == {"split=val"}
    assert selected["time_in_warning"] <= 0.5


def test_threshold_sweep_library_refuses_unsplit_table_by_default():
    base = pd.Timestamp("2026-01-01 00:00:00")
    preds = pd.DataFrame(
        {
            "patient_id": ["p1"],
            "recording_id": ["r1"],
            "window_start": [base],
            "window_end": [base + pd.Timedelta(minutes=1)],
            "risk_score": [0.5],
            "forecast_label": [False],
            "is_excluded": [False],
        }
    )
    events = pd.DataFrame(columns=["patient_id", "recording_id", "seizure_start", "seizure_end"])

    try:
        threshold_sweep_table(preds, events, 2, 5, thresholds=[0.0, 1.0])
    except ValueError as exc:
        assert "no split column" in str(exc)
    else:
        raise AssertionError("expected unsplit threshold sweep to fail")


def test_threshold_sweep_library_refuses_test_split_by_default():
    base = pd.Timestamp("2026-01-01 00:00:00")
    preds = pd.DataFrame(
        {
            "patient_id": ["p1"],
            "recording_id": ["r1"],
            "window_start": [base],
            "window_end": [base + pd.Timedelta(minutes=1)],
            "risk_score": [0.5],
            "forecast_label": [False],
            "is_excluded": [False],
            "split": ["test"],
        }
    )
    events = pd.DataFrame(columns=["patient_id", "recording_id", "seizure_start", "seizure_end"])

    try:
        threshold_sweep_table(preds, events, 2, 5, thresholds=[0.0, 1.0], sweep_filter="split=test")
    except ValueError as exc:
        assert "split=test" in str(exc)
    else:
        raise AssertionError("expected test threshold sweep to fail")
