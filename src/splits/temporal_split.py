from __future__ import annotations

import pandas as pd

from src.utils.time import ensure_datetime


def temporal_split_per_patient(
    df: pd.DataFrame,
    train_fraction: float = 0.7,
    val_fraction: float = 0.1,
    purge_overlap: bool = True,
    purge_label: str = "purge",
) -> pd.DataFrame:
    """Pseudo-prospective split: train on past, validate/test on future per patient.

    When ``purge_overlap`` is true, windows at split boundaries are assigned to ``purge`` if
    their interval overlaps the previous split. This prevents stride/window-duration overlap
    from leaking nearly identical samples across train/validation/test.
    """
    if not {"patient_id", "window_start", "window_end"}.issubset(df.columns):
        raise ValueError("df must contain patient_id, window_start, and window_end")
    out = df.copy()
    out["window_start"] = ensure_datetime(out["window_start"])
    out["window_end"] = ensure_datetime(out["window_end"])
    out["split"] = "train"
    for _, g in out.sort_values(["window_start", "window_end"]).groupby("patient_id"):
        n = len(g)
        train_end = int(n * train_fraction)
        val_end = int(n * (train_fraction + val_fraction))
        idx = g.index.to_list()
        out.loc[idx[train_end:val_end], "split"] = "val"
        out.loc[idx[val_end:], "split"] = "test"
        if not purge_overlap:
            continue
        for earlier, later in (("train", "val"), ("train", "test"), ("val", "test")):
            earlier_rows = out.loc[idx].loc[out.loc[idx, "split"].eq(earlier)]
            if earlier_rows.empty:
                continue
            earlier_end = earlier_rows["window_end"].max()
            later_rows = out.loc[idx].loc[out.loc[idx, "split"].eq(later)]
            overlap_idx = later_rows.loc[later_rows["window_start"] < earlier_end].index
            out.loc[overlap_idx, "split"] = purge_label
    return out
