#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.reports.clinical_utility import (  # noqa: E402
    ClinicalUtilityAssumptions,
    ClinicalUtilityConstraints,
    clinical_utility_markdown,
    clinical_utility_table,
)
from src.utils.io import read_table, write_table  # noqa: E402


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Score alarm-threshold policies under configurable clinical utility assumptions."
    )
    parser.add_argument("--sweep", required=True, help="Threshold sweep CSV/parquet/TSV")
    parser.add_argument("--out-csv", required=True)
    parser.add_argument("--out-md", required=True)
    parser.add_argument("--detected-event-benefit", type=float, default=1.0)
    parser.add_argument("--missed-event-cost", type=float, default=1.0)
    parser.add_argument("--false-alarm-cost-per-day", type=float, default=0.1)
    parser.add_argument("--warning-time-cost", type=float, default=0.5)
    parser.add_argument("--lead-time-bonus-per-hour", type=float, default=0.0)
    parser.add_argument("--brier-skill-score-weight", type=float, default=0.0)
    parser.add_argument("--max-far-per-day", type=float, default=None)
    parser.add_argument("--max-time-in-warning", type=float, default=None)
    parser.add_argument("--min-sensitivity", type=float, default=None)
    parser.add_argument(
        "--result-status",
        choices=[
            "pre_gate_c_exploratory_not_citable",
            "gate_c_frozen_citable",
            "synthetic_smoke_test_not_citable",
        ],
        default="pre_gate_c_exploratory_not_citable",
    )
    parser.add_argument(
        "--citation-status",
        choices=["not_citable_pre_gate_c", "citable_after_gate_c", "synthetic_not_citable"],
        default="not_citable_pre_gate_c",
    )
    parser.add_argument(
        "--gate-c-status",
        choices=["not_started", "partial", "passed", "failed"],
        default="not_started",
    )
    parser.add_argument("--title", default="Clinical Utility Analysis")
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    if args.citation_status == "citable_after_gate_c" and args.gate_c_status != "passed":
        raise SystemExit("citable clinical utility reports require --gate-c-status passed")
    assumptions = ClinicalUtilityAssumptions(
        detected_event_benefit=args.detected_event_benefit,
        missed_event_cost=args.missed_event_cost,
        false_alarm_cost_per_day=args.false_alarm_cost_per_day,
        warning_time_cost=args.warning_time_cost,
        lead_time_bonus_per_hour=args.lead_time_bonus_per_hour,
        brier_skill_score_weight=args.brier_skill_score_weight,
    )
    constraints = ClinicalUtilityConstraints(
        max_far_per_day=args.max_far_per_day,
        max_time_in_warning=args.max_time_in_warning,
        min_sensitivity=args.min_sensitivity,
    )
    sweep = read_table(args.sweep)
    utility = clinical_utility_table(
        sweep,
        assumptions=assumptions,
        constraints=constraints,
    )
    utility["result_status"] = args.result_status
    utility["citation_status"] = args.citation_status
    utility["gate_c_status"] = args.gate_c_status
    write_table(utility, args.out_csv)
    out_md = Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(
        clinical_utility_markdown(
            utility,
            assumptions=assumptions,
            constraints=constraints,
            title=args.title,
            citation_status=args.citation_status,
            gate_c_status=args.gate_c_status,
        ),
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "out_csv": args.out_csv,
                "out_md": args.out_md,
                "rows": int(len(utility)),
                "selected_rows": int(utility["selected_under_assumptions"].sum()),
                "result_status": args.result_status,
                "citation_status": args.citation_status,
                "gate_c_status": args.gate_c_status,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
