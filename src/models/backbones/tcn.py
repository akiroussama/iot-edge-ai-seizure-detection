from __future__ import annotations

import torch
from torch import nn


class CausalConv1d(nn.Module):
    def __init__(self, channels: int, kernel_size: int, dilation: int) -> None:
        super().__init__()
        self.padding = (kernel_size - 1) * dilation
        self.conv = nn.Conv1d(channels, channels, kernel_size, dilation=dilation, padding=self.padding)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        y = self.conv(x)
        if self.padding > 0:
            y = y[..., :-self.padding]
        return y


class CausalTCN(nn.Module):
    """Small causal TCN backbone.

    Input/output shape: [B, T, D]
    """

    def __init__(self, hidden_dim: int, layers: int = 3, kernel_size: int = 3) -> None:
        super().__init__()
        blocks = []
        for i in range(layers):
            dilation = 2**i
            blocks.append(
                nn.Sequential(
                    CausalConv1d(hidden_dim, kernel_size, dilation),
                    nn.GELU(),
                    nn.Conv1d(hidden_dim, hidden_dim, 1),
                )
            )
        self.blocks = nn.ModuleList(blocks)
        self.norm = nn.LayerNorm(hidden_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        y = x.transpose(1, 2)
        for block in self.blocks:
            residual = y
            y = block(y) + residual
        return self.norm(y.transpose(1, 2))
