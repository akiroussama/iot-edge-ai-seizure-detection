# T17 Statistical Robustness Layer

Date: 2026-05-21

Branch: `codex/statistical-robustness`

Base: `origin/main@cbbbd12`

## Objective

Add the statistical inference layer required before any forecast leaderboard can
be treated as scientifically defensible. Point estimates alone are not enough
for a Q1-grade benchmark: patient dependence, event dependence, small-N cohorts,
and horizon/modality multiplicity must be visible in every table.

This task does not train a model and does not create citable real-data
benchmark claims. It creates the machinery that future Gate-C-frozen runs must
use.

## Implementation

- Added `src/reports/statistical_robustness.py`.
- Exported robustness helpers from `src/reports/__init__.py`.
- Added CLI `scripts/make_statistical_robustness_report.py`.
- Added synthetic known-effect tests in `tests/test_statistical_robustness.py`.

## Scientific Guardrails

- Prediction/reference rows are aligned through the existing fail-closed
  calibration alignment keys.
- Patient-level and event-level bootstrap CIs are both explicit.
- Paired permutation tests use clustered sign flips by patient when a patient
  column is available.
- Multiple-comparison correction supports Benjamini-Hochberg FDR and Bonferroni.
- Tiny group counts, wide confidence intervals, and skill CIs crossing zero are
  emitted as machine-readable warning rows.
- Citable output requires `gate_c_status=passed`.

## Output Tables

The CLI writes:

- `robustness_intervals.csv`
- `robustness_permutation.csv`
- `robustness_multiplicity.csv`
- `robustness_warnings.csv`
- `robustness_report.json`
- `robustness_report.md`

The JSON and Markdown include `result_status`, `citation_status`, and
`gate_c_status`, so pre-Gate-C exploratory runs cannot be silently promoted into
paper claims.

## Validation

Executed targeted validation:

```bash
uv run --extra dev ruff check src/reports/statistical_robustness.py src/reports/__init__.py scripts/make_statistical_robustness_report.py tests/test_statistical_robustness.py
uv run --extra dev pytest tests/test_statistical_robustness.py tests/test_calibration_skill_report.py
```

Executed full validation:

```bash
uv run --extra dev ruff check .
uv run --extra dev --extra torch pytest
```

Result:

- Targeted Ruff: passed.
- Targeted pytest: 12 passed.
- Full Ruff: passed.
- Full pytest: 204 passed.

## Remaining Limits

- The permutation layer is a paired Brier-loss sign-flip test; it is not a full
  hierarchical Bayesian uncertainty model.
- Real paper tables still require frozen splits, Gate C, and the clinical audit
  record.
- Horizon/modality families must be passed in as multiple reference rows or
  concatenated report rows by the downstream benchmark runner.
