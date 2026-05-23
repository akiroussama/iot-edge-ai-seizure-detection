#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.reports.gate_b_decision_intake import (  # noqa: E402
    build_gate_b_decision_intake_report,
    table_records,
)
from src.utils.io import read_table, write_table  # noqa: E402


def _read_text_table(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    if path.suffix == ".csv":
        return pd.read_csv(path, keep_default_na=False)
    if path.suffix == ".tsv":
        return pd.read_csv(path, sep="\t", keep_default_na=False)
    return read_table(path)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Preflight real Gate B decisions before applying them to the closeout ledger."
    )
    parser.add_argument("--closeout-ledger", required=True)
    parser.add_argument("--required-decisions", required=True)
    parser.add_argument("--decisions", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--run-id", default="gate_b_real_decision_intake_2026-05-23")
    parser.add_argument(
        "--source-uri",
        default=None,
        help="Evidence URI/path for the supplied decisions. Defaults to --decisions.",
    )
    parser.add_argument(
        "--fail-on-blocked",
        action="store_true",
        help="Exit with status 2 unless the decisions are ready for clean closeout application.",
    )
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    source_uri = args.source_uri or args.decisions
    report = build_gate_b_decision_intake_report(
        closeout_ledger=_read_text_table(args.closeout_ledger),
        required_decisions=_read_text_table(args.required_decisions),
        decisions=_read_text_table(args.decisions),
        run_id=args.run_id,
        source_uri=source_uri,
    )
    out_dir = Path(args.out_dir)
    write_table(report.rows, out_dir / "gate_b_real_decision_intake_rows.csv")
    write_table(report.summary, out_dir / "gate_b_real_decision_intake_summary.csv")
    (out_dir / "gate_b_real_decision_intake_manifest.json").write_text(
        json.dumps(report.manifest, indent=2),
        encoding="utf-8",
    )
    (out_dir / "gate_b_real_decision_intake.json").write_text(
        json.dumps(
            {
                "manifest": report.manifest,
                "summary": table_records(report.summary),
                "rows": table_records(report.rows),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (out_dir / "gate_b_real_decision_intake.md").write_text(
        report.markdown,
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "out_dir": str(out_dir),
                "intake_status": report.manifest["intake_status"],
                "gate_b_next_status": report.manifest["gate_b_next_status"],
                "required_rows": int(report.summary.loc[0, "required_rows"]),
                "accepted_rows": int(report.summary.loc[0, "accepted_rows"]),
                "issue_rows": int(report.summary.loc[0, "issue_rows"]),
                "claim_status": report.manifest["claim_status"],
            },
            indent=2,
        )
    )
    if args.fail_on_blocked and report.manifest["gate_b_next_status"] != (
        "ready_to_apply_closeout_and_run_validation"
    ):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
