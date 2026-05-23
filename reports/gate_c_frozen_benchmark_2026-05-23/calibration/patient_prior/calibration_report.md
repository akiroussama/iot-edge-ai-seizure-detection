# Calibration And Null-Corrected Skill Report

## Metadata

- Model: `patient_prior`
- References: `split_prevalence_prior`
- Result status: `gate_c_frozen_citable`
- Citation status: `citable_after_gate_c`
- Gate C status: `passed`
- Bootstrap samples: `1000`

## Summary

| series_name | series_role | prediction_rows | valid_prediction_rows | positive_windows | empirical_rate | mean_risk_score | brier_score | expected_calibration_error |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| patient_prior | model | 10309 | 1418 | 373 | 0.2630465444287729 | 0.3689751680551893 | 0.1276733800426928 | 0.13101441631256677 |
| split_prevalence_prior | reference | 10309 | 1418 | 373 | 0.2630465444287729 | 0.4754971590909091 | 0.23898832356317398 | 0.21245061466213622 |

## Brier Skill Score

| model_name | reference_name | model_brier_score | reference_brier_score | brier_skill_score | model_expected_calibration_error | reference_expected_calibration_error | valid_prediction_rows |
| --- | --- | --- | --- | --- | --- | --- | --- |
| patient_prior | split_prevalence_prior | 0.1276733800426928 | 0.23898832356317398 | 0.4657756574080335 | 0.13101441631256677 | 0.21245061466213622 | 1418 |

## Bootstrap Confidence Intervals

| scope | group_col | reference_name | metric | n_groups | n_bootstrap | mean | ci_low | ci_high |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| patient | patient_id | split_prevalence_prior | brier_skill_score | 8 | 1000 | 0.4026481814516308 | -0.42025363316071224 | 0.7709513355533065 |

## Reliability Bins

| series_name | series_role | bin | bin_start | bin_end | count | mean_score | empirical_rate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| patient_prior | model | 0 | 0.0 | 0.1 | 325 | 0.0569239189928845 | 0.09846153846153846 |
| patient_prior | model | 1 | 0.1 | 0.2 | 584 | 0.13112391930835735 | 0.03424657534246575 |
| patient_prior | model | 2 | 0.2 | 0.30000000000000004 | 71 | 0.2776605537018593 | 0.3380281690140845 |
| patient_prior | model | 3 | 0.30000000000000004 | 0.4 | 0 | nan | nan |
| patient_prior | model | 4 | 0.4 | 0.5 | 0 | nan | nan |
| patient_prior | model | 5 | 0.5 | 0.6000000000000001 | 0 | nan | nan |
| patient_prior | model | 6 | 0.6000000000000001 | 0.7000000000000001 | 0 | nan | nan |
| patient_prior | model | 7 | 0.7000000000000001 | 0.8 | 0 | nan | nan |
| patient_prior | model | 8 | 0.8 | 0.9 | 109 | 0.8571428571428573 | 0.0 |
| patient_prior | model | 9 | 0.9 | 1.0 | 329 | 0.9574093465412978 | 0.9027355623100304 |
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
