from __future__ import annotations

import subprocess
import sys

import pandas as pd

from src.baselines.random_rate_matched import generate_random_rate_matched_alarms
from src.metrics.alarm_metrics import time_in_warning
from src.utils.io import read_table, write_table


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


def test_run_baseline_can_use_existing_labels_without_relabeling(tmp_path):
    labels = pd.DataFrame(
        {
            "patient_id": ["p1", "p1"],
            "recording_id": ["r1", "r1"],
            "window_start": pd.date_range("2026-01-01", periods=2, freq="1h"),
            "window_end": pd.date_range("2026-01-01 01:00", periods=2, freq="1h"),
            "forecast_label": [False, True],
            "is_excluded": [False, True],
        }
    )
    labels_path = tmp_path / "labels.parquet"
    out_path = tmp_path / "predictions.parquet"
    write_table(labels, labels_path)

    subprocess.run(
        [
            sys.executable,
            "scripts/run_baseline.py",
            "--labels",
            str(labels_path),
            "--out",
            str(out_path),
            "--tiw",
            "1.0",
        ],
        check=True,
    )

    preds = read_table(out_path)
    assert preds["is_excluded"].tolist() == [False, True]
    assert preds["alarm"].tolist() == [True, False]
