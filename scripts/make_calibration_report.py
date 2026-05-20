#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import pandas as pd

from src.reports.calibration_skill import (
    build_calibration_skill_report,
    table_records,
)
from src.utils.io import read_table, write_table


def _parse_id_columns(value: str) -> tuple[str, ...]:
    columns = tuple(col.strip() for col in value.split(",") if col.strip())
    if not columns:
        raise argparse.ArgumentTypeError("--id-cols must contain at least one column")
    return columns


def _parse_reference(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise argparse.ArgumentTypeError(
            "--reference-predictions must be formatted as NAME=PATH"
        )
    name, path = value.split("=", maxsplit=1)
    name = name.strip()
    if not name:
        raise argparse.ArgumentTypeError("reference name cannot be empty")
    return name, Path(path)


def _filter_rows(df: pd.DataFrame, expression: str | None, name: str) -> pd.DataFrame:
    if not expression:
        return df
    if "=" not in expression:
        raise ValueError(f"{name} filter must be formatted as column=value")
    column, value = expression.split("=", maxsplit=1)
    if column not in df.columns:
        raise ValueError(f"{name} filter column not found: {column}")
    return df.loc[df[column].astype(str).eq(value)].reset_index(drop=True)


def _markdown_table(df: pd.DataFrame, max_rows: int = 20) -> str:
    if df.empty:
        return "_No rows._"
    view = df.head(max_rows)
    headers = [str(col) for col in view.columns]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for _, row in view.iterrows():
        lines.append("| " + " | ".join(str(row[col]) for col in view.columns) + " |")
    if len(df) > max_rows:
        lines.append(f"\n_Showing {max_rows} of {len(df)} rows._")
    return "\n".join(lines)


def _write_json(report, path: Path) -> None:
    payload = {
        "metadata": report.metadata,
        "summary": table_records(report.summary),
        "skill": table_records(report.skill),
        "reliability": table_records(report.reliability),
        "bootstrap": table_records(report.bootstrap),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _write_markdown(report, path: Path) -> None:
    warning = ""
    if report.metadata["citation_status"] != "citable_after_gate_c":
        warning = "\n**Citation status:** not citable as a benchmark result.\n"
    text = f"""# Calibration And Null-Corrected Skill Report
{warning}
## Metadata

- Model: `{report.metadata["model_name"]}`
- References: `{", ".join(report.metadata["reference_names"])}`
- Result status: `{report.metadata["result_status"]}`
- Citation status: `{report.metadata["citation_status"]}`
- Gate C status: `{report.metadata["gate_c_status"]}`
- Bootstrap samples: `{report.metadata["n_bootstrap"]}`

## Summary

{_markdown_table(report.summary)}

## Brier Skill Score

{_markdown_table(report.skill)}

## Bootstrap Confidence Intervals

{_markdown_table(report.bootstrap)}

## Reliability Bins

{_markdown_table(report.reliability)}
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Write calibration, BSS, reliability, and bootstrap reports."
    )
    parser.add_argument("--predictions", required=True)
    parser.add_argument(
        "--reference-predictions",
        action="append",
        type=_parse_reference,
        required=True,
        help="Reference prediction table, formatted as NAME=PATH. Repeat for multiple nulls.",
    )
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--model-name", required=True)
    parser.add_argument("--prediction-filter", default=None)
    parser.add_argument(
        "--id-cols",
        type=_parse_id_columns,
        default=("patient_id", "recording_id", "window_start", "window_end"),
    )
    parser.add_argument("--n-bins", type=int, default=10)
    parser.add_argument("--bootstrap-samples", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--patient-col", default="patient_id")
    parser.add_argument("--event-col", default="event_id")
    parser.add_argument("--no-patient-bootstrap", action="store_true")
    parser.add_argument("--no-event-bootstrap", action="store_true")
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
    predictions = _filter_rows(read_table(args.predictions), args.prediction_filter, "prediction")
    references = {
        name: _filter_rows(read_table(path), args.prediction_filter, f"reference {name}")
        for name, path in args.reference_predictions
    }
    report = build_calibration_skill_report(
        predictions,
        references,
        model_name=args.model_name,
        id_columns=args.id_cols,
        n_bins=args.n_bins,
        n_bootstrap=args.bootstrap_samples,
        seed=args.seed,
        patient_col=None if args.no_patient_bootstrap else args.patient_col,
        event_col=None if args.no_event_bootstrap else args.event_col,
        result_status=args.result_status,
        citation_status=args.citation_status,
        gate_c_status=args.gate_c_status,
    )

    out_dir = Path(args.out_dir)
    write_table(report.summary, out_dir / "calibration_summary.csv")
    write_table(report.skill, out_dir / "calibration_skill.csv")
    write_table(report.reliability, out_dir / "calibration_reliability.csv")
    write_table(report.bootstrap, out_dir / "calibration_bootstrap.csv")
    _write_json(report, out_dir / "calibration_report.json")
    _write_markdown(report, out_dir / "calibration_report.md")
    print(json.dumps({"out_dir": str(out_dir), **report.metadata}, indent=2))


if __name__ == "__main__":
    main()
