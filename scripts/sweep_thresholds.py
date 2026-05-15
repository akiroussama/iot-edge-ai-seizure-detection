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


def _split_value(expression: str | None) -> str | None:
    if expression is None or "=" not in expression:
        return None
    column, value = expression.split("=", maxsplit=1)
    return value if column == "split" else None


def _validate_sweep_scope(preds, sweep_filter: str | None, allow_unsplit_exploratory: bool, allow_test_sweep: bool) -> None:
    if "split" not in preds.columns:
        if not allow_unsplit_exploratory:
            raise ValueError(
                "predictions have no split column. Refusing threshold sweep because calibration/test scope "
                "is ambiguous. Pass --allow-unsplit-exploratory only for non-publishable diagnostics."
            )
        return
    if sweep_filter is None:
        raise ValueError(
            "predictions contain split column; pass --sweep-filter split=val/train. "
            "Do not sweep thresholds on the full table."
        )
    value = _split_value(sweep_filter)
    if value == "test" and not allow_test_sweep:
        raise ValueError(
            "refusing threshold sweep on split=test. Use validation/calibration rows for threshold tuning, "
            "or pass --allow-test-sweep only for a clearly non-publishable diagnostic."
        )


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
    _validate_sweep_scope(preds, args.sweep_filter, args.allow_unsplit_exploratory, args.allow_test_sweep)
    scoped_preds = _filter_rows(preds, args.sweep_filter, "sweep filter")
    scoped_events = _filter_rows(events, args.event_filter, "event filter")
    if scoped_preds.empty:
        raise ValueError(f"sweep filter produced no prediction rows: {args.sweep_filter}")
    out = threshold_sweep_table(scoped_preds, scoped_events, args.sph_minutes, args.sop_minutes, args.steps)
    out["sweep_filter"] = args.sweep_filter or "none"
    out["event_filter"] = args.event_filter or "none"
    out["publishable_threshold_tuning"] = bool(args.sweep_filter and _split_value(args.sweep_filter) != "test")
    out["falsifiability"] = (
        "This sweep is valid for threshold selection only if the sweep rows are calibration/validation rows "
        "that are disjoint from final test reporting."
    )
    write_table(out, args.output)
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
