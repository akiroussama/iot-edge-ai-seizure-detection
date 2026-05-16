from __future__ import annotations

import pandas as pd

from src.baselines.random_rate_matched import generate_random_rate_matched_alarms
from src.datasets.seizeit2_loader import make_synthetic_seizeit2_tables
from src.labeling.sph_sop import label_forecast_windows
from src.metrics.calibration import brier_score, expected_calibration_error, reliability_table


def test_calibration_metrics_are_finite():
    _, windows, events = make_synthetic_seizeit2_tables()
    labeled = label_forecast_windows(
        windows, events, 5, 30, postictal_exclusion_minutes=5, require_recording_end=False
    )
    preds = generate_random_rate_matched_alarms(labeled, 0.1, seed=1)
    assert brier_score(preds) >= 0
    assert expected_calibration_error(preds) >= 0


def test_reliability_table_bins_valid_windows_only():
    preds = pd.DataFrame(
        {
            "risk_score": [0.1, 0.2, 0.9],
            "forecast_label": [False, True, True],
            "is_excluded": [False, False, True],
        }
    )

    table = reliability_table(preds, n_bins=2)

    assert table["count"].sum() == 2
    assert table.loc[0, "count"] == 2
