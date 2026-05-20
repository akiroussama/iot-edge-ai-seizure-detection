from __future__ import annotations

from src.models.backbones.gru import CausalGRUBackbone


class MambaPlaceholderBackbone(CausalGRUBackbone):
    """Interface placeholder for causal Mamba-2.

    The real implementation should use an audited mamba-ssm dependency. Until then, this class
    behaves as a GRU so the pipeline remains testable and dependency-light.
    """

    def __init__(self, hidden_dim: int, layers: int = 1) -> None:
        super().__init__(hidden_dim=hidden_dim, layers=layers)
        self.placeholder_name = "mamba2_placeholder_gru"
