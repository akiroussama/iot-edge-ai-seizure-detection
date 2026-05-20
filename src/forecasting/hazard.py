from __future__ import annotations

import numpy as np
import pandas as pd


def discrete_hazard_to_risk(hazard: np.ndarray, dt_seconds: float = 1.0) -> np.ndarray:
    """Convert non-negative discrete hazard values into cumulative event risk.

    risk = 1 - exp(-sum(lambda_t * dt))
    """
    h = np.asarray(hazard, dtype=float)
    h = np.clip(h, 0.0, None)
    return 1.0 - np.exp(-np.cumsum(h * float(dt_seconds), axis=-1))


def point_process_nll_np(
    hazard: np.ndarray,
    event: np.ndarray,
    dt_seconds: float = 1.0,
    eps: float = 1e-8,
) -> float:
    """Discrete approximation of a survival/point-process negative log-likelihood.

    hazard and event must have the same shape. event[t] is 1 if event occurs at time t.
    This function is used for tests and non-torch sanity checks.
    """
    h = np.clip(np.asarray(hazard, dtype=float), eps, None)
    y = np.asarray(event, dtype=float)
    if h.shape != y.shape:
        raise ValueError(f"hazard shape {h.shape} does not match event shape {y.shape}")
    return float(np.sum(h * dt_seconds - y * np.log(h + eps)))


def add_discrete_hazard_targets(
    windows: pd.DataFrame,
    events: pd.DataFrame,
    horizon_minutes: float,
    interval_minutes: float = 1.0,
) -> pd.DataFrame:
    """Attach a coarse future-event target for survival-style experiments.

    This v0.1 helper creates a scalar target equal to 1 if an event starts within the next
    horizon after window_end. It keeps SPH/SOP labeling as the primary benchmark task while
    enabling simple hazard-head tests.
    """
    if horizon_minutes <= 0 or interval_minutes <= 0:
        raise ValueError("horizon_minutes and interval_minutes must be positive")
    out = windows.copy()
    out["window_end"] = pd.to_datetime(out["window_end"])
    ev = events.copy()
    ev["seizure_start"] = pd.to_datetime(ev["seizure_start"])
    horizon = pd.Timedelta(minutes=horizon_minutes)
    labels = []
    for _, row in out.iterrows():
        patient_events = ev.loc[ev["patient_id"].eq(row["patient_id"])]
        if "recording_id" in out.columns and "recording_id" in ev.columns:
            patient_events = patient_events.loc[patient_events["recording_id"].eq(row["recording_id"])]
        t0 = row["window_end"]
        labels.append(bool(((patient_events["seizure_start"] >= t0) & (patient_events["seizure_start"] < t0 + horizon)).any()))
    out["hazard_event_within_horizon"] = labels
    return out
