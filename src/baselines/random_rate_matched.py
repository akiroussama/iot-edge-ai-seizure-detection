from __future__ import annotations

import numpy as np
import pandas as pd

from src.metrics.alarm_metrics import _union_duration_seconds


def generate_random_rate_matched_alarms(
    windows_df: pd.DataFrame,
    time_in_warning_fraction: float,
    seed: int = 42,
    group_col: str = "patient_id",
) -> pd.DataFrame:
    """Generate random alarms with approximately fixed time-in-warning fraction.

    This is a sanity baseline: a forecasting model should beat an alarm process with the same
    warning budget.
    """
    if not 0 <= time_in_warning_fraction <= 1:
        raise ValueError("time_in_warning_fraction must be in [0, 1]")
    rng = np.random.default_rng(seed)
    out = windows_df.copy()
    out["risk_score"] = 0.0
    out["alarm"] = False
    valid_mask = ~out.get("is_excluded", pd.Series(False, index=out.index)).fillna(False)
    groups = out.loc[valid_mask].groupby(group_col) if group_col in out.columns else [(None, out.loc[valid_mask])]
    for _, g in groups:
        n = len(g)
        if n == 0:
            continue
        out.loc[g.index, "risk_score"] = rng.uniform(0, 0.49, size=n)
        if time_in_warning_fraction == 0:
            continue
        if time_in_warning_fraction == 1:
            chosen = g.index.to_numpy()
        else:
            all_intervals = list(zip(g["window_start"], g["window_end"], strict=False))
            target_seconds = time_in_warning_fraction * _union_duration_seconds(all_intervals)
            chosen_intervals: list[tuple[pd.Timestamp, pd.Timestamp]] = []
            current_seconds = 0.0
            chosen_idx: list[object] = []
            for idx in rng.permutation(g.index.to_numpy()):
                row = g.loc[idx]
                candidate_intervals = chosen_intervals + [(row["window_start"], row["window_end"])]
                candidate_seconds = _union_duration_seconds(candidate_intervals)
                if candidate_seconds <= target_seconds or abs(candidate_seconds - target_seconds) < abs(
                    current_seconds - target_seconds
                ):
                    chosen_intervals = candidate_intervals
                    current_seconds = candidate_seconds
                    chosen_idx.append(idx)
            chosen = np.asarray(chosen_idx)
        if len(chosen) == 0:
            continue
        out.loc[chosen, "alarm"] = True
        # Provide a probability-like score useful for calibration sanity checks.
        out.loc[chosen, "risk_score"] = rng.uniform(0.5, 1.0, size=len(chosen))
    return out
