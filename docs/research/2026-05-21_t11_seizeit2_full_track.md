# T11 SeizeIT2 Full-Benchmark Track

Date: 2026-05-21

Branch: `codex/seizeit2-full-benchmark-track`

Base: `origin/main@82f71e9`

## Objective

Stop treating SeizeIT2 as a small edge subset and create a full benchmark-track
readiness layer. The track explicitly separates:

- ictal/background detection;
- short early warning;
- long-horizon forecasting.

It also separates ECG-only, ACC-only, bte-EEG-only, and multimodal tracks.

This task does not compute model scores and does not create citable real-data
claims. It builds the reproducible track matrix that later benchmark runs must
target.

## Implementation

- Added `src/reports/seizeit2_benchmark_track.py`.
- Exported helpers from `src/reports/__init__.py`.
- Added CLI `scripts/make_seizeit2_full_track.py`.
- Added tests in `tests/test_seizeit2_benchmark_track.py`.

The report consumes canonical SeizeIT2 processed tables:

- `recordings`
- `events`
- `modality_availability`
- optional `windows`
- optional official split manifest
- optional expected published counts JSON

## Scientific Guardrails

- Source tables with `source_dataset` not containing `seizeit2` fail closed.
- Official split manifests must cover every requested row.
- Duplicate split manifest keys fail closed.
- Invalid split names fail closed.
- Citable status requires `gate_c_status=passed`.
- MSG long-horizon forecasting is explicitly excluded from this track.
- Missing modality tracks remain explicit negative readiness rows.

## Track Matrix

Each row records:

- benchmark family: `seizeit2_full_track`;
- task name/type and leaderboard task type;
- horizon fields where relevant;
- score level (`sample_and_event` or `event`);
- modality track and required modalities;
- patients, recordings, events, optional sample rows;
- official split status;
- citable/non-citable status;
- `track_ready` and `track_reason`.

`track_ready=True` means the row has an official split, eligible recordings,
and events. It does not mean model performance exists.

## Count Summary

The count summary compares discovered counts to optional expected counts. If no
expected counts are supplied, it marks `expected_count_not_provided` instead of
pretending the published count was checked.

## Validation

Executed targeted validation:

```bash
uv run --extra dev ruff check src/reports/seizeit2_benchmark_track.py src/reports/__init__.py scripts/make_seizeit2_full_track.py tests/test_seizeit2_benchmark_track.py
uv run --extra dev pytest tests/test_seizeit2_benchmark_track.py tests/test_dataset_parsers.py tests/test_label_fidelity_audit.py
uv run --extra dev ruff check .
uv run --extra dev --extra torch pytest
```

Result:

- Targeted Ruff: passed.
- Targeted pytest: 26 passed.
- Full Ruff: passed.
- Full pytest: 199 passed.

## Remaining Limits

- Real count matching still requires official SeizeIT2 artifacts and documented
  filters.
- This does not decode waveforms or train/evaluate models.
- Detection/early-warning/forecasting outputs remain readiness rows until
  prediction tables are produced through the benchmark runner.
- Final paper-table claims still require Gate C and completed human audit.
