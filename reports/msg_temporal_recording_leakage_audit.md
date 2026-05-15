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
Postictal positive labels not excluded: False
Temporal ordering/overlap leakage: False
Feature normalization leakage: not machine-checkable without fit metadata
Future-information feature leakage: requires manual feature audit
```

Interpretation:

- Patient overlap is expected for within-patient temporal forecasting.
- Recording overlap is false, so a parsed Empatica recording is not split across train/validation/test.
- This does not clear normalization leakage because future-information feature scope is not yet
  machine-checkable.
