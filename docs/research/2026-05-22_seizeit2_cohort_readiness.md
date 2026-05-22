# SeizeIT2 Cohort Readiness Guardrail

Date: 2026-05-22

Branch: `codex/seizeit2-cohort-readiness`

Base: `origin/main@246a765`

## Objective

Prevent the project from presenting a SeizeIT2 smoke test or partial local
download as a full-cohort benchmark. Task T11 created a full-track readiness
matrix; this task adds the stop rule that consumes that matrix and says whether
the artifacts can support a full-cohort claim.

This task does not train a model, score predictions, or make a citable clinical
claim.

## Implementation

- Added `src/reports/seizeit2_cohort_readiness.py`.
- Added CLI `scripts/build_seizeit2_cohort_readiness.py`.
- Added tests in `tests/test_seizeit2_cohort_readiness.py`.

The report consumes:

- `track_csv` from `scripts/make_seizeit2_full_track.py`;
- `count_summary_csv` from the same T11 pipeline.

It writes:

- `seizeit2_cohort_readiness_summary.csv`;
- `seizeit2_cohort_readiness_blockers.csv`;
- `seizeit2_cohort_readiness_warnings.csv`;
- `seizeit2_cohort_readiness_manifest.csv`;
- `seizeit2_cohort_readiness_report.json`;
- `seizeit2_cohort_readiness_report.md`.

## Blocking Logic

The guardrail blocks full-cohort claims when any of these conditions hold:

- Gate B is not passed.
- Gate C is not passed.
- observed patients are below the configured full-cohort threshold;
- observed events are below the configured full-cohort threshold;
- expected published counts are missing or mismatched;
- official split manifest status is not clean;
- required splits, tasks, or modality tracks are missing;
- required split/task combinations have no ready track row.

Defaults are conservative:

- minimum patients for full-cohort claim: `100`;
- minimum events for full-cohort claim: `100`;
- required splits: `train,val,test`;
- required tasks: detection, short early-warning, long-horizon forecasting;
- required modalities: ECG, ACC, bte-EEG, multimodal.

## Scientific Guardrails

- Claim status is always `seizeit2_cohort_readiness_pre_gate_c_not_citable`.
- The report is a readiness guardrail, not model performance.
- Count mismatches are blockers, not prose footnotes.
- Non-ready tracks remain explicit negative readiness rows.
- No SeizeIT2 result becomes citable without Gate B and Gate C.

## Example

```bash
uv run --extra dev python scripts/build_seizeit2_cohort_readiness.py \
  --track-csv reports/seizeit2_full_track.csv \
  --count-summary-csv reports/seizeit2_full_track_counts.csv \
  --out-dir reports/seizeit2_cohort_readiness_2026-05-22 \
  --gate-b-status not_started \
  --gate-c-status not_started \
  --fail-on-blockers
```

## Validation

Targeted validation:

```bash
uv run --extra dev ruff check src/reports/seizeit2_cohort_readiness.py scripts/build_seizeit2_cohort_readiness.py tests/test_seizeit2_cohort_readiness.py
uv run --extra dev pytest tests/test_seizeit2_cohort_readiness.py tests/test_seizeit2_benchmark_track.py
```

Full validation:

```bash
uv run --extra dev ruff check .
uv run --extra dev --extra torch pytest
git diff --check
```

Result:

- Targeted Ruff: passed.
- Targeted pytest: 10 passed.
- Full Ruff: passed.
- Full pytest: 300 passed.
- `git diff --check`: passed.

## Remaining Limits

- This does not download missing SeizeIT2 subjects.
- This does not validate waveform decoding quality.
- Official expected counts still need source citation and advisor-approved
  filter definitions before Gate C.
- A ready cohort report is only a prerequisite; model rows still need frozen
  predictions, calibration, clinical utility, and leaderboard artifacts.
