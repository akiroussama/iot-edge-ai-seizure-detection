# Codex Phase R2 Remediation After Claude Audit

Date: 2026-05-15

Branch: `feature/epibench-forecast-v0.1`

PR: https://github.com/akiroussama/iot-edge-ai-seizure-detection/pull/1

## Scope

This file documents the Codex remediation pass triggered by the Claude Phase R audit summary
reported by the user. The full committed Claude report `17d298b` was not available in this
checkout or on `origin` when this pass started, so the work below targets the explicit findings
included in the user-provided audit summary.

No synthetic or MSG numbers below are clinical claims. They are software and methods audit
signals only.

## Audit Findings Addressed

### P0: Right-Censoring Excluded Confirmed Positive Windows

Claude reported that `src/labeling/sph_sop.py` excluded windows with incomplete future horizon even
when a seizure onset was already observed inside the SPH/SOP interval.

Change:

- `is_right_censored` still records that the full horizon extends past `recording_end`.
- `is_excluded` now excludes only `is_right_censored & ~forecast_label`.
- Confirmed positive windows remain valid unless they are ictal or postictal.

Test added:

- `test_right_censored_confirmed_positive_is_not_excluded`

Impact on local MSG SPH60/SOP1440 labels after regeneration:

| Quantity | Before Phase R2 | After Phase R2 |
| --- | ---: | ---: |
| Total windows | 49,596 | 49,577 |
| Valid windows | 4,854 | 7,919 |
| Excluded windows | 44,742 | 41,658 |
| Right-censored windows | 44,708 | 44,689 |
| Total positive windows | 3,781 | 3,781 |
| Valid positive windows | 260 | 3,325 |

The large jump in valid positives confirms Claude's P0 was active and materially invalidated the
previous MSG reports.

### C1: Threshold Sweep Safety Only Existed In CLI

Claude reported that `scripts/sweep_thresholds.py` was guarded, but the library functions in
`src.metrics.sweep` could still tune on test/all rows.

Change:

- Added `scope_predictions_for_threshold_sweep`.
- `threshold_sweep_table`, `sensitivity_at_fixed_far`, and
  `sensitivity_at_fixed_time_in_warning` now enforce split-safe sweep scope.
- A table with a `split` column must pass `sweep_filter='split=val'` or another calibration split.
- `split=test` is refused by default.
- A table with no `split` column is refused unless `allow_unsplit_exploratory=True`.
- CLI now delegates the safety check to the library rather than owning the only guard.

Tests added:

- library refuses unsplit threshold sweeps by default;
- library refuses `split=test` sweeps by default;
- valid sweeps record `sweep_filter` and `publishable_threshold_tuning`.

Validation-only MSG HR threshold sweep regenerated:

```text
output: reports/msg_hr_threshold_sweep_val.csv
sweep_filter: split=val
publishable_threshold_tuning: True
```

### C3: Rule Baselines Still Had Silent No-Alarm Paths

Claude reported remaining holes in rule-baseline degeneration.

Change:

- `ecg_tachycardia_score` now raises if `hr_mean` is missing.
- `acc_energy_score` now raises if `acc_energy` is missing.
- `generic_zscore_anomaly` now raises if requested feature columns are absent or if no numeric
  feature columns are available.
- `patient_specific_quantile_thresholds` raises if a patient has no finite calibration scores.
- `apply_patient_thresholds` raises if predictions contain patients without thresholds, instead of
  mapping to `NaN` and silently producing no alarms.

Tests added:

- missing HR feature fails;
- missing generic feature fails;
- missing patient-specific threshold fails.

### H3: Duplicate Recording Time Ranges Were Detected But Not Enforced

Claude reported that duplicate MSG recording ranges were detected but temporal splitting still
allowed them unless reviewers noticed the audit line.

Change:

- `temporal_split_per_patient` now fails closed on exact duplicate recording time ranges within a
  patient.
- `scripts/make_splits.py` exposes `--allow-duplicate-recording-time-ranges` only as a diagnostic
  override.
- MSG parser now has an explicit duplicate recording policy:
  - `error` by default;
  - `drop_exact` only when duplicated files are documented.
- Added `scripts/clean_msg_recordings.py` to resolve exact duplicates in an already processed
  recordings table without hiding the policy.

Local MSG duplicate resolution:

```text
input_recordings: 2070
output_recordings: 2068
duplicate_rows: 4
dropped_recordings: 2
policy: drop_exact
```

The duplicate rows were the two patient `2002` `(1)` segment copies previously flagged by the
leakage audit.

## Regenerated MSG Audit Artifacts

Commands were run from the Git checkout with copied local MSG processed data:

```bash
uv run python scripts/clean_msg_recordings.py \
  --recordings data/processed/msg/recordings.parquet \
  --out data/processed/msg/recordings.parquet \
  --duplicates-out reports/msg_duplicate_recordings_dropped.csv \
  --duplicate-recording-policy drop_exact

uv run python scripts/make_windows.py \
  --recordings data/processed/msg/recordings.parquet \
  --out data/processed/msg/windows_1h.parquet \
  --window-duration 1h \
  --stride 1h

uv run python scripts/label_windows.py \
  --windows data/processed/msg/windows_1h.parquet \
  --events data/processed/msg/events.parquet \
  --output data/processed/msg/labels_sph60_sop1440.parquet \
  --sph-minutes 60 \
  --sop-minutes 1440 \
  --postictal-exclusion-minutes 240

uv run python scripts/make_splits.py \
  --labels data/processed/msg/labels_sph60_sop1440.parquet \
  --out data/processed/msg/split_temporal_recording.parquet \
  --audit-out reports/msg_temporal_recording_leakage_audit.txt \
  --strategy temporal \
  --temporal-unit recording \
  --temporal-basis elapsed_time
```

Regenerated reports:

- `reports/msg_full_real_check/dataset_report.md`
- `reports/msg_full_real_check_coverable/dataset_report.md`
- `reports/msg_cycle_hour_recording_test_check/dataset_report.md`
- `reports/msg_hr_tachycardia_recording_splitaware_check/dataset_report.md`
- `reports/msg_event_coverage_summary.md`
- `reports/msg_full_audit_packet.md`
- `reports/msg_temporal_recording_leakage_audit.md`

## Current MSG Audit Numbers After P0 Fix

These are not paper results.

### Label Distribution

```text
total_windows: 49,577
valid_windows: 7,919
excluded_windows: 41,658
positive_windows_valid: 3,325
positive_fraction_valid: 0.419876
```

### Event Denominators

```text
source events: 768
matched events: 510
matched coverable events, full table: 436
matched coverable events, temporal-recording test split: 54
```

This supersedes the earlier Phase R statement that only 13 test events were coverable under
SPH60/SOP1440. That earlier statement was downstream of the P0 right-censoring bug.

### Baseline Audit Signals

Full random rate-matched, all source events:

```text
n_events: 768
n_forecasted: 256
sensitivity: 0.333333
FAR/day: 0.878899
TIW: 0.100013
Brier: 0.301153
ECE: 0.199545
```

Full random rate-matched, matched and coverable events:

```text
n_events: 436
n_forecasted: 256
sensitivity: 0.587156
FAR/day: 0.878899
TIW: 0.100013
```

Cycle-hour baseline, matched coverable temporal-recording test split:

```text
n_events: 54
n_forecasted: 3
sensitivity: 0.055556
FAR/day: 0.084626
TIW: 0.040197
Brier: 0.124915
ECE: 0.130521
```

HR tachycardia baseline, matched coverable temporal-recording test split:

```text
n_events: 54
n_forecasted: 46
sensitivity: 0.851852
FAR/day: 0.981664
TIW: 0.117772
Brier: 0.348331
ECE: 0.378230
score_fit_split: train
threshold_source_split: val
```

Interpretation: HR tachycardia remains an audit signal with poor calibration and high warning
burden, not a clinical result. It must be reviewed against seizure timelines and potential
wear-time/event-selection bias before being used in any claim.

## Leakage Audit Status

Temporal-recording split labels:

```text
Recording overlap across splits: False
Duplicate window intervals: False
Duplicate recording time ranges: False
Postictal positive labels not excluded: False
Temporal ordering/overlap leakage: False
Feature normalization leakage: UNVERIFIED_OR_FAILED
```

HR tachycardia predictions:

```text
Recording overlap across splits: False
Duplicate recording time ranges: False
Temporal ordering/overlap leakage: False
Feature normalization leakage: metadata present; no test-scope fit metadata detected
```

The label-only split audit still cannot verify feature fitting because labels do not carry
`score_fit_split` and `threshold_source_split`. Prediction tables must carry this metadata.

## Validation Commands

```bash
uv run --extra dev --extra torch python -m pytest -q
uv run --extra dev ruff check .
uv run python scripts/run_synthetic_demo.py
uv run --extra torch python scripts/train_epitwin_ssl.py --epochs 1 --batch-size 4
```

Observed status:

```text
95 tests passed
ruff: All checks passed
synthetic demo: completed
smoke training: completed one epoch
```

## Remaining Methodological Risks

1. The full Claude report `17d298b` still needs to be pushed or otherwise made visible so Codex can
   address any detailed findings not included in the user summary.
2. H1 cluster policy remains a decision: current reports document seizure-level metrics with
   clusters not collapsed.
3. C4 is visibility-improved, but matched wear-time subset policy remains a scientific decision.
4. MSG seizure ends are still all imputed at 60 seconds from onset-only annotations.
5. HR feature artifacts were relinked to corrected labels/splits from existing processed features;
   raw MSG data should be remounted or re-downloaded before any final baseline table.
6. Manual review of seizure-centered timelines remains mandatory.
7. A100 training remains blocked until labels, splits, random baseline, leakage audit, and manual
   seizure timeline inspection are clean.

## Advisor Checkpoint

Advisor-checkpoint: Phase R2 changes alter the right-censoring validity policy and materially
change MSG denominators. An advisor or Claude review must approve this policy before M2 can be
declared closed.
