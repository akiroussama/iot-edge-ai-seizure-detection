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

## Baseline

| baseline | horizon | n_events | n_forecasted | sensitivity | far_per_hour | far_per_day | time_in_warning | median_lead_time_seconds | brier_score | ece |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| cycle_hour_recording_val_tiw10_testsplit | SPH 60 / SOP 1440 | 53 | 3 | 0.05660377358490566 | 0.009413067552602437 | 0.22591362126245848 | 0.1141749723145072 | 76673.0 | 0.04907874401112727 | 0.04380269753172383 |

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
