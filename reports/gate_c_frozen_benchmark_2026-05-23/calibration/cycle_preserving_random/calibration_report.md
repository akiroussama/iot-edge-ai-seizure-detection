# Calibration And Null-Corrected Skill Report

## Metadata

- Model: `cycle_preserving_random`
- References: `split_prevalence_prior`
- Result status: `gate_c_frozen_citable`
- Citation status: `citable_after_gate_c`
- Gate C status: `passed`
- Bootstrap samples: `1000`

## Summary

| series_name | series_role | prediction_rows | valid_prediction_rows | positive_windows | empirical_rate | mean_risk_score | brier_score | expected_calibration_error |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| cycle_preserving_random | model | 10309 | 1418 | 373 | 0.2630465444287729 | 0.4539645194593037 | 0.22237042583524766 | 0.19091797503053085 |
| split_prevalence_prior | reference | 10309 | 1418 | 373 | 0.2630465444287729 | 0.4754971590909091 | 0.23898832356317398 | 0.21245061466213622 |

## Brier Skill Score

| model_name | reference_name | model_brier_score | reference_brier_score | brier_skill_score | model_expected_calibration_error | reference_expected_calibration_error | valid_prediction_rows |
| --- | --- | --- | --- | --- | --- | --- | --- |
| cycle_preserving_random | split_prevalence_prior | 0.22237042583524766 | 0.23898832356317398 | 0.06953434996389507 | 0.19091797503053085 | 0.21245061466213622 | 1418 |

## Bootstrap Confidence Intervals

| scope | group_col | reference_name | metric | n_groups | n_bootstrap | mean | ci_low | ci_high |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| patient | patient_id | split_prevalence_prior | brier_skill_score | 8 | 1000 | 0.06766813954108201 | 0.03406978460542379 | 0.08880311651094253 |

## Reliability Bins

| series_name | series_role | bin | bin_start | bin_end | count | mean_score | empirical_rate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| cycle_preserving_random | model | 0 | 0.0 | 0.1 | 0 | nan | nan |
| cycle_preserving_random | model | 1 | 0.1 | 0.2 | 0 | nan | nan |
| cycle_preserving_random | model | 2 | 0.2 | 0.30000000000000004 | 65 | 0.28571428571428564 | 0.16923076923076924 |
| cycle_preserving_random | model | 3 | 0.30000000000000004 | 0.4 | 425 | 0.34041571748605337 | 0.16470588235294117 |
| cycle_preserving_random | model | 4 | 0.4 | 0.5 | 438 | 0.4634673848234276 | 0.24429223744292236 |
| cycle_preserving_random | model | 5 | 0.5 | 0.6000000000000001 | 333 | 0.5411300709461317 | 0.36036036036036034 |
| cycle_preserving_random | model | 6 | 0.6000000000000001 | 0.7000000000000001 | 157 | 0.6196086109080784 | 0.4140127388535032 |
| cycle_preserving_random | model | 7 | 0.7000000000000001 | 0.8 | 0 | nan | nan |
| cycle_preserving_random | model | 8 | 0.8 | 0.9 | 0 | nan | nan |
| cycle_preserving_random | model | 9 | 0.9 | 1.0 | 0 | nan | nan |
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
