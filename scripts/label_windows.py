from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.labeling.sph_sop import label_forecast_windows
from src.utils.io import read_table, write_table


def main() -> None:
    parser = argparse.ArgumentParser(description="Create SPH/SOP forecasting labels.")
    parser.add_argument("--windows", required=True)
    parser.add_argument("--events", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--sph-minutes", type=float, default=5)
    parser.add_argument("--sop-minutes", type=float, default=30)
    parser.add_argument("--postictal-exclusion-minutes", type=float, default=60)
    parser.add_argument("--include-ictal", action="store_true")
    args = parser.parse_args()

    windows = read_table(args.windows)
    events = read_table(args.events)
    labeled = label_forecast_windows(
        windows,
        events,
        sph_minutes=args.sph_minutes,
        sop_minutes=args.sop_minutes,
        postictal_exclusion_minutes=args.postictal_exclusion_minutes,
        ictal_exclusion=not args.include_ictal,
    )
    write_table(labeled, args.output)
    print(f"wrote {args.output} with {len(labeled)} windows")


if __name__ == "__main__":
    main()
