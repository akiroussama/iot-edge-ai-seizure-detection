from __future__ import annotations

import torch

from src.models.edge.edge_student import EdgeObservableStudent, EdgeStudentConfig, observable_latent_distillation_loss
from src.models.epitwin_ssl import EpiTwinConfig, EpiTwinSSL, future_latent_prediction_loss, masked_reconstruction_loss, modality_dropout


def test_epitwin_ssl_forward_shapes() -> None:
    modalities = ("ecg", "acc")
    model = EpiTwinSSL(EpiTwinConfig(modalities=modalities, hidden_dim=16, backbone="tcn"))
    batch = {"signals": {m: torch.randn(2, 12, 1) for m in modalities}}
    out = model(batch)
    assert out["z"].shape == (2, 12, 16)
    assert out["hazard"]["risk_score"].shape == (2,)
    assert torch.isfinite(masked_reconstruction_loss(out, batch, modalities))
    assert torch.isfinite(future_latent_prediction_loss(out))


def test_epitwin_ssl_missing_modality() -> None:
    modalities = ("ecg", "acc")
    model = EpiTwinSSL(EpiTwinConfig(modalities=modalities, hidden_dim=16, backbone="gru"))
    batch = {"signals": {"ecg": torch.randn(2, 12, 1), "acc": None}}
    out = model(batch)
    assert out["z"].shape == (2, 12, 16)


def test_modality_dropout_keeps_one_modality() -> None:
    signals = {"ecg": torch.ones(1, 4, 1), "acc": torch.ones(1, 4, 1)}
    dropped = modality_dropout(signals, drop_prob=1.0, training=True)
    assert sum(v is not None for v in dropped.values()) >= 1


def test_edge_student_and_distillation_loss() -> None:
    model = EdgeObservableStudent(EdgeStudentConfig(input_dim=4, hidden_dim=8))
    out = model(torch.randn(2, 10, 4))
    assert out["z"].shape == (2, 10, 8)
    loss = observable_latent_distillation_loss(out["z"], torch.randn(2, 10, 8), out["uncertainty"])
    assert torch.isfinite(loss)
