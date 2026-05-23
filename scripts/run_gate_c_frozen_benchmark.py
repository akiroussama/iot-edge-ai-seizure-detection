#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.artifacts.gate_c_frozen_benchmark import (  # noqa: E402
    FROZEN_NULL_MODELS,
    GateCFrozenBenchmarkConfig,
    run_gate_c_frozen_benchmark,
)


def _parse_models(value: str) -> tuple[str, ...]:
    if value == "all":
        return FROZEN_NULL_MODELS
    models = tuple(part.strip() for part in value.split(",") if part.strip())
    unknown = sorted(set(models) - set(FROZEN_NULL_MODELS))
    if unknown:
        raise argparse.ArgumentTypeError(f"unknown null models: {unknown}")
    if "split_prevalence_prior" not in models:
        raise argparse.ArgumentTypeError("split_prevalence_prior is required as BSS reference")
    return models


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run frozen-only Gate C null baselines and reports from a registry."
    )
    parser.add_argument("--registry", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--root", default=".")
    parser.add_argument("--null-models", type=_parse_models, default=FROZEN_NULL_MODELS)
    parser.add_argument("--fit-split", default="train")
    parser.add_argument("--threshold-split", default="val")
    parser.add_argument("--evaluation-split", default="test")
    parser.add_argument("--target-tiw", type=float, default=0.1)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--patient-min-events", type=int, default=3)
    parser.add_argument("--event-filter", default="recording_match_status=matched")
    parser.add_argument("--no-restrict-events-to-prediction-coverage", action="store_true")
    parser.add_argument("--sph-minutes", type=float, default=60.0)
    parser.add_argument("--sop-minutes", type=float, default=1440.0)
    parser.add_argument("--window-seconds", type=float, default=3600.0)
    parser.add_argument("--stride-seconds", type=float, default=3600.0)
    parser.add_argument("--n-bins", type=int, default=10)
    parser.add_argument("--bootstrap-samples", type=int, default=200)
    parser.add_argument("--min-events", type=int, default=5)
    parser.add_argument("--min-valid-prediction-rows", type=int, default=100)
    parser.add_argument("--min-brier-skill-score", type=float, default=0.0)
    parser.add_argument("--max-far-per-day", type=float, default=None)
    parser.add_argument("--doi-or-prereg-uri", default=None)
    parser.add_argument("--notes", default=GateCFrozenBenchmarkConfig.notes)
    return parser


def main() -> None:
    args = _build_parser().parse_args()
    config = GateCFrozenBenchmarkConfig(
        registry_path=args.registry,
        out_dir=args.out_dir,
        root=args.root,
        null_models=args.null_models,
        fit_split=args.fit_split,
        threshold_split=args.threshold_split,
        evaluation_split=args.evaluation_split,
        target_tiw=args.target_tiw,
        seed=args.seed,
        patient_min_events=args.patient_min_events,
        event_filter=args.event_filter,
        restrict_events_to_prediction_coverage=not args.no_restrict_events_to_prediction_coverage,
        sph_minutes=args.sph_minutes,
        sop_minutes=args.sop_minutes,
        window_seconds=args.window_seconds,
        stride_seconds=args.stride_seconds,
        n_bins=args.n_bins,
        bootstrap_samples=args.bootstrap_samples,
        min_events=args.min_events,
        min_valid_prediction_rows=args.min_valid_prediction_rows,
        min_brier_skill_score=args.min_brier_skill_score,
        max_far_per_day=args.max_far_per_day,
        doi_or_prereg_uri=args.doi_or_prereg_uri,
        notes=args.notes,
    )
    result = run_gate_c_frozen_benchmark(config)
    print(
        json.dumps(
            {
                "out_dir": args.out_dir,
                "benchmark_status": result.manifest["benchmark_status"],
                "leaderboard_rows": int(len(result.leaderboard)),
                "atlas_labels": result.manifest["forecastability_labels"],
                "output_paths": result.output_paths,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
