from __future__ import annotations

from dataclasses import dataclass

import torch
from torch import nn
import torch.nn.functional as F

from src.models.backbones.causal_transformer import CausalTransformerBackbone
from src.models.backbones.cfc_placeholder import TinyCfCBackbone
from src.models.backbones.gru import CausalGRUBackbone
from src.models.backbones.mamba_placeholder import MambaPlaceholderBackbone
from src.models.backbones.tcn import CausalTCN
from src.models.encoders.simple_encoders import ConvSignalEncoder, EncoderConfig
from src.models.fusion.multimodal_fusion import GatedMultimodalFusion
from src.models.heads.hazard_head import HazardHead
from src.models.heads.reconstruction_head import ReconstructionHead
from src.models.heads.uncertainty_head import UncertaintyHead


@dataclass(frozen=True)
class EpiTwinConfig:
    modalities: tuple[str, ...] = ("ecg", "acc", "emg")
    input_channels: int = 1
    hidden_dim: int = 32
    backbone: str = "tcn"
    backbone_layers: int = 2


def _make_backbone(name: str, hidden_dim: int, layers: int) -> nn.Module:
    if name == "tcn":
        return CausalTCN(hidden_dim, layers=layers)
    if name == "gru":
        return CausalGRUBackbone(hidden_dim, layers=layers)
    if name == "transformer":
        return CausalTransformerBackbone(hidden_dim, layers=max(1, layers))
    if name == "cfc":
        return TinyCfCBackbone(hidden_dim)
    if name == "mamba_placeholder":
        return MambaPlaceholderBackbone(hidden_dim, layers=layers)
    raise ValueError(f"unknown backbone: {name}")


class EpiTwinSSL(nn.Module):
    """CPU-testable v0.1 of the EpiTwin predictive coding model.

    Batch format:
    {
      "signals": {"ecg": Tensor[B,T,C] or None, ...},
      "delta_t": optional Tensor[B,T,1]
    }
    """

    def __init__(self, config: EpiTwinConfig) -> None:
        super().__init__()
        self.config = config
        self.modalities = list(config.modalities)
        self.encoders = nn.ModuleDict(
            {
                m: ConvSignalEncoder(EncoderConfig(input_channels=config.input_channels, hidden_dim=config.hidden_dim))
                for m in self.modalities
            }
        )
        self.fusion = GatedMultimodalFusion(config.hidden_dim, self.modalities)
        self.backbone = _make_backbone(config.backbone, config.hidden_dim, config.backbone_layers)
        self.hazard_head = HazardHead(config.hidden_dim)
        self.uncertainty_head = UncertaintyHead(config.hidden_dim)
        self.reconstruction_heads = nn.ModuleDict(
            {m: ReconstructionHead(config.hidden_dim, config.input_channels) for m in self.modalities}
        )
        self.future_head = nn.Linear(config.hidden_dim, config.hidden_dim)

    def forward(self, batch: dict) -> dict[str, object]:
        signals: dict[str, torch.Tensor | None] = batch["signals"]
        embeddings: dict[str, torch.Tensor | None] = {}
        for m in self.modalities:
            x = signals.get(m)
            embeddings[m] = self.encoders[m](x) if x is not None else None
        fused, gates = self.fusion(embeddings)
        if isinstance(self.backbone, TinyCfCBackbone):
            z = self.backbone(fused, batch.get("delta_t"))
        else:
            z = self.backbone(fused)
        recon = {m: self.reconstruction_heads[m](z) for m in self.modalities}
        hazard = self.hazard_head(z)
        uncertainty = self.uncertainty_head(z)
        future_z = self.future_head(z)
        return {
            "z": z,
            "future_z": future_z,
            "recon": recon,
            "hazard": hazard,
            "uncertainty": uncertainty,
            "gates": gates,
        }


def modality_dropout(signals: dict[str, torch.Tensor | None], drop_prob: float, training: bool = True) -> dict[str, torch.Tensor | None]:
    if not training or drop_prob <= 0:
        return dict(signals)
    out = dict(signals)
    available = [m for m, x in out.items() if x is not None]
    if len(available) <= 1:
        return out
    for m in available:
        if torch.rand(()) < drop_prob and sum(v is not None for v in out.values()) > 1:
            out[m] = None
    return out


def masked_reconstruction_loss(outputs: dict, batch: dict, modalities: list[str] | tuple[str, ...]) -> torch.Tensor:
    losses = []
    signals = batch["signals"]
    for m in modalities:
        target = signals.get(m)
        if target is None:
            continue
        pred = outputs["recon"][m]
        losses.append(F.mse_loss(pred, target))
    if not losses:
        raise ValueError("no available modalities for reconstruction loss")
    return torch.stack(losses).mean()


def future_latent_prediction_loss(outputs: dict, steps: int = 1) -> torch.Tensor:
    z = outputs["z"].detach()
    pred = outputs["future_z"]
    if z.shape[1] <= steps:
        return F.mse_loss(pred, z)
    return F.mse_loss(pred[:, :-steps], z[:, steps:])


def cross_modal_prediction_loss(outputs: dict, batch: dict, modalities: list[str] | tuple[str, ...]) -> torch.Tensor:
    # v0.1 proxy: reconstruction of all available modalities from shared latent.
    return masked_reconstruction_loss(outputs, batch, modalities)
