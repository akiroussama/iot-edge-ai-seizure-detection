# SeizeIT2 Cohort Readiness - Local Artifacts

**Citation status:** not citable as a benchmark result before Gate C.

This report is a full-cohort claim guardrail. It consumes SeizeIT2 readiness
tables and count summaries, then records why a cohort-level claim is blocked or
ready for Gate C review. It does not train or score a model.

## Summary

| readiness_status | full_cohort_claim_status | gate_b_status | gate_c_status | patients_observed | events_observed | track_rows | ready_track_rows | blockers | warnings | claim_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| blocked | blocked_not_full_cohort_ready | passed | not_started | 1 | 2 | 1 | 0 | 19 | 1 | seizeit2_cohort_readiness_pre_gate_c_not_citable |

## Blockers

| issue_code | severity | detail | affected_rows | claim_status |
| --- | --- | --- | --- | --- |
| gate_c_not_passed | blocker | Gate C status is 'not_started'; artifacts are not frozen/citable. |  | seizeit2_cohort_readiness_pre_gate_c_not_citable |
| patients_below_full_cohort_threshold | blocker | Observed patients=1; required minimum is 100 for a full-cohort claim. | 1.0 | seizeit2_cohort_readiness_pre_gate_c_not_citable |
| events_below_full_cohort_threshold | blocker | Observed events=2; required minimum is 100 for a full-cohort claim. | 2.0 | seizeit2_cohort_readiness_pre_gate_c_not_citable |
| patients_expected_count_not_provided | blocker | Expected published count for patients was not supplied. |  | seizeit2_cohort_readiness_pre_gate_c_not_citable |
| recordings_expected_count_not_provided | blocker | Expected published count for recordings was not supplied. |  | seizeit2_cohort_readiness_pre_gate_c_not_citable |
| events_expected_count_not_provided | blocker | Expected published count for events was not supplied. |  | seizeit2_cohort_readiness_pre_gate_c_not_citable |
| official_split_manifest_not_clean | blocker | Official split statuses present: ['missing_official_manifest']. | 1.0 | seizeit2_cohort_readiness_pre_gate_c_not_citable |
| required_splits_missing | blocker | Missing required splits: ['train', 'val', 'test']. | 3.0 | seizeit2_cohort_readiness_pre_gate_c_not_citable |
| required_tasks_missing | blocker | Missing required tasks: ['ictal_detection', 'short_early_warning']. | 2.0 | seizeit2_cohort_readiness_pre_gate_c_not_citable |
| required_modality_tracks_missing | blocker | Missing required modality tracks: ['ecg', 'acc', 'bte_eeg', 'multimodal']. | 4.0 | seizeit2_cohort_readiness_pre_gate_c_not_citable |
| required_ready_track_missing | blocker | No ready track for split=train, task=ictal_detection. |  | seizeit2_cohort_readiness_pre_gate_c_not_citable |
| required_ready_track_missing | blocker | No ready track for split=train, task=short_early_warning. |  | seizeit2_cohort_readiness_pre_gate_c_not_citable |
| required_ready_track_missing | blocker | No ready track for split=train, task=long_horizon_forecasting. |  | seizeit2_cohort_readiness_pre_gate_c_not_citable |
| required_ready_track_missing | blocker | No ready track for split=val, task=ictal_detection. |  | seizeit2_cohort_readiness_pre_gate_c_not_citable |
| required_ready_track_missing | blocker | No ready track for split=val, task=short_early_warning. |  | seizeit2_cohort_readiness_pre_gate_c_not_citable |
| required_ready_track_missing | blocker | No ready track for split=val, task=long_horizon_forecasting. |  | seizeit2_cohort_readiness_pre_gate_c_not_citable |
| required_ready_track_missing | blocker | No ready track for split=test, task=ictal_detection. |  | seizeit2_cohort_readiness_pre_gate_c_not_citable |
| required_ready_track_missing | blocker | No ready track for split=test, task=short_early_warning. |  | seizeit2_cohort_readiness_pre_gate_c_not_citable |
| required_ready_track_missing | blocker | No ready track for split=test, task=long_horizon_forecasting. |  | seizeit2_cohort_readiness_pre_gate_c_not_citable |

## Warnings

| issue_code | severity | detail | affected_rows | claim_status |
| --- | --- | --- | --- | --- |
| non_ready_track_rows_present | warning | Some task/modality/split rows are not ready; keep them as negative readiness rows. | 1 | seizeit2_cohort_readiness_pre_gate_c_not_citable |

## Interpretation Rules

- `blocked_not_full_cohort_ready` means the current artifacts cannot support a
  full SeizeIT2 cohort claim.
- Count mismatches or missing expected counts must be resolved before any paper
  wording claims full-cohort comparability.
- Gate B and Gate C must both pass before any citable SeizeIT2 result is reported.
- Non-ready track rows are negative readiness findings, not hidden exclusions.

## Manifest

- Claim status: `seizeit2_cohort_readiness_pre_gate_c_not_citable`
- Result status: `cohort_readiness_guardrail_not_model_result`
- Track hash: `ccc2d9c7da7518fd03bd854bc224a59ada5212a0bf83578e47ec97288abddae8`
- Count-summary hash: `39a5d4c40c975e8f229a6bb93de61f142bab688bb13f86ac958621f08993e8e1`
