# MSG Cycle Hour Temporal-Recording Test Check Dataset Report

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
- Prediction filter used for metrics: `split=test`
- Events restricted to selected prediction horizon coverage: `True`

## Dataset Summary

| patients | recordings | windows | events | window_hours_sum |
| --- | --- | --- | --- | --- |
| 8.0 | 459.0 | 10309.0 | 54.0 | 10309.0 |

## Label Distribution

| total_windows | valid_windows | excluded_windows | positive_windows | positive_fraction_valid |
| --- | --- | --- | --- | --- |
| 10309.0 | 1418.0 | 8891.0 | 373.0 | 0.2630465444287729 |

## Event Denominator

| event_unit | events_source_total | events_after_filter | events_used_for_metrics | metric_units_after_filter | metric_units_used_for_metrics | event_filter | prediction_filter | restricted_to_prediction_coverage | denominator_warning | cluster_gap_minutes | cluster_policy |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| seizure | 768 | 510 | 54 | 510 | 54 | recording_match_status=matched | split=test | True | recording_match_status=matched selects seizures whose onsets could be matched to parsed wearable recording intervals; report source totals separately and do not generalize to all annotated seizures without coverage audit | 240.0 | seizure_level_metrics_clusters_not_collapsed |

## Event Annotation

| events_source_total | seizure_end_imputed_events | seizure_end_imputed_fraction | imputed_duration_seconds_values |
| --- | --- | --- | --- |
| 768 | 768 | 1.0 | 60.0 |

## Prediction Metadata

| prediction_rows | valid_prediction_rows | alarms | splits | alarm_threshold_min | alarm_threshold_max |
| --- | --- | --- | --- | --- | --- |
| 10309 | 1418 | 57 | test | 0.9878694350646349 | 0.9878694350646349 |

## Baseline

| baseline | horizon | n_events | n_forecasted | sensitivity | far_per_hour | far_per_day | time_in_warning | median_lead_time_seconds | brier_score | ece |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| cycle_hour | SPH 60 / SOP 1440 | 54 | 3 | 0.05555555555555555 | 0.003526093088857546 | 0.0846262341325811 | 0.04019746121297602 | 69473.0 | 0.12491471884580932 | 0.13053287346948575 |

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
