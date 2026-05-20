#!/usr/bin/env python
"""Automated label audit -- parser fidelity (Phase B).

Re-reads the RAW seizure annotations independently and checks that
data/processed/{msg,seizeit2}/events.parquet (produced by the repo parsers)
reflects them exactly -- no dropped, added, or shifted seizures. Read-only.
Exits non-zero on any mismatch.

NOT a human clinical audit: it verifies parser fidelity (raw source ->
events.parquet), not the clinical correctness of the source annotations
themselves. The MSG arm compares onset timestamps. The SeizeIT2 arm keeps the
per-patient count check and also compares raw BIDS onset rows to processed
relative onsets (seizure_start - recording_start). A human clinical spot-check
remains recommended regardless.

The MSG-source helpers below are copied verbatim from src/datasets/msg_loader.py
so the audit's raw-file discovery matches the parser it audits.
"""
from __future__ import annotations

import argparse
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from zipfile import BadZipFile, ZipFile

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
MSG_RAW_ROOT_OVERRIDE: Path | None = None
MSG_EVENTS_PATH_OVERRIDE: Path | None = None
SEIZEIT2_RAW_ROOT_OVERRIDE: Path | None = None
SEIZEIT2_EVENTS_PATH_OVERRIDE: Path | None = None
SEIZEIT2_RECORDINGS_PATH_OVERRIDE: Path | None = None
findings: list[str] = []
SEIZURE_PATTERNS = ("seizure", "ictal", "sz")
NON_SEIZURE_EVENT_TYPES = {"bckg", "background", "impd", "artifact", "artefact", "n/a", "nan", ""}
ONSET_TOLERANCE_US = 1


def flag(msg: str) -> None:
    findings.append(msg)
    print(f"  MISMATCH: {msg}")


def _read_required_parquet(path: Path, label: str) -> pd.DataFrame | None:
    if not path.exists():
        flag(f"{label}: missing required parquet: {path}")
        return None
    try:
        return pd.read_parquet(path)
    except Exception as exc:  # noqa: BLE001 - report any unreadable audit input
        flag(f"{label}: failed to read {path}: {exc}")
        return None


def _configured_path(override: Path | None, default: Path) -> Path:
    return override if override is not None else default


def _msg_raw_root() -> Path:
    return _configured_path(MSG_RAW_ROOT_OVERRIDE, REPO / "data/raw/msg")


def _msg_events_path() -> Path:
    return _configured_path(MSG_EVENTS_PATH_OVERRIDE, REPO / "data/processed/msg/events.parquet")


def _seizeit2_raw_root() -> Path:
    return _configured_path(SEIZEIT2_RAW_ROOT_OVERRIDE, REPO / "data/raw/seizeit2")


def _seizeit2_events_path() -> Path:
    return _configured_path(SEIZEIT2_EVENTS_PATH_OVERRIDE, REPO / "data/processed/seizeit2/events.parquet")


def _seizeit2_recordings_path() -> Path:
    return _configured_path(
        SEIZEIT2_RECORDINGS_PATH_OVERRIDE,
        REPO / "data/processed/seizeit2/recordings.parquet",
    )


@dataclass(frozen=True)
class Seizeit2OnsetKey:
    patient_id: str
    recording_id: str
    event_source_file: str
    onset_us: int


@dataclass(frozen=True)
class Seizeit2ParsedOnset:
    row_idx: int
    patient_id: str
    recording_id: str
    event_source_file: str
    onset_us: int
    seizure_start: object


def _seconds_to_us(value: object, src: str) -> int | None:
    try:
        seconds = float(value)
    except (TypeError, ValueError):
        flag(f"{src}: non-numeric onset {value!r}")
        return None
    if pd.isna(seconds):
        flag(f"{src}: missing onset")
        return None
    return int(round(seconds * 1_000_000))


def _is_seizeit2_seizure_event_type(value: object) -> bool:
    """Local lexical classifier; deliberately does not import parser internals."""
    event_type = str(value).strip().lower()
    if event_type in NON_SEIZURE_EVENT_TYPES:
        return False
    return any(pattern in event_type for pattern in SEIZURE_PATTERNS)


def _seizeit2_event_type_column(table: pd.DataFrame) -> str | None:
    return next((col for col in ("trial_type", "event_type", "eventType") if col in table.columns), None)


def _seizeit2_patient_id(tsv: Path, table: pd.DataFrame) -> str:
    pid = next((p for p in tsv.parts if p.startswith("sub-")), None)
    if pid is not None:
        return str(pid)
    if "patient_id" in table.columns and len(table):
        return str(table["patient_id"].iloc[0])
    return tsv.parent.name


def _seizeit2_recording_id(tsv: Path) -> str:
    return tsv.name.removesuffix("_events.tsv")


def _seizeit2_source_file(value: object) -> str | None:
    if pd.isna(value) or not str(value).strip():
        return None
    return str(value).replace("\\", "/")


def _looks_like_msg_seizure_text(path_name: str) -> bool:
    """Verbatim from msg_loader._looks_like_msg_seizure_text."""
    path = Path(path_name)
    stem = path.stem.removeprefix("Mayo_")
    parent = path.parent.name.removeprefix("Mayo_")
    if "info" in stem.lower() or "tags" in stem.lower():
        return False
    return stem.isdigit() or parent.isdigit() or "seizure" in str(path).lower()


def _msg_pid(path_name: str) -> str:
    """Verbatim from msg_loader._patient_id_from_seizure_text_path."""
    return Path(path_name).stem.removeprefix("Mayo_")


def _onsets_from_lines(lines: list[str], src: str, pid: str, onsets: set[tuple[str, int]]) -> None:
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            onsets.add((pid, int(float(line))))
        except ValueError:
            flag(f"MSG {src}: non-numeric onset line {line!r}")


def msg_raw_onsets(raw_root: Path) -> set[tuple[str, int]]:
    """(patient_id, unix_second) for raw MSG onsets, mirroring parse_msg_events.

    parse_msg_events prefers seizure_times.csv / seizures.csv and only falls
    back to .txt files. If a CSV is present, this txt-fidelity audit does not
    cover the path the parser used -- flag it loudly (no false OK) and bail.
    """
    for csv_name in ("seizure_times.csv", "seizures.csv"):
        if (raw_root / csv_name).exists():
            flag(f"MSG: {csv_name} present -- parse_msg_events uses the CSV branch, "
                 "which this txt-fidelity audit does not cover; MSG fidelity unverified")
            return set()
    onsets: set[tuple[str, int]] = set()
    # extracted .txt on disk (parser: _parse_msg_onset_only_txt_events rglob)
    for p in sorted(raw_root.rglob("*.txt")):
        rel = str(p.relative_to(raw_root))
        if _looks_like_msg_seizure_text(rel):
            _onsets_from_lines(p.read_text(encoding="utf-8").splitlines(), rel, _msg_pid(rel), onsets)
    # .txt inside the patient zips
    for zp in sorted(raw_root.glob("*.zip")):
        try:
            with ZipFile(zp) as z:
                for name in z.namelist():
                    if name.lower().endswith(".txt") and _looks_like_msg_seizure_text(name):
                        _onsets_from_lines(
                            z.read(name).decode("utf-8").splitlines(),
                            f"{zp.name}:{name}", _msg_pid(name), onsets,
                        )
        except BadZipFile:
            flag(f"MSG {zp.name}: not a valid zip")
    return onsets


def audit_msg() -> None:
    print("=== MSG parser fidelity (events.parquet vs raw onsets) ===")
    ev = _read_required_parquet(_msg_events_path(), "MSG")
    if ev is None:
        return
    # seizure_start is tz-naive UTC wall-clock; .value is ns-since-epoch (UTC).
    parsed = {
        (str(row.patient_id), int(pd.Timestamp(row.seizure_start).value // 10**9))
        for row in ev.itertuples()
    }
    raw = msg_raw_onsets(_msg_raw_root())
    if not raw:
        print("  MSG fidelity NOT verified (see flag above)")
        return
    print(f"  raw onsets: {len(raw)}  |  events.parquet onsets: {len(parsed)}")
    missing = raw - parsed
    extra = parsed - raw
    if missing:
        flag(f"MSG: {len(missing)} raw onset(s) absent from events.parquet, e.g. {sorted(missing)[:3]}")
    if extra:
        flag(f"MSG: {len(extra)} events.parquet onset(s) not in raw source, e.g. {sorted(extra)[:3]}")
    if not missing and not extra:
        print("  OK: events.parquet onset set is identical to the raw source onset set")


def audit_seizeit2() -> None:
    print("=== SeizeIT2 parser fidelity (events.parquet vs raw *events.tsv) ===")
    ev = _read_required_parquet(_seizeit2_events_path(), "SeizeIT2")
    if ev is None:
        return
    raw_per_patient: dict[str, int] = {}
    raw_onsets: list[Seizeit2OnsetKey] = []
    raw_total = 0
    raw_root = _seizeit2_raw_root()
    if not raw_root.exists():
        flag(f"SeizeIT2: raw root missing: {raw_root}")
        return
    raw_event_files = sorted(raw_root.rglob("*events.tsv"))
    if not raw_event_files:
        flag(f"SeizeIT2: no raw *events.tsv files found under {raw_root}")
        return
    for tsv in raw_event_files:
        try:
            table = pd.read_csv(tsv, sep="\t")
        except Exception as exc:  # noqa: BLE001 - report any unreadable annotation
            flag(f"SeizeIT2 {tsv.name}: read failed: {exc}")
            continue
        pid = _seizeit2_patient_id(tsv, table)
        recording_id = _seizeit2_recording_id(tsv)
        source_file = tsv.relative_to(raw_root).as_posix()
        col = _seizeit2_event_type_column(table)
        if col is None:
            seizure_rows = table
        else:
            vals = table[col].astype(str).str.strip().str.lower()
            seizure_rows = table.loc[vals.map(_is_seizeit2_seizure_event_type)]
        n = len(seizure_rows)
        raw_per_patient[pid] = raw_per_patient.get(pid, 0) + n
        raw_total += n
        if "onset" not in seizure_rows.columns and n:
            flag(f"SeizeIT2 {source_file}: {n} seizure row(s) lack raw onset; onset fidelity unverified")
            continue
        for raw_idx, row in seizure_rows.iterrows():
            onset_us = _seconds_to_us(row.get("onset"), f"SeizeIT2 {source_file} row {raw_idx}")
            if onset_us is None:
                continue
            raw_onsets.append(Seizeit2OnsetKey(pid, recording_id, source_file, onset_us))
    parsed_total = len(ev)
    parsed_per_patient = ev.groupby(ev["patient_id"].astype(str)).size().to_dict()
    print(f"  raw *events.tsv seizures: {raw_total}  |  events.parquet: {parsed_total}")
    if raw_total != parsed_total:
        flag(f"SeizeIT2: raw seizure count {raw_total} != events.parquet count {parsed_total}")
    mismatched = sorted(
        p for p in set(raw_per_patient) | set(parsed_per_patient)
        if raw_per_patient.get(p, 0) != parsed_per_patient.get(p, 0)
    )
    if mismatched:
        flag(f"SeizeIT2: {len(mismatched)} patient(s) with raw vs parsed count mismatch: "
             f"{[(p, raw_per_patient.get(p, 0), parsed_per_patient.get(p, 0)) for p in mismatched[:5]]}")
    if raw_total == parsed_total and not mismatched:
        print("  OK: raw seizure counts match events.parquet, overall and per patient")
    _audit_seizeit2_onsets(ev, raw_onsets)


def _audit_seizeit2_onsets(ev: pd.DataFrame, raw_onsets: list[Seizeit2OnsetKey]) -> None:
    required_key_cols = {
        "patient_id",
        "recording_id",
        "event_source_file",
        "event_onset_seconds",
    }
    missing_key_cols = required_key_cols - set(ev.columns)
    if missing_key_cols:
        flag(f"SeizeIT2: events.parquet missing onset-audit key column(s): {sorted(missing_key_cols)}")
        return

    parsed_onsets: list[Seizeit2ParsedOnset] = []
    offset_mismatch = False
    offset_unverified = False
    for row_idx, row in enumerate(ev.itertuples(index=False)):
        patient_id = str(row.patient_id)
        recording_id = str(row.recording_id)
        source_file = _seizeit2_source_file(row.event_source_file)
        if source_file is None:
            offset_unverified = True
            flag(f"SeizeIT2 events.parquet row {row_idx}: missing event_source_file")
            continue
        onset_us = _seconds_to_us(row.event_onset_seconds, f"SeizeIT2 events.parquet row {row_idx}")
        if onset_us is None:
            offset_unverified = True
            continue
        parsed_onsets.append(
            Seizeit2ParsedOnset(
                row_idx,
                patient_id,
                recording_id,
                source_file,
                onset_us,
                getattr(row, "seizure_start", None),
            )
        )

    raw_counts = Counter(raw_onsets)
    parsed_counts = Counter(
        Seizeit2OnsetKey(row.patient_id, row.recording_id, row.event_source_file, row.onset_us)
        for row in parsed_onsets
    )
    missing = raw_counts - parsed_counts
    extra = parsed_counts - raw_counts
    print(f"  raw onset keys: {sum(raw_counts.values())}  |  events.parquet onset keys: {sum(parsed_counts.values())}")
    if missing:
        examples = [(key, count) for key, count in missing.items()][:3]
        flag(f"SeizeIT2: {sum(missing.values())} raw onset row(s) absent from events.parquet, e.g. {examples}")
    if extra:
        examples = [(key, count) for key, count in extra.items()][:3]
        flag(f"SeizeIT2: {sum(extra.values())} events.parquet onset row(s) not in raw source, e.g. {examples}")
    if not missing and not extra:
        print("  OK: raw onset multiset matches events.parquet patient/recording/source/onset keys")

    rec_path = _seizeit2_recordings_path()
    if not rec_path.exists():
        flag("SeizeIT2: recordings.parquet missing; cannot verify seizure_start - recording_start")
        return
    recordings = _read_required_parquet(rec_path, "SeizeIT2")
    if recordings is None:
        return
    required_rec_cols = {"patient_id", "recording_id", "recording_start"}
    missing_rec_cols = required_rec_cols - set(recordings.columns)
    if missing_rec_cols:
        flag(f"SeizeIT2: recordings.parquet missing onset-audit column(s): {sorted(missing_rec_cols)}")
        return
    if "seizure_start" not in ev.columns:
        flag("SeizeIT2: events.parquet missing onset-offset column(s): ['seizure_start']")
        return

    rec_starts: dict[tuple[str, str], pd.Timestamp] = {}
    for (patient_id, recording_id), group in recordings.groupby(
        [recordings["patient_id"].astype(str), recordings["recording_id"].astype(str)],
        dropna=False,
    ):
        starts = pd.to_datetime(group["recording_start"]).dropna().drop_duplicates()
        if len(starts) != 1:
            flag(
                "SeizeIT2: recording_start is not uniquely verifiable for "
                f"{patient_id}/{recording_id}: {starts.astype(str).tolist()}"
            )
            continue
        rec_starts[(str(patient_id), str(recording_id))] = starts.iloc[0]

    for row in parsed_onsets:
        rec_start = rec_starts.get((row.patient_id, row.recording_id))
        if rec_start is None:
            offset_unverified = True
            flag(f"SeizeIT2 events.parquet row {row.row_idx}: missing recording_start for "
                 f"{row.patient_id}/{row.recording_id}")
            continue
        seizure_start = pd.to_datetime(row.seizure_start)
        if pd.isna(seizure_start):
            offset_unverified = True
            flag(f"SeizeIT2 events.parquet row {row.row_idx}: missing seizure_start")
            continue
        parsed_offset_us = int(round((seizure_start - rec_start).total_seconds() * 1_000_000))
        if abs(parsed_offset_us - row.onset_us) > ONSET_TOLERANCE_US:
            offset_mismatch = True
            flag(
                f"SeizeIT2 {row.patient_id}/{row.recording_id} {row.event_source_file}: relative onset mismatch "
                f"raw/event_onset={row.onset_us / 1_000_000:.6f}s vs "
                f"seizure_start-recording_start={parsed_offset_us / 1_000_000:.6f}s"
            )
    if not offset_mismatch and not offset_unverified:
        print("  OK: seizure_start - recording_start matches every raw SeizeIT2 onset")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dataset",
        choices=("all", "msg", "seizeit2"),
        default="all",
        help="Dataset arm to audit.",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=REPO,
        help="Repository/data root containing data/raw and data/processed.",
    )
    parser.add_argument("--msg-raw-root", type=Path, default=None)
    parser.add_argument("--msg-events", type=Path, default=None)
    parser.add_argument("--seizeit2-raw-root", type=Path, default=None)
    parser.add_argument("--seizeit2-events", type=Path, default=None)
    parser.add_argument("--seizeit2-recordings", type=Path, default=None)
    return parser.parse_args()


def main(
    repo_root: Path | None = None,
    dataset: str = "all",
    msg_raw_root: Path | None = None,
    msg_events: Path | None = None,
    seizeit2_raw_root: Path | None = None,
    seizeit2_events: Path | None = None,
    seizeit2_recordings: Path | None = None,
) -> None:
    global REPO  # noqa: PLW0603 - CLI override keeps existing audit helpers simple.
    global MSG_EVENTS_PATH_OVERRIDE, MSG_RAW_ROOT_OVERRIDE
    global SEIZEIT2_EVENTS_PATH_OVERRIDE, SEIZEIT2_RAW_ROOT_OVERRIDE, SEIZEIT2_RECORDINGS_PATH_OVERRIDE
    if repo_root is not None:
        REPO = repo_root.resolve()
    MSG_RAW_ROOT_OVERRIDE = msg_raw_root.resolve() if msg_raw_root else None
    MSG_EVENTS_PATH_OVERRIDE = msg_events.resolve() if msg_events else None
    SEIZEIT2_RAW_ROOT_OVERRIDE = seizeit2_raw_root.resolve() if seizeit2_raw_root else None
    SEIZEIT2_EVENTS_PATH_OVERRIDE = seizeit2_events.resolve() if seizeit2_events else None
    SEIZEIT2_RECORDINGS_PATH_OVERRIDE = seizeit2_recordings.resolve() if seizeit2_recordings else None
    if dataset in {"all", "msg"}:
        audit_msg()
    if dataset == "all":
        print()
    if dataset in {"all", "seizeit2"}:
        audit_seizeit2()
    print("\n===== summary =====")
    if findings:
        print(f"{len(findings)} parser-fidelity finding(s):")
        for f in findings:
            print(f"  - {f}")
        sys.exit(1)
    print("no mismatches: events.parquet is faithful to the raw source annotations")
    print("(automated parser-fidelity audit only; human clinical spot-check still recommended)")


if __name__ == "__main__":
    args = _parse_args()
    main(
        repo_root=args.repo_root,
        dataset=args.dataset,
        msg_raw_root=args.msg_raw_root,
        msg_events=args.msg_events,
        seizeit2_raw_root=args.seizeit2_raw_root,
        seizeit2_events=args.seizeit2_events,
        seizeit2_recordings=args.seizeit2_recordings,
    )
