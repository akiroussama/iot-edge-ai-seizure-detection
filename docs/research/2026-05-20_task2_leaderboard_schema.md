# Task 2 - Unified Leaderboard Schema

Date: 2026-05-20
Branch: `codex/leaderboard-schema` from `origin/main@249cd12`
Status: engineering-only, pre-Gate-C-safe.

## Plan

Task 2 adds a versioned schema for future leaderboard rows. It does not compute
new benchmark numbers and does not change any model or training code.

The schema must represent:

- dataset and cohort identity
- split policy and split reference
- horizon definition
- denominator accounting
- sensitivity, FAR/day, TIW
- Brier score and Brier Skill Score
- leakage and gate status
- edge deployment cost
- provenance and citable/not-citable status

## Plan Validation

This plan is valid only if:

- every leaderboard row must state whether it is citable;
- pre-Gate-C exploratory rows are supported but explicitly marked as
  `not_citable_pre_gate_c`;
- the schema can represent both forecasting and detection rows;
- edge-cost fields can be null for non-edge rows without removing the columns;
- no real-data model is trained and no new metric value is generated.

## Attack

The implementation adds five artifacts:

- `schemas/leaderboard_entry.schema.json`: JSON Schema draft 2020-12 for one
  leaderboard row.
- `schemas/leaderboard_columns.csv`: human-readable column dictionary.
- `schemas/leaderboard_template.csv`: empty CSV template with the canonical
  header order.
- `tests/test_leaderboard_schema.py`: consistency checks between the JSON
  schema, column dictionary, and CSV template.
- `docs/research/2026-05-20_task2_leaderboard_schema.md`: execution trace,
  audit notes, and the Task 2 stop point.

The schema uses a single-row model rather than separate detection/forecasting
schemas. Task-specific fields that do not apply are represented as `null`, but
the columns remain present so comparison tables can be joined safely.

## Result

The canonical row fields are:

- identity and provenance: `schema_version`, `result_id`, `repo_commit`,
  `evidence_uri`, `notes`
- curation status: `result_status`, `citation_status`
- task/dataset/model: `task_type`, `dataset`, `cohort`, `modality`,
  `model_name`, `model_family`
- split/horizon: `split_name`, `split_policy`, `split_ref`, `horizon_name`,
  `sph_minutes`, `sop_minutes`, `window_seconds`, `stride_seconds`
- denominator: `event_unit`, `events_source_total`, `events_after_filter`,
  `events_used_for_metrics`, `metric_units_used_for_metrics`,
  `prediction_rows`, `valid_prediction_rows`, `positive_windows`,
  `monitored_hours`
- metrics: `n_forecasted_or_detected`, `sensitivity`,
  `false_alarm_rate_per_day`, `false_alarm_rate_per_hour`,
  `time_in_warning`, `precision`, `f1_score`, `median_lead_time_seconds`,
  `brier_score`, `brier_skill_score`, `bss_reference`,
  `expected_calibration_error`, `auroc`, `auprc`
- validation gates: `label_audit_status`, `gate_b_status`, `gate_c_status`,
  `leakage_status`, `split_frozen_status`, `doi_or_prereg_uri`
- edge cost: `edge_target`, `quantization`, `model_size_kb`, `ram_kb`,
  `flash_kb`, `latency_ms`, `energy_mj_per_inference`

The citable status is deliberately explicit:

- `pre_gate_c_exploratory_not_citable`
- `gate_c_frozen_citable`
- `external_sota_context`
- `synthetic_smoke_test_not_citable`
- `invalid_or_retracted`

## Audit Of Result

Strengths:

- The schema prevents silent citation of pre-Gate-C numbers.
- Detection, forecasting, external SOTA, synthetic checks, and edge-cost rows
  can share one table.
- The CSV header is tested against the JSON Schema required fields, preventing
  later drift.

Limitations:

- This is a schema only; Task 3 still needs the evaluation runner that writes
  rows from prediction/event files.
- JSON Schema validation is not wired into a CLI yet.
- Brier Skill Score is represented but not computed here.
- External SOTA rows will still require manual provenance checks because many
  papers do not expose raw predictions.

## Conclusion

Task 2 establishes the leaderboard contract. Task 3 should implement the runner
that converts prediction tables and event tables into rows matching
`leaderboard.v1`.

## Execution Log

Commands:

```bash
git fetch origin main
git worktree add -b codex/leaderboard-schema \
  /tmp/epitwin-main-leaderboard-schema \
  origin/main
git diff --check
python -m json.tool schemas/leaderboard_entry.schema.json
uv run pytest tests/test_leaderboard_schema.py
uv run ruff check tests/test_leaderboard_schema.py
uv run --extra dev pytest tests/test_leaderboard_schema.py
uv run --extra dev ruff check tests/test_leaderboard_schema.py
```

Validation result:

- `git diff --check`: pass.
- `python -m json.tool schemas/leaderboard_entry.schema.json`: pass.
- `uv run pytest tests/test_leaderboard_schema.py`: failed because the default
  venv has no `pytest` installed.
- `uv run ruff check tests/test_leaderboard_schema.py`: failed because the
  default venv has no `ruff` installed.
- `uv run --extra dev pytest tests/test_leaderboard_schema.py`: `4 passed`.
- `uv run --extra dev ruff check tests/test_leaderboard_schema.py`: pass.
