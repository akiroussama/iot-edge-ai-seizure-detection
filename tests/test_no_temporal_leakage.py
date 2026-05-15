from __future__ import annotations

from src.datasets.seizeit2_loader import make_synthetic_seizeit2_tables
import pandas as pd

from src.splits.leakage_checks import (
    check_duplicate_recording_time_ranges,
    check_duplicate_windows,
    check_fit_scope_metadata,
    check_postictal_label_contamination,
    check_temporal_leakage,
    leakage_audit,
)
from src.splits.recording_split import recording_wise_split
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


def test_temporal_split_uses_elapsed_time_by_default_not_row_count():
    base = pd.Timestamp("2026-01-01 00:00:00")
    windows = pd.DataFrame(
        {
            "patient_id": ["p1"] * 4,
            "recording_id": ["r1"] * 4,
            "window_start": [
                base,
                base + pd.Timedelta(minutes=1),
                base + pd.Timedelta(minutes=2),
                base + pd.Timedelta(hours=10),
            ],
            "window_end": [
                base + pd.Timedelta(minutes=1),
                base + pd.Timedelta(minutes=2),
                base + pd.Timedelta(minutes=3),
                base + pd.Timedelta(hours=11),
            ],
        }
    )

    split = temporal_split_per_patient(
        windows,
        train_fraction=0.5,
        val_fraction=0.25,
        purge_overlap=False,
    )

    assert split["split"].tolist() == ["train", "train", "train", "test"]


def test_leakage_audit_marks_temporal_patient_overlap_as_contextual():
    _, windows, _ = make_synthetic_seizeit2_tables()
    split = temporal_split_per_patient(windows, train_fraction=0.7, val_fraction=0.1)

    report = leakage_audit(split, split_strategy="temporal")

    assert "Patient overlap across splits: True" in report
    assert "Temporal ordering/overlap leakage: False" in report
    assert "Feature normalization leakage: UNVERIFIED_OR_FAILED" in report


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


def test_duplicate_recording_time_ranges_flag_reset_timestamps():
    base = pd.Timestamp("2026-01-01 00:00:00")
    df = pd.DataFrame(
        {
            "patient_id": ["p1", "p1"],
            "recording_id": ["r1", "r2"],
            "window_start": [base, base],
            "window_end": [base + pd.Timedelta(minutes=1), base + pd.Timedelta(minutes=1)],
        }
    )

    audit = check_duplicate_recording_time_ranges(df)

    assert audit["has_leakage"]
    assert {issue["recording_id"] for issue in audit["issues"]} == {"r1", "r2"}


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


def test_recording_wise_split_keeps_recordings_disjoint():
    base = pd.Timestamp("2026-01-01 00:00:00")
    rows = []
    for rec in range(10):
        for i in range(3):
            rows.append(
                {
                    "patient_id": "single_patient",
                    "recording_id": f"run-{rec:02d}",
                    "window_start": base + pd.Timedelta(minutes=i),
                    "window_end": base + pd.Timedelta(minutes=i + 1),
                }
            )
    windows = pd.DataFrame(rows)

    split = recording_wise_split(windows, test_fraction=0.2, val_fraction=0.1, seed=7)
    report = leakage_audit(split, split_strategy="recording_wise")

    assert split.groupby("recording_id")["split"].nunique().max() == 1
    assert "Patient overlap across splits: True" in report
    assert "Recording overlap across splits: False" in report
    assert "Temporal ordering/overlap leakage: not evaluated" in report


def test_temporal_recording_unit_keeps_recordings_disjoint_and_ordered():
    base = pd.Timestamp("2026-01-01 00:00:00")
    rows = []
    for rec in range(5):
        rec_start = base + pd.Timedelta(days=rec)
        for hour in range(4):
            rows.append(
                {
                    "patient_id": "p1",
                    "recording_id": f"r{rec}",
                    "window_start": rec_start + pd.Timedelta(hours=hour),
                    "window_end": rec_start + pd.Timedelta(hours=hour + 1),
                }
            )
    windows = pd.DataFrame(rows)

    split = temporal_split_per_patient(
        windows,
        train_fraction=0.4,
        val_fraction=0.2,
        split_unit="recording",
    )
    report = leakage_audit(split, split_strategy="temporal_recording")

    assert split.groupby("recording_id")["split"].nunique().max() == 1
    assert "Recording overlap across splits: False" in report
    assert "Temporal ordering/overlap leakage: False" in report


def test_temporal_recording_unit_requires_recording_id():
    _, windows, _ = make_synthetic_seizeit2_tables()

    try:
        temporal_split_per_patient(windows.drop(columns=["recording_id"]), split_unit="recording")
    except ValueError as exc:
        assert "recording_id" in str(exc)
    else:
        raise AssertionError("expected recording_id validation error")


def test_fit_scope_metadata_flags_test_fit_scope() -> None:
    df = pd.DataFrame(
        {
            "score_fit_split": ["test", "test"],
            "threshold_source_split": ["val", "val"],
        }
    )

    audit = check_fit_scope_metadata(df)

    assert audit["has_leakage"]
    assert audit["issues"][0]["status"] == "test_scope_used"


def test_fit_scope_metadata_passes_train_val_scope() -> None:
    df = pd.DataFrame(
        {
            "score_fit_split": ["train", "train"],
            "threshold_source_split": ["val", "val"],
        }
    )

    audit = check_fit_scope_metadata(df)

    assert not audit["has_leakage"]
