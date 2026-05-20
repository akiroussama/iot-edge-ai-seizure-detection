from __future__ import annotations

from io import BytesIO
from pathlib import Path
from zipfile import BadZipFile, ZipFile

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

SAMPLE_COLUMNS = ["patient_id", "recording_id", "timestamp", "modality", "value", "source_file"]
DEFAULT_ONSET_ONLY_SEIZURE_DURATION_SECONDS = 60
MSG_DUPLICATE_RECORDING_POLICIES = {"error", "drop_exact"}
EMPATICA_MODALITY_FILES = {
    "HR.csv": "hr",
    "ACC.csv": "acc",
    "EDA.csv": "eda",
    "BVP.csv": "bvp",
    "TEMP.csv": "temp",
    "IBI.csv": "ibi",
}


class MySeizureGaugeDataset(BaseDataset):
    """Minimal My Seizure Gauge table loader for HR/steps long-horizon forecasting."""

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


def inspect_msg_raw_layout(raw_root: str | Path) -> dict[str, object]:
    """Inspect expected My Seizure Gauge files without extracting streams."""
    root = Path(raw_root)
    if not root.exists():
        return {
            "raw_root": str(root),
            "exists": False,
            "patient_zip_files": 0,
            "seizure_time_files": [],
            "example_zip_files": [],
            "next_action": "Create or mount data/raw/msg before running real preparation.",
        }
    zip_files = sorted(root.glob("*.zip"))
    complete_zip_files = []
    incomplete_zip_files = []
    for path in zip_files:
        if _is_valid_zip(path):
            complete_zip_files.append(path)
        else:
            incomplete_zip_files.append(path)
    seizure_files = [p for p in (root / "seizure_times.csv", root / "seizures.csv") if p.exists()]
    seizure_txt_files = sorted(root.rglob("*.txt"))
    seizure_zip_files = [
        f"{path.name}:{name}"
        for path in complete_zip_files
        for name in _safe_zip_names(path)
        if name.lower().endswith(".txt") and _looks_like_msg_seizure_text(name)
    ]
    return {
        "raw_root": str(root),
        "exists": True,
        "patient_zip_files": len(zip_files),
        "complete_patient_zip_files": len(complete_zip_files),
        "incomplete_patient_zip_files": [p.name for p in incomplete_zip_files],
        "seizure_time_files": [p.name for p in seizure_files],
        "seizure_txt_files": [p.relative_to(root).as_posix() for p in seizure_txt_files[:20]],
        "seizure_txt_files_in_zips": seizure_zip_files[:20],
        "example_zip_files": [p.name for p in zip_files[:5]],
        "next_action": (
            "Verify seizure times against chronic EEG annotations, then extract HR/steps "
            "streams into canonical samples before windowing."
        ),
    }


def _is_valid_zip(path: Path) -> bool:
    try:
        with ZipFile(path) as zf:
            zf.infolist()
            return True
    except (BadZipFile, FileNotFoundError, OSError):
        return False


def _safe_zip_names(path: Path) -> list[str]:
    try:
        with ZipFile(path) as zf:
            return zf.namelist()
    except (BadZipFile, FileNotFoundError, OSError):
        return []


def _patient_id_from_seizure_text_path(path_name: str) -> str:
    return Path(path_name).stem.removeprefix("Mayo_")


def _patient_id_from_msg_zip(path: Path) -> str:
    return path.stem.removeprefix("Mayo_")


def _looks_like_msg_seizure_text(path_name: str) -> bool:
    path = Path(path_name)
    stem = path.stem.removeprefix("Mayo_")
    parent = path.parent.name.removeprefix("Mayo_")
    if "info" in stem.lower() or "tags" in stem.lower():
        return False
    return stem.isdigit() or parent.isdigit() or "seizure" in str(path).lower()


def _parse_unix_timestamp_lines(lines: list[str], source_file: str) -> pd.DataFrame:
    rows = []
    patient_id = _patient_id_from_seizure_text_path(source_file)
    for line_number, line in enumerate(lines, start=1):
        value = line.strip()
        if not value:
            continue
        try:
            timestamp = float(value)
        except ValueError as exc:
            raise ValueError(f"{source_file}:{line_number} is not a Unix timestamp: {value!r}") from exc
        seizure_start = pd.to_datetime(timestamp, unit="s", utc=True).tz_convert(None)
        rows.append(
            {
                "patient_id": patient_id,
                "recording_id": f"{patient_id}_longitudinal",
                "seizure_start": seizure_start,
                "seizure_end": seizure_start
                + pd.to_timedelta(DEFAULT_ONSET_ONLY_SEIZURE_DURATION_SECONDS, unit="s"),
                "source_dataset": "my_seizure_gauge",
                "source_file": source_file,
                "seizure_end_imputed": True,
                "imputed_duration_seconds": DEFAULT_ONSET_ONLY_SEIZURE_DURATION_SECONDS,
            }
        )
    return pd.DataFrame(rows)


def _parse_msg_onset_only_txt_events(root: Path) -> pd.DataFrame:
    frames = []
    for path in sorted(root.rglob("*.txt")):
        if not _looks_like_msg_seizure_text(str(path.relative_to(root))):
            continue
        frames.append(
            _parse_unix_timestamp_lines(
                path.read_text(encoding="utf-8").splitlines(),
                str(path.relative_to(root)),
            )
        )
    for zip_path in sorted(root.glob("*.zip")):
        if not _is_valid_zip(zip_path):
            continue
        with ZipFile(zip_path) as zf:
            for name in sorted(zf.namelist()):
                if not name.lower().endswith(".txt") or not _looks_like_msg_seizure_text(name):
                    continue
                with zf.open(name) as f:
                    lines = f.read().decode("utf-8").splitlines()
                frames.append(_parse_unix_timestamp_lines(lines, f"{zip_path.name}:{name}"))
    frames = [frame for frame in frames if not frame.empty]
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def _nested_zip_patient_id(outer_zip: Path, member_name: str) -> str:
    parent = Path(member_name).parts[0] if Path(member_name).parts else outer_zip.stem
    if parent.startswith("Mayo_"):
        return parent.removeprefix("Mayo_")
    return _patient_id_from_msg_zip(outer_zip)


def _recording_id_for_nested_zip(patient_id: str, member_name: str) -> str:
    return f"{patient_id}_{Path(member_name).stem}"


def _read_empatica_header_and_count(zf: ZipFile, member_name: str) -> tuple[pd.Timestamp, float, int]:
    data = zf.read(member_name)
    lines = data.splitlines()
    if len(lines) < 2:
        raise ValueError(f"{member_name} missing Empatica start/sample-rate rows")
    first_start = lines[0].decode("utf-8").split(",")[0].strip()
    first_rate = lines[1].decode("utf-8").split(",")[0].strip()
    start = pd.to_datetime(float(first_start), unit="s", utc=True).tz_convert(None)
    sample_rate = float(first_rate)
    sample_count = max(0, len(lines) - 2)
    return start, sample_rate, sample_count


def _duplicate_recording_range_mask(recordings: pd.DataFrame) -> pd.Series:
    if recordings.empty:
        return pd.Series(False, index=recordings.index)
    required = {"patient_id", "recording_start", "recording_end"}
    if not required.issubset(recordings.columns):
        return pd.Series(False, index=recordings.index)
    return recordings.duplicated(["patient_id", "recording_start", "recording_end"], keep=False)


def resolve_msg_duplicate_recording_ranges(
    recordings: pd.DataFrame,
    duplicate_time_range_policy: str = "error",
) -> pd.DataFrame:
    """Resolve exact duplicate MSG recording ranges according to an explicit policy.

    Duplicate ranges in MSG nested ZIPs usually indicate copied segment files such as ``(1)``
    suffixes. Keeping both creates duplicated windows and ambiguous temporal splits. The default
    is therefore to fail; ``drop_exact`` prefers non-copy filenames before ``(1)``-style copies and
    records the policy in the output table.
    """
    if duplicate_time_range_policy not in MSG_DUPLICATE_RECORDING_POLICIES:
        raise ValueError(
            "duplicate_time_range_policy must be one of "
            f"{sorted(MSG_DUPLICATE_RECORDING_POLICIES)}"
        )
    out = recordings.copy()
    duplicate_mask = _duplicate_recording_range_mask(out)
    if not duplicate_mask.any():
        out["duplicate_time_range_policy"] = duplicate_time_range_policy
        out["duplicate_time_range_dropped"] = False
        return out
    duplicates = out.loc[
        duplicate_mask,
        ["patient_id", "recording_id", "recording_start", "recording_end", "source_file"],
    ].sort_values(["patient_id", "recording_start", "source_file"])
    if duplicate_time_range_policy == "error":
        raise ValueError(
            "MSG duplicate recording time ranges detected; rerun with "
            "duplicate_time_range_policy='drop_exact' only after documenting the duplicated files. "
            f"First duplicates: {duplicates.head(10).to_dict('records')}"
        )
    out["_copy_suffix_rank"] = out["source_file"].astype(str).str.contains(r"\s\(\d+\)").astype(int)
    out = out.sort_values(
        ["patient_id", "recording_start", "recording_end", "_copy_suffix_rank", "source_file"]
    ).copy()
    out["duplicate_time_range_policy"] = duplicate_time_range_policy
    out["duplicate_time_range_dropped"] = out.duplicated(
        ["patient_id", "recording_start", "recording_end"],
        keep="first",
    )
    return out.loc[~out["duplicate_time_range_dropped"]].drop(columns=["_copy_suffix_rank"]).reset_index(drop=True)


def discover_msg_recordings(
    raw_root: str | Path,
    duplicate_time_range_policy: str = "error",
) -> pd.DataFrame:
    """Discover Empatica segment intervals from complete MSG patient ZIP archives."""
    root = Path(raw_root)
    rows = []
    for outer_path in sorted(root.glob("*.zip")):
        if not _is_valid_zip(outer_path):
            continue
        with ZipFile(outer_path) as outer:
            nested_zip_names = sorted(name for name in outer.namelist() if name.lower().endswith(".zip"))
            for nested_name in nested_zip_names:
                patient_id = _nested_zip_patient_id(outer_path, nested_name)
                nested_bytes = outer.read(nested_name)
                try:
                    with ZipFile(BytesIO(nested_bytes)) as nested:
                        members = set(nested.namelist())
                        timing_member = "HR.csv" if "HR.csv" in members else "ACC.csv" if "ACC.csv" in members else None
                        if timing_member is None:
                            continue
                        start, sample_rate, sample_count = _read_empatica_header_and_count(
                            nested, timing_member
                        )
                except BadZipFile as exc:
                    raise ValueError(f"{outer_path.name}:{nested_name} is not a valid nested ZIP") from exc
                duration_seconds = sample_count / sample_rate if sample_rate > 0 else 0
                rows.append(
                    {
                        "patient_id": patient_id,
                        "recording_id": _recording_id_for_nested_zip(patient_id, nested_name),
                        "recording_start": start,
                        "recording_end": start + pd.to_timedelta(duration_seconds, unit="s"),
                        "center_id": None,
                        "source_dataset": "my_seizure_gauge",
                        "source_file": f"{outer_path.name}:{nested_name}",
                        "timing_modality": timing_member.removesuffix(".csv").lower(),
                        "timing_sample_rate": sample_rate,
                        "timing_sample_count": sample_count,
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
            "source_file",
            "timing_modality",
            "timing_sample_rate",
            "timing_sample_count",
        ],
    )
    recordings = resolve_msg_duplicate_recording_ranges(recordings, duplicate_time_range_policy)
    validate_recordings(recordings, allow_empty=True)
    return recordings


def discover_msg_metadata(
    raw_root: str | Path,
    duplicate_time_range_policy: str = "error",
) -> pd.DataFrame:
    recordings = discover_msg_recordings(raw_root, duplicate_time_range_policy)
    if recordings.empty:
        events = parse_msg_events(raw_root)
        metadata = events[["patient_id", "recording_id", "source_dataset"]].drop_duplicates().copy()
        metadata["center_id"] = None
        metadata = metadata[["patient_id", "recording_id", "center_id", "source_dataset"]]
    else:
        metadata = recordings[["patient_id", "recording_id", "center_id", "source_dataset"]].drop_duplicates()
    validate_metadata(metadata, allow_empty=True)
    return metadata.reset_index(drop=True)


def parse_msg_events(raw_root: str | Path) -> pd.DataFrame:
    """Parse MSG seizure times from canonical CSV files or Zenodo onset-only text files."""
    root = Path(raw_root)
    path = root / "seizure_times.csv"
    if not path.exists():
        path = root / "seizures.csv"
    if not path.exists():
        txt_events = _parse_msg_onset_only_txt_events(root)
        if txt_events.empty:
            raise FileNotFoundError(
                "expected seizure_times.csv, seizures.csv, or Zenodo SeizureTimesOnly/*.txt in MSG raw root"
            )
        txt_events = (
            txt_events.sort_values(["patient_id", "seizure_start", "source_file"])
            .drop_duplicates(["patient_id", "seizure_start"], keep="first")
            .reset_index(drop=True)
        )
        validate_events(txt_events, allow_empty=False)
        return txt_events
    events = pd.read_csv(path)
    required = {"patient_id", "seizure_start", "seizure_end"}
    missing = required - set(events.columns)
    if missing:
        raise ValueError(f"{path} missing required columns: {sorted(missing)}")
    if "recording_id" not in events.columns:
        events["recording_id"] = events["patient_id"].astype(str) + "_longitudinal"
    events["seizure_start"] = pd.to_datetime(events["seizure_start"])
    events["seizure_end"] = pd.to_datetime(events["seizure_end"])
    events["source_dataset"] = "my_seizure_gauge"
    cols = ["patient_id", "recording_id", "seizure_start", "seizure_end", "source_dataset"]
    out = events[cols + [c for c in events.columns if c not in cols]]
    out = out.sort_values(["patient_id", "seizure_start"]).drop_duplicates(
        ["patient_id", "seizure_start"], keep="first"
    )
    validate_events(out, allow_empty=False)
    return out


def assign_msg_events_to_recordings(events: pd.DataFrame, recordings: pd.DataFrame) -> pd.DataFrame:
    """Attach onset-only MSG seizures to the wearable segment containing the seizure onset.

    MSG seizure text files provide patient-level onsets, while wearable data are split into many
    Empatica segment ZIPs. Forecasting labels require event and window recording scopes to agree.
    Events outside downloaded/complete recording intervals are retained with their original
    longitudinal recording id and marked ``recording_match_status='unmatched'``.
    """
    out = events.copy()
    out["recording_match_status"] = "unmatched"
    if out.empty or recordings.empty:
        return out
    out["seizure_start"] = pd.to_datetime(out["seizure_start"])
    rec = recordings.copy()
    rec["recording_start"] = pd.to_datetime(rec["recording_start"])
    rec["recording_end"] = pd.to_datetime(rec["recording_end"])
    for idx, event in out.iterrows():
        matches = rec[
            rec["patient_id"].astype(str).eq(str(event["patient_id"]))
            & (rec["recording_start"] <= event["seizure_start"])
            & (rec["recording_end"] > event["seizure_start"])
        ].sort_values("recording_start")
        if matches.empty:
            continue
        out.at[idx, "recording_id"] = matches.iloc[0]["recording_id"]
        out.at[idx, "recording_match_status"] = "matched"
    validate_events(out, allow_empty=True)
    return out


def parse_msg_modality_availability(raw_root: str | Path) -> pd.DataFrame:
    """Read per-patient ZIP manifests and report whether HR/steps streams are present."""
    root = Path(raw_root)
    rows = []
    for path in sorted(root.glob("*.zip")):
        if not _is_valid_zip(path):
            continue
        patient_id = _patient_id_from_msg_zip(path)
        with ZipFile(path) as zf:
            nested_zip_names = sorted(name for name in zf.namelist() if name.lower().endswith(".zip"))
            top_level_names = {Path(name).name for name in zf.namelist()}
            top_level_names_lower = {name.lower() for name in top_level_names}
            segment_modalities: dict[str, set[str]] = {}
            for nested_name in nested_zip_names:
                nested_patient_id = _nested_zip_patient_id(path, nested_name)
                recording_id = _recording_id_for_nested_zip(nested_patient_id, nested_name)
                with ZipFile(BytesIO(zf.read(nested_name))) as nested:
                    segment_modalities[recording_id] = {
                        modality
                        for filename, modality in EMPATICA_MODALITY_FILES.items()
                        if filename in nested.namelist()
                    }
            if not segment_modalities:
                top_level_modalities = {
                    modality
                    for filename, modality in EMPATICA_MODALITY_FILES.items()
                    if filename.lower() in top_level_names_lower
                }
                if any(name in {"steps.csv", "step_count.csv", "stepcount.csv"} for name in top_level_names_lower):
                    top_level_modalities.add("steps")
                if not top_level_modalities:
                    continue
                segment_modalities[f"{patient_id}_longitudinal"] = top_level_modalities
        for recording_id, modalities in segment_modalities.items():
            for modality in sorted(set(EMPATICA_MODALITY_FILES.values()) | {"steps"}):
                matched = modality in modalities
                rows.append(
                    {
                        "patient_id": patient_id,
                        "recording_id": recording_id,
                        "modality": modality,
                        "available": matched,
                        "sampling_rate": None,
                        "channel_count": 3 if modality == "acc" and matched else 1 if matched else 0,
                        "notes": f"ZIP manifest only: {path.name}; nested recording {recording_id}",
                    }
                )
            continue
        modality_patterns = {
            "hr": ("hr", "heart_rate", "heartrate"),
            "steps": ("steps", "step_count", "stepcount"),
        }
        names = [name.lower() for name in _safe_zip_names(path)]
        for modality, patterns in modality_patterns.items():
            matched = any(any(pattern in name for pattern in patterns) for name in names)
            rows.append(
                {
                    "patient_id": patient_id,
                    "recording_id": f"{patient_id}_longitudinal",
                    "modality": modality,
                    "available": matched,
                    "sampling_rate": None,
                    "channel_count": 1 if matched else 0,
                    "notes": f"ZIP manifest only: {path.name}",
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


def _modality_from_stream_name(name: str) -> str | None:
    lower = name.lower()
    if any(token in lower for token in ("heart_rate", "heartrate", "hr")):
        return "hr"
    if any(token in lower for token in ("steps", "step_count", "stepcount")):
        return "steps"
    return None


def _standardize_msg_stream(
    table: pd.DataFrame,
    patient_id: str,
    source_file: str,
    modality: str,
) -> pd.DataFrame:
    time_col = next((c for c in ("timestamp", "time", "datetime", "date") if c in table.columns), None)
    if not time_col:
        raise ValueError(f"{source_file} missing timestamp/time column")
    value_candidates = {
        "hr": ("hr", "heart_rate", "heartrate", "bpm", "value"),
        "steps": ("steps", "step_count", "stepcount", "count", "value"),
    }[modality]
    value_col = next((c for c in value_candidates if c in table.columns), None)
    if not value_col:
        raise ValueError(f"{source_file} missing value column for modality {modality}")
    out = pd.DataFrame(
        {
            "patient_id": patient_id,
            "recording_id": f"{patient_id}_longitudinal",
            "timestamp": pd.to_datetime(table[time_col]),
            "modality": modality,
            "value": pd.to_numeric(table[value_col], errors="coerce"),
            "source_file": source_file,
        }
    )
    if out["timestamp"].isna().any() or out["value"].isna().any():
        raise ValueError(f"{source_file} contains invalid timestamps or values")
    return out


def parse_msg_wearable_samples(raw_root: str | Path) -> pd.DataFrame:
    """Parse supported HR/steps CSV streams from per-patient ZIPs or extracted folders."""
    root = Path(raw_root)
    if not root.exists():
        raise FileNotFoundError(f"My Seizure Gauge raw root does not exist: {root}")
    frames = []
    for zip_path in sorted(root.glob("*.zip")):
        if not _is_valid_zip(zip_path):
            continue
        patient_id = _patient_id_from_msg_zip(zip_path)
        with ZipFile(zip_path) as zf:
            for name in sorted(zf.namelist()):
                if not name.lower().endswith(".csv"):
                    continue
                modality = _modality_from_stream_name(name)
                if modality is None:
                    continue
                with zf.open(name) as f:
                    table = pd.read_csv(f)
                frames.append(
                    _standardize_msg_stream(table, patient_id, f"{zip_path.name}:{name}", modality)
                )

    for csv_path in sorted(root.rglob("*.csv")):
        if csv_path.name in {"seizure_times.csv", "seizures.csv"}:
            continue
        modality = _modality_from_stream_name(csv_path.name)
        if modality is None:
            continue
        patient_id = csv_path.parent.name if csv_path.parent != root else csv_path.stem.split("_")[0]
        frames.append(_standardize_msg_stream(pd.read_csv(csv_path), patient_id, str(csv_path), modality))

    if not frames:
        return pd.DataFrame(columns=SAMPLE_COLUMNS)
    samples = pd.concat(frames, ignore_index=True)[SAMPLE_COLUMNS]
    return samples.sort_values(["patient_id", "timestamp", "modality"]).reset_index(drop=True)


def prepare_msg_tables(
    raw_root: str | Path,
    processed_root: str | Path,
    duplicate_time_range_policy: str = "error",
) -> dict[str, Path]:
    """Write canonical MSG event and modality-availability tables from supported metadata."""
    root = Path(raw_root)
    if not root.exists():
        raise FileNotFoundError(f"My Seizure Gauge raw root does not exist: {root}")
    processed = Path(processed_root)
    processed.mkdir(parents=True, exist_ok=True)
    metadata_path = processed / "metadata.parquet"
    recordings_path = processed / "recordings.parquet"
    events_path = processed / "events.parquet"
    availability_path = processed / "modality_availability.parquet"
    samples_path = processed / "samples.parquet"
    recordings = discover_msg_recordings(raw_root, duplicate_time_range_policy)
    events = assign_msg_events_to_recordings(parse_msg_events(raw_root), recordings)
    metadata = (
        recordings[["patient_id", "recording_id", "center_id", "source_dataset"]]
        .drop_duplicates()
        .reset_index(drop=True)
        if not recordings.empty
        else events[["patient_id", "recording_id", "source_dataset"]]
        .drop_duplicates()
        .assign(center_id=None)[["patient_id", "recording_id", "center_id", "source_dataset"]]
    )
    validate_metadata(metadata, allow_empty=True)
    write_table(metadata, metadata_path)
    write_table(recordings, recordings_path)
    write_table(events, events_path)
    write_table(parse_msg_modality_availability(raw_root), availability_path)
    samples = parse_msg_wearable_samples(raw_root)
    write_table(samples, samples_path)
    return {
        "metadata": metadata_path,
        "recordings": recordings_path,
        "events": events_path,
        "modality_availability": availability_path,
        "samples": samples_path,
    }


def make_mock_msg_artifacts() -> dict[str, pd.DataFrame]:
    """Create deterministic MSG-shaped benchmark artifacts for dry runs."""
    base = pd.Timestamp("2026-01-01 00:00:00")
    metadata = pd.DataFrame(
        [
            {
                "patient_id": "MSG001",
                "recording_id": "MSG001_longitudinal",
                "center_id": None,
                "source_dataset": "my_seizure_gauge_mock",
            }
        ]
    )
    recordings = pd.DataFrame(
        [
            {
                "patient_id": "MSG001",
                "recording_id": "MSG001_longitudinal",
                "recording_start": base,
                "recording_end": base + pd.Timedelta(days=2),
                "center_id": None,
                "source_dataset": "my_seizure_gauge_mock",
            }
        ]
    )
    events = pd.DataFrame(
        [
            {
                "patient_id": "MSG001",
                "recording_id": "MSG001_longitudinal",
                "seizure_start": base + pd.Timedelta(hours=27),
                "seizure_end": base + pd.Timedelta(hours=27, minutes=2),
                "source_dataset": "my_seizure_gauge_mock",
            }
        ]
    )
    windows = generate_fixed_windows(recordings, window_duration="1h", stride="1h")
    availability = pd.DataFrame(
        [
            {
                "patient_id": "MSG001",
                "recording_id": "MSG001_longitudinal",
                "modality": modality,
                "available": True,
                "sampling_rate": sampling_rate,
                "channel_count": 1,
                "notes": "deterministic mock manifest; not real MSG data",
            }
            for modality, sampling_rate in [("hr", 1 / 60), ("steps", 1 / 60)]
        ]
    )
    samples = pd.DataFrame(
        [
            {
                "patient_id": "MSG001",
                "recording_id": "MSG001_longitudinal",
                "timestamp": base + pd.Timedelta(hours=i),
                "modality": modality,
                "value": value,
                "source_file": "mock",
            }
            for i in range(48)
            for modality, value in [("hr", 70 + (i % 6)), ("steps", 100 * (i % 4))]
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
        "samples": samples,
    }


def prepare_mock_msg_tables(processed_root: str | Path) -> dict[str, Path]:
    processed = Path(processed_root)
    processed.mkdir(parents=True, exist_ok=True)
    artifacts = make_mock_msg_artifacts()
    written = {}
    for name, table in artifacts.items():
        path = processed / f"{name}.parquet"
        write_table(table, path)
        written[name] = path
    return written
