from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import argparse

from src.baselines.random_rate_matched import generate_random_rate_matched_alarms
from src.datasets.seizeit2_loader import make_synthetic_seizeit2_tables
from src.labeling.sph_sop import label_forecast_windows
from src.utils.io import read_table, write_table


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--synthetic", action="store_true")
    parser.add_argument("--labels", default=None, help="Use an existing labeled windows table instead of relabeling.")
    parser.add_argument("--windows", default=None)
    parser.add_argument("--events", default=None)
    parser.add_argument("--out", default="reports/synthetic_predictions.csv")
    parser.add_argument("--sph-minutes", type=float, default=5)
    parser.add_argument("--sop-minutes", type=float, default=30)
    parser.add_argument("--postictal-exclusion-minutes", type=float, default=60)
    parser.add_argument("--tiw", type=float, default=0.1)
    args = parser.parse_args()

    if args.synthetic:
        _, windows, events = make_synthetic_seizeit2_tables()
        labeled = label_forecast_windows(
            windows,
            events,
            args.sph_minutes,
            args.sop_minutes,
            postictal_exclusion_minutes=args.postictal_exclusion_minutes,
        )
    elif args.labels:
        labeled = read_table(args.labels)
        events = None
    else:
        if not args.windows or not args.events:
            raise SystemExit("Provide --labels or both --windows and --events unless using --synthetic")
        windows = read_table(args.windows)
        events = read_table(args.events)
        labeled = label_forecast_windows(
            windows,
            events,
            args.sph_minutes,
            args.sop_minutes,
            postictal_exclusion_minutes=args.postictal_exclusion_minutes,
        )
    preds = generate_random_rate_matched_alarms(labeled, args.tiw, seed=42)
    write_table(preds, args.out)
    if args.synthetic and events is not None:
        write_table(events, Path(args.out).parent / f"synthetic_events{Path(args.out).suffix}")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
