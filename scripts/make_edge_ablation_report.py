#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.reports.edge_ablation import (  # noqa: E402
    EdgeAblationConfig,
    build_edge_ablation_report,
    edge_ablation_markdown,
    table_records,
)
from src.utils.io import read_table, write_table  # noqa: E402


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Join clinical leaderboard rows with traceable edge profiles and "
            "write an edge-aware skill-vs-cost ablation report."
        )
    )
    parser.add_argument("--clinical-rows", required=True)
    parser.add_argument("--edge-profiles", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--report-name", default="edge_aware_ablation")
    parser.add_argument(
        "--skill-metric",
        choices=["auto", "brier_skill_score", "auroc", "auprc", "sensitivity"],
        default="auto",
    )
    parser.add_argument("--latency-budget-ms", type=float, default=100.0)
    parser.add_argument("--ram-budget-kb", type=float, default=512.0)
    parser.add_argument("--flash-budget-kb", type=float, default=1024.0)
    parser.add_argument("--energy-budget-mj", type=float, default=1.0)
    parser.add_argument("--model-size-budget-kb", type=float, default=1024.0)
    parser.add_argument("--parameter-budget", type=float, default=100_000.0)
    parser.add_argument("--allow-missing-traceability", action="store_true")
    parser.add_argument("--title", default="Edge-Aware Ablation Report")
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    config = EdgeAblationConfig(
        skill_metric=args.skill_metric,
        latency_budget_ms=args.latency_budget_ms,
        ram_budget_kb=args.ram_budget_kb,
        flash_budget_kb=args.flash_budget_kb,
        energy_budget_mj=args.energy_budget_mj,
        model_size_budget_kb=args.model_size_budget_kb,
        parameter_budget=args.parameter_budget,
        require_traceability=not args.allow_missing_traceability,
    )
    report = build_edge_ablation_report(
        read_table(args.clinical_rows),
        read_table(args.edge_profiles),
        config=config,
        report_name=args.report_name,
    )
    out_dir = Path(args.out_dir)
    write_table(report.table, out_dir / "edge_ablation_table.csv")
    write_table(report.pareto, out_dir / "edge_pareto_frontier.csv")
    write_table(report.warnings, out_dir / "edge_ablation_warnings.csv")
    write_table(report.manifest, out_dir / "edge_ablation_manifest.csv")
    payload = {
        "metadata": report.metadata,
        "table": table_records(report.table),
        "pareto": table_records(report.pareto),
        "warnings": table_records(report.warnings),
    }
    (out_dir / "edge_ablation_report.json").write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )
    (out_dir / "edge_ablation_report.md").write_text(
        edge_ablation_markdown(report, title=args.title),
        encoding="utf-8",
    )
    print(json.dumps({"out_dir": str(out_dir), **report.metadata}, indent=2))


if __name__ == "__main__":
    main()
