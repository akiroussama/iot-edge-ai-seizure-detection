# Gate B Validation Rerun

**Status:** `blocked_pending_real_closeout`

This report validates real Gate B closeout decisions against the current local
guardrail rerun. It is not a Gate C pass and it does not make benchmark rows
citable.

## Summary

| run_id | source_uri | guardrail_actions | gate_b_actions | gate_b_closed_actions | gate_b_open_actions | gate_b_p0_open_actions | gate_b_source_review_actions | msg_p0_patients | msg_unmatched_events | msg_not_main_horizons | msg_source_review_horizons | seizeit2_readiness_status | seizeit2_blockers | seizeit2_warnings | simulation_marker_detected | gate_b_validation_status | gate_b_passed | gate_c_next_status | claim_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| gate_b_validation_rerun_2026-05-22 | reports/gate_b_validation_rerun_2026-05-22/guardrails | 8 | 7 | 2 | 5 | 0 | 0 | 3 | 258 | 5 | 1 | blocked | 20 | 1 | False | blocked_pending_real_closeout | False | blocked_by_gate_b_validation | gate_b_validation_rerun_not_citable_pre_gate_c |

## Validation Matrix

| ledger_id | gate | priority | domain | validation_status | human_decision | next_action |
| --- | --- | --- | --- | --- | --- | --- |
| GB-001 | Gate B | P0 | MSG source-data coverage | closed_by_real_attestation | RESOLVED | No real-closeout action; keep rerun evidence attached to the ledger. |
| GB-002 | Gate B | P0 | SeizeIT2 full-cohort evidence | closed_by_real_attestation | APPROVED_EXCLUSION | No real-closeout action; keep rerun evidence attached to the ledger. |
| GB-003 | Gate C | P0 | Freeze prerequisite | closed_by_real_attestation | APPROVED_EXCLUSION | No real-closeout action; keep rerun evidence attached to the ledger. |
| GB-004 | Gate B | P1 | MSG denominator integrity | pending_real_closeout |  | Complete real human closeout for this guardrail action with reviewer, date, evidence URI, and rerun artifact when required. |
| GB-005 | Gate B | P1 | MSG horizon feasibility | pending_real_closeout |  | Complete real human closeout for this guardrail action with reviewer, date, evidence URI, and rerun artifact when required. |
| GB-006 | Gate B | P1 | SeizeIT2 track completeness | pending_real_closeout |  | Complete real human closeout for this guardrail action with reviewer, date, evidence URI, and rerun artifact when required. |
| GB-007 | Gate B | P2 | MSG horizon source review | pending_real_closeout |  | Complete real human closeout for this guardrail action with reviewer, date, evidence URI, and rerun artifact when required. |
| GB-008 | Gate B | P2 | SeizeIT2 negative readiness rows | pending_real_closeout |  | Complete real human closeout for this guardrail action with reviewer, date, evidence URI, and rerun artifact when required. |

## Rules

- Simulation markers in a real closeout ledger block validation.
- Current Gate B guardrail actions must have real closed attestations.
- Rows needing source review or invalid metadata block Gate B.
- A passing Gate B validation only enables Gate C dry-run; it is not a citable
  benchmark result.
- Claim status: `gate_b_validation_rerun_not_citable_pre_gate_c`

## Manifest

- Run ID: `gate_b_validation_rerun_2026-05-22`
- Source URI: `reports/gate_b_validation_rerun_2026-05-22/guardrails`
- Matrix hash: `7960cedebe1449f3da4095ef125553691f5f68abd7ce3234452eaefdbb1df78b`
- Summary hash: `4c10f71f759823ee1060ed3233586ed18b43d598f84a66931bf1fa56009238c7`
