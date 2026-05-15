from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import torch
from torch import nn

torch.set_num_threads(1)

from src.models.epitwin_ssl import EpiTwinConfig, EpiTwinSSL, future_latent_prediction_loss, masked_reconstruction_loss


def make_synthetic_batch(batch_size: int, time_steps: int, channels: int, modalities: list[str]) -> dict:
    signals = {m: torch.randn(batch_size, time_steps, channels) for m in modalities}
    return {"signals": signals, "delta_t": torch.ones(batch_size, time_steps, 1)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Smoke-train EpiTwin-SSL on synthetic tensors.")
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--time-steps", type=int, default=64)
    parser.add_argument("--hidden-dim", type=int, default=32)
    parser.add_argument("--backbone", choices=["tcn", "gru", "transformer", "cfc", "mamba_placeholder"], default="tcn")
    args = parser.parse_args()

    modalities = ["ecg", "acc", "emg"]
    model = EpiTwinSSL(EpiTwinConfig(modalities=tuple(modalities), hidden_dim=args.hidden_dim, backbone=args.backbone))
    opt = torch.optim.AdamW(model.parameters(), lr=1e-3)
    for epoch in range(args.epochs):
        batch = make_synthetic_batch(args.batch_size, args.time_steps, 1, modalities)
        out = model(batch)
        loss = masked_reconstruction_loss(out, batch, modalities) + 0.1 * future_latent_prediction_loss(out)
        opt.zero_grad()
        loss.backward()
        nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
        print({"epoch": epoch, "loss": float(loss.detach())})


if __name__ == "__main__":
    main()
