# T8 Forecastability Atlas

Date: 2026-05-21

Branch: `codex/forecastability-atlas`

Base: `origin/main@352d66a`

## Objective

Create the paper-facing synthesis layer that answers the core Q1 question:
which dataset/patient/modality/horizon/model settings are forecastable above a
null baseline, and which are not?

This task does not generate new benchmark numbers. It consumes leaderboard and
calibration artifacts and turns them into a forecastability atlas with explicit
claim status, Gate C readiness, and negative findings.

## Implementation

- Added `src/reports/forecastability_atlas.py`.
- Exported atlas utilities from `src/reports/__init__.py`.
- Added CLI `scripts/make_forecastability_atlas.py`.
- Added synthetic tests in `tests/test_forecastability_atlas.py`.

The atlas accepts leaderboard-style rows and optional calibration reliability
bins. It outputs one row per evaluated setting with:

- dataset/cohort/patient scope;
- modality and horizon;
- model and null reference;
- sensitivity, FAR/day, TIW, BSS, BSS confidence bounds, ECE;
- weighted reliability slope when reliability bins are supplied;
- forecastability label;
- claim status;
- `paper_table_ready` flag.

## Classification Rules

Current labels:

- `forecastable_above_null`: BSS confidence interval lower bound is above the
  null baseline.
- `unforecastable_null_overlap`: BSS confidence interval overlaps the null.
- `unforecastable_not_above_null`: BSS or confidence bounds are not above the
  null.
- `exploratory_positive_no_ci`: BSS is positive, but uncertainty bounds are
  missing.
- `underpowered`: event count or valid-window count is below thresholds.
- `not_citable_pre_gate_c`: Gate C/citation guardrail blocks a paper-table
  claim.
- `unassessed_no_null`: no BSS/null reference is available.

Negative results remain rows in the atlas instead of being hidden.

## Gate C Guardrail

By default the CLI requires Gate C for `paper_table_ready=True`. Rows may still
be included before Gate C, but they are marked as non-citable. A row declaring
`citation_status=citable_after_gate_c` without `gate_c_status=passed` raises an
error.

This preserves the project rule: citable benchmark claims require frozen
artifacts.

## Validation

Executed targeted validation:

```bash
uv run --extra dev ruff check src/reports/forecastability_atlas.py src/reports/__init__.py scripts/make_forecastability_atlas.py tests/test_forecastability_atlas.py
uv run --extra dev pytest tests/test_forecastability_atlas.py tests/test_calibration_skill_report.py tests/test_leaderboard_runner.py
uv run --extra dev ruff check .
uv run --extra dev --extra torch pytest
```

Result:

- Targeted Ruff: passed.
- Targeted pytest: 17 passed.
- Full Ruff: passed.
- Full pytest: 182 passed.

## Remaining Limits

- The atlas is only as credible as the input leaderboard rows and confidence
  intervals.
- Without BSS confidence intervals, positive rows remain exploratory.
- Real paper-ready atlas rows still depend on frozen Gate C artifacts and
  completed human audit.
- This scaffold does not compute model metrics from raw predictions; it
  intentionally synthesizes already generated benchmark artifacts.
