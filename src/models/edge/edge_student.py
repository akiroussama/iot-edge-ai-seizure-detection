from __future__ import annotations

from dataclasses import dataclass

import torch
from torch import nn
import torch.nn.functional as F

from src.models.backbones.gru import CausalGRUBackbone
from src.models.heads.hazard_head import HazardHead
from src.models.heads.uncertainty_head import UncertaintyHead


@dataclass(frozen=True)
class EdgeStudentConfig:
    input_dim: int = 8
    hidden_dim: int = 32
    layers: int = 1


class EdgeObservableStudent(nn.Module):
    """Tiny student estimating observable latent risk from edge-compatible features."""

    def __init__(self, config: EdgeStudentConfig) -> None:
        super().__init__()
        self.in_proj = nn.Linear(config.input_dim, config.hidden_dim)
        self.backbone = CausalGRUBackbone(config.hidden_dim, layers=config.layers)
        self.hazard_head = HazardHead(config.hidden_dim)
        self.uncertainty_head = UncertaintyHead(config.hidden_dim)

    def forward(self, x: torch.Tensor) -> dict[str, torch.Tensor | dict[str, torch.Tensor]]:
        # x: [B,T,F]
        z = self.backbone(F.gelu(self.in_proj(x)))
        return {"z": z, "hazard": self.hazard_head(z), "uncertainty": self.uncertainty_head(z)}


def observable_latent_distillation_loss(
    student_z: torch.Tensor,
    teacher_z: torch.Tensor,
    teacher_uncertainty: torch.Tensor | None = None,
) -> torch.Tensor:
    """Distill only predictable/observable latent components.

    If teacher_uncertainty is provided, high-uncertainty positions receive lower weight.
    """
    if student_z.shape != teacher_z.shape:
        raise ValueError(f"shape mismatch: {student_z.shape} vs {teacher_z.shape}")
    per_step = torch.mean((student_z - teacher_z.detach()) ** 2, dim=-1)
    if teacher_uncertainty is None:
        return per_step.mean()
    weights = 1.0 - teacher_uncertainty.detach().clamp(0.0, 1.0)
    return torch.sum(per_step * weights) / torch.clamp(weights.sum(), min=1e-6)
