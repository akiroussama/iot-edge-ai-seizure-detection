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

## Dataset Summary

| patients | recordings | windows | events | window_hours_sum |
| --- | --- | --- | --- | --- |
| 4.0 | 858.0 | 19964.0 | 111.0 | 19964.0 |

## Label Distribution

| total_windows | valid_windows | excluded_windows | positive_windows | positive_fraction_valid |
| --- | --- | --- | --- | --- |
| 19964.0 | 19553.0 | 411.0 | 1008.0 | 0.051552191479568354 |

## Baseline

| baseline | horizon | n_events | n_forecasted | sensitivity | far_per_hour | far_per_day | time_in_warning | median_lead_time_seconds | brier_score | ece |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| random_rate_matched_tiw10 | SPH 60 / SOP 1440 | 111 | 70 | 0.6306306306306306 | 0.04229529995397126 | 1.01508719889531 | 0.09988237099166368 | 43278.0 | 0.15130343799271098 | 0.2447543514512368 |

## Event Coverage

```json
{
  "matched": 111,
  "unmatched": 177
}
```

## Required Manual Audit

1. Inspect seizure-centered windows in the exported label audit CSV.
2. Verify onset timestamps against source annotations.
3. Confirm ictal and postictal exclusions around every audited seizure.
4. Confirm whether this run is detection, early warning, short-horizon forecasting, or long-horizon forecasting.
5. Freeze splits and rerun leakage audit before any A100 training.
