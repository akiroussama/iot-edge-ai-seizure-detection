# EpiBench Evidence Panels

Generated from machine-certified EpiBench result bundles.

## Purpose

These panels are manuscript artefacts, not new certification rules. They summarize why a leaderboard
line must be interpreted through dataset evidence, split policy, label audit, failure transparency,
and claim eligibility.

## Generated Files

- `bundle_summary.csv`: one row per result bundle.
- `naive_score_leaderboard.csv`: ranking by Epi-Score only.
- `claim_gated_leaderboard.csv`: ranking by final claim, then Epi-Score.
- `rank_comparison.csv`: explicit naive versus claim-gated rank movement.
- `claim_gate_waterfall.csv`: all claim ceilings per run.
- `failure_matrix.csv`: sentinel visibility matrix.
- `score_axis_matrix.csv`: per-axis Epi-Score inputs.

## Audit Highlights

- Bundle count: `14`.
- Highest naive Epi-Score: `leakage_high_metric_demo` with score `94.727` and final claim `E1`.
- Highest claim-gated result: `prospective_e4_claim_demo` with final claim `E4` and score `72.424`.
- Claim distribution: `E1=5, E2-PD=2, E2-PI=4, E3=2, E4=1`.
- Dataset tier distribution: `T1=11, T2=1, T3=2`.
- Rank interpretation distribution: `claim_gate_promotes_more_defensible_evidence=5, claim_structure_valid_but_performance_poor=1, high_or_mid_score_claim_limited_by_evidence_gate=5, rank_stable_under_claim_gate=3`.

## Scientific Boundary

These panels do not imply clinical approval, device readiness, or deployment fitness. They are
retrospective evidence summaries under EpiBench v1.0-draft.
