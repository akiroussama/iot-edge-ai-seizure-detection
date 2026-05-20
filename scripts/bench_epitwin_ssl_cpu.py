#!/usr/bin/env python
"""CPU timing benchmark for EpiTwin-SSL.

Estimates Phase E training time on a non-A100 (CPU) machine by timing the
real EpiTwinSSL forward + backward + optimizer step on synthetic batches,
then extrapolating to the full SeizeIT2 processed-window count.

This is NOT the real training pipeline (that runs on real data and is built
in Phase E). It measures per-window compute cost only; real training adds
data-loading I/O on top -- so the figures here are a lower bound. The config
sizes are assumptions, printed in the output; the real Stage C config is not
yet pinned.
"""
from __future__ import annotations

import os
import platform
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import torch
from torch import nn

from src.models.epitwin_ssl import (
    EpiTwinConfig,
    EpiTwinSSL,
    future_latent_prediction_loss,
    masked_reconstruction_loss,
)

MODALITIES = ["ecg", "acc", "emg"]
# SeizeIT2 processed window count (scripts/verify_processed_data.py full-data run).
SEIZEIT2_WINDOWS = 1_385_203


def make_batch(batch_size: int, time_steps: int) -> dict:
    signals = {m: torch.randn(batch_size, time_steps, 1) for m in MODALITIES}
    return {"signals": signals, "delta_t": torch.ones(batch_size, time_steps, 1)}


def bench(backbone: str, batch_size: int, time_steps: int, hidden_dim: int,
          warmup: int = 2, iters: int = 20) -> float:
    """Time one optimizer step; return seconds for one epoch over SEIZEIT2_WINDOWS."""
    model = EpiTwinSSL(
        EpiTwinConfig(modalities=tuple(MODALITIES), hidden_dim=hidden_dim, backbone=backbone)
    )
    opt = torch.optim.AdamW(model.parameters(), lr=1e-3)
    n_params = sum(p.numel() for p in model.parameters())

    def step() -> None:
        batch = make_batch(batch_size, time_steps)
        out = model(batch)
        loss = (
            masked_reconstruction_loss(out, batch, MODALITIES)
            + 0.1 * future_latent_prediction_loss(out)
        )
        opt.zero_grad()
        loss.backward()
        nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()

    for _ in range(warmup):
        step()
    t0 = time.perf_counter()
    for _ in range(iters):
        step()
    elapsed = time.perf_counter() - t0

    sec_per_iter = elapsed / iters
    windows_per_sec = batch_size / sec_per_iter
    epoch_sec = SEIZEIT2_WINDOWS / windows_per_sec
    print(f"  {backbone:12s} batch={batch_size} steps={time_steps} hidden={hidden_dim} "
          f"params={n_params:,}")
    print(f"    {sec_per_iter * 1000:8.1f} ms/step | {windows_per_sec:9,.0f} windows/s | "
          f"1 epoch (1.385M windows) = {epoch_sec / 60:6.1f} min")
    return epoch_sec


def main() -> None:
    print(f"host={platform.node()}  python={platform.python_version()}  torch={torch.__version__}")
    print(f"logical CPUs={os.cpu_count()}  torch threads={torch.get_num_threads()}")
    print()
    configs = [
        ("tcn", 64, 128, 64),
        ("tcn", 64, 128, 128),
        ("gru", 64, 128, 128),
    ]
    results: dict[str, float] = {}
    for backbone, batch, steps, hidden in configs:
        results[f"{backbone}-h{hidden}"] = bench(backbone, batch, steps, hidden)
        print()

    rep = results["tcn-h128"]
    print("=== extrapolation (tcn-h128, taken as a representative Stage C config) ===")
    for epochs in (20, 30, 50):
        run_h = rep * epochs / 3600
        print(f"  full SSL pretrain, {epochs:2d} epochs : {run_h:7.1f} h  ({run_h / 24:5.2f} days)")
    sweep_h = rep * 30 * 7 / 3600
    print(
        f"  Stage D ablation sweep (~7 variants x 30 epochs) : "
        f"{sweep_h:.0f} h ({sweep_h / 24:.1f} days)"
    )
    print()
    print("NOTE: synthetic-batch compute only -- real training adds data-loading I/O.")
    print("Epoch counts and model sizes are assumptions, not the pinned Stage C config.")


if __name__ == "__main__":
    main()
