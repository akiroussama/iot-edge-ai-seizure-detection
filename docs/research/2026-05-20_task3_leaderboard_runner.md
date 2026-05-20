# Task 3 - Leaderboard Evaluation Runner

Date: 2026-05-20
Branch: `codex/leaderboard-runner` stacked on `origin/codex/leaderboard-schema@3035e62`
Status: engineering-only, pre-Gate-C-safe.

## Plan

Task 3 adds a CLI runner that converts prediction and event tables into one
`leaderboard.v1` row. It does not train a model and does not run on real data in
this step.

The runner must:

- read prediction and event tables;
- apply optional prediction and event filters;
- optionally restrict events to prediction-horizon coverage;
- compute event-level denominator, sensitivity, FAR/day, TIW, Brier, BSS,
  calibration, AUROC/AUPRC, and edge metadata when available;
- write CSV, JSON, and Markdown outputs;
- preserve explicit Gate-C/citation status in every row.

## Plan Validation

This plan is valid because Task 3 is pure tooling:

- tests use synthetic toy data only;
- no real-data benchmark number is generated;
- default `result_status` is `pre_gate_c_exploratory_not_citable`;
- default `citation_status` is `not_citable_pre_gate_c`;
- the row shape is checked against the Task 2 schema/template.

Task 2 PR #3 was still open when this branch started, so this branch is stacked
on `codex/leaderboard-schema`. After PR #3 merges, this PR should be rebased or
retargeted onto `main`.

## Attack

Implementation:

- `scripts/make_leaderboard_row.py`
  - CLI input: `--predictions`, `--events`, identity/status metadata, split,
    horizon, gate status, edge metadata.
  - Outputs: `--out-csv`, optional `--out-json`, optional `--out-md`.
  - Uses existing project metrics for sensitivity, FAR/day, FAR/hour, TIW,
    median lead time, Brier score, and ECE.
  - Adds dependency-free AUROC/AUPRC helpers for binary risk scores.
  - Adds optional Brier Skill Score when `--reference-predictions` is supplied.

Tests:

- `tests/test_leaderboard_runner.py`
  - synthetic predictions/events;
  - direct row construction;
  - Brier Skill Score with a constant reference;
  - CSV/JSON/Markdown output;
  - subprocess CLI smoke test.

## Result

The runner can now produce a standardized row with the exact `leaderboard.v1`
header:

```bash
uv run --extra dev python scripts/make_leaderboard_row.py \
  --predictions predictions.csv \
  --events events.csv \
  --out-csv leaderboard_row.csv \
  --out-json leaderboard_row.json \
  --out-md leaderboard_row.md \
  --result-id example \
  --dataset synthetic \
  --model-name toy \
  --split-policy synthetic \
  --sph-minutes 30 \
  --sop-minutes 120
```

The generated Markdown report carries a visible non-citable warning unless the
row is explicitly marked `citable_after_gate_c`.

## Audit Of Result

Strengths:

- Converts existing metric code into a leaderboard contract without changing the
  metric implementations.
- Keeps denominator fields explicit: source events, filtered events, metric
  events, prediction rows, valid prediction rows.
- Supports BSS without adding a dependency.
- Keeps citation safety as a first-class field.

Limitations:

- The runner currently supports event units `seizure` and `cluster`; schema
  placeholders for `window`, `episode`, and `not_applicable` remain for future
  tasks.
- JSON Schema validation is structural through header/key checks, not a full
  JSON Schema validator dependency.
- External SOTA rows are not generated here; they still need a separate manual
  provenance workflow.
- AUROC/AUPRC are window-level over `forecast_label` and `risk_score`; papers
  using event-level AUC need explicit notes before comparison.

## Conclusion

Task 3 makes the leaderboard schema executable. After PR #3 merges, this branch
should be retargeted to `main`; then Task 4 can add constrained null models that
feed `--reference-predictions` and make Brier Skill Score meaningful.

## Execution Log

Commands:

```bash
git worktree add -b codex/leaderboard-runner \
  /tmp/epitwin-leaderboard-runner \
  origin/codex/leaderboard-schema
git diff --check
uv run --extra dev pytest tests/test_leaderboard_runner.py tests/test_leaderboard_schema.py
uv run --extra dev ruff check \
  scripts/make_leaderboard_row.py \
  tests/test_leaderboard_runner.py \
  tests/test_leaderboard_schema.py
```

Validation result:

- `git diff --check`: pass.
- `uv run --extra dev pytest tests/test_leaderboard_runner.py tests/test_leaderboard_schema.py`: `8 passed`.
- `uv run --extra dev ruff check scripts/make_leaderboard_row.py tests/test_leaderboard_runner.py tests/test_leaderboard_schema.py`: pass.
