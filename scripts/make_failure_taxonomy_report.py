#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.reports.failure_taxonomy import (  # noqa: E402
    FailureTaxonomyConfig,
    build_failure_taxonomy_report,
    failure_taxonomy_markdown,
    table_records,
)
from src.utils.io import read_table, write_table  # noqa: E402


def _parse_columns(value: str | None) -> tuple[str, ...]:
    if not value:
        return ("patient_id", "recording_id", "window_start", "window_end")
    columns = tuple(column.strip() for column in value.split(",") if column.strip())
    if not columns:
        raise argparse.ArgumentTypeError("id column list cannot be empty")
    return columns


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a post-hoc failure taxonomy from standardized prediction rows."
    )
    parser.add_argument("--predictions", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--model-name", required=True)
    parser.add_argument("--id-cols", type=_parse_columns, default=("patient_id", "recording_id", "window_start", "window_end"))
    parser.add_argument("--risk-col", default="risk_score")
    parser.add_argument("--alarm-col", default="alarm")
    parser.add_argument("--label-col", default="forecast_label")
    parser.add_argument("--excluded-col", default="is_excluded")
    parser.add_argument("--patient-col", default="patient_id")
    parser.add_argument("--high-risk-threshold", type=float, default=0.7)
    parser.add_argument("--low-risk-threshold", type=float, default=0.3)
    parser.add_argument("--title", default="Failure Taxonomy Report")
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    config = FailureTaxonomyConfig(
        risk_col=args.risk_col,
        alarm_col=args.alarm_col,
        label_col=args.label_col,
        excluded_col=args.excluded_col,
        patient_col=args.patient_col,
        high_risk_threshold=args.high_risk_threshold,
        low_risk_threshold=args.low_risk_threshold,
    )
    report = build_failure_taxonomy_report(
        read_table(args.predictions),
        config=config,
        model_name=args.model_name,
        id_columns=args.id_cols,
    )
    out_dir = Path(args.out_dir)
    write_table(report.rows, out_dir / "failure_taxonomy_rows.csv")
    write_table(report.summary, out_dir / "failure_taxonomy_summary.csv")
    write_table(report.patient_summary, out_dir / "failure_taxonomy_patient_summary.csv")
    write_table(report.warnings, out_dir / "failure_taxonomy_warnings.csv")
    write_table(report.manifest, out_dir / "failure_taxonomy_manifest.csv")
    payload = {
        "metadata": report.metadata,
        "summary": table_records(report.summary),
        "patient_summary": table_records(report.patient_summary),
        "warnings": table_records(report.warnings),
    }
    (out_dir / "failure_taxonomy_report.json").write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )
    (out_dir / "failure_taxonomy_report.md").write_text(
        failure_taxonomy_markdown(report, title=args.title),
        encoding="utf-8",
    )
    print(json.dumps({"out_dir": str(out_dir), **report.metadata}, indent=2))


if __name__ == "__main__":
    main()
