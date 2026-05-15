from __future__ import annotations

import torch
from torch import nn


class GatedMultimodalFusion(nn.Module):
    """Fuse available modality embeddings with learned modality gates.

    Inputs are a dict of tensors [B, T, D]. Missing modalities can be None. The module returns
    a fused tensor [B, T, D] and a dict of scalar gates for interpretability.
    """

    def __init__(self, hidden_dim: int, modalities: list[str]) -> None:
        super().__init__()
        self.modalities = list(modalities)
        self.gates = nn.ModuleDict({m: nn.Linear(hidden_dim, 1) for m in self.modalities})
        self.proj = nn.Linear(hidden_dim, hidden_dim)

    def forward(self, embeddings: dict[str, torch.Tensor | None]) -> tuple[torch.Tensor, dict[str, torch.Tensor]]:
        available = [(m, embeddings.get(m)) for m in self.modalities if embeddings.get(m) is not None]
        if not available:
            raise ValueError("at least one modality embedding must be available")
        weighted = []
        gate_values: dict[str, torch.Tensor] = {}
        for m, emb in available:
            assert emb is not None
            gate = torch.sigmoid(self.gates[m](emb))
            gate_values[m] = gate
            weighted.append(emb * gate)
        fused = torch.stack(weighted, dim=0).sum(dim=0) / (torch.stack([gate_values[m] for m, _ in available], dim=0).sum(dim=0) + 1e-6)
        return self.proj(fused), gate_values
