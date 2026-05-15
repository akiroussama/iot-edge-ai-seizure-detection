from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.metrics.sweep import threshold_sweep_table
from src.utils.io import read_table, write_table


def _filter_rows(df, expression: str | None, name: str):
    if expression is None:
        return df
    if "=" not in expression:
        raise ValueError(f"{name} must be formatted as column=value")
    column, value = expression.split("=", maxsplit=1)
    if column not in df.columns:
        raise ValueError(f"{name} column not found: {column}")
    return df.loc[df[column].astype(str).eq(value)].reset_index(drop=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Sweep risk-score thresholds and report clinical metrics.")
    parser.add_argument("--predictions", required=True)
    parser.add_argument("--events", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--sph-minutes", type=float, default=5)
    parser.add_argument("--sop-minutes", type=float, default=30)
    parser.add_argument("--steps", type=int, default=101)
    parser.add_argument(
        "--sweep-filter",
        default=None,
        help="Required when predictions contain split, for example split=val. Never defaults to test.",
    )
    parser.add_argument(
        "--event-filter",
        default=None,
        help="Optional event filter such as recording_match_status=matched.",
    )
    parser.add_argument(
        "--allow-unsplit-exploratory",
        action="store_true",
        help="Allow sweeping a predictions table with no split column. Output is exploratory only.",
    )
    parser.add_argument(
        "--allow-test-sweep",
        action="store_true",
        help="Allow split=test sweeps for non-publishable diagnostics. Do not use for threshold selection.",
    )
    args = parser.parse_args()
    preds = read_table(args.predictions)
    events = read_table(args.events)
    scoped_events = _filter_rows(events, args.event_filter, "event filter")
    out = threshold_sweep_table(
        preds,
        scoped_events,
        args.sph_minutes,
        args.sop_minutes,
        args.steps,
        sweep_filter=args.sweep_filter,
        allow_unsplit_exploratory=args.allow_unsplit_exploratory,
        allow_test_sweep=args.allow_test_sweep,
    )
    out["event_filter"] = args.event_filter or "none"
    write_table(out, args.output)
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
