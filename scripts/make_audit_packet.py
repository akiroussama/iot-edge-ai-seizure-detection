#!/usr/bin/env python
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.reports.audit_packet import build_label_audit_packet
from src.utils.io import read_table


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a Markdown packet for human label audit.")
    parser.add_argument("--audit", required=True, help="CSV/parquet from scripts/audit_labels.py")
    parser.add_argument("--out", required=True)
    parser.add_argument("--max-events", type=int, default=10)
    parser.add_argument("--title", default="Label Audit Packet")
    args = parser.parse_args()

    audit = read_table(args.audit)
    packet = build_label_audit_packet(audit, max_events=args.max_events, title=args.title)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(packet, encoding="utf-8")
    print({"out": str(out), "events_in_packet": min(args.max_events, audit["event_index"].nunique())})


if __name__ == "__main__":
    main()
