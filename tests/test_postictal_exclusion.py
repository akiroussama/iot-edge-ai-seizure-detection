from __future__ import annotations

import pandas as pd

from src.datasets.seizeit2_loader import make_synthetic_seizeit2_tables
from src.labeling.sph_sop import label_forecast_windows


def test_ictal_and_postictal_exclusion():
    _, windows, events = make_synthetic_seizeit2_tables()
    labeled = label_forecast_windows(windows, events, 5, 30, postictal_exclusion_minutes=5)

    ictal = labeled.loc[labeled["is_ictal"]]
    assert not ictal.empty
    assert ictal["window_start"].min() < pd.Timestamp("2026-01-01 10:42:00")
    assert ictal["window_end"].max() > pd.Timestamp("2026-01-01 10:40:00")

    postictal = labeled.loc[labeled["is_postictal"]]
    assert not postictal.empty
    assert postictal["window_start"].min() < pd.Timestamp("2026-01-01 10:47:00")
    assert postictal["window_end"].max() > pd.Timestamp("2026-01-01 10:42:00")

    assert labeled.loc[labeled["is_ictal"] | labeled["is_postictal"], "is_excluded"].all()
