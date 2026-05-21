#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.features.observability import (  # noqa: E402
    ObservabilityConfig,
    add_observability_features,
    apply_observability_abstention,
    observability_markdown,
    observability_metric_strata,
    observability_summary,
    table_records,
)
from src.utils.io import read_table, write_table  # noqa: E402


def _parse_modalities(value: str) -> tuple[str, ...]:
    modalities = tuple(item.strip().lower() for item in value.split(",") if item.strip())
    if not modalities:
        raise argparse.ArgumentTypeError("--modalities must contain at least one modality")
    return modalities


def _write_json(payload: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compute wearable observability, deficiency time, and abstention reports."
    )
    parser.add_argument("--features", required=True, help="Feature or prediction table")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--modalities", type=_parse_modalities, default=("hr", "acc"))
    parser.add_argument("--min-coverage-fraction", type=float, default=0.7)
    parser.add_argument("--max-dropout-fraction", type=float, default=0.3)
    parser.add_argument("--observable-threshold", type=float, default=0.65)
    parser.add_argument("--max-abstention-fraction", type=float, default=None)
    parser.add_argument("--title", default="Observability And Missingness Report")
    parser.add_argument(
        "--group-cols",
        default="",
        help="Comma-separated grouping columns for summary, e.g. split,patient_id.",
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
    if args.citation_status == "citable_after_gate_c" and args.gate_c_status != "passed":
        raise SystemExit("citable observability reports require --gate-c-status passed")
    group_cols = tuple(item.strip() for item in args.group_cols.split(",") if item.strip())
    config = ObservabilityConfig(
        modalities=args.modalities,
        min_coverage_fraction=args.min_coverage_fraction,
        max_dropout_fraction=args.max_dropout_fraction,
        observable_threshold=args.observable_threshold,
    )
    features = read_table(args.features)
    enriched = add_observability_features(features, config=config)
    enriched = apply_observability_abstention(
        enriched,
        max_abstention_fraction=args.max_abstention_fraction,
    )
    summary = observability_summary(enriched, group_cols=group_cols)
    strata = observability_metric_strata(enriched)

    out_dir = Path(args.out_dir)
    write_table(enriched, out_dir / "observability_enriched.csv")
    write_table(summary, out_dir / "observability_summary.csv")
    write_table(strata, out_dir / "observability_metric_strata.csv")
    payload = {
        "metadata": {
            "modalities": list(args.modalities),
            "min_coverage_fraction": args.min_coverage_fraction,
            "max_dropout_fraction": args.max_dropout_fraction,
            "observable_threshold": args.observable_threshold,
            "max_abstention_fraction": args.max_abstention_fraction,
            "citation_status": args.citation_status,
            "gate_c_status": args.gate_c_status,
        },
        "summary": table_records(summary),
        "metric_strata": table_records(strata),
    }
    _write_json(payload, out_dir / "observability_report.json")
    (out_dir / "observability_report.md").write_text(
        observability_markdown(
            enriched,
            summary,
            strata,
            title=args.title,
            citation_status=args.citation_status,
            gate_c_status=args.gate_c_status,
        ),
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "out_dir": str(out_dir),
                "rows": int(len(enriched)),
                "observable_rows": int(enriched["is_observable"].sum()),
                "abstained_rows": int(enriched["abstain_for_observability"].sum()),
                "citation_status": args.citation_status,
                "gate_c_status": args.gate_c_status,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
