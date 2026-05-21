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
    build_audit_target_table,
    select_audit_targets,
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
        description="Prioritize label-audit events for active human review."
    )
    parser.add_argument("--audit", required=True, help="CSV/parquet from the label audit workflow")
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
    parser.add_argument("--out", required=True, help="Selected audit queue CSV/parquet/TSV")
    parser.add_argument(
        "--candidates-out",
        default=None,
        help="Optional full scored candidate table CSV/parquet/TSV",
    )
    parser.add_argument("--budget", type=int, required=True, help="Number of events to review")
    parser.add_argument(
        "--selection-strategy",
        choices=["top_score", "patient_spread", "random"],
        default="top_score",
    )
    parser.add_argument("--seed", type=int, default=42, help="Seed for random baseline selection")
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
    if args.budget <= 0:
        raise SystemExit("--budget must be positive")

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
    candidates = build_audit_target_table(
        audit,
        predictions_df=predictions,
        reference_predictions=references,
        id_columns=args.id_cols,
        weights=weights,
    )
    selected = select_audit_targets(
        candidates,
        budget=args.budget,
        selection_strategy=args.selection_strategy,
        seed=args.seed,
    )
    write_table(selected, args.out)
    if args.candidates_out:
        write_table(candidates, args.candidates_out)
    print(
        json.dumps(
            {
                "out": args.out,
                "candidates_out": args.candidates_out,
                "candidate_events": int(len(candidates)),
                "selected_events": int(len(selected)),
                "budget": int(args.budget),
                "selection_strategy": args.selection_strategy,
                "reference_names": list(references),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
