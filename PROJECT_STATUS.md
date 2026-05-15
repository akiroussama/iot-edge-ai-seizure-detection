# EpiTwin-Open project status

Generated package status:

- Benchmark scaffold: implemented.
- SPH/SOP labeling: implemented and tested.
- Right-censoring: implemented for windows whose full SPH/SOP horizon exceeds `recording_end`; the
  real-data `label_windows.py` path now requires `recording_end` unless explicitly overridden for
  legacy diagnostics.
- Clinical metrics: implemented and tested.
- Leakage-aware splits: implemented and tested, including patient-wise, temporal, center-wise, and
  recording-wise smoke-check splits.
- Synthetic reports: generated.
- EpiTwin-SSL CPU smoke model: implemented and tested.
- Hazard head: implemented and tested.
- Edge observable student: implemented and tested.
- Calibration thresholding: implemented and tested.
- A100 real-data training: not run. Labels, splits, leakage audit, and manual seizure timeline review are not yet clean/frozen.
- Real SeizeIT2 parsing: BIDS-score `eventType/dateTime/recordingDuration` annotations are supported; local `sub-125` annotation import produced real pipeline-check labels.
- Real MSG parsing: Zenodo `Mayo_*.zip` nested Empatica manifests, patient onset text files, recording intervals, event-to-segment matching, and partial-download handling are supported. The current local full-download pass produced 2070 wearable segments, 768 seizure onsets, and 510 onsets matched to downloaded wearable segments.
- Real MSG transparent baseline support: HR window features are extractable from nested Empatica ZIPs without materializing all raw samples; the current local full-download HR extraction populated 49,562 / 49,596 one-hour windows.
- Transparent rule baselines are now split-aware when a `split` column is present: robust feature
  statistics and score normalization default to train rows, and alarm thresholds default to
  validation rows. Reports include prediction metadata with fit/threshold scope.
- Real MSG cycle baseline support: an hour-of-day patient-specific prior can be fit on the train
  split and thresholded on validation only. The current local temporal-test pipeline check is weak
  in event sensitivity and remains unaudited.
- Real MSG event-coverage audit support: `scripts/summarize_event_coverage.py` now reports
  per-patient matched/unmatched events, parsed recording hours, and seizure-cluster size. The
  current local report is `reports/msg_event_coverage_summary.md`.
- Temporal split support now includes `--temporal-unit recording`, which keeps every recording in a
  single split while preserving per-patient chronological ordering. This should be preferred when
  within-recording split boundaries would create preprocessing or artifact leakage risk.
- Temporal split boundaries now default to elapsed patient time rather than row/recording counts.
  The old count-based behavior requires explicit `--temporal-basis count`.
- Phase R audit remediation has started from `docs/CLAUDE_REVIEW_2026-05-15.md`. C1-C4 are now
  guarded in code, but the advisor has not yet declared M2 closed.
- Leakage audit now flags missing fit-scope metadata as `UNVERIFIED_OR_FAILED` and detects duplicate
  recording time ranges that can invalidate temporal assumptions.

Verified test status:

```text
Run `uv run python -m pytest -q` for the current count.
```

Next human action:

1. Manually audit `reports/seizeit2_sub125_label_audit.csv` and `reports/msg_full_label_audit.csv`.
2. Compare source seizure annotations against 5-10 exported seizure-centered timelines per dataset.
3. Freeze patient/temporal splits only after the audit is clean.
4. Rerun baselines and leakage audit after any parser or label correction before A100 training.

Known limitations:

- Current SeizeIT2 local run uses one downloaded/local subject and fetched annotation TSVs; it is not a cohort result.
- Recording-wise splits are only for single-patient/run-disjoint smoke checks. They do not support
  prospective or patient-generalization claims.
- Current MSG local run uses the full Zenodo file list available through the downloader, but 258 seizure onsets are still unmatched to downloaded wearable segments and are excluded from metric denominators only when explicitly filtered.
- After right-censoring SPH60/SOP1440 horizons against parsed Empatica recording ends, only 4,854
  / 49,596 MSG one-hour windows remain valid; 44,708 windows are right-censored. This is a major
  feasibility warning for 24-hour SOP evaluation on per-segment wearable files.
- Current MSG temporal-recording split audit flags duplicate recording time ranges for patient
  `2002`, including duplicated recording IDs with ` (1)` suffixes. This must be resolved before
  split freeze.
- The current MSG temporal-recording elapsed-time split has 33,853 train windows, 5,415 validation
  windows, and 10,328 test windows.
- MSG patients 1219, 1675, and 1942 currently have seizure annotations but zero parsed wearable
  recordings in the local artifacts; they require source-data review before being treated as
  evaluable forecast events.
- Current MSG random, cycle, and HR tachycardia metrics are pipeline checks only. Denominators now
  explicitly report source events, matched events, and prediction-coverable events.
- MSG seizure end times are onset-only imputations in the current public annotation path; reports
  now expose `seizure_end_imputed_events=768` and `imputed_duration_seconds_values=60.0` instead of
  treating seizure duration as measured clinical ground truth.
- The split-aware HR tachycardia check uses train-fitted score statistics and validation-selected
  thresholds, but remains unaudited and should not be compared as a final result.
- Current MSG cycle baseline metrics are split-filtered pipeline checks only; do not compare them
  as final paper results until split policy and timeline audit are frozen.
- Real reports are pipeline checks only until manual seizure timeline audit, split freezing, and leakage audit are complete.
- `docs/SOTA_REVIEW_2026.md` and `docs/PUBLICATION_PROPOSAL.md` summarize the current publication framing and its evidence limits.
