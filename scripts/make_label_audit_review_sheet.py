#!/usr/bin/env python
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.reports.label_audit import build_label_audit_review_sheet
from src.utils.io import read_table, write_table


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create a one-row-per-event manual label audit review sheet."
    )
    parser.add_argument("--audit", required=True, help="CSV/parquet from scripts/audit_labels.py")
    parser.add_argument("--out", required=True, help="CSV/parquet/TSV review sheet destination")
    parser.add_argument(
        "--max-events",
        type=int,
        default=10,
        help="Number of audit events to include. Use 0 with --all-events for all events.",
    )
    parser.add_argument(
        "--all-events",
        action="store_true",
        help="Include every event present in the audit table.",
    )
    parser.add_argument(
        "--selection-strategy",
        choices=["patient_spread", "first"],
        default="patient_spread",
        help="How to select events when --max-events limits the review sheet.",
    )
    args = parser.parse_args()
    if args.all_events:
        max_events = None
    elif args.max_events <= 0:
        raise SystemExit("--max-events must be positive unless --all-events is set")
    else:
        max_events = args.max_events

    audit = read_table(args.audit)
    sheet = build_label_audit_review_sheet(
        audit,
        max_events=max_events,
        selection_strategy=args.selection_strategy,
    )
    write_table(sheet, args.out)
    print({"out": args.out, "events_in_sheet": len(sheet)})


if __name__ == "__main__":
    main()
