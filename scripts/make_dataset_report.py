from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import pandas as pd

from src.metrics import (
    brier_score,
    event_level_sensitivity,
    expected_calibration_error,
    false_alarm_rate_per_day,
    false_alarm_rate_per_hour,
    median_lead_time,
    time_in_warning,
)
from src.reports.summary_tables import dataset_summary, label_distribution
from src.utils.io import read_table, write_table


def _markdown_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "_No rows._"
    headers = [str(c) for c in df.columns]
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for _, row in df.iterrows():
        lines.append("| " + " | ".join(str(row[col]) for col in df.columns) + " |")
    return "\n".join(lines)


def _filter_events(events: pd.DataFrame, expression: str | None) -> pd.DataFrame:
    if not expression:
        return events
    if "=" not in expression:
        raise ValueError("--event-filter must be formatted as column=value")
    column, value = expression.split("=", maxsplit=1)
    if column not in events.columns:
        raise ValueError(f"event filter column not found: {column}")
    return events.loc[events[column].astype(str).eq(value)].reset_index(drop=True)


def _baseline_table(
    predictions: pd.DataFrame,
    events: pd.DataFrame,
    sph_minutes: float,
    sop_minutes: float,
    baseline_name: str,
) -> pd.DataFrame:
    sens = event_level_sensitivity(predictions, events, sph_minutes, sop_minutes)
    return pd.DataFrame(
        [
            {
                "baseline": baseline_name,
                "horizon": f"SPH {sph_minutes:g} / SOP {sop_minutes:g}",
                "n_events": sens["n_events"],
                "n_forecasted": sens["n_forecasted"],
                "sensitivity": sens["sensitivity"],
                "far_per_hour": false_alarm_rate_per_hour(predictions, events, sph_minutes, sop_minutes),
                "far_per_day": false_alarm_rate_per_day(predictions, events, sph_minutes, sop_minutes),
                "time_in_warning": time_in_warning(predictions),
                "median_lead_time_seconds": median_lead_time(predictions, events, sph_minutes, sop_minutes),
                "brier_score": brier_score(predictions),
                "ece": expected_calibration_error(predictions),
            }
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a dataset-specific benchmark status report.")
    parser.add_argument("--dataset-name", required=True)
    parser.add_argument("--windows", required=True)
    parser.add_argument("--labels", required=True)
    parser.add_argument("--events", required=True)
    parser.add_argument("--predictions", default=None)
    parser.add_argument("--baseline-name", default="random_rate_matched")
    parser.add_argument("--event-filter", default=None, help="Optional filter such as recording_match_status=matched")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--sph-minutes", type=float, required=True)
    parser.add_argument("--sop-minutes", type=float, required=True)
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    windows = read_table(args.windows)
    labels = read_table(args.labels)
    events_all = read_table(args.events)
    events_eval = _filter_events(events_all, args.event_filter)

    summary = dataset_summary(windows, events_eval)
    distribution = label_distribution(labels)
    write_table(summary, out_dir / "dataset_summary.csv")
    write_table(distribution, out_dir / "label_distribution.csv")

    baseline = pd.DataFrame()
    if args.predictions:
        predictions = read_table(args.predictions)
        baseline = _baseline_table(
            predictions,
            events_eval,
            args.sph_minutes,
            args.sop_minutes,
            args.baseline_name,
        )
        write_table(baseline, out_dir / "baseline_results.csv")

    event_status = {}
    if "recording_match_status" in events_all.columns:
        event_status = {
            str(key): int(value)
            for key, value in events_all["recording_match_status"].value_counts().sort_index().items()
        }

    report = f"""# {args.dataset_name} Dataset Report

## Status

This report is generated from local data files and is for pipeline verification and manual audit planning.
It is not clinical evidence and must not be used as a paper result until seizure timelines, labels, splits,
normalization, and leakage audits have been manually reviewed.

## Task

Forecasting labels use SPH/SOP: a window ending at `t` is positive when seizure onset falls in
`[t + SPH, t + SPH + SOP)`.

- SPH minutes: {args.sph_minutes:g}
- SOP minutes: {args.sop_minutes:g}
- Event filter used for metrics: `{args.event_filter or "none"}`

## Dataset Summary

{_markdown_table(summary)}

## Label Distribution

{_markdown_table(distribution)}

## Baseline

{_markdown_table(baseline)}

## Event Coverage

```json
{json.dumps(event_status, indent=2)}
```

## Required Manual Audit

1. Inspect seizure-centered windows in the exported label audit CSV.
2. Verify onset timestamps against source annotations.
3. Confirm ictal and postictal exclusions around every audited seizure.
4. Confirm whether this run is detection, early warning, short-horizon forecasting, or long-horizon forecasting.
5. Freeze splits and rerun leakage audit before any A100 training.
"""
    (out_dir / "dataset_report.md").write_text(report, encoding="utf-8")
    print(f"wrote dataset report to {out_dir}")


if __name__ == "__main__":
    main()
