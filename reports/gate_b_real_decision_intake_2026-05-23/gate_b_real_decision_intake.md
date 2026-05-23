# Gate B Real Decision Intake

**Status:** `blocked_invalid_or_incomplete_decisions`

This preflight validates reviewer-supplied real decisions before they are
applied to the Gate B closeout ledger. It does not close Gate B and does not make
benchmark rows citable.

## Summary

| run_id | source_uri | required_rows | decision_rows | accepted_rows | closing_rows | human_blocker_rows | issue_rows | missing_rows | incomplete_rows | invalid_decision_rows | simulation_marker_rows | invalid_hash_rows | rerun_artifact_issue_rows | unknown_decision_rows | intake_status | gate_b_next_status | claim_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| gate_b_real_decision_intake_2026-05-23 | reports/gate_b_real_closeout_2026-05-22/gate_b_real_closeout_required_decisions_template.csv | 5 | 5 | 0 | 0 | 0 | 5 | 0 | 5 | 0 | 0 | 0 | 5 | 0 | blocked_invalid_or_incomplete_decisions | blocked_by_real_decision_intake | gate_b_real_decision_intake_not_citable_pre_gate_c |

## Decision Rows

| ledger_id | decision_status | human_decision | evidence_hash_status | rerun_artifact_status | next_action |
| --- | --- | --- | --- | --- | --- |
| GB-004 | incomplete_decision_metadata |  | missing | invalid_rerun_required | Fill required fields: human_decision, reviewer_name, review_date, evidence_uri, evidence_hash, resolution_notes, rerun_required. |
| GB-005 | incomplete_decision_metadata |  | missing | invalid_rerun_required | Fill required fields: human_decision, reviewer_name, review_date, evidence_uri, evidence_hash, resolution_notes, rerun_required. |
| GB-006 | incomplete_decision_metadata |  | missing | invalid_rerun_required | Fill required fields: human_decision, reviewer_name, review_date, evidence_uri, evidence_hash, resolution_notes, rerun_required. |
| GB-007 | incomplete_decision_metadata |  | missing | invalid_rerun_required | Fill required fields: human_decision, reviewer_name, review_date, evidence_uri, evidence_hash, resolution_notes, rerun_required. |
| GB-008 | incomplete_decision_metadata |  | missing | invalid_rerun_required | Fill required fields: human_decision, reviewer_name, review_date, evidence_uri, evidence_hash, resolution_notes, rerun_required. |

## Rules

- Every required ledger row must have a real decision.
- Simulation markers block intake.
- `evidence_hash` must use `sha256:<64 hex>`.
- `rerun_required=yes` requires a non-empty rerun artifact URI.
- `BLOCKED` and `NEEDS_SOURCE_REVIEW` are valid human decisions, but they keep
  Gate B blocked after application.
- Claim status: `gate_b_real_decision_intake_not_citable_pre_gate_c`

## Manifest

- Run ID: `gate_b_real_decision_intake_2026-05-23`
- Source URI: `reports/gate_b_real_closeout_2026-05-22/gate_b_real_closeout_required_decisions_template.csv`
- Rows hash: `89895ba2a9f2ff282f4a11f09d80c360c664bb8245a8a078d433d92a936fc1d4`
- Summary hash: `b75a9f1ab25eb8c6c89e12e5992f2f9e0212b6406c98c9cf789bd0be19852c37`
