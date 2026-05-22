# Gate B Closeout Ledger

**Status:** pending human closeout; this is not a Gate B pass.

This ledger converts guardrail actions into human-review rows. It does not mark
any blocker as resolved. Reviewers must fill the human decision columns and
attach evidence before Gate B can be rerun.

## Summary

| run_id | source_uri | ledger_rows | closed_rows | open_rows | blocked_rows | invalid_rows | p0_open_rows | gate_b_status | claim_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| gate_b_closeout_2026-05-22 | reports/gate_b_closeout_2026-05-22/gate_b_closeout_decisions_partial_2026-05-22.csv | 8 | 3 | 5 | 0 | 0 | 0 | blocked_pending_human_closeout | gate_b_closeout_ledger_pending_human_review_not_citable |

## Ledger Preview

| ledger_id | gate | priority | domain | action | required_evidence | closeout_status |
| --- | --- | --- | --- | --- | --- | --- |
| GB-001 | Gate B | P0 | MSG source-data coverage | Recover or explicitly document exclusion for zero-recording/zero-matched patients. | Per-patient source decision for each P0 MSG patient: recovered wearable segment manifest or advisor-approved exclusion record; rerun MSG triage showing zero p0_blocker rows. | closed_by_human_review |
| GB-002 | Gate B | P0 | SeizeIT2 full-cohort evidence | Stop full-cohort wording until official split/count/source coverage is complete. | Official SeizeIT2 split manifest, expected-count source citations, full-cohort artifact coverage, and rerun cohort readiness with no P0 blockers. | closed_by_human_review |
| GB-003 | Gate C | P0 | Freeze prerequisite | Do not freeze splits or citable rows until Gate B checklist items are closed. | Completed Gate B ledger, clean guardrail rerun, and Gate C dry-run reporting ready_for_gate_c_review before split freeze. | closed_by_human_review |
| GB-004 | Gate B | P1 | MSG denominator integrity | Resolve unmatched events or lock a matched-event-only denominator policy. | Denominator policy signed off for source, matched, and prediction-coverable events; regenerated leaderboard rows expose all denominator fields. | pending_human_decision |
| GB-005 | Gate B | P1 | MSG horizon feasibility | Demote failing SPH/SOP horizons or document them as feasibility-negative analyses. | Advisor-approved main horizon choice or documented demotion to feasibility-negative analysis; regenerated horizon triage for chosen horizons. | pending_human_decision |
| GB-006 | Gate B | P1 | SeizeIT2 track completeness | Complete required split/task/modality readiness rows before benchmark claims. | Ready track matrix covering required splits, tasks, and modality tracks; count summary matching documented expected counts. | pending_human_decision |
| GB-007 | Gate B | P2 | MSG horizon source review | Keep source-review-required horizons out of citable tables until event gaps close. | Source-review decision for each source-review-required horizon and evidence that chosen main horizons no longer depend on unresolved event gaps. | pending_human_decision |
| GB-008 | Gate B | P2 | SeizeIT2 negative readiness rows | Preserve non-ready track rows as explicit negative readiness findings. | Paper-table or appendix plan preserving non-ready tracks as explicit negative readiness findings. | pending_human_decision |

## Human Review Instructions

Fill these columns for every row:

`human_decision, reviewer_name, review_date, evidence_uri, evidence_hash, resolution_notes, rerun_required, rerun_artifact_uri`

Allowed `human_decision` values:

`APPROVED_EXCLUSION, BLOCKED, DEFERRED, NEEDS_SOURCE_REVIEW, RESOLVED`

Rows with `BLOCKED` or `NEEDS_SOURCE_REVIEW` keep Gate B blocked. Rows marked
`RESOLVED`, `APPROVED_EXCLUSION`, or `DEFERRED` must also include reviewer,
date, and evidence URI before the ledger can advance to Gate B validation rerun.

## Guardrails

- This ledger is an audit instrument, not clinical evidence.
- Blank human decision columns mean Gate B remains blocked.
- Gate C remains blocked until this ledger is closed and guardrails are rerun.
- Claim status: `gate_b_closeout_ledger_pending_human_review_not_citable`

## Manifest

- Run ID: `gate_b_closeout_2026-05-22`
- Source URI: `reports/gate_b_closeout_2026-05-22/gate_b_closeout_decisions_partial_2026-05-22.csv`
- Ledger hash: `d7aaa3ae1924634c12d504232ae78a3e44bc9eb49f74d57fd6ad648e952fea9b`
