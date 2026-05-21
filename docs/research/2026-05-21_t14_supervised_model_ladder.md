# T14 Supervised Model Ladder

Date: 2026-05-21

Branch: `codex/supervised-model-ladder`

Base: `origin/main@f40beae`

## Objective

Add a controlled supervised model ladder that can turn frozen window-feature
tables into standardized prediction files for later leaderboard, calibration,
robustness, and clinical-utility reports.

This task is an engineering layer only. It does not train on real frozen
artifacts and does not create citable benchmark claims before Gate C.

## Implementation

- Added `src/models/supervised_ladder.py`.
- Added CLI `scripts/run_supervised_model_ladder.py`.
- Added config contract `configs/model/supervised_ladder.yaml`.
- Exported supervised ladder helpers from `src/models/__init__.py`.
- Added synthetic behavior tests in `tests/test_supervised_ladder.py`.

The initial ladder registers five rungs:

- `logistic_regression`
- `gradient_stumps`
- `mlp`
- `tcn`
- `gru`

The temporal rungs are declared as sequence-model rungs but currently consume
the same leakage-screened window-feature table as the other rungs. They should
not be presented as true temporal-sequence models until Gate C sequence tensors
are materialized.

## Scientific Guardrails

- A named null/reference comparator is mandatory for every run.
- Prediction/reference rows must align exactly on patient, recording, and
  window keys.
- `forecast_label` and `is_excluded` must match between the model table and
  comparator table.
- Feature selection excludes IDs, labels, split metadata, risk/alarm outputs,
  and explicit temporal-leakage columns such as
  `time_to_next_seizure_seconds`.
- Thresholds are fit only on the configured validation split.
- Training uses only the configured training split.
- Test-label perturbation is covered by a regression test and must not change
  risk scores.
- Multi-rung CLI runs derive deterministic per-model seeds.
- Outputs carry `feature_set_hash`, `training_artifact_hash`,
  `comparator_reference_hash`, and the seed used.
- Rows without usable feature evidence are explicitly marked through
  `supervised_prediction_status`.

## Output Tables

The CLI writes:

- `{model_name}_predictions.csv`
- `supervised_ladder_manifest.csv`
- `supervised_ladder_manifest.json`

Prediction files append the standardized supervised ladder columns while
passing through the input columns required by the leaderboard runner.

## Validation

Executed targeted validation:

```bash
uv run --extra dev ruff check src/models/supervised_ladder.py src/models/__init__.py scripts/run_supervised_model_ladder.py tests/test_supervised_ladder.py
uv run --extra dev pytest tests/test_supervised_ladder.py tests/test_msg_tabular_training.py tests/test_leaderboard_runner.py
```

Executed full validation:

```bash
uv run --extra dev ruff check .
uv run --extra dev --extra torch pytest
```

Result:

- Targeted Ruff: passed.
- Targeted pytest: 15 passed.
- Full Ruff: passed.
- Full pytest: 229 passed.

## Remaining Limits

- No real-data supervised result is claimed here.
- Temporal rungs are registered for a common CLI contract but are not yet true
  sequence models.
- Citable comparisons still require Gate C frozen artifacts, null-corrected
  reporting, and downstream robustness/calibration/clinical-utility reports.
