#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.interpretability.counterfactual import (  # noqa: E402
    CounterfactualConfig,
    build_counterfactual_report,
    counterfactual_markdown,
    table_records,
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
            "Fit a leakage-screened linear risk surrogate and emit local "
            "counterfactual feature changes."
        )
    )
    parser.add_argument("--features", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--model-name", default="counterfactual_surrogate")
    parser.add_argument(
        "--id-cols",
        type=_parse_columns,
        default=("patient_id", "recording_id", "window_start", "window_end"),
    )
    parser.add_argument("--feature-cols", type=_parse_columns, default=())
    parser.add_argument("--fit-split", default="train")
    parser.add_argument("--split-col", default="split")
    parser.add_argument("--risk-col", default="risk_score")
    parser.add_argument("--alarm-col", default="alarm")
    parser.add_argument("--excluded-col", default="is_excluded")
    parser.add_argument("--threshold-col", default="alarm_threshold")
    parser.add_argument("--target-risk", type=float, default=None)
    parser.add_argument("--direction", choices=["prevent_alarm", "trigger_alarm"], default="prevent_alarm")
    parser.add_argument("--margin", type=float, default=0.01)
    parser.add_argument("--ridge-alpha", type=float, default=1e-3)
    parser.add_argument("--top-k-features", type=int, default=3)
    parser.add_argument("--title", default="Counterfactual Probing Report")
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    fit_split = None if str(args.fit_split).lower() in {"", "none", "all"} else args.fit_split
    config = CounterfactualConfig(
        fit_split=fit_split,
        split_col=args.split_col,
        risk_col=args.risk_col,
        alarm_col=args.alarm_col,
        excluded_col=args.excluded_col,
        threshold_col=args.threshold_col,
        target_risk=args.target_risk,
        direction=args.direction,
        margin=args.margin,
        ridge_alpha=args.ridge_alpha,
        top_k_features=args.top_k_features,
        feature_cols=args.feature_cols,
    )
    report = build_counterfactual_report(
        read_table(args.features),
        config=config,
        model_name=args.model_name,
        id_columns=args.id_cols,
    )
    out_dir = Path(args.out_dir)
    write_table(report.rows, out_dir / "counterfactual_rows.csv")
    write_table(report.feature_changes, out_dir / "counterfactual_feature_changes.csv")
    write_table(report.summary, out_dir / "counterfactual_summary.csv")
    write_table(report.manifest, out_dir / "counterfactual_manifest.csv")
    payload = {
        "metadata": report.metadata,
        "summary": table_records(report.summary),
        "rows": table_records(report.rows),
        "feature_changes": table_records(report.feature_changes),
    }
    (out_dir / "counterfactual_report.json").write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )
    (out_dir / "counterfactual_report.md").write_text(
        counterfactual_markdown(report, title=args.title),
        encoding="utf-8",
    )
    print(json.dumps({"out_dir": str(out_dir), **report.metadata}, indent=2))


if __name__ == "__main__":
    main()
