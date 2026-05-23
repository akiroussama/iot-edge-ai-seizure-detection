# Gate C Frozen Null Benchmark

Date: 2026-05-23

## What Changed

- Added `scripts/run_gate_c_frozen_benchmark.py`.
- Added `src/artifacts/gate_c_frozen_benchmark.py`.
- Added tests for frozen-only registry enforcement and CLI execution.
- Extended leaderboard registry verification to accept an explicit registry
  root, so temp-root and committed-root registries are both verified correctly.
- Generated the first frozen MSG null benchmark report package under
  `reports/gate_c_frozen_benchmark_2026-05-23`.

## Results

Frozen input registry:

- `reports/gate_c_msg_freeze_2026-05-23/gate_c_registry.json`

Frozen benchmark outputs:

- `reports/gate_c_frozen_benchmark_2026-05-23/frozen_benchmark_manifest.json`
- `reports/gate_c_frozen_benchmark_2026-05-23/frozen_benchmark_audit.md`
- `reports/gate_c_frozen_benchmark_2026-05-23/leaderboard_rows_with_ci.csv`
- `reports/gate_c_frozen_benchmark_2026-05-23/forecastability_atlas.csv`

Key counts:

- Source events: 768.
- Matched events: 510.
- Test prediction-coverable matched events: 54.
- Valid test prediction rows: 1,418.
- Positive test windows: 373.

Key findings:

- `split_prevalence_prior`: BSS 0.000.
- `rate_matched_random`: BSS 0.000.
- `patient_prior`: BSS 0.466, CI [-0.420, 0.771], null-overlap.
- `cycle_preserving_random`: BSS 0.070, CI [0.034, 0.089], above climatology null.

## Validation

Commands executed:

```bash
uv run ruff check src/artifacts/gate_c_frozen_benchmark.py scripts/run_gate_c_frozen_benchmark.py scripts/make_leaderboard_row.py tests/test_gate_c_frozen_benchmark.py
uv run pytest -q tests/test_gate_c_frozen_benchmark.py tests/test_leaderboard_runner.py tests/test_forecast_nulls.py tests/test_calibration_skill_report.py tests/test_forecastability_atlas.py
uv run python scripts/run_gate_c_frozen_benchmark.py --registry reports/gate_c_msg_freeze_2026-05-23/gate_c_registry.json --out-dir reports/gate_c_frozen_benchmark_2026-05-23 --bootstrap-samples 1000 --doi-or-prereg-uri doi:10.5281/zenodo.17380899
python -m json.tool reports/gate_c_frozen_benchmark_2026-05-23/frozen_benchmark_manifest.json
```

## Guardrail

The benchmark is frozen and citable as a registry-backed null-baseline result,
but it is not a trained clinical model result and not a SOTA claim. The event
metric denominator is the matched, prediction-coverable MSG test subset.
