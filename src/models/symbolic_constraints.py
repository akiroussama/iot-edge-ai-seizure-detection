from __future__ import annotations

import torch


def signal_quality_uncertainty_loss(signal_quality: torch.Tensor, uncertainty: torch.Tensor) -> torch.Tensor:
    """Soft rule: poor quality should increase uncertainty.

    If quality is low, target uncertainty is high. This is a differentiable proxy for a
    neuro-symbolic constraint and can be replaced by LTN-style logic later.
    """
    target = 1.0 - signal_quality.clamp(0.0, 1.0)
    return torch.mean((uncertainty - target) ** 2)


def tachycardia_context_rule_loss(
    tachycardia_score: torch.Tensor,
    motion_score: torch.Tensor,
    autonomic_risk: torch.Tensor,
) -> torch.Tensor:
    """Soft rule: tachycardia with low motion can support autonomic arousal.

    This is intentionally weak; it should regularize, not dictate, seizure risk.
    """
    evidence = torch.sigmoid(tachycardia_score) * (1.0 - torch.sigmoid(motion_score))
    return torch.mean(torch.relu(evidence - autonomic_risk))
