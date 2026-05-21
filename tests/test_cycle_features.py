from __future__ import annotations

import subprocess
import sys

import pandas as pd

from src.baselines.cycle_baseline import (
    fit_multiday_cycle_prior,
    permute_cycle_labels_within_patient,
    predict_multiday_cycle_prior,
    rolling_origin_multiday_cycle_predictions,
)
from src.features.cycle_features import add_cycle_phase_features
from src.utils.io import read_table, write_table


def _weekly_cycle_labels() -> pd.DataFrame:
    base = pd.Timestamp("2026-01-05 00:00:00")
    rows = []
    for day in range(28):
        split = "train" if day < 14 else "val" if day < 21 else "test"
        positive = day % 7 == 2
        start = base + pd.Timedelta(days=day)
        rows.append(
            {
                "patient_id": "p1",
                "recording_id": f"r{day // 7}",
                "window_start": start,
                "window_end": start + pd.Timedelta(hours=1),
                "forecast_label": positive,
                "is_excluded": False,
                "split": split,
            }
        )
    return pd.DataFrame(rows)


def test_cycle_phase_features_add_circadian_and_weekly_columns() -> None:
    labels = _weekly_cycle_labels().head(2)

    out = add_cycle_phase_features(labels, period_hours=(24.0, 168.0))

    assert {"cycle_24h_sin", "cycle_24h_cos", "cycle_168h_sin", "cycle_168h_cos"}.issubset(
        out.columns
    )
    assert out["cycle_24h_phase"].between(0, 1).all()


def test_multiday_cycle_prior_learns_weekly_phase_from_fit_rows() -> None:
    labels = _weekly_cycle_labels()
    fit = labels.loc[labels["split"].eq("train")]

    model = fit_multiday_cycle_prior(
        fit,
        period_hours=(168.0,),
        n_phase_bins=7,
        smoothing=1.0,
    )
    preds = predict_multiday_cycle_prior(labels, model)

    weekly_positive = preds.loc[preds["window_end"].dt.dayofweek.eq(2), "risk_score"].mean()
    weekly_other = preds.loc[~preds["window_end"].dt.dayofweek.eq(2), "risk_score"].mean()
    assert weekly_positive > weekly_other
    assert "cycle_168h_risk" in preds.columns


def test_rolling_origin_predictions_ignore_future_label_mutation() -> None:
    labels = _weekly_cycle_labels()
    mutated = labels.copy()
    future_mask = mutated["window_end"] > mutated.loc[10, "window_end"]
    mutated.loc[future_mask, "forecast_label"] = ~mutated.loc[future_mask, "forecast_label"].astype(bool)

    preds = rolling_origin_multiday_cycle_predictions(
        labels,
        period_hours=(168.0,),
        n_phase_bins=7,
        min_history_rows=3,
        smoothing=1.0,
    )
    mutated_preds = rolling_origin_multiday_cycle_predictions(
        mutated,
        period_hours=(168.0,),
        n_phase_bins=7,
        min_history_rows=3,
        smoothing=1.0,
    )

    assert preds.loc[:10, "risk_score"].tolist() == mutated_preds.loc[:10, "risk_score"].tolist()


def test_label_permutation_negative_control_preserves_patient_prevalence() -> None:
    labels = _weekly_cycle_labels()

    control = permute_cycle_labels_within_patient(labels, seed=3)

    assert control["forecast_label"].sum() == labels["forecast_label"].sum()
    assert set(control["cycle_negative_control"]) == {"label_permutation_within_patient"}


def test_run_cycle_baseline_cli_supports_multiday_family(tmp_path) -> None:
    labels_path = tmp_path / "labels.parquet"
    out_path = tmp_path / "preds.parquet"
    write_table(_weekly_cycle_labels(), labels_path)

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
            "--cycle-family",
            "multiday",
            "--cycle-period-hours",
            "24",
            "168",
            "--phase-bins",
            "7",
            "--target-tiw",
            "0.25",
        ],
        check=True,
    )

    preds = read_table(out_path)
    assert {"cycle_24h_risk", "cycle_168h_risk", "risk_score", "alarm"}.issubset(preds.columns)
