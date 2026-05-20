# A100 runbook

## Do not train before benchmark validation

The A100 is not the bottleneck. Bad labels and leakage are the bottleneck.

## Stage A — smoke tests

```bash
uv run --extra dev --extra torch python -m pytest -q
uv run --extra dev ruff check .
uv run python scripts/run_synthetic_demo.py
uv run --extra torch python scripts/train_epitwin_ssl.py --epochs 3 --backbone tcn
```

## Stage B — first real baseline

```bash
python scripts/label_windows.py \
  --windows data/processed/seizeit2/windows.parquet \
  --events data/processed/seizeit2/events.parquet \
  --output data/processed/seizeit2/labels_sph5_sop30.parquet \
  --sph-minutes 5 \
  --sop-minutes 30
```

Then inspect labels:

```bash
python scripts/inspect_labels.py \
  --labels data/processed/seizeit2/labels_sph5_sop30.parquet \
  --events data/processed/seizeit2/events.parquet
```

For MSG, also run the horizon viability audit before selecting a headline SPH/SOP:

```bash
make msg-horizon-viability
```

If SPH60/SOP1440 is coverage-limited, it can remain an exploratory or negative analysis, but it
must not become the main table without advisor approval.

## Stage B2 — blocking manual audit gate

Generate and fill the review sheet:

```bash
make msg-label-audit-sheet
```

After a human has verified the source annotations and filled every decision column, run:

```bash
make msg-label-audit-check
```

This gate is expected to fail on an unfilled sheet. Do not bypass it for A100 training.

## Stage C — EpiTwin-SSL first real run

Use only after Stage B and Stage B2 pass manual audit.

Recommended initial config:
- Modalities: ECG + ACC + EMG features.
- Window: 120 s.
- Stride: 30 s.
- Horizon: SPH 5 / SOP 30.
- Backbone: TCN first, then Mamba/CfC ablations.
- Mixed precision: bf16.

## Stage D — ablations

Run:
- no SSL;
- masked only;
- future latent only;
- cross-modal;
- no uncertainty;
- no patient adapter;
- full modalities vs edge modalities.
