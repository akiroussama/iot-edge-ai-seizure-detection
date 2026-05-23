# Gate B/C Action Checklist

**Citation status:** not citable as a benchmark result before Gate C.

This checklist is generated from local guardrail outputs. It is an operational
audit plan, not a model result and not clinical evidence.

## Summary

| source_label | actions_total | p0_actions | p1_actions | p2_actions | gate_b_actions | gate_c_actions | claim_status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| local_committed_reports_2026-05-22 | 8 | 3 | 3 | 2 | 7 | 1 | gate_bc_action_checklist_pre_gate_c_not_citable |

## Actions

| gate | priority | domain | blocker_source | action | evidence | owner | exit_criterion | claim_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Gate B | P0 | MSG source-data coverage | msg_gap_patient_triage | Recover or explicitly document exclusion for zero-recording/zero-matched patients. | Patients: 1942, 1219, 1675; events_unmatched=131. | human_clinical_audit | Each P0 patient has recovered wearable segments or an advisor-approved exclusion record, and rerun MSG triage has zero p0_blocker rows. | gate_bc_action_checklist_pre_gate_c_not_citable |
| Gate B | P0 | SeizeIT2 full-cohort evidence | seizeit2_cohort_readiness_blockers | Stop full-cohort wording until official split/count/source coverage is complete. | Blockers: gate_c_not_passed, patients_below_full_cohort_threshold, events_below_full_cohort_threshold, official_split_manifest_not_clean. | human_clinical_audit | SeizeIT2 readiness rerun reports Gate B/Gate C passed, expected counts verified, official splits clean, and no P0 cohort blockers. | gate_bc_action_checklist_pre_gate_c_not_citable |
| Gate C | P0 | Freeze prerequisite | combined_guardrails | Do not freeze splits or citable rows until Gate B checklist items are closed. | MSG blockers=3 P0 patients; SeizeIT2 blockers=19. | project_lead | Gate B audit log is complete, guardrails rerun cleanly, and Gate C dry-run reports ready_for_gate_c_review. | gate_bc_action_checklist_pre_gate_c_not_citable |
| Gate B | P1 | MSG denominator integrity | msg_gap_patient_triage | Resolve unmatched events or lock a matched-event-only denominator policy. | Patients: 1988, 1965, 2002, 1110, 1904, 1876, 1869; events_unmatched=127. | human_clinical_audit | All unmatched events have source-review decisions and every leaderboard row declares source, matched, and prediction-coverable denominators. | gate_bc_action_checklist_pre_gate_c_not_citable |
| Gate B | P1 | MSG horizon feasibility | msg_gap_horizon_triage | Demote failing SPH/SOP horizons or document them as feasibility-negative analyses. | Horizons: SPH5/SOP1440, SPH60/SOP1440, SPH60/SOP360, SPH5/SOP30, SPH60/SOP30; min_valid_window_fraction=0.160; min_event_coverable_fraction=0.230. | human_clinical_audit | Main-paper horizon choice is advisor-approved and any failing horizons are excluded from main claims or labeled as negative feasibility findings. | gate_bc_action_checklist_pre_gate_c_not_citable |
| Gate B | P1 | SeizeIT2 track completeness | seizeit2_cohort_readiness_blockers | Complete required split/task/modality readiness rows before benchmark claims. | Blockers: patients_expected_count_not_provided, recordings_expected_count_not_provided, events_expected_count_not_provided, required_splits_missing, required_tasks_missing, required_modality_tracks_missing, required_ready_track_missing, required_ready_track_missing, required_ready_track_missing, required_ready_track_missing, required_ready_track_missing, required_ready_track_missing, ... (15 total). | human_clinical_audit | All required split/task/modality combinations have ready track rows. | gate_bc_action_checklist_pre_gate_c_not_citable |
| Gate B | P2 | MSG horizon source review | msg_gap_horizon_triage | Keep source-review-required horizons out of citable tables until event gaps close. | Horizons needing source review: SPH5/SOP360. | human_clinical_audit | Rerun horizon triage has no source_review_required rows for chosen main horizons. | gate_bc_action_checklist_pre_gate_c_not_citable |
| Gate B | P2 | SeizeIT2 negative readiness rows | seizeit2_cohort_readiness_warnings | Preserve non-ready track rows as explicit negative readiness findings. | Warnings: non_ready_track_rows_present. | human_clinical_audit | Paper tables and text disclose non-ready tracks instead of hiding them. | gate_bc_action_checklist_pre_gate_c_not_citable |

## Interpretation Rules

- P0 actions block any claim of full evaluation readiness.
- P1 actions block main-paper tables until resolved or explicitly demoted.
- P2 actions should be completed before submission packaging.
- Gate C freeze can start only after Gate B actions are closed and the Gate C
  dry-run reports `ready_for_gate_c_review`.

## Manifest

- Claim status: `gate_bc_action_checklist_pre_gate_c_not_citable`
- Source label: `local_committed_reports_2026-05-22`
- Actions hash: `cfd3674564df44be3cefeda23faa61b93bfe77054b7469cdaa4adfa85d69e8ea`
