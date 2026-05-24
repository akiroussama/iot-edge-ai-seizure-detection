# EpiBench Overclaim Audit

Generated from public-facing Markdown, YAML, JSON, and text artefacts.

## Purpose

This audit identifies wording that can be misread as clinical, regulatory, deployment, real-time,
generalization, or SOTA overclaim. It is a review aid, not a scientific certification result.

## Summary

- Findings: `367`.
- Bounded/anti-overclaim context: `291`.
- Requires wording review: `76`.

## Category Counts

- `clinical_or_regulatory`: `101`
- `edge_or_realtime`: `101`
- `scope_or_generality`: `22`
- `sota_or_leaderboard`: `143`

## Severity Counts

- `bounded`: `291`
- `major`: `25`
- `moderate`: `51`

## Files With Most Review Findings

- `docs/research/2026-05-20_q1_publishable_task_roadmap.md`: `9`
- `docs/research/2026-05-20_step1_sota_leaderboard_plan.md`: `8`
- `docs/research/2026-05-20_step1_execution_log.md`: `7`
- `docs/research/2026-05-22_general_status_and_roadmap.md`: `6`
- `docs/EPIBENCH_PHASE1_DETAILED_PLAN.md`: `5`
- `docs/EPIBENCH_PHASE7_GOVERNANCE_ADOPTION.md`: `5`
- `docs/EPIBENCH_PROTOCOL.md`: `4`
- `docs/EPIBENCH_SPEC_V1.md`: `4`
- `docs/EPIBENCH_PHASE1_REVIEW_CHECKLIST.md`: `3`
- `docs/EPIBENCH_Q1_STANDARD_ROADMAP.md`: `3`

## Findings Requiring Review

- `docs/EPIBENCH_PHASE1_ADJUDICATION_EXAMPLES.md:358` real-time (major) -> Review wording; add evidence boundary or remove unsupported claim.
- `docs/EPIBENCH_PHASE1_ADJUDICATION_EXAMPLES.md:370` real-time (major) -> Review wording; add evidence boundary or remove unsupported claim.
- `docs/EPIBENCH_PHASE1_DETAILED_PLAN.md:151` sota (moderate) -> Review wording; add evidence boundary or remove unsupported claim.
- `docs/EPIBENCH_PHASE1_DETAILED_PLAN.md:478` real-time (major) -> Review wording; add evidence boundary or remove unsupported claim.
- `docs/EPIBENCH_PHASE1_DETAILED_PLAN.md:553` generalize (major) -> Review wording; add evidence boundary or remove unsupported claim.
- `docs/EPIBENCH_PHASE1_DETAILED_PLAN.md:864` real-time (major) -> Review wording; add evidence boundary or remove unsupported claim.
- `docs/EPIBENCH_PHASE1_DETAILED_PLAN.md:908` real-time (major) -> Review wording; add evidence boundary or remove unsupported claim.
- `docs/EPIBENCH_PHASE1_REVIEW_CHECKLIST.md:144` real-time (major) -> Review wording; add evidence boundary or remove unsupported claim.
- `docs/EPIBENCH_PHASE1_REVIEW_CHECKLIST.md:156` real-time (major) -> Review wording; add evidence boundary or remove unsupported claim.
- `docs/EPIBENCH_PHASE1_REVIEW_CHECKLIST.md:194` real-time (major) -> Review wording; add evidence boundary or remove unsupported claim.
- `docs/EPIBENCH_PHASE2_SINGLE_SOURCE_OF_TRUTH.md:87` sota (moderate) -> Review wording; add evidence boundary or remove unsupported claim.
- `docs/EPIBENCH_PHASE2_SINGLE_SOURCE_OF_TRUTH.md:121` sota (moderate) -> Review wording; add evidence boundary or remove unsupported claim.
- `docs/EPIBENCH_PHASE4_REFERENCE_IMPLEMENTATION.md:29` sota (moderate) -> Review wording; add evidence boundary or remove unsupported claim.
- `docs/EPIBENCH_PHASE6_Q1_PAPER_STRATEGY.md:192` sota (moderate) -> Review wording; add evidence boundary or remove unsupported claim.
- `docs/EPIBENCH_PHASE7_GOVERNANCE_ADOPTION.md:31` sota (moderate) -> Review wording; add evidence boundary or remove unsupported claim.
- `docs/EPIBENCH_PHASE7_GOVERNANCE_ADOPTION.md:59` sota (moderate) -> Review wording; add evidence boundary or remove unsupported claim.
- `docs/EPIBENCH_PHASE7_GOVERNANCE_ADOPTION.md:116` sota (moderate) -> Review wording; add evidence boundary or remove unsupported claim.
- `docs/EPIBENCH_PHASE7_GOVERNANCE_ADOPTION.md:149` sota (moderate) -> Review wording; add evidence boundary or remove unsupported claim.
- `docs/EPIBENCH_PHASE7_GOVERNANCE_ADOPTION.md:158` sota (moderate) -> Review wording; add evidence boundary or remove unsupported claim.
- `docs/EPIBENCH_PROTOCOL.md:293` real-time (major) -> Review wording; add evidence boundary or remove unsupported claim.

## Boundary

`bounded` means the phrase appears in an explicit limitation, forbidden-phrase list, or
anti-overclaim statement. It should still be checked before submission, but it is not automatically
unsafe.

Before Q1 submission, every `requires_review` line should be either rewritten, bounded by explicit
evidence conditions, or recorded as an intentional editorial waiver in the manuscript review log.
