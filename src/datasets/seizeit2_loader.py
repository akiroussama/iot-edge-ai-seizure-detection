from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src.datasets.base import BaseDataset
from src.datasets.schemas import (
    validate_events,
    validate_metadata,
    validate_modality_availability,
    validate_recordings,
    validate_windows,
)
from src.preprocessing.windowing import generate_fixed_windows
from src.utils.io import read_table, write_table

SIGNAL_SUFFIXES = (".edf", ".bdf", ".vhdr", ".set", ".csv", ".tsv")
SEIZURE_EVENT_PATTERNS = ("seizure", "ictal", "sz")
NON_SEIZURE_EVENT_TYPES = {"bckg", "background", "impd", "artifact", "artefact", "n/a", "nan", ""}
BIDS_METADATA_FILENAMES = {
    "participants.tsv",
    "participants.json",
    "dataset_description.json",
    "events.json",
    "README",
    "CHANGES",
}


class SeizeIT2Dataset(BaseDataset):
    """Minimal SeizeIT2 table loader.

    This loader intentionally expects pre-extracted tabular files in v0.1. The official SeizeIT2
    repository/loaders can be wired here once raw data are downloaded. The clinical labeling and
    metrics code remain dataset-agnostic.
    """

    def _optional_table(self, name: str) -> pd.DataFrame:
        for suffix in (".parquet", ".csv"):
            path = self.processed_root / f"{name}{suffix}"
            if path.exists():
                return read_table(path)
        return pd.DataFrame()

    def load_metadata(self) -> pd.DataFrame:
        return self._optional_table("metadata")

    def load_events(self) -> pd.DataFrame:
        return self._optional_table("events")

    def load_windows(self) -> pd.DataFrame:
        return self._optional_table("windows")

    def load_modality_availability(self) -> pd.DataFrame:
        return self._optional_table("modality_availability")


def inspect_seizeit2_raw_layout(raw_root: str | Path) -> dict[str, object]:
    """Inspect a BIDS/OpenNeuro-like SeizeIT2 tree without parsing raw signals."""
    root = Path(raw_root)
    if not root.exists():
        return {
            "raw_root": str(root),
            "exists": False,
            "event_files": 0,
            "signal_like_files": 0,
            "example_event_files": [],
            "next_action": "Create or mount data/raw/seizeit2 before running real preparation.",
        }
    event_files = sorted(root.rglob("*events.tsv"))
    sidecar_files = sorted(root.rglob("*.json"))
    channel_files = sorted(root.rglob("*channels.tsv"))
    subjects = sorted(
        {part for path in root.rglob("*") for part in path.relative_to(root).parent.parts if part.startswith("sub-")}
    )
    sessions = sorted(
        {part for path in root.rglob("*") for part in path.relative_to(root).parent.parts if part.startswith("ses-")}
    )
    signal_files = sorted(
        p
        for suffix in ("*.edf", "*.bdf", "*.vhdr", "*.set", "*.csv", "*.tsv")
        for p in root.rglob(suffix)
        if _is_supported_signal_file(p)
    )
    participants = root / "participants.tsv"
    return {
        "raw_root": str(root),
        "exists": True,
        "participants_tsv": participants.exists(),
        "subjects_discovered": len(subjects),
        "sessions_discovered": len(sessions),
        "event_files": len(event_files),
        "sidecar_json_files": len(sidecar_files),
        "channel_files": len(channel_files),
        "signal_like_files": len(signal_files),
        "example_event_files": [str(p.relative_to(root)) for p in event_files[:5]],
        "next_action": (
            "Verify event onsets against raw recording starts, then run prepare_seizeit2.py. "
            "Raw waveform decoding remains dataset-version specific."
        ),
    }


def _patient_id_from_path(root: Path, path: Path, fallback: str | None = None) -> str:
    rel_parts = path.relative_to(root).parts
    patient_id = next((part for part in rel_parts if part.startswith("sub-")), None)
    return str(patient_id or fallback or path.parent.name)


def _recording_id_from_path(path: Path) -> str:
    stem = path.name
    for suffix in ("_events.tsv", "_channels.tsv"):
        if stem.endswith(suffix):
            stem = stem.removesuffix(suffix)
            break
    else:
        stem = path.stem
    for modality_suffix in ("_eeg", "_ecg", "_emg", "_mov", "_acc", "_gyr", "_gyro"):
        if stem.endswith(modality_suffix):
            return stem.removesuffix(modality_suffix)
    return stem


def _is_supported_signal_file(path: Path) -> bool:
    if path.name in BIDS_METADATA_FILENAMES:
        return False
    if path.name.endswith("_events.tsv") or path.name.endswith("_channels.tsv"):
        return False
    return path.suffix.lower() in SIGNAL_SUFFIXES


def _infer_modalities(path: Path) -> list[str]:
    text = str(path).lower()
    if "ecg" in text or "ekg" in text:
        return ["ecg"]
    if "emg" in text:
        return ["emg"]
    if "accelerometer" in text or "_acc" in text or "acc_" in text:
        return ["acc"]
    if "gyroscope" in text or "_gyr" in text or "gyro" in text:
        return ["gyr"]
    if "mov" in text:
        return ["acc", "gyr"]
    if "eeg" in text or "bte" in text:
        return ["bte_eeg"]
    return []


def _read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _matching_sidecar(path: Path) -> dict:
    candidates = [path.with_suffix(".json")]
    if "_" in path.name:
        candidates.append(path.with_name(path.name.split("_")[0] + ".json"))
    for candidate in candidates:
        if candidate.exists():
            return _read_json(candidate)
    return {}


def _matching_channels(path: Path) -> pd.DataFrame:
    candidates = [path.with_name(path.stem + "_channels.tsv")]
    for candidate in candidates:
        if candidate.exists():
            return pd.read_csv(candidate, sep="\t")
    return pd.DataFrame()


def _event_type_column(table: pd.DataFrame) -> str | None:
    return next((col for col in ("trial_type", "event_type", "eventType") if col in table.columns), None)


def _is_seizure_event_type(value: object) -> bool:
    event_type = str(value).strip().lower()
    if event_type in NON_SEIZURE_EVENT_TYPES:
        return False
    return any(pattern in event_type for pattern in SEIZURE_EVENT_PATTERNS)


def _parse_recording_start(row: pd.Series, table: pd.DataFrame, path: Path) -> pd.Timestamp:
    if "recording_start" in table.columns:
        return pd.to_datetime(row["recording_start"])
    if "dateTime" in table.columns:
        return pd.to_datetime(row["dateTime"])
    raise ValueError(f"{path} needs recording_start or dateTime with onset/duration events")


def _parse_recording_duration(row: pd.Series, table: pd.DataFrame) -> float | None:
    if "recordingDuration" in table.columns and pd.notna(row["recordingDuration"]):
        return float(row["recordingDuration"])
    if "recording_duration" in table.columns and pd.notna(row["recording_duration"]):
        return float(row["recording_duration"])
    return None


def discover_seizeit2_modality_availability(raw_root: str | Path) -> pd.DataFrame:
    """Create a modality manifest from supported BIDS-like filenames/sidecars.

    This is a discovery manifest, not waveform decoding. Missing sampling rate or channel count
    stays null instead of being invented.
    """
    root = Path(raw_root)
    if not root.exists():
        raise FileNotFoundError(f"SeizeIT2 raw root does not exist: {root}")
    rows = []
    for path in sorted(root.rglob("*")):
        if not _is_supported_signal_file(path):
            continue
        modalities = _infer_modalities(path)
        if not modalities:
            continue
        sidecar = _matching_sidecar(path)
        channels = _matching_channels(path)
        sampling_rate = sidecar.get("SamplingFrequency") or sidecar.get("sampling_rate")
        for modality in modalities:
            modality_channel_key = {
                "bte_eeg": "EEGChannelCount",
                "ecg": "ECGChannelCount",
                "emg": "EMGChannelCount",
                "acc": "ACCChannelCount",
                "gyr": "GYRChannelCount",
            }.get(modality)
            channel_count = (
                len(channels)
                if not channels.empty
                else sidecar.get(modality_channel_key) or sidecar.get("ChannelCount")
            )
            notes = str(path.relative_to(root))
            if modality in {"acc", "gyr"} and "MOVChannelCount" in sidecar:
                notes += "; modality inferred from MOV sidecar, channel split requires manual verification"
            rows.append(
                {
                    "patient_id": _patient_id_from_path(root, path),
                    "recording_id": _recording_id_from_path(path),
                    "modality": modality,
                    "available": True,
                    "sampling_rate": sampling_rate,
                    "channel_count": channel_count,
                    "notes": notes,
                }
            )
    availability = pd.DataFrame(
        rows,
        columns=[
            "patient_id",
            "recording_id",
            "modality",
            "available",
            "sampling_rate",
            "channel_count",
            "notes",
        ],
    )
    validate_modality_availability(availability, allow_empty=True)
    return availability


def discover_seizeit2_metadata(raw_root: str | Path) -> pd.DataFrame:
    """Discover patient/recording identifiers from event and signal files."""
    root = Path(raw_root)
    if not root.exists():
        raise FileNotFoundError(f"SeizeIT2 raw root does not exist: {root}")
    rows = []
    files = [
        path
        for path in sorted(root.rglob("*"))
        if path.name.endswith("_events.tsv")
        or _is_supported_signal_file(path)
    ]
    for path in files:
        rows.append(
            {
                "patient_id": _patient_id_from_path(root, path),
                "recording_id": _recording_id_from_path(path),
                "center_id": None,
                "source_dataset": "seizeit2",
            }
        )
    metadata = pd.DataFrame(
        rows,
        columns=["patient_id", "recording_id", "center_id", "source_dataset"],
    ).drop_duplicates().reset_index(drop=True)
    validate_metadata(metadata, allow_empty=True)
    return metadata


def discover_seizeit2_recordings(raw_root: str | Path) -> pd.DataFrame:
    """Discover recording intervals only when event files explicitly provide them."""
    root = Path(raw_root)
    if not root.exists():
        raise FileNotFoundError(f"SeizeIT2 raw root does not exist: {root}")
    rows = []
    for path in sorted(root.rglob("*events.tsv")):
        table = pd.read_csv(path, sep="\t")
        patient_id = _patient_id_from_path(
            root,
            path,
            fallback=table["patient_id"].iloc[0] if "patient_id" in table.columns else None,
        )
        if {"recording_start", "recording_end"}.issubset(table.columns):
            recording_start = pd.to_datetime(table["recording_start"].iloc[0])
            recording_end = pd.to_datetime(table["recording_end"].iloc[0])
        elif {"dateTime", "recordingDuration"}.issubset(table.columns):
            recording_start = pd.to_datetime(table["dateTime"].iloc[0])
            recording_end = recording_start + pd.to_timedelta(
                float(table["recordingDuration"].iloc[0]), unit="s"
            )
        else:
            continue
        rows.append(
            {
                "patient_id": patient_id,
                "recording_id": _recording_id_from_path(path),
                "recording_start": recording_start,
                "recording_end": recording_end,
                "center_id": table["center_id"].iloc[0] if "center_id" in table.columns else None,
                "source_dataset": "seizeit2",
            }
        )
    recordings = pd.DataFrame(
        rows,
        columns=[
            "patient_id",
            "recording_id",
            "recording_start",
            "recording_end",
            "center_id",
            "source_dataset",
        ],
    )
    validate_recordings(recordings, allow_empty=True)
    return recordings


def parse_bids_like_seizeit2_events(raw_root: str | Path) -> pd.DataFrame:
    """Parse seizure events from tiny BIDS-like ``*_events.tsv`` files.

    Supported schemas are canonical ``seizure_start``/``seizure_end`` columns and BIDS-score
    style ``onset``/``duration`` rows with either ``recording_start`` or ``dateTime``. Non-seizure
    background rows such as ``bckg`` are ignored. This function does not decode waveform files.
    """
    root = Path(raw_root)
    rows: list[dict] = []
    for path in sorted(root.rglob("*events.tsv")):
        table = pd.read_csv(path, sep="\t")
        patient_id = next((part for part in path.parts if part.startswith("sub-")), None)
        if patient_id is None:
            patient_id = table["patient_id"].iloc[0] if "patient_id" in table.columns else path.parent.name
        recording_id = path.name.removesuffix("_events.tsv")

        event_col = _event_type_column(table)
        if event_col:
            mask = table[event_col].map(_is_seizure_event_type)
            table = table.loc[mask]
        if table.empty:
            continue

        for _, row in table.iterrows():
            if {"seizure_start", "seizure_end"}.issubset(table.columns):
                seizure_start = pd.to_datetime(row["seizure_start"])
                seizure_end = pd.to_datetime(row["seizure_end"])
            elif {"onset", "duration"}.issubset(table.columns):
                rec_start = _parse_recording_start(row, table, path)
                seizure_start = rec_start + pd.to_timedelta(float(row["onset"]), unit="s")
                seizure_end = seizure_start + pd.to_timedelta(float(row["duration"]), unit="s")
            else:
                raise ValueError(
                    f"{path} needs seizure_start/seizure_end or onset/duration with recording_start/dateTime"
                )
            rows.append(
                {
                    "patient_id": str(patient_id),
                    "recording_id": recording_id,
                    "seizure_start": seizure_start,
                    "seizure_end": seizure_end,
                    "seizure_type": row.get(event_col) if event_col else None,
                    "center_id": row.get("center_id"),
                    "source_dataset": "seizeit2",
                    "event_source_file": str(path.relative_to(root)),
                    "event_onset_seconds": float(row["onset"]) if "onset" in table.columns else None,
                    "recording_duration_seconds": _parse_recording_duration(row, table),
                }
            )
    events = pd.DataFrame(
        rows,
        columns=[
            "patient_id",
            "recording_id",
            "seizure_start",
            "seizure_end",
            "seizure_type",
            "center_id",
            "source_dataset",
            "event_source_file",
            "event_onset_seconds",
            "recording_duration_seconds",
        ],
    )
    validate_events(events, allow_empty=True)
    return events


def prepare_seizeit2_tables(raw_root: str | Path, processed_root: str | Path) -> dict[str, Path]:
    """Write canonical SeizeIT2 event tables from supported metadata files."""
    root = Path(raw_root)
    if not root.exists():
        raise FileNotFoundError(f"SeizeIT2 raw root does not exist: {root}")
    processed = Path(processed_root)
    processed.mkdir(parents=True, exist_ok=True)
    metadata = discover_seizeit2_metadata(raw_root)
    recordings = discover_seizeit2_recordings(raw_root)
    events = parse_bids_like_seizeit2_events(raw_root)
    availability = discover_seizeit2_modality_availability(raw_root)
    validate_events(events, allow_empty=False)
    tables = {
        "metadata": metadata,
        "recordings": recordings,
        "events": events,
        "modality_availability": availability,
    }
    written = {}
    for name, table in tables.items():
        path = processed / f"{name}.parquet"
        write_table(table, path)
        written[name] = path
    return written


def make_mock_seizeit2_artifacts() -> dict[str, pd.DataFrame]:
    """Create deterministic SeizeIT2-shaped benchmark artifacts for dry runs."""
    base = pd.Timestamp("2026-01-01 10:00:00")
    metadata = pd.DataFrame(
        [
            {
                "patient_id": "P001",
                "recording_id": "R001",
                "center_id": "C001",
                "source_dataset": "seizeit2_mock",
            }
        ]
    )
    recordings = pd.DataFrame(
        [
            {
                "patient_id": "P001",
                "recording_id": "R001",
                "recording_start": base,
                "recording_end": base + pd.Timedelta(minutes=90),
                "center_id": "C001",
                "source_dataset": "seizeit2_mock",
            }
        ]
    )
    events = pd.DataFrame(
        [
            {
                "patient_id": "P001",
                "recording_id": "R001",
                "seizure_start": base + pd.Timedelta(minutes=40),
                "seizure_end": base + pd.Timedelta(minutes=42),
                "seizure_type": "focal_mock",
                "center_id": "C001",
                "source_dataset": "seizeit2_mock",
            }
        ]
    )
    windows = generate_fixed_windows(recordings, window_duration="1min", stride="1min")
    availability = pd.DataFrame(
        [
            {
                "patient_id": "P001",
                "recording_id": "R001",
                "modality": modality,
                "available": True,
                "sampling_rate": sampling_rate,
                "channel_count": channel_count,
                "notes": "deterministic mock manifest; not real SeizeIT2 data",
            }
            for modality, sampling_rate, channel_count in [
                ("bte_eeg", 256.0, 2),
                ("ecg", 256.0, 1),
                ("emg", 256.0, 1),
                ("acc", 50.0, 3),
                ("gyr", 50.0, 3),
            ]
        ]
    )
    validate_metadata(metadata)
    validate_recordings(recordings)
    validate_events(events)
    validate_windows(windows)
    validate_modality_availability(availability)
    return {
        "metadata": metadata,
        "recordings": recordings,
        "events": events,
        "windows": windows,
        "modality_availability": availability,
    }


def prepare_mock_seizeit2_tables(processed_root: str | Path) -> dict[str, Path]:
    processed = Path(processed_root)
    processed.mkdir(parents=True, exist_ok=True)
    artifacts = make_mock_seizeit2_artifacts()
    written = {}
    for name, table in artifacts.items():
        path = processed / f"{name}.parquet"
        write_table(table, path)
        written[name] = path
    return written


def make_synthetic_seizeit2_tables() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Create a tiny deterministic SeizeIT2-like synthetic dataset for demos/tests."""
    base = pd.Timestamp("2026-01-01 10:00:00")
    windows = []
    for i in range(90):
        start = base + pd.Timedelta(minutes=i)
        windows.append(
            {
                "patient_id": "P001",
                "recording_id": "R001",
                "center_id": "C001",
                "window_start": start,
                "window_end": start + pd.Timedelta(minutes=1),
            }
        )
    events = pd.DataFrame(
        [
            {
                "patient_id": "P001",
                "recording_id": "R001",
                "seizure_start": base + pd.Timedelta(minutes=40),
                "seizure_end": base + pd.Timedelta(minutes=42),
            }
        ]
    )
    metadata = pd.DataFrame([{"patient_id": "P001", "recording_id": "R001", "center_id": "C001"}])
    return metadata, pd.DataFrame(windows), events
