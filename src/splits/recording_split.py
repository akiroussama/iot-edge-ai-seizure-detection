from __future__ import annotations

import numpy as np
import pandas as pd


def recording_wise_split(
    df: pd.DataFrame,
    test_fraction: float = 0.2,
    val_fraction: float = 0.1,
    seed: int = 42,
) -> pd.DataFrame:
    """Assign train/val/test splits without sharing recordings across splits.

    This is useful for single-patient public-data smoke checks where patient-wise splitting is
    impossible and absolute recording timestamps are dummy or reset per file. It is not a substitute
    for patient-wise evaluation on a full cohort.
    """
    if not {"patient_id", "recording_id"}.issubset(df.columns):
        raise ValueError("df must contain patient_id and recording_id")
    out = df.copy()
    streams = (
        out[["patient_id", "recording_id"]]
        .drop_duplicates()
        .sort_values(["patient_id", "recording_id"])
        .reset_index(drop=True)
    )
    rng = np.random.default_rng(seed)
    order = np.arange(len(streams))
    rng.shuffle(order)
    n = len(order)
    n_test = int(round(n * test_fraction))
    n_val = int(round(n * val_fraction))
    test_idx = set(order[:n_test])
    val_idx = set(order[n_test : n_test + n_val])
    split_map = {}
    for pos, row in streams.iterrows():
        key = (row["patient_id"], row["recording_id"])
        if pos in test_idx:
            split_map[key] = "test"
        elif pos in val_idx:
            split_map[key] = "val"
        else:
            split_map[key] = "train"
    out["split"] = [
        split_map[(patient_id, recording_id)]
        for patient_id, recording_id in zip(out["patient_id"], out["recording_id"], strict=True)
    ]
    return out
