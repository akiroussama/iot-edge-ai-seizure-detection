from __future__ import annotations

import json
import subprocess
import sys

import pandas as pd

from src.artifacts.gate_c_source_discovery import (
    discover_gate_c_sources,
    write_gate_c_source_discovery,
)
from src.utils.io import read_table, write_table


def _write_sources(root) -> None:
    base = pd.Timestamp("2026-01-01 00:00:00")
    recordings = pd.DataFrame(
        {
            "patient_id": ["p1"],
            "recording_id": ["r1"],
            "recording_start": [base],
            "recording_end": [base + pd.Timedelta(hours=4)],
        }
    )
    events = pd.DataFrame(
        {
            "patient_id": ["p1"],
            "recording_id": ["r1"],
            "seizure_start": [base + pd.Timedelta(hours=2)],
            "seizure_end": [base + pd.Timedelta(hours=2, minutes=1)],
        }
    )
    write_table(recordings, root / "recordings.csv")
    write_table(events, root / "events.csv")


def test_gate_c_source_discovery_finds_source_ready_tables(tmp_path) -> None:
    _write_sources(tmp_path)

    discovery = discover_gate_c_sources((tmp_path,))

    assert discovery.summary["scan_status"] == "gate_c_sources_available"
    assert discovery.summary["role_ready_counts"] == {"recordings": 1, "events": 1}
    assert discovery.summary["missing_roles"] == []
    assert "Gate C Source Discovery" in discovery.markdown


def test_gate_c_source_discovery_reports_missing_sources(tmp_path) -> None:
    write_table(pd.DataFrame({"patient_id": ["p1"], "note": ["not source-ready"]}), tmp_path / "notes.csv")

    discovery = discover_gate_c_sources((tmp_path,))

    assert discovery.summary["scan_status"] == "blocked_missing_gate_c_sources"
    assert discovery.summary["missing_roles"] == ["recordings", "events"]
    assert discovery.candidates.loc[0, "candidate_roles"] == ""


def test_gate_c_source_discovery_writes_report(tmp_path) -> None:
    _write_sources(tmp_path)
    discovery = discover_gate_c_sources((tmp_path,))

    paths = write_gate_c_source_discovery(discovery, tmp_path / "out")

    summary = json.loads(open(paths["summary"], encoding="utf-8").read())
    candidates = read_table(paths["candidates"])
    markdown = open(paths["markdown"], encoding="utf-8").read()
    assert summary["scan_status"] == "gate_c_sources_available"
    assert len(candidates) == 2
    assert "Candidate Source Files" in markdown


def test_gate_c_source_discovery_cli(tmp_path) -> None:
    _write_sources(tmp_path)
    out_dir = tmp_path / "cli_out"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/discover_gate_c_sources.py",
            "--root",
            str(tmp_path),
            "--out-dir",
            str(out_dir),
        ],
        check=True,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    summary = json.loads((out_dir / "gate_c_source_discovery.json").read_text(encoding="utf-8"))
    assert payload["scan_status"] == "gate_c_sources_available"
    assert summary["missing_roles"] == []
