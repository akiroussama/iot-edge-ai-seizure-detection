# MSG Full Label Audit Packet

This packet is for manual label audit only. It is not a clinical result.

Checklist for each event:

- Confirm source seizure onset/end.
- Confirm forecast positives satisfy `[window_end + SPH, window_end + SPH + SOP)`.
- Confirm ictal windows are excluded.
- Confirm postictal windows are excluded.
- Record any parser or annotation issue before training.

## Event 1

- Patient: `1110`
- Recording: `1110_1598624269_A01EE3`
- Seizure start: `2020-08-29 12:26:51`
- Seizure end: `2020-08-29 12:27:51`

State counts:

| audit_state | rows |
| --- | --- |
| forecast_positive | 2 |
| ictal_excluded | 1 |
| postictal_excluded | 3 |
| valid_negative | 1 |

Timeline rows:

| window_end | minutes_to_seizure | forecast_label | is_ictal | is_postictal | is_excluded | audit_state |
| --- | --- | --- | --- | --- | --- | --- |
| 2020-08-29 10:17:59 | 128.87 | True | False | False | False | forecast_positive |
| 2020-08-29 11:17:59 | 68.87 | True | False | False | False | forecast_positive |
| 2020-08-29 12:17:59 | 8.87 | False | False | False | False | valid_negative |
| 2020-08-29 13:17:59 | -51.13 | False | True | True | True | ictal_excluded |
| 2020-08-29 14:17:59 | -111.13 | False | False | True | True | postictal_excluded |
| 2020-08-29 15:17:59 | -171.13 | False | False | True | True | postictal_excluded |
| 2020-08-29 16:17:59 | -231.13 | False | False | True | True | postictal_excluded |

## Event 2

- Patient: `1110`
- Recording: `1110_1598624269_A01EE3`
- Seizure start: `2020-08-29 12:29:48`
- Seizure end: `2020-08-29 12:30:48`

State counts:

| audit_state | rows |
| --- | --- |
| forecast_positive | 2 |
| ictal_excluded | 1 |
| postictal_excluded | 3 |
| valid_negative | 1 |

Timeline rows:

| window_end | minutes_to_seizure | forecast_label | is_ictal | is_postictal | is_excluded | audit_state |
| --- | --- | --- | --- | --- | --- | --- |
| 2020-08-29 10:17:59 | 131.82 | True | False | False | False | forecast_positive |
| 2020-08-29 11:17:59 | 71.82 | True | False | False | False | forecast_positive |
| 2020-08-29 12:17:59 | 11.82 | False | False | False | False | valid_negative |
| 2020-08-29 13:17:59 | -48.18 | False | True | True | True | ictal_excluded |
| 2020-08-29 14:17:59 | -108.18 | False | False | True | True | postictal_excluded |
| 2020-08-29 15:17:59 | -168.18 | False | False | True | True | postictal_excluded |
| 2020-08-29 16:17:59 | -228.18 | False | False | True | True | postictal_excluded |

## Event 3

- Patient: `1110`
- Recording: `1110_1598624269_A01EE3`
- Seizure start: `2020-08-29 12:31:53`
- Seizure end: `2020-08-29 12:32:53`

State counts:

| audit_state | rows |
| --- | --- |
| forecast_positive | 2 |
| ictal_excluded | 1 |
| postictal_excluded | 3 |
| valid_negative | 1 |

Timeline rows:

| window_end | minutes_to_seizure | forecast_label | is_ictal | is_postictal | is_excluded | audit_state |
| --- | --- | --- | --- | --- | --- | --- |
| 2020-08-29 10:17:59 | 133.9 | True | False | False | False | forecast_positive |
| 2020-08-29 11:17:59 | 73.9 | True | False | False | False | forecast_positive |
| 2020-08-29 12:17:59 | 13.9 | False | False | False | False | valid_negative |
| 2020-08-29 13:17:59 | -46.1 | False | True | True | True | ictal_excluded |
| 2020-08-29 14:17:59 | -106.1 | False | False | True | True | postictal_excluded |
| 2020-08-29 15:17:59 | -166.1 | False | False | True | True | postictal_excluded |
| 2020-08-29 16:17:59 | -226.1 | False | False | True | True | postictal_excluded |

## Event 4

- Patient: `1110`
- Recording: `1110_1599352806_A02294`
- Seizure start: `2020-09-07 10:57:49`
- Seizure end: `2020-09-07 10:58:49`

State counts:

| audit_state | rows |
| --- | --- |
| forecast_positive | 3 |
| ictal_excluded | 2 |
| postictal_excluded | 1 |

Timeline rows:

| window_end | minutes_to_seizure | forecast_label | is_ictal | is_postictal | is_excluded | audit_state |
| --- | --- | --- | --- | --- | --- | --- |
| 2020-09-07 08:40:16 | 137.55 | True | False | False | False | forecast_positive |
| 2020-09-07 09:40:16 | 77.55 | True | False | False | False | forecast_positive |
| 2020-09-07 10:40:16 | 17.55 | True | False | False | False | forecast_positive |
| 2020-09-07 11:40:16 | -42.45 | False | True | True | True | ictal_excluded |
| 2020-09-07 12:40:16 | -102.45 | False | True | True | True | ictal_excluded |
| 2020-09-07 13:40:16 | -162.45 | False | False | True | True | postictal_excluded |

## Event 5

- Patient: `1110`
- Recording: `1110_1599352806_A02294`
- Seizure start: `2020-09-07 11:54:50`
- Seizure end: `2020-09-07 11:55:50`

State counts:

| audit_state | rows |
| --- | --- |
| forecast_positive | 2 |
| ictal_excluded | 2 |
| postictal_excluded | 1 |

Timeline rows:

| window_end | minutes_to_seizure | forecast_label | is_ictal | is_postictal | is_excluded | audit_state |
| --- | --- | --- | --- | --- | --- | --- |
| 2020-09-07 09:40:16 | 134.57 | True | False | False | False | forecast_positive |
| 2020-09-07 10:40:16 | 74.57 | True | False | False | False | forecast_positive |
| 2020-09-07 11:40:16 | 14.57 | False | True | True | True | ictal_excluded |
| 2020-09-07 12:40:16 | -45.43 | False | True | True | True | ictal_excluded |
| 2020-09-07 13:40:16 | -105.43 | False | False | True | True | postictal_excluded |

## Event 6

- Patient: `1110`
- Recording: `1110_1599352806_A02294`
- Seizure start: `2020-09-07 12:05:42`
- Seizure end: `2020-09-07 12:06:42`

State counts:

| audit_state | rows |
| --- | --- |
| forecast_positive | 2 |
| ictal_excluded | 2 |
| postictal_excluded | 1 |

Timeline rows:

| window_end | minutes_to_seizure | forecast_label | is_ictal | is_postictal | is_excluded | audit_state |
| --- | --- | --- | --- | --- | --- | --- |
| 2020-09-07 09:40:16 | 145.43 | True | False | False | False | forecast_positive |
| 2020-09-07 10:40:16 | 85.43 | True | False | False | False | forecast_positive |
| 2020-09-07 11:40:16 | 25.43 | False | True | True | True | ictal_excluded |
| 2020-09-07 12:40:16 | -34.57 | False | True | True | True | ictal_excluded |
| 2020-09-07 13:40:16 | -94.57 | False | False | True | True | postictal_excluded |

## Event 7

- Patient: `1110`
- Recording: `1110_1599352806_A02294`
- Seizure start: `2020-09-07 12:32:35`
- Seizure end: `2020-09-07 12:33:35`

State counts:

| audit_state | rows |
| --- | --- |
| forecast_positive | 2 |
| ictal_excluded | 2 |
| postictal_excluded | 1 |

Timeline rows:

| window_end | minutes_to_seizure | forecast_label | is_ictal | is_postictal | is_excluded | audit_state |
| --- | --- | --- | --- | --- | --- | --- |
| 2020-09-07 09:40:16 | 172.32 | True | False | False | False | forecast_positive |
| 2020-09-07 10:40:16 | 112.32 | True | False | False | False | forecast_positive |
| 2020-09-07 11:40:16 | 52.32 | False | True | True | True | ictal_excluded |
| 2020-09-07 12:40:16 | -7.68 | False | True | True | True | ictal_excluded |
| 2020-09-07 13:40:16 | -67.68 | False | False | True | True | postictal_excluded |

## Event 8

- Patient: `1110`
- Recording: `1110_1601509460_A02294`
- Seizure start: `2020-10-01 09:31:53`
- Seizure end: `2020-10-01 09:32:53`

State counts:

| audit_state | rows |
| --- | --- |
| forecast_positive | 2 |
| ictal_excluded | 1 |
| postictal_excluded | 3 |
| valid_negative | 1 |

Timeline rows:

| window_end | minutes_to_seizure | forecast_label | is_ictal | is_postictal | is_excluded | audit_state |
| --- | --- | --- | --- | --- | --- | --- |
| 2020-10-01 06:44:30 | 167.38 | True | False | False | False | forecast_positive |
| 2020-10-01 07:44:30 | 107.38 | True | False | False | False | forecast_positive |
| 2020-10-01 08:44:30 | 47.38 | False | False | False | False | valid_negative |
| 2020-10-01 09:44:30 | -12.62 | False | True | True | True | ictal_excluded |
| 2020-10-01 10:44:30 | -72.62 | False | False | True | True | postictal_excluded |
| 2020-10-01 11:44:30 | -132.62 | False | False | True | True | postictal_excluded |
| 2020-10-01 12:44:30 | -192.62 | False | False | True | True | postictal_excluded |

## Event 9

- Patient: `1110`
- Recording: `1110_1601509460_A02294`
- Seizure start: `2020-10-01 09:34:54`
- Seizure end: `2020-10-01 09:35:54`

State counts:

| audit_state | rows |
| --- | --- |
| forecast_positive | 2 |
| ictal_excluded | 1 |
| postictal_excluded | 3 |
| valid_negative | 1 |

Timeline rows:

| window_end | minutes_to_seizure | forecast_label | is_ictal | is_postictal | is_excluded | audit_state |
| --- | --- | --- | --- | --- | --- | --- |
| 2020-10-01 06:44:30 | 170.4 | True | False | False | False | forecast_positive |
| 2020-10-01 07:44:30 | 110.4 | True | False | False | False | forecast_positive |
| 2020-10-01 08:44:30 | 50.4 | False | False | False | False | valid_negative |
| 2020-10-01 09:44:30 | -9.6 | False | True | True | True | ictal_excluded |
| 2020-10-01 10:44:30 | -69.6 | False | False | True | True | postictal_excluded |
| 2020-10-01 11:44:30 | -129.6 | False | False | True | True | postictal_excluded |
| 2020-10-01 12:44:30 | -189.6 | False | False | True | True | postictal_excluded |

## Event 10

- Patient: `1110`
- Recording: `1110_1602106469_A02294`
- Seizure start: `2020-10-09 14:50:51`
- Seizure end: `2020-10-09 14:51:51`

State counts:

| audit_state | rows |
| --- | --- |
| forecast_positive | 2 |
| ictal_excluded | 1 |
| valid_negative | 1 |

Timeline rows:

| window_end | minutes_to_seizure | forecast_label | is_ictal | is_postictal | is_excluded | audit_state |
| --- | --- | --- | --- | --- | --- | --- |
| 2020-10-09 12:34:39 | 136.2 | True | False | False | False | forecast_positive |
| 2020-10-09 13:34:39 | 76.2 | True | False | False | False | forecast_positive |
| 2020-10-09 14:34:39 | 16.2 | False | False | False | False | valid_negative |
| 2020-10-09 15:34:39 | -43.8 | False | True | True | True | ictal_excluded |
