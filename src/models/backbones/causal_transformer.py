from __future__ import annotations

import torch
from torch import nn


class CausalTransformerBackbone(nn.Module):
    def __init__(self, hidden_dim: int, n_heads: int = 4, layers: int = 2, dropout: float = 0.0) -> None:
        super().__init__()
        enc_layer = nn.TransformerEncoderLayer(
            d_model=hidden_dim,
            nhead=n_heads,
            dim_feedforward=hidden_dim * 4,
            dropout=dropout,
            batch_first=True,
            activation="gelu",
        )
        self.encoder = nn.TransformerEncoder(enc_layer, num_layers=layers)
        self.norm = nn.LayerNorm(hidden_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        t = x.shape[1]
        mask = torch.triu(torch.ones(t, t, device=x.device, dtype=torch.bool), diagonal=1)
        return self.norm(self.encoder(x, mask=mask))
