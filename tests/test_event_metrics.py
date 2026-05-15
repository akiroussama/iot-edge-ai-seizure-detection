from __future__ import annotations

import pandas as pd

from src.datasets.seizeit2_loader import make_synthetic_seizeit2_tables
from src.labeling.sph_sop import label_forecast_windows
from src.metrics.event_metrics import event_level_sensitivity
from src.metrics.alarm_metrics import median_lead_time


def test_event_level_sensitivity_detects_valid_forecast_alarm():
    _, windows, events = make_synthetic_seizeit2_tables()
    preds = label_forecast_windows(windows, events, 5, 30, postictal_exclusion_minutes=5)
    preds["risk_score"] = 0.0
    preds["alarm"] = False
    # Alarm window ending 10:30 forecasts the seizure at 10:40 for SPH 5 / SOP 30.
    preds.loc[preds["window_end"].eq(pd.Timestamp("2026-01-01 10:30:00")), "alarm"] = True
    preds.loc[preds["alarm"], "risk_score"] = 0.9

    result = event_level_sensitivity(preds, events, 5, 30)
    assert result["n_events"] == 1
    assert result["n_forecasted"] == 1
    assert result["sensitivity"] == 1.0
    assert median_lead_time(preds, events, 5, 30) == 10 * 60


def test_event_level_sensitivity_ignores_late_alarm():
    _, windows, events = make_synthetic_seizeit2_tables()
    preds = label_forecast_windows(windows, events, 5, 30, postictal_exclusion_minutes=5)
    preds["risk_score"] = 0.0
    preds["alarm"] = False
    # Too late: seizure at 10:40, alarm at 10:39 violates SPH=5.
    preds.loc[preds["window_end"].eq(pd.Timestamp("2026-01-01 10:39:00")), "alarm"] = True
    result = event_level_sensitivity(preds, events, 5, 30)
    assert result["n_forecasted"] == 0
    assert result["sensitivity"] == 0.0
