# T13 Patient-Adaptive Hierarchical Baselines

Date: 2026-05-21

Branch: `codex/patient-adaptive-baselines`

Base: `origin/main@0290f53`

## Objective

Add strong non-neural patient-adaptive baselines before building larger
supervised models. A neural seizure-risk model should be compared against
population, patient-specific, and empirical-Bayes shrinkage priors under
explicit cold-start, warm-start, and rolling-origin evaluation modes.

This task does not report real-data benchmark results. It creates leakage-safe
baseline generators that later frozen runs can score through the existing
leaderboard/calibration stack.

## Implementation

- Added `src/baselines/patient_adaptive.py`.
- Added CLI `scripts/run_patient_adaptive_baseline.py`.
- Exported helpers from `src/baselines/__init__.py`.
- Added synthetic behavior tests in `tests/test_patient_adaptive_baselines.py`.

## Scientific Guardrails

- `cold_start` ignores patient history and emits an explicit population variant.
- `warm_start` uses only the configured fit split for patient statistics.
- `rolling_origin` uses strictly earlier windows for the same patient.
- Patients below `min_patient_observations` fall back with explicit
  `*_fallback_population` markers.
- Empirical-Bayes shrinkage exposes the prior strength used to pull sparse
  patients toward the population rate.

## Validation

Executed targeted validation:

```bash
uv run --extra dev ruff check src/baselines/patient_adaptive.py src/baselines/__init__.py scripts/run_patient_adaptive_baseline.py tests/test_patient_adaptive_baselines.py
uv run --extra dev pytest tests/test_patient_adaptive_baselines.py tests/test_forecast_nulls.py tests/test_calibration_skill_report.py
```

Executed full validation:

```bash
uv run --extra dev ruff check .
uv run --extra dev --extra torch pytest
```

Result:

- Targeted Ruff: passed.
- Targeted pytest: 31 passed.
- Full Ruff: passed.
- Full pytest: 221 passed.

## Remaining Limits

- These are probability priors, not physiological models.
- Rolling-origin adaptation assumes prior outcomes become known before later
  windows are scored; papers must label that evaluation mode explicitly.
- Real citable comparisons still require Gate C frozen artifacts.
