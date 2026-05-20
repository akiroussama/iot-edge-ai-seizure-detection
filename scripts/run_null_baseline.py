#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.baselines.forecast_nulls import generate_forecast_null, variant_counts
from src.utils.io import read_table, write_table


def main() -> None:
    parser = argparse.ArgumentParser(description="Run constrained forecasting null models.")
    parser.add_argument("--labels", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument(
        "--null-model",
        choices=[
            "split_prevalence_prior",
            "rate_matched_random",
            "patient_prior",
            "cycle_preserving_random",
        ],
        required=True,
    )
    parser.add_argument("--fit-split", default="train")
    parser.add_argument("--threshold-split", default="val")
    parser.add_argument("--target-tiw", type=float, default=0.1)
    parser.add_argument("--split-col", default="split")
    parser.add_argument("--patient-min-events", type=int, default=3)
    parser.add_argument("--cycle-bin", choices=["hour_of_day"], default="hour_of_day")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    labels = read_table(args.labels)
    predictions = generate_forecast_null(
        labels,
        null_model=args.null_model,
        fit_split=args.fit_split,
        threshold_split=args.threshold_split,
        target_tiw=args.target_tiw,
        split_col=args.split_col,
        patient_min_events=args.patient_min_events,
        cycle_bin=args.cycle_bin,
        seed=args.seed,
    )
    write_table(predictions, args.out)
    metadata = {
        "out": args.out,
        "rows": len(predictions),
        "null_model": args.null_model,
        "null_model_variants": variant_counts(predictions),
        "fit_split": args.fit_split,
        "threshold_split": args.threshold_split,
        "target_tiw": args.target_tiw,
        "seed": args.seed,
        "actual_model_seed": int(predictions["seed"].iloc[0]) if len(predictions) else None,
    }
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
