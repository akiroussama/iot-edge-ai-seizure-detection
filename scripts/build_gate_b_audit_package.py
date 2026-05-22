#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.active.audit_selection import (  # noqa: E402
    DEFAULT_AUDIT_ID_COLUMNS,
    DEFAULT_AUDIT_SELECTION_WEIGHTS,
)
from src.reports.gate_b_audit_package import (  # noqa: E402
    build_gate_b_audit_package,
    gate_b_audit_package_markdown,
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


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a Gate B manual-audit acceleration package."
    )
    parser.add_argument("--audit", required=True, help="CSV/parquet from label-audit workflow")
    parser.add_argument("--dataset", required=True, help="Dataset label for the package manifest")
    parser.add_argument("--out-dir", required=True, help="Directory for package outputs")
    parser.add_argument(
        "--predictions",
        default=None,
        help="Optional model prediction table aligned to audit windows",
    )
    parser.add_argument(
        "--reference-predictions",
        action="append",
        type=_parse_reference,
        default=[],
        help="Optional null/reference predictions formatted as NAME=PATH. Repeatable.",
    )
    parser.add_argument("--budget", type=int, default=10, help="Number of events to review")
    parser.add_argument("--min-events", type=int, default=5, help="Minimum completed review rows for Gate B validation")
    parser.add_argument(
        "--selection-strategy",
        choices=["top_score", "patient_spread", "random"],
        default="patient_spread",
    )
    parser.add_argument(
        "--id-cols",
        type=_parse_id_columns,
        default=DEFAULT_AUDIT_ID_COLUMNS,
        help="Comma-separated audit/prediction alignment columns",
    )
    parser.add_argument(
        "--uncertainty-weight",
        type=float,
        default=DEFAULT_AUDIT_SELECTION_WEIGHTS["uncertainty"],
    )
    parser.add_argument(
        "--disagreement-weight",
        type=float,
        default=DEFAULT_AUDIT_SELECTION_WEIGHTS["disagreement"],
    )
    parser.add_argument(
        "--clinical-leverage-weight",
        type=float,
        default=DEFAULT_AUDIT_SELECTION_WEIGHTS["clinical_leverage"],
    )
    parser.add_argument(
        "--edge-case-weight",
        type=float,
        default=DEFAULT_AUDIT_SELECTION_WEIGHTS["edge_case"],
    )
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    review_path = out_dir / "gate_b_audit_review_sheet.csv"
    candidates_path = out_dir / "gate_b_audit_candidates.csv"
    manifest_path = out_dir / "gate_b_audit_manifest.json"
    markdown_path = out_dir / "gate_b_audit_package.md"
    validation_path = out_dir / "gate_b_audit_validation.csv"

    audit = read_table(args.audit)
    predictions = read_table(args.predictions) if args.predictions else None
    references = {
        name: read_table(path)
        for name, path in args.reference_predictions
    }
    weights = {
        "uncertainty": args.uncertainty_weight,
        "disagreement": args.disagreement_weight,
        "clinical_leverage": args.clinical_leverage_weight,
        "edge_case": args.edge_case_weight,
    }
    package = build_gate_b_audit_package(
        audit,
        dataset=args.dataset,
        predictions_df=predictions,
        reference_predictions=references,
        budget=args.budget,
        selection_strategy=args.selection_strategy,
        id_columns=args.id_cols,
        weights=weights,
        min_events_required=args.min_events,
        audit_source=args.audit,
        prediction_source=args.predictions,
    )
    write_table(package.review_sheet, review_path)
    write_table(package.candidates, candidates_path)
    manifest_path.write_text(json.dumps(package.manifest, indent=2), encoding="utf-8")
    markdown = gate_b_audit_package_markdown(
        manifest=package.manifest,
        review_sheet=package.review_sheet,
        review_sheet_path=str(review_path),
        candidates_path=str(candidates_path),
        validation_path=str(validation_path),
    )
    markdown_path.write_text(markdown, encoding="utf-8")
    print(
        json.dumps(
            {
                "package_status": package.manifest["package_status"],
                "dataset": args.dataset,
                "review_sheet": str(review_path),
                "candidates": str(candidates_path),
                "manifest": str(manifest_path),
                "markdown": str(markdown_path),
                "selected_events": package.manifest["selected_events"],
                "candidate_events": package.manifest["candidate_events"],
                "minimum_event_budget_met": package.manifest["minimum_event_budget_met"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
