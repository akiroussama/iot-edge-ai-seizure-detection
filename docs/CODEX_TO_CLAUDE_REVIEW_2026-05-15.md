# Codex to Claude Code Review Handoff - EpiTwin-Open

Date: 2026-05-15

Repository: `EpiTwin-Open`

PR: https://github.com/akiroussama/iot-edge-ai-seizure-detection/pull/1

Branch: `feature/epibench-forecast-v0.1`

Latest pushed commit at original handoff: `f45f76b` (`Add human label audit packets`)

Continued autonomous work after the original handoff added a split-safe cycle baseline and
split-filtered report support. Review these additional files too:

```text
src/baselines/cycle_baseline.py
scripts/run_cycle_baseline.py
scripts/make_dataset_report.py
tests/test_cycle_baseline.py
tests/test_dataset_report.py
reports/msg_cycle_hour_test_check/dataset_report.md
```

## Review Request For Claude Code

Act as a strict biomedical ML reviewer and senior software architect. Do not praise the package.
Attack it for leakage, mislabeled forecasting windows, event/window metric confusion, postictal
contamination, calibration mistakes, threshold fitting on test data, overclaiming, and weak
reproducibility. Then propose concrete fixes.

The most important review question is not whether the code looks nice. It is whether this benchmark
can survive a serious seizure-forecasting methods review.

## Scientific Boundary

EpiTwin-Open must not claim that all seizures are predictable.

EpiTwin-Open must not claim to be the first wearable seizure-forecasting system. Nasseri et al.,
Epilepsia 2025, DOI `10.1111/epi.18466`, already reports ultra-long-term non-invasive wearable
seizure forecasting using HR/step data with EEG-confirmed seizures.

The defensible contribution is:

- open public-data benchmark infrastructure;
- leakage-safe SPH/SOP labels;
- explicit ictal/postictal exclusions;
- event-level clinical metrics;
- alarm-burden metrics: FAR/day and Time-in-Warning;
- calibration metrics: Brier and ECE;
- transparent baselines before deep models;
- forecastability/observability analysis over available modalities;
- clear separation of detection, early warning, short-horizon forecasting, and long-horizon forecasting.

No A100 training is allowed until real labels, splits, random baseline, leakage audit, and manual
seizure timeline inspection are clean.

## What Codex Did In This Work Session

This section reconstructs the last work session from git history, local artifacts, and pushed PR
comments.

### 1. Verified And Pushed The Core EpiTwin-Open Package

The pushed branch replaces the old IoT/Streamlit demo root with the EpiTwin-Open benchmark package.
This was intentional because the project direction changed to a publication-oriented wearable
seizure-risk forecasting benchmark.

Initial core package commit:

```text
cbf59a4 Build EpiTwin-Open benchmark infrastructure
```

The package includes:

- SPH/SOP labeling with half-open interval semantics;
- ictal and postictal exclusion flags;
- fixed-window generation;
- schema validation;
- event-level sensitivity;
- FAR/hour and FAR/day;
- Time-in-Warning;
- median lead time;
- Brier score;
- ECE;
- threshold sweeps;
- patient-wise, temporal, center-wise split utilities;
- leakage audit scaffolding;
- random rate-matched baseline;
- simple rule baselines;
- CPU-smoke EpiTwin-SSL model scaffold;
- hazard/risk head;
- docs, runbooks, report scripts, and tests.

Important staging problem discovered and fixed:

```text
70b6626 Restore dataset modules in pushed package
```

The first push clone accidentally excluded `src/datasets` and `configs/data` because the rsync
exclude rules used broad names like `--exclude data --exclude datasets`. This was fixed by using
anchored excludes such as `/data/` and `/datasets/`. Claude should check that this class of mistake
cannot recur in the release process.

### 2. Added Reproducible MSG Zenodo Downloader

Commit:

```text
9b8bf8d Add reproducible MSG Zenodo downloader
```

Added:

- `scripts/download_msg_zenodo.py`
- current Zenodo API support for record `17380899`;
- resumable `curl` download behavior;
- file filtering through `--include`;
- no hidden data downloads during tests.

The old GitHub S3 links from `seermedical/msg-2022` were not sufficient. The current Zenodo record
was used instead.

Downloaded locally to avoid filling the C drive:

```text
data/raw/msg -> /home/oakir/epitwin_data/msg/raw
```

Full local file list after download:

```text
Mayo_1110.zip
Mayo_1869.zip
Mayo_1876.zip
Mayo_1904.zip
Mayo_1927.zip
Mayo_1965.zip
Mayo_1988.zip
Mayo_2002.zip
SeizureTimesOnly.zip
SeizureTimesOnly/1219.txt
SeizureTimesOnly/1675.txt
SeizureTimesOnly/1942.txt
```

Raw data are not committed.

### 3. Implemented And Audited Recording-Wise Split For Single-Patient Smoke Checks

Commit:

```text
12ca0b9 Add recording-wise split audits for local SeizeIT2 checks
```

Reason:

The local SeizeIT2 check currently contains one subject (`sub-125`) and many recordings with dummy
or reset timestamps. A patient-wise split is impossible and a naive temporal split can share
recordings across splits or look misleading. A recording-wise split was added as a smoke-check tool
only.

Added:

- `src/splits/recording_split.py`
- `scripts/make_splits.py`
- `recording_wise` strategy
- tests in `tests/test_no_temporal_leakage.py`

Important boundary:

Recording-wise splits do not support prospective or patient-generalization claims. They only verify
that runs are not shared across train/validation/test in single-patient local checks.

Local SeizeIT2 recording-wise audit:

```text
Patient overlap across splits: True
Recording overlap across splits: False
Duplicate window intervals: False
Postictal positive labels not excluded: False
Temporal ordering/overlap leakage: not evaluated (strategy=recording_wise; use temporal splits for prospective claims)
```

### 4. Fixed Baseline Relabeling Bug

Commit:

```text
372efd7 Use audited labels for random baseline generation
```

Problem:

`scripts/run_baseline.py` previously accepted `--windows` and `--events`, then recomputed labels
internally. That was dangerous because real labels may have been generated with a non-default
postictal exclusion. Specifically, MSG long-horizon labels used `postictal_exclusion_minutes=240`,
while the baseline script defaulted to 60 minutes.

Fix:

- Added `--labels` to `scripts/run_baseline.py`.
- Real-data quickstart now uses `--labels`.
- Added CLI regression test proving excluded windows remain excluded.

Why this matters:

Prediction masks, Brier/ECE denominators, FAR denominators, and label distribution must all use the
same labeled-window table. Silent relabeling is a leakage/methodology risk.

### 5. Added MSG HR/ACC Feature Extraction And Transparent Rule Baselines

Commit:

```text
5167a1a Add MSG HR ACC feature and rule baselines
```

Added:

- `src/features/msg_empatica.py`
- `scripts/extract_msg_features.py`
- `scripts/run_rule_baseline.py`

The MSG feature extractor reads nested Empatica ZIP files one recording at a time and produces
per-window HR/ACC summary features without materializing all raw samples into one long table.

Supported modalities:

- `hr`
- `acc`

Transparent rule baselines:

- `hr_tachycardia`
- `acc_energy`
- `generic_zscore`

Important fix included:

Rule baseline calibration uses only windows with feature evidence. Windows with missing features or
`is_excluded=True` are forced to `alarm=False`.

Real-data smoke checks:

```bash
uv run python scripts/extract_msg_features.py \
  --raw-dir data/raw/msg \
  --windows data/processed/msg/labels_sph60_sop1440.parquet \
  --out /tmp/msg_features_smoke.parquet \
  --modalities hr \
  --max-recordings 3
```

Observed:

```text
rows=19964 before full refresh, feature_recordings_processed=3, hr_mean populated for 51 windows
```

HR+ACC smoke:

```text
feature_recordings_processed=1
hr_mean populated for 21 windows
acc_mean populated for 21 windows
```

### 6. Completed Full Local MSG Pipeline Check

Commit:

```text
2fc9428 Document full MSG pipeline check artifacts
```

After the MSG Zenodo downloads completed, the full local pipeline was rerun.

Commands run:

```bash
uv run python scripts/prepare_msg.py \
  --raw-dir data/raw/msg \
  --processed-dir data/processed/msg

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

uv run python scripts/audit_labels.py \
  --labels data/processed/msg/labels_sph60_sop1440.parquet \
  --events data/processed/msg/events.parquet \
  --out reports/msg_full_label_audit.csv \
  --minutes-before 180 \
  --minutes-after 240
```

Full local MSG preparation summary:

```text
metadata: 2070 rows
recordings: 2070 rows
events: 768 rows
modality_availability: 14506 rows
samples: 0 rows
matched events: 510
unmatched events: 258
```

Events by patient:

```text
1110: 31
1219: 31
1675: 12
1869: 26
1876: 44
1904: 31
1927: 11
1942: 88
1965: 241
1988: 197
2002: 56
```

Important interpretation:

The parser currently finds 768 seizure onsets and 510 matched onsets. These are local parser
artifacts requiring manual audit, not official publication statistics.

Labels:

```text
one-hour windows: 49,596
valid windows: 47,713
excluded windows: 1,883
valid positive windows: 3,325
ictal windows: 465
postictal windows: 1,875
```

Audit CSV:

```text
reports/msg_full_label_audit.csv
rows: 3,162
```

Generated but not committed because they are CSV/TXT artifacts:

```text
reports/msg_full_label_audit.csv
reports/msg_full_leakage_audit.txt
reports/msg_full_patient_wise_leakage_audit.txt
```

Committed markdown reports:

```text
reports/msg_full_real_check/dataset_report.md
reports/msg_hr_tachycardia_check/dataset_report.md
```

Random rate-matched TIW10 pipeline check:

```text
n_events: 510
n_forecasted: 251
sensitivity: 0.492156862745098
FAR/day: 0.9989730262192693
TIW: 0.09970029132521535
median lead: 37,835 s
Brier: 0.15899199121893864
ECE: 0.23332878165512572
```

HR tachycardia TIW10 pipeline check:

```text
n_events: 510
n_forecasted: 208
sensitivity: 0.40784313725490196
FAR/day: 0.8993775281369857
TIW: 0.09993083645966508
median lead: 29,407 s
Brier: 0.32550513453865654
ECE: 0.42924298158852886
```

Interpretation:

HR tachycardia underperforms the random rate-matched sanity baseline in this unaudited check. This
is useful negative benchmark evidence, not a clinical conclusion.

### 7. Tightened SOTA Framing

Commit:

```text
3f9b4b2 Tighten SOTA framing after current literature check
```

Updated:

- `docs/SOTA_REVIEW_2026.md`
- `docs/PUBLICATION_PROPOSAL.md`

Sources checked:

- SeizeIT2 Scientific Data 2025: https://www.nature.com/articles/s41597-025-05580-x
- MSG Zenodo record: https://zenodo.org/records/17380899
- Nasseri et al. Epilepsia 2025: https://doi.org/10.1111/epi.18466
- Journal of Neurology 2024 seizure forecast review/meta-analysis:
  https://link.springer.com/article/10.1007/s00415-024-12655-z
- ICLR 2024 wearable biosignal foundation models:
  https://proceedings.iclr.cc/paper_files/paper/2024/hash/0d99a8c048befb6dd6e17d7684adacac-Abstract-Conference.html
- PaPaGei PPG foundation model: https://arxiv.org/abs/2410.20542

Key correction:

EpiTwin-Open should not claim novelty as the first wearable seizure-forecasting system. The novelty
must be framed around an open, leakage-safe, clinically constrained benchmark and
forecastability/observability framework.

### 8. Added Human Label Audit Packets

Commit:

```text
f45f76b Add human label audit packets
```

Added:

- `src/reports/audit_packet.py`
- `scripts/make_audit_packet.py`
- `tests/test_audit_packet.py`

Generated and committed:

- `reports/seizeit2_sub125_audit_packet.md`
- `reports/msg_full_audit_packet.md`

Purpose:

The packets make manual label review feasible without opening long CSVs first. They group rows by
event, show state counts, and list:

- `window_end`
- `minutes_to_seizure`
- `forecast_label`
- `is_ictal`
- `is_postictal`
- `is_excluded`
- `audit_state`

Important observation:

The audit packets expose seizure-cluster edge cases where a window close to a future seizure can be
excluded because it overlaps ictal or postictal context from a previous seizure. This may be correct
under the current rules, but it is exactly the kind of case that must be manually reviewed before
training.

### 9. Added Split-Safe Hour-Of-Day Cycle Baseline

Added after the initial audit packet push:

```text
src/baselines/cycle_baseline.py
scripts/run_cycle_baseline.py
tests/test_cycle_baseline.py
```

Purpose:

MSG forecasting must be compared against a cycle/rhythm baseline, not only random and HR
tachycardia. The implemented baseline fits empirical patient/hour-of-day forecast-label risk on a
fit split only, then selects an alarm threshold on a validation split only.

Command used locally:

```bash
uv run python scripts/run_cycle_baseline.py \
  --split-labels data/processed/msg/split_temporal.parquet \
  --out data/processed/msg/cycle_hour_predictions_sph60_sop1440.parquet \
  --fit-split train \
  --threshold-split val \
  --target-tiw 0.1
```

Observed local output:

```text
threshold: 0.23266888314601855
global_prior: 0.07919717927854625
rows: 49,596
alarms: 4,689
```

The baseline still requires manual label audit before any claim.

### 10. Added Split-Filtered Dataset Reports

The report generator now supports:

```text
--prediction-filter split=test
--restrict-events-to-prediction-coverage
```

This avoids a common evaluation bug: filtering predictions to a split but still counting events that
could not possibly be forecasted by any selected prediction window.

Local MSG cycle test-split report:

```text
reports/msg_cycle_hour_test_check/dataset_report.md
```

Pipeline-check summary:

```text
events covered by selected test horizons: 54
forecasted events: 3
sensitivity: 0.0556
FAR/day: 0.2081
TIW: 0.1045
Brier: 0.0480
ECE: 0.0421
```

Interpretation:

This is not a clinical result. It suggests the simple hour-of-day cycle prior is conservative and
well-calibrated on this unaudited temporal-test slice, but weak in event sensitivity. Manual audit
and final split policy are still blocking.

## Validation Status

Latest local validation:

```bash
uv run python -m pytest -q
# 66 passed

uv run ruff check .
# All checks passed
```

Latest push-clone validation:

```bash
uv run --extra dev --extra torch python -m pytest -q
# 70 passed after event-coverage continuation

uv run --extra dev ruff check .
# All checks passed
```

GitHub Actions:

```text
workflow: tests
latest checked run number before this continuation: 24
status: success
commit: 29fd714
```

## Files Claude Should Review First

Highest priority:

```text
src/labeling/sph_sop.py
src/metrics/event_metrics.py
src/metrics/alarm_metrics.py
src/splits/leakage_checks.py
src/splits/temporal_split.py
src/splits/patient_split.py
src/splits/recording_split.py
scripts/make_splits.py
scripts/run_baseline.py
scripts/run_rule_baseline.py
scripts/run_cycle_baseline.py
scripts/make_dataset_report.py
src/baselines/cycle_baseline.py
src/features/msg_empatica.py
src/datasets/msg_loader.py
src/datasets/seizeit2_loader.py
src/reports/label_audit.py
src/reports/audit_packet.py
src/reports/event_coverage.py
```

Audit artifacts:

```text
reports/seizeit2_sub125_real_check/dataset_report.md
reports/msg_full_real_check/dataset_report.md
reports/msg_hr_tachycardia_check/dataset_report.md
reports/msg_cycle_hour_test_check/dataset_report.md
reports/seizeit2_sub125_audit_packet.md
reports/msg_full_audit_packet.md
reports/msg_event_coverage_summary.md
```

Docs:

```text
docs/SOTA_REVIEW_2026.md
docs/PUBLICATION_PROPOSAL.md
docs/REAL_DATA_QUICKSTART.md
docs/HUMAN_INTERVENTION_CHECKPOINTS.md
docs/VERSION_ACCEPTANCE_CRITERIA.md
PROJECT_STATUS.md
MANIFEST.md
```

## Known Risks And Open Methodology Questions

### Risk 1: Manual Label Audit Is Not Done

The code generated audit packets, but a human has not verified seizure onsets against source files.
No clinical claim is allowed.

Required human action:

```text
Open reports/seizeit2_sub125_audit_packet.md
Open reports/msg_full_audit_packet.md
Verify 5-10 seizure timelines per dataset
Record every parser or label issue before split freeze
```

### Risk 2: MSG Has Unmatched Events

Current local MSG parser:

```text
768 total onsets
510 matched
258 unmatched
```

I added a per-patient coverage and cluster report:

```text
reports/msg_event_coverage_summary.md
```

Key findings from the local full MSG files:

```text
1219, 1675, and 1942 have seizure annotations but zero parsed wearable recordings.
Several wearable patients still have unmatched events: 1110, 1869, 1876, 1904, 1965, 1988, 2002.
Only patient 1927 has 100% event-to-recording matching in the current parsed local artifacts.
Large clusters are visible, including max cluster size 20 for patient 1942.
```

Questions:

- Are unmatched events outside downloaded wearable segments?
- Are they from participants with only seizure annotations and no wearable ZIP?
- Are any unmatched events due to parser timestamp mistakes?
- Should final denominators exclude seizure-only patients, or should they be reported as a separate
  coverage limitation?

### Risk 3: Seizure Clusters

MSG audit packets show clustered seizures. Current logic can exclude windows that are inside the
postictal/ictal interval of one seizure even if they would be forecast-positive for a later seizure.

Questions:

- Is this clinically intended?
- Should clustered seizures be collapsed into seizure clusters for long-horizon MSG evaluation?
- Should event-level sensitivity count cluster-level forecasts instead of individual seizures?

### Risk 4: Temporal Split Shares Recordings

For MSG temporal splits, patient overlap is expected and temporal ordering is clean, but some
recordings span train/val/test boundaries. This is currently treated as allowed for
within-recording temporal analysis.

Questions:

- Should MSG primary evaluation be patient-wise or temporal?
- If temporal, should split boundaries be forced to recording boundaries?
- Should per-recording normalization be allowed only if fit on training portion?

### Risk 5: Normalization Leakage Is Not Machine-Checked Yet

Leakage audit currently states:

```text
Feature normalization leakage: not machine-checkable without fit metadata
Future-information feature leakage: requires manual feature audit
```

Needed:

- fit-transform artifacts with explicit train/val/test scope;
- checks that no scaler is fit on validation or test rows;
- pipeline metadata saved with every baseline/model run.

### Risk 6: Threshold Selection Needs Validation-Only Runner

Current random and HR rule reports use target TIW directly over the prediction table. This is useful
for pipeline checks but not final scientific evaluation.

Needed:

- config-driven experiment runner;
- fit threshold on validation split only;
- apply frozen threshold to test split;
- report train/val/test split names and threshold source.

### Risk 7: Cycle/Rhythm Baseline Needs Stronger Split-Frozen Evaluation

MSG publication framing requires a circadian/multiday baseline. I added a patient-specific
hour-of-day cycle baseline with training-only priors and validation-only thresholding, but this is
still a pipeline check until labels, coverage, and splits are manually audited.

Needed:

- decide whether the primary MSG task is temporal within-patient or patient-held-out;
- force split boundaries to recording boundaries if within-recording leakage is unacceptable;
- add day-of-week or multiday phase only if it can be justified without post-hoc tuning.

### Risk 8: SOTA Claim Must Remain Conservative

Nasseri et al. already provides wearable forecasting evidence. EpiTwin-Open can still be important,
but the claim must be:

```text
open leakage-safe benchmark + forecastability/observability framework
```

not:

```text
first wearable seizure forecasting
```

## Commands To Reproduce Current Local Checks

Synthetic/software:

```bash
uv run python -m pytest -q
uv run ruff check .
uv run python scripts/run_synthetic_demo.py
uv run python scripts/make_report.py --synthetic --out-dir reports
uv run python -u scripts/train_epitwin_ssl.py --epochs 1 --batch-size 1 --time-steps 4 --hidden-dim 4 --backbone gru
```

MSG full local pipeline:

```bash
uv run python scripts/prepare_msg.py \
  --raw-dir data/raw/msg \
  --processed-dir data/processed/msg

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

uv run python scripts/run_baseline.py \
  --labels data/processed/msg/labels_sph60_sop1440.parquet \
  --out data/processed/msg/random_tiw10_predictions_sph60_sop1440.parquet \
  --sph-minutes 60 \
  --sop-minutes 1440 \
  --tiw 0.1

uv run python scripts/extract_msg_features.py \
  --raw-dir data/raw/msg \
  --windows data/processed/msg/labels_sph60_sop1440.parquet \
  --out data/processed/msg/features_hr_sph60_sop1440.parquet \
  --modalities hr

uv run python scripts/run_rule_baseline.py \
  --features data/processed/msg/features_hr_sph60_sop1440.parquet \
  --out data/processed/msg/hr_tachycardia_predictions_sph60_sop1440.parquet \
  --rule hr_tachycardia \
  --target-tiw 0.1

uv run python scripts/run_cycle_baseline.py \
  --split-labels data/processed/msg/split_temporal.parquet \
  --out data/processed/msg/cycle_hour_predictions_sph60_sop1440.parquet \
  --fit-split train \
  --threshold-split val \
  --target-tiw 0.1
```

MSG reports:

```bash
uv run python scripts/make_dataset_report.py \
  --dataset-name MSG-local-full-download \
  --windows data/processed/msg/windows_1h.parquet \
  --labels data/processed/msg/labels_sph60_sop1440.parquet \
  --events data/processed/msg/events.parquet \
  --predictions data/processed/msg/random_tiw10_predictions_sph60_sop1440.parquet \
  --baseline-name random_rate_matched_tiw10 \
  --event-filter recording_match_status=matched \
  --out-dir reports/msg_full_real_check \
  --sph-minutes 60 \
  --sop-minutes 1440

uv run python scripts/make_dataset_report.py \
  --dataset-name MSG-local-full-download \
  --windows data/processed/msg/windows_1h.parquet \
  --labels data/processed/msg/labels_sph60_sop1440.parquet \
  --events data/processed/msg/events.parquet \
  --predictions data/processed/msg/hr_tachycardia_predictions_sph60_sop1440.parquet \
  --baseline-name hr_tachycardia_tiw10 \
  --event-filter recording_match_status=matched \
  --out-dir reports/msg_hr_tachycardia_check \
  --sph-minutes 60 \
  --sop-minutes 1440

uv run python scripts/make_dataset_report.py \
  --dataset-name MSG-local-full-download \
  --windows data/processed/msg/windows_1h.parquet \
  --labels data/processed/msg/labels_sph60_sop1440.parquet \
  --events data/processed/msg/events.parquet \
  --predictions data/processed/msg/cycle_hour_predictions_sph60_sop1440.parquet \
  --baseline-name cycle_hour_val_tiw10_testsplit \
  --event-filter recording_match_status=matched \
  --prediction-filter split=test \
  --restrict-events-to-prediction-coverage \
  --out-dir reports/msg_cycle_hour_test_check \
  --sph-minutes 60 \
  --sop-minutes 1440

uv run python scripts/summarize_event_coverage.py \
  --events data/processed/msg/events.parquet \
  --recordings data/processed/msg/recordings.parquet \
  --out-md reports/msg_event_coverage_summary.md \
  --out-coverage-csv reports/msg_event_coverage_summary.csv \
  --out-clusters-csv reports/msg_event_cluster_summary.csv \
  --cluster-gap-minutes 240 \
  --title "MSG Event Coverage And Cluster Summary"
```

Audit packets:

```bash
uv run python scripts/audit_labels.py \
  --labels data/processed/msg/labels_sph60_sop1440.parquet \
  --events data/processed/msg/events.parquet \
  --out reports/msg_full_label_audit.csv \
  --minutes-before 180 \
  --minutes-after 240

uv run python scripts/make_audit_packet.py \
  --audit reports/msg_full_label_audit.csv \
  --out reports/msg_full_audit_packet.md \
  --max-events 10 \
  --title "MSG Full Label Audit Packet"
```

## Exact Review Prompt For Claude Code

Claude, review EpiTwin-Open as a strict biomedical ML methods reviewer. Focus on:

1. SPH/SOP labeling correctness.
2. Ictal and postictal exclusion correctness.
3. Event-level metrics and false-alarm definitions.
4. FAR/day and Time-in-Warning denominators.
5. Whether random and rule baselines are being evaluated on excluded rows.
6. Whether threshold selection leaks test information.
7. Whether MSG event-to-recording matching can shift or drop events incorrectly.
8. Whether seizure clusters should be collapsed or treated as separate events.
9. Whether temporal/patient/recording splits are appropriate for each dataset.
10. Whether SOTA framing overclaims novelty.

Do not accept "tests pass" as sufficient. Identify concrete failure modes, missing tests, and
changes needed before A100 training or paper claims.
