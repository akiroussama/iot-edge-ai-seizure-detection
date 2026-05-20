from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import argparse

from src.reports.label_audit import build_label_audit_table
from src.utils.io import read_table, write_table


def main() -> None:
    parser = argparse.ArgumentParser(description="Export seizure-centered label audit timelines.")
    parser.add_argument("--labels", required=True)
    parser.add_argument("--events", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--minutes-before", type=float, default=60)
    parser.add_argument("--minutes-after", type=float, default=60)
    args = parser.parse_args()

    labels = read_table(args.labels)
    events = read_table(args.events)
    audit = build_label_audit_table(
        labels,
        events,
        minutes_before=args.minutes_before,
        minutes_after=args.minutes_after,
    )
    write_table(audit, args.out)
    print(f"wrote {args.out} with {len(audit)} audit rows")


if __name__ == "__main__":
    main()
