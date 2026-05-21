#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.reports.forecastability_atlas import (  # noqa: E402
    ForecastabilityThresholds,
    build_forecastability_atlas,
    forecastability_atlas_markdown,
)
from src.utils.io import read_table, write_table  # noqa: E402


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a forecastability atlas from leaderboard rows."
    )
    parser.add_argument("--leaderboard", required=True)
    parser.add_argument("--out-csv", required=True)
    parser.add_argument("--out-md", required=True)
    parser.add_argument("--reliability-table", default=None)
    parser.add_argument(
        "--allow-pre-gate-c",
        action="store_true",
        help="Do not require Gate C for paper_table_ready classification.",
    )
    parser.add_argument("--min-events", type=int, default=5)
    parser.add_argument("--min-valid-prediction-rows", type=int, default=100)
    parser.add_argument("--min-brier-skill-score", type=float, default=0.0)
    parser.add_argument("--max-far-per-day", type=float, default=None)
    parser.add_argument("--title", default="Forecastability Atlas")
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    if args.min_events <= 0:
        raise SystemExit("--min-events must be positive")
    if args.min_valid_prediction_rows <= 0:
        raise SystemExit("--min-valid-prediction-rows must be positive")

    leaderboard = read_table(args.leaderboard)
    reliability = read_table(args.reliability_table) if args.reliability_table else None
    thresholds = ForecastabilityThresholds(
        min_events=args.min_events,
        min_valid_prediction_rows=args.min_valid_prediction_rows,
        min_brier_skill_score=args.min_brier_skill_score,
        max_false_alarm_rate_per_day=args.max_far_per_day,
    )
    atlas = build_forecastability_atlas(
        leaderboard,
        reliability_df=reliability,
        thresholds=thresholds,
        gate_c_required=not args.allow_pre_gate_c,
    )
    write_table(atlas, args.out_csv)
    out_md = Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(forecastability_atlas_markdown(atlas, title=args.title), encoding="utf-8")
    print(
        json.dumps(
            {
                "out_csv": args.out_csv,
                "out_md": args.out_md,
                "rows": int(len(atlas)),
                "paper_table_ready_rows": int(atlas["paper_table_ready"].sum()) if not atlas.empty else 0,
                "labels": atlas["forecastability_label"].value_counts().to_dict()
                if not atlas.empty
                else {},
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
