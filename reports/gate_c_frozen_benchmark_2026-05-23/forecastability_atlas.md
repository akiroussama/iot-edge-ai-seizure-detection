# Gate C Frozen Forecastability Atlas

This atlas is a forecastability synthesis, not a new model metric.
Rows marked non-citable must not be used as benchmark claims before Gate C.

## Label Counts

- `forecastable_above_null`: 1
- `unforecastable_null_overlap`: 3

## Atlas

| atlas_scope | dataset | cohort | modality | horizon_name | model_name | brier_skill_score | brier_skill_score_ci_low | brier_skill_score_ci_high | sensitivity | false_alarm_rate_per_day | time_in_warning | reliability_slope | forecastability_label | claim_status | paper_table_ready |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| pooled | msg | matched_prediction_coverable_test | labels_only_null | SPH60_SOP1440 | split_prevalence_prior | 0 | 0 | 0 | 0.648 | 1.557 | 0.099 |  | unforecastable_null_overlap | citable_after_gate_c | False |
| pooled | msg | matched_prediction_coverable_test | labels_only_null | SPH60_SOP1440 | rate_matched_random | 0 | 0 | 0 | 0.463 | 1.472 | 0.096 |  | unforecastable_null_overlap | citable_after_gate_c | False |
| pooled | msg | matched_prediction_coverable_test | labels_only_null | SPH60_SOP1440 | patient_prior | 0.466 | -0.420 | 0.771 | 0.056 | 0.085 | 0.038 | 0.769 | unforecastable_null_overlap | citable_after_gate_c | False |
| pooled | msg | matched_prediction_coverable_test | labels_only_null | SPH60_SOP1440 | cycle_preserving_random | 0.070 | 0.034 | 0.089 | 0.741 | 0.592 | 0.097 | 0.877 | forecastable_above_null | citable_after_gate_c | True |

Interpretation:

- `forecastable_above_null` requires BSS confidence bounds above the null baseline.
- `unforecastable_null_overlap` keeps negative findings visible.
- `paper_table_ready` is true only for citable Gate-C-passed rows.
- Rows without confidence intervals remain exploratory even when BSS is positive.