# W2 Active Audit Selection

Date: 2026-05-21

Branch: `codex/active-audit-selection`

Base: `origin/main@67108be`

## Objective

Reduce the Phase B human label-audit bottleneck without replacing human review.
The selector turns seizure-centered audit timelines into an event-level review
queue ordered by acquisition signals that are relevant to clinical source
verification:

- model uncertainty near the event;
- disagreement against one or more null/reference predictors;
- clinical leverage from valid alarms or high risk close to seizure onset;
- edge-case density from censoring, unexpected ictal/postictal rows, and valid
  forecast positives.

The output is not a benchmark result and is not citable as model performance.
It is an audit prioritization artifact for deciding what a reviewer should
inspect first.

## Implementation

- Added `src/active/audit_selection.py`.
- Added package export in `src/active/__init__.py`.
- Added CLI `scripts/select_audit_targets.py`.
- Added synthetic behavior tests in `tests/test_active_audit_selection.py`.

The API preserves the existing label-audit review sheet columns and appends
active-selection columns such as `uncertainty_score`, `disagreement_score`,
`clinical_leverage_score`, `edge_case_score`, `active_audit_score`,
`dominant_acquisition`, and `selection_reason`.

## Guardrails

- Prediction and reference rows are aligned by identity columns
  `patient_id,recording_id,window_start,window_end` by default.
- Missing prediction rows fail closed with a `ValueError`.
- Duplicate prediction keys fail closed with a `ValueError`.
- Reference predictors require model predictions, avoiding a meaningless
  disagreement score.
- The selector emits only prioritization metadata; reviewer decision fields
  remain blank and must be completed by a human.

## Validation

Executed targeted validation:

```bash
uv run --extra dev ruff check src/active/__init__.py src/active/audit_selection.py scripts/select_audit_targets.py tests/test_active_audit_selection.py
uv run --extra dev pytest tests/test_active_audit_selection.py tests/test_label_audit.py
uv run --extra dev ruff check .
uv run --extra dev --extra torch pytest
```

Result:

- Targeted Ruff: passed.
- Targeted pytest: 12 passed.
- Full Ruff: passed.
- Full pytest: 170 passed.

The synthetic behavior test injects one label issue and verifies that
top-score active selection captures it with budget 1 while a fixed-seed random
baseline does not. This is a sanity check of acquisition behavior, not a claim
about real clinical yield.

## Remaining Limits

- Real Phase B yield still requires clinician-completed audit sheets.
- Acquisition weights are transparent defaults, not optimized on real data.
- The module does not infer label correctness; it only prioritizes review.
- Any downstream real-data numbers before Gate C remain pre-Gate-C exploratory
  and not citable as benchmark claims.
