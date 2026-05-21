# M3 Counterfactual Probing

Date: 2026-05-22

Branch: `codex/counterfactual-probing`

Base: `origin/main@de42b22`

## Objective

Add local counterfactual probing for standardized prediction rows with feature
columns. For each row, the report estimates which minimal feature changes would
move a linear risk surrogate across the alarm threshold.

This is interpretability infrastructure only. It explains a fitted surrogate of
the model risk score, not a causal physiological mechanism.

## Implementation

- Added `src/interpretability/counterfactual.py`.
- Exported helpers from `src/interpretability/__init__.py`.
- Added CLI `scripts/run_counterfactual_probing.py`.
- Added config contract `configs/report/counterfactual_probing.yaml`.
- Added synthetic tests in `tests/test_counterfactual_probing.py`.

The CLI writes:

- `counterfactual_rows.csv`
- `counterfactual_feature_changes.csv`
- `counterfactual_summary.csv`
- `counterfactual_manifest.csv`
- `counterfactual_report.json`
- `counterfactual_report.md`

## Method

The report fits a ridge-regularized linear surrogate from leakage-screened
features to the model's `risk_score` on the configured fit split. Local
counterfactuals are computed in standardized feature space by moving along the
surrogate gradient until the target risk threshold is crossed.

Default direction is `prevent_alarm`: estimate the feature change that would
reduce surrogate risk below the alarm threshold. The CLI also supports
`trigger_alarm`.

## Scientific Guardrails

- Feature selection excludes IDs, labels, split metadata, prediction outputs,
  and explicit seizure-timing leakage columns.
- The surrogate fits model risk scores, not `forecast_label`.
- Label-flip regression tests verify that counterfactual rows, feature changes,
  and training artifact hash do not change when labels change.
- Output narratives are marked as surrogate post-hoc explanations, not causal
  claims.
- Reports remain pre-Gate-C and not citable as benchmark results.

## Validation

Executed targeted validation:

```bash
uv run --extra dev ruff check src/interpretability/counterfactual.py src/interpretability/__init__.py scripts/run_counterfactual_probing.py tests/test_counterfactual_probing.py
uv run --extra dev pytest tests/test_counterfactual_probing.py
uv run --extra dev pytest tests/test_counterfactual_probing.py tests/test_sparse_autoencoder_interpretability.py tests/test_failure_taxonomy.py tests/test_supervised_ladder.py
```

Executed full validation:

```bash
uv run --extra dev ruff check .
uv run --extra dev --extra torch pytest
```

Result:

- Targeted Ruff: passed.
- Targeted pytest: 5 passed.
- Neighbor pytest: 23 passed.
- Full Ruff: passed.
- Full pytest: 259 passed.

## Remaining Limits

- Counterfactuals are only as faithful as the local linear surrogate.
- Feature changes may be physiologically impossible unless constrained by a
  domain-specific feasibility model.
- The method does not prove causality.
- Citable interpretation requires Gate C frozen inputs, robust model outputs,
  and clinician review of any proposed narrative.
