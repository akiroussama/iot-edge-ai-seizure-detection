# MSG Data-Gap Triage - Local Artifacts

**Citation status:** not citable as a benchmark result before Gate C.

This report is a source-data and feasibility triage. It does not train a model,
does not report sensitivity, false alarms, Brier score, BSS, or clinical utility,
and does not mark any split or artifact as frozen.

## Summary

| dataset | patients_total | patients_p0_blocker | patients_p1_source_review_required | patients_p1_timeline_review_required | patients_p2_routine | events_total | events_matched | events_unmatched | horizons_total | horizons_not_main_table_ready | horizons_source_review_required | horizons_candidate_after_gate_b_c | claim_status | gate_c_implication |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| MSG | 11 | 3 | 7 | 0 | 1 | 768 | 510 | 258 | 6 | 5 | 1 | 0 | msg_gap_triage_pre_gate_c_not_citable | blocked_until_source_review_audit_and_freeze |

## Patient Triage

| patient_id | triage_priority | evaluable_status | issue_flags | recommended_action | events_total | events_matched | events_unmatched | matched_fraction | recordings | recording_hours | clusters | clustered_events | max_cluster_size | claim_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1942 | p0_blocker | not_evaluable_without_source_review | zero_parsed_recordings;zero_matched_events;unmatched_events;low_matched_fraction;large_seizure_cluster | recover_or_document_missing_wearable_segments_before_gate_c;exclude_from_evaluable_denominators_until_source_review;resolve_unmatched_events_or_restrict_denominator_explicitly;audit_patient_manifest_and_event_timestamps;review_cluster_definition_and_postictal_policy | 88 | 0 | 88 | 0.000 | 0 | 0.000 | 12 | 83 | 20 | msg_gap_triage_pre_gate_c_not_citable |
| 1219 | p0_blocker | not_evaluable_without_source_review | zero_parsed_recordings;zero_matched_events;unmatched_events;low_matched_fraction | recover_or_document_missing_wearable_segments_before_gate_c;exclude_from_evaluable_denominators_until_source_review;resolve_unmatched_events_or_restrict_denominator_explicitly;audit_patient_manifest_and_event_timestamps | 31 | 0 | 31 | 0.000 | 0 | 0.000 | 29 | 3 | 3 | msg_gap_triage_pre_gate_c_not_citable |
| 1675 | p0_blocker | not_evaluable_without_source_review | zero_parsed_recordings;zero_matched_events;unmatched_events;low_matched_fraction;large_seizure_cluster | recover_or_document_missing_wearable_segments_before_gate_c;exclude_from_evaluable_denominators_until_source_review;resolve_unmatched_events_or_restrict_denominator_explicitly;audit_patient_manifest_and_event_timestamps;review_cluster_definition_and_postictal_policy | 12 | 0 | 12 | 0.000 | 0 | 0.000 | 4 | 11 | 6 | msg_gap_triage_pre_gate_c_not_citable |
| 1988 | p1_source_review_required | partially_evaluable_matched_only | unmatched_events;large_seizure_cluster | resolve_unmatched_events_or_restrict_denominator_explicitly;review_cluster_definition_and_postictal_policy | 197 | 158 | 39 | 0.802 | 290 | 6612.207 | 119 | 113 | 6 | msg_gap_triage_pre_gate_c_not_citable |
| 1965 | p1_source_review_required | partially_evaluable_matched_only | unmatched_events | resolve_unmatched_events_or_restrict_denominator_explicitly | 241 | 210 | 31 | 0.871 | 366 | 8094.673 | 221 | 37 | 3 | msg_gap_triage_pre_gate_c_not_citable |
| 2002 | p1_source_review_required | partially_evaluable_matched_only | unmatched_events;low_matched_fraction | resolve_unmatched_events_or_restrict_denominator_explicitly;audit_patient_manifest_and_event_timestamps | 56 | 40 | 16 | 0.714 | 337 | 6234.824 | 52 | 7 | 3 | msg_gap_triage_pre_gate_c_not_citable |
| 1110 | p1_source_review_required | partially_evaluable_matched_only | unmatched_events;low_matched_fraction;large_seizure_cluster | resolve_unmatched_events_or_restrict_denominator_explicitly;audit_patient_manifest_and_event_timestamps;review_cluster_definition_and_postictal_policy | 31 | 16 | 15 | 0.516 | 146 | 4986.199 | 12 | 27 | 7 | msg_gap_triage_pre_gate_c_not_citable |
| 1904 | p1_source_review_required | partially_evaluable_matched_only | unmatched_events;low_matched_fraction;large_seizure_cluster | resolve_unmatched_events_or_restrict_denominator_explicitly;audit_patient_manifest_and_event_timestamps;review_cluster_definition_and_postictal_policy | 31 | 20 | 11 | 0.645 | 220 | 7860.681 | 15 | 24 | 6 | msg_gap_triage_pre_gate_c_not_citable |
| 1876 | p1_source_review_required | partially_evaluable_matched_only | unmatched_events;low_matched_fraction | resolve_unmatched_events_or_restrict_denominator_explicitly;audit_patient_manifest_and_event_timestamps | 44 | 35 | 9 | 0.795 | 204 | 4640.054 | 33 | 20 | 3 | msg_gap_triage_pre_gate_c_not_citable |
| 1869 | p1_source_review_required | partially_evaluable_matched_only | unmatched_events;low_matched_fraction | resolve_unmatched_events_or_restrict_denominator_explicitly;audit_patient_manifest_and_event_timestamps | 26 | 20 | 6 | 0.769 | 182 | 4520.158 | 22 | 7 | 3 | msg_gap_triage_pre_gate_c_not_citable |
| 1927 | p2_routine | routine_gate_b_sampling | none | routine_gate_b_sampling | 11 | 11 | 0 | 1.000 | 323 | 7677.402 | 11 | 0 | 1 | msg_gap_triage_pre_gate_c_not_citable |

## Horizon Triage

| sph_minutes | sop_minutes | horizon_status | issue_flags | recommended_action | windows_total | valid_windows | valid_window_fraction | positive_windows_total | valid_positive_windows | right_censored_unknown_windows | right_censored_unknown_fraction | events_total | events_coverable_by_valid_windows | event_coverable_fraction | events_recording_matched | events_recording_unmatched | claim_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5.000 | 1440.000 | not_main_table_ready | low_valid_window_fraction;high_right_censored_unknown_fraction;unmatched_events_present | demote_horizon_or_mark_as_feasibility_negative;document_right_censoring_before_split_freeze;resolve_unmatched_events_or_restrict_denominator_explicitly | 49577 | 8689 | 0.175 | 4058 | 3563 | 40365 | 0.814 | 768 | 456 | 0.594 | 510 | 258 | msg_gap_triage_pre_gate_c_not_citable |
| 60.000 | 1440.000 | not_main_table_ready | low_valid_window_fraction;high_right_censored_unknown_fraction;unmatched_events_present | demote_horizon_or_mark_as_feasibility_negative;document_right_censoring_before_split_freeze;resolve_unmatched_events_or_restrict_denominator_explicitly | 49577 | 7920 | 0.160 | 3781 | 3326 | 41178 | 0.831 | 768 | 436 | 0.568 | 510 | 258 | msg_gap_triage_pre_gate_c_not_citable |
| 60.000 | 360.000 | not_main_table_ready | high_right_censored_unknown_fraction;unmatched_events_present | document_right_censoring_before_split_freeze;resolve_unmatched_events_or_restrict_denominator_explicitly | 49577 | 34468 | 0.695 | 1960 | 1646 | 13774 | 0.278 | 768 | 426 | 0.555 | 510 | 258 | msg_gap_triage_pre_gate_c_not_citable |
| 5.000 | 30.000 | not_main_table_ready | low_event_coverable_fraction;unmatched_events_present | do_not_anchor_main_table_until_event_coverage_improves;resolve_unmatched_events_or_restrict_denominator_explicitly | 49577 | 46598 | 0.940 | 213 | 166 | 1152 | 0.023 | 768 | 177 | 0.230 | 510 | 258 | msg_gap_triage_pre_gate_c_not_citable |
| 60.000 | 30.000 | not_main_table_ready | low_event_coverable_fraction;unmatched_events_present | do_not_anchor_main_table_until_event_coverage_improves;resolve_unmatched_events_or_restrict_denominator_explicitly | 49577 | 44781 | 0.903 | 207 | 167 | 3058 | 0.062 | 768 | 179 | 0.233 | 510 | 258 | msg_gap_triage_pre_gate_c_not_citable |
| 5.000 | 360.000 | source_review_required | unmatched_events_present | resolve_unmatched_events_or_restrict_denominator_explicitly | 49577 | 36215 | 0.730 | 2054 | 1722 | 11950 | 0.241 | 768 | 444 | 0.578 | 510 | 258 | msg_gap_triage_pre_gate_c_not_citable |

## Interpretation Rules

- `p0_blocker` patients require source-data recovery or explicit exclusion before Gate C.
- `p1_source_review_required` patients can only be used with explicit matched-event denominators.
- `not_main_table_ready` horizons should be demoted to feasibility or negative findings until the
  source-data and right-censoring issues are resolved.
- No row in this report upgrades any current MSG pipeline check into a citable clinical result.

## Manifest

- Dataset: `MSG`
- Claim status: `msg_gap_triage_pre_gate_c_not_citable`
- Result status: `feasibility_gap_triage_not_model_result`
- Patient triage hash: `dfc6801f0f3ddc29716af4c6906a7572fbdbe3bb4e255816904311f4c5b08332`
- Horizon triage hash: `85228bb4f81daccaddbd0ec06394f48811e23bbe2ae92938c20accfd45392c6a`
