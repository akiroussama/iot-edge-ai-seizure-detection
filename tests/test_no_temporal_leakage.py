from __future__ import annotations

from src.datasets.seizeit2_loader import make_synthetic_seizeit2_tables
import pandas as pd

from src.splits.leakage_checks import (
    check_duplicate_windows,
    check_postictal_label_contamination,
    check_temporal_leakage,
    leakage_audit,
)
from src.splits.temporal_split import temporal_split_per_patient


def test_temporal_split_has_no_order_leakage():
    _, windows, _ = make_synthetic_seizeit2_tables()
    split = temporal_split_per_patient(windows, train_fraction=0.7, val_fraction=0.1)
    audit = check_temporal_leakage(split)
    assert not audit["has_leakage"]


def test_temporal_leakage_detected_when_test_before_train():
    _, windows, _ = make_synthetic_seizeit2_tables()
    split = windows.copy()
    split["split"] = "train"
    split.loc[split.index[:10], "split"] = "test"
    audit = check_temporal_leakage(split)
    assert audit["has_leakage"]


def test_temporal_split_purges_overlapping_boundary_windows():
    base = pd.Timestamp("2026-01-01 00:00:00")
    windows = pd.DataFrame(
        {
            "patient_id": ["p1"] * 6,
            "recording_id": ["r1"] * 6,
            "window_start": [base + pd.Timedelta(minutes=i) for i in range(6)],
            "window_end": [base + pd.Timedelta(minutes=i + 3) for i in range(6)],
        }
    )

    split = temporal_split_per_patient(windows, train_fraction=0.5, val_fraction=0.25)
    audit = check_temporal_leakage(split.loc[split["split"].ne("purge")])

    assert "purge" in set(split["split"])
    assert not audit["has_leakage"]


def test_leakage_audit_marks_temporal_patient_overlap_as_contextual():
    _, windows, _ = make_synthetic_seizeit2_tables()
    split = temporal_split_per_patient(windows, train_fraction=0.7, val_fraction=0.1)

    report = leakage_audit(split, split_strategy="temporal")

    assert "Patient overlap across splits: True" in report
    assert "Temporal ordering/overlap leakage: False" in report


def test_duplicate_window_check_detects_repeated_intervals():
    df = pd.DataFrame(
        {
            "patient_id": ["p1", "p1"],
            "recording_id": ["r1", "r1"],
            "window_start": [pd.Timestamp("2026-01-01")] * 2,
            "window_end": [pd.Timestamp("2026-01-01 00:01:00")] * 2,
        }
    )

    assert check_duplicate_windows(df)["has_leakage"]


def test_postictal_label_contamination_check_detects_unexcluded_positive():
    df = pd.DataFrame(
        {
            "patient_id": ["p1"],
            "recording_id": ["r1"],
            "window_start": [pd.Timestamp("2026-01-01")],
            "window_end": [pd.Timestamp("2026-01-01 00:01:00")],
            "forecast_label": [True],
            "is_postictal": [True],
            "is_excluded": [False],
        }
    )

    assert check_postictal_label_contamination(df)["has_leakage"]
