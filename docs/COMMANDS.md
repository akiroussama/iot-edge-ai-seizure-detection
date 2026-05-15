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

## A100 Policy

Do not launch A100 training until:

- real labels are generated and manually audited;
- real splits are frozen;
- random baseline has run;
- leakage audit is clean;
- 5-10 real seizure timelines have been inspected by a human.

Synthetic/mock commands are software checks only and do not support clinical claims.
