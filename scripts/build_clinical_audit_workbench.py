#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.reports.clinical_audit_workbench import (  # noqa: E402
    build_clinical_audit_workbench,
    clinical_audit_workbench_html,
    clinical_audit_workbench_markdown,
    table_records,
)
from src.utils.io import read_table, write_table  # noqa: E402


def _write_json(report, path: Path) -> None:
    payload = {
        "metadata": report.metadata,
        "summary": table_records(report.summary),
        "review_sheet": table_records(report.review_sheet),
        "timeline_geometry": table_records(report.timeline_geometry),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a static clinical label-audit timeline workbench."
    )
    parser.add_argument("--audit", required=True, help="CSV/parquet from scripts/audit_labels.py")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--title", default="Clinical Timeline Audit Workbench")
    parser.add_argument("--sph-minutes", type=float, required=True)
    parser.add_argument("--sop-minutes", type=float, required=True)
    parser.add_argument("--postictal-exclusion-minutes", type=float, default=None)
    parser.add_argument(
        "--max-events",
        type=int,
        default=20,
        help="Number of events to include. Use --all-events to include every event.",
    )
    parser.add_argument("--all-events", action="store_true")
    parser.add_argument(
        "--selection-strategy",
        choices=["patient_spread", "first"],
        default="patient_spread",
    )
    parser.add_argument(
        "--result-status",
        choices=[
            "pre_gate_c_audit_artifact_not_citable",
            "gate_c_frozen_citable",
            "synthetic_smoke_test_not_citable",
        ],
        default="pre_gate_c_audit_artifact_not_citable",
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
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    if args.all_events:
        max_events = None
    elif args.max_events <= 0:
        raise SystemExit("--max-events must be positive unless --all-events is set")
    else:
        max_events = args.max_events

    audit = read_table(args.audit)
    report = build_clinical_audit_workbench(
        audit,
        sph_minutes=args.sph_minutes,
        sop_minutes=args.sop_minutes,
        postictal_exclusion_minutes=args.postictal_exclusion_minutes,
        max_events=max_events,
        selection_strategy=args.selection_strategy,
        result_status=args.result_status,
        citation_status=args.citation_status,
        gate_c_status=args.gate_c_status,
    )

    out_dir = Path(args.out_dir)
    write_table(report.timeline_geometry, out_dir / "timeline_geometry.csv")
    write_table(report.review_sheet, out_dir / "review_sheet.csv")
    write_table(report.summary, out_dir / "audit_workbench_summary.csv")
    _write_json(report, out_dir / "audit_workbench_report.json")
    (out_dir / "audit_workbench.html").write_text(
        clinical_audit_workbench_html(report, title=args.title),
        encoding="utf-8",
    )
    (out_dir / "audit_workbench.md").write_text(
        clinical_audit_workbench_markdown(report, title=args.title),
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "out_dir": str(out_dir),
                "events_in_workbench": int(report.summary.loc[0, "events_in_workbench"]),
                "review_sheet_rows": int(report.summary.loc[0, "review_sheet_rows"]),
                **report.metadata,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
