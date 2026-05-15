from __future__ import annotations


def is_torch_available() -> bool:
    try:
        import torch  # noqa: F401

        return True
    except Exception:
        return False


class TorchNotAvailableError(RuntimeError):
    pass


def build_tcn_small(*args, **kwargs):
    """Optional placeholder for the first supervised baseline.

    The 48h milestone prioritizes labels/metrics. This function avoids importing torch unless
    the user explicitly starts model training.
    """
    if not is_torch_available():
        raise TorchNotAvailableError("Install epitwin-open[torch] to use tcn_small")
    import torch
    from torch import nn

    input_channels = kwargs.get("input_channels", 4)
    hidden = kwargs.get("hidden", 32)
    kernel_size = kwargs.get("kernel_size", 5)

    class SmallTCN(nn.Module):
        def __init__(self):
            super().__init__()
            self.net = nn.Sequential(
                nn.Conv1d(input_channels, hidden, kernel_size, padding=kernel_size // 2),
                nn.ReLU(),
                nn.Conv1d(hidden, hidden, kernel_size, padding=kernel_size // 2),
                nn.ReLU(),
                nn.AdaptiveAvgPool1d(1),
            )
            self.head = nn.Linear(hidden, 1)

        def forward(self, x):
            z = self.net(x).squeeze(-1)
            return torch.sigmoid(self.head(z)).squeeze(-1)

    return SmallTCN()
