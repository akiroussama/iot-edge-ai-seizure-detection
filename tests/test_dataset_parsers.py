from __future__ import annotations

from io import BytesIO
from zipfile import ZipFile

import pandas as pd

from src.datasets.msg_loader import (
    assign_msg_events_to_recordings,
    discover_msg_metadata,
    discover_msg_recordings,
    inspect_msg_raw_layout,
    parse_msg_events,
    parse_msg_modality_availability,
    parse_msg_wearable_samples,
    prepare_mock_msg_tables,
)
from src.datasets.schemas import (
    validate_events,
    validate_metadata,
    validate_modality_availability,
    validate_recordings,
    validate_windows,
)
from src.datasets.seizeit2_loader import (
    discover_seizeit2_metadata,
    discover_seizeit2_modality_availability,
    discover_seizeit2_recordings,
    inspect_seizeit2_raw_layout,
    parse_bids_like_seizeit2_events,
    prepare_mock_seizeit2_tables,
    prepare_seizeit2_tables,
)
from src.utils.io import read_table


def test_parse_bids_like_seizeit2_events_from_mock_tree(tmp_path):
    event_dir = tmp_path / "sub-P001" / "ses-01" / "eeg"
    event_dir.mkdir(parents=True)
    events_path = event_dir / "sub-P001_ses-01_task-rest_events.tsv"
    pd.DataFrame(
        {
            "onset": [60.0, 120.0],
            "duration": [30.0, 10.0],
            "trial_type": ["seizure", "artifact"],
            "recording_start": ["2026-01-01 10:00:00", "2026-01-01 10:00:00"],
            "recording_end": ["2026-01-01 11:00:00", "2026-01-01 11:00:00"],
            "center_id": ["C001", "C001"],
        }
    ).to_csv(events_path, sep="\t", index=False)
    signal_path = event_dir / "sub-P001_ses-01_task-rest_ecg.csv"
    signal_path.write_text("time,ecg\n2026-01-01 10:00:00,0.1\n", encoding="utf-8")
    (event_dir / "sub-P001_ses-01_task-rest_ecg.json").write_text(
        '{"SamplingFrequency": 256, "ChannelCount": 1}',
        encoding="utf-8",
    )

    layout = inspect_seizeit2_raw_layout(tmp_path)
    events = parse_bids_like_seizeit2_events(tmp_path)
    metadata = discover_seizeit2_metadata(tmp_path)
    recordings = discover_seizeit2_recordings(tmp_path)
    availability = discover_seizeit2_modality_availability(tmp_path)

    assert layout["event_files"] == 1
    assert layout["subjects_discovered"] == 1
    assert len(events) == 1
    assert events.loc[0, "patient_id"] == "sub-P001"
    assert events.loc[0, "seizure_start"] == pd.Timestamp("2026-01-01 10:01:00")
    assert events.loc[0, "seizure_end"] == pd.Timestamp("2026-01-01 10:01:30")
    assert len(metadata) >= 1
    assert recordings.loc[0, "recording_end"] == pd.Timestamp("2026-01-01 11:00:00")
    assert availability.loc[0, "modality"] == "ecg"
    assert availability.loc[0, "sampling_rate"] == 256


def test_parse_bids_score_event_type_and_datetime_schema(tmp_path):
    event_dir = tmp_path / "sub-P001" / "ses-01" / "eeg"
    event_dir.mkdir(parents=True)
    events_path = event_dir / "sub-P001_ses-01_task-szMonitoring_run-01_events.tsv"
    pd.DataFrame(
        {
            "onset": [0.0, 300.0, 900.0],
            "duration": [300.0, 60.0, 120.0],
            "eventType": ["bckg", "sz_foc_a", "impd"],
            "dateTime": ["2026-01-01 10:00:00"] * 3,
            "recordingDuration": [1800.0] * 3,
        }
    ).to_csv(events_path, sep="\t", index=False)

    events = parse_bids_like_seizeit2_events(tmp_path)
    recordings = discover_seizeit2_recordings(tmp_path)

    assert len(events) == 1
    assert events.loc[0, "seizure_type"] == "sz_foc_a"
    assert events.loc[0, "seizure_start"] == pd.Timestamp("2026-01-01 10:05:00")
    assert events.loc[0, "seizure_end"] == pd.Timestamp("2026-01-01 10:06:00")
    assert events.loc[0, "event_onset_seconds"] == 300.0
    assert recordings.loc[0, "recording_end"] == pd.Timestamp("2026-01-01 10:30:00")


def test_seizeit2_discovery_ignores_bids_metadata_and_normalizes_modalities(tmp_path):
    tmp_path.joinpath("participants.tsv").write_text("participant_id\nsub-P001\n", encoding="utf-8")
    event_dir = tmp_path / "sub-P001" / "ses-01" / "mov"
    event_dir.mkdir(parents=True)
    signal_path = event_dir / "sub-P001_ses-01_task-szMonitoring_run-01_mov.edf"
    signal_path.write_text("", encoding="utf-8")
    signal_path.with_suffix(".json").write_text(
        '{"SamplingFrequency": 25, "MOVChannelCount": 12}',
        encoding="utf-8",
    )

    metadata = discover_seizeit2_metadata(tmp_path)
    availability = discover_seizeit2_modality_availability(tmp_path)

    assert set(metadata["patient_id"]) == {"sub-P001"}
    assert metadata.loc[0, "recording_id"] == "sub-P001_ses-01_task-szMonitoring_run-01"
    assert set(availability["modality"]) == {"acc", "gyr"}
    assert set(availability["recording_id"]) == {"sub-P001_ses-01_task-szMonitoring_run-01"}
    assert availability["notes"].str.contains("manual verification").all()


def test_prepare_seizeit2_tables_writes_discovered_real_mode_artifacts(tmp_path):
    raw = tmp_path / "raw"
    event_dir = raw / "sub-P001" / "ses-01" / "eeg"
    event_dir.mkdir(parents=True)
    pd.DataFrame(
        {
            "onset": [60.0],
            "duration": [30.0],
            "trial_type": ["seizure"],
            "recording_start": ["2026-01-01 10:00:00"],
            "recording_end": ["2026-01-01 11:00:00"],
        }
    ).to_csv(event_dir / "sub-P001_ses-01_task-rest_events.tsv", sep="\t", index=False)

    written = prepare_seizeit2_tables(raw, tmp_path / "processed")

    assert set(written) == {"metadata", "recordings", "events", "modality_availability"}
    validate_events(read_table(written["events"]))
    validate_recordings(read_table(written["recordings"]))


def test_parse_msg_events_and_zip_modality_manifest(tmp_path):
    pd.DataFrame(
        {
            "patient_id": ["MSG001"],
            "seizure_start": ["2026-01-02 03:00:00"],
            "seizure_end": ["2026-01-02 03:02:00"],
        }
    ).to_csv(tmp_path / "seizure_times.csv", index=False)
    with ZipFile(tmp_path / "MSG001.zip", "w") as zf:
        zf.writestr("hr.csv", "time,hr\n2026-01-01,70\n")
        zf.writestr("steps.csv", "time,steps\n2026-01-01,10\n")

    layout = inspect_msg_raw_layout(tmp_path)
    events = parse_msg_events(tmp_path)
    availability = parse_msg_modality_availability(tmp_path)
    samples = parse_msg_wearable_samples(tmp_path)

    assert layout["patient_zip_files"] == 1
    assert events.loc[0, "recording_id"] == "MSG001_longitudinal"
    assert set(availability.loc[availability["available"], "modality"]) == {"hr", "steps"}
    assert set(samples["modality"]) == {"hr", "steps"}
    assert samples["value"].tolist() == [70, 10]


def test_parse_msg_nested_empatica_zip_manifest_and_recordings(tmp_path):
    nested_buffer = BytesIO()
    with ZipFile(nested_buffer, "w") as nested:
        nested.writestr("HR.csv", "1760055000.0\n1.0\n70\n71\n72\n")
        nested.writestr("ACC.csv", "1760054990.0,1760054990.0,1760054990.0\n32.0,32.0,32.0\n1,2,3\n")
        nested.writestr("info.txt", "Empatica archive")
    with ZipFile(tmp_path / "Mayo_1869.zip", "w") as outer:
        outer.writestr("Mayo_1869/1869.txt", "1760055060\n")
        outer.writestr("Mayo_1869/1760055000_A000.zip", nested_buffer.getvalue())

    layout = inspect_msg_raw_layout(tmp_path)
    events = parse_msg_events(tmp_path)
    recordings = discover_msg_recordings(tmp_path)
    metadata = discover_msg_metadata(tmp_path)
    availability = parse_msg_modality_availability(tmp_path)

    assert layout["complete_patient_zip_files"] == 1
    assert layout["seizure_txt_files_in_zips"] == ["Mayo_1869.zip:Mayo_1869/1869.txt"]
    assert events.loc[0, "patient_id"] == "1869"
    assert recordings.loc[0, "recording_id"] == "1869_1760055000_A000"
    assert recordings.loc[0, "recording_start"] == pd.Timestamp("2025-10-10 00:10:00")
    assert recordings.loc[0, "recording_end"] == pd.Timestamp("2025-10-10 00:10:03")
    assert metadata.loc[0, "patient_id"] == "1869"
    assert set(availability.loc[availability["available"], "modality"]) == {"acc", "hr"}


def test_assign_msg_events_to_matching_recording_segment():
    events = pd.DataFrame(
        {
            "patient_id": ["1869", "1869"],
            "recording_id": ["1869_longitudinal", "1869_longitudinal"],
            "seizure_start": [pd.Timestamp("2025-10-10 00:10:01"), pd.Timestamp("2025-10-11")],
            "seizure_end": [pd.Timestamp("2025-10-10 00:11:01"), pd.Timestamp("2025-10-11 00:01:00")],
        }
    )
    recordings = pd.DataFrame(
        {
            "patient_id": ["1869"],
            "recording_id": ["1869_segment_a"],
            "recording_start": [pd.Timestamp("2025-10-10 00:10:00")],
            "recording_end": [pd.Timestamp("2025-10-10 00:20:00")],
            "center_id": [None],
            "source_dataset": ["my_seizure_gauge"],
        }
    )

    assigned = assign_msg_events_to_recordings(events, recordings)

    assert assigned.loc[0, "recording_id"] == "1869_segment_a"
    assert assigned.loc[0, "recording_match_status"] == "matched"
    assert assigned.loc[1, "recording_id"] == "1869_longitudinal"
    assert assigned.loc[1, "recording_match_status"] == "unmatched"


def test_parse_msg_zenodo_seizure_times_only_txt(tmp_path):
    seizure_dir = tmp_path / "SeizureTimesOnly"
    seizure_dir.mkdir()
    (seizure_dir / "1942.txt").write_text("1760055000\n1760141400\n", encoding="utf-8")

    layout = inspect_msg_raw_layout(tmp_path)
    events = parse_msg_events(tmp_path)

    assert layout["seizure_txt_files"] == ["SeizureTimesOnly/1942.txt"]
    assert len(events) == 2
    assert events.loc[0, "patient_id"] == "1942"
    assert events.loc[0, "recording_id"] == "1942_longitudinal"
    assert bool(events.loc[0, "seizure_end_imputed"]) is True
    assert (
        events.loc[0, "seizure_end"] - events.loc[0, "seizure_start"]
    ) == pd.Timedelta(seconds=60)


def test_prepare_mock_seizeit2_tables_writes_standard_artifacts(tmp_path):
    written = prepare_mock_seizeit2_tables(tmp_path)

    assert set(written) == {
        "metadata",
        "recordings",
        "events",
        "windows",
        "modality_availability",
    }
    validate_metadata(read_table(written["metadata"]))
    validate_recordings(read_table(written["recordings"]))
    validate_events(read_table(written["events"]))
    validate_windows(read_table(written["windows"]))
    validate_modality_availability(read_table(written["modality_availability"]))


def test_prepare_mock_msg_tables_writes_standard_artifacts(tmp_path):
    written = prepare_mock_msg_tables(tmp_path)

    assert set(written) == {
        "metadata",
        "recordings",
        "events",
        "windows",
        "modality_availability",
        "samples",
    }
    validate_metadata(read_table(written["metadata"]))
    validate_recordings(read_table(written["recordings"]))
    validate_events(read_table(written["events"]))
    validate_windows(read_table(written["windows"]))
    validate_modality_availability(read_table(written["modality_availability"]))
    assert not read_table(written["samples"]).empty
