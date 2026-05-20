#!/usr/bin/env python
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.reports.label_audit import validate_label_audit_review_sheet
from src.utils.io import read_table, write_table


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate that a human label-audit review sheet is complete and passing."
    )
    parser.add_argument("--review-sheet", required=True, help="CSV/parquet/TSV review sheet")
    parser.add_argument("--out", help="Optional CSV/parquet/TSV validation report")
    parser.add_argument("--min-events", type=int, default=5)
    args = parser.parse_args()

    review = read_table(args.review_sheet)
    report = validate_label_audit_review_sheet(review, min_events=args.min_events)
    if args.out:
        write_table(report, args.out)

    passed = bool(report["passed"].all()) if not report.empty else False
    print(report.to_string(index=False))
    if not passed:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
