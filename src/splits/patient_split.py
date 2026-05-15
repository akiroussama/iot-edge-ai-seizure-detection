from __future__ import annotations

import numpy as np
import pandas as pd


def patient_wise_split(
    df: pd.DataFrame,
    test_fraction: float = 0.2,
    val_fraction: float = 0.1,
    seed: int = 42,
) -> pd.DataFrame:
    """Assign train/val/test splits without sharing patients across splits."""
    if "patient_id" not in df.columns:
        raise ValueError("df must contain patient_id")
    out = df.copy()
    patients = np.array(sorted(out["patient_id"].dropna().unique()))
    rng = np.random.default_rng(seed)
    rng.shuffle(patients)
    n = len(patients)
    n_test = int(round(n * test_fraction))
    n_val = int(round(n * val_fraction))
    test = set(patients[:n_test])
    val = set(patients[n_test : n_test + n_val])
    out["split"] = "train"
    out.loc[out["patient_id"].isin(val), "split"] = "val"
    out.loc[out["patient_id"].isin(test), "split"] = "test"
    return out
