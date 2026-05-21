from __future__ import annotations

import json
import subprocess
import sys

import pandas as pd
import pytest

from src.baselines.patient_adaptive import (
    PatientAdaptiveConfig,
    patient_adaptive_predictions,
    patient_adaptive_summary,
)
from src.metrics.alarm_metrics import time_in_warning
from src.utils.io import read_table, write_table


def _adaptive_labels() -> pd.DataFrame:
    base = pd.Timestamp("2026-01-01 00:00:00")
    rows = []
    spec = [
        ("p1", "train", [True, True, True, True]),
        ("p2", "train", [False, False, False, False]),
        ("p1", "val", [True, False]),
        ("p2", "val", [False, False]),
        ("p3", "val", [False, True]),
        ("p1", "test", [False, True, False]),
        ("p2", "test", [True, False, False]),
        ("p3", "test", [False, False, False]),
    ]
    cursor = 0
    for patient, split, labels in spec:
        for value in labels:
            start = base + pd.Timedelta(hours=cursor)
            rows.append(
                {
                    "patient_id": patient,
                    "recording_id": f"{patient}_{split}",
                    "window_start": start,
                    "window_end": start + pd.Timedelta(hours=1),
                    "forecast_label": value,
                    "is_excluded": False,
                    "split": split,
                }
            )
            cursor += 1
    return pd.DataFrame(rows)


def test_empirical_bayes_warm_start_recovers_patient_rates_with_shrinkage() -> None:
    preds = patient_adaptive_predictions(
        _adaptive_labels(),
        config=PatientAdaptiveConfig(
            baseline="empirical_bayes",
            evaluation_mode="warm_start",
            min_patient_observations=3,
            prior_strength=4.0,
            target_tiw=0.5,
        ),
    )

    test = preds.loc[preds["split"].eq("test")]
    p1 = test.loc[test["patient_id"].eq("p1"), "risk_score"].iloc[0]
    p2 = test.loc[test["patient_id"].eq("p2"), "risk_score"].iloc[0]
    p3 = test.loc[test["patient_id"].eq("p3"), "risk_score"].iloc[0]
    assert p1 == pytest.approx(0.75)
    assert p2 == pytest.approx(0.25)
    assert p3 == pytest.approx(0.5)
    assert set(test.loc[test["patient_id"].eq("p3"), "patient_adaptive_variant"]) == {
        "empirical_bayes_fallback_population"
    }


def test_cold_start_is_distinct_from_warm_start() -> None:
    labels = _adaptive_labels()
    cold = patient_adaptive_predictions(
        labels,
        config=PatientAdaptiveConfig(
            baseline="empirical_bayes",
            evaluation_mode="cold_start",
            prior_strength=4.0,
        ),
    )
    warm = patient_adaptive_predictions(
        labels,
        config=PatientAdaptiveConfig(
            baseline="empirical_bayes",
            evaluation_mode="warm_start",
            prior_strength=4.0,
        ),
    )

    assert cold["risk_score"].nunique() == 1
    assert "cold_start" in cold["patient_adaptive_variant"].iloc[0]
    assert warm["risk_score"].nunique() > 1
    assert set(cold["adaptive_evaluation_mode"]) == {"cold_start"}
    assert set(warm["adaptive_evaluation_mode"]) == {"warm_start"}


def test_rolling_origin_does_not_read_future_labels() -> None:
    labels = _adaptive_labels()
    mutated = labels.copy()
    future_idx = mutated.index[mutated["split"].eq("test") & mutated["patient_id"].eq("p1")].max()
    mutated.loc[future_idx, "forecast_label"] = True

    config = PatientAdaptiveConfig(
        baseline="empirical_bayes",
        evaluation_mode="rolling_origin",
        min_patient_observations=3,
        prior_strength=4.0,
    )
    preds = patient_adaptive_predictions(labels, config=config)
    mutated_preds = patient_adaptive_predictions(mutated, config=config)
    first_p1_test = labels.index[labels["split"].eq("test") & labels["patient_id"].eq("p1")].min()

    assert preds.loc[first_p1_test, "risk_score"] == pytest.approx(
        mutated_preds.loc[first_p1_test, "risk_score"]
    )


def test_min_observations_fallback_is_explicit() -> None:
    preds = patient_adaptive_predictions(
        _adaptive_labels(),
        config=PatientAdaptiveConfig(
            baseline="patient",
            evaluation_mode="warm_start",
            min_patient_observations=5,
        ),
    )

    assert set(preds["patient_adaptive_variant"]) == {"patient_fallback_population"}


def test_patient_adaptive_summary_and_tiw() -> None:
    preds = patient_adaptive_predictions(
        _adaptive_labels(),
        config=PatientAdaptiveConfig(target_tiw=0.5),
    )
    summary = patient_adaptive_summary(preds)

    assert not summary.empty
    assert abs(time_in_warning(preds.loc[preds["split"].eq("val")]) - 0.5) <= 0.25


def test_run_patient_adaptive_baseline_cli_writes_outputs(tmp_path) -> None:
    labels_path = tmp_path / "labels.csv"
    out_path = tmp_path / "predictions.csv"
    summary_path = tmp_path / "summary.csv"
    json_path = tmp_path / "summary.json"
    write_table(_adaptive_labels(), labels_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_patient_adaptive_baseline.py",
            "--labels",
            str(labels_path),
            "--out",
            str(out_path),
            "--summary-out",
            str(summary_path),
            "--json-out",
            str(json_path),
            "--baseline",
            "empirical_bayes",
            "--evaluation-mode",
            "warm_start",
            "--prior-strength",
            "4",
            "--target-tiw",
            "0.5",
        ],
        check=True,
        text=True,
        capture_output=True,
    )

    preds = read_table(out_path)
    summary = read_table(summary_path)
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert '"baseline": "empirical_bayes"' in result.stdout
    assert {"risk_score", "alarm", "patient_adaptive_variant"}.issubset(preds.columns)
    assert not summary.empty
    assert payload["config"]["baseline"] == "empirical_bayes"
