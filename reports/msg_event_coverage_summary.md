# MSG Event Coverage And Cluster Summary

This report is an audit aid, not a clinical result.

Interpretation rules:

- Events with no matched wearable recording must not silently enter final metric denominators.
- Patients with zero parsed recordings require source-data review before being treated as evaluable.
- Large seizure clusters require manual review of postictal exclusions and event-level association.

## Event Coverage

| patient_id | events_total | events_matched | events_unmatched | events_unknown | matched_fraction | recordings | recording_hours | first_seizure_start | last_seizure_start | manual_review_priority |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1110 | 31 | 16 | 15 | 0 | 0.516 | 146 | 4986.199 | 2020-08-19 10:14:29 | 2021-04-04 12:16:49 | high |
| 1219 | 31 | 0 | 31 | 0 | 0.000 | 0 | 0.000 | 2020-01-25 22:21:46 | 2020-08-26 00:06:58 | high |
| 1675 | 12 | 0 | 12 | 0 | 0.000 | 0 | 0.000 | 2019-07-21 17:46:28 | 2019-08-26 03:10:30 | high |
| 1869 | 26 | 20 | 6 | 0 | 0.769 | 182 | 4520.158 | 2020-01-21 23:33:53 | 2020-07-23 22:48:39 | high |
| 1876 | 44 | 35 | 9 | 0 | 0.795 | 204 | 4640.054 | 2020-01-01 22:48:37 | 2020-07-08 12:51:11 | high |
| 1904 | 31 | 20 | 11 | 0 | 0.645 | 220 | 7860.681 | 2020-02-12 07:50:12 | 2021-01-06 06:14:00 | high |
| 1927 | 11 | 11 | 0 | 0 | 1.000 | 323 | 7677.402 | 2020-01-11 23:39:43 | 2020-03-30 00:44:51 | routine |
| 1942 | 88 | 0 | 88 | 0 | 0.000 | 0 | 0.000 | 2020-01-02 12:41:01 | 2020-01-11 05:37:25 | high |
| 1965 | 241 | 210 | 31 | 0 | 0.871 | 366 | 8094.673 | 2020-01-02 08:14:17 | 2020-12-26 04:19:32 | high |
| 1988 | 197 | 158 | 39 | 0 | 0.802 | 290 | 6612.207 | 2020-01-02 10:40:48 | 2020-12-28 17:24:34 | high |
| 2002 | 56 | 40 | 16 | 0 | 0.714 | 339 | 6255.434 | 2020-01-10 23:30:47 | 2020-12-24 22:37:05 | high |

## Seizure Cluster Summary

| patient_id | events_total | clusters | clustered_events | max_cluster_size | mean_events_per_cluster | cluster_gap_minutes | manual_review_priority |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1110 | 31 | 12 | 27 | 7 | 2.583 | 240.000 | high |
| 1219 | 31 | 29 | 3 | 3 | 1.069 | 240.000 | routine |
| 1675 | 12 | 4 | 11 | 6 | 3.000 | 240.000 | high |
| 1869 | 26 | 22 | 7 | 3 | 1.182 | 240.000 | routine |
| 1876 | 44 | 33 | 20 | 3 | 1.333 | 240.000 | routine |
| 1904 | 31 | 15 | 24 | 6 | 2.067 | 240.000 | high |
| 1927 | 11 | 11 | 0 | 1 | 1.000 | 240.000 | routine |
| 1942 | 88 | 12 | 83 | 20 | 7.333 | 240.000 | high |
| 1965 | 241 | 221 | 37 | 3 | 1.090 | 240.000 | routine |
| 1988 | 197 | 119 | 113 | 6 | 1.655 | 240.000 | high |
| 2002 | 56 | 52 | 7 | 3 | 1.077 | 240.000 | routine |

Manual review should prioritize patients with low matched fractions and large clusters.