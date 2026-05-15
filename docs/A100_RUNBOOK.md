# A100 runbook

## Do not train before benchmark validation

The A100 is not the bottleneck. Bad labels and leakage are the bottleneck.

## Stage A — smoke tests

```bash
python -m pytest -q
python scripts/run_synthetic_demo.py
python scripts/train_epitwin_ssl.py --epochs 3 --backbone tcn
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

## Stage C — EpiTwin-SSL first real run

Use only after Stage B passes manual audit.

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
