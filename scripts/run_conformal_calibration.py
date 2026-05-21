#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.calibration.conformal import (  # noqa: E402
    build_conformal_report,
    table_records,
)
from src.utils.io import read_table, write_table  # noqa: E402


def _filter_rows(df, expression: str | None, name: str):
    if not expression:
        return df
    if "=" not in expression:
        raise ValueError(f"{name} filter must be formatted as column=value")
    column, value = expression.split("=", maxsplit=1)
    if column not in df.columns:
        raise ValueError(f"{name} filter column not found: {column}")
    return df.loc[df[column].astype(str).eq(value)].reset_index(drop=True)


def _markdown_table(df, max_rows: int = 20) -> str:
    if df.empty:
        return "_No rows._"
    view = df.head(max_rows)
    headers = [str(column) for column in view.columns]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for _, row in view.iterrows():
        lines.append("| " + " | ".join(str(row[column]) for column in view.columns) + " |")
    if len(df) > max_rows:
        lines.append(f"\n_Showing {max_rows} of {len(df)} rows._")
    return "\n".join(lines)


def _write_json(report, path: Path) -> None:
    payload = {
        "metadata": report.metadata,
        "summary": table_records(report.summary),
        "patient_summary": table_records(report.patient_summary),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _write_markdown(report, path: Path) -> None:
    warning = ""
    if report.metadata["citation_status"] != "citable_after_gate_c":
        warning = "\n**Citation status:** not citable as a benchmark result.\n"
    text = f"""# Conformal Risk Interval Report
{warning}
## Metadata

- Method: `{report.metadata["method"]}`
- Alpha: `{report.metadata["alpha"]}`
- Nominal coverage: `{report.metadata["nominal_coverage"]}`
- Global radius: `{report.metadata["global_radius"]}`
- Global calibration rows: `{report.metadata["global_calibration_n"]}`
- Patient-calibrated patients: `{report.metadata["patient_calibrated_count"]}`
- Result status: `{report.metadata["result_status"]}`
- Citation status: `{report.metadata["citation_status"]}`
- Gate C status: `{report.metadata["gate_c_status"]}`

## Summary

{_markdown_table(report.summary)}

## Patient Summary

{_markdown_table(report.patient_summary)}
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Fit split conformal risk intervals and evaluate empirical coverage."
    )
    parser.add_argument("--predictions", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--calibration-filter", required=True, help="Example: split=val")
    parser.add_argument("--evaluation-filter", required=True, help="Example: split=test")
    parser.add_argument("--alpha", type=float, default=0.1)
    parser.add_argument("--method", choices=["global", "patient"], default="patient")
    parser.add_argument("--min-patient-calibration", type=int, default=20)
    parser.add_argument("--patient-col", default="patient_id")
    parser.add_argument("--score-col", default="risk_score")
    parser.add_argument("--label-col", default="forecast_label")
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
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    predictions = read_table(args.predictions)
    calibration = _filter_rows(predictions, args.calibration_filter, "calibration")
    evaluation = _filter_rows(predictions, args.evaluation_filter, "evaluation")
    if calibration.empty:
        raise SystemExit("calibration filter produced no rows")
    if evaluation.empty:
        raise SystemExit("evaluation filter produced no rows")

    report = build_conformal_report(
        calibration,
        evaluation,
        alpha=args.alpha,
        method=args.method,
        patient_col=args.patient_col,
        score_col=args.score_col,
        label_col=args.label_col,
        min_patient_calibration=args.min_patient_calibration,
        result_status=args.result_status,
        citation_status=args.citation_status,
        gate_c_status=args.gate_c_status,
    )

    out_dir = Path(args.out_dir)
    write_table(report.intervals, out_dir / "conformal_intervals.csv")
    write_table(report.summary, out_dir / "conformal_summary.csv")
    write_table(report.patient_summary, out_dir / "conformal_patient_summary.csv")
    _write_json(report, out_dir / "conformal_report.json")
    _write_markdown(report, out_dir / "conformal_report.md")
    print(json.dumps({"out_dir": str(out_dir), **report.metadata}, indent=2))


if __name__ == "__main__":
    main()
