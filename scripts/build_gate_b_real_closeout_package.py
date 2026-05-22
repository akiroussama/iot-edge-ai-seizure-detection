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
    build_gate_b_real_closeout_package,
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
        description="Build a real Gate B closeout package without promoting simulation evidence."
    )
    parser.add_argument("--ledger", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--run-id", default="gate_b_real_closeout_2026-05-22")
    parser.add_argument(
        "--source-uri",
        default=None,
        help="Evidence URI/path for the real ledger. Defaults to --ledger.",
    )
    parser.add_argument(
        "--simulation-decisions",
        default=None,
        help="Optional simulation decisions CSV used only as non-promoted reviewer-intent hints.",
    )
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    source_uri = args.source_uri or args.ledger
    simulation_decisions = (
        _read_text_table(args.simulation_decisions) if args.simulation_decisions else None
    )
    package = build_gate_b_real_closeout_package(
        _read_text_table(args.ledger),
        source_uri=source_uri,
        run_id=args.run_id,
        simulation_decisions=simulation_decisions,
    )
    out_dir = Path(args.out_dir)
    write_table(package.readiness, out_dir / "gate_b_real_closeout_readiness.csv")
    write_table(package.template, out_dir / "gate_b_real_closeout_required_decisions_template.csv")
    write_table(package.summary, out_dir / "gate_b_real_closeout_summary.csv")
    (out_dir / "gate_b_real_closeout_manifest.json").write_text(
        json.dumps(package.manifest, indent=2),
        encoding="utf-8",
    )
    (out_dir / "gate_b_real_closeout.json").write_text(
        json.dumps(
            {
                "manifest": package.manifest,
                "summary": table_records(package.summary),
                "readiness": table_records(package.readiness),
                "template": table_records(package.template),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (out_dir / "gate_b_real_closeout.md").write_text(package.markdown, encoding="utf-8")
    print(
        json.dumps(
            {
                "out_dir": str(out_dir),
                "gate_b_real_closeout_status": package.manifest["gate_b_real_closeout_status"],
                "ledger_rows": package.manifest["ledger_rows"],
                "real_closed_rows": package.manifest["real_closed_rows"],
                "real_open_rows": package.manifest["real_open_rows"],
                "simulation_available_open_rows": package.manifest[
                    "simulation_available_open_rows"
                ],
                "claim_status": package.manifest["claim_status"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
