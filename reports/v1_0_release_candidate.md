# EpiTwin-Open v1.0 Release-Candidate Status

Date: 2026-05-15

Status: partial release candidate.

## Passed

- Tests: 51 passed.
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

## Not Yet Complete

- Real SeizeIT2 data have not been mounted or validated.
- Real My Seizure Gauge data have not been mounted or validated.
- Real waveform decoding remains dataset-version specific.
- Feature extraction layer is not yet production complete.
- Baseline experiment runner is not yet config-driven.
- TCN/GRU research baseline configs are not yet complete.

## A100 Readiness

Not ready. A100 launch remains blocked until real labels, splits, random baseline, leakage audit, and manual timeline audit are clean.
