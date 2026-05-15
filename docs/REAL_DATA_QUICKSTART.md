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
  --windows data/processed/seizeit2/windows.parquet \
  --events data/processed/seizeit2/events.parquet \
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
```

## My Seizure Gauge

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
  --windows data/processed/msg/windows_1h.parquet \
  --events data/processed/msg/events.parquet \
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
  --out-dir reports/msg_real_check \
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
