from __future__ import annotations

import numpy as np
import pandas as pd

from src.utils.time import ensure_datetime


def period_key(period_hours: float) -> str:
    if float(period_hours).is_integer():
        return f"{int(period_hours)}h"
    text = str(float(period_hours)).replace(".", "p")
    return f"{text}h"


def add_cycle_phase_features(
    windows: pd.DataFrame,
    *,
    period_hours: tuple[float, ...] = (24.0, 168.0),
    time_col: str = "window_end",
) -> pd.DataFrame:
    """Append deterministic cyclic phase features from window timestamps.

    The features depend only on timestamps and fixed periods, not on labels or
    future observations. They are safe to compute before train/validation/test
    splitting.
    """
    if time_col not in windows.columns:
        raise ValueError(f"windows must contain {time_col}")
    out = windows.copy()
    out[time_col] = ensure_datetime(out[time_col])
    epoch_seconds = (out[time_col] - pd.Timestamp("1970-01-01")).dt.total_seconds()
    for period in period_hours:
        if period <= 0:
            raise ValueError("period_hours values must be positive")
        key = period_key(period)
        period_seconds = float(period) * 3600.0
        phase = np.mod(epoch_seconds, period_seconds) / period_seconds
        out[f"cycle_{key}_phase"] = phase.astype(float)
        out[f"cycle_{key}_sin"] = np.sin(2.0 * np.pi * phase)
        out[f"cycle_{key}_cos"] = np.cos(2.0 * np.pi * phase)
    return out
