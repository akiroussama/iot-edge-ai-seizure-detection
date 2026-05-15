from __future__ import annotations

import subprocess
import sys

import pandas as pd

from src.baselines.cycle_baseline import (
    apply_validation_quantile_alarm,
    fit_cycle_prior,
    predict_cycle_prior,
)
from src.utils.io import read_table, write_table


def _cycle_labels() -> pd.DataFrame:
    base = pd.Timestamp("2026-01-01")
    rows = []
    for day in range(4):
        for hour in (1, 13):
            split = "train" if day < 2 else "val" if day == 2 else "test"
            rows.append(
                {
                    "patient_id": "p1",
                    "recording_id": f"r{day}",
                    "window_start": base + pd.Timedelta(days=day, hours=hour - 1),
                    "window_end": base + pd.Timedelta(days=day, hours=hour),
                    "forecast_label": hour == 13 and day < 2,
                    "is_excluded": False,
                    "split": split,
                }
            )
    return pd.DataFrame(rows)


def test_cycle_prior_learns_hour_of_day_risk_from_fit_rows() -> None:
    labels = _cycle_labels()
    model = fit_cycle_prior(labels.loc[labels["split"].eq("train")], smoothing=1.0)
    preds = predict_cycle_prior(labels, model)

    hour_13 = preds.loc[preds["window_end"].dt.hour.eq(13), "risk_score"].mean()
    hour_1 = preds.loc[preds["window_end"].dt.hour.eq(1), "risk_score"].mean()

    assert hour_13 > hour_1


def test_cycle_threshold_is_selected_on_validation_split_only() -> None:
    labels = _cycle_labels()
    model = fit_cycle_prior(labels.loc[labels["split"].eq("train")], smoothing=1.0)
    preds = predict_cycle_prior(labels, model)

    out, threshold = apply_validation_quantile_alarm(preds, threshold_split="val", target_tiw=0.5)

    assert threshold == preds.loc[preds["split"].eq("val"), "risk_score"].quantile(0.5)
    assert out.loc[out["is_excluded"], "alarm"].sum() == 0


def test_run_cycle_baseline_cli(tmp_path) -> None:
    labels_path = tmp_path / "split_labels.parquet"
    out_path = tmp_path / "cycle_predictions.parquet"
    write_table(_cycle_labels(), labels_path)

    subprocess.run(
        [
            sys.executable,
            "scripts/run_cycle_baseline.py",
            "--split-labels",
            str(labels_path),
            "--out",
            str(out_path),
            "--fit-split",
            "train",
            "--threshold-split",
            "val",
            "--target-tiw",
            "0.5",
        ],
        check=True,
    )

    preds = read_table(out_path)
    assert {"risk_score", "alarm", "alarm_threshold", "threshold_fit_split"}.issubset(preds.columns)
    assert set(preds["threshold_fit_split"]) == {"val"}
