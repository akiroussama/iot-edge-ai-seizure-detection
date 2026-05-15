# MSG-local-full-download-right-censored Dataset Report

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

| prediction_rows | valid_prediction_rows | alarms | splits | score_fit_split | threshold_source_split | alarm_threshold_min | alarm_threshold_max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 9260 | 792 | 63 | test | train | val | 0.9004579552159133 | 0.9004579552159133 |

## Baseline

| baseline | horizon | n_events | n_forecasted | sensitivity | far_per_hour | far_per_day | time_in_warning | median_lead_time_seconds | brier_score | ece |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| hr_tachycardia_trainfit_valthreshold_recording_right_censored_testsplit | SPH 60 / SOP 1440 | 13 | 10 | 0.7692307692307693 | 0.050505050505050504 | 1.2121212121212122 | 0.07954545454545454 | 62243.5 | 0.40961799574173907 | 0.5933435299813521 |

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
