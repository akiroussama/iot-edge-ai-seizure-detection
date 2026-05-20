# MSG-local-full-download Dataset Report

> SUPERSEDED LEGACY REPORT: this file predates the Phase R right-censoring, recording-wise split,
> onset-anchored postictal, cluster-denominator, and false-alarm episode fixes. Keep it only as a
> historical audit artifact. Use `reports/msg_hr_tachycardia_recording_splitaware_check/` and
> `reports/msg_hr_tachycardia_cluster_recording_splitaware_check/` for the current pipeline check.

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
| 8.0 | 2057.0 | 49596.0 | 510.0 | 49596.0 |

## Label Distribution

| total_windows | valid_windows | excluded_windows | positive_windows | positive_fraction_valid |
| --- | --- | --- | --- | --- |
| 49596.0 | 47713.0 | 1883.0 | 3325.0 | 0.06968750654957769 |

## Baseline

| baseline | horizon | n_events | n_forecasted | sensitivity | far_per_hour | far_per_day | time_in_warning | median_lead_time_seconds | brier_score | ece |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| hr_tachycardia_tiw10 | SPH 60 / SOP 1440 | 510 | 208 | 0.40784313725490196 | 0.03747406367237441 | 0.8993775281369857 | 0.09993083645966508 | 29407.0 | 0.32550513453865654 | 0.42924298158852886 |

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
