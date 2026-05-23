#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.artifacts.gate_c_materialize_inputs import (  # noqa: E402
    GateCMaterializationConfig,
    materialize_gate_c_inputs,
    write_gate_c_materialization,
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Materialize Gate C events/labels/splits from recordings and events."
    )
    parser.add_argument("--recordings", required=True)
    parser.add_argument("--events", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--suffix", choices=[".csv", ".tsv", ".parquet"], default=".csv")
    parser.add_argument("--window-duration", default="2min")
    parser.add_argument("--stride", default="30s")
    parser.add_argument("--sph-minutes", type=float, default=5.0)
    parser.add_argument("--sop-minutes", type=float, default=30.0)
    parser.add_argument("--postictal-exclusion-minutes", type=float, default=60.0)
    parser.add_argument(
        "--postictal-anchor",
        choices=["seizure_end", "seizure_start"],
        default="seizure_end",
    )
    parser.add_argument("--include-ictal", action="store_true")
    parser.add_argument(
        "--strategy",
        choices=["temporal", "patient_wise", "recording_wise"],
        default="temporal",
    )
    parser.add_argument("--train-fraction", type=float, default=0.7)
    parser.add_argument("--val-fraction", type=float, default=0.1)
    parser.add_argument("--test-fraction", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--no-purge-overlap", action="store_true")
    parser.add_argument(
        "--temporal-unit",
        choices=["window", "recording"],
        default="window",
    )
    parser.add_argument(
        "--temporal-basis",
        choices=["elapsed_time", "count"],
        default="elapsed_time",
    )
    parser.add_argument("--allow-duplicate-recording-time-ranges", action="store_true")
    return parser


def main() -> None:
    args = _build_parser().parse_args()
    cfg = GateCMaterializationConfig(
        window_duration=args.window_duration,
        stride=args.stride,
        sph_minutes=args.sph_minutes,
        sop_minutes=args.sop_minutes,
        postictal_exclusion_minutes=args.postictal_exclusion_minutes,
        postictal_anchor=args.postictal_anchor,
        include_ictal=args.include_ictal,
        strategy=args.strategy,
        train_fraction=args.train_fraction,
        val_fraction=args.val_fraction,
        test_fraction=args.test_fraction,
        seed=args.seed,
        purge_overlap=not args.no_purge_overlap,
        temporal_unit=args.temporal_unit,
        temporal_basis=args.temporal_basis,
        allow_duplicate_recording_time_ranges=args.allow_duplicate_recording_time_ranges,
    )
    try:
        materialization = materialize_gate_c_inputs(
            recordings_path=args.recordings,
            events_path=args.events,
            cfg=cfg,
        )
        materialization = write_gate_c_materialization(
            materialization,
            out_dir=args.out_dir,
            recordings_path=args.recordings,
            events_path=args.events,
            cfg=cfg,
            suffix=args.suffix,
        )
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    print(
        json.dumps(
            {
                "out_dir": args.out_dir,
                "materialization_status": materialization.manifest["materialization_status"],
                "claim_status": materialization.manifest["claim_status"],
                "events_rows": materialization.manifest["events_rows"],
                "labels_rows": materialization.manifest["labels_rows"],
                "splits_rows": materialization.manifest["splits_rows"],
                "positive_valid_windows": materialization.manifest["positive_valid_windows"],
                "split_ids": materialization.manifest["split_ids"],
                "output_paths": materialization.output_paths,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
