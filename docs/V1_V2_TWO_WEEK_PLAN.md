# EpiTwin-Open v1.0 / v2.0 Two-Week Plan

This plan converts the verified v0.1 scaffold into:

- v1.0: real-dataset-ready benchmark infrastructure.
- v2.0: first research-grade baseline/model package, A100-ready after human clearance.

The priority order is fixed: benchmark correctness, real-data artifacts, label audits, clinical metrics, simple baselines, then controlled small models. No A100 training is allowed before real labels, splits, random baseline, leakage audit, and manual seizure timeline inspection are clean.

## Day 0 - Verification And Baseline Freeze

Status: completed on 2026-05-15.

Deliverables:

- Verified environment sync, tests, lint, synthetic demo, report generation, and SSL smoke training.
- Created `reports/v0_1_verification.md`.
- Confirmed this workspace is not a Git repository, so branch/commit steps are blocked.

## Day 1 - Repository Hardening And CLI Standardization

Status: completed on 2026-05-15.

Goals:

- Add `lint`, `all-checks`, and explicit command docs.
- Make `RUN_THIS_FIRST.sh` print each step and fail clearly.
- Extend `.gitignore` for checkpoints, experiment outputs, `wandb`, and `mlruns`.
- Add `configs/default.yaml` if no central config exists.
- Create `docs/COMMANDS.md`.

Acceptance:

- A new user can verify the repo with one command.
- Direct `uv run` equivalents are documented for systems without `make`.

## Day 2 - Dataset Schema Layer

Status: completed on 2026-05-15.

Goals:

- Add canonical schemas for metadata, events, recordings, windows, modality availability, features, and predictions.
- Add validation helpers for required columns, null IDs, timestamps, and seizure interval sanity.
- Add mock/dry-run modes for dataset preparation scripts.

Acceptance:

- Mock SeizeIT2 and mock MSG paths write standardized parquet artifacts.
- Malformed input fails with clear errors.

## Days 3-4 - Dataset Parsers

Status: in progress. SeizeIT2 discovery and MSG HR/steps mock/CSV parsing are implemented for supported layouts.

SeizeIT2:

- Improve BIDS/OpenNeuro-like discovery for subjects, sessions, event files, sidecars, and modality manifests.
- Do not invent missing metadata.

My Seizure Gauge:

- Discover ZIPs or extracted folders.
- Parse seizure annotations and supported HR/steps CSV streams.
- Add hourly window support.

Acceptance:

- Both datasets have mock pipelines and dry-run summaries.

## Day 5 - Windowing And Labeling Production Pass

Status: partially complete. Label audit export is implemented and mock-verified; remaining work is broader production coverage checks on real recordings.

Goals:

- Add recording coverage checks.
- Add `scripts/audit_labels.py` to export seizure-centered timelines.
- Expand tests for half-open SPH/SOP boundaries and ictal/postictal overlap.

Acceptance:

- Human can inspect 5-10 seizure timelines from exported CSV.

## Day 6 - Metrics Production Pass

Goals:

- Strengthen event-level and alarm episode tests.
- Expand threshold sweep outputs with FAR/day, Time-in-Warning, sensitivity, Brier, and ECE.
- Document false-alarm association logic.

Acceptance:

- Reports distinguish event-level metrics from window-level calibration.

## Day 7 - v1.0 Release Candidate

Goals:

- Run all checks and create `reports/v1_0_release_candidate.md`.
- Add `docs/REAL_DATA_QUICKSTART.md` and `docs/HUMAN_LABEL_AUDIT_PROTOCOL.md`.

Acceptance:

- Professor demo runs without real data.
- Real dataset next commands are explicit.

## Days 8-14 - v2.0 Baselines And A100-Ready Package

Sequence:

1. Feature extraction layer for HR/ECG, ACC/GYR, EMG, and optional EEG summary features.
2. Config-driven baseline runner with deterministic outputs.
3. Modest TCN-small and GRU-small baselines.
4. EpiTwin-SSL v0.2 configs and smoke tests.
5. Validation-only alarm threshold selection.
6. Observable latent student and optional soft constraints.
7. v2.0 release-candidate docs and A100 launch checklist.

Acceptance:

- Synthetic/mock full benchmark works.
- A100 configs exist but are not launched without human clearance.
- No clinical claims are made from synthetic or mock results.
