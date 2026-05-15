# MSG-local Dataset Report

## Status

This report is generated from local data files and is for pipeline verification and manual audit planning.
It is not clinical evidence and must not be used as a paper result until seizure timelines, labels, splits,
normalization, and leakage audits have been manually reviewed.

## Task

Forecasting labels use SPH/SOP: a window ending at `t` is positive when seizure onset falls in
`[t + SPH, t + SPH + SOP)`.

- SPH minutes: 60
- SOP minutes: 1440
- Event filter used for metrics: `recording_match_status=matched`
- Prediction filter used for metrics: `none`
- Events restricted to selected prediction horizon coverage: `True`

## Dataset Summary

| patients | recordings | windows | events | window_hours_sum |
| --- | --- | --- | --- | --- |
| 8.0 | 2055.0 | 49577.0 | 436.0 | 49577.0 |

## Label Distribution

| total_windows | valid_windows | excluded_windows | positive_windows | positive_fraction_valid |
| --- | --- | --- | --- | --- |
| 49577.0 | 7920.0 | 41657.0 | 3326.0 | 0.41994949494949496 |

## Event Denominator

| event_unit | events_source_total | events_after_filter | events_used_for_metrics | metric_units_after_filter | metric_units_used_for_metrics | event_filter | prediction_filter | restricted_to_prediction_coverage | denominator_warning | cluster_gap_minutes | cluster_policy |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| seizure | 768 | 510 | 436 | 510 | 436 | recording_match_status=matched | none | True | recording_match_status=matched selects seizures whose onsets could be matched to parsed wearable recording intervals; report source totals separately and do not generalize to all annotated seizures without coverage audit | 240.0 | seizure_level_metrics_clusters_not_collapsed |

## Event Annotation

| events_source_total | seizure_end_imputed_events | seizure_end_imputed_fraction | imputed_duration_seconds_values |
| --- | --- | --- | --- |
| 768 | 768 | 1.0 | 60.0 |

## Prediction Metadata

| prediction_rows | valid_prediction_rows | alarms | splits |
| --- | --- | --- | --- |
| 49577 | 7920 | 792 | test,train,val |

## Baseline

| baseline | horizon | n_events | n_forecasted | sensitivity | far_per_hour | far_per_day | time_in_warning | median_lead_time_seconds | brier_score | ece |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| random_rate_matched | SPH 60 / SOP 1440 | 436 | 240 | 0.5504587155963303 | 0.05025252525252525 | 1.206060606060606 | 0.1 | 35262.0 | 0.3015899425315694 | 0.20049106257335464 |

## Event Coverage

```json
{
  "matched": 510,
  "unmatched": 258
}
```

## Required Manual Audit

1. Inspect seizure-centered windows in the exported label audit CSV.
2. Verify onset timestamps against source annotations.
3. Confirm ictal and postictal exclusions around every audited seizure.
4. Confirm whether this run is detection, early warning, short-horizon forecasting, or long-horizon forecasting.
5. Freeze splits and rerun leakage audit before any A100 training.
