# EpiBench Q1 Rejection Hardening Register

Status: `controlled_with_external_dependencies`

## Purpose

This register answers the ten most plausible attacks from a severe Q1 reviewer. It is intentionally
stricter than the manuscript narrative. An angle is not considered controlled by optimism; it must be
closed by executable evidence, neutralized by explicit manuscript scope, or listed as an external
dependency before submission.

## Summary

- Angles tracked: `10`.
- Closed by evidence: `3`.
- Neutralized by scope: `3`.
- External dependencies: `4`.
- Uncontrolled: `0`.

## Angle Status

- `Q1-01` external_dependency: Too much protocol, not enough real proof.
- `Q1-02` external_dependency: No third-party adoption or independent reproduction.
- `Q1-03` external_dependency: No independent clinical review.
- `Q1-04` closed_by_evidence: EpiBench reinvents SzCORE.
- `Q1-05` neutralized_by_scope: Universal certification is overclaimed.
- `Q1-06` external_dependency: MTS/DSI remain subjective.
- `Q1-07` closed_by_evidence: Epi-Score weights are arbitrary.
- `Q1-08` neutralized_by_scope: No real target hardware evidence for edge or real-time claims.
- `Q1-09` neutralized_by_scope: No prospective clinical evidence.
- `Q1-10` closed_by_evidence: Detection, warning, forecasting, and embedded viability are too broad.

## External Actions Still Required

- `Q1-01` P0: Full-scale signal-derived EEG package, preferably CHB-MIT/TUSZ, with patient-independent event scoring and per-patient distributions.
- `Q1-02` P0: At least one independent clean-checkout reproduction report from a lab not involved in EpiBench development.
- `Q1-03` P0: Two independent reviewers, including clinical epilepsy/neurophysiology expertise, with adjudicated item-level MTS/DSI register.
- `Q1-06` P0: Independent inter-reviewer agreement with no unresolved score difference greater than one point.

## Boundary

A controlled register does not mean the paper is guaranteed acceptable. It means every major rejection angle is either answered by evidence, neutralized by bounded scope, or made explicit as an external pre-submission dependency.
