# EpiTwin-Open project status

Generated package status:

- Benchmark scaffold: implemented.
- SPH/SOP labeling: implemented and tested.
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
- Current MSG random and HR tachycardia metrics are pipeline checks only. HR tachycardia underperforms the random rate-matched sanity baseline in the current unaudited full-download check.
- Real reports are pipeline checks only until manual seizure timeline audit, split freezing, and leakage audit are complete.
- `docs/SOTA_REVIEW_2026.md` and `docs/PUBLICATION_PROPOSAL.md` summarize the current publication framing and its evidence limits.
