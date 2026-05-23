# Gate C Frozen Null Benchmark

Date: 2026-05-23

## Objective

Run the first frozen MSG benchmark pass from the Gate C registry-backed
artifacts only. The run must refuse local `data/*` source tables and must use
the committed freeze package as its only benchmark input.

This block covers:

- Frozen-only rerun harness.
- First frozen null baseline results.
- Unified leaderboard rows.
- Calibration/Brier Skill Score reports.
- Scientific audit.
- Forecastability atlas as the next research-upgrade artifact.

## Frozen Inputs

Registry:

- `reports/gate_c_msg_freeze_2026-05-23/gate_c_registry.json`

Required frozen artifacts:

- `reports/gate_c_msg_freeze_2026-05-23/artifacts/events.csv`
- `reports/gate_c_msg_freeze_2026-05-23/artifacts/labels.csv`
- `reports/gate_c_msg_freeze_2026-05-23/artifacts/splits.csv`

The harness verifies the Gate C registry with `require_frozen=True` and rejects
required input artifacts whose paths are under `data/*`.

## Benchmark Configuration

- Dataset: MSG.
- Horizon: SPH60/SOP1440.
- Window: 1 hour.
- Stride: 1 hour.
- Fit split: train.
- Threshold split: val.
- Evaluation split: test.
- Target TIW: 0.10.
- Event filter: `recording_match_status=matched`.
- Event denominator: prediction-coverable matched test events.
- Bootstrap samples for BSS confidence intervals: 1,000 patient-level draws.

## Results

Source and denominator counts:

- Source events: 768.
- Matched events after event filter: 510.
- Test prediction-coverable events used for metrics: 54.
- Valid test prediction rows: 1,418.
- Positive test windows: 373.

| Null model | Sensitivity | FAR/day | TIW | Brier | BSS vs climatology | BSS CI |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| split_prevalence_prior | 0.648 | 1.557 | 0.099 | 0.239 | 0.000 | [0.000, 0.000] |
| rate_matched_random | 0.463 | 1.472 | 0.096 | 0.239 | 0.000 | [0.000, 0.000] |
| patient_prior | 0.056 | 0.085 | 0.038 | 0.128 | 0.466 | [-0.420, 0.771] |
| cycle_preserving_random | 0.741 | 0.592 | 0.097 | 0.222 | 0.070 | [0.034, 0.089] |

## Interpretation

The frozen null benchmark is scientifically useful because it exposes a real
structure in the frozen MSG labels before training any neural model:

- The hour-of-day cycle-preserving null is above the split-prevalence null in
  BSS with a patient-bootstrap interval above zero.
- Patient-prior risk has a strong point estimate but is not stable under the
  patient bootstrap, so it remains a null-overlap finding.
- Split prevalence and rate-matched random behave as expected with BSS equal to
  zero against the climatology reference.

This is not a clinical model result. It says that a simple temporal-cycle null
already captures non-trivial risk structure in the frozen test split. Any future
learned model must beat this baseline, not only the split-prevalence prior.

## Forecastability Atlas

The generated atlas is:

- `reports/gate_c_frozen_benchmark_2026-05-23/forecastability_atlas.csv`
- `reports/gate_c_frozen_benchmark_2026-05-23/forecastability_atlas.md`

Atlas labels:

- `forecastable_above_null`: 1 row.
- `unforecastable_null_overlap`: 3 rows.

The only `forecastable_above_null` row is the cycle-preserving null baseline.
That row is paper-table-ready as a baseline result, not as evidence that a
deployable model exists.

## Exact Command

```bash
uv run python scripts/run_gate_c_frozen_benchmark.py \
  --registry reports/gate_c_msg_freeze_2026-05-23/gate_c_registry.json \
  --out-dir reports/gate_c_frozen_benchmark_2026-05-23 \
  --bootstrap-samples 1000 \
  --doi-or-prereg-uri doi:10.5281/zenodo.17380899
```

## Outputs

- `reports/gate_c_frozen_benchmark_2026-05-23/frozen_benchmark_manifest.json`
- `reports/gate_c_frozen_benchmark_2026-05-23/frozen_benchmark_audit.md`
- `reports/gate_c_frozen_benchmark_2026-05-23/leaderboard_rows.csv`
- `reports/gate_c_frozen_benchmark_2026-05-23/leaderboard_rows_with_ci.csv`
- `reports/gate_c_frozen_benchmark_2026-05-23/calibration_summary.csv`
- `reports/gate_c_frozen_benchmark_2026-05-23/calibration_skill.csv`
- `reports/gate_c_frozen_benchmark_2026-05-23/calibration_reliability.csv`
- `reports/gate_c_frozen_benchmark_2026-05-23/calibration_bootstrap.csv`
- `reports/gate_c_frozen_benchmark_2026-05-23/forecastability_atlas.csv`
- `reports/gate_c_frozen_benchmark_2026-05-23/forecastability_atlas.md`

## Next Scientific Lock

The next useful lock is to run a non-null frozen baseline that uses wearable
signals or engineered cyclic features, then compare it against
`cycle_preserving_random`, not only against climatology. A learned model that
does not beat the cycle-preserving null should not be presented as a major
forecasting contribution.
