# P3 N=1 Longitudinal Deep Dive

Date: 2026-05-22

Branch: `codex/n1-longitudinal-deep-dive`

Base: `origin/main@7394348`

## Objective

Add a single-patient longitudinal deep-dive report for wearable seizure-risk
predictions. This supports a personalized-medicine thesis angle: not only
whether a model performs on average, but how risk evolves over time for one
well-observed patient.

This task is descriptive infrastructure only. It does not select or analyze a
real citable patient before Gate C.

## Implementation

- Added `src/reports/longitudinal_deep_dive.py`.
- Added CLI `scripts/make_longitudinal_deep_dive.py`.
- Exported helpers from `src/reports/__init__.py`.
- Added config contract `configs/report/longitudinal_deep_dive.yaml`.
- Added synthetic tests in `tests/test_longitudinal_deep_dive.py`.

The CLI writes:

- `n1_patient_selection.csv`
- `n1_timeline.csv`
- `n1_segment_summary.csv`
- `n1_event_neighborhoods.csv`
- `n1_manifest.csv`
- `n1_report.json`
- `n1_report.md`

## Method

If no `patient_id` is provided, the report selects the patient with the highest
selection score combining duration, positives, and alarms. For the selected
patient it emits:

- a full ordered timeline;
- rolling 12-row mean risk;
- risk deltas from previous rows;
- segment-level summaries;
- event-neighborhood rows around positive windows;
- failure categories when supplied by Task 19.

## Scientific Guardrails

- The report is explicitly single-patient and not generalizable.
- It is descriptive, not causal.
- Failure categories and observability fields are consumed when present but not
  invented when absent.
- The report remains pre-Gate-C and not citable as a benchmark result.

## Validation

Executed targeted validation:

```bash
uv run --extra dev ruff check src/reports/longitudinal_deep_dive.py src/reports/__init__.py scripts/make_longitudinal_deep_dive.py tests/test_longitudinal_deep_dive.py
uv run --extra dev pytest tests/test_longitudinal_deep_dive.py
uv run --extra dev pytest tests/test_longitudinal_deep_dive.py tests/test_failure_taxonomy.py tests/test_forecastability_atlas.py tests/test_clinical_audit_workbench.py
```

Executed full validation:

```bash
uv run --extra dev ruff check .
uv run --extra dev --extra torch pytest
```

Result:

- Targeted Ruff: passed.
- Targeted pytest: 5 passed.
- Neighbor pytest: 21 passed.
- Full Ruff: passed.
- Full pytest: 264 passed.

## Remaining Limits

- Real patient selection must wait for Gate C frozen predictions and reviewed
  labels.
- N=1 analysis can generate hypotheses; it cannot establish cohort-level
  generalization.
- Clinical interpretation still requires review of the underlying event
  timeline and sensor quality.
