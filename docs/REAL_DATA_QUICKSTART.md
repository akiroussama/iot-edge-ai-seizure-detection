# Real Data Quickstart

Use this only after public datasets are downloaded locally. Do not commit raw or processed data.

The commands below are designed to fail loudly when annotations are missing or when ZIP downloads
are incomplete. Generated numbers are pipeline checks until the manual label audit is complete.

## SeizeIT2

Inspect:

```bash
uv run python scripts/prepare_seizeit2.py \
  --raw-dir data/raw/seizeit2 \
  --processed-dir data/processed/seizeit2 \
  --inspect-only
```

Prepare supported metadata:

```bash
uv run python scripts/prepare_seizeit2.py \
  --raw-dir data/raw/seizeit2 \
  --processed-dir data/processed/seizeit2
```

If your local SeizeIT2 checkout is missing `*_events.tsv` files but has OpenNeuro `ds005873`
signals, fetch the matching annotation TSVs from OpenNeuro/GitHub before preparation. Do not infer
seizure labels from filenames.

If `recordings.parquet` is populated, window:

```bash
uv run python scripts/make_windows.py \
  --recordings data/processed/seizeit2/recordings.parquet \
  --out data/processed/seizeit2/windows.parquet \
  --window-duration 2min \
  --stride 30s
```

Label:

```bash
uv run python scripts/label_windows.py \
  --windows data/processed/seizeit2/windows.parquet \
  --events data/processed/seizeit2/events.parquet \
  --output data/processed/seizeit2/forecast_labels.parquet \
  --sph-minutes 5 \
  --sop-minutes 30 \
  --postictal-exclusion-minutes 60
```

Run a random alarm sanity baseline and dataset report:

```bash
uv run python scripts/run_baseline.py \
  --labels data/processed/seizeit2/forecast_labels.parquet \
  --out data/processed/seizeit2/random_tiw10_predictions.parquet \
  --sph-minutes 5 \
  --sop-minutes 30 \
  --tiw 0.1

uv run python scripts/make_dataset_report.py \
  --dataset-name SeizeIT2-local \
  --windows data/processed/seizeit2/windows.parquet \
  --labels data/processed/seizeit2/forecast_labels.parquet \
  --events data/processed/seizeit2/events.parquet \
  --predictions data/processed/seizeit2/random_tiw10_predictions.parquet \
  --baseline-name random_rate_matched_tiw10 \
  --out-dir reports/seizeit2_real_check \
  --sph-minutes 5 \
  --sop-minutes 30
```

Audit:

```bash
uv run python scripts/audit_labels.py \
  --labels data/processed/seizeit2/forecast_labels.parquet \
  --events data/processed/seizeit2/events.parquet \
  --out reports/seizeit2_label_audit.csv

uv run python scripts/make_audit_packet.py \
  --audit reports/seizeit2_label_audit.csv \
  --out reports/seizeit2_audit_packet.md \
  --max-events 10 \
  --title "SeizeIT2 Label Audit Packet"
```

Split and leakage audit. Prefer temporal or patient-wise splits for actual evaluation. If a local
SeizeIT2 smoke check contains only one patient and recordings with reset/dummy timestamps, use
`recording_wise` only to verify that runs are not shared across splits; do not treat it as a
prospective clinical split.

```bash
uv run python scripts/make_splits.py \
  --labels data/processed/seizeit2/forecast_labels.parquet \
  --out data/processed/seizeit2/split_temporal.parquet \
  --audit-out reports/seizeit2_leakage_audit.txt \
  --strategy temporal

uv run python scripts/make_splits.py \
  --labels data/processed/seizeit2/forecast_labels.parquet \
  --out data/processed/seizeit2/split_recording.parquet \
  --audit-out reports/seizeit2_recording_leakage_audit.txt \
  --strategy recording_wise
```

## My Seizure Gauge

Download from the current Zenodo record with resumable `curl`:

```bash
uv run python scripts/download_msg_zenodo.py \
  --out-dir data/raw/msg
```

For a quick annotation-only check:

```bash
uv run python scripts/download_msg_zenodo.py \
  --out-dir data/raw/msg \
  --include SeizureTimesOnly.zip
```

Inspect:

```bash
uv run python scripts/prepare_msg.py \
  --raw-dir data/raw/msg \
  --processed-dir data/processed/msg \
  --inspect-only
```

The Zenodo MSG release uses per-patient `Mayo_*.zip` files containing many nested Empatica ZIPs
with `HR.csv`, `ACC.csv`, `EDA.csv`, `BVP.csv`, `TEMP.csv`, `IBI.csv`, plus patient-level seizure
onset text files. The loader first creates a manifest and recording intervals; it does not load all
raw samples into RAM.

Prepare supported metadata, recording intervals, events, modality manifests, and an empty samples
placeholder:

```bash
uv run python scripts/prepare_msg.py \
  --raw-dir data/raw/msg \
  --processed-dir data/processed/msg
```

Generate one-hour windows for a long-horizon check:

```bash
uv run python scripts/make_windows.py \
  --recordings data/processed/msg/recordings.parquet \
  --out data/processed/msg/windows_1h.parquet \
  --window-duration 1h \
  --stride 1h

uv run python scripts/label_windows.py \
  --windows data/processed/msg/windows_1h.parquet \
  --events data/processed/msg/events.parquet \
  --output data/processed/msg/labels_sph60_sop1440.parquet \
  --sph-minutes 60 \
  --sop-minutes 1440 \
  --postictal-exclusion-minutes 240
```

For partial downloads, evaluate only events whose onsets were matched to a downloaded wearable
segment:

```bash
uv run python - <<'PY'
import pandas as pd
from src.utils.io import write_table

events = pd.read_parquet("data/processed/msg/events.parquet")
matched = events.loc[events["recording_match_status"].eq("matched")]
write_table(matched, "data/processed/msg/events_matched.parquet")
PY

uv run python scripts/run_baseline.py \
  --labels data/processed/msg/labels_sph60_sop1440.parquet \
  --out data/processed/msg/random_tiw10_predictions_sph60_sop1440.parquet \
  --sph-minutes 60 \
  --sop-minutes 1440 \
  --tiw 0.1

uv run python scripts/make_dataset_report.py \
  --dataset-name MSG-local \
  --windows data/processed/msg/windows_1h.parquet \
  --labels data/processed/msg/labels_sph60_sop1440.parquet \
  --events data/processed/msg/events.parquet \
  --predictions data/processed/msg/random_tiw10_predictions_sph60_sop1440.parquet \
  --baseline-name random_rate_matched_tiw10 \
  --event-filter recording_match_status=matched \
  --acknowledge-event-filter-bias \
  --out-dir reports/msg_real_check \
  --sph-minutes 60 \
  --sop-minutes 1440
```

Before comparing baselines, summarize event coverage and clusters. Patients with many unmatched
events or large clusters must be manually reviewed before the denominator is treated as fixed:

```bash
uv run python scripts/summarize_event_coverage.py \
  --events data/processed/msg/events.parquet \
  --recordings data/processed/msg/recordings.parquet \
  --out-md reports/msg_event_coverage_summary.md \
  --out-coverage-csv reports/msg_event_coverage_summary.csv \
  --out-clusters-csv reports/msg_event_cluster_summary.csv \
  --cluster-gap-minutes 240 \
  --title "MSG Event Coverage And Cluster Summary"
```

Then generate a temporal leakage audit:

```bash
uv run python scripts/make_splits.py \
  --labels data/processed/msg/labels_sph60_sop1440.parquet \
  --out data/processed/msg/split_temporal.parquet \
  --audit-out reports/msg_leakage_audit.txt \
  --strategy temporal

uv run python scripts/make_splits.py \
  --labels data/processed/msg/labels_sph60_sop1440.parquet \
  --out data/processed/msg/split_temporal_recording.parquet \
  --audit-out reports/msg_temporal_recording_leakage_audit.txt \
  --strategy temporal \
  --temporal-unit recording

uv run python scripts/run_cycle_baseline.py \
  --split-labels data/processed/msg/split_temporal_recording.parquet \
  --out data/processed/msg/cycle_hour_recording_predictions_sph60_sop1440.parquet \
  --fit-split train \
  --threshold-split val \
  --target-tiw 0.1
```

Export a compact Markdown packet for manual review:

```bash
uv run python scripts/audit_labels.py \
  --labels data/processed/msg/labels_sph60_sop1440.parquet \
  --events data/processed/msg/events.parquet \
  --out reports/msg_full_label_audit.csv \
  --minutes-before 180 \
  --minutes-after 240

uv run python scripts/make_audit_packet.py \
  --audit reports/msg_full_label_audit.csv \
  --out reports/msg_full_audit_packet.md \
  --max-events 10 \
  --title "MSG Full Label Audit Packet"
```

Extract transparent HR/ACC feature baselines after the patient ZIP downloads are complete enough for
the target patients. For quick parser checks, use `--max-recordings`; omit it for the full run.

```bash
uv run python scripts/extract_msg_features.py \
  --raw-dir data/raw/msg \
  --windows data/processed/msg/split_temporal_recording.parquet \
  --out data/processed/msg/features_hr_temporal_recording_sph60_sop1440.parquet \
  --modalities hr

uv run python scripts/run_rule_baseline.py \
  --features data/processed/msg/features_hr_temporal_recording_sph60_sop1440.parquet \
  --out data/processed/msg/hr_tachycardia_recording_splitaware_predictions_sph60_sop1440.parquet \
  --rule hr_tachycardia \
  --target-tiw 0.1 \
  --score-fit-split train \
  --threshold-split val

uv run python scripts/make_dataset_report.py \
  --dataset-name MSG-local \
  --windows data/processed/msg/windows_1h.parquet \
  --labels data/processed/msg/labels_sph60_sop1440.parquet \
  --events data/processed/msg/events.parquet \
  --predictions data/processed/msg/hr_tachycardia_recording_splitaware_predictions_sph60_sop1440.parquet \
  --baseline-name hr_tachycardia_trainfit_valthreshold_recording_testsplit \
  --event-filter recording_match_status=matched \
  --acknowledge-event-filter-bias \
  --prediction-filter split=test \
  --restrict-events-to-prediction-coverage \
  --cluster-gap-minutes 240 \
  --out-dir reports/msg_hr_tachycardia_recording_splitaware_check \
  --sph-minutes 60 \
  --sop-minutes 1440
```

## Stop Conditions

Stop and fix parser assumptions if:

- event files are discovered but no events are written;
- recording intervals are missing and windows cannot be generated;
- seizure times are not absolute timestamps;
- modality availability is empty despite known signals;
- label audit reveals shifted seizure times.
