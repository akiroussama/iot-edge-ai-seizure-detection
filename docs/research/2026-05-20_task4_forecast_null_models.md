# Task 4 - Constrained Forecast Null Models

Date: 2026-05-20
Branch: `codex/forecast-null-models`
Base: `origin/main@22f7908`
Work order: `docs/CLAUDE_TO_CODEX_WORK_ORDER_TASK4_2026-05-20.md`
Status: engineering-only, pre-Gate-C-safe.

## Plan

Task 4 implements four constrained null models for seizure forecasting
predictions:

- `split_prevalence_prior`: constant train-split prevalence risk, the
  canonical Brier Skill Score climatology reference.
- `rate_matched_random`: seed-reproducible random alarms matched to a target
  time-in-warning budget on the threshold split.
- `patient_prior`: per-patient train-split prevalence, with explicit
  population fallback when a patient is absent from train or has fewer than
  `--patient-min-events` positive train events.
- `cycle_preserving_random`: hour-of-day train-split prevalence, with
  zero-positive bins contributing zero risk and no zero-score alarms.

The implementation adds pure functions in `src/baselines/forecast_nulls.py`, a
small CLI wrapper in `scripts/run_null_baseline.py`, package exports, and
synthetic tests. No real-data run is part of this PR.

## Plan Validation

The work order is the authoritative revision of the original chat plan. It
adds six integrity refinements before implementation:

- `split_prevalence_prior` is mandatory, not optional.
- `patient_prior` fallbacks are marked in `null_model_variant`.
- fallback sensitivity is parameterized by `--patient-min-events`.
- output rows preserve all input columns and append the prediction contract.
- behavior-sanity tests cover fallback counts, Brier climatology, and
  Brier Skill Score against self.
- per-model seed derivation prevents RNG coupling when multiple null models
  are invoked with the same user seed.

This is pre-Gate-C safe because it creates tooling and synthetic tests only.
It does not run a model on real clinical data and does not report benchmark
numbers.

## Attack

Implementation choices:

- common input validation rejects missing required columns, missing split
  columns, output-column collisions, invalid `target_tiw`, and empty fit or
  threshold splits after `is_excluded` filtering;
- forbidden timing and censoring columns are ignored by construction;
- all model outputs preserve the input table unchanged, then append
  `risk_score`, `alarm`, `null_model`, `null_model_variant`,
  `score_fit_split`, `threshold_source_split`, `target_tiw`, and `seed`;
- thresholding uses the threshold split only to select the target alarm
  budget, then applies the derived threshold deterministically to valid rows;
- each model derives a stable model-specific RNG seed from the user seed and
  the model name.

The CLI reads CSV, TSV, or Parquet through the existing table helpers, writes
the same formats, and prints JSON metadata including `null_model_variant`
counts.

## Result

Implemented files:

- `src/baselines/forecast_nulls.py`
- `scripts/run_null_baseline.py`
- `src/baselines/__init__.py`
- `tests/test_forecast_nulls.py`

The tests cover the required work-order cases:

- target time-in-warning behavior for `rate_matched_random`;
- fit-only behavior for `patient_prior` and `cycle_preserving_random`;
- explicit errors for missing or empty fit/threshold data;
- test-split mutation guards;
- strict seed reproducibility;
- forbidden-column invariance;
- `patient_prior_fallback_population` markers and countability;
- Brier climatology and BSS-vs-self sanity checks;
- CLI smoke coverage.

## Audit

Integrity checks:

- no real-data run;
- no external citation;
- no swallowed exception pattern or `_metric_or_none` reuse;
- no silent `patient_prior` fallback;
- no use of forbidden leakage-prone columns;
- synthetic behavior tests verify null-model semantics, not only shape.

Remaining scope boundaries:

- `cycle_preserving_random` is hour-of-day only; multiday cycles are deferred.
- The leaderboard runner consumes these predictions via
  `--reference-predictions` in a later PR.
- Any future real-data number remains pre-Gate-C exploratory and not citable
  until frozen splits and artifact DOI are complete.

## Commands

```bash
git diff --check
uv run --extra dev pytest tests/test_forecast_nulls.py
uv run --extra dev ruff check src/baselines/forecast_nulls.py \
  scripts/run_null_baseline.py tests/test_forecast_nulls.py
```

Validation result:

- `git diff --check`: pass
- `uv run --extra dev pytest tests/test_forecast_nulls.py`: pass, 18 tests
- `uv run --extra dev ruff check src/baselines/forecast_nulls.py scripts/run_null_baseline.py tests/test_forecast_nulls.py`: pass
- `uv run --extra dev --extra torch pytest`: pass, 154 tests

## Conclusion

Task 4 turns the forecasting leaderboard contract into reusable constrained
null predictions. The branch is reviewable as engineering-only groundwork:
synthetic tests demonstrate leakage controls, fallback transparency, BSS
climatology behavior, and deterministic reproducibility without making any
clinical or benchmark claim.
