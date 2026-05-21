#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.baselines.patient_adaptive import (  # noqa: E402
    PatientAdaptiveConfig,
    patient_adaptive_predictions,
    patient_adaptive_summary,
    table_records,
)
from src.utils.io import read_table, write_table  # noqa: E402


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate leakage-safe patient-adaptive baseline predictions."
    )
    parser.add_argument("--labels", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--summary-out", default=None)
    parser.add_argument("--json-out", default=None)
    parser.add_argument(
        "--baseline",
        choices=["population", "patient", "empirical_bayes"],
        default="empirical_bayes",
    )
    parser.add_argument(
        "--evaluation-mode",
        choices=["cold_start", "warm_start", "rolling_origin"],
        default="warm_start",
    )
    parser.add_argument("--split-col", default="split")
    parser.add_argument("--fit-split", default="train")
    parser.add_argument("--threshold-split", default="val")
    parser.add_argument("--patient-col", default="patient_id")
    parser.add_argument("--min-patient-observations", type=int, default=3)
    parser.add_argument("--prior-strength", type=float, default=8.0)
    parser.add_argument("--target-tiw", type=float, default=0.1)
    parser.add_argument("--seed", type=int, default=42)
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    labels = read_table(args.labels)
    config = PatientAdaptiveConfig(
        baseline=args.baseline,
        evaluation_mode=args.evaluation_mode,
        split_col=args.split_col,
        fit_split=args.fit_split,
        threshold_split=args.threshold_split,
        patient_col=args.patient_col,
        min_patient_observations=args.min_patient_observations,
        prior_strength=args.prior_strength,
        target_tiw=args.target_tiw,
        seed=args.seed,
    )
    predictions = patient_adaptive_predictions(labels, config=config)
    summary = patient_adaptive_summary(predictions)
    write_table(predictions, args.out)
    if args.summary_out:
        write_table(summary, args.summary_out)
    if args.json_out:
        payload = {
            "config": config.__dict__,
            "summary": table_records(summary),
        }
        out = Path(args.json_out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "out": args.out,
                "summary_out": args.summary_out,
                "rows": int(len(predictions)),
                "variants": summary["patient_adaptive_variant"].value_counts().to_dict(),
                "baseline": args.baseline,
                "evaluation_mode": args.evaluation_mode,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
