# Codex Phase R3 Cluster And Postictal Policy Pass

Date: 2026-05-16

Branch: `feature/epibench-forecast-v0.1`

## Scope

This pass turns two remaining Phase R policy gaps into executable, testable code paths:

1. H1 seizure clusters are now evaluable as explicit cluster-level metric units.
2. MSG onset-only seizure annotations no longer silently drive postictal exclusion from an imputed
   seizure end.

These changes do not make MSG results clinically publishable. They make the benchmark harder to
misreport.

## H1: Cluster-Level Event Units

New functions:

```text
src.metrics.event_metrics.assign_event_clusters
src.metrics.event_metrics.collapse_event_clusters
```

Policy:

- Clusters are defined by onset-to-onset gap within `cluster_gap_minutes`.
- Default clustering preserves `recording_id` scope when present, because event metrics associate
  alarms by patient and recording.
- Cluster-level sensitivity uses the first seizure onset in the cluster as the metric event.
- Later seizures inside the same cluster are removed from the event denominator.

CLI/report changes:

- `scripts/make_dataset_report.py --event-unit cluster --cluster-gap-minutes 240`
- `scripts/evaluate_predictions.py --event-unit cluster --cluster-gap-minutes 240`
- Event denominator tables now include:
  - `metric_units_after_filter`
  - `metric_units_used_for_metrics`
  - `cluster_policy=cluster_level_first_event`

MSG SPH60/SOP1440 audit signals after cluster-level reporting:

```text
HR tachycardia seizure-level test denominator: 54 events, 46 forecasted, sensitivity 0.851852
HR tachycardia cluster-level test denominator: 40 clusters, 33 forecasted, sensitivity 0.825000

Cycle seizure-level test denominator: 54 events, 3 forecasted, sensitivity 0.055556
Cycle cluster-level test denominator: 40 clusters, 3 forecasted, sensitivity 0.075000
```

Interpretation:

The cluster-level denominator is materially different from the seizure-level denominator. Any future
table must state which event unit is being reported.

## Onset-Only Postictal Policy

New label option:

```text
label_forecast_windows(..., postictal_anchor="seizure_end" | "seizure_start")
```

CLI behavior:

- `scripts/label_windows.py` adds `--postictal-anchor seizure_start|seizure_end`.
- If events contain `seizure_end_imputed=True`, postictal exclusion anchored to `seizure_end` now
  fails unless `--allow-imputed-seizure-end-postictal` is explicitly provided.

MSG regeneration policy:

```bash
uv run python scripts/label_windows.py \
  --windows data/processed/msg/windows_1h.parquet \
  --events data/processed/msg/events.parquet \
  --output data/processed/msg/labels_sph60_sop1440.parquet \
  --sph-minutes 60 \
  --sop-minutes 1440 \
  --postictal-exclusion-minutes 240 \
  --postictal-anchor seizure_start
```

MSG label distribution after explicit onset-only postictal policy:

```text
total windows: 49,577
valid windows: 7,920
excluded windows: 41,657
right-censored windows: 44,689
positive windows total: 3,781
positive windows valid: 3,326
```

The numerical change from Phase R2 is small at one-hour stride, but the policy is now explicit and
machine-enforced.

## Regenerated Reports

Updated:

- `reports/msg_full_real_check/dataset_report.md`
- `reports/msg_full_real_check_coverable/dataset_report.md`
- `reports/msg_cycle_hour_recording_test_check/dataset_report.md`
- `reports/msg_hr_tachycardia_recording_splitaware_check/dataset_report.md`
- `reports/msg_event_coverage_summary.md`
- `reports/msg_full_audit_packet.md`
- `reports/msg_temporal_recording_leakage_audit.md`

Added:

- `reports/msg_hr_tachycardia_cluster_recording_splitaware_check/dataset_report.md`
- `reports/msg_cycle_hour_cluster_recording_test_check/dataset_report.md`

## Validation

Targeted tests:

```bash
uv run --extra dev --extra torch python -m pytest \
  tests/test_labeling_edge_cases.py \
  tests/test_event_metrics.py \
  tests/test_dataset_report.py -q
```

Expected additional full checks before merging:

```bash
uv run --extra dev --extra torch python -m pytest -q
uv run --extra dev ruff check .
```

## Remaining Risks

1. Cluster gap of 240 minutes is a pre-registered audit policy, not a clinical truth.
2. Cluster-level first-event sensitivity may be too strict or too lenient depending on the paper task.
3. MSG remains coverage-limited and onset-only.
4. Manual timeline audit remains mandatory before any result claim.
5. A100 remains blocked.
