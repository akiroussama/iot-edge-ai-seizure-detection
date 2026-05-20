from __future__ import annotations

import subprocess
import sys

import pandas as pd
import pytest

from src.baselines.forecast_nulls import (
    appended_columns,
    cycle_preserving_random,
    derive_model_seed,
    generate_forecast_null,
    patient_prior,
    rate_matched_random,
    split_prevalence_prior,
    variant_counts,
)
from src.metrics.calibration import brier_score
from src.metrics.alarm_metrics import time_in_warning
from src.utils.io import read_table, write_table


def _labels(
    *,
    n_per_split: int = 12,
    positive_every: int = 4,
    patients: tuple[str, ...] = ("p1", "p2"),
) -> pd.DataFrame:
    base = pd.Timestamp("2026-01-01 00:00:00")
    rows = []
    pos = 0
    for split_idx, split in enumerate(("train", "val", "test")):
        for i in range(n_per_split):
            patient = patients[i % len(patients)]
            start = base + pd.Timedelta(days=split_idx, hours=i)
            rows.append(
                {
                    "patient_id": patient,
                    "recording_id": f"{patient}_{split}",
                    "window_start": start,
                    "window_end": start + pd.Timedelta(hours=1),
                    "forecast_label": pos % positive_every == 0,
                    "is_excluded": False,
                    "split": split,
                }
            )
            pos += 1
    return pd.DataFrame(rows)


def _patient_prior_labels() -> pd.DataFrame:
    base = pd.Timestamp("2026-01-01 00:00:00")
    rows = []
    spec = [
        ("p1", "train", [True, True, True, False]),
        ("p2", "train", [True, False, False, False]),
        ("p1", "val", [True, False]),
        ("p2", "val", [False, False]),
        ("p3", "val", [False, True]),
        ("p1", "test", [False, True]),
        ("p2", "test", [True, False]),
        ("p3", "test", [False, False]),
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


def _cycle_labels() -> pd.DataFrame:
    base = pd.Timestamp("2026-01-01")
    rows = []
    for split_idx, split in enumerate(("train", "val", "test")):
        for day in range(4):
            for hour in (3, 15):
                start = base + pd.Timedelta(days=split_idx * 5 + day, hours=hour)
                rows.append(
                    {
                        "patient_id": "p1",
                        "recording_id": f"{split}_{day}",
                        "window_start": start,
                        "window_end": start + pd.Timedelta(hours=1),
                        "forecast_label": split == "train" and hour == 15,
                        "is_excluded": False,
                        "split": split,
                    }
                )
    return pd.DataFrame(rows)


def test_output_passes_through_input_columns_and_appends_contract_columns() -> None:
    labels = _labels()

    preds = split_prevalence_prior(labels, target_tiw=0.25)

    assert preds.columns.tolist() == labels.columns.tolist() + list(appended_columns())
    pd.testing.assert_frame_equal(preds[labels.columns], labels)


def test_rate_matched_random_respects_target_tiw_on_threshold_split() -> None:
    labels = _labels(n_per_split=20)

    preds = rate_matched_random(labels, target_tiw=0.25, seed=7)
    val_preds = preds.loc[preds["split"].eq("val")]

    assert abs(time_in_warning(val_preds) - 0.25) <= 0.06


def test_patient_prior_fit_uses_only_fit_split() -> None:
    labels = _patient_prior_labels()
    mutated = labels.copy()
    mutated.loc[mutated["split"].eq("test"), "forecast_label"] = ~mutated.loc[
        mutated["split"].eq("test"), "forecast_label"
    ].astype(bool)

    preds = patient_prior(labels, target_tiw=0.5, seed=11, patient_min_events=2)
    mutated_preds = patient_prior(mutated, target_tiw=0.5, seed=11, patient_min_events=2)

    pd.testing.assert_series_equal(preds["risk_score"], mutated_preds["risk_score"])
    pd.testing.assert_series_equal(preds["alarm"], mutated_preds["alarm"])


def test_cycle_preserving_random_uses_only_fit_split_for_bins() -> None:
    labels = _cycle_labels()
    mutated = labels.copy()
    mutated.loc[mutated["split"].eq("test") & mutated["window_start"].dt.hour.eq(3), "forecast_label"] = True

    preds = cycle_preserving_random(labels, target_tiw=0.5, seed=5)
    mutated_preds = cycle_preserving_random(mutated, target_tiw=0.5, seed=5)

    pd.testing.assert_series_equal(preds["risk_score"], mutated_preds["risk_score"])
    assert preds.loc[preds["window_start"].dt.hour.eq(3), "risk_score"].eq(0.0).all()
    assert not preds.loc[preds["window_start"].dt.hour.eq(3), "alarm"].any()


def test_empty_threshold_split_raises_explicit_error() -> None:
    labels = _labels()
    labels.loc[labels["split"].eq("val"), "is_excluded"] = True

    with pytest.raises(ValueError, match="threshold split"):
        split_prevalence_prior(labels)


def test_empty_fit_split_raises_explicit_error() -> None:
    labels = _labels()
    labels.loc[labels["split"].eq("train"), "is_excluded"] = True

    with pytest.raises(ValueError, match="fit split"):
        split_prevalence_prior(labels)


def test_missing_split_column_raises_explicit_error() -> None:
    labels = _labels().drop(columns=["split"])

    with pytest.raises(ValueError, match="split column"):
        split_prevalence_prior(labels)


def test_test_split_never_used_for_fit_or_threshold() -> None:
    labels = _labels()
    mutated = labels.copy()
    mutated.loc[mutated["split"].eq("test"), "forecast_label"] = True
    mutated.loc[mutated["split"].eq("test"), "is_excluded"] = False

    preds = split_prevalence_prior(labels, target_tiw=0.25, seed=9)
    mutated_preds = split_prevalence_prior(mutated, target_tiw=0.25, seed=9)

    pd.testing.assert_series_equal(preds["risk_score"], mutated_preds["risk_score"])
    pd.testing.assert_series_equal(preds["alarm"], mutated_preds["alarm"])


def test_identical_seed_produces_identical_output() -> None:
    labels = _labels()

    a = rate_matched_random(labels, target_tiw=0.25, seed=123)
    b = rate_matched_random(labels, target_tiw=0.25, seed=123)

    pd.testing.assert_frame_equal(a, b)


def test_model_seed_derivation_is_per_model_and_stable() -> None:
    seed = 42

    derived = {
        "split_prevalence_prior": derive_model_seed(seed, "split_prevalence_prior"),
        "rate_matched_random": derive_model_seed(seed, "rate_matched_random"),
        "patient_prior": derive_model_seed(seed, "patient_prior"),
        "cycle_preserving_random": derive_model_seed(seed, "cycle_preserving_random"),
    }

    assert len(set(derived.values())) == len(derived)
    assert derived["rate_matched_random"] == derive_model_seed(seed, "rate_matched_random")


def test_forbidden_columns_are_ignored_for_risk_scores() -> None:
    labels = _labels()
    injected = labels.copy()
    injected["time_to_next_seizure_seconds"] = range(len(injected))
    injected["time_since_last_seizure_seconds"] = list(reversed(range(len(injected))))
    injected["is_right_censored"] = injected["split"].eq("test")
    injected["right_censoring_applied"] = True

    base_preds = patient_prior(labels, target_tiw=0.25, seed=17, patient_min_events=1)
    injected_preds = patient_prior(injected, target_tiw=0.25, seed=17, patient_min_events=1)

    pd.testing.assert_series_equal(base_preds["risk_score"], injected_preds["risk_score"])
    pd.testing.assert_series_equal(base_preds["alarm"], injected_preds["alarm"])


def test_patient_prior_marks_population_fallbacks() -> None:
    labels = _patient_prior_labels()

    preds = patient_prior(labels, target_tiw=0.5, patient_min_events=2)

    assert set(preds.loc[preds["patient_id"].eq("p1"), "null_model_variant"]) == {"patient_prior"}
    assert set(preds.loc[preds["patient_id"].eq("p2"), "null_model_variant"]) == {
        "patient_prior_fallback_population"
    }
    assert set(preds.loc[preds["patient_id"].eq("p3"), "null_model_variant"]) == {
        "patient_prior_fallback_population"
    }


def test_patient_prior_variant_counts_are_reportable() -> None:
    labels = _patient_prior_labels()

    counts = variant_counts(patient_prior(labels, target_tiw=0.5, patient_min_events=2))

    assert counts["patient_prior"] == 8
    assert counts["patient_prior_fallback_population"] == 12


def test_split_prevalence_prior_brier_matches_climatology() -> None:
    labels = _labels(n_per_split=12, positive_every=4)
    train_p = labels.loc[labels["split"].eq("train"), "forecast_label"].mean()

    preds = split_prevalence_prior(labels, target_tiw=0.25)

    assert brier_score(preds) == pytest.approx(train_p * (1 - train_p))


def test_split_prevalence_prior_bss_against_itself_is_zero() -> None:
    labels = _labels(n_per_split=12, positive_every=4)
    preds = split_prevalence_prior(labels, target_tiw=0.25)

    bss = 1.0 - brier_score(preds) / brier_score(preds)

    assert bss == pytest.approx(0.0)


def test_rate_matched_random_brier_is_climatology_like() -> None:
    labels = _labels(n_per_split=12, positive_every=4)
    train_p = labels.loc[labels["split"].eq("train"), "forecast_label"].mean()

    preds = rate_matched_random(labels, target_tiw=0.25, seed=99)

    assert brier_score(preds) == pytest.approx(train_p * (1 - train_p))


def test_run_null_baseline_cli(tmp_path) -> None:
    labels_path = tmp_path / "labels.csv"
    out_path = tmp_path / "null_predictions.csv"
    write_table(_patient_prior_labels(), labels_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_null_baseline.py",
            "--labels",
            str(labels_path),
            "--out",
            str(out_path),
            "--null-model",
            "patient_prior",
            "--target-tiw",
            "0.5",
            "--patient-min-events",
            "2",
        ],
        check=True,
        text=True,
        capture_output=True,
    )

    preds = read_table(out_path)
    assert "patient_prior_fallback_population" in result.stdout
    assert {"risk_score", "alarm", "null_model", "null_model_variant"}.issubset(preds.columns)
    assert preds["null_model"].eq("patient_prior").all()


def test_unknown_null_model_raises() -> None:
    with pytest.raises(ValueError, match="unknown null_model"):
        generate_forecast_null(_labels(), null_model="unknown")
