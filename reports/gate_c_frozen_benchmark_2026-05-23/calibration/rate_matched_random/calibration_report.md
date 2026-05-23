# Calibration And Null-Corrected Skill Report

## Metadata

- Model: `rate_matched_random`
- References: `split_prevalence_prior`
- Result status: `gate_c_frozen_citable`
- Citation status: `citable_after_gate_c`
- Gate C status: `passed`
- Bootstrap samples: `1000`

## Summary

| series_name | series_role | prediction_rows | valid_prediction_rows | positive_windows | empirical_rate | mean_risk_score | brier_score | expected_calibration_error |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| rate_matched_random | model | 10309 | 1418 | 373 | 0.2630465444287729 | 0.4754971590909091 | 0.23898832356317398 | 0.21245061466213622 |
| split_prevalence_prior | reference | 10309 | 1418 | 373 | 0.2630465444287729 | 0.4754971590909091 | 0.23898832356317398 | 0.21245061466213622 |

## Brier Skill Score

| model_name | reference_name | model_brier_score | reference_brier_score | brier_skill_score | model_expected_calibration_error | reference_expected_calibration_error | valid_prediction_rows |
| --- | --- | --- | --- | --- | --- | --- | --- |
| rate_matched_random | split_prevalence_prior | 0.23898832356317398 | 0.23898832356317398 | 0.0 | 0.21245061466213622 | 0.21245061466213622 | 1418 |

## Bootstrap Confidence Intervals

| scope | group_col | reference_name | metric | n_groups | n_bootstrap | mean | ci_low | ci_high |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| patient | patient_id | split_prevalence_prior | brier_skill_score | 8 | 1000 | 0.0 | 0.0 | 0.0 |

## Reliability Bins

| series_name | series_role | bin | bin_start | bin_end | count | mean_score | empirical_rate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| rate_matched_random | model | 0 | 0.0 | 0.1 | 0 | nan | nan |
| rate_matched_random | model | 1 | 0.1 | 0.2 | 0 | nan | nan |
| rate_matched_random | model | 2 | 0.2 | 0.30000000000000004 | 0 | nan | nan |
| rate_matched_random | model | 3 | 0.30000000000000004 | 0.4 | 0 | nan | nan |
| rate_matched_random | model | 4 | 0.4 | 0.5 | 1418 | 0.4754971590909091 | 0.2630465444287729 |
| rate_matched_random | model | 5 | 0.5 | 0.6000000000000001 | 0 | nan | nan |
| rate_matched_random | model | 6 | 0.6000000000000001 | 0.7000000000000001 | 0 | nan | nan |
| rate_matched_random | model | 7 | 0.7000000000000001 | 0.8 | 0 | nan | nan |
| rate_matched_random | model | 8 | 0.8 | 0.9 | 0 | nan | nan |
| rate_matched_random | model | 9 | 0.9 | 1.0 | 0 | nan | nan |
| split_prevalence_prior | reference | 0 | 0.0 | 0.1 | 0 | nan | nan |
| split_prevalence_prior | reference | 1 | 0.1 | 0.2 | 0 | nan | nan |
| split_prevalence_prior | reference | 2 | 0.2 | 0.30000000000000004 | 0 | nan | nan |
| split_prevalence_prior | reference | 3 | 0.30000000000000004 | 0.4 | 0 | nan | nan |
| split_prevalence_prior | reference | 4 | 0.4 | 0.5 | 1418 | 0.4754971590909091 | 0.2630465444287729 |
| split_prevalence_prior | reference | 5 | 0.5 | 0.6000000000000001 | 0 | nan | nan |
| split_prevalence_prior | reference | 6 | 0.6000000000000001 | 0.7000000000000001 | 0 | nan | nan |
| split_prevalence_prior | reference | 7 | 0.7000000000000001 | 0.8 | 0 | nan | nan |
| split_prevalence_prior | reference | 8 | 0.8 | 0.9 | 0 | nan | nan |
| split_prevalence_prior | reference | 9 | 0.9 | 1.0 | 0 | nan | nan |
