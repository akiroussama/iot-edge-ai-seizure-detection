# Claude Review 2026-05-15

This file preserves the review summary provided to Codex in chat on 2026-05-15. The original file
was not present in this checkout when Phase R started, so this document records the actionable
findings that now drive remediation.

## Verdict

The benchmark would not survive a serious seizure-forecasting methods review in its current state,
but the blockers are framing and plumbing defects rather than fundamental design failures. The
central defect is that leakage safety is opt-in, and unsafe paths fail silently by returning zeros,
NaNs, or no alarms instead of raising errors.

## Critical Findings

### C1: Threshold Tuning On Test

`scripts/sweep_thresholds.py` sweeps thresholds over `--predictions` with no split concept. This can
turn a test set into a calibration set.

Files:

- `src/metrics/sweep.py`
- `scripts/sweep_thresholds.py`

### C2: No Right Censoring

Windows whose forecast horizon extends beyond the recording end are counted as true negatives. This
is especially severe for MSG with a 24-hour SOP.

File:

- `src/labeling/sph_sop.py`

### C3: Silent Degeneration For Held-Out Patients

Rule baselines can degenerate silently to "never alarm" on held-out patients when the reference
scope is empty.

File:

- `src/baselines/simple_rules.py`

### C4: Biased MSG Matched Subset And Inconsistent Denominators

The matched MSG subset is biased toward seizures during wear time, and sensitivity denominators are
inconsistent across reports.

Files:

- `src/datasets/msg_loader.py`
- `scripts/make_dataset_report.py`

## High Findings

- H1: Seizure clusters can place structurally non-forecastable seizures in the denominator.
- H2: Leakage audit gives false assurance with a static "not machine-checkable" line.
- H3: Temporal splits assume monotonic timestamps and can fail silently when SeizeIT2 timestamps are
  reset.
- H4: Temporal split uses window index, not elapsed time, for split boundaries.
- H5: MSG seizure durations are imputed to 60 seconds.

## Medium Findings

- Duplicate postictal implementations.
- Silent fallback to 0.5 in some calibration paths.
- Tiny cohort splits not guarded.
- FAR behavior is stride-dependent.
- Documentation included a likely phantom arXiv reference.
- README/test-count documentation was stale.
- The word "tibia" appeared where "TinyML" or actual hardware wording was intended.

## Positive Findings

- SPH/SOP interval primitive is correct.
- Cycle and rule baseline runners are now split-safe in their main intended paths.
- `is_excluded` plumbing exists and is used by core metrics.
- The gate forbidding A100 and paper claims before manual audit is correct.

## Recommended Order

1. C1: make threshold sweeps split-safe and impossible to use as test tuning by default.
2. C2: add right-censoring of forecast horizons beyond recording end.
3. C3/M4: make empty reference scopes fail loudly.
4. C4/H1: make MSG event denominator and seizure-cluster policy explicit.
5. H2/H3: make leakage audit adversarial rather than reassuring.
6. Regenerate audit packets after the fixes.

## Phase R Rule

No M3/M4 work, A100 training, or paper-result claims until C1-C4 are closed and an advisor verdict
says M2 is closed.
