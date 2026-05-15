from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import numpy as np
import pandas as pd

from src.baselines.random_rate_matched import generate_random_rate_matched_alarms
from src.datasets.seizeit2_loader import make_synthetic_seizeit2_tables
from src.forecasting.alarm_controller import choose_threshold_under_budget
from src.labeling.sph_sop import label_forecast_windows
from src.metrics.alarm_metrics import false_alarm_rate_per_day, time_in_warning
from src.metrics.calibration import brier_score, expected_calibration_error
from src.metrics.event_metrics import event_level_sensitivity
from src.utils.io import write_table


def main() -> None:
    out_dir = Path("reports/synthetic_demo")
    out_dir.mkdir(parents=True, exist_ok=True)
    metadata, windows, events = make_synthetic_seizeit2_tables()
    labeled = label_forecast_windows(windows, events, sph_minutes=5, sop_minutes=30)
    preds = generate_random_rate_matched_alarms(labeled, time_in_warning_fraction=0.1, seed=7)
    # Add a deterministic toy risk: high when time-to-next-seizure is in the forecast zone.
    ttn = preds["time_to_next_seizure_seconds"].astype(float)
    toy = np.exp(-np.abs(ttn - 15 * 60) / (20 * 60))
    preds["risk_score"] = np.nan_to_num(toy, nan=0.02)
    chosen = choose_threshold_under_budget(preds, events, 5, 30)
    rows = []
    for name, df in [("random_rate_matched", preds), ("toy_oracle_sanity", preds.assign(alarm=preds["risk_score"] >= chosen["threshold"]))]:
        sens = event_level_sensitivity(df, events, 5, 30)
        rows.append(
            {
                "baseline": name,
                "sensitivity": sens["sensitivity"],
                "far_per_day": false_alarm_rate_per_day(df, events, 5, 30),
                "time_in_warning": time_in_warning(df),
                "brier": brier_score(df),
                "ece": expected_calibration_error(df),
            }
        )
    results = pd.DataFrame(rows)
    write_table(metadata, out_dir / "metadata.csv")
    write_table(events, out_dir / "events.csv")
    write_table(labeled, out_dir / "labels.csv")
    write_table(preds, out_dir / "predictions.csv")
    write_table(results, out_dir / "baseline_results.csv")
    print(results.to_string(index=False))


if __name__ == "__main__":
    main()
