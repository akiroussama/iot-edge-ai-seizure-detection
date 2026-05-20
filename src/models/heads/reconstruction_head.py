from __future__ import annotations

import torch
from torch import nn


class ReconstructionHead(nn.Module):
    def __init__(self, hidden_dim: int, output_channels: int) -> None:
        super().__init__()
        self.proj = nn.Linear(hidden_dim, output_channels)

    def forward(self, z: torch.Tensor) -> torch.Tensor:
        return self.proj(z)
