#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.reports.gate_b_closeout import (  # noqa: E402
    build_gate_b_closeout_ledger,
    table_records,
)
from src.utils.io import read_table, write_table  # noqa: E402


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a human-fillable Gate B closeout ledger from guardrail actions."
    )
    parser.add_argument("--action-checklist", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--run-id", default="gate_b_closeout_2026-05-22")
    parser.add_argument(
        "--source-uri",
        default=None,
        help="Evidence URI/path for the action checklist. Defaults to --action-checklist.",
    )
    parser.add_argument(
        "--decision-evidence-status",
        default="pending_human_review",
        help="Evidence status recorded in summary/manifest.",
    )
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    source_uri = args.source_uri or args.action_checklist
    package = build_gate_b_closeout_ledger(
        read_table(args.action_checklist),
        source_uri=source_uri,
        run_id=args.run_id,
        decision_evidence_status=args.decision_evidence_status,
    )
    out_dir = Path(args.out_dir)
    write_table(package.ledger, out_dir / "gate_b_closeout_ledger.csv")
    write_table(package.summary, out_dir / "gate_b_closeout_summary.csv")
    (out_dir / "gate_b_closeout_manifest.json").write_text(
        json.dumps(package.manifest, indent=2),
        encoding="utf-8",
    )
    (out_dir / "gate_b_closeout_ledger.json").write_text(
        json.dumps(
            {
                "manifest": package.manifest,
                "summary": table_records(package.summary),
                "ledger": table_records(package.ledger),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (out_dir / "gate_b_closeout_ledger.md").write_text(package.markdown, encoding="utf-8")
    print(
        json.dumps(
            {
                "out_dir": str(out_dir),
                "gate_b_status": package.manifest["gate_b_status"],
                "ledger_rows": package.manifest["ledger_rows"],
                "open_rows": package.manifest["open_rows"],
                "claim_status": package.manifest["claim_status"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
