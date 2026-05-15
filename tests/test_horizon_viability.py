from __future__ import annotations

import pandas as pd

from src.reports.horizon_viability import horizon_viability_markdown, horizon_viability_summary


def test_horizon_viability_counts_right_censoring_and_event_coverage() -> None:
    base = pd.Timestamp("2024-01-01 00:00:00")
    windows = pd.DataFrame(
        {
            "patient_id": ["p1", "p1", "p1"],
            "recording_id": ["r1", "r1", "r1"],
            "window_start": [base, base + pd.Timedelta(hours=1), base + pd.Timedelta(hours=2)],
            "window_end": [
                base + pd.Timedelta(hours=1),
                base + pd.Timedelta(hours=2),
                base + pd.Timedelta(hours=3),
            ],
            "recording_end": [base + pd.Timedelta(hours=3)] * 3,
        }
    )
    events = pd.DataFrame(
        {
            "patient_id": ["p1"],
            "recording_id": ["r1"],
            "seizure_start": [base + pd.Timedelta(hours=2, minutes=30)],
            "seizure_end": [base + pd.Timedelta(hours=2, minutes=31)],
        }
    )

    summary = horizon_viability_summary(
        windows,
        events,
        sph_minutes_values=[0],
        sop_minutes_values=[60, 180],
        postictal_exclusion_minutes=0,
    )

    short = summary.loc[summary["sop_minutes"].eq(60)].iloc[0]
    long = summary.loc[summary["sop_minutes"].eq(180)].iloc[0]
    assert short["events_coverable_by_valid_windows"] == 1
    assert long["right_censored_windows"] > short["right_censored_windows"]
    assert long["right_censored_unknown_windows"] > 0


def test_horizon_viability_markdown_disclaims_model_results() -> None:
    summary = pd.DataFrame({"sph_minutes": [60], "sop_minutes": [1440]})

    text = horizon_viability_markdown(summary)

    assert "not a model result" in text
    assert "Right-censored unknown windows" in text
