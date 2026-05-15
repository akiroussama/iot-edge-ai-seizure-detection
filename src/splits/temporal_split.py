from __future__ import annotations

import pandas as pd

from src.utils.time import ensure_datetime


def temporal_split_per_patient(
    df: pd.DataFrame,
    train_fraction: float = 0.7,
    val_fraction: float = 0.1,
    purge_overlap: bool = True,
    purge_label: str = "purge",
    split_unit: str = "window",
    split_basis: str = "elapsed_time",
) -> pd.DataFrame:
    """Pseudo-prospective split: train on past, validate/test on future per patient.

    When ``purge_overlap`` is true, windows at split boundaries are assigned to ``purge`` if
    their interval overlaps the previous split. This prevents stride/window-duration overlap
    from leaking nearly identical samples across train/validation/test.

    ``split_unit="recording"`` assigns whole recordings to train/validation/test in chronological
    order. Use it when per-recording preprocessing, recording-level artifacts, or nested wearable
    files make within-recording split boundaries methodologically risky.

    ``split_basis="elapsed_time"`` uses each patient's observed time span for boundaries. The
    legacy ``count`` basis is available only for explicit diagnostics because dense and sparse
    windows should not receive equal temporal weight by default.
    """
    if not {"patient_id", "window_start", "window_end"}.issubset(df.columns):
        raise ValueError("df must contain patient_id, window_start, and window_end")
    if split_unit not in {"window", "recording"}:
        raise ValueError("split_unit must be 'window' or 'recording'")
    if split_basis not in {"elapsed_time", "count"}:
        raise ValueError("split_basis must be 'elapsed_time' or 'count'")
    if split_unit == "recording" and "recording_id" not in df.columns:
        raise ValueError("split_unit='recording' requires recording_id")
    out = df.copy()
    out["window_start"] = ensure_datetime(out["window_start"])
    out["window_end"] = ensure_datetime(out["window_end"])
    out["split"] = "train"

    for patient, g in out.sort_values(["window_start", "window_end"]).groupby("patient_id"):
        if split_unit == "recording":
            _assign_recording_units(
                out,
                patient=patient,
                group=g,
                train_fraction=train_fraction,
                val_fraction=val_fraction,
                split_basis=split_basis,
            )
        else:
            _assign_window_units(
                out,
                group=g,
                train_fraction=train_fraction,
                val_fraction=val_fraction,
                split_basis=split_basis,
            )
        if purge_overlap:
            _purge_split_overlaps(out, g.index.to_list(), purge_label=purge_label, split_unit=split_unit)
    return out


def _assign_window_units(
    out: pd.DataFrame,
    group: pd.DataFrame,
    train_fraction: float,
    val_fraction: float,
    split_basis: str,
) -> None:
    g = group.sort_values(["window_start", "window_end"])
    if split_basis == "elapsed_time":
        train_cut, val_cut = _elapsed_time_cuts(g["window_start"], g["window_end"], train_fraction, val_fraction)
        out.loc[g.index[g["window_start"] >= train_cut], "split"] = "val"
        out.loc[g.index[g["window_start"] >= val_cut], "split"] = "test"
        return
    n = len(g)
    train_end = int(n * train_fraction)
    val_end = int(n * (train_fraction + val_fraction))
    idx = g.index.to_list()
    out.loc[idx[train_end:val_end], "split"] = "val"
    out.loc[idx[val_end:], "split"] = "test"


def _assign_recording_units(
    out: pd.DataFrame,
    patient: object,
    group: pd.DataFrame,
    train_fraction: float,
    val_fraction: float,
    split_basis: str,
) -> None:
    if group["recording_id"].isna().any():
        raise ValueError(f"patient {patient!r} has null recording_id values")
    units = (
        group.groupby("recording_id", sort=False)
        .agg(unit_start=("window_start", "min"), unit_end=("window_end", "max"))
        .sort_values(["unit_start", "unit_end"])
    )
    if split_basis == "elapsed_time":
        train_cut, val_cut = _elapsed_time_cuts(units["unit_start"], units["unit_end"], train_fraction, val_fraction)
        split_by_recording = {}
        for recording_id, row in units.iterrows():
            if row["unit_start"] >= val_cut:
                split_by_recording[recording_id] = "test"
            elif row["unit_start"] >= train_cut:
                split_by_recording[recording_id] = "val"
            else:
                split_by_recording[recording_id] = "train"
        for recording_id, split in split_by_recording.items():
            idx = group.index[group["recording_id"].eq(recording_id)]
            out.loc[idx, "split"] = split
        return
    n = len(units)
    train_end = int(n * train_fraction)
    val_end = int(n * (train_fraction + val_fraction))
    split_by_recording = {recording_id: "train" for recording_id in units.index[:train_end]}
    split_by_recording.update({recording_id: "val" for recording_id in units.index[train_end:val_end]})
    split_by_recording.update({recording_id: "test" for recording_id in units.index[val_end:]})
    for recording_id, split in split_by_recording.items():
        idx = group.index[group["recording_id"].eq(recording_id)]
        out.loc[idx, "split"] = split


def _elapsed_time_cuts(
    starts: pd.Series,
    ends: pd.Series,
    train_fraction: float,
    val_fraction: float,
) -> tuple[pd.Timestamp, pd.Timestamp]:
    min_start = starts.min()
    max_end = ends.max()
    span = max_end - min_start
    if pd.isna(min_start) or pd.isna(max_end) or span <= pd.Timedelta(0):
        raise ValueError("temporal elapsed_time split requires a positive observed time span")
    return min_start + span * train_fraction, min_start + span * (train_fraction + val_fraction)


def _purge_split_overlaps(
    out: pd.DataFrame,
    idx: list[object],
    purge_label: str,
    split_unit: str,
) -> None:
    for earlier, later in (("train", "val"), ("train", "test"), ("val", "test")):
        earlier_rows = out.loc[idx].loc[out.loc[idx, "split"].eq(earlier)]
        if earlier_rows.empty:
            continue
        earlier_end = earlier_rows["window_end"].max()
        later_rows = out.loc[idx].loc[out.loc[idx, "split"].eq(later)]
        overlap_idx = later_rows.loc[later_rows["window_start"] < earlier_end].index
        if split_unit == "recording" and len(overlap_idx) > 0:
            overlapping_recordings = set(out.loc[overlap_idx, "recording_id"])
            overlap_idx = out.loc[idx].loc[out.loc[idx, "recording_id"].isin(overlapping_recordings)].index
        out.loc[overlap_idx, "split"] = purge_label
