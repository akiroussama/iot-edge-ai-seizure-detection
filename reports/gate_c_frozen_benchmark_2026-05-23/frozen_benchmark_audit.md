# Gate C Frozen Null Benchmark Audit

## Frozen-Only Guard

- Registry id: `msg_gate_c_sph60_sop1440_2026-05-23`
- Registry verification ok: `True`
- Registry artifacts verified: `7`
- Required benchmark inputs came from committed freeze artifacts, not `data/*`.
- Output manifest: `reports/gate_c_frozen_benchmark_2026-05-23/frozen_benchmark_manifest.json`

## Denominator

- Source events: `768`
- Event filter: `recording_match_status=matched`
- Events after filter: `510`
- Restricted to prediction coverage: `True`
- Events used for metrics on `test`: `54`

The filtered denominator is a matched, prediction-coverable subset. It is the
right denominator for comparing frozen forecasts on this split, but it must not
be described as all annotated MSG seizures.

## Frozen Null Results

| model_name | events_used_for_metrics | valid_prediction_rows | sensitivity | false_alarm_rate_per_day | time_in_warning | brier_score | brier_skill_score | brier_skill_score_ci_low | brier_skill_score_ci_high | expected_calibration_error |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| split_prevalence_prior | 54 | 1418 | 0.6481481481481481 | 1.5571227080394923 | 0.09873060648801128 | 0.23898832356317398 | 0.0 | 0.0 | 0.0 | 0.21245061466213622 |
| rate_matched_random | 54 | 1418 | 0.46296296296296297 | 1.472496473906911 | 0.09590973201692525 | 0.23898832356317398 | 0.0 | 0.0 | 0.0 | 0.21245061466213622 |
| patient_prior | 54 | 1418 | 0.05555555555555555 | 0.0846262341325811 | 0.0380818053596615 | 0.1276733800426928 | 0.4657756574080335 | -0.42025363316071224 | 0.7709513355533065 | 0.13101441631256677 |
| cycle_preserving_random | 54 | 1418 | 0.7407407407407407 | 0.5923836389280677 | 0.09732016925246827 | 0.22237042583524766 | 0.06953434996389507 | 0.03406978460542379 | 0.08880311651094253 | 0.19091797503053085 |

## Forecastability Classification

| model_name | forecastability_label | claim_status | paper_table_ready | forecastability_reason |
| --- | --- | --- | --- | --- |
| split_prevalence_prior | unforecastable_null_overlap | citable_after_gate_c | False | BSS confidence interval overlaps null |
| rate_matched_random | unforecastable_null_overlap | citable_after_gate_c | False | BSS confidence interval overlaps null |
| patient_prior | unforecastable_null_overlap | citable_after_gate_c | False | BSS confidence interval overlaps null |
| cycle_preserving_random | forecastable_above_null | citable_after_gate_c | True | BSS confidence interval is above null |

## Scientific Interpretation

- These rows are null baselines, not trained wearable models.
- `split_prevalence_prior` is the BSS reference; its self-skill should be zero.
- Any positive skill from `patient_prior` or `cycle_preserving_random` is evidence
  that patient/cycle structure in the frozen labels is exploitable, not proof of
  a deployable clinical model.
- A Q1-level claim still requires comparing non-null models against these frozen
  nulls, reporting denominator scope, and preserving negative/underpowered rows.
