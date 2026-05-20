from __future__ import annotations

import numpy as np
import torch

from src.forecasting.hazard import discrete_hazard_to_risk, point_process_nll_np
from src.models.heads.hazard_head import point_process_nll_torch


def test_discrete_hazard_to_risk_monotonic() -> None:
    hazard = np.array([0.0, 0.1, 0.2, 0.0])
    risk = discrete_hazard_to_risk(hazard)
    assert np.all(np.diff(risk) >= -1e-9)
    assert 0 <= risk[-1] <= 1


def test_point_process_nll_np_positive() -> None:
    hazard = np.array([[0.1, 0.2, 0.3]])
    event = np.array([[0, 0, 1]])
    assert point_process_nll_np(hazard, event) > 0


def test_point_process_nll_torch_finite() -> None:
    hazard = torch.tensor([[0.1, 0.2, 0.3]])
    event = torch.tensor([[0.0, 0.0, 1.0]])
    loss = point_process_nll_torch(hazard, event)
    assert torch.isfinite(loss)
