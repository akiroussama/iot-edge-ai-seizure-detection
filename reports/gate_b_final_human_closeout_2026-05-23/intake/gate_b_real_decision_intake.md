# Gate B Real Decision Intake

**Status:** `ready_for_closeout_application`

This preflight validates reviewer-supplied real decisions before they are
applied to the Gate B closeout ledger. It does not close Gate B and does not make
benchmark rows citable.

## Summary

| run_id | source_uri | required_rows | decision_rows | accepted_rows | closing_rows | human_blocker_rows | issue_rows | missing_rows | incomplete_rows | invalid_decision_rows | simulation_marker_rows | invalid_hash_rows | rerun_artifact_issue_rows | unknown_decision_rows | intake_status | gate_b_next_status | claim_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| gate_b_final_human_decision_intake_2026-05-23 | reports/gate_b_final_human_closeout_2026-05-23/gate_b_real_decisions_2026-05-23.csv | 5 | 5 | 5 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | ready_for_closeout_application | ready_to_apply_closeout_and_run_validation | gate_b_real_decision_intake_not_citable_pre_gate_c |

## Decision Rows

| ledger_id | decision_status | human_decision | evidence_hash_status | rerun_artifact_status | next_action |
| --- | --- | --- | --- | --- | --- |
| GB-004 | accepted_closing_decision | RESOLVED | valid_sha256 | present | Ready to apply to the real closeout ledger. |
| GB-005 | accepted_closing_decision | RESOLVED | valid_sha256 | present | Ready to apply to the real closeout ledger. |
| GB-006 | accepted_closing_decision | APPROVED_EXCLUSION | valid_sha256 | present | Ready to apply to the real closeout ledger. |
| GB-007 | accepted_closing_decision | DEFERRED | valid_sha256 | not_required | Ready to apply to the real closeout ledger. |
| GB-008 | accepted_closing_decision | RESOLVED | valid_sha256 | not_required | Ready to apply to the real closeout ledger. |

## Rules

- Every required ledger row must have a real decision.
- Simulation markers block intake.
- `evidence_hash` must use `sha256:<64 hex>`.
- `rerun_required=yes` requires a non-empty rerun artifact URI.
- `BLOCKED` and `NEEDS_SOURCE_REVIEW` are valid human decisions, but they keep
  Gate B blocked after application.
- Claim status: `gate_b_real_decision_intake_not_citable_pre_gate_c`

## Manifest

- Run ID: `gate_b_final_human_decision_intake_2026-05-23`
- Source URI: `reports/gate_b_final_human_closeout_2026-05-23/gate_b_real_decisions_2026-05-23.csv`
- Rows hash: `7eab290abd422c793514c421c1ad276c0760251406af3676051f41c695d0e07b`
- Summary hash: `680eca48dbd61cb559d3c9d3f483cc4ae74774f772f253119d17b24eaa2f61b2`
