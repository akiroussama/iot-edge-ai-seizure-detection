# T12 Observability And Missingness

Date: 2026-05-21

Branch: `codex/observability-missingness`

Base: `origin/main@3d5d154`

## Objective

Make "not observable" a first-class benchmark output. A wearable seizure-risk
system should not be forced to emit an apparently precise risk estimate when HR,
ACC, or other wearable streams are absent, implausible, or too sparse.

This task does not train a model and does not create citable real-data claims.
It adds the signal-quality layer that later citable rows must carry.

## Implementation

- Added `src/features/observability.py`.
- Added CLI `scripts/compute_observability_report.py`.
- Fixed and extended `src/features/__init__.py` exports.
- Extended the leaderboard schema/template with:
  - `observable_prediction_rows`
  - `deficient_prediction_rows`
  - `abstained_prediction_rows`
  - `deficiency_time_minutes`
  - `mean_observable_score`
- Updated `scripts/make_leaderboard_row.py` to populate those fields when
  prediction rows carry observability outputs.
- Added synthetic behavior tests in `tests/test_observability.py`.

## Scientific Guardrails

- Observability features use sensor coverage, dropout, and physiological
  plausibility fields only; they do not use `forecast_label`.
- The anti-leakage test flips labels and verifies identical observability
  outputs.
- Abstention can be threshold-based or bounded by a fixed abstention fraction.
- Reports remain not citable unless Gate C is passed.

## Output Tables

The CLI writes:

- `observability_enriched.csv`
- `observability_summary.csv`
- `observability_metric_strata.csv`
- `observability_report.json`
- `observability_report.md`

## Validation

Executed targeted validation:

```bash
uv run --extra dev ruff check src/features/observability.py src/features/__init__.py scripts/compute_observability_report.py scripts/make_leaderboard_row.py schemas/leaderboard_entry.schema.json tests/test_observability.py tests/test_leaderboard_schema.py tests/test_leaderboard_runner.py
uv run --extra dev pytest tests/test_observability.py tests/test_leaderboard_schema.py tests/test_leaderboard_runner.py tests/test_features.py
```

Executed full validation:

```bash
uv run --extra dev ruff check .
uv run --extra dev --extra torch pytest
```

Result:

- Targeted Ruff: passed.
- Targeted pytest: 23 passed.
- Full Ruff: passed.
- Full pytest: 215 passed.

## Remaining Limits

- Real sensor-quality thresholds should be tuned per dataset and documented in
  the Gate C registry.
- Current plausibility rules are conservative deterministic checks, not a
  learned artifact classifier.
- The abstention policy marks windows; downstream model reports still need to
  decide whether to score with or without abstained windows.
