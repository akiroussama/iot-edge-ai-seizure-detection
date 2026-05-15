# EpiTwin-Open project status

Generated package status:

- Benchmark scaffold: implemented.
- SPH/SOP labeling: implemented and tested.
- Clinical metrics: implemented and tested.
- Leakage-aware splits: implemented and tested.
- Synthetic reports: generated.
- EpiTwin-SSL CPU smoke model: implemented and tested.
- Hazard head: implemented and tested.
- Edge observable student: implemented and tested.
- Calibration thresholding: implemented and tested.
- A100 real-data training: not run. Labels, splits, leakage audit, and manual seizure timeline review are not yet clean/frozen.
- Real SeizeIT2 parsing: BIDS-score `eventType/dateTime/recordingDuration` annotations are supported; local `sub-125` annotation import produced real pipeline-check labels.
- Real MSG parsing: Zenodo `Mayo_*.zip` nested Empatica manifests, patient onset text files, recording intervals, event-to-segment matching, and partial-download handling are supported.

Verified test status:

```text
Run `uv run python -m pytest -q` for the current count.
```

Next human action:

1. Finish MSG Zenodo downloads and rerun `scripts/prepare_msg.py`.
2. Manually audit `reports/seizeit2_sub125_label_audit.csv` and `reports/msg_partial_label_audit.csv`.
3. Freeze patient/temporal splits only after the audit is clean.
4. Rerun random baselines and leakage audit before any A100 training.

Known limitations:

- Current SeizeIT2 local run uses one downloaded/local subject and fetched annotation TSVs; it is not a cohort result.
- Current MSG run is partial because the Zenodo download is still in progress; unmatched seizure onsets are excluded from metric denominators only when explicitly filtered.
- Real reports are pipeline checks only until manual seizure timeline audit, split freezing, and leakage audit are complete.
- `docs/SOTA_REVIEW_2026.md` and `docs/PUBLICATION_PROPOSAL.md` summarize the current publication framing and its evidence limits.
