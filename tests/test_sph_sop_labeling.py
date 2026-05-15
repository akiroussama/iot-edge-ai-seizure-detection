from __future__ import annotations

import pandas as pd

from src.datasets.seizeit2_loader import make_synthetic_seizeit2_tables
from src.labeling.sph_sop import label_forecast_windows


def test_sph_sop_labeling_exact_boundaries():
    _, windows, events = make_synthetic_seizeit2_tables()
    labeled = label_forecast_windows(
        windows,
        events,
        sph_minutes=5,
        sop_minutes=30,
        postictal_exclusion_minutes=5,
    )
    seizure_start = events.iloc[0]["seizure_start"]
    positive_ends = set(labeled.loc[labeled["forecast_label"], "window_end"])

    # Positive iff seizure_start in [window_end + 5 min, window_end + 35 min).
    expected = set()
    for _, row in labeled.iterrows():
        if seizure_start >= row["window_end"] + pd.Timedelta(minutes=5) and seizure_start < row["window_end"] + pd.Timedelta(minutes=35):
            expected.add(row["window_end"])
    assert positive_ends == expected

    # Exact expected interval for seizure at 10:40 with 1-minute windows.
    assert min(positive_ends) == pd.Timestamp("2026-01-01 10:06:00")
    assert max(positive_ends) == pd.Timestamp("2026-01-01 10:35:00")


def test_time_to_next_and_since_last_seizure():
    _, windows, events = make_synthetic_seizeit2_tables()
    labeled = label_forecast_windows(windows, events, 5, 30, postictal_exclusion_minutes=5)
    row = labeled.loc[labeled["window_end"].eq(pd.Timestamp("2026-01-01 10:10:00"))].iloc[0]
    assert row["time_to_next_seizure_seconds"] == 30 * 60
    post = labeled.loc[labeled["window_end"].eq(pd.Timestamp("2026-01-01 10:50:00"))].iloc[0]
    assert post["time_since_last_seizure_seconds"] == 8 * 60
