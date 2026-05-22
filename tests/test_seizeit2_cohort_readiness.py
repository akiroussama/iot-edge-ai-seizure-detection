from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pandas as pd

from src.reports.seizeit2_cohort_readiness import (
    CLAIM_STATUS,
    build_seizeit2_cohort_readiness_report,
    seizeit2_cohort_readiness_markdown,
)
from src.utils.io import write_table


def _ready_track() -> pd.DataFrame:
    rows = []
    for split in ("train", "val", "test"):
        for task in ("ictal_detection", "short_early_warning", "long_horizon_forecasting"):
            for modality in ("ecg", "acc", "bte_eeg", "multimodal"):
                rows.append(
                    {
                        "split_name": split,
                        "task_name": task,
                        "modality_track": modality,
                        "official_split_status": "official_manifest_applied",
                        "track_ready": True,
                    }
                )
    return pd.DataFrame(rows)


def _ready_counts() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "metric": ["patients", "recordings", "events", "windows"],
            "observed": [125, 400, 883, 12000],
            "expected": [125, 400, 883, None],
            "count_status": [
                "matches_expected_count",
                "matches_expected_count",
                "matches_expected_count",
                "expected_count_not_provided",
            ],
        }
    )


def _blocked_track() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "split_name": ["unassigned"],
            "task_name": ["ictal_detection"],
            "modality_track": ["ecg"],
            "official_split_status": ["missing_official_manifest"],
            "track_ready": [False],
        }
    )


def _blocked_counts() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "metric": ["patients", "recordings", "events"],
            "observed": [1, 1, 1],
            "expected": [None, None, None],
            "count_status": ["expected_count_not_provided"] * 3,
        }
    )


def test_cohort_readiness_blocks_smoke_subset_claims() -> None:
    report = build_seizeit2_cohort_readiness_report(_blocked_track(), _blocked_counts())

    codes = set(report.blockers["issue_code"])
    assert report.summary.loc[0, "readiness_status"] == "blocked"
    assert report.summary.loc[0, "full_cohort_claim_status"] == "blocked_not_full_cohort_ready"
    assert "gate_b_not_passed" in codes
    assert "gate_c_not_passed" in codes
    assert "patients_below_full_cohort_threshold" in codes
    assert "events_below_full_cohort_threshold" in codes
    assert "official_split_manifest_not_clean" in codes
    assert "required_splits_missing" in codes
    assert report.summary.loc[0, "claim_status"] == CLAIM_STATUS


def test_cohort_readiness_can_pass_only_after_gate_b_c_and_clean_counts() -> None:
    report = build_seizeit2_cohort_readiness_report(
        _ready_track(),
        _ready_counts(),
        gate_b_status="passed",
        gate_c_status="passed",
    )

    assert report.blockers.empty
    assert report.summary.loc[0, "readiness_status"] == "ready_for_gate_c_review"
    assert report.summary.loc[0, "full_cohort_claim_status"] == "candidate_after_gate_b_c"
    assert report.summary.loc[0, "ready_track_rows"] == len(_ready_track())
    text = seizeit2_cohort_readiness_markdown(report)
    assert "not citable as a benchmark result before Gate C" in text
    assert "does not train or score a model" in text


def test_build_seizeit2_cohort_readiness_cli_writes_outputs(tmp_path: Path) -> None:
    track_path = tmp_path / "track.csv"
    counts_path = tmp_path / "counts.csv"
    out_dir = tmp_path / "out"
    write_table(_ready_track(), track_path)
    write_table(_ready_counts(), counts_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/build_seizeit2_cohort_readiness.py",
            "--track-csv",
            str(track_path),
            "--count-summary-csv",
            str(counts_path),
            "--out-dir",
            str(out_dir),
            "--gate-b-status",
            "passed",
            "--gate-c-status",
            "passed",
        ],
        check=True,
        cwd=Path(__file__).resolve().parents[1],
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    assert payload["readiness_status"] == "ready_for_gate_c_review"
    assert payload["claim_status"] == CLAIM_STATUS
    assert (out_dir / "seizeit2_cohort_readiness_summary.csv").exists()
    assert (out_dir / "seizeit2_cohort_readiness_blockers.csv").exists()
    report_text = (out_dir / "seizeit2_cohort_readiness_report.md").read_text(
        encoding="utf-8"
    )
    assert "full-cohort claim guardrail" in report_text
