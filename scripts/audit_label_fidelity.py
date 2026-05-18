#!/usr/bin/env python
"""Automated label audit -- parser fidelity (Phase B).

Re-reads the RAW seizure annotations independently and checks that
data/processed/{msg,seizeit2}/events.parquet (produced by the repo parsers)
reflects them exactly -- no dropped, added, or shifted seizures. Read-only.
Exits non-zero on any mismatch.

NOT a human clinical audit: it verifies parser fidelity (raw source ->
events.parquet), not the clinical correctness of the source annotations
themselves. The SeizeIT2 arm compares seizure counts per patient (catches
dropped, added, or mis-assigned seizures, not sub-second timestamp shifts);
the MSG arm compares onset timestamps. A human clinical spot-check remains
recommended regardless.

The MSG-source helpers below are copied verbatim from src/datasets/msg_loader.py
so the audit's raw-file discovery matches the parser it audits.
"""
from __future__ import annotations

import sys
from pathlib import Path
from zipfile import BadZipFile, ZipFile

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
findings: list[str] = []


def flag(msg: str) -> None:
    findings.append(msg)
    print(f"  MISMATCH: {msg}")


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
    ev = pd.read_parquet(REPO / "data/processed/msg/events.parquet")
    # seizure_start is tz-naive UTC wall-clock; .value is ns-since-epoch (UTC).
    parsed = {
        (str(row.patient_id), int(pd.Timestamp(row.seizure_start).value // 10**9))
        for row in ev.itertuples()
    }
    raw = msg_raw_onsets(REPO / "data/raw/msg")
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
    ev = pd.read_parquet(REPO / "data/processed/seizeit2/events.parquet")
    seizure_patterns = ("seizure", "ictal", "sz")
    non_seizure = {"bckg", "background", "impd", "artifact", "artefact", "n/a", "nan", ""}
    raw_per_patient: dict[str, int] = {}
    raw_total = 0
    for tsv in sorted((REPO / "data/raw/seizeit2").rglob("*events.tsv")):
        try:
            table = pd.read_csv(tsv, sep="\t")
        except Exception as exc:  # noqa: BLE001 - report any unreadable annotation
            flag(f"SeizeIT2 {tsv.name}: read failed: {exc}")
            continue
        pid = next((p for p in tsv.parts if p.startswith("sub-")), None)
        if pid is None:  # mirror parse_bids_like_seizeit2_events fallback
            if "patient_id" in table.columns and len(table):
                pid = str(table["patient_id"].iloc[0])
            else:
                pid = tsv.parent.name
        col = next((c for c in ("trial_type", "event_type", "eventType") if c in table.columns), None)
        if col is None:
            n = len(table)
        else:
            vals = table[col].astype(str).str.strip().str.lower()
            n = int(vals.map(lambda v: v not in non_seizure and any(p in v for p in seizure_patterns)).sum())
        raw_per_patient[pid] = raw_per_patient.get(pid, 0) + n
        raw_total += n
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


def main() -> None:
    audit_msg()
    print()
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
    main()
