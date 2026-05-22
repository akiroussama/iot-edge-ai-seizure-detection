#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.reports.federated_benchmark import (  # noqa: E402
    FederatedBenchmarkConfig,
    federated_benchmark_markdown,
    federated_benchmark_summary,
    table_records,
)
from src.utils.io import read_table, write_table  # noqa: E402


def _split_csv(value: str) -> tuple[str, ...]:
    return tuple(item.strip() for item in value.split(",") if item.strip())


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Aggregate site-level leaderboard rows into a federated benchmark report."
    )
    parser.add_argument("--site-results", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--site-col", default="site_id")
    parser.add_argument("--group-cols", default="dataset,task_type,model_name,horizon_name")
    parser.add_argument("--min-sites", type=int, default=2)
    parser.add_argument("--weight-col", default="events_used_for_metrics")
    parser.add_argument(
        "--citation-status",
        choices=["not_citable_pre_gate_c", "citable_after_gate_c"],
        default="not_citable_pre_gate_c",
    )
    parser.add_argument(
        "--gate-c-status",
        choices=["not_started", "partial", "passed", "failed"],
        default="not_started",
    )
    parser.add_argument(
        "--privacy-status",
        default="site_level_metrics_only_no_raw_windows",
    )
    parser.add_argument("--title", default="Federated Benchmark Protocol")
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    config = FederatedBenchmarkConfig(
        site_col=args.site_col,
        group_cols=_split_csv(args.group_cols),
        min_sites=args.min_sites,
        weight_col=args.weight_col,
        citation_status=args.citation_status,
        gate_c_status=args.gate_c_status,
        privacy_status=args.privacy_status,
    )
    report = federated_benchmark_summary(read_table(args.site_results), config=config)
    out_dir = Path(args.out_dir)
    write_table(report.validated_sites, out_dir / "federated_site_results_validated.csv")
    write_table(report.summary, out_dir / "federated_benchmark_summary.csv")
    write_table(report.manifest, out_dir / "federated_benchmark_manifest.csv")
    (out_dir / "federated_benchmark_manifest.json").write_text(
        json.dumps(table_records(report.manifest), indent=2),
        encoding="utf-8",
    )
    (out_dir / "federated_benchmark_report.md").write_text(
        federated_benchmark_markdown(report, title=args.title),
        encoding="utf-8",
    )
    print(json.dumps(report.metadata, indent=2))


if __name__ == "__main__":
    main()
