# T9 Multiday Cycle Features

Date: 2026-05-21

Branch: `codex/multiday-cycle-features`

Base: `origin/main@679b4a0`

## Objective

Strengthen the benchmark beyond hour-of-day priors by adding deterministic
circadian, weekly, and multiday cycle features plus a split-safe multicycle
prior baseline.

This directly addresses the current gap documented in Task 4: the existing
cycle-preserving null is hour-of-day only.

## Implementation

- Added `src/features/cycle_features.py`.
- Extended `src/baselines/cycle_baseline.py` with:
  - `MultiCyclePriorModel`;
  - `fit_multiday_cycle_prior`;
  - `predict_multiday_cycle_prior`;
  - `rolling_origin_multiday_cycle_predictions`;
  - `permute_cycle_labels_within_patient`.
- Extended `scripts/run_cycle_baseline.py` with:
  - `--cycle-family hour_of_day|multiday`;
  - `--cycle-period-hours`;
  - `--phase-bins`;
  - `--rolling-origin`;
  - `--min-history-rows`.
- Added tests in `tests/test_cycle_features.py`.

Default CLI behavior remains the previous hour-of-day baseline, preserving
backward compatibility.

## Leakage Controls

- Cycle phase features depend only on timestamps and fixed periods.
- The multiday baseline fits only on caller-provided fit rows.
- Rolling-origin predictions use strictly earlier `window_end` rows only.
- A future-label mutation test verifies that earlier rolling-origin predictions
  are unchanged.
- The negative control permutes labels within patient, preserving prevalence
  while destroying phase alignment.

## Important Bug Fixed During Implementation

The first implementation converted timestamps with `astype("int64") / 1e9`.
That is unsafe because pandas may store datetimes at microsecond resolution
instead of nanosecond resolution. The final implementation uses:

```python
(timestamp - pd.Timestamp("1970-01-01")).dt.total_seconds()
```

This avoids silently wrong cycle bins.

## Validation

Executed targeted validation:

```bash
uv run --extra dev ruff check src/features/cycle_features.py src/features/__init__.py src/baselines/cycle_baseline.py src/baselines/__init__.py scripts/run_cycle_baseline.py tests/test_cycle_features.py tests/test_cycle_baseline.py
uv run --extra dev pytest tests/test_cycle_features.py tests/test_cycle_baseline.py tests/test_forecast_nulls.py
uv run --extra dev ruff check .
uv run --extra dev --extra torch pytest
```

Result:

- Targeted Ruff: passed.
- Targeted pytest: 26 passed.
- Full Ruff: passed.
- Full pytest: 192 passed.

## Remaining Limits

- Multiday cycles require enough longitudinal coverage; short recordings should
  be interpreted as underpowered.
- The baseline is empirical and interpretable, not a replacement for a
  supervised model ladder.
- Randomized-time negative controls should be reported alongside any apparent
  cycle skill.
- Real-data claims remain non-citable until Gate C and human audit are complete.
