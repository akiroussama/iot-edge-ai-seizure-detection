from __future__ import annotations

import numpy as np
import pandas as pd

from src.metrics.alarm_metrics import false_alarm_rate_per_day, median_lead_time, time_in_warning
from src.metrics.calibration import brier_score, expected_calibration_error
from src.metrics.event_metrics import event_level_sensitivity


def _threshold_grid(thresholds: int | list[float]) -> np.ndarray:
    if isinstance(thresholds, int):
        if thresholds < 2:
            raise ValueError("thresholds must be >= 2 when passed as an integer")
        return np.linspace(0, 1, thresholds)
    return np.array(thresholds, dtype=float)


def _split_value(expression: str | None) -> str | None:
    if expression is None or "=" not in expression:
        return None
    column, value = expression.split("=", maxsplit=1)
    return value if column == "split" else None


def _filter_rows(df: pd.DataFrame, expression: str | None, name: str) -> pd.DataFrame:
    if expression is None:
        return df
    if "=" not in expression:
        raise ValueError(f"{name} must be formatted as column=value")
    column, value = expression.split("=", maxsplit=1)
    if column not in df.columns:
        raise ValueError(f"{name} column not found: {column}")
    return df.loc[df[column].astype(str).eq(value)].reset_index(drop=True)


def scope_predictions_for_threshold_sweep(
    predictions_df: pd.DataFrame,
    sweep_filter: str | None = None,
    allow_unsplit_exploratory: bool = False,
    allow_test_sweep: bool = False,
) -> tuple[pd.DataFrame, dict[str, object]]:
    """Return threshold-tuning rows after enforcing split-safe sweep scope.

    Threshold sweeps are a calibration operation. They must be run on calibration or validation
    rows, not on final test rows. This guard lives in the library so notebooks and future scripts
    cannot bypass the safer CLI defaults by calling the metric primitive directly.
    """
    if "split" not in predictions_df.columns:
        if not allow_unsplit_exploratory:
            raise ValueError(
                "predictions have no split column. Refusing threshold sweep because calibration/test scope "
                "is ambiguous. Pass allow_unsplit_exploratory=True only for non-publishable diagnostics."
            )
        scoped = predictions_df.reset_index(drop=True)
        metadata = {
            "sweep_filter": "none",
            "publishable_threshold_tuning": False,
            "falsifiability": (
                "This sweep is exploratory only because predictions have no split column. It must not be "
                "used for publishable threshold selection."
            ),
        }
        return scoped, metadata

    if sweep_filter is None:
        raise ValueError(
            "predictions contain split column; pass sweep_filter='split=val' or another calibration split "
            "(CLI: pass --sweep-filter split=val). "
            "Do not sweep thresholds on the full table."
        )
    filter_column = sweep_filter.split("=", maxsplit=1)[0].strip()
    if filter_column != "split":
        raise ValueError(
            f"sweep_filter must scope to the split column, e.g. 'split=val'; got {sweep_filter!r}. "
            "A non-split filter such as score_fit_split=train selects a constant column and would "
            "sweep thresholds across train/val/test (Phase R audit C1 Gap 2)."
        )
    value = _split_value(sweep_filter)
    if value == "test" and not allow_test_sweep:
        raise ValueError(
            "refusing threshold sweep on split=test. Use validation/calibration rows for threshold tuning, "
            "or pass allow_test_sweep=True only for a clearly non-publishable diagnostic."
        )
    scoped = _filter_rows(predictions_df, sweep_filter, "sweep filter")
    if scoped.empty:
        raise ValueError(f"sweep filter produced no prediction rows: {sweep_filter}")
    publishable = bool(value and value != "test")
    metadata = {
        "sweep_filter": sweep_filter,
        "publishable_threshold_tuning": publishable,
        "falsifiability": (
            "This sweep is valid for threshold selection only if the sweep rows are calibration/validation "
            "rows that are disjoint from final test reporting."
        ),
    }
    return scoped.reset_index(drop=True), metadata


def sensitivity_at_fixed_far(
    predictions_df: pd.DataFrame,
    events_df: pd.DataFrame,
    sph_minutes: float,
    sop_minutes: float,
    max_far_per_day: float,
    thresholds: int | list[float] = 101,
    sweep_filter: str | None = None,
    allow_unsplit_exploratory: bool = False,
    allow_test_sweep: bool = False,
) -> dict[str, float]:
    """Sweep thresholds and return the best sensitivity satisfying FAR/day constraint."""
    scoped_predictions, metadata = scope_predictions_for_threshold_sweep(
        predictions_df,
        sweep_filter=sweep_filter,
        allow_unsplit_exploratory=allow_unsplit_exploratory,
        allow_test_sweep=allow_test_sweep,
    )
    ths = _threshold_grid(thresholds)
    best = {"threshold": float("nan"), "sensitivity": float("nan"), "far_per_day": float("nan")}
    for th in ths:
        df = scoped_predictions.copy()
        df["alarm"] = df["risk_score"].astype(float) >= th
        far = false_alarm_rate_per_day(df, events_df, sph_minutes, sop_minutes)
        if np.isnan(far) or far > max_far_per_day:
            continue
        sens = event_level_sensitivity(df, events_df, sph_minutes, sop_minutes)["sensitivity"]
        if np.isnan(best["sensitivity"]) or sens > best["sensitivity"]:
            best = {"threshold": float(th), "sensitivity": float(sens), "far_per_day": float(far)}
    best.update(metadata)
    return best


def sensitivity_at_fixed_time_in_warning(
    predictions_df: pd.DataFrame,
    events_df: pd.DataFrame,
    sph_minutes: float,
    sop_minutes: float,
    max_time_in_warning: float,
    thresholds: int | list[float] = 101,
    sweep_filter: str | None = None,
    allow_unsplit_exploratory: bool = False,
    allow_test_sweep: bool = False,
) -> dict[str, float]:
    """Sweep thresholds and return best event sensitivity under a warning-time budget."""
    if not 0 <= max_time_in_warning <= 1:
        raise ValueError("max_time_in_warning must be in [0, 1]")
    scoped_predictions, metadata = scope_predictions_for_threshold_sweep(
        predictions_df,
        sweep_filter=sweep_filter,
        allow_unsplit_exploratory=allow_unsplit_exploratory,
        allow_test_sweep=allow_test_sweep,
    )
    ths = _threshold_grid(thresholds)
    best = {"threshold": float("nan"), "sensitivity": float("nan"), "time_in_warning": float("nan")}
    for th in ths:
        df = scoped_predictions.copy()
        df["alarm"] = df["risk_score"].astype(float) >= th
        tiw = time_in_warning(df)
        if np.isnan(tiw) or tiw > max_time_in_warning:
            continue
        sens = event_level_sensitivity(df, events_df, sph_minutes, sop_minutes)["sensitivity"]
        if np.isnan(best["sensitivity"]) or sens > best["sensitivity"]:
            best = {"threshold": float(th), "sensitivity": float(sens), "time_in_warning": float(tiw)}
    best.update(metadata)
    return best


def threshold_sweep_table(
    predictions_df: pd.DataFrame,
    events_df: pd.DataFrame,
    sph_minutes: float,
    sop_minutes: float,
    thresholds: int | list[float] = 101,
    sweep_filter: str | None = None,
    allow_unsplit_exploratory: bool = False,
    allow_test_sweep: bool = False,
) -> pd.DataFrame:
    """Return clinical metrics for a grid of alarm thresholds.

    The sweep uses existing risk scores and recomputes alarms at each threshold. Labels and
    excluded windows are passed through the metric functions, which exclude invalid windows.
    """
    if "risk_score" not in predictions_df.columns:
        raise ValueError("predictions_df must contain risk_score")
    scoped_predictions, metadata = scope_predictions_for_threshold_sweep(
        predictions_df,
        sweep_filter=sweep_filter,
        allow_unsplit_exploratory=allow_unsplit_exploratory,
        allow_test_sweep=allow_test_sweep,
    )
    ths = _threshold_grid(thresholds)
    rows = []
    for th in ths:
        df = scoped_predictions.copy()
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
    out = pd.DataFrame(rows)
    for key, value in metadata.items():
        out[key] = value
    return out


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
