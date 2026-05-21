from __future__ import annotations

import json
import subprocess
import sys

import pandas as pd
import pytest

from src.reports.seizeit2_benchmark_track import (
    apply_official_seizeit2_splits,
    build_seizeit2_full_track_matrix,
    seizeit2_count_summary,
    seizeit2_full_track_markdown,
)
from src.utils.io import read_table, write_table


def _seizeit2_tables() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    recordings = pd.DataFrame(
        {
            "patient_id": ["sub-001", "sub-002", "sub-003"],
            "recording_id": ["r1", "r2", "r3"],
            "recording_start": pd.date_range("2026-01-01", periods=3, freq="D"),
            "recording_end": pd.date_range("2026-01-01 01:00", periods=3, freq="D"),
            "source_dataset": ["seizeit2"] * 3,
        }
    )
    events = pd.DataFrame(
        {
            "patient_id": ["sub-001", "sub-002"],
            "recording_id": ["r1", "r2"],
            "seizure_start": [pd.Timestamp("2026-01-01 00:30"), pd.Timestamp("2026-01-02 00:30")],
            "seizure_end": [pd.Timestamp("2026-01-01 00:31"), pd.Timestamp("2026-01-02 00:31")],
            "source_dataset": ["seizeit2"] * 2,
        }
    )
    availability = pd.DataFrame(
        [
            {"patient_id": "sub-001", "recording_id": "r1", "modality": "ecg", "available": True},
            {"patient_id": "sub-001", "recording_id": "r1", "modality": "acc", "available": True},
            {"patient_id": "sub-002", "recording_id": "r2", "modality": "bte_eeg", "available": True},
            {"patient_id": "sub-002", "recording_id": "r2", "modality": "ecg", "available": True},
            {"patient_id": "sub-003", "recording_id": "r3", "modality": "acc", "available": True},
        ]
    )
    availability["source_dataset"] = "seizeit2"
    windows = pd.DataFrame(
        {
            "patient_id": ["sub-001", "sub-001", "sub-002", "sub-003"],
            "recording_id": ["r1", "r1", "r2", "r3"],
            "window_start": pd.date_range("2026-01-01", periods=4, freq="h"),
            "window_end": pd.date_range("2026-01-01 00:30", periods=4, freq="h"),
            "source_dataset": ["seizeit2"] * 4,
        }
    )
    splits = pd.DataFrame(
        {
            "patient_id": ["sub-001", "sub-002", "sub-003"],
            "recording_id": ["r1", "r2", "r3"],
            "split": ["train", "val", "test"],
        }
    )
    return recordings, events, availability, windows, splits


def test_apply_official_splits_fails_closed_on_missing_rows() -> None:
    recordings, _, _, _, splits = _seizeit2_tables()

    with pytest.raises(ValueError, match="does not cover all rows"):
        apply_official_seizeit2_splits(recordings, splits.iloc[:2])


def test_apply_official_splits_fails_on_duplicate_keys() -> None:
    recordings, _, _, _, splits = _seizeit2_tables()
    duplicated = pd.concat([splits, splits.iloc[[0]]], ignore_index=True)

    with pytest.raises(ValueError, match="duplicate keys"):
        apply_official_seizeit2_splits(recordings, duplicated)


def test_full_track_matrix_separates_tasks_modalities_and_splits() -> None:
    recordings, events, availability, windows, splits = _seizeit2_tables()

    track = build_seizeit2_full_track_matrix(
        recordings,
        events,
        availability,
        windows_df=windows,
        official_splits_df=splits,
        result_status="synthetic_smoke_test_not_citable",
        citation_status="synthetic_not_citable",
    )

    assert set(track["dataset"]) == {"seizeit2"}
    assert {"detection", "early_warning", "forecasting"} == set(track["task_type"])
    assert {"ecg", "acc", "bte_eeg", "multimodal"} == set(track["modality_track"])
    assert {"train", "val", "test"} == set(track["split_name"])
    train_multimodal = track.loc[
        track["split_name"].eq("train")
        & track["modality_track"].eq("multimodal")
        & track["task_name"].eq("ictal_detection")
    ].iloc[0]
    assert bool(train_multimodal["track_ready"]) is True
    assert train_multimodal["sample_rows"] == 2
    assert set(track["official_split_status"]) == {"official_manifest_applied"}


def test_full_track_rejects_msg_source_dataset() -> None:
    recordings, events, availability, _, splits = _seizeit2_tables()
    recordings.loc[0, "source_dataset"] = "my_seizure_gauge"

    with pytest.raises(ValueError, match="non-SeizeIT2"):
        build_seizeit2_full_track_matrix(
            recordings,
            events,
            availability,
            official_splits_df=splits,
        )


def test_count_summary_compares_expected_counts_and_markdown_disclaims_results() -> None:
    recordings, events, availability, windows, splits = _seizeit2_tables()
    track = build_seizeit2_full_track_matrix(
        recordings,
        events,
        availability,
        windows_df=windows,
        official_splits_df=splits,
    )

    counts = seizeit2_count_summary(
        recordings,
        events,
        availability,
        windows_df=windows,
        expected_counts={"patients": 3, "recordings": 99, "events": 2},
    )
    text = seizeit2_full_track_markdown(track, counts)

    statuses = dict(zip(counts["metric"], counts["count_status"], strict=True))
    assert statuses["patients"] == "matches_expected_count"
    assert statuses["recordings"] == "count_mismatch_document_filter_or_parser"
    assert "not a model result" in text
    assert "must not be mixed with MSG" in text


def test_make_seizeit2_full_track_cli_writes_outputs(tmp_path) -> None:
    recordings, events, availability, windows, splits = _seizeit2_tables()
    recordings_path = tmp_path / "recordings.csv"
    events_path = tmp_path / "events.csv"
    availability_path = tmp_path / "availability.csv"
    windows_path = tmp_path / "windows.csv"
    splits_path = tmp_path / "splits.csv"
    expected_path = tmp_path / "expected.json"
    out_csv = tmp_path / "track.csv"
    out_counts = tmp_path / "counts.csv"
    out_md = tmp_path / "track.md"
    write_table(recordings, recordings_path)
    write_table(events, events_path)
    write_table(availability, availability_path)
    write_table(windows, windows_path)
    write_table(splits, splits_path)
    expected_path.write_text(json.dumps({"patients": 3, "recordings": 3, "events": 2}), encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "scripts/make_seizeit2_full_track.py",
            "--recordings",
            str(recordings_path),
            "--events",
            str(events_path),
            "--modality-availability",
            str(availability_path),
            "--windows",
            str(windows_path),
            "--official-splits",
            str(splits_path),
            "--expected-counts-json",
            str(expected_path),
            "--out-csv",
            str(out_csv),
            "--out-counts-csv",
            str(out_counts),
            "--out-md",
            str(out_md),
            "--result-status",
            "synthetic_smoke_test_not_citable",
            "--citation-status",
            "synthetic_not_citable",
        ],
        check=True,
        text=True,
        capture_output=True,
    )

    track = read_table(out_csv)
    counts = read_table(out_counts)
    assert '"official_splits": true' in result.stdout
    assert track["benchmark_family"].eq("seizeit2_full_track").all()
    assert counts["count_status"].eq("matches_expected_count").sum() == 3
    assert "benchmark-track readiness report" in out_md.read_text(encoding="utf-8")


def test_cli_requires_gate_c_for_citable(tmp_path) -> None:
    recordings, events, availability, _, _ = _seizeit2_tables()
    recordings_path = tmp_path / "recordings.csv"
    events_path = tmp_path / "events.csv"
    availability_path = tmp_path / "availability.csv"
    write_table(recordings, recordings_path)
    write_table(events, events_path)
    write_table(availability, availability_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/make_seizeit2_full_track.py",
            "--recordings",
            str(recordings_path),
            "--events",
            str(events_path),
            "--modality-availability",
            str(availability_path),
            "--out-csv",
            str(tmp_path / "track.csv"),
            "--out-counts-csv",
            str(tmp_path / "counts.csv"),
            "--out-md",
            str(tmp_path / "track.md"),
            "--citation-status",
            "citable_after_gate_c",
            "--gate-c-status",
            "not_started",
        ],
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode != 0
    assert "gate-c-status passed" in result.stderr
