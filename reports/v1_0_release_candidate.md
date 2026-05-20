# EpiTwin-Open v1.0 Release-Candidate Status

Date: 2026-05-16

Status: partial release candidate.

## Passed

- Tests: 99 passed at the Phase R3 checkpoint.
- Ruff: passed.
- First-run script: passed.
- Synthetic demo: passed.
- Synthetic report generation: passed.
- Mock SeizeIT2 artifacts: passed.
- Mock My Seizure Gauge artifacts: passed.
- Label audit export: passed.
- Threshold sweep table: passed.

## Implemented

- CLI hardening and command docs.
- Canonical schemas and validation helpers.
- Mock dataset artifact generation.
- SeizeIT2 BIDS-like event/recording/modality discovery.
- MSG seizure metadata, ZIP manifest, and HR/steps CSV parsing.
- Label audit CSV export.
- Threshold sweep table with sensitivity, FAR/day, TIW, lead time, Brier, and ECE.
- SOTA snapshot and publication proposal docs.
- Split-safe threshold sweeps enforced in library code, not only CLI code.
- Right-censored confirmed positives preserved; right-censored unknown negatives excluded.
- MSG onset-only postictal policy exposed with `--postictal-anchor seizure_start`.
- Cluster-level first-event metric reports available alongside seizure-level reports.

## Not Yet Complete

- Real SeizeIT2 cohort data have not been mounted or validated beyond the local `sub-125` check.
- Real My Seizure Gauge labels/reports are local audit artifacts and are not manually validated.
- Real waveform decoding remains dataset-version specific.
- Feature extraction layer is not yet production complete.
- Baseline experiment runner is not yet config-driven.
- TCN/GRU research baseline configs are not yet complete.
- Advisor/Claude has not yet declared M2 closed.

## A100 Readiness

Not ready. A100 launch remains blocked until real labels, splits, random baseline, leakage audit, and manual timeline audit are clean.
