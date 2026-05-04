"""
Pipeline complet multi-run : preprocess + features sur tous les dossiers
data/sub-*_run-*/, concatene en une matrice unifiee avec subject_id.

Utilise les fonctions de preprocess.py et features.py.
"""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

import mne
import numpy as np

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from features import FEATURE_PER_CH, channel_features

DATA_ROOT = ROOT.parent / "data"
OUT_NPZ = DATA_ROOT / "multirun_features.npz"
OUT_JSON = DATA_ROOT / "multirun_features.json"

TARGET_FS = 50
WINDOW_SEC = 2.56
WINDOW_LEN = int(WINDOW_SEC * TARGET_FS)
HOP_LEN = int(WINDOW_LEN * 0.5)
LOWPASS_HZ = 20.0

DIR_RE = re.compile(r"^sub-(\d+)_run-(\d+)$")


def parse_seizures(events_path: Path) -> list[tuple[float, float]]:
    intervals: list[tuple[float, float]] = []
    with events_path.open(encoding="utf-8") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            ev = row["eventType"]
            if ev.startswith("sz") and ev not in ("bckg", "impd"):
                onset = float(row["onset"])
                duration = float(row["duration"])
                intervals.append((onset, onset + duration))
    return intervals


def label_window(t0: float, t1: float, intervals: list[tuple[float, float]]) -> int:
    return 1 if any(t0 < e and t1 > s for s, e in intervals) else 0


def process_run(run_dir: Path, sub_id: int, run_id: int) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    eeg_edf = run_dir / "eeg.edf"
    mov_edf = run_dir / "mov.edf"
    events_tsv = run_dir / "events.tsv"
    if not (eeg_edf.exists() and mov_edf.exists() and events_tsv.exists()):
        return np.empty((0, 0)), np.empty(0), np.empty(0), np.empty(0), np.empty(0)
    if mov_edf.stat().st_size < 1024:
        print(f"  SKIP (mov too small) : {run_dir.name}")
        return np.empty((0, 0)), np.empty(0), np.empty(0), np.empty(0), np.empty(0)

    raw_eeg = mne.io.read_raw_edf(eeg_edf, preload=True, verbose="ERROR")
    raw_mov = mne.io.read_raw_edf(mov_edf, preload=True, verbose="ERROR")

    raw_eeg.filter(l_freq=None, h_freq=LOWPASS_HZ, method="iir",
                   iir_params={"order": 4, "ftype": "butter"}, verbose="ERROR")
    if abs(raw_eeg.info["sfreq"] - TARGET_FS) > 0.5:
        raw_eeg = raw_eeg.resample(TARGET_FS, npad="auto", verbose="ERROR")
    if abs(raw_mov.info["sfreq"] - TARGET_FS) > 0.5:
        raw_mov = raw_mov.resample(TARGET_FS, npad="auto", verbose="ERROR")

    N_EEG_KEEP = 2
    N_MOV_KEEP = 6
    eeg_data = raw_eeg.get_data()[:N_EEG_KEEP]
    mov_data = raw_mov.get_data()[:N_MOV_KEEP]
    n_eeg = eeg_data.shape[0]
    n_mov = mov_data.shape[0]
    if n_eeg < N_EEG_KEEP or n_mov < N_MOV_KEEP:
        print(f"  SKIP (insufficient channels) : {run_dir.name}  "
              f"eeg={n_eeg}, mov={n_mov}")
        return np.empty((0, 0)), np.empty(0), np.empty(0), np.empty(0), np.empty(0)
    n_samples = min(eeg_data.shape[1], mov_data.shape[1])
    eeg_data = eeg_data[:, :n_samples]
    mov_data = mov_data[:, :n_samples]

    intervals = parse_seizures(events_tsv)
    n_windows = (n_samples - WINDOW_LEN) // HOP_LEN + 1
    if n_windows <= 0:
        return np.empty((0, 0)), np.empty(0), np.empty(0), np.empty(0), np.empty(0)

    n_features = (n_eeg + n_mov) * len(FEATURE_PER_CH)
    X = np.zeros((n_windows, n_features), dtype=np.float32)
    y = np.zeros(n_windows, dtype=np.int8)
    t_start = np.zeros(n_windows, dtype=np.float32)
    sub_arr = np.full(n_windows, sub_id, dtype=np.int16)
    run_arr = np.full(n_windows, run_id, dtype=np.int16)

    for i in range(n_windows):
        i0 = i * HOP_LEN
        i1 = i0 + WINDOW_LEN
        t0 = i0 / TARGET_FS
        t1 = i1 / TARGET_FS
        t_start[i] = t0
        y[i] = label_window(t0, t1, intervals)
        feats = []
        for c in range(n_eeg):
            feats.append(channel_features(eeg_data[c, i0:i1].astype(np.float32), TARGET_FS))
        for c in range(n_mov):
            feats.append(channel_features(mov_data[c, i0:i1].astype(np.float32), TARGET_FS))
        X[i] = np.concatenate(feats)

    print(f"  OK {run_dir.name:25s} : {n_windows} windows, "
          f"{int(y.sum())} positives, {n_eeg} EEG ch + {n_mov} MOV ch, "
          f"{len(intervals)} seizures")
    return X, y, t_start, sub_arr, run_arr


def main() -> int:
    print(f"Scanning {DATA_ROOT}/sub-*_run-* ...")
    run_dirs = sorted([d for d in DATA_ROOT.iterdir() if d.is_dir() and DIR_RE.match(d.name)])
    print(f"  Found {len(run_dirs)} run directories")

    Xs, ys, ts, subs, runs = [], [], [], [], []
    n_eeg_ch_seen: int | None = None
    n_mov_ch_seen: int | None = None
    for d in run_dirs:
        m = DIR_RE.match(d.name)
        if not m:
            continue
        sub_id = int(m.group(1))
        run_id = int(m.group(2))
        X_r, y_r, t_r, s_r, ru_r = process_run(d, sub_id, run_id)
        if X_r.size == 0:
            continue
        Xs.append(X_r)
        ys.append(y_r)
        ts.append(t_r)
        subs.append(s_r)
        runs.append(ru_r)

    if not Xs:
        print("No usable run found.")
        return 1

    X = np.concatenate(Xs, axis=0)
    y = np.concatenate(ys, axis=0)
    t = np.concatenate(ts, axis=0)
    sub = np.concatenate(subs, axis=0)
    run = np.concatenate(runs, axis=0)

    nan_count = int(np.isnan(X).sum())
    inf_count = int(np.isinf(X).sum())
    if nan_count or inf_count:
        print(f"  Replacing {nan_count} NaN and {inf_count} Inf with 0")
        X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)

    n_total = len(y)
    n_pos = int(y.sum())
    n_subjects = len(np.unique(sub))
    print(f"\n[Concatenated dataset]")
    print(f"  Total windows : {n_total}")
    print(f"  Positives     : {n_pos}  ({100 * n_pos / n_total:.2f} %)")
    print(f"  Subjects      : {n_subjects}")
    print(f"  X shape       : {X.shape}")

    print(f"\n[Per-subject breakdown]")
    for s_id in np.unique(sub):
        m = sub == s_id
        print(f"  sub-{int(s_id):03d} : {m.sum():5d} windows, "
              f"{int(y[m].sum()):3d} positives ({100 * y[m].mean():.2f} %)")

    np.savez_compressed(OUT_NPZ, X=X, y=y, t_start=t, subject=sub, run=run)
    OUT_JSON.write_text(json.dumps({
        "n_windows": int(n_total),
        "n_positives": int(n_pos),
        "n_subjects": int(n_subjects),
        "subjects": sorted(int(s) for s in np.unique(sub)),
        "n_features": int(X.shape[1]),
        "fs": TARGET_FS,
        "window_sec": WINDOW_SEC,
        "feature_per_channel": FEATURE_PER_CH,
        "lowpass_hz": LOWPASS_HZ,
    }, indent=2), encoding="utf-8")
    print(f"\nSaved : {OUT_NPZ} ({OUT_NPZ.stat().st_size / (1024*1024):.1f} MB)")
    print(f"Saved : {OUT_JSON}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
