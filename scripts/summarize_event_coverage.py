#!/usr/bin/env python
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.reports.event_coverage import (
    event_cluster_summary,
    event_coverage_markdown,
    event_coverage_summary,
)
from src.utils.io import read_table, write_table


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize event coverage and seizure clusters.")
    parser.add_argument("--events", required=True)
    parser.add_argument("--recordings", default=None)
    parser.add_argument("--out-md", required=True)
    parser.add_argument("--out-coverage-csv", default=None)
    parser.add_argument("--out-clusters-csv", default=None)
    parser.add_argument("--cluster-gap-minutes", type=float, default=240)
    parser.add_argument("--title", default="Event Coverage And Cluster Summary")
    args = parser.parse_args()

    events = read_table(args.events)
    recordings = read_table(args.recordings) if args.recordings else None
    coverage = event_coverage_summary(events, recordings)
    clusters = event_cluster_summary(events, cluster_gap_minutes=args.cluster_gap_minutes)

    out_md = Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(event_coverage_markdown(coverage, clusters, title=args.title), encoding="utf-8")
    if args.out_coverage_csv:
        write_table(coverage, args.out_coverage_csv)
    if args.out_clusters_csv:
        write_table(clusters, args.out_clusters_csv)
    print({"out_md": str(out_md), "patients": int(coverage["patient_id"].nunique()) if not coverage.empty else 0})


if __name__ == "__main__":
    main()
