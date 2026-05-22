#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.reports.seizeit2_cohort_readiness import (  # noqa: E402
    SeizeIT2CohortReadinessConfig,
    build_seizeit2_cohort_readiness_report,
    seizeit2_cohort_readiness_markdown,
    table_records,
)
from src.utils.io import read_table, write_table  # noqa: E402


def _parse_list(value: str) -> tuple[str, ...]:
    parsed = tuple(item.strip() for item in value.split(",") if item.strip())
    if not parsed:
        raise argparse.ArgumentTypeError("comma-separated list cannot be empty")
    return parsed


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a SeizeIT2 full-cohort readiness guardrail report."
    )
    parser.add_argument("--track-csv", required=True)
    parser.add_argument("--count-summary-csv", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--gate-b-status", default="not_started")
    parser.add_argument("--gate-c-status", default="not_started")
    parser.add_argument("--min-patients-for-full-cohort", type=int, default=100)
    parser.add_argument("--min-events-for-full-cohort", type=int, default=100)
    parser.add_argument("--required-splits", type=_parse_list, default=("train", "val", "test"))
    parser.add_argument(
        "--required-task-names",
        type=_parse_list,
        default=("ictal_detection", "short_early_warning", "long_horizon_forecasting"),
    )
    parser.add_argument(
        "--required-modality-tracks",
        type=_parse_list,
        default=("ecg", "acc", "bte_eeg", "multimodal"),
    )
    parser.add_argument(
        "--allow-missing-expected-counts",
        action="store_true",
        help="Treat missing expected published counts as warnings handled outside this report.",
    )
    parser.add_argument("--fail-on-blockers", action="store_true")
    parser.add_argument("--title", default="SeizeIT2 Cohort Readiness")
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    config = SeizeIT2CohortReadinessConfig(
        min_patients_for_full_cohort=args.min_patients_for_full_cohort,
        min_events_for_full_cohort=args.min_events_for_full_cohort,
        required_splits=args.required_splits,
        required_task_names=args.required_task_names,
        required_modality_tracks=args.required_modality_tracks,
        require_expected_counts=not args.allow_missing_expected_counts,
    )
    report = build_seizeit2_cohort_readiness_report(
        read_table(args.track_csv),
        read_table(args.count_summary_csv),
        gate_b_status=args.gate_b_status,
        gate_c_status=args.gate_c_status,
        config=config,
    )
    out_dir = Path(args.out_dir)
    write_table(report.summary, out_dir / "seizeit2_cohort_readiness_summary.csv")
    write_table(report.blockers, out_dir / "seizeit2_cohort_readiness_blockers.csv")
    write_table(report.warnings, out_dir / "seizeit2_cohort_readiness_warnings.csv")
    write_table(report.manifest, out_dir / "seizeit2_cohort_readiness_manifest.csv")
    payload = {
        "metadata": report.metadata,
        "summary": table_records(report.summary),
        "blockers": table_records(report.blockers),
        "warnings": table_records(report.warnings),
    }
    (out_dir / "seizeit2_cohort_readiness_report.json").write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )
    (out_dir / "seizeit2_cohort_readiness_report.md").write_text(
        seizeit2_cohort_readiness_markdown(report, title=args.title),
        encoding="utf-8",
    )
    summary = report.summary.iloc[0].to_dict()
    print(
        json.dumps(
            {
                "out_dir": str(out_dir),
                "readiness_status": summary["readiness_status"],
                "full_cohort_claim_status": summary["full_cohort_claim_status"],
                "blockers": int(summary["blockers"]),
                "warnings": int(summary["warnings"]),
                "claim_status": summary["claim_status"],
            },
            indent=2,
        )
    )
    if args.fail_on_blockers and int(summary["blockers"]) > 0:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
