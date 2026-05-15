#!/usr/bin/env python
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.reports.horizon_viability import horizon_viability_markdown, horizon_viability_summary
from src.utils.io import read_table, write_table


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Summarize whether candidate SPH/SOP horizons are supported by recording coverage."
    )
    parser.add_argument("--windows", required=True)
    parser.add_argument("--events", required=True)
    parser.add_argument("--out-csv", required=True)
    parser.add_argument("--out-md", required=True)
    parser.add_argument("--sph-minutes", nargs="+", type=float, required=True)
    parser.add_argument("--sop-minutes", nargs="+", type=float, required=True)
    parser.add_argument("--postictal-exclusion-minutes", type=float, default=60)
    parser.add_argument(
        "--postictal-anchor",
        choices=["seizure_end", "seizure_start"],
        default="seizure_end",
    )
    parser.add_argument("--title", default="Horizon Viability Summary")
    args = parser.parse_args()

    windows = read_table(args.windows)
    events = read_table(args.events)
    summary = horizon_viability_summary(
        windows,
        events,
        sph_minutes_values=args.sph_minutes,
        sop_minutes_values=args.sop_minutes,
        postictal_exclusion_minutes=args.postictal_exclusion_minutes,
        postictal_anchor=args.postictal_anchor,
    )
    write_table(summary, args.out_csv)
    out_md = Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(horizon_viability_markdown(summary, title=args.title), encoding="utf-8")
    print({"out_csv": args.out_csv, "out_md": args.out_md, "rows": len(summary)})


if __name__ == "__main__":
    main()
