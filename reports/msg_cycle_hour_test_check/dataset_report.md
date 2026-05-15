# MSG-local-full-download-cycle-test Dataset Report

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
| 8.0 | 459.0 | 9924.0 | 54.0 | 9924.0 |

## Label Distribution

| total_windows | valid_windows | excluded_windows | positive_windows | positive_fraction_valid |
| --- | --- | --- | --- | --- |
| 9924.0 | 9688.0 | 236.0 | 388.0 | 0.040049545829892653 |

## Baseline

| baseline | horizon | n_events | n_forecasted | sensitivity | far_per_hour | far_per_day | time_in_warning | median_lead_time_seconds | brier_score | ece |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| cycle_hour_val_tiw10_testsplit | SPH 60 / SOP 1440 | 54 | 3 | 0.05555555555555555 | 0.008670520231213872 | 0.20809248554913293 | 0.10445912469033856 | 76673.0 | 0.04801214559102761 | 0.04211062434112113 |

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
