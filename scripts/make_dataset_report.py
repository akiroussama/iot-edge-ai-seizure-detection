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


def _filter_rows(df: pd.DataFrame, expression: str | None, name: str) -> pd.DataFrame:
    if not expression:
        return df
    if "=" not in expression:
        raise ValueError(f"{name} filter must be formatted as column=value")
    column, value = expression.split("=", maxsplit=1)
    if column not in df.columns:
        raise ValueError(f"{name} filter column not found: {column}")
    return df.loc[df[column].astype(str).eq(value)].reset_index(drop=True)


def _filter_column(expression: str) -> str:
    return expression.split("=", maxsplit=1)[0]


def _requires_bias_acknowledgement(expression: str | None) -> bool:
    return expression == "recording_match_status=matched"


def _events_coverable_by_predictions(
    predictions: pd.DataFrame,
    events: pd.DataFrame,
    sph_minutes: float,
    sop_minutes: float,
) -> pd.DataFrame:
    """Keep events that could be forecasted by at least one selected prediction window."""
    if predictions.empty or events.empty:
        return events.iloc[0:0].copy()
    preds = predictions.copy()
    preds = preds.loc[~preds.get("is_excluded", pd.Series(False, index=preds.index)).fillna(False)]
    preds["window_end"] = pd.to_datetime(preds["window_end"])
    ev = events.copy()
    ev["seizure_start"] = pd.to_datetime(ev["seizure_start"])
    sph = pd.Timedelta(minutes=sph_minutes)
    sop = pd.Timedelta(minutes=sop_minutes)

    keep_indices = []
    for idx, event in ev.iterrows():
        candidates = preds.loc[preds["patient_id"].astype(str).eq(str(event["patient_id"]))]
        if "recording_id" in preds.columns and "recording_id" in ev.columns:
            candidates = candidates.loc[candidates["recording_id"].astype(str).eq(str(event["recording_id"]))]
        if candidates.empty:
            continue
        horizon_start = candidates["window_end"] + sph
        horizon_end = candidates["window_end"] + sph + sop
        if ((event["seizure_start"] >= horizon_start) & (event["seizure_start"] < horizon_end)).any():
            keep_indices.append(idx)
    return ev.loc[keep_indices].reset_index(drop=True)


def _event_denominator_table(
    events_all: pd.DataFrame,
    events_after_filter: pd.DataFrame,
    events_after_coverage: pd.DataFrame,
    event_filter: str | None,
    prediction_filter: str | None,
    restricted_to_prediction_coverage: bool,
    event_unit: str,
    cluster_gap_minutes: float | None,
) -> pd.DataFrame:
    row: dict[str, object] = {
        "event_unit": event_unit,
        "events_source_total": len(events_all),
        "events_after_filter": len(events_after_filter),
        "events_used_for_metrics": len(events_after_coverage),
        "event_filter": event_filter or "none",
        "prediction_filter": prediction_filter or "none",
        "restricted_to_prediction_coverage": restricted_to_prediction_coverage,
        "denominator_warning": "none",
    }
    if _requires_bias_acknowledgement(event_filter):
        row["denominator_warning"] = (
            "recording_match_status=matched selects seizures whose onsets could be matched to parsed "
            "wearable recording intervals; report source totals separately and do not generalize to all "
            "annotated seizures without coverage audit"
        )
    if cluster_gap_minutes is not None:
        row["cluster_gap_minutes"] = cluster_gap_minutes
        row["cluster_policy"] = "seizure_level_metrics_clusters_not_collapsed"
    else:
        row["cluster_policy"] = "not_summarized"
    return pd.DataFrame([row])


def _event_annotation_table(events_all: pd.DataFrame) -> pd.DataFrame:
    row: dict[str, object] = {"events_source_total": len(events_all)}
    if "seizure_end_imputed" in events_all.columns:
        imputed = events_all["seizure_end_imputed"].fillna(False).astype(bool)
        row["seizure_end_imputed_events"] = int(imputed.sum())
        row["seizure_end_imputed_fraction"] = float(imputed.mean()) if len(imputed) else float("nan")
    else:
        row["seizure_end_imputed_events"] = "unknown"
        row["seizure_end_imputed_fraction"] = "unknown"
    if "imputed_duration_seconds" in events_all.columns:
        values = pd.to_numeric(events_all["imputed_duration_seconds"], errors="coerce").dropna()
        row["imputed_duration_seconds_values"] = ",".join(str(float(v)) for v in sorted(values.unique()))
    else:
        row["imputed_duration_seconds_values"] = "unknown"
    return pd.DataFrame([row])


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


def _prediction_metadata_table(predictions: pd.DataFrame) -> pd.DataFrame:
    if predictions.empty:
        return pd.DataFrame()
    valid_mask = ~predictions.get("is_excluded", pd.Series(False, index=predictions.index)).fillna(False).astype(bool)
    row: dict[str, object] = {
        "prediction_rows": len(predictions),
        "valid_prediction_rows": int(valid_mask.sum()),
        "alarms": int(predictions.get("alarm", pd.Series(False, index=predictions.index)).fillna(False).sum()),
    }
    if "split" in predictions.columns:
        row["splits"] = ",".join(sorted(predictions["split"].dropna().astype(str).unique()))
    for col in ["score_fit_split", "threshold_source_split"]:
        if col in predictions.columns:
            row[col] = ",".join(sorted(predictions[col].dropna().astype(str).unique()))
    for col in ["alarm_threshold", "patient_threshold"]:
        if col in predictions.columns:
            values = pd.to_numeric(predictions[col], errors="coerce").dropna()
            if not values.empty:
                row[f"{col}_min"] = float(values.min())
                row[f"{col}_max"] = float(values.max())
    return pd.DataFrame([row])


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a dataset-specific benchmark status report.")
    parser.add_argument("--dataset-name", required=True)
    parser.add_argument("--windows", required=True)
    parser.add_argument("--labels", required=True)
    parser.add_argument("--events", required=True)
    parser.add_argument("--predictions", default=None)
    parser.add_argument("--baseline-name", default="random_rate_matched")
    parser.add_argument("--event-filter", default=None, help="Optional filter such as recording_match_status=matched")
    parser.add_argument("--prediction-filter", default=None, help="Optional filter such as split=test")
    parser.add_argument(
        "--acknowledge-event-filter-bias",
        action="store_true",
        help="Required for recording_match_status=matched because this is a wear-time matched subset.",
    )
    parser.add_argument(
        "--restrict-events-to-prediction-coverage",
        action="store_true",
        help="Evaluate only events whose onset is inside at least one selected prediction horizon.",
    )
    parser.add_argument("--event-unit", choices=["seizure"], default="seizure")
    parser.add_argument(
        "--cluster-gap-minutes",
        type=float,
        default=None,
        help="Optional cluster gap to document that metrics remain seizure-level, not cluster-collapsed.",
    )
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--sph-minutes", type=float, required=True)
    parser.add_argument("--sop-minutes", type=float, required=True)
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    windows = read_table(args.windows)
    labels = read_table(args.labels)
    events_all = read_table(args.events)
    if _requires_bias_acknowledgement(args.event_filter) and not args.acknowledge_event_filter_bias:
        raise ValueError(
            "recording_match_status=matched is a biased wear-time subset. Re-run with "
            "--acknowledge-event-filter-bias and report source event totals."
        )
    events_eval = _filter_events(events_all, args.event_filter)
    events_after_filter = events_eval.copy()
    predictions = read_table(args.predictions) if args.predictions else pd.DataFrame()
    if args.prediction_filter:
        predictions = _filter_rows(predictions, args.prediction_filter, "prediction")
        filter_col = _filter_column(args.prediction_filter)
        if filter_col in labels.columns:
            labels = _filter_rows(labels, args.prediction_filter, "label")
        if filter_col in windows.columns:
            windows = _filter_rows(windows, args.prediction_filter, "window")
    if args.restrict_events_to_prediction_coverage:
        if predictions.empty:
            raise ValueError("--restrict-events-to-prediction-coverage requires --predictions")
        events_eval = _events_coverable_by_predictions(
            predictions,
            events_eval,
            args.sph_minutes,
            args.sop_minutes,
        )
    denominator = _event_denominator_table(
        events_all=events_all,
        events_after_filter=events_after_filter,
        events_after_coverage=events_eval,
        event_filter=args.event_filter,
        prediction_filter=args.prediction_filter,
        restricted_to_prediction_coverage=args.restrict_events_to_prediction_coverage,
        event_unit=args.event_unit,
        cluster_gap_minutes=args.cluster_gap_minutes,
    )
    annotation = _event_annotation_table(events_all)

    summary = dataset_summary(windows, events_eval)
    distribution = label_distribution(labels)
    write_table(summary, out_dir / "dataset_summary.csv")
    write_table(distribution, out_dir / "label_distribution.csv")
    write_table(denominator, out_dir / "event_denominator.csv")
    write_table(annotation, out_dir / "event_annotation.csv")

    baseline = pd.DataFrame()
    prediction_metadata = _prediction_metadata_table(predictions)
    if args.predictions:
        baseline = _baseline_table(
            predictions,
            events_eval,
            args.sph_minutes,
            args.sop_minutes,
            args.baseline_name,
        )
        write_table(baseline, out_dir / "baseline_results.csv")
        write_table(prediction_metadata, out_dir / "prediction_metadata.csv")

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
- Prediction filter used for metrics: `{args.prediction_filter or "none"}`
- Events restricted to selected prediction horizon coverage: `{args.restrict_events_to_prediction_coverage}`

## Dataset Summary

{_markdown_table(summary)}

## Label Distribution

{_markdown_table(distribution)}

## Event Denominator

{_markdown_table(denominator)}

## Event Annotation

{_markdown_table(annotation)}

## Prediction Metadata

{_markdown_table(prediction_metadata)}

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
