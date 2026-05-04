"""
Pretraitement SeizeIT2 alignant EEG (256 Hz) et MOV (25 Hz) a 50 Hz uniforme,
filtrage Butterworth passe-bas et fenetrage 2.56 s avec 50% d'overlap, comme
dans Raman & Velmurugan 2025.

Choix volontaire 50 Hz :
- aligne avec le pipeline du paper Raman (fenetres de 128 samples)
- preserve le contenu spectral EEG jusqu'a 25 Hz (Nyquist), couvre l'essentiel
  des bandes epileptiques cliniques (delta 0.5-4, theta 4-8, alpha 8-13,
  beta 13-30 Hz partiellement)
- ne change pas l'information IMU (upsample lineaire 25 -> 50 Hz, pas
  d'invention de signal mais alignement temporel)

Sortie : data/sub-001_run-07_windows.npz contenant
    X_eeg : (n_windows, 128, 2)   -- 128 samples, 2 canaux EEG bte
    X_mov : (n_windows, 128, 12)  -- 128 samples, 12 canaux ACC+GYR
    y     : (n_windows,)           -- 1 si fenetre intersecte une crise, 0 sinon
    t_start : (n_windows,)        -- temps debut fenetre en secondes
"""

from __future__ import annotations

import csv
from pathlib import Path

import mne
import numpy as np

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "sub-001_run-07"
OUT_FILE = Path(__file__).resolve().parent.parent / "data" / "sub-001_run-07_windows.npz"

TARGET_FS = 50
WINDOW_SEC = 2.56
WINDOW_LEN = int(WINDOW_SEC * TARGET_FS)
OVERLAP = 0.5
HOP_LEN = int(WINDOW_LEN * (1 - OVERLAP))
LOWPASS_HZ = 20.0


def parse_seizure_intervals(events_path: Path) -> list[tuple[float, float]]:
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
    for s, e in intervals:
        if t0 < e and t1 > s:
            return 1
    return 0


def resample_to(raw: mne.io.BaseRaw, target_fs: int) -> mne.io.BaseRaw:
    if abs(raw.info["sfreq"] - target_fs) < 0.5:
        return raw
    return raw.resample(target_fs, npad="auto", verbose="ERROR")


def main() -> int:
    print(f"Loading EEG and MOV from {DATA_DIR}...")
    raw_eeg = mne.io.read_raw_edf(DATA_DIR / "eeg.edf", preload=True, verbose="ERROR")
    raw_mov = mne.io.read_raw_edf(DATA_DIR / "mov.edf", preload=True, verbose="ERROR")
    print(f"  EEG : {raw_eeg.info['sfreq']:.0f} Hz, {len(raw_eeg.ch_names)} ch, "
          f"{raw_eeg.times[-1]:.1f} s")
    print(f"  MOV : {raw_mov.info['sfreq']:.0f} Hz, {len(raw_mov.ch_names)} ch, "
          f"{raw_mov.times[-1]:.1f} s")

    print(f"\nLow-pass filter < {LOWPASS_HZ} Hz (Butterworth-equivalent)...")
    raw_eeg.filter(l_freq=None, h_freq=LOWPASS_HZ, method="iir",
                   iir_params={"order": 4, "ftype": "butter"}, verbose="ERROR")

    print(f"\nResampling both streams to {TARGET_FS} Hz...")
    raw_eeg = resample_to(raw_eeg, TARGET_FS)
    raw_mov = resample_to(raw_mov, TARGET_FS)
    print(f"  EEG resampled : {raw_eeg.info['sfreq']:.0f} Hz, "
          f"{len(raw_eeg.times)} samples")
    print(f"  MOV resampled : {raw_mov.info['sfreq']:.0f} Hz, "
          f"{len(raw_mov.times)} samples")

    eeg_data = raw_eeg.get_data()
    mov_data = raw_mov.get_data()
    n_samples = min(eeg_data.shape[1], mov_data.shape[1])
    eeg_data = eeg_data[:, :n_samples]
    mov_data = mov_data[:, :n_samples]
    duration = n_samples / TARGET_FS
    print(f"  Aligned duration : {duration:.1f} s ({n_samples} samples)")

    intervals = parse_seizure_intervals(DATA_DIR / "events.tsv")
    print(f"\nSeizure intervals ({len(intervals)}) :")
    for s, e in intervals:
        print(f"  [{s:.1f}, {e:.1f}] s  duration {e - s:.1f} s")

    print(f"\nWindowing : {WINDOW_LEN} samples ({WINDOW_SEC} s), hop "
          f"{HOP_LEN} samples ({HOP_LEN / TARGET_FS:.2f} s)...")
    n_windows = (n_samples - WINDOW_LEN) // HOP_LEN + 1
    X_eeg = np.zeros((n_windows, WINDOW_LEN, eeg_data.shape[0]), dtype=np.float32)
    X_mov = np.zeros((n_windows, WINDOW_LEN, mov_data.shape[0]), dtype=np.float32)
    y = np.zeros(n_windows, dtype=np.int8)
    t_start = np.zeros(n_windows, dtype=np.float32)

    for i in range(n_windows):
        i0 = i * HOP_LEN
        i1 = i0 + WINDOW_LEN
        X_eeg[i] = eeg_data[:, i0:i1].T.astype(np.float32)
        X_mov[i] = mov_data[:, i0:i1].T.astype(np.float32)
        t0 = i0 / TARGET_FS
        t1 = i1 / TARGET_FS
        t_start[i] = t0
        y[i] = label_window(t0, t1, intervals)

    n_pos = int(y.sum())
    n_neg = n_windows - n_pos
    print(f"\nWindow stats :")
    print(f"  Total windows : {n_windows}")
    print(f"  Seizure (y=1) : {n_pos}  ({100 * n_pos / n_windows:.2f} %)")
    print(f"  Background    : {n_neg}  ({100 * n_neg / n_windows:.2f} %)")
    print(f"  X_eeg shape   : {X_eeg.shape}")
    print(f"  X_mov shape   : {X_mov.shape}")

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        OUT_FILE,
        X_eeg=X_eeg,
        X_mov=X_mov,
        y=y,
        t_start=t_start,
        eeg_ch_names=np.array(raw_eeg.ch_names),
        mov_ch_names=np.array(raw_mov.ch_names),
        target_fs=np.array(TARGET_FS),
        window_sec=np.array(WINDOW_SEC),
        overlap=np.array(OVERLAP),
    )
    size_mb = OUT_FILE.stat().st_size / (1024 * 1024)
    print(f"\nSaved : {OUT_FILE} ({size_mb:.1f} MB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
