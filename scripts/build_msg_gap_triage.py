#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.reports.msg_gap_triage import (  # noqa: E402
    MSGGapTriageConfig,
    build_msg_gap_triage_report,
    msg_gap_triage_markdown,
    table_records,
)
from src.utils.io import read_table, write_table  # noqa: E402


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a pre-Gate-C MSG source-data and horizon feasibility triage."
    )
    parser.add_argument("--coverage-csv", required=True, help="Event coverage summary CSV/TSV/parquet")
    parser.add_argument("--clusters-csv", default=None, help="Optional seizure-cluster summary table")
    parser.add_argument("--viability-csv", default=None, help="Optional horizon viability table")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--dataset", default="MSG")
    parser.add_argument("--title", default="MSG Data-Gap Triage")
    parser.add_argument("--min-matched-fraction", type=float, default=0.8)
    parser.add_argument("--max-cluster-size-for-routine", type=int, default=3)
    parser.add_argument("--min-valid-window-fraction", type=float, default=0.5)
    parser.add_argument("--min-event-coverable-fraction", type=float, default=0.5)
    parser.add_argument("--max-right-censored-unknown-fraction", type=float, default=0.25)
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    config = MSGGapTriageConfig(
        min_matched_fraction=args.min_matched_fraction,
        max_cluster_size_for_routine=args.max_cluster_size_for_routine,
        min_valid_window_fraction=args.min_valid_window_fraction,
        min_event_coverable_fraction=args.min_event_coverable_fraction,
        max_right_censored_unknown_fraction=args.max_right_censored_unknown_fraction,
    )
    report = build_msg_gap_triage_report(
        read_table(args.coverage_csv),
        read_table(args.clusters_csv) if args.clusters_csv else None,
        read_table(args.viability_csv) if args.viability_csv else None,
        dataset=args.dataset,
        config=config,
    )
    out_dir = Path(args.out_dir)
    write_table(report.patient_triage, out_dir / "msg_gap_patient_triage.csv")
    write_table(report.horizon_triage, out_dir / "msg_gap_horizon_triage.csv")
    write_table(report.summary, out_dir / "msg_gap_summary.csv")
    write_table(report.manifest, out_dir / "msg_gap_triage_manifest.csv")
    payload = {
        "metadata": report.metadata,
        "summary": table_records(report.summary),
        "patient_triage": table_records(report.patient_triage),
        "horizon_triage": table_records(report.horizon_triage),
    }
    (out_dir / "msg_gap_triage_report.json").write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )
    (out_dir / "msg_gap_triage_report.md").write_text(
        msg_gap_triage_markdown(report, title=args.title),
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "out_dir": str(out_dir),
                "claim_status": report.metadata["claim_status"],
                "patients_total": int(report.summary.loc[0, "patients_total"]),
                "patients_p0_blocker": int(report.summary.loc[0, "patients_p0_blocker"]),
                "events_unmatched": int(report.summary.loc[0, "events_unmatched"]),
                "horizons_not_main_table_ready": int(
                    report.summary.loc[0, "horizons_not_main_table_ready"]
                ),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
