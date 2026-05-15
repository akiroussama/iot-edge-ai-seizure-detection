# Commands

Use `uv run` as the canonical execution path. `make` targets are provided for convenience, but some environments do not have `make` installed.

## Setup

```bash
uv sync --extra dev --extra torch
```

## Verification

One-command synthetic/mock verification:

```bash
./RUN_THIS_FIRST.sh
```

Direct equivalents:

```bash
uv run python -m pytest -q
uv run ruff check .
uv run python scripts/run_synthetic_demo.py
uv run python scripts/make_report.py --synthetic --out-dir reports
uv run python -u scripts/train_epitwin_ssl.py --epochs 1 --batch-size 1 --time-steps 4 --hidden-dim 4 --backbone gru
```

Make equivalents when `make` is installed:

```bash
make test
make lint
make demo
make report
make smoke-train
make all-checks
```

## Dataset Inspection

Mock SeizeIT2 artifacts:

```bash
uv run python scripts/prepare_seizeit2.py \
  --mock \
  --processed-dir /tmp/epitwin_mock_seizeit2
```

Mock My Seizure Gauge artifacts:

```bash
uv run python scripts/prepare_msg.py \
  --mock \
  --processed-dir /tmp/epitwin_mock_msg
```

SeizeIT2 dry inspection:

```bash
uv run python scripts/prepare_seizeit2.py \
  --raw-dir data/raw/seizeit2 \
  --processed-dir data/processed/seizeit2 \
  --inspect-only
```

My Seizure Gauge dry inspection:

```bash
uv run python scripts/download_msg_zenodo.py \
  --out-dir data/raw/msg \
  --include SeizureTimesOnly.zip

uv run python scripts/prepare_msg.py \
  --raw-dir data/raw/msg \
  --processed-dir data/processed/msg \
  --inspect-only
```

## Windows And Labels

```bash
uv run python scripts/make_windows.py \
  --recordings data/processed/seizeit2/recordings.parquet \
  --out data/processed/seizeit2/windows.parquet \
  --window-duration 2min \
  --stride 30s

uv run python scripts/label_windows.py \
  --windows data/processed/seizeit2/windows.parquet \
  --events data/processed/seizeit2/events.parquet \
  --output data/processed/seizeit2/forecast_labels.parquet \
  --sph-minutes 5 \
  --sop-minutes 30 \
  --postictal-exclusion-minutes 60
```

Export a human label audit CSV:

```bash
uv run python scripts/audit_labels.py \
  --labels data/processed/seizeit2/forecast_labels.parquet \
  --events data/processed/seizeit2/events.parquet \
  --out reports/seizeit2_label_audit.csv \
  --minutes-before 60 \
  --minutes-after 60
```

Create a compact Markdown packet for manual review:

```bash
uv run python scripts/make_audit_packet.py \
  --audit reports/seizeit2_label_audit.csv \
  --out reports/seizeit2_audit_packet.md \
  --max-events 10 \
  --title "SeizeIT2 Label Audit Packet"
```

Generate a dataset-specific pipeline-check report:

```bash
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

For MSG partial downloads, pass `--event-filter recording_match_status=matched` so events outside
downloaded wearable segments are reported as coverage gaps rather than false model failures.

Create temporal splits and a leakage audit:

```bash
uv run python scripts/make_splits.py \
  --labels data/processed/seizeit2/forecast_labels.parquet \
  --out data/processed/seizeit2/split_temporal.parquet \
  --audit-out reports/seizeit2_leakage_audit.txt \
  --strategy temporal
```

For single-patient SeizeIT2 smoke checks with recordings that reset to dummy dates, create a
recording-wise split to confirm no run appears in more than one split. This is not a substitute for
patient-wise or prospective temporal evaluation.

```bash
uv run python scripts/make_splits.py \
  --labels data/processed/seizeit2/forecast_labels.parquet \
  --out data/processed/seizeit2/split_recording.parquet \
  --audit-out reports/seizeit2_recording_leakage_audit.txt \
  --strategy recording_wise
```

## Transparent Rule Baselines

MSG Empatica HR/ACC features can be extracted directly from nested ZIPs without writing all raw
samples to a single table:

```bash
uv run python scripts/extract_msg_features.py \
  --raw-dir data/raw/msg \
  --windows data/processed/msg/labels_sph60_sop1440.parquet \
  --out data/processed/msg/features_hr_acc_sph60_sop1440.parquet \
  --modalities hr acc

uv run python scripts/run_rule_baseline.py \
  --features data/processed/msg/features_hr_acc_sph60_sop1440.parquet \
  --out data/processed/msg/hr_tachycardia_predictions_sph60_sop1440.parquet \
  --rule hr_tachycardia \
  --target-tiw 0.1
```

## A100 Policy

Do not launch A100 training until:

- real labels are generated and manually audited;
- real splits are frozen;
- random baseline has run;
- leakage audit is clean;
- 5-10 real seizure timelines have been inspected by a human.

Synthetic/mock commands are software checks only and do not support clinical claims.
