# Codex To Claude Code Review - Phase R Remediation

Generated: 2026-05-15T20:39:19+02:00  
Repository: `akiroussama/iot-edge-ai-seizure-detection`  
Branch: `feature/epibench-forecast-v0.1`  
PR: https://github.com/akiroussama/iot-edge-ai-seizure-detection/pull/1

## Review Request

Claude Code, please review this repository as a strict biomedical ML methods reviewer. This is not a
request for encouragement. The goal is to decide whether Phase R has actually closed the audit
blockers or only added another layer of plumbing.

Focus on whether the benchmark is now harder to misuse:

1. Can threshold tuning still leak test information?
2. Are right-censored SPH/SOP horizons excluded correctly?
3. Can rule baselines still silently degrade to no alarms?
4. Are MSG event denominators honest and consistent?
5. Does leakage audit now fail usefully instead of reassuring falsely?
6. Are temporal splits now based on elapsed patient time rather than window counts?
7. Are onset-only MSG seizure durations clearly treated as imputed, not measured?
8. What still prevents M2 from being marked closed?

Do not accept "tests pass" as sufficient. Try to break the assumptions.

## Current Verdict From Codex

Phase R made the benchmark substantially safer, but M2 is not closed yet.

The code now fails closed for the four critical findings from the review, and it exposes several
previously hidden methodological problems. However, the right-censoring and duplicate-recording
audits revealed that MSG SPH60/SOP1440 is much less straightforward than the earlier reports made it
look. The current artifacts are still audit artifacts only, not clinical results and not paper
results.

A100 remains blocked. M3/M4 remains blocked.

## Source Review Preserved

The chat-provided Claude review summary was preserved in:

```text
docs/CLAUDE_REVIEW_2026-05-15.md
```

It recorded:

- 4 critical findings: C1-C4.
- 5 high findings: H1-H5.
- Several medium/doc findings.
- The Phase R rule: no M3/M4 or A100 until C1-C4 are closed and advisor says M2 is closed.

Important note: the user also mentioned an adjusted `CODEX_PLAYBOOK_12_WEEKS.md`, but that file was
not present in this checkout when I searched the workspace. I followed the user-provided summary and
the preserved Claude review. If the playbook is expected to be source-controlled, it should be added
before the next phase.

## Commits Since The Prior Handoff

The relevant commits on this branch are:

```text
f45c3aa Expose imputed MSG seizure durations
8139bde Split temporal folds by elapsed time
4345e08 Make leakage audit adversarial
df64c9b Remediate critical benchmark audit findings
b662aeb Refresh publication proposal SOTA boundaries
841dc65 Make rule baselines split-aware
9bb929c Add recording-boundary temporal splits
1976b95 Add MSG event coverage audit summary
29fd714 Add Claude review handoff and cycle baseline
```

The Phase R remediation proper starts at `df64c9b` and continues through `f45c3aa`.

## Validation Status

Local validation before the latest pushes:

```bash
uv run --extra dev --extra torch python -m pytest -q
uv run --extra dev ruff check .
```

Latest local result:

```text
88 tests collected/passing
Ruff: all checks passed
```

GitHub Actions status observed:

```text
tests #40: success on f45c3aa58f578ae88a6b4fe050bdf937c0777cf0
```

## Phase R Remediation Details

### C1 - Threshold Tuning On Test

Original problem:

```text
scripts/sweep_thresholds.py swept thresholds over --predictions with no split concept.
This allowed threshold tuning directly on test predictions.
```

What changed:

- `scripts/sweep_thresholds.py` now checks the sweep scope before computing metrics.
- If predictions contain `split`, a sweep must pass `--sweep-filter`.
- `--sweep-filter split=test` is refused by default.
- `--allow-test-sweep` exists only as an explicit non-publishable diagnostic override.
- Tables without split metadata are refused unless `--allow-unsplit-exploratory` is passed.
- Sweep outputs now include:
  - `sweep_filter`
  - `event_filter`
  - `publishable_threshold_tuning`
  - `falsifiability`

Files changed:

```text
scripts/sweep_thresholds.py
tests/test_threshold_sweep_cli.py
docs/COMMANDS.md
```

Tests added:

- no split filter with split metadata fails;
- `split=test` sweep fails by default;
- `split=val` sweep succeeds and records scope metadata.

Falsifiability:

This fix is false if Claude can run a threshold sweep over a table containing `split` without
specifying a calibration/validation filter, or if `split=test` is accepted without explicit override.

### C2 - No Right Censoring

Original problem:

```text
Windows whose horizon extends beyond recording end were counted as true negatives.
For MSG SPH60/SOP1440 this is huge because many Empatica recordings are shorter than the full horizon.
```

What changed:

- `generate_fixed_windows(...)` now carries `recording_start` and `recording_end` into window rows.
- `label_forecast_windows(...)` computes `is_right_censored`.
- `is_right_censored=True` when:

```text
window_end + SPH + SOP > recording_end
```

- right-censored rows are included in `is_excluded`.
- `scripts/label_windows.py` requires `recording_end` by default.
- Missing `recording_end` now raises unless `--allow-missing-recording-end` is passed for legacy
  diagnostics.

Files changed:

```text
src/preprocessing/windowing.py
src/labeling/sph_sop.py
scripts/label_windows.py
tests/test_labeling_edge_cases.py
tests/test_windowing.py
```

Tests added:

- a horizon beyond `recording_end` is right-censored and excluded;
- real-data label path can fail loudly when `recording_end` is missing;
- generated windows carry recording boundary metadata.

MSG impact:

After regenerating MSG SPH60/SOP1440 labels:

```text
total windows: 49,596
valid windows: 4,854
excluded windows: 44,742
right-censored windows: 44,708
positive windows: 260
```

This invalidates earlier comparisons with pre-right-censoring MSG reports.

Falsifiability:

This fix is false if a real-data labeling command can silently produce labels without `recording_end`
or if `window_end + SPH + SOP > recording_end` remains usable as a negative training/evaluation row.

### C3 - Silent Degeneration For Held-Out Patients

Original problem:

```text
Rule baselines could return zeros when reference rows were empty, leading to silent never-alarm
behavior on held-out patients.
```

What changed:

- `robust_zscore(...)` raises on empty reference rows.
- `normalize_score(...)` raises on empty reference rows.
- `scripts/run_rule_baseline.py` raises when threshold split has no valid evidence rows.
- No-alarm fallback is no longer allowed as an implicit success path.

Files changed:

```text
src/baselines/simple_rules.py
scripts/run_rule_baseline.py
tests/test_features.py
```

Tests added:

- held-out patient with no train reference rows raises;
- normalization with empty reference mask raises;
- split-aware rule baseline records `score_fit_split=train` and `threshold_source_split=val`.

Falsifiability:

This fix is false if a rule baseline can produce all-zero scores or no alarms because the reference
scope is empty without raising an explicit error.

### C4 - Biased MSG Matched Subset And Inconsistent Denominators

Original problem:

```text
MSG recording_match_status=matched is a biased wear-time subset, and reports used inconsistent
event denominators.
```

What changed:

- `scripts/make_dataset_report.py` now requires `--acknowledge-event-filter-bias` when using:

```text
--event-filter recording_match_status=matched
```

- Reports now include an `Event Denominator` table with:
  - `events_source_total`
  - `events_after_filter`
  - `events_used_for_metrics`
  - `event_filter`
  - `prediction_filter`
  - `restricted_to_prediction_coverage`
  - explicit matched-subset warning
  - cluster policy

Files changed:

```text
scripts/make_dataset_report.py
tests/test_dataset_report.py
docs/REAL_DATA_QUICKSTART.md
docs/COMMANDS.md
reports/msg_full_real_check/dataset_report.md
reports/msg_full_real_check_coverable/dataset_report.md
reports/msg_cycle_hour_recording_test_check/dataset_report.md
reports/msg_hr_tachycardia_recording_splitaware_check/dataset_report.md
```

Current MSG denominator facts:

```text
source events: 768
matched events: 510
unmatched events: 258
patients with seizure annotations but zero parsed wearable recordings: 1219, 1675, 1942
```

For right-censored SPH60/SOP1440:

```text
full-table matched coverable events: 78
test split matched coverable events: 13
```

Falsifiability:

This fix is false if a report can use the matched subset without acknowledging bias, or if final
metrics can be read without knowing whether the denominator is source events, matched events, or
prediction-coverable matched events.

### H1 - Seizure Clusters

Original problem:

```text
Seizure clusters may put structurally non-forecastable seizures in the denominator.
```

What changed:

- `reports/msg_event_coverage_summary.md` summarizes cluster counts and max cluster sizes.
- Dataset reports now expose cluster policy in `Event Denominator`.
- Current policy is explicitly:

```text
seizure_level_metrics_clusters_not_collapsed
```

This is not a final scientific decision. It is an explicit placeholder requiring advisor review.

Key MSG cluster warning:

```text
patient 1942: max cluster size 20 under 240-minute onset-gap definition
```

Review question:

Should the primary MSG analysis be seizure-level, cluster-level, or both?

### H2 - Leakage Audit False Assurance

Original problem:

```text
Leakage audit printed static lines such as "not machine-checkable", which looked like a clean check.
```

What changed:

- `leakage_audit(...)` now calls `check_fit_scope_metadata(...)`.
- If fit metadata is absent, audit reports:

```text
Feature normalization leakage: UNVERIFIED_OR_FAILED
```

- If `score_fit_split=test` appears, it is flagged.
- Train/validation metadata passes this specific metadata check.

Files changed:

```text
src/splits/leakage_checks.py
tests/test_no_temporal_leakage.py
reports/msg_temporal_recording_leakage_audit.md
```

Falsifiability:

This fix is false if leakage audit reports normalization as clean without metadata, or if test-scope
fit metadata is not flagged.

### H3 - Reset Or Duplicated Recording Timestamps

Original problem:

```text
Temporal splits assumed timestamps were meaningful and monotonic. Reset or duplicated recording
time ranges could slip through.
```

What changed:

- Added `check_duplicate_recording_time_ranges(...)`.
- Leakage audit now flags repeated `(patient_id, recording_window_start, recording_window_end)`
  across different recording IDs.

Current MSG finding:

```text
Duplicate recording time ranges: True
patient 2002:
  2002_1607691981_A029E3
  2002_1607691981_A029E3 (1)
  2002_1607987768_A029E3
  2002_1607987768_A029E3 (1)
```

Interpretation:

This may be duplicate archives, parser duplication, or valid repeated files. It must be resolved
before split freeze.

Review question:

Should duplicated MSG recording ranges be de-duplicated by exact interval, treated as separate
recordings, or excluded pending source review?

### H4 - Temporal Split By Window Count

Original problem:

```text
Temporal split boundaries were based on row/recording counts, not elapsed time. Dense early windows
could dominate fold assignment.
```

What changed:

- `temporal_split_per_patient(...)` now defaults to:

```text
split_basis="elapsed_time"
```

- `scripts/make_splits.py` now exposes:

```text
--temporal-basis elapsed_time|count
```

- legacy count basis is available only as explicit diagnostic behavior.
- audit strategy labels include basis, e.g.:

```text
temporal_recording_elapsed_time
```

Current MSG elapsed-time recording split:

```text
train: 33,853 windows
val: 5,415 windows
test: 10,328 windows
```

Files changed:

```text
src/splits/temporal_split.py
scripts/make_splits.py
tests/test_no_temporal_leakage.py
docs/COMMANDS.md
docs/REAL_DATA_QUICKSTART.md
```

Falsifiability:

This fix is false if default temporal splits still use row count, or if dense sampling can move the
chronological split boundary away from elapsed-time fractions.

### H5 - MSG Seizure Durations Imputed

Original problem:

```text
MSG seizure_end was onset + 60 seconds, but reports could make that look like measured clinical
duration.
```

What changed:

- Parser already had:
  - `seizure_end_imputed=True`
  - `imputed_duration_seconds=60`
- Reports now expose this in an `Event Annotation` table.

Current MSG annotation status:

```text
events_source_total: 768
seizure_end_imputed_events: 768
seizure_end_imputed_fraction: 1.0
imputed_duration_seconds_values: 60.0
```

Files changed:

```text
scripts/make_dataset_report.py
tests/test_dataset_report.py
reports/msg_full_real_check/dataset_report.md
reports/msg_full_real_check_coverable/dataset_report.md
reports/msg_cycle_hour_recording_test_check/dataset_report.md
reports/msg_hr_tachycardia_recording_splitaware_check/dataset_report.md
```

Review question:

Should MSG postictal exclusion anchor to the imputed seizure end, or should onset-only datasets use
an onset-anchored exclusion policy?

## Regenerated Real-Data Audit Artifacts

These files were regenerated after Phase R changes:

```text
reports/msg_full_real_check/dataset_report.md
reports/msg_full_real_check_coverable/dataset_report.md
reports/msg_cycle_hour_recording_test_check/dataset_report.md
reports/msg_hr_tachycardia_recording_splitaware_check/dataset_report.md
reports/msg_temporal_recording_leakage_audit.md
reports/msg_full_audit_packet.md
```

The CSV outputs are ignored by `.gitignore` and are local working artifacts, not review artifacts.

## Current MSG Pipeline-Check Numbers

These are not clinical results and not paper results.

### Random Rate-Matched, Right-Censored, Coverable Denominator

Report:

```text
reports/msg_full_real_check_coverable/dataset_report.md
```

Summary:

```text
n_events: 78
n_forecasted: 36
sensitivity: 0.4615
FAR/day: 1.4141
TIW: 0.0999
Brier: 0.1529
ECE: 0.2438
```

### Cycle Hour Baseline, Right-Censored, Elapsed-Time Test Split

Report:

```text
reports/msg_cycle_hour_recording_test_check/dataset_report.md
```

Summary:

```text
n_events: 13
n_forecasted: 9
sensitivity: 0.6923
FAR/day: 1.3593
TIW: 0.2117
Brier: 0.0399
ECE: 0.0553
```

Warning:

The target TIW was 0.1 on validation, but test TIW is 0.2117. This is not a failure of split safety,
but it is clinically important and must be reported.

### HR Tachycardia, Train-Fit/Val-Threshold, Right-Censored, Elapsed-Time Test Split

Report:

```text
reports/msg_hr_tachycardia_recording_splitaware_check/dataset_report.md
```

Summary:

```text
n_events: 13
n_forecasted: 11
sensitivity: 0.8462
FAR/day: 1.4930
TIW: 0.1105
Brier: 0.4132
ECE: 0.6040
score_fit_split: train
threshold_source_split: val
```

Warning:

These numbers are based on only 13 prediction-coverable matched test events after right-censoring.
They are audit signals only. They are not stable enough for a paper claim.

## Files Claude Should Review First

Critical code:

```text
scripts/sweep_thresholds.py
scripts/label_windows.py
scripts/make_dataset_report.py
scripts/run_rule_baseline.py
scripts/make_splits.py
src/labeling/sph_sop.py
src/preprocessing/windowing.py
src/baselines/simple_rules.py
src/splits/leakage_checks.py
src/splits/temporal_split.py
src/datasets/msg_loader.py
```

Critical tests:

```text
tests/test_threshold_sweep_cli.py
tests/test_labeling_edge_cases.py
tests/test_dataset_report.py
tests/test_features.py
tests/test_no_temporal_leakage.py
tests/test_windowing.py
```

Critical reports:

```text
reports/msg_full_real_check_coverable/dataset_report.md
reports/msg_temporal_recording_leakage_audit.md
reports/msg_cycle_hour_recording_test_check/dataset_report.md
reports/msg_hr_tachycardia_recording_splitaware_check/dataset_report.md
reports/msg_event_coverage_summary.md
reports/msg_full_audit_packet.md
```

## Commands To Reproduce Main Checks

Software checks:

```bash
uv run --extra dev --extra torch python -m pytest -q
uv run --extra dev ruff check .
```

MSG right-censored labels:

```bash
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
```

MSG elapsed-time temporal recording split:

```bash
uv run python scripts/make_splits.py \
  --labels data/processed/msg/labels_sph60_sop1440.parquet \
  --out data/processed/msg/split_temporal_recording.parquet \
  --audit-out reports/msg_temporal_recording_leakage_audit.txt \
  --strategy temporal \
  --temporal-unit recording \
  --temporal-basis elapsed_time
```

Validation-only threshold sweep:

```bash
uv run python scripts/sweep_thresholds.py \
  --predictions data/processed/msg/hr_tachycardia_recording_splitaware_predictions_sph60_sop1440.parquet \
  --events data/processed/msg/events.parquet \
  --output reports/msg_hr_threshold_sweep_val.csv \
  --sweep-filter split=val \
  --event-filter recording_match_status=matched \
  --sph-minutes 60 \
  --sop-minutes 1440 \
  --steps 11
```

## Remaining Blockers Before M2 Closure

1. Advisor/Claude must verify C1-C4 fixes are genuinely closed.
2. Patient `2002` duplicate recording ranges must be resolved.
3. MSG onset-only postictal policy must be decided.
4. Cluster-level vs seizure-level event sensitivity must be decided.
5. Manual timeline audit remains mandatory for MSG and SeizeIT2.
6. SeizeIT2 is still only a local `sub-125` check, not a cohort.
7. Normalization/fit metadata is now checked where present, but future model pipelines must carry
   the same metadata.
8. A100 remains blocked.

## Exact Questions For Claude

Please answer directly:

1. Does `scripts/sweep_thresholds.py` now prevent publishable threshold tuning on test by default?
2. Is `is_right_censored` correctly defined and propagated into `is_excluded`?
3. Should right-censored rows keep `forecast_label=True` for transparency, or should labels be nulled?
4. Is `--allow-missing-recording-end` too permissive, even as a legacy/debug flag?
5. Is raising on empty patient reference rows the right behavior for held-out patients, or should the
   baseline fall back to a pre-registered global reference/abstention policy?
6. Is `recording_match_status=matched` bias sufficiently explicit in reports?
7. Should final MSG metrics use all matched events, prediction-coverable matched events, or both?
8. Should seizure clusters be collapsed for MSG long-horizon forecasting?
9. Is elapsed-time temporal splitting the correct default for MSG?
10. Should duplicate patient `2002` recordings be de-duplicated, excluded, or manually inspected first?
11. Should MSG postictal windows be computed from imputed seizure end or onset-only policy?
12. What still prevents the advisor verdict "M2 closed"?

## Bottom Line

Phase R turned several silent unsafe paths into explicit failures or explicit warnings. The biggest
scientific finding is negative but valuable: after right-censoring, MSG SPH60/SOP1440 has far fewer
valid forecast windows and only a small number of prediction-coverable matched test events. This may
force a horizon rethink or a much stricter coverage definition before any publication table.

No clinical claim is currently allowed.

No A100 training is allowed.

No M3/M4 work should start until this file and the Phase R commits are reviewed and advisor marks M2
closed.
