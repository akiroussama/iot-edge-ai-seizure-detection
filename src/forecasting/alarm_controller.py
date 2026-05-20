from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from src.metrics.alarm_metrics import false_alarm_rate_per_day, time_in_warning
from src.metrics.event_metrics import event_level_sensitivity


@dataclass(frozen=True)
class AlarmControllerConfig:
    max_far_per_day: float = 1.0
    max_time_in_warning: float = 0.2
    min_signal_quality: float = 0.0
    max_uncertainty: float = 1.0


def apply_alarm_threshold(
    predictions: pd.DataFrame,
    threshold: float,
    uncertainty_col: str | None = "uncertainty",
    quality_col: str | None = "signal_quality",
    config: AlarmControllerConfig | None = None,
) -> pd.DataFrame:
    """Apply clinical alarm gating: risk threshold + uncertainty + signal quality."""
    cfg = config or AlarmControllerConfig()
    df = predictions.copy()
    if "risk_score" not in df.columns:
        raise ValueError("predictions must contain risk_score")
    alarm = df["risk_score"].astype(float) >= float(threshold)
    if uncertainty_col and uncertainty_col in df.columns:
        alarm &= df[uncertainty_col].astype(float) <= cfg.max_uncertainty
    if quality_col and quality_col in df.columns:
        alarm &= df[quality_col].astype(float) >= cfg.min_signal_quality
    df["alarm"] = alarm.astype(bool)
    df["alarm_threshold"] = float(threshold)
    return df


def choose_threshold_under_budget(
    predictions: pd.DataFrame,
    events: pd.DataFrame,
    sph_minutes: float,
    sop_minutes: float,
    config: AlarmControllerConfig | None = None,
    thresholds: int | list[float] = 101,
) -> dict[str, float]:
    """Pick threshold maximizing sensitivity under FAR/day and Time-in-Warning constraints."""
    cfg = config or AlarmControllerConfig()
    ths = np.linspace(0.0, 1.0, thresholds) if isinstance(thresholds, int) else np.asarray(thresholds, dtype=float)
    best = {
        "threshold": float("nan"),
        "sensitivity": float("nan"),
        "far_per_day": float("nan"),
        "time_in_warning": float("nan"),
    }
    for th in ths:
        cand = apply_alarm_threshold(predictions, float(th), config=cfg)
        far = false_alarm_rate_per_day(cand, events, sph_minutes, sop_minutes)
        tiw = time_in_warning(cand)
        if np.isnan(far) or np.isnan(tiw) or far > cfg.max_far_per_day or tiw > cfg.max_time_in_warning:
            continue
        sens = event_level_sensitivity(cand, events, sph_minutes, sop_minutes)["sensitivity"]
        if np.isnan(best["sensitivity"]) or sens > best["sensitivity"]:
            best = {
                "threshold": float(th),
                "sensitivity": float(sens),
                "far_per_day": float(far),
                "time_in_warning": float(tiw),
            }
    return best
