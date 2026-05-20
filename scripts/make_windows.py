from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import argparse
from pathlib import Path

from src.datasets.seizeit2_loader import make_synthetic_seizeit2_tables
from src.preprocessing.windowing import generate_fixed_windows
from src.utils.io import read_table, write_table


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--synthetic", action="store_true")
    parser.add_argument("--recordings", default=None, help="CSV/parquet with recording_start/end.")
    parser.add_argument("--out", default="reports/synthetic_windows.csv")
    parser.add_argument("--window-duration", default="2min")
    parser.add_argument("--stride", default="30s")
    args = parser.parse_args()
    if args.synthetic:
        metadata, windows, events = make_synthetic_seizeit2_tables()
        out = Path(args.out)
        write_table(windows, out)
        write_table(events, out.parent / f"synthetic_events{out.suffix}")
        write_table(metadata, out.parent / f"synthetic_metadata{out.suffix}")
        print(f"wrote {out}")
        return
    if not args.recordings:
        raise SystemExit("Provide --recordings unless using --synthetic")
    recordings = read_table(args.recordings)
    windows = generate_fixed_windows(
        recordings,
        window_duration=args.window_duration,
        stride=args.stride,
    )
    out = Path(args.out)
    write_table(windows, out)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
