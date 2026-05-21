#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.reports.longitudinal_deep_dive import (  # noqa: E402
    LongitudinalDeepDiveConfig,
    build_longitudinal_deep_dive_report,
    longitudinal_deep_dive_markdown,
    table_records,
)
from src.utils.io import read_table, write_table  # noqa: E402


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a descriptive N=1 longitudinal deep-dive report for one patient."
    )
    parser.add_argument("--predictions", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--report-name", default="n1_longitudinal_deep_dive")
    parser.add_argument("--patient-id", default=None)
    parser.add_argument("--patient-col", default="patient_id")
    parser.add_argument("--time-col", default="window_start")
    parser.add_argument("--risk-col", default="risk_score")
    parser.add_argument("--alarm-col", default="alarm")
    parser.add_argument("--label-col", default="forecast_label")
    parser.add_argument("--excluded-col", default="is_excluded")
    parser.add_argument("--segments", type=int, default=6)
    parser.add_argument("--event-neighborhood-rows", type=int, default=3)
    parser.add_argument("--title", default="N=1 Longitudinal Deep Dive")
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    config = LongitudinalDeepDiveConfig(
        patient_id=args.patient_id,
        patient_col=args.patient_col,
        time_col=args.time_col,
        risk_col=args.risk_col,
        alarm_col=args.alarm_col,
        label_col=args.label_col,
        excluded_col=args.excluded_col,
        segments=args.segments,
        event_neighborhood_rows=args.event_neighborhood_rows,
    )
    report = build_longitudinal_deep_dive_report(
        read_table(args.predictions),
        config=config,
        report_name=args.report_name,
    )
    out_dir = Path(args.out_dir)
    write_table(report.patient_selection, out_dir / "n1_patient_selection.csv")
    write_table(report.timeline, out_dir / "n1_timeline.csv")
    write_table(report.segment_summary, out_dir / "n1_segment_summary.csv")
    write_table(report.event_neighborhoods, out_dir / "n1_event_neighborhoods.csv")
    write_table(report.manifest, out_dir / "n1_manifest.csv")
    payload = {
        "metadata": report.metadata,
        "patient_selection": table_records(report.patient_selection),
        "segment_summary": table_records(report.segment_summary),
        "event_neighborhoods": table_records(report.event_neighborhoods),
    }
    (out_dir / "n1_report.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    (out_dir / "n1_report.md").write_text(
        longitudinal_deep_dive_markdown(report, title=args.title),
        encoding="utf-8",
    )
    print(json.dumps({"out_dir": str(out_dir), **report.metadata}, indent=2))


if __name__ == "__main__":
    main()
