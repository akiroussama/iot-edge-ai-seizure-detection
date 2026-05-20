from __future__ import annotations

import torch
from torch import nn


class HazardHead(nn.Module):
    """Outputs non-negative seizure intensity and horizon risk."""

    def __init__(self, hidden_dim: int) -> None:
        super().__init__()
        self.net = nn.Sequential(nn.Linear(hidden_dim, hidden_dim), nn.GELU(), nn.Linear(hidden_dim, 1))
        self.softplus = nn.Softplus()

    def forward(self, z: torch.Tensor, horizon_steps: int | None = None) -> dict[str, torch.Tensor]:
        hazard = self.softplus(self.net(z)).squeeze(-1)
        if horizon_steps is None:
            horizon_steps = z.shape[1]
        h = hazard[:, -horizon_steps:]
        risk = 1.0 - torch.exp(-torch.cumsum(h, dim=1))
        return {"hazard": hazard, "risk_sequence": risk, "risk_score": risk[:, -1]}


def point_process_nll_torch(hazard: torch.Tensor, event: torch.Tensor, dt: float = 1.0, eps: float = 1e-8) -> torch.Tensor:
    hazard = torch.clamp(hazard, min=eps)
    event = event.to(dtype=hazard.dtype)
    if hazard.shape != event.shape:
        raise ValueError(f"hazard shape {tuple(hazard.shape)} != event shape {tuple(event.shape)}")
    return torch.mean(torch.sum(hazard * dt - event * torch.log(hazard + eps), dim=-1))
