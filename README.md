# EpiTwin-Open

**EpiTwin-Open** is a leakage-safe research scaffold for public wearable seizure-risk forecasting. It is designed for a PhD project that moves from reactive seizure detection toward calibrated, forecastability-aware seizure-risk estimation.

The repository deliberately starts with **clinical task definition, SPH/SOP labeling, event-level metrics, anti-leakage splits, calibration, and sanity baselines** before training large models.

## Core thesis

Seizure forecasting should not be framed as a naive binary preictal/interictal classification task. A clinically useful system must estimate:

```text
risk + uncertainty + observability + alarm burden
```

The model must be able to say not only “risk is high”, but also “risk is not observable from these sensors” or “signal quality is insufficient”.

## Implemented in this package

### Benchmark and labels

- SPH/SOP labeling.
- Ictal and postictal exclusion.
- Event-level forecasting metrics.
- Patient-wise, temporal, and center-wise split utilities.
- Leakage audit utilities.

### Clinical metrics

- Event-level sensitivity.
- False alarm rate per hour/day.
- Time-in-Warning.
- Median lead time.
- Brier score.
- Expected calibration error.
- Threshold sweeping under alarm budgets.

### Baselines

- Random rate-matched predictor.
- ECG/HR tachycardia-style score.
- ACC energy-style score.
- Generic z-score anomaly score.
- Optional TCN-small baseline.

### EpiTwin v0.1 model scaffolding

- Multimodal signal encoders.
- Gated multimodal fusion.
- Causal TCN, GRU, causal Transformer, CfC placeholder, Mamba placeholder.
- Hazard/survival head.
- Uncertainty head.
- Masked reconstruction loss.
- Future latent prediction loss.
- Cross-modal predictive coding proxy.
- Edge observable student.
- Observable-latent distillation loss.
- Soft neuro-symbolic constraints for signal quality and autonomic context.

### Scripts

- `label_windows.py`: create SPH/SOP labels.
- `inspect_labels.py`: audit labels manually.
- `run_baseline.py`: random baseline.
- `evaluate_predictions.py`: clinical metrics.
- `sweep_thresholds.py`: threshold-vs-clinical-budget sweep.
- `run_synthetic_demo.py`: end-to-end synthetic demo.
- `train_epitwin_ssl.py`: CPU-testable SSL smoke training.

## Why SPH/SOP matters

For a window ending at time `t`, a forecasting label is positive if seizure onset occurs in:

```text
[t + SPH, t + SPH + SOP)
```

Example: with `SPH=5 min` and `SOP=30 min`, a window ending at 10:00 is positive if a seizure starts between 10:05 and 10:35.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev,torch]'
python -m pytest -q
```

Or with `uv`:

```bash
uv sync --extra dev --extra torch
uv run python -m pytest -q
```

The test count changes as remediation tests are added. The current Phase R3 checkpoint passes
99 tests; treat CI and the local command output as the source of truth rather than a hard-coded
claim.

```text
all tests pass
```

## Synthetic demo

```bash
python scripts/run_synthetic_demo.py
python -u scripts/train_epitwin_ssl.py --epochs 1 --batch-size 1 --time-steps 4 --hidden-dim 4 --backbone gru
```

Preferred reproducible entrypoints:

```bash
./RUN_THIS_FIRST.sh
make test
make demo
make report
make smoke-train
```

## First real-data workflow

```bash
python scripts/prepare_seizeit2.py \
  --raw-dir data/raw/seizeit2 \
  --processed-dir data/processed/seizeit2

python scripts/make_windows.py \
  --recordings data/processed/seizeit2/recordings.parquet \
  --out data/processed/seizeit2/windows.parquet \
  --window-duration 2min \
  --stride 30s

python scripts/label_windows.py \
  --windows data/processed/seizeit2/windows.parquet \
  --events data/processed/seizeit2/events.parquet \
  --output data/processed/seizeit2/labels_sph5_sop30.parquet \
  --sph-minutes 5 \
  --sop-minutes 30 \
  --postictal-exclusion-minutes 60

python scripts/inspect_labels.py \
  --labels data/processed/seizeit2/labels_sph5_sop30.parquet \
  --events data/processed/seizeit2/events.parquet
```

## Human checkpoints before A100 training

Do not launch serious GPU training until:

1. labels are manually audited around multiple seizures;
2. ictal, postictal, and right-censored horizon exclusions are verified;
3. random rate-matched baseline exists;
4. split is frozen;
5. leakage audit passes;
6. FAR/day and Time-in-Warning are computed.

## Current scope and honesty

This package does **not** claim real seizure-forecasting performance yet. It is a research-ready scaffold to make the first paper rigorous before large-scale A100 experiments.

Forbidden claims at this stage:

- wearable edge/TinyML hardware performance;
- closed-loop stimulation;
- 90% sensitivity at 0.1 FAR/day;
- prediction of all focal seizures.

Allowed claim:

> EpiTwin-Open establishes a leakage-safe, clinically meaningful benchmark and model scaffold for measuring what is actually forecastable from public wearable seizure datasets.
