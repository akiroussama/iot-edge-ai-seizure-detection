from __future__ import annotations

import torch
from torch import nn


class TinyCfCBackbone(nn.Module):
    """Tiny continuous-time inspired backbone.

    This is a CPU-testable placeholder, not a faithful CfC/LTC implementation. It exposes the
    same interface so that real CfC/LTC layers can be swapped in later.
    """

    def __init__(self, hidden_dim: int) -> None:
        super().__init__()
        self.ff = nn.Linear(hidden_dim, hidden_dim)
        self.gate = nn.Linear(hidden_dim, hidden_dim)
        self.norm = nn.LayerNorm(hidden_dim)

    def forward(self, x: torch.Tensor, delta_t: torch.Tensor | None = None) -> torch.Tensor:
        if delta_t is None:
            delta_t = torch.ones(x.shape[0], x.shape[1], 1, device=x.device, dtype=x.dtype)
        if delta_t.ndim == 2:
            delta_t = delta_t.unsqueeze(-1)
        state = torch.zeros_like(x[:, 0])
        outs = []
        for i in range(x.shape[1]):
            alpha = torch.sigmoid(self.gate(x[:, i]) * delta_t[:, i].clamp_min(1e-6))
            candidate = torch.tanh(self.ff(x[:, i]))
            state = (1.0 - alpha) * state + alpha * candidate
            outs.append(state)
        return self.norm(torch.stack(outs, dim=1))
