# Task 5 - Calibration, BSS, And Null-Corrected Skill Report

Date: 2026-05-20
Branch: `codex/calibration-bss`
Base: `origin/main@2f89a16`
Status: engineering-only, pre-Gate-C-safe.

## Plan

Task 5 turns the Task 4 null predictions into an auditable calibration and
skill report. The goal is not to run real data. The goal is to make future
prediction tables comparable against constrained nulls with strict row
alignment, Brier Skill Score, reliability bins, and bootstrap uncertainty.

Deliverables:

- strict `brier_skill_score` metric;
- pure report builder in `src/reports/calibration_skill.py`;
- CLI `scripts/make_calibration_report.py`;
- synthetic tests for BSS-vs-self, null non-improvement, row mismatch, label
  mismatch, bootstrap scopes, and Gate C citation guard.

## Plan Validation

This task is valid immediately after Task 4 because `origin/main` now contains:

- `scripts/run_null_baseline.py`;
- the four constrained null models;
- the leaderboard schema fields for Brier, BSS, and ECE;
- the Task 3 runner, which can later consume one selected reference via
  `--reference-predictions`.

Task 5 stays pre-Gate-C safe:

- synthetic tests only;
- no real-data benchmark number;
- no external citation added;
- citable output is blocked unless `gate_c_status=passed`.

## Attack

Implementation choices:

- Alignment uses identity columns, defaulting to
  `patient_id, recording_id, window_start, window_end`.
- Every reference table must contain exactly the same rows as the model table.
- `forecast_label` and `is_excluded` must match between model and reference.
- Missing alignment columns, duplicate keys, missing reference rows, extra
  reference rows, and label mismatches raise `ValueError`.
- BSS is strict: if the reference Brier score is zero, the function raises
  instead of returning a silent placeholder.
- Bootstrap confidence intervals are group bootstraps over patient and event
  columns. Missing requested group columns raise explicit errors.

The CLI writes:

- `calibration_summary.csv`
- `calibration_skill.csv`
- `calibration_reliability.csv`
- `calibration_bootstrap.csv`
- `calibration_report.json`
- `calibration_report.md`

## Result

Implemented files:

- `src/metrics/calibration.py`
- `src/metrics/__init__.py`
- `src/reports/__init__.py`
- `src/reports/calibration_skill.py`
- `scripts/make_calibration_report.py`
- `tests/test_calibration_skill_report.py`

The report supports multiple references, for example:

```bash
uv run --extra dev python scripts/make_calibration_report.py \
  --predictions model_predictions.csv \
  --reference-predictions split_prevalence_prior=null_split.csv \
  --reference-predictions patient_prior=null_patient.csv \
  --reference-predictions rate_matched_random=null_random.csv \
  --reference-predictions cycle_preserving_random=null_cycle.csv \
  --out-dir reports/calibration/example \
  --model-name example_model \
  --prediction-filter split=test \
  --bootstrap-samples 1000
```

## Audit

What is stronger now:

- A model cannot get BSS credit against a mismatched null table.
- A random or worse-than-null model can be detected by non-positive BSS.
- Calibration reports carry explicit citation/Gate-C status.
- Patient/event uncertainty is part of the report, not an afterthought.

Known boundaries:

- Event bootstrap requires an event grouping column in the prediction table.
  If the column is absent, the report fails closed unless event bootstrap is
  explicitly disabled.
- This PR creates reporting infrastructure only. It does not choose the final
  paper reference null or run real data.
- Future Gate C work must freeze artifact hashes and split manifests before
  any real-data output becomes citable.

## Commands

```bash
git diff --check
uv run --extra dev pytest tests/test_calibration_skill_report.py
uv run --extra dev pytest tests/test_calibration_skill_report.py \
  tests/test_calibration.py tests/test_leaderboard_runner.py \
  tests/test_forecast_nulls.py
uv run --extra dev ruff check src/metrics/calibration.py \
  src/metrics/__init__.py src/reports/__init__.py \
  src/reports/calibration_skill.py scripts/make_calibration_report.py \
  tests/test_calibration_skill_report.py
```

Validation result:

- Initial targeted ruff: pass.
- Initial targeted pytest: `7 passed`.
- `git diff --check`: pass.
- `uv run --extra dev ruff check src/metrics/calibration.py src/metrics/__init__.py src/reports/__init__.py src/reports/calibration_skill.py scripts/make_calibration_report.py tests/test_calibration_skill_report.py`: pass.
- `uv run --extra dev pytest tests/test_calibration_skill_report.py tests/test_calibration.py tests/test_leaderboard_runner.py tests/test_forecast_nulls.py`: `31 passed`.
- `uv run --extra dev --extra torch pytest`: `161 passed`.

## Conclusion

Task 5 adds the missing null-corrected calibration layer needed for a serious
forecasting paper. It makes future model claims harder to overstate: every
score must be aligned to the same windows, compared against explicit nulls,
and reported with patient/event uncertainty and Gate-C citation status.
