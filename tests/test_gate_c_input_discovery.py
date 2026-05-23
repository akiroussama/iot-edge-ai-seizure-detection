from __future__ import annotations

import json
import subprocess
import sys

import pandas as pd

from src.artifacts.gate_c_input_discovery import discover_gate_c_inputs, write_gate_c_input_discovery
from src.utils.io import read_table, write_table


def _write_valid_inputs(root) -> None:
    base = pd.Timestamp("2026-01-01 00:00:00")
    events = pd.DataFrame(
        {
            "patient_id": ["p1"],
            "recording_id": ["r1"],
            "seizure_start": [base + pd.Timedelta(hours=1)],
            "seizure_end": [base + pd.Timedelta(hours=1, minutes=1)],
        }
    )
    labels = pd.DataFrame(
        {
            "patient_id": ["p1", "p1", "p1"],
            "recording_id": ["r1", "r1", "r1"],
            "window_start": [
                base,
                base + pd.Timedelta(hours=1),
                base + pd.Timedelta(hours=2),
            ],
            "window_end": [
                base + pd.Timedelta(hours=1),
                base + pd.Timedelta(hours=2),
                base + pd.Timedelta(hours=3),
            ],
            "split": ["train", "val", "test"],
            "forecast_label": [False, True, False],
            "is_excluded": [False, False, False],
        }
    )
    splits = labels[["patient_id", "recording_id", "window_start", "window_end", "split"]]
    write_table(events, root / "events.csv")
    write_table(labels, root / "labels.csv")
    write_table(splits, root / "splits.csv")


def test_gate_c_input_discovery_finds_role_ready_tables(tmp_path) -> None:
    _write_valid_inputs(tmp_path)

    discovery = discover_gate_c_inputs((tmp_path,))

    assert discovery.summary["scan_status"] == "gate_c_inputs_available"
    assert discovery.summary["role_ready_counts"]["events"] == 1
    assert discovery.summary["role_ready_counts"]["labels"] == 1
    assert discovery.summary["role_ready_counts"]["splits"] >= 1
    assert discovery.summary["missing_roles"] == []
    assert "Gate C Input Discovery" in discovery.markdown


def test_gate_c_input_discovery_reports_missing_roles(tmp_path) -> None:
    write_table(pd.DataFrame({"patient_id": ["p1"], "note": ["not a gate c table"]}), tmp_path / "notes.csv")

    discovery = discover_gate_c_inputs((tmp_path,))

    assert discovery.summary["scan_status"] == "blocked_missing_gate_c_inputs"
    assert discovery.summary["missing_roles"] == ["events", "labels", "splits"]
    assert discovery.candidates.loc[0, "candidate_roles"] == ""


def test_gate_c_input_discovery_writes_report(tmp_path) -> None:
    _write_valid_inputs(tmp_path)
    discovery = discover_gate_c_inputs((tmp_path,))

    paths = write_gate_c_input_discovery(discovery, tmp_path / "out")

    summary = json.loads(open(paths["summary"], encoding="utf-8").read())
    candidates = read_table(paths["candidates"])
    markdown = open(paths["markdown"], encoding="utf-8").read()
    assert summary["scan_status"] == "gate_c_inputs_available"
    assert len(candidates) == 3
    assert "Candidate Files" in markdown


def test_gate_c_input_discovery_cli(tmp_path) -> None:
    _write_valid_inputs(tmp_path)
    out_dir = tmp_path / "cli_out"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/discover_gate_c_inputs.py",
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
    summary = json.loads((out_dir / "gate_c_input_discovery.json").read_text(encoding="utf-8"))
    assert payload["scan_status"] == "gate_c_inputs_available"
    assert summary["missing_roles"] == []
