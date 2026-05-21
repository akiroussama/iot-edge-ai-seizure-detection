#!/usr/bin/env python
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.baselines.cycle_baseline import (
    apply_validation_quantile_alarm,
    fit_cycle_prior,
    fit_multiday_cycle_prior,
    predict_cycle_prior,
    predict_multiday_cycle_prior,
    rolling_origin_multiday_cycle_predictions,
)
from src.utils.io import read_table, write_table


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a split-safe cycle baseline.")
    parser.add_argument("--split-labels", required=True, help="Labeled windows table containing a split column.")
    parser.add_argument("--out", required=True)
    parser.add_argument("--fit-split", default="train")
    parser.add_argument("--threshold-split", default="val")
    parser.add_argument("--target-tiw", type=float, default=0.1)
    parser.add_argument("--smoothing", type=float, default=10.0)
    parser.add_argument("--split-col", default="split")
    parser.add_argument(
        "--cycle-family",
        choices=["hour_of_day", "multiday"],
        default="hour_of_day",
    )
    parser.add_argument("--cycle-period-hours", nargs="+", type=float, default=[24.0, 168.0])
    parser.add_argument("--phase-bins", type=int, default=8)
    parser.add_argument("--rolling-origin", action="store_true")
    parser.add_argument("--min-history-rows", type=int, default=10)
    args = parser.parse_args()

    labels = read_table(args.split_labels)
    if args.split_col not in labels.columns:
        raise SystemExit(f"{args.split_labels} must contain split column {args.split_col!r}")

    fit_rows = labels.loc[labels[args.split_col].eq(args.fit_split)].copy()
    if fit_rows.empty:
        raise SystemExit(f"fit split {args.fit_split!r} has no rows")

    if args.rolling_origin:
        preds = rolling_origin_multiday_cycle_predictions(
            labels,
            period_hours=tuple(args.cycle_period_hours),
            n_phase_bins=args.phase_bins,
            smoothing=args.smoothing,
            min_history_rows=args.min_history_rows,
        )
        global_prior = float(preds["risk_score"].mean())
    elif args.cycle_family == "multiday":
        model = fit_multiday_cycle_prior(
            fit_rows,
            period_hours=tuple(args.cycle_period_hours),
            n_phase_bins=args.phase_bins,
            smoothing=args.smoothing,
        )
        preds = predict_multiday_cycle_prior(labels, model)
        global_prior = model.global_prior
    else:
        model = fit_cycle_prior(fit_rows, smoothing=args.smoothing)
        preds = predict_cycle_prior(labels, model)
        global_prior = model.global_prior
    preds, threshold = apply_validation_quantile_alarm(
        preds,
        threshold_split=args.threshold_split,
        target_tiw=args.target_tiw,
        split_col=args.split_col,
    )
    write_table(preds, args.out)
    print(
        {
            "out": args.out,
            "fit_split": args.fit_split,
            "threshold_split": args.threshold_split,
            "target_tiw": args.target_tiw,
            "threshold": threshold,
            "cycle_family": args.cycle_family,
            "rolling_origin": args.rolling_origin,
            "global_prior": global_prior,
            "rows": len(preds),
            "alarms": int(preds["alarm"].sum()),
        }
    )


if __name__ == "__main__":
    main()
