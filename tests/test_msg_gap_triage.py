from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pandas as pd

from src.reports.msg_gap_triage import (
    CLAIM_STATUS,
    build_horizon_gap_triage,
    build_msg_gap_triage_report,
    build_patient_gap_triage,
    msg_gap_triage_markdown,
)


def _coverage() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "patient_id": ["zero", "partial", "routine"],
            "events_total": [5, 10, 4],
            "events_matched": [0, 7, 4],
            "events_unmatched": [5, 3, 0],
            "matched_fraction": [0.0, 0.7, 1.0],
            "recordings": [0, 12, 8],
            "recording_hours": [0.0, 120.0, 80.0],
        }
    )


def _clusters() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "patient_id": ["zero", "partial", "routine"],
            "clusters": [2, 3, 4],
            "clustered_events": [5, 6, 0],
            "max_cluster_size": [3, 5, 1],
        }
    )


def _viability() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "sph_minutes": [60, 5],
            "sop_minutes": [1440, 30],
            "windows_total": [100, 100],
            "valid_windows": [20, 90],
            "valid_window_fraction": [0.2, 0.9],
            "positive_windows_total": [30, 5],
            "valid_positive_windows": [12, 4],
            "right_censored_unknown_windows": [60, 5],
            "events_total": [20, 20],
            "events_coverable_by_valid_windows": [8, 18],
            "event_coverable_fraction": [0.4, 0.9],
            "events_recording_matched": [15, 15],
            "events_recording_unmatched": [5, 5],
        }
    )


def test_patient_gap_triage_separates_blockers_from_matched_only_cases() -> None:
    triage = build_patient_gap_triage(_coverage(), _clusters())

    zero = triage.loc[triage["patient_id"].eq("zero")].iloc[0]
    partial = triage.loc[triage["patient_id"].eq("partial")].iloc[0]
    routine = triage.loc[triage["patient_id"].eq("routine")].iloc[0]

    assert triage.iloc[0]["patient_id"] == "zero"
    assert zero["triage_priority"] == "p0_blocker"
    assert zero["evaluable_status"] == "not_evaluable_without_source_review"
    assert "zero_parsed_recordings" in zero["issue_flags"]
    assert partial["triage_priority"] == "p1_source_review_required"
    assert "large_seizure_cluster" in partial["issue_flags"]
    assert routine["triage_priority"] == "p2_routine"
    assert routine["issue_flags"] == "none"


def test_horizon_gap_triage_marks_not_main_table_ready_without_claiming_result() -> None:
    triage = build_horizon_gap_triage(_viability())

    long = triage.loc[triage["sop_minutes"].eq(1440)].iloc[0]
    short = triage.loc[triage["sop_minutes"].eq(30)].iloc[0]

    assert long["horizon_status"] == "not_main_table_ready"
    assert "low_valid_window_fraction" in long["issue_flags"]
    assert "high_right_censored_unknown_fraction" in long["issue_flags"]
    assert short["horizon_status"] == "source_review_required"
    assert short["claim_status"] == CLAIM_STATUS


def test_msg_gap_triage_report_and_markdown_are_pre_gate_c() -> None:
    report = build_msg_gap_triage_report(_coverage(), _clusters(), _viability(), dataset="MSG")

    assert report.summary.loc[0, "patients_p0_blocker"] == 1
    assert report.summary.loc[0, "events_unmatched"] == 8
    assert report.summary.loc[0, "horizons_not_main_table_ready"] == 1
    text = msg_gap_triage_markdown(report)
    assert "not citable as a benchmark result before Gate C" in text
    assert "does not report sensitivity" in text
    assert "p0_blocker" in text


def test_build_msg_gap_triage_cli_writes_artifacts(tmp_path: Path) -> None:
    coverage = tmp_path / "coverage.csv"
    clusters = tmp_path / "clusters.csv"
    viability = tmp_path / "viability.csv"
    out_dir = tmp_path / "out"
    _coverage().to_csv(coverage, index=False)
    _clusters().to_csv(clusters, index=False)
    _viability().to_csv(viability, index=False)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/build_msg_gap_triage.py",
            "--coverage-csv",
            str(coverage),
            "--clusters-csv",
            str(clusters),
            "--viability-csv",
            str(viability),
            "--out-dir",
            str(out_dir),
        ],
        check=True,
        cwd=Path(__file__).resolve().parents[1],
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    assert payload["claim_status"] == CLAIM_STATUS
    assert payload["patients_p0_blocker"] == 1
    assert (out_dir / "msg_gap_patient_triage.csv").exists()
    assert (out_dir / "msg_gap_horizon_triage.csv").exists()
    assert (out_dir / "msg_gap_summary.csv").exists()
    assert "not citable" in (out_dir / "msg_gap_triage_report.md").read_text(encoding="utf-8")
