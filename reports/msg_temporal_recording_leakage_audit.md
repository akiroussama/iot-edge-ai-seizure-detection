# MSG Temporal Recording Leakage Audit

This report is generated from local MSG pipeline artifacts and is an audit aid, not a clinical
result.

Command:

```bash
uv run python scripts/make_splits.py \
  --labels data/processed/msg/labels_sph60_sop1440.parquet \
  --out data/processed/msg/split_temporal_recording.parquet \
  --audit-out reports/msg_temporal_recording_leakage_audit.txt \
  --strategy temporal \
  --temporal-unit recording
```

Observed split counts:

| split | windows |
| --- | ---: |
| train | 35627 |
| val | 4709 |
| test | 9260 |

Audit output:

```text
EpiTwin-Open leakage audit
===========================

Patient overlap across splits: True (allowed only for temporal/within-patient analyses; strategy=temporal_recording)
[{'patient_id': '1110', 'splits': ['test', 'train', 'val']}, {'patient_id': '1869', 'splits': ['test', 'train', 'val']}, {'patient_id': '1876', 'splits': ['test', 'train', 'val']}, {'patient_id': '1904', 'splits': ['test', 'train', 'val']}, {'patient_id': '1927', 'splits': ['test', 'train', 'val']}, {'patient_id': '1965', 'splits': ['test', 'train', 'val']}, {'patient_id': '1988', 'splits': ['test', 'train', 'val']}, {'patient_id': '2002', 'splits': ['test', 'train', 'val']}]
Recording overlap across splits: False (allowed only for temporal/within-recording analyses; strategy=temporal_recording)
Duplicate window intervals: False
Duplicate recording time ranges: True
Potential timestamp reset or duplicated recording intervals; temporal splits may be invalid. [{'patient_id': '2002', 'recording_id': '2002_1607691981_A029E3', 'recording_window_start': Timestamp('2020-12-11 13:06:31'), 'recording_window_end': Timestamp('2020-12-12 04:06:31')}, {'patient_id': '2002', 'recording_id': '2002_1607691981_A029E3 (1)', 'recording_window_start': Timestamp('2020-12-11 13:06:31'), 'recording_window_end': Timestamp('2020-12-12 04:06:31')}, {'patient_id': '2002', 'recording_id': '2002_1607987768_A029E3', 'recording_window_start': Timestamp('2020-12-14 23:16:18'), 'recording_window_end': Timestamp('2020-12-15 03:16:18')}, {'patient_id': '2002', 'recording_id': '2002_1607987768_A029E3 (1)', 'recording_window_start': Timestamp('2020-12-14 23:16:18'), 'recording_window_end': Timestamp('2020-12-15 03:16:18')}]
Postictal positive labels not excluded: False
Temporal ordering/overlap leakage: False
Feature normalization leakage: UNVERIFIED_OR_FAILED [{'status': 'unverified', 'reason': 'missing score_fit_split/threshold_source_split metadata'}]
Future-information feature leakage: requires manual feature audit
```

Interpretation:

- Patient overlap is expected for within-patient temporal forecasting.
- Recording overlap is false, so a parsed Empatica recording is not split across train/validation/test.
- Duplicate recording ranges exist for patient `2002`; this must be resolved before treating the
  temporal split as final.
- Split tables do not carry score-fit or threshold-selection metadata, so feature normalization
  remains unverified at the split-audit level. Prediction reports must carry that metadata.
