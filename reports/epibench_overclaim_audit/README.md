# EpiBench Overclaim Audit

Generated from public-facing Markdown, YAML, JSON, and text artefacts.

## Purpose

This audit identifies wording that can be misread as clinical, regulatory, deployment, real-time,
generalization, or SOTA overclaim. It is a review aid, not a scientific certification result.

## Summary

- Findings: `355`.
- Bounded/anti-overclaim context: `187`.
- Requires wording review: `168`.

## Category Counts

- `clinical_or_regulatory`: `97`
- `edge_or_realtime`: `93`
- `scope_or_generality`: `22`
- `sota_or_leaderboard`: `143`

## Severity Counts

- `bounded`: `187`
- `critical`: `77`
- `major`: `38`
- `moderate`: `53`

## Files With Most Review Findings

- `docs/EPIBENCH_PHASE1_DETAILED_PLAN.md`: `13`
- `docs/research/2026-05-20_q1_publishable_task_roadmap.md`: `9`
- `docs/research/2026-05-20_step1_execution_log.md`: `8`
- `docs/research/2026-05-20_step1_sota_leaderboard_plan.md`: `8`
- `docs/EPIBENCH_PROTOCOL.md`: `7`
- `docs/EPIBENCH_SPEC_V1.md`: `7`
- `docs/research/2026-05-22_general_status_and_roadmap.md`: `6`
- `docs/EPIBENCH_PHASE7_GOVERNANCE_ADOPTION.md`: `5`
- `reports/epibench_chbmit_e2pi_package_report.md`: `5`
- `docs/EPIBENCH_PHASE1_REVIEW_CHECKLIST.md`: `4`

## Findings Requiring Review

- `docs/EPIBENCH_PHASE1_ADJUDICATION_EXAMPLES.md:358` real-time (major) -> Review wording; add evidence boundary or remove unsupported claim.
- `docs/EPIBENCH_PHASE1_ADJUDICATION_EXAMPLES.md:370` real-time (major) -> Review wording; add evidence boundary or remove unsupported claim.
- `docs/EPIBENCH_PHASE1_DETAILED_PLAN.md:151` sota (moderate) -> Review wording; add evidence boundary or remove unsupported claim.
- `docs/EPIBENCH_PHASE1_DETAILED_PLAN.md:196` clinical certification (critical) -> Review wording; add evidence boundary or remove unsupported claim.
- `docs/EPIBENCH_PHASE1_DETAILED_PLAN.md:197` clinically approved (critical) -> Review wording; add evidence boundary or remove unsupported claim.
- `docs/EPIBENCH_PHASE1_DETAILED_PLAN.md:217` clinically certified (critical) -> Review wording; add evidence boundary or remove unsupported claim.
- `docs/EPIBENCH_PHASE1_DETAILED_PLAN.md:478` real-time (major) -> Review wording; add evidence boundary or remove unsupported claim.
- `docs/EPIBENCH_PHASE1_DETAILED_PLAN.md:553` generalize (major) -> Review wording; add evidence boundary or remove unsupported claim.
- `docs/EPIBENCH_PHASE1_DETAILED_PLAN.md:695` real-time (major) -> Review wording; add evidence boundary or remove unsupported claim.
- `docs/EPIBENCH_PHASE1_DETAILED_PLAN.md:845` generalize (major) -> Review wording; add evidence boundary or remove unsupported claim.
- `docs/EPIBENCH_PHASE1_DETAILED_PLAN.md:864` real-time (major) -> Review wording; add evidence boundary or remove unsupported claim.
- `docs/EPIBENCH_PHASE1_DETAILED_PLAN.md:869` real-time (major) -> Review wording; add evidence boundary or remove unsupported claim.
- `docs/EPIBENCH_PHASE1_DETAILED_PLAN.md:904` clinically certified (critical) -> Review wording; add evidence boundary or remove unsupported claim.
- `docs/EPIBENCH_PHASE1_DETAILED_PLAN.md:907` generalizable (major) -> Review wording; add evidence boundary or remove unsupported claim.
- `docs/EPIBENCH_PHASE1_DETAILED_PLAN.md:908` real-time (major) -> Review wording; add evidence boundary or remove unsupported claim.
- `docs/EPIBENCH_PHASE1_REVIEW_CHECKLIST.md:110` real-time (major) -> Review wording; add evidence boundary or remove unsupported claim.
- `docs/EPIBENCH_PHASE1_REVIEW_CHECKLIST.md:144` real-time (major) -> Review wording; add evidence boundary or remove unsupported claim.
- `docs/EPIBENCH_PHASE1_REVIEW_CHECKLIST.md:156` real-time (major) -> Review wording; add evidence boundary or remove unsupported claim.
- `docs/EPIBENCH_PHASE1_REVIEW_CHECKLIST.md:194` real-time (major) -> Review wording; add evidence boundary or remove unsupported claim.
- `docs/EPIBENCH_PHASE2_SINGLE_SOURCE_OF_TRUTH.md:87` sota (moderate) -> Review wording; add evidence boundary or remove unsupported claim.

## Boundary

`bounded` means the phrase appears in an explicit limitation, forbidden-phrase list, or
anti-overclaim statement. It should still be checked before submission, but it is not automatically
unsafe.

Before Q1 submission, every `requires_review` line should be either rewritten, bounded by explicit
evidence conditions, or recorded as an intentional editorial waiver in the manuscript review log.
