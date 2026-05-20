from __future__ import annotations

import pandas as pd

from scripts import audit_label_fidelity as audit


def _write_seizeit2_audit_fixture(
    root,
    *,
    processed_offsets: list[float],
    processed_event_onsets: list[float] | None = None,
    use_backslash_source_file: bool = False,
    write_recordings: bool = True,
) -> None:
    raw_root = root / "data/raw/seizeit2"
    event_dir = raw_root / "sub-P001" / "ses-01" / "eeg"
    event_dir.mkdir(parents=True)
    event_path = event_dir / "sub-P001_ses-01_task-szMonitoring_run-01_events.tsv"
    pd.DataFrame(
        {
            "onset": [60.0, 90.0, 120.0],
            "duration": [10.0, 5.0, 20.0],
            "eventType": ["sz_foc_a", "bckg", "seizure"],
            "dateTime": ["2000-01-01 00:00:00"] * 3,
            "recordingDuration": [300.0] * 3,
        }
    ).to_csv(event_path, sep="\t", index=False)

    processed_root = root / "data/processed/seizeit2"
    processed_root.mkdir(parents=True)
    base = pd.Timestamp("2000-01-01 00:00:00")
    recording_id = "sub-P001_ses-01_task-szMonitoring_run-01"
    source_file = str(event_path.relative_to(raw_root))
    if use_backslash_source_file:
        source_file = source_file.replace("/", "\\")
    event_onsets = processed_event_onsets if processed_event_onsets is not None else [60.0, 120.0]
    if len(event_onsets) != len(processed_offsets):
        raise ValueError("processed_event_onsets must match processed_offsets length")
    pd.DataFrame(
        {
            "patient_id": ["sub-P001"] * len(processed_offsets),
            "recording_id": [recording_id] * len(processed_offsets),
            "seizure_start": [base + pd.to_timedelta(offset, unit="s") for offset in processed_offsets],
            "seizure_end": [base + pd.to_timedelta(offset + 10.0, unit="s") for offset in processed_offsets],
            "seizure_type": ["sz_foc_a", "seizure"][: len(processed_offsets)],
            "center_id": [None] * len(processed_offsets),
            "source_dataset": ["seizeit2"] * len(processed_offsets),
            "event_source_file": [source_file] * len(processed_offsets),
            "event_onset_seconds": event_onsets,
            "recording_duration_seconds": [300.0] * len(processed_offsets),
        }
    ).to_parquet(processed_root / "events.parquet")
    if write_recordings:
        pd.DataFrame(
            {
                "patient_id": ["sub-P001"],
                "recording_id": [recording_id],
                "recording_start": [base],
                "recording_end": [base + pd.Timedelta(seconds=300)],
                "center_id": [None],
                "source_dataset": ["seizeit2"],
            }
        ).to_parquet(processed_root / "recordings.parquet")


def _run_seizeit2_audit(tmp_path, monkeypatch) -> list[str]:
    monkeypatch.setattr(audit, "REPO", tmp_path)
    audit.findings.clear()
    audit.audit_seizeit2()
    return list(audit.findings)


def test_seizeit2_onset_audit_passes_matching_relative_onsets(tmp_path, monkeypatch):
    _write_seizeit2_audit_fixture(tmp_path, processed_offsets=[60.0, 120.0])

    findings = _run_seizeit2_audit(tmp_path, monkeypatch)

    assert findings == []


def test_seizeit2_onset_audit_flags_count_preserving_timestamp_shift(tmp_path, monkeypatch):
    _write_seizeit2_audit_fixture(tmp_path, processed_offsets=[61.0, 120.0])

    findings = _run_seizeit2_audit(tmp_path, monkeypatch)

    assert not any("raw seizure count" in finding for finding in findings)
    assert any("relative onset mismatch" in finding for finding in findings)


def test_seizeit2_onset_audit_flags_unverifiable_missing_recording_start(tmp_path, monkeypatch):
    _write_seizeit2_audit_fixture(
        tmp_path,
        processed_offsets=[60.0, 120.0],
        write_recordings=False,
    )

    findings = _run_seizeit2_audit(tmp_path, monkeypatch)

    assert any("recordings.parquet missing" in finding for finding in findings)


def test_seizeit2_onset_audit_accepts_backslash_source_file(tmp_path, monkeypatch):
    _write_seizeit2_audit_fixture(
        tmp_path,
        processed_offsets=[60.0, 120.0],
        use_backslash_source_file=True,
    )

    findings = _run_seizeit2_audit(tmp_path, monkeypatch)

    assert findings == []


def test_seizeit2_onset_audit_checks_multiset_without_recordings(tmp_path, monkeypatch):
    _write_seizeit2_audit_fixture(
        tmp_path,
        processed_offsets=[60.0],
        processed_event_onsets=[60.0],
        write_recordings=False,
    )

    findings = _run_seizeit2_audit(tmp_path, monkeypatch)

    assert any("raw onset row(s) absent from events.parquet" in finding for finding in findings)
    assert any("recordings.parquet missing" in finding for finding in findings)


def test_seizeit2_onset_audit_flags_missing_raw_root(tmp_path, monkeypatch):
    processed_root = tmp_path / "data/processed/seizeit2"
    processed_root.mkdir(parents=True)
    pd.DataFrame(
        {
            "patient_id": [],
            "recording_id": [],
            "seizure_start": [],
            "event_source_file": [],
            "event_onset_seconds": [],
        }
    ).to_parquet(processed_root / "events.parquet")

    findings = _run_seizeit2_audit(tmp_path, monkeypatch)

    assert any("raw root missing" in finding for finding in findings)


def test_seizeit2_onset_audit_flags_missing_processed_events(tmp_path, monkeypatch):
    monkeypatch.setattr(audit, "REPO", tmp_path)
    audit.findings.clear()

    audit.audit_seizeit2()

    assert any("missing required parquet" in finding for finding in audit.findings)
