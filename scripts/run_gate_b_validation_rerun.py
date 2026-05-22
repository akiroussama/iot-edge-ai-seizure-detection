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

from src.reports.gate_b_validation import (  # noqa: E402
    build_gate_b_validation_rerun_report,
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
        description="Validate real Gate B closeout against a local guardrail rerun."
    )
    parser.add_argument("--closeout-ledger", required=True)
    parser.add_argument("--guardrails-dir", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--run-id", default="gate_b_validation_rerun_2026-05-22")
    parser.add_argument(
        "--source-uri",
        default=None,
        help="Evidence URI/path for this validation rerun. Defaults to --guardrails-dir.",
    )
    parser.add_argument(
        "--closeout-summary",
        default=None,
        help="Optional real closeout summary CSV produced by build_gate_b_real_closeout_package.py.",
    )
    parser.add_argument(
        "--fail-on-blocked",
        action="store_true",
        help="Exit with status 2 unless Gate B validation passes.",
    )
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    guardrails_dir = Path(args.guardrails_dir)
    source_uri = args.source_uri or str(guardrails_dir)
    closeout_summary = _read_text_table(args.closeout_summary) if args.closeout_summary else None
    report = build_gate_b_validation_rerun_report(
        closeout_ledger=_read_text_table(args.closeout_ledger),
        action_checklist=_read_text_table(guardrails_dir / "gate_bc_action_checklist.csv"),
        msg_summary=_read_text_table(guardrails_dir / "msg_gap_summary.csv"),
        seizeit2_summary=_read_text_table(
            guardrails_dir / "seizeit2_cohort_readiness_summary.csv"
        ),
        run_id=args.run_id,
        source_uri=source_uri,
        closeout_summary=closeout_summary,
    )
    out_dir = Path(args.out_dir)
    write_table(report.matrix, out_dir / "gate_b_validation_matrix.csv")
    write_table(report.summary, out_dir / "gate_b_validation_summary.csv")
    (out_dir / "gate_b_validation_manifest.json").write_text(
        json.dumps(report.manifest, indent=2),
        encoding="utf-8",
    )
    (out_dir / "gate_b_validation_rerun.json").write_text(
        json.dumps(
            {
                "manifest": report.manifest,
                "summary": table_records(report.summary),
                "matrix": table_records(report.matrix),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (out_dir / "gate_b_validation_rerun.md").write_text(report.markdown, encoding="utf-8")
    print(
        json.dumps(
            {
                "out_dir": str(out_dir),
                "gate_b_validation_status": report.manifest["gate_b_validation_status"],
                "gate_b_passed": report.manifest["gate_b_passed"],
                "gate_b_open_actions": int(report.summary.loc[0, "gate_b_open_actions"]),
                "gate_b_p0_open_actions": int(report.summary.loc[0, "gate_b_p0_open_actions"]),
                "claim_status": report.manifest["claim_status"],
            },
            indent=2,
        )
    )
    if args.fail_on_blocked and not report.manifest["gate_b_passed"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
