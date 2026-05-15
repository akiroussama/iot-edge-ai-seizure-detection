# SeizeIT2 sub-125 Label Audit Packet

This packet is for manual label audit only. It is not a clinical result.

Checklist for each event:

- Confirm source seizure onset/end.
- Confirm forecast positives satisfy `[window_end + SPH, window_end + SPH + SOP)`.
- Confirm ictal windows are excluded.
- Confirm postictal windows are excluded.
- Record any parser or annotation issue before training.

## Event 1

- Patient: `sub-125`
- Recording: `sub-125_ses-01_task-szMonitoring_run-37`
- Seizure start: `2000-01-01 00:20:54`
- Seizure end: `2000-01-01 00:25:37`

State counts:

| audit_state | rows |
| --- | --- |
| forecast_positive | 15 |
| ictal_excluded | 5 |
| valid_negative | 5 |

Timeline rows:

| window_end | minutes_to_seizure | forecast_label | is_ictal | is_postictal | is_excluded | audit_state |
| --- | --- | --- | --- | --- | --- | --- |
| 2000-01-01 00:01:00 | 19.9 | True | False | False | False | forecast_positive |
| 2000-01-01 00:02:00 | 18.9 | True | False | False | False | forecast_positive |
| 2000-01-01 00:03:00 | 17.9 | True | False | False | False | forecast_positive |
| 2000-01-01 00:04:00 | 16.9 | True | False | False | False | forecast_positive |
| 2000-01-01 00:05:00 | 15.9 | True | False | False | False | forecast_positive |
| 2000-01-01 00:06:00 | 14.9 | True | False | False | False | forecast_positive |
| 2000-01-01 00:07:00 | 13.9 | True | False | False | False | forecast_positive |
| 2000-01-01 00:08:00 | 12.9 | True | False | False | False | forecast_positive |
| 2000-01-01 00:09:00 | 11.9 | True | False | False | False | forecast_positive |
| 2000-01-01 00:10:00 | 10.9 | True | False | False | False | forecast_positive |
| 2000-01-01 00:11:00 | 9.9 | True | False | False | False | forecast_positive |
| 2000-01-01 00:12:00 | 8.9 | True | False | False | False | forecast_positive |
| 2000-01-01 00:13:00 | 7.9 | True | False | False | False | forecast_positive |
| 2000-01-01 00:14:00 | 6.9 | True | False | False | False | forecast_positive |
| 2000-01-01 00:15:00 | 5.9 | True | False | False | False | forecast_positive |
| 2000-01-01 00:16:00 | 4.9 | False | False | False | False | valid_negative |
| 2000-01-01 00:17:00 | 3.9 | False | False | False | False | valid_negative |
| 2000-01-01 00:18:00 | 2.9 | False | False | False | False | valid_negative |
| 2000-01-01 00:19:00 | 1.9 | False | False | False | False | valid_negative |
| 2000-01-01 00:20:00 | 0.9 | False | False | False | False | valid_negative |
| 2000-01-01 00:21:00 | -0.1 | False | True | False | True | ictal_excluded |
| 2000-01-01 00:22:00 | -1.1 | False | True | False | True | ictal_excluded |
| 2000-01-01 00:23:00 | -2.1 | False | True | False | True | ictal_excluded |
| 2000-01-01 00:24:00 | -3.1 | False | True | False | True | ictal_excluded |
| 2000-01-01 00:25:00 | -4.1 | False | True | False | True | ictal_excluded |

## Event 0

- Patient: `sub-125`
- Recording: `sub-125_ses-01_task-szMonitoring_run-21`
- Seizure start: `2000-01-01 01:22:44`
- Seizure end: `2000-01-01 01:32:14`

State counts:

| audit_state | rows |
| --- | --- |
| forecast_positive | 30 |
| ictal_excluded | 11 |
| postictal_excluded | 6 |
| valid_negative | 15 |

Timeline rows:

| window_end | minutes_to_seizure | forecast_label | is_ictal | is_postictal | is_excluded | audit_state |
| --- | --- | --- | --- | --- | --- | --- |
| 2000-01-01 00:38:00 | 44.73 | False | False | False | False | valid_negative |
| 2000-01-01 00:39:00 | 43.73 | False | False | False | False | valid_negative |
| 2000-01-01 00:40:00 | 42.73 | False | False | False | False | valid_negative |
| 2000-01-01 00:41:00 | 41.73 | False | False | False | False | valid_negative |
| 2000-01-01 00:42:00 | 40.73 | False | False | False | False | valid_negative |
| 2000-01-01 00:43:00 | 39.73 | False | False | False | False | valid_negative |
| 2000-01-01 00:44:00 | 38.73 | False | False | False | False | valid_negative |
| 2000-01-01 00:45:00 | 37.73 | False | False | False | False | valid_negative |
| 2000-01-01 00:46:00 | 36.73 | False | False | False | False | valid_negative |
| 2000-01-01 00:47:00 | 35.73 | False | False | False | False | valid_negative |
| 2000-01-01 00:48:00 | 34.73 | True | False | False | False | forecast_positive |
| 2000-01-01 00:49:00 | 33.73 | True | False | False | False | forecast_positive |
| 2000-01-01 00:50:00 | 32.73 | True | False | False | False | forecast_positive |
| 2000-01-01 00:51:00 | 31.73 | True | False | False | False | forecast_positive |
| 2000-01-01 00:52:00 | 30.73 | True | False | False | False | forecast_positive |
| 2000-01-01 00:53:00 | 29.73 | True | False | False | False | forecast_positive |
| 2000-01-01 00:54:00 | 28.73 | True | False | False | False | forecast_positive |
| 2000-01-01 00:55:00 | 27.73 | True | False | False | False | forecast_positive |
| 2000-01-01 00:56:00 | 26.73 | True | False | False | False | forecast_positive |
| 2000-01-01 00:57:00 | 25.73 | True | False | False | False | forecast_positive |
| 2000-01-01 00:58:00 | 24.73 | True | False | False | False | forecast_positive |
| 2000-01-01 00:59:00 | 23.73 | True | False | False | False | forecast_positive |
| 2000-01-01 01:00:00 | 22.73 | True | False | False | False | forecast_positive |
| 2000-01-01 01:01:00 | 21.73 | True | False | False | False | forecast_positive |
| 2000-01-01 01:02:00 | 20.73 | True | False | False | False | forecast_positive |
| 2000-01-01 01:03:00 | 19.73 | True | False | False | False | forecast_positive |
| 2000-01-01 01:04:00 | 18.73 | True | False | False | False | forecast_positive |
| 2000-01-01 01:05:00 | 17.73 | True | False | False | False | forecast_positive |
| 2000-01-01 01:06:00 | 16.73 | True | False | False | False | forecast_positive |
| 2000-01-01 01:07:00 | 15.73 | True | False | False | False | forecast_positive |
| 2000-01-01 01:08:00 | 14.73 | True | False | False | False | forecast_positive |
| 2000-01-01 01:09:00 | 13.73 | True | False | False | False | forecast_positive |
| 2000-01-01 01:10:00 | 12.73 | True | False | False | False | forecast_positive |
| 2000-01-01 01:11:00 | 11.73 | True | False | False | False | forecast_positive |
| 2000-01-01 01:12:00 | 10.73 | True | False | False | False | forecast_positive |
| 2000-01-01 01:13:00 | 9.73 | True | False | False | False | forecast_positive |
| 2000-01-01 01:14:00 | 8.73 | True | False | False | False | forecast_positive |
| 2000-01-01 01:15:00 | 7.73 | True | False | False | False | forecast_positive |
| 2000-01-01 01:16:00 | 6.73 | True | False | False | False | forecast_positive |
| 2000-01-01 01:17:00 | 5.73 | True | False | False | False | forecast_positive |
| 2000-01-01 01:18:00 | 4.73 | False | False | False | False | valid_negative |
| 2000-01-01 01:19:00 | 3.73 | False | False | False | False | valid_negative |
| 2000-01-01 01:20:00 | 2.73 | False | False | False | False | valid_negative |
| 2000-01-01 01:21:00 | 1.73 | False | False | False | False | valid_negative |
| 2000-01-01 01:22:00 | 0.73 | False | False | False | False | valid_negative |
| 2000-01-01 01:23:00 | -0.27 | False | True | False | True | ictal_excluded |
| 2000-01-01 01:24:00 | -1.27 | False | True | False | True | ictal_excluded |
| 2000-01-01 01:25:00 | -2.27 | False | True | False | True | ictal_excluded |
| 2000-01-01 01:26:00 | -3.27 | False | True | False | True | ictal_excluded |
| 2000-01-01 01:27:00 | -4.27 | False | True | False | True | ictal_excluded |
| 2000-01-01 01:28:00 | -5.27 | False | True | False | True | ictal_excluded |
| 2000-01-01 01:29:00 | -6.27 | False | True | False | True | ictal_excluded |
| 2000-01-01 01:30:00 | -7.27 | False | True | False | True | ictal_excluded |
| 2000-01-01 01:31:00 | -8.27 | False | True | False | True | ictal_excluded |
| 2000-01-01 01:32:00 | -9.27 | False | True | False | True | ictal_excluded |
| 2000-01-01 01:33:00 | -10.27 | False | True | True | True | ictal_excluded |
| 2000-01-01 01:34:00 | -11.27 | False | False | True | True | postictal_excluded |
| 2000-01-01 01:35:00 | -12.27 | False | False | True | True | postictal_excluded |
| 2000-01-01 01:36:00 | -13.27 | False | False | True | True | postictal_excluded |
| 2000-01-01 01:37:00 | -14.27 | False | False | True | True | postictal_excluded |
| 2000-01-01 01:38:00 | -15.27 | False | False | True | True | postictal_excluded |
| 2000-01-01 01:39:00 | -16.27 | False | False | True | True | postictal_excluded |
