# MSG-local-full-download Dataset Report

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
| 8.0 | 2057.0 | 49596.0 | 53.0 | 49596.0 |

## Label Distribution

| total_windows | valid_windows | excluded_windows | positive_windows | positive_fraction_valid |
| --- | --- | --- | --- | --- |
| 49596.0 | 47713.0 | 1883.0 | 3325.0 | 0.06968750654957769 |

## Prediction Metadata

| prediction_rows | valid_prediction_rows | alarms | splits | score_fit_split | threshold_source_split | alarm_threshold_min | alarm_threshold_max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 9260 | 9030 | 881 | test | train | val | 0.9107408760149468 | 0.9107408760149468 |

## Baseline

| baseline | horizon | n_events | n_forecasted | sensitivity | far_per_hour | far_per_day | time_in_warning | median_lead_time_seconds | brier_score | ece |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| hr_tachycardia_trainfit_valthreshold_recording_testsplit | SPH 60 / SOP 1440 | 53 | 41 | 0.7735849056603774 | 0.03787375415282392 | 0.9089700996677741 | 0.09756367663344408 | 34305.0 | 0.4108845828737248 | 0.5902287486132363 |

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
