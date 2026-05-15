# MSG-local-full-download-right-censored-elapsed-time Dataset Report

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
| 8.0 | 2057.0 | 49596.0 | 13.0 | 49596.0 |

## Label Distribution

| total_windows | valid_windows | excluded_windows | positive_windows | positive_fraction_valid |
| --- | --- | --- | --- | --- |
| 49596.0 | 4854.0 | 44742.0 | 260.0 | 0.053564070869386075 |

## Event Denominator

| event_unit | events_source_total | events_after_filter | events_used_for_metrics | event_filter | prediction_filter | restricted_to_prediction_coverage | denominator_warning | cluster_gap_minutes | cluster_policy |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| seizure | 768 | 510 | 13 | recording_match_status=matched | split=test | True | recording_match_status=matched selects seizures whose onsets could be matched to parsed wearable recording intervals; report source totals separately and do not generalize to all annotated seizures without coverage audit | 240.0 | seizure_level_metrics_clusters_not_collapsed |

## Prediction Metadata

| prediction_rows | valid_prediction_rows | alarms | splits | alarm_threshold_min | alarm_threshold_max |
| --- | --- | --- | --- | --- | --- |
| 10328 | 1077 | 228 | test | 0.06852789988630621 | 0.06852789988630621 |

## Baseline

| baseline | horizon | n_events | n_forecasted | sensitivity | far_per_hour | far_per_day | time_in_warning | median_lead_time_seconds | brier_score | ece |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| cycle_hour_recording_val_tiw10_right_censored_testsplit_elapsed_time | SPH 60 / SOP 1440 | 13 | 9 | 0.6923076923076923 | 0.056638811513463325 | 1.3593314763231197 | 0.2116991643454039 | 63567.0 | 0.03994688727933054 | 0.05532927962325607 |

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
