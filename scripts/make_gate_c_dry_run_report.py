#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.artifacts.registry import load_registry  # noqa: E402
from src.reports.gate_c_dry_run import build_gate_c_dry_run_report  # noqa: E402
from src.utils.io import write_table  # noqa: E402


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create a non-citable Gate C dry-run diagnostics report."
    )
    parser.add_argument("--registry", required=True, help="Gate C registry JSON")
    parser.add_argument("--out-json", required=True, help="Diagnostics JSON output")
    parser.add_argument("--out-md", required=True, help="Markdown diagnostics output")
    parser.add_argument(
        "--artifact-summary-out",
        default=None,
        help="Optional CSV/parquet/TSV artifact summary output",
    )
    parser.add_argument("--root", default=".")
    parser.add_argument("--split-col", default="split")
    parser.add_argument(
        "--gate-b-status",
        choices=["not_started", "partial", "passed", "failed"],
        default="not_started",
    )
    parser.add_argument(
        "--required-role",
        action="append",
        default=None,
        help="Required artifact role for this dry run. Repeatable. Defaults to events, labels, splits.",
    )
    parser.add_argument(
        "--allow-missing-prereg",
        action="store_true",
        help="Do not block on a missing DOI/preregistration URI.",
    )
    parser.add_argument(
        "--fail-on-blockers",
        action="store_true",
        help="Exit with status 2 when dry-run blockers are present.",
    )
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    report = build_gate_c_dry_run_report(
        load_registry(args.registry),
        root=args.root,
        gate_b_status=args.gate_b_status,
        required_roles=tuple(args.required_role) if args.required_role else ("events", "labels", "splits"),
        require_prereg=not args.allow_missing_prereg,
        split_col=args.split_col,
    )
    out_json = Path(args.out_json)
    out_md = Path(args.out_md)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report.diagnostics, indent=2), encoding="utf-8")
    out_md.write_text(report.markdown, encoding="utf-8")
    if args.artifact_summary_out:
        write_table(report.artifact_summary, args.artifact_summary_out)
    print(
        json.dumps(
            {
                "out_json": str(out_json),
                "out_md": str(out_md),
                "readiness_status": report.diagnostics["readiness_status"],
                "citable_ready": report.diagnostics["citable_ready"],
                "blockers": len(report.diagnostics["blockers"]),
                "warnings": len(report.diagnostics["warnings"]),
            },
            indent=2,
        )
    )
    if args.fail_on_blockers and report.diagnostics["blockers"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
