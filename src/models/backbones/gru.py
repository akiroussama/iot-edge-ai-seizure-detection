from __future__ import annotations

import torch
from torch import nn


class CausalGRUBackbone(nn.Module):
    """GRU baseline for latent physiological dynamics."""

    def __init__(self, hidden_dim: int, layers: int = 1, dropout: float = 0.0) -> None:
        super().__init__()
        self.gru = nn.GRU(hidden_dim, hidden_dim, num_layers=layers, batch_first=True, dropout=dropout if layers > 1 else 0.0)
        self.norm = nn.LayerNorm(hidden_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        y, _ = self.gru(x)
        return self.norm(y)
