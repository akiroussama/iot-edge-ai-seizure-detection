# Gate B Real Closeout Package

**Status:** `ready_for_gate_b_validation_rerun`

This package separates real Gate B closeout from positive simulation rows. Simulation
decisions can identify what a reviewer intended, but they are not copied into the
real decision template and do not unlock citable claims.

## Summary

| run_id | source_uri | ledger_rows | real_closed_rows | real_open_rows | blocked_rows | invalid_rows | simulation_available_open_rows | gate_b_real_closeout_status | claim_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| gate_b_final_real_closeout_package_2026-05-23 | reports/gate_b_final_human_closeout_2026-05-23/closeout/gate_b_closeout_ledger.csv | 8 | 8 | 0 | 0 | 0 | 0 | ready_for_gate_b_validation_rerun | gate_b_real_closeout_pending_validation_not_citable |

## Readiness Matrix

| ledger_id | priority | domain | current_closeout_status | real_closeout_state | simulation_decision_available | real_closeout_action |
| --- | --- | --- | --- | --- | --- | --- |
| GB-001 | P0 | MSG source-data coverage | closed_by_human_review | closed_real_attested_unverified | no | Keep attestation; rerun guardrails after every Gate B row is closed. |
| GB-002 | P0 | SeizeIT2 full-cohort evidence | closed_by_human_review | closed_real_attested_unverified | no | Keep attestation; rerun guardrails after every Gate B row is closed. |
| GB-003 | P0 | Freeze prerequisite | closed_by_human_review | closed_real_attested_unverified | no | Keep attestation; rerun guardrails after every Gate B row is closed. |
| GB-004 | P1 | MSG denominator integrity | closed_by_human_review | closed_real_attested_unverified | no | Keep attestation; rerun guardrails after every Gate B row is closed. |
| GB-005 | P1 | MSG horizon feasibility | closed_by_human_review | closed_real_attested_unverified | no | Keep attestation; rerun guardrails after every Gate B row is closed. |
| GB-006 | P1 | SeizeIT2 track completeness | closed_by_human_review | closed_real_attested_unverified | no | Keep attestation; rerun guardrails after every Gate B row is closed. |
| GB-007 | P2 | MSG horizon source review | closed_by_human_review | closed_real_attested_unverified | no | Keep attestation; rerun guardrails after every Gate B row is closed. |
| GB-008 | P2 | SeizeIT2 negative readiness rows | closed_by_human_review | closed_real_attested_unverified | no | Keep attestation; rerun guardrails after every Gate B row is closed. |

## Real Decision Template

_No rows._

## Rules

- Do not paste simulation rows into the real ledger without replacing them with real evidence.
- Evidence URIs and hashes remain reviewer attestations unless independently verified by a rerun.
- Gate B can only advance to validation rerun when `real_open_rows` is zero.
- Claim status: `gate_b_real_closeout_pending_validation_not_citable`

## Manifest

- Run ID: `gate_b_final_real_closeout_package_2026-05-23`
- Source URI: `reports/gate_b_final_human_closeout_2026-05-23/closeout/gate_b_closeout_ledger.csv`
- Readiness hash: `e501b09ae64049e29b315287a9a5b58d879535e069eba14389cf3b6ca43eac51`
- Template hash: `0d49f5ebc95eca5b095bce93ac296448bd4879c16136916510b2b7e36cf317ad`
