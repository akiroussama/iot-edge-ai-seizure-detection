# EpiBench Epi-Score Weight Sensitivity Panel

Generated from `reports/epibench_evidence_panels/score_axis_matrix.csv`.

## Purpose

This panel tests whether the paper's interpretation depends on a single convenient Epi-Score weight
choice. It perturbs the preregistered axis weights and compares score-only ranks with claim-gated
ranks. The claim itself is intentionally invariant because claim eligibility is controlled by dataset
evidence, split policy, label audit, failures, and hardware evidence rather than by score weights.

## Summary

- Bundles evaluated: `16`.
- Weight scenarios: `11`.
- Maximum score-only rank range across scenarios: `5`.
- Maximum claim-gated rank range across scenarios: `0`.
- Scenarios with at least one `E1` run in the score-only top 3: `11`.
- Top claim-gated final claims observed across scenarios: `E4`.

## Generated Files

- `weight_sensitivity_scores.csv`: score and ranks for every bundle under every weight scenario.
- `weight_sensitivity_rank_stability.csv`: per-bundle score range and rank range across scenarios.
- `weight_sensitivity_summary.csv`: top score-only and top claim-gated run per scenario.

## Interpretation

If score-only ranks move under perturbation, that is expected and should be reported. The scientific
test is whether high-score but invalid runs can acquire stronger claims through reweighting. Under
EpiBench they cannot, because claim gates are not score-weight parameters.

## Boundary

This is a sensitivity analysis of a retrospective methodological score. It does not validate clinical
utility, regulatory safety, or deployment readiness.
