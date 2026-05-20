# EpiTwin-Open v0.1 Verification

Date: 2026-05-15

## Scope

This report freezes the current v0.1 scaffold before v1.0/v2.0 work begins. It verifies only software behavior on synthetic/mock pathways. It does not report real clinical performance.

## Repository State

- Workspace root: `/mnt/c/doctorat/iot/epitwin-open`
- Git repository: no
- Real datasets mounted: no evidence found in this workspace
- Raw data processed: no
- A100 training launched: no

## Commands Run

```bash
uv sync --extra dev --extra torch
uv run python -m pytest -q
uv run ruff check .
./RUN_THIS_FIRST.sh
uv run python scripts/run_synthetic_demo.py
uv run python scripts/make_report.py --synthetic --out-dir reports
uv run python -u scripts/train_epitwin_ssl.py --epochs 1 --batch-size 1 --time-steps 4 --hidden-dim 4 --backbone gru
```

## Results

- Dependency sync: passed.
- Tests: `42 passed`.
- Ruff: passed.
- Synthetic demo: passed.
- Synthetic report generation: passed.
- SSL smoke training: passed on CPU.
- `RUN_THIS_FIRST.sh`: passed.

## Verified Capabilities

- SPH/SOP label generation.
- Ictal and postictal exclusion.
- Event-level sensitivity.
- False alarm rate per hour/day.
- Time-in-Warning.
- Median lead time.
- Brier score and ECE.
- Reliability table utility.
- Threshold sweep utilities.
- Temporal split purging.
- Leakage audit for patient/recording overlap, duplicate windows, temporal overlap, and postictal contamination.
- Fixed window generation for datetime and numeric-second recordings.
- Mock-tested SeizeIT2 BIDS-like event parsing.
- Mock-tested My Seizure Gauge seizure/ZIP manifest parsing.
- EpiTwin-SSL tiny CPU forward/smoke path.

## Synthetic-Only Disclaimer

The synthetic demo uses toy data and a toy risk score. Its sensitivity, FAR/day, Time-in-Warning, Brier score, and ECE are software smoke-test outputs only. They are not clinical evidence and must not be used in a paper result claim.

## Day 0 Findings

- `MANIFEST.md` had a stale test count and was updated.
- This workspace is not under Git, so Day 0 branch/commit steps cannot be executed here.
- `make` may not be installed in the current environment; direct `uv run` commands are verified.
- Day 1 should standardize command docs and improve `RUN_THIS_FIRST.sh` progress output.

## Remaining Methodological Risks

- No real SeizeIT2 or My Seizure Gauge data were parsed.
- Real waveform decoding remains dataset-version specific.
- My Seizure Gauge HR/steps stream extraction is not complete.
- Feature normalization leakage cannot be fully audited until feature extraction records fit metadata.
- Threshold fitting must be constrained to validation splits before v2.0 claims.
- Manual review of 5-10 real seizure timelines is required before A100 training.

## A100 Readiness

Not ready.

Required before launch:

- Real labels generated and manually audited.
- Real splits frozen.
- Random baseline evaluated.
- Leakage audit clean.
- Human seizure timeline inspection complete.
