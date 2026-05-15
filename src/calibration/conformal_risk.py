from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class ConformalRiskResult:
    threshold: float
    empirical_risk: float
    target_risk: float
    n: int


def calibrate_threshold_by_empirical_risk(
    calibration_df: pd.DataFrame,
    target_risk: float,
    score_col: str = "risk_score",
    loss_col: str = "false_alarm_loss",
    thresholds: int | list[float] = 101,
) -> ConformalRiskResult:
    """Simple empirical-risk threshold selector inspired by conformal risk control.

    This is not a formal exchangeability guarantee for temporally dependent biosignals. It is a
    transparent v0.1 calibration primitive that can be replaced by blocked/time-series conformal
    methods later.
    """
    if not 0 <= target_risk <= 1:
        raise ValueError("target_risk must be in [0, 1]")
    if score_col not in calibration_df.columns or loss_col not in calibration_df.columns:
        raise ValueError(f"calibration_df must contain {score_col} and {loss_col}")
    ths = np.linspace(0.0, 1.0, thresholds) if isinstance(thresholds, int) else np.asarray(thresholds, dtype=float)
    best = None
    for th in sorted(ths):
        alarms = calibration_df[score_col].astype(float).to_numpy() >= float(th)
        if alarms.sum() == 0:
            risk = 0.0
        else:
            risk = float(np.mean(calibration_df.loc[alarms, loss_col].astype(float)))
        if risk <= target_risk:
            best = ConformalRiskResult(float(th), risk, target_risk, int(len(calibration_df)))
            break
    if best is None:
        best = ConformalRiskResult(float("nan"), float("nan"), target_risk, int(len(calibration_df)))
    return best
