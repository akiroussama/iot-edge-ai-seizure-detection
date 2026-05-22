# Gate B Real Closeout Package

**Status:** `blocked_pending_real_evidence`

This package separates real Gate B closeout from positive simulation rows. Simulation
decisions can identify what a reviewer intended, but they are not copied into the
real decision template and do not unlock citable claims.

## Summary

| run_id | source_uri | ledger_rows | real_closed_rows | real_open_rows | blocked_rows | invalid_rows | simulation_available_open_rows | gate_b_real_closeout_status | claim_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| gate_b_real_closeout_2026-05-22 | reports/gate_b_closeout_2026-05-22/gate_b_closeout_ledger.csv | 8 | 3 | 5 | 0 | 0 | 5 | blocked_pending_real_evidence | gate_b_real_closeout_pending_validation_not_citable |

## Readiness Matrix

| ledger_id | priority | domain | current_closeout_status | real_closeout_state | simulation_decision_available | real_closeout_action |
| --- | --- | --- | --- | --- | --- | --- |
| GB-001 | P0 | MSG source-data coverage | closed_by_human_review | closed_real_attested_unverified | no | Keep attestation; rerun guardrails after every Gate B row is closed. |
| GB-002 | P0 | SeizeIT2 full-cohort evidence | closed_by_human_review | closed_real_attested_unverified | no | Keep attestation; rerun guardrails after every Gate B row is closed. |
| GB-003 | P0 | Freeze prerequisite | closed_by_human_review | closed_real_attested_unverified | no | Keep attestation; rerun guardrails after every Gate B row is closed. |
| GB-004 | P1 | MSG denominator integrity | pending_human_decision | missing_real_attestation_simulation_available | yes | Replace the simulated decision with real evidence and human attestation, or keep the row non-citable. Required evidence: Denominator policy signed off for source, matched, and prediction-coverable events; regenerated leaderboard rows expose all denominator fields. |
| GB-005 | P1 | MSG horizon feasibility | pending_human_decision | missing_real_attestation_simulation_available | yes | Replace the simulated decision with real evidence and human attestation, or keep the row non-citable. Required evidence: Advisor-approved main horizon choice or documented demotion to feasibility-negative analysis; regenerated horizon triage for chosen horizons. |
| GB-006 | P1 | SeizeIT2 track completeness | pending_human_decision | missing_real_attestation_simulation_available | yes | Replace the simulated decision with real evidence and human attestation, or keep the row non-citable. Required evidence: Ready track matrix covering required splits, tasks, and modality tracks; count summary matching documented expected counts. |
| GB-007 | P2 | MSG horizon source review | pending_human_decision | missing_real_attestation_simulation_available | yes | Replace the simulated decision with real evidence and human attestation, or keep the row non-citable. Required evidence: Source-review decision for each source-review-required horizon and evidence that chosen main horizons no longer depend on unresolved event gaps. |
| GB-008 | P2 | SeizeIT2 negative readiness rows | pending_human_decision | missing_real_attestation_simulation_available | yes | Replace the simulated decision with real evidence and human attestation, or keep the row non-citable. Required evidence: Paper-table or appendix plan preserving non-ready tracks as explicit negative readiness findings. |

## Real Decision Template

| ledger_id | required_evidence | human_decision | reviewer_name | review_date | evidence_uri | evidence_hash | resolution_notes | rerun_required | rerun_artifact_uri |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GB-004 | Denominator policy signed off for source, matched, and prediction-coverable events; regenerated leaderboard rows expose all denominator fields. |  |  |  |  |  |  |  |  |
| GB-005 | Advisor-approved main horizon choice or documented demotion to feasibility-negative analysis; regenerated horizon triage for chosen horizons. |  |  |  |  |  |  |  |  |
| GB-006 | Ready track matrix covering required splits, tasks, and modality tracks; count summary matching documented expected counts. |  |  |  |  |  |  |  |  |
| GB-007 | Source-review decision for each source-review-required horizon and evidence that chosen main horizons no longer depend on unresolved event gaps. |  |  |  |  |  |  |  |  |
| GB-008 | Paper-table or appendix plan preserving non-ready tracks as explicit negative readiness findings. |  |  |  |  |  |  |  |  |

## Rules

- Do not paste simulation rows into the real ledger without replacing them with real evidence.
- Evidence URIs and hashes remain reviewer attestations unless independently verified by a rerun.
- Gate B can only advance to validation rerun when `real_open_rows` is zero.
- Claim status: `gate_b_real_closeout_pending_validation_not_citable`

## Manifest

- Run ID: `gate_b_real_closeout_2026-05-22`
- Source URI: `reports/gate_b_closeout_2026-05-22/gate_b_closeout_ledger.csv`
- Readiness hash: `d839d2ee06890643fb6b99451435a69e943066a5f1e4b0b44d8478edbc30a567`
- Template hash: `29fd9540fe8563634fe1cedc744ff607f96f595a0536af562b53ab339b1feda5`
