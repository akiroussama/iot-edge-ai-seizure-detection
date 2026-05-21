# T16 Edge-Aware Forecasting Ablation

Date: 2026-05-21

Branch: `codex/edge-aware-ablation`

Base: `origin/main@7db6574`

## Objective

Connect forecast quality to deployability. Wearable seizure-risk models should
not be compared only on clinical metrics; the paper also needs a traceable
view of RAM, flash, model size, latency, energy, quantization, and Pareto
trade-offs.

This task creates the reporting layer only. It does not claim measured ESP32,
MCU, or wearable-device performance unless an input edge profile explicitly
documents such a measurement.

## Implementation

- Added `src/reports/edge_ablation.py`.
- Added CLI `scripts/make_edge_ablation_report.py`.
- Exported edge-ablation helpers from `src/reports/__init__.py`.
- Added config contract `configs/report/edge_ablation.yaml`.
- Added synthetic tests in `tests/test_edge_ablation.py`.

The CLI writes:

- `edge_ablation_table.csv`
- `edge_pareto_frontier.csv`
- `edge_ablation_warnings.csv`
- `edge_ablation_manifest.csv`
- `edge_ablation_report.json`
- `edge_ablation_report.md`

## Input Contract

The report joins:

- clinical rows keyed by `model_name`, usually leaderboard or metric rows;
- edge profiles keyed by `model_name`, `edge_target`, and `quantization`.

Each edge profile must include:

- `parameter_count`
- `model_size_kb`
- `ram_kb`
- `flash_kb`
- `latency_ms`
- `energy_mj_per_inference`
- `profiling_method`
- `evidence_uri`

## Scientific Guardrails

- Cost values must be numeric and non-negative.
- Duplicate edge profile keys fail validation.
- Missing `profiling_method` or `evidence_uri` fails validation by default.
- Pre-Gate-C clinical rows are warned as non-citable.
- Estimated edge costs are warned separately from measured hardware profiles.
- Clinical score and edge cost are reported in separate columns.
- Pareto status maximizes the selected clinical score while minimizing
  parameter count, model size, RAM, flash, latency, and energy.
- The report is a pre-Gate-C engineering artifact unless downstream inputs are
  frozen and citable.

## Validation

Executed targeted validation:

```bash
uv run --extra dev ruff check src/reports/edge_ablation.py src/reports/__init__.py scripts/make_edge_ablation_report.py tests/test_edge_ablation.py
uv run --extra dev pytest tests/test_edge_ablation.py
uv run --extra dev --extra torch pytest tests/test_edge_ablation.py tests/test_leaderboard_schema.py tests/test_leaderboard_runner.py tests/test_models.py
```

Executed full validation:

```bash
uv run --extra dev ruff check .
uv run --extra dev --extra torch pytest
```

Result:

- Targeted Ruff: passed.
- Targeted pytest: 5 passed.
- Neighbor pytest with Torch: 17 passed.
- Full Ruff: passed.
- Full pytest: 245 passed.

## Remaining Limits

- The report does not measure hardware by itself; it enforces traceable input
  profiles.
- Energy values remain estimates unless the profile evidence points to a real
  measurement command or hardware log.
- Pareto efficiency depends on the selected clinical metric and supplied
  budgets; paper tables must state these assumptions.
- Citable edge/clinical claims still require Gate C frozen clinical rows and
  measured or carefully documented hardware profiles.
