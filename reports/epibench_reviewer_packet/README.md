# EpiBench Reviewer Evidence Packet

Generated from EpiBench evidence panels, coverage audit, overclaim audit, submission-readiness gate,
and inter-reviewer report.

## Purpose

This packet is a pre-submission defense matrix. It does not claim that the paper will be accepted.
It identifies the reviewer attacks that remain scientifically plausible and links each attack to a
specific artefact, quantitative indicator, and required action.

## Summary

- Reviewer attacks tracked: `12`.
- Defense status: `partial=4, strong=8`.
- Severity distribution: `critical=5, high=7`.
- Result bundles represented in evidence panels: `16`.
- Protocol tracks represented: `D, E, F, W`.
- Submission-readiness gate: `passed`.
- Q1 hardening register: `controlled_with_external_dependencies` with
  `0` uncontrolled angle(s).
- Open or partial action count: `4`.

## Files Generated

- `reviewer_attack_matrix.csv`: one row per major reviewer objection.
- `pre_submission_action_register.csv`: only unresolved or partially resolved reviewer risks.
- `evidence_index.csv`: map from evidence families to concrete report files.

## Highest-Priority Remaining Actions

- `A05` partial: Run the external clinical/methods review packet and commit adjudicated rubric changes.
- `A06` partial: Scale CHB-MIT waveform evidence beyond the micro-subset and add stronger patient-independent baselines.
- `A10` partial: Measure the final model on a declared target IoT device before any edge-ready or real-time claim.
- `A12` partial: Mint Zenodo DOI and obtain one independent external clean-checkout reproduction run.

## Boundary

This packet is an internal scientific risk-control artefact. It is not clinical validation, regulatory
clearance, or a guarantee of Q1 acceptance. It is meant to make the remaining rejection risks explicit
before manuscript freeze.
