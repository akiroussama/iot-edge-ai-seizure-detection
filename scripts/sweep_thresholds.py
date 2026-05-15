from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.metrics.sweep import threshold_sweep_table
from src.utils.io import read_table, write_table


def main() -> None:
    parser = argparse.ArgumentParser(description="Sweep risk-score thresholds and report clinical metrics.")
    parser.add_argument("--predictions", required=True)
    parser.add_argument("--events", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--sph-minutes", type=float, default=5)
    parser.add_argument("--sop-minutes", type=float, default=30)
    parser.add_argument("--steps", type=int, default=101)
    args = parser.parse_args()
    preds = read_table(args.predictions)
    events = read_table(args.events)
    out = threshold_sweep_table(preds, events, args.sph_minutes, args.sop_minutes, args.steps)
    write_table(out, args.output)
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
