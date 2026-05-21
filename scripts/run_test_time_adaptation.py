#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.adaptation.test_time import (  # noqa: E402
    TestTimeAdaptationConfig,
    build_test_time_adaptation_report,
    table_records,
    test_time_adaptation_markdown,
)
from src.utils.io import read_table, write_table  # noqa: E402


def _parse_columns(value: str | None) -> tuple[str, ...]:
    if not value:
        return ()
    columns = tuple(column.strip() for column in value.split(",") if column.strip())
    if not columns:
        raise argparse.ArgumentTypeError("column list cannot be empty")
    return columns


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Apply leakage-safe rolling-origin test-time adaptation to "
            "standardized prediction risk scores."
        )
    )
    parser.add_argument("--predictions", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--model-name", default="test_time_adapted_model")
    parser.add_argument(
        "--id-cols",
        type=_parse_columns,
        default=("patient_id", "recording_id", "window_start", "window_end"),
    )
    parser.add_argument("--score-col", default="risk_score")
    parser.add_argument("--patient-col", default="patient_id")
    parser.add_argument("--time-col", default="window_start")
    parser.add_argument("--split-col", default="split")
    parser.add_argument("--threshold-split", default="val")
    parser.add_argument("--target-tiw", type=float, default=0.1)
    parser.add_argument("--history-window", type=int, default=48)
    parser.add_argument("--min-history", type=int, default=6)
    parser.add_argument("--blend-alpha", type=float, default=0.5)
    parser.add_argument("--title", default="Test-Time Adaptation Report")
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    threshold_split = (
        None
        if str(args.threshold_split).lower() in {"", "none", "all"}
        else args.threshold_split
    )
    config = TestTimeAdaptationConfig(
        score_col=args.score_col,
        patient_col=args.patient_col,
        time_col=args.time_col,
        split_col=args.split_col,
        threshold_split=threshold_split,
        target_tiw=args.target_tiw,
        history_window=args.history_window,
        min_history=args.min_history,
        blend_alpha=args.blend_alpha,
    )
    report = build_test_time_adaptation_report(
        read_table(args.predictions),
        config=config,
        model_name=args.model_name,
        id_columns=args.id_cols,
    )
    out_dir = Path(args.out_dir)
    write_table(report.predictions, out_dir / "tta_predictions.csv")
    write_table(report.summary, out_dir / "tta_summary.csv")
    write_table(report.manifest, out_dir / "tta_manifest.csv")
    payload = {
        "metadata": report.metadata,
        "summary": table_records(report.summary),
    }
    (out_dir / "tta_report.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    (out_dir / "tta_report.md").write_text(
        test_time_adaptation_markdown(report, title=args.title),
        encoding="utf-8",
    )
    print(json.dumps({"out_dir": str(out_dir), **report.metadata}, indent=2))


if __name__ == "__main__":
    main()
