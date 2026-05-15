from __future__ import annotations

import subprocess
import sys

import pandas as pd

from src.utils.io import read_table, write_table


def _write_inputs(tmp_path):
    base = pd.Timestamp("2026-01-01 00:00:00")
    predictions = pd.DataFrame(
        {
            "patient_id": ["p1"] * 6,
            "recording_id": ["r1"] * 6,
            "window_start": [base + pd.Timedelta(hours=i) for i in range(6)],
            "window_end": [base + pd.Timedelta(hours=i + 1) for i in range(6)],
            "risk_score": [0.1, 0.7, 0.2, 0.8, 0.3, 0.9],
            "forecast_label": [False, True, False, True, False, True],
            "is_excluded": [False] * 6,
            "split": ["train", "train", "val", "val", "test", "test"],
        }
    )
    events = pd.DataFrame(
        {
            "patient_id": ["p1"],
            "recording_id": ["r1"],
            "seizure_start": [base + pd.Timedelta(hours=4)],
            "seizure_end": [base + pd.Timedelta(hours=4, minutes=1)],
        }
    )
    predictions_path = tmp_path / "predictions.parquet"
    events_path = tmp_path / "events.parquet"
    write_table(predictions, predictions_path)
    write_table(events, events_path)
    return predictions_path, events_path


def test_sweep_thresholds_requires_split_filter_when_split_exists(tmp_path) -> None:
    predictions_path, events_path = _write_inputs(tmp_path)
    out_path = tmp_path / "sweep.csv"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/sweep_thresholds.py",
            "--predictions",
            str(predictions_path),
            "--events",
            str(events_path),
            "--output",
            str(out_path),
        ],
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode != 0
    assert "pass --sweep-filter" in result.stderr


def test_sweep_thresholds_refuses_test_sweep_by_default(tmp_path) -> None:
    predictions_path, events_path = _write_inputs(tmp_path)
    out_path = tmp_path / "sweep.csv"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/sweep_thresholds.py",
            "--predictions",
            str(predictions_path),
            "--events",
            str(events_path),
            "--output",
            str(out_path),
            "--sweep-filter",
            "split=test",
        ],
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode != 0
    assert "refusing threshold sweep on split=test" in result.stderr


def test_sweep_thresholds_records_validation_scope(tmp_path) -> None:
    predictions_path, events_path = _write_inputs(tmp_path)
    out_path = tmp_path / "sweep.csv"

    subprocess.run(
        [
            sys.executable,
            "scripts/sweep_thresholds.py",
            "--predictions",
            str(predictions_path),
            "--events",
            str(events_path),
            "--output",
            str(out_path),
            "--sweep-filter",
            "split=val",
            "--steps",
            "3",
        ],
        check=True,
    )

    sweep = read_table(out_path)
    assert set(sweep["sweep_filter"]) == {"split=val"}
    assert set(sweep["publishable_threshold_tuning"]) == {True}
    assert "falsifiability" in sweep.columns
