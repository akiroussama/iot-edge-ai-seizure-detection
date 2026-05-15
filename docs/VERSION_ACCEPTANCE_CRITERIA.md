# Version Acceptance Criteria

## v0.1 - Verified Scaffold

Status on 2026-05-15: pass.

Required:

- Tests pass.
- Lint passes.
- Synthetic demo runs.
- Report generation runs.
- SSL smoke training runs on CPU.
- SPH/SOP labeling, exclusions, metrics, leakage checks, and basic model scaffolding are present.

Not required:

- Real dataset parsing completion.
- Real clinical scores.
- A100 training.

## v1.0 - Real-Dataset-Ready Benchmark

Required:

- Canonical schema validation for metadata, events, recordings, windows, labels, modality availability, features, and predictions.
- Mock SeizeIT2 pipeline writes standardized parquet artifacts.
- Mock My Seizure Gauge pipeline writes standardized parquet artifacts.
- Real-mode parser failures are explicit when files are missing or unsupported.
- Window generation never crosses recording boundaries.
- SPH/SOP labels are tested for half-open interval behavior.
- Ictal and postictal windows are excluded by default.
- Patient-wise, temporal, and center-wise split logic exists.
- Leakage audit reports patient/recording overlap, duplicate windows, temporal overlap, and postictal contamination.
- Random rate-matched, cycle/rhythm placeholder, HR/ACC/EMG rule, and generic anomaly baselines are available or explicitly documented as pending.
- Reports include dataset summary, label distribution, baseline metrics, leakage audit, and human audit checklist.
- Synthetic/mock reports are clearly labeled as non-clinical.

Blocked until user provides data:

- Verified SeizeIT2 real artifacts.
- Verified My Seizure Gauge real artifacts.
- Manual seizure timeline audit.

## v2.0 - Research-Grade Baselines And A100-Ready Package

Required:

- v1.0 criteria pass.
- Feature extraction produces split-safe feature artifacts with missing-modality handling.
- Baseline experiment runner is config-driven and writes predictions, metrics, sweep tables, config copy, and run summary.
- TCN-small and GRU-small have CPU smoke tests and A100-ready configs.
- EpiTwin-SSL v0.2 supports missing modalities, modality dropout, masked reconstruction, future latent prediction, hazard/risk output, and uncertainty output.
- Alarm thresholds are selected on validation data only.
- Patient-specific thresholds and Time-in-Warning/FAR-constrained thresholds are available.
- Observable latent student supports full-modality teacher versus edge-modality student without forcing EEG-only hallucination.
- A100 launch checklist exists.
- Paper result templates exist.

Not acceptable:

- Accuracy as a primary metric.
- Random window split as default.
- Test-set threshold fitting.
- Synthetic/mock clinical claims.
- Large A100 training before label/split/random-baseline/leakage/manual-audit clearance.
