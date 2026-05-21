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

from src.reports.statistical_robustness import (  # noqa: E402
    build_statistical_robustness_report,
    statistical_robustness_markdown,
    table_records,
)
from src.utils.io import read_table, write_table  # noqa: E402


def _parse_id_columns(value: str) -> tuple[str, ...]:
    columns = tuple(column.strip() for column in value.split(",") if column.strip())
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


def _write_json(report, path: Path) -> None:
    payload = {
        "metadata": report.metadata,
        "intervals": table_records(report.intervals),
        "permutation": table_records(report.permutation),
        "multiplicity": table_records(report.multiplicity),
        "warnings": table_records(report.warnings),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Write bootstrap confidence intervals, paired permutation tests, "
            "and multiple-comparison correction for forecast prediction tables."
        )
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
    parser.add_argument("--bootstrap-samples", type=int, default=1000)
    parser.add_argument("--permutations", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--ci", type=float, default=0.95)
    parser.add_argument("--patient-col", default="patient_id")
    parser.add_argument("--event-col", default="event_id")
    parser.add_argument("--no-patient-bootstrap", action="store_true")
    parser.add_argument("--no-event-bootstrap", action="store_true")
    parser.add_argument("--min-groups", type=int, default=5)
    parser.add_argument("--max-ci-width", type=float, default=0.5)
    parser.add_argument(
        "--multiplicity-method",
        choices=["benjamini_hochberg", "bonferroni"],
        default="benjamini_hochberg",
    )
    parser.add_argument(
        "--permutation-alternative",
        choices=["greater", "less", "two-sided"],
        default="greater",
    )
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
    parser.add_argument("--title", default="Statistical Robustness Report")
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    predictions = _filter_rows(read_table(args.predictions), args.prediction_filter, "prediction")
    references = {
        name: _filter_rows(read_table(path), args.prediction_filter, f"reference {name}")
        for name, path in args.reference_predictions
    }
    report = build_statistical_robustness_report(
        predictions,
        references,
        model_name=args.model_name,
        id_columns=args.id_cols,
        patient_col=None if args.no_patient_bootstrap else args.patient_col,
        event_col=None if args.no_event_bootstrap else args.event_col,
        n_bootstrap=args.bootstrap_samples,
        n_permutations=args.permutations,
        seed=args.seed,
        ci=args.ci,
        min_groups=args.min_groups,
        max_ci_width=args.max_ci_width,
        multiplicity_method=args.multiplicity_method,
        permutation_alternative=args.permutation_alternative,
        result_status=args.result_status,
        citation_status=args.citation_status,
        gate_c_status=args.gate_c_status,
    )

    out_dir = Path(args.out_dir)
    write_table(report.intervals, out_dir / "robustness_intervals.csv")
    write_table(report.permutation, out_dir / "robustness_permutation.csv")
    write_table(report.multiplicity, out_dir / "robustness_multiplicity.csv")
    write_table(report.warnings, out_dir / "robustness_warnings.csv")
    _write_json(report, out_dir / "robustness_report.json")
    (out_dir / "robustness_report.md").write_text(
        statistical_robustness_markdown(report, title=args.title),
        encoding="utf-8",
    )
    print(json.dumps({"out_dir": str(out_dir), **report.metadata}, indent=2))


if __name__ == "__main__":
    main()
