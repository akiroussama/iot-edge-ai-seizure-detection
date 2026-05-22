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

from src.reports.gate_b_closeout import (  # noqa: E402
    apply_gate_b_closeout_decisions,
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
        description="Apply human-supplied Gate B closeout decisions to a ledger."
    )
    parser.add_argument("--ledger", required=True)
    parser.add_argument("--decisions", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--run-id", default="gate_b_closeout_2026-05-22")
    parser.add_argument(
        "--source-uri",
        default=None,
        help="Evidence URI/path for the updated ledger. Defaults to --ledger.",
    )
    parser.add_argument(
        "--decision-evidence-status",
        default="human_attested_not_independently_verified",
        help=(
            "Evidence status recorded in summary/manifest, e.g. "
            "human_attested_not_independently_verified or "
            "simulation_positive_not_real_gate_b_evidence."
        ),
    )
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    source_uri = args.source_uri or args.ledger
    package = apply_gate_b_closeout_decisions(
        _read_text_table(args.ledger),
        _read_text_table(args.decisions),
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
                "closed_rows": int(package.summary.loc[0, "closed_rows"]),
                "p0_open_rows": int(package.summary.loc[0, "p0_open_rows"]),
                "claim_status": package.manifest["claim_status"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
