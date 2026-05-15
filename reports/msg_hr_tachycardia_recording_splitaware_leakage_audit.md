# MSG HR Tachycardia Prediction Leakage Audit

```text
EpiTwin-Open leakage audit
===========================

Patient overlap across splits: True (allowed only for temporal/within-patient analyses; strategy=temporal_recording_elapsed_time)
[{'patient_id': '1110', 'splits': ['test', 'train', 'val']}, {'patient_id': '1869', 'splits': ['test', 'train', 'val']}, {'patient_id': '1876', 'splits': ['test', 'train', 'val']}, {'patient_id': '1904', 'splits': ['test', 'train', 'val']}, {'patient_id': '1927', 'splits': ['test', 'train', 'val']}, {'patient_id': '1965', 'splits': ['test', 'train', 'val']}, {'patient_id': '1988', 'splits': ['test', 'train', 'val']}, {'patient_id': '2002', 'splits': ['test', 'train', 'val']}]
Recording overlap across splits: False (allowed only for temporal/within-recording analyses; strategy=temporal_recording_elapsed_time)
Duplicate window intervals: False
Duplicate recording time ranges: False
Postictal positive labels not excluded: False
Temporal ordering/overlap leakage: False
Feature normalization leakage: metadata present (['score_fit_split', 'threshold_source_split']); no test-scope fit metadata detected
Future-information feature leakage: requires manual feature audit
```

This audit applies to the regenerated HR tachycardia prediction table, which records `score_fit_split=train` and `threshold_source_split=val`.
