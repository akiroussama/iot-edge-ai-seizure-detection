# T19 Failure Taxonomy

Date: 2026-05-21

Branch: `codex/failure-taxonomy`

Base: `origin/main@eb30601`

## Objective

Convert aggregate forecasting metrics into an auditable row-level taxonomy of
where a model fails. This is needed for a publishable benchmark because
sensitivity, FAR/day, BSS, calibration, and observability can identify that a
model is weak, but not why a specific patient/window failed.

This task is post-hoc descriptive analysis. It does not infer causal
physiology and does not create citable clinical claims before Gate C.

## Implementation

- Added `src/reports/failure_taxonomy.py`.
- Added CLI `scripts/make_failure_taxonomy_report.py`.
- Exported failure-taxonomy helpers from `src/reports/__init__.py`.
- Added config contract `configs/report/failure_taxonomy.yaml`.
- Added synthetic tests in `tests/test_failure_taxonomy.py`.

The CLI writes:

- `failure_taxonomy_rows.csv`
- `failure_taxonomy_summary.csv`
- `failure_taxonomy_patient_summary.csv`
- `failure_taxonomy_warnings.csv`
- `failure_taxonomy_manifest.csv`
- `failure_taxonomy_report.json`
- `failure_taxonomy_report.md`

## Categories

The current taxonomy assigns one primary category per prediction row:

- `excluded_alarm`
- `excluded_row`
- `observability_abstained`
- `observability_deficient`
- `true_positive_alarm`
- `true_positive_low_margin`
- `missed_low_risk_positive`
- `missed_forecast_positive`
- `false_alarm_high_risk_negative`
- `false_alarm_negative`
- `high_risk_true_negative`
- `true_negative`

Excluded rows and observability failures take precedence over ordinary
miss/false-alarm labels so that sensor/data problems are not hidden as model
errors.

## Scientific Guardrails

- The taxonomy is marked `post_hoc_descriptive_not_causal`.
- Rows without observability columns produce warnings instead of silently
  pretending observability was assessed.
- Excluded/censored rows are separated before valid clinical categories.
- Each row carries `failure_category`, `failure_reason`, and
  `failure_severity`.
- Summaries are produced by category and by patient.
- The report remains pre-Gate-C and not citable as a benchmark result.

## Validation

Executed targeted validation:

```bash
uv run --extra dev ruff check src/reports/failure_taxonomy.py src/reports/__init__.py scripts/make_failure_taxonomy_report.py tests/test_failure_taxonomy.py
uv run --extra dev pytest tests/test_failure_taxonomy.py
uv run --extra dev pytest tests/test_failure_taxonomy.py tests/test_observability.py tests/test_clinical_utility.py tests/test_leaderboard_runner.py
```

Executed full validation:

```bash
uv run --extra dev ruff check .
uv run --extra dev --extra torch pytest
```

Result:

- Targeted Ruff: passed.
- Targeted pytest: 5 passed.
- Neighbor pytest: 20 passed.
- Full Ruff: passed.
- Full pytest: 254 passed.

## Remaining Limits

- Category thresholds are configurable but still heuristic.
- The taxonomy explains rows using observed labels, alarms, risks, exclusion,
  and observability status; it does not prove physiological mechanisms.
- Patient-level summaries can guide review, but clinician audit remains
  required before paper claims.
- Citable failure analysis requires Gate C frozen inputs and reviewed labels.
