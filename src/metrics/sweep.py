from __future__ import annotations

import numpy as np
import pandas as pd

from src.metrics.alarm_metrics import false_alarm_rate_per_day, median_lead_time, time_in_warning
from src.metrics.calibration import brier_score, expected_calibration_error
from src.metrics.event_metrics import event_level_sensitivity


def sensitivity_at_fixed_far(
    predictions_df: pd.DataFrame,
    events_df: pd.DataFrame,
    sph_minutes: float,
    sop_minutes: float,
    max_far_per_day: float,
    thresholds: int | list[float] = 101,
) -> dict[str, float]:
    """Sweep thresholds and return the best sensitivity satisfying FAR/day constraint."""
    if isinstance(thresholds, int):
        ths = np.linspace(0, 1, thresholds)
    else:
        ths = np.array(thresholds, dtype=float)
    best = {"threshold": float("nan"), "sensitivity": float("nan"), "far_per_day": float("nan")}
    for th in ths:
        df = predictions_df.copy()
        df["alarm"] = df["risk_score"].astype(float) >= th
        far = false_alarm_rate_per_day(df, events_df, sph_minutes, sop_minutes)
        if np.isnan(far) or far > max_far_per_day:
            continue
        sens = event_level_sensitivity(df, events_df, sph_minutes, sop_minutes)["sensitivity"]
        if np.isnan(best["sensitivity"]) or sens > best["sensitivity"]:
            best = {"threshold": float(th), "sensitivity": float(sens), "far_per_day": float(far)}
    return best


def sensitivity_at_fixed_time_in_warning(
    predictions_df: pd.DataFrame,
    events_df: pd.DataFrame,
    sph_minutes: float,
    sop_minutes: float,
    max_time_in_warning: float,
    thresholds: int | list[float] = 101,
) -> dict[str, float]:
    """Sweep thresholds and return best event sensitivity under a warning-time budget."""
    if not 0 <= max_time_in_warning <= 1:
        raise ValueError("max_time_in_warning must be in [0, 1]")
    if isinstance(thresholds, int):
        ths = np.linspace(0, 1, thresholds)
    else:
        ths = np.array(thresholds, dtype=float)
    best = {"threshold": float("nan"), "sensitivity": float("nan"), "time_in_warning": float("nan")}
    for th in ths:
        df = predictions_df.copy()
        df["alarm"] = df["risk_score"].astype(float) >= th
        tiw = time_in_warning(df)
        if np.isnan(tiw) or tiw > max_time_in_warning:
            continue
        sens = event_level_sensitivity(df, events_df, sph_minutes, sop_minutes)["sensitivity"]
        if np.isnan(best["sensitivity"]) or sens > best["sensitivity"]:
            best = {"threshold": float(th), "sensitivity": float(sens), "time_in_warning": float(tiw)}
    return best


def threshold_sweep_table(
    predictions_df: pd.DataFrame,
    events_df: pd.DataFrame,
    sph_minutes: float,
    sop_minutes: float,
    thresholds: int | list[float] = 101,
) -> pd.DataFrame:
    """Return clinical metrics for a grid of alarm thresholds.

    The sweep uses existing risk scores and recomputes alarms at each threshold. Labels and
    excluded windows are passed through the metric functions, which exclude invalid windows.
    """
    if "risk_score" not in predictions_df.columns:
        raise ValueError("predictions_df must contain risk_score")
    if isinstance(thresholds, int):
        if thresholds < 2:
            raise ValueError("thresholds must be >= 2 when passed as an integer")
        ths = np.linspace(0, 1, thresholds)
    else:
        ths = np.array(thresholds, dtype=float)
    rows = []
    for th in ths:
        df = predictions_df.copy()
        df["alarm"] = df["risk_score"].astype(float) >= float(th)
        sens = event_level_sensitivity(df, events_df, sph_minutes, sop_minutes)
        rows.append(
            {
                "threshold": float(th),
                "sensitivity": sens["sensitivity"],
                "n_events": sens["n_events"],
                "n_forecasted": sens["n_forecasted"],
                "far_per_day": false_alarm_rate_per_day(
                    df, events_df, sph_minutes, sop_minutes
                ),
                "time_in_warning": time_in_warning(df),
                "median_lead_time_seconds": median_lead_time(
                    df, events_df, sph_minutes, sop_minutes
                ),
                "brier_score": brier_score(df),
                "ece": expected_calibration_error(df),
            }
        )
    return pd.DataFrame(rows)


def select_threshold_under_constraints(
    sweep_df: pd.DataFrame,
    max_far_per_day: float | None = None,
    max_time_in_warning: float | None = None,
) -> dict[str, float]:
    """Select threshold with best sensitivity under optional clinical constraints."""
    required = {"threshold", "sensitivity", "far_per_day", "time_in_warning"}
    missing = required - set(sweep_df.columns)
    if missing:
        raise ValueError(f"sweep_df missing required columns: {sorted(missing)}")
    valid = sweep_df.copy()
    if max_far_per_day is not None:
        valid = valid.loc[valid["far_per_day"] <= max_far_per_day]
    if max_time_in_warning is not None:
        valid = valid.loc[valid["time_in_warning"] <= max_time_in_warning]
    valid = valid.loc[valid["sensitivity"].notna()]
    if valid.empty:
        return {
            "threshold": float("nan"),
            "sensitivity": float("nan"),
            "far_per_day": float("nan"),
            "time_in_warning": float("nan"),
        }
    best = valid.sort_values(
        ["sensitivity", "far_per_day", "time_in_warning", "threshold"],
        ascending=[False, True, True, False],
    ).iloc[0]
    return {
        "threshold": float(best["threshold"]),
        "sensitivity": float(best["sensitivity"]),
        "far_per_day": float(best["far_per_day"]),
        "time_in_warning": float(best["time_in_warning"]),
    }
