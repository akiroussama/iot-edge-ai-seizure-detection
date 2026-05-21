# P2 Conformal Risk Intervals

Date: 2026-05-21

Branch: `codex/personal-conformal-risk`

Base: `origin/main@dcc5a0e`

## Objective

Add a formal uncertainty layer on top of existing `risk_score` prediction
tables. The goal is to report calibrated risk intervals such as `[lower,
upper]` per forecast window, with empirical coverage summaries, while keeping
all pre-Gate-C outputs explicitly non-citable as benchmark claims.

This extends the Task 5 calibration/BSS layer. Brier and ECE summarize average
calibration quality; split conformal intervals give a per-window uncertainty
range with an explicit nominal coverage target.

## Implementation

- Added `src/calibration/conformal.py`.
- Exported conformal utilities from `src/calibration/__init__.py`.
- Added CLI `scripts/run_conformal_calibration.py`.
- Added synthetic tests in `tests/test_conformal_prediction.py`.

The implemented nonconformity score is `abs(forecast_label - risk_score)` on
valid non-excluded calibration rows. The split-conformal radius uses the
finite-sample rank `ceil((n + 1) * (1 - alpha))`; when the rank exceeds the
available calibration size, the interval radius falls back to `1.0`, giving a
trivial but honest `[0, 1]` interval.

## Personal Calibration

Two methods are available:

- `global`: one radius for all evaluation rows.
- `patient`: patient-specific radius when that patient has at least
  `min_patient_calibration` valid calibration rows; otherwise an explicit
  `global_fallback` marker is emitted.

The fallback is intentionally visible through `conformal_variant` and
`conformal_calibration_n`. There is no silent claim that every patient has a
personalized conformal model.

## CLI Outputs

`scripts/run_conformal_calibration.py` consumes one prediction table and two
scope filters, for example `split=val` and `split=test`.

It writes:

- `conformal_intervals.csv`
- `conformal_summary.csv`
- `conformal_patient_summary.csv`
- `conformal_report.json`
- `conformal_report.md`

Default report status is `pre_gate_c_exploratory_not_citable`. Citable status
requires `gate_c_status=passed`, matching the Gate C guardrail pattern added in
Task 6.

## Validation

Executed targeted validation:

```bash
uv run --extra dev ruff check src/calibration/conformal.py src/calibration/__init__.py scripts/run_conformal_calibration.py tests/test_conformal_prediction.py
uv run --extra dev pytest tests/test_conformal_prediction.py tests/test_calibration_thresholding.py tests/test_calibration_skill_report.py
uv run --extra dev ruff check .
uv run --extra dev --extra torch pytest
```

Result:

- Targeted Ruff: passed.
- Targeted pytest: 17 passed.
- Full Ruff: passed.
- Full pytest: 176 passed.

## Remaining Limits

- The current method is split conformal on window-level binary risk scores, not
  a blocked time-series conformal proof for dependent biosignals.
- Patient-specific calibration needs enough patient-level validation rows; the
  code marks insufficient-patient cases as `global_fallback`.
- Real-data coverage numbers before frozen splits and Gate C remain
  exploratory and not citable.
- The intervals quantify forecast uncertainty; they do not make a clinical
  treatment recommendation.
