from __future__ import annotations

from dataclasses import dataclass

import torch
from torch import nn


@dataclass(frozen=True)
class EncoderConfig:
    input_channels: int = 1
    hidden_dim: int = 64
    kernel_size: int = 5


class ConvSignalEncoder(nn.Module):
    """Small causal-ish 1D encoder for CPU-testable biosignal experiments.

    Input shape: [batch, time, channels]
    Output shape: [batch, time, hidden_dim]
    """

    def __init__(self, config: EncoderConfig) -> None:
        super().__init__()
        padding = config.kernel_size // 2
        self.net = nn.Sequential(
            nn.Conv1d(config.input_channels, config.hidden_dim, config.kernel_size, padding=padding),
            nn.GELU(),
            nn.Conv1d(config.hidden_dim, config.hidden_dim, config.kernel_size, padding=padding),
            nn.GELU(),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if x.ndim != 3:
            raise ValueError("expected [batch, time, channels]")
        y = self.net(x.transpose(1, 2)).transpose(1, 2)
        return y


class LinearFeatureEncoder(nn.Module):
    """Encoder for tabular per-window features, e.g. HR/steps summaries."""

    def __init__(self, input_dim: int, hidden_dim: int) -> None:
        super().__init__()
        self.net = nn.Sequential(nn.Linear(input_dim, hidden_dim), nn.GELU(), nn.Linear(hidden_dim, hidden_dim))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if x.ndim == 2:
            return self.net(x)
        if x.ndim == 3:
            return self.net(x)
        raise ValueError("expected [batch, features] or [batch, time, features]")
