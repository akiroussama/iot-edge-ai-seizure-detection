# Gate B Validation Rerun

**Status:** `passed_ready_for_gate_c_dry_run`

This report validates real Gate B closeout decisions against the current local
guardrail rerun. It is not a Gate C pass and it does not make benchmark rows
citable.

## Summary

| run_id | source_uri | guardrail_actions | gate_b_actions | gate_b_closed_actions | gate_b_open_actions | gate_b_p0_open_actions | gate_b_source_review_actions | msg_p0_patients | msg_unmatched_events | msg_not_main_horizons | msg_source_review_horizons | seizeit2_readiness_status | seizeit2_blockers | seizeit2_warnings | simulation_marker_detected | gate_b_validation_status | gate_b_passed | gate_c_next_status | claim_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| gate_b_final_validation_rerun_2026-05-23 | reports/gate_b_final_human_closeout_2026-05-23/validation_guardrails | 8 | 7 | 7 | 0 | 0 | 0 | 3 | 258 | 5 | 1 | blocked | 19 | 1 | False | passed_ready_for_gate_c_dry_run | True | ready_for_gate_c_dry_run | gate_b_validation_rerun_not_citable_pre_gate_c |

## Validation Matrix

| ledger_id | gate | priority | domain | validation_status | human_decision | next_action |
| --- | --- | --- | --- | --- | --- | --- |
| GB-001 | Gate B | P0 | MSG source-data coverage | closed_by_real_attestation | RESOLVED | No real-closeout action; keep rerun evidence attached to the ledger. |
| GB-002 | Gate B | P0 | SeizeIT2 full-cohort evidence | closed_by_real_attestation | APPROVED_EXCLUSION | No real-closeout action; keep rerun evidence attached to the ledger. |
| GB-003 | Gate C | P0 | Freeze prerequisite | closed_by_real_attestation | APPROVED_EXCLUSION | No real-closeout action; keep rerun evidence attached to the ledger. |
| GB-004 | Gate B | P1 | MSG denominator integrity | closed_by_real_attestation | RESOLVED | No real-closeout action; keep rerun evidence attached to the ledger. |
| GB-005 | Gate B | P1 | MSG horizon feasibility | closed_by_real_attestation | RESOLVED | No real-closeout action; keep rerun evidence attached to the ledger. |
| GB-006 | Gate B | P1 | SeizeIT2 track completeness | closed_by_real_attestation | APPROVED_EXCLUSION | No real-closeout action; keep rerun evidence attached to the ledger. |
| GB-007 | Gate B | P2 | MSG horizon source review | closed_by_real_attestation | DEFERRED | No real-closeout action; keep rerun evidence attached to the ledger. |
| GB-008 | Gate B | P2 | SeizeIT2 negative readiness rows | closed_by_real_attestation | RESOLVED | No real-closeout action; keep rerun evidence attached to the ledger. |

## Rules

- Simulation markers in a real closeout ledger block validation.
- Current Gate B guardrail actions must have real closed attestations.
- Rows needing source review or invalid metadata block Gate B.
- A passing Gate B validation only enables Gate C dry-run; it is not a citable
  benchmark result.
- Claim status: `gate_b_validation_rerun_not_citable_pre_gate_c`

## Manifest

- Run ID: `gate_b_final_validation_rerun_2026-05-23`
- Source URI: `reports/gate_b_final_human_closeout_2026-05-23/validation_guardrails`
- Matrix hash: `4f944e6c44c32f9a734c26b6d581844e82cc98f5ea2447a34404ad90a470e619`
- Summary hash: `d971327c70f4aba68d12b3229247e8014fd986be43261a433816aa830511f67d`
