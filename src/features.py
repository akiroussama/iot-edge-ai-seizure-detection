"""
Extraction de features par fenetre, sur chaque canal independamment.

10 features per channel x 14 channels (2 EEG + 12 MOV) = 140 features per window.

Liste des features :
1.  mean             : moyenne
2.  variance         : variance (Raman)
3.  skewness         : asymetrie (Raman)
4.  kurtosis         : kurtose (extension)
5.  rms              : racine de la moyenne quadratique
6.  higuchi_fd       : longueur fractale max via Higuchi (Raman)
7.  spectral_entropy : entropie de Shannon du spectre (Raman)
8.  mean_freq        : frequence moyenne ponderee par puissance (Raman)
9.  median_freq      : frequence mediane (Raman)
10. band_power_4_13  : puissance dans la bande 4-13 Hz (theta+alpha, signature
                       epilepsie clinique standard)

Sortie :
    data/sub-001_run-07_features.npz   -- arrays numeriques uniquement
    data/sub-001_run-07_features.json  -- noms de features et metadata
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy import stats
from scipy.fft import rfft, rfftfreq

WINDOWS_FILE = Path(__file__).resolve().parent.parent / "data" / "sub-001_run-07_windows.npz"
WINDOWS_META = Path(__file__).resolve().parent.parent / "data" / "sub-001_run-07_windows.json"
OUT_NPZ = Path(__file__).resolve().parent.parent / "data" / "sub-001_run-07_features.npz"
OUT_JSON = Path(__file__).resolve().parent.parent / "data" / "sub-001_run-07_features.json"

EPS = 1e-12

FEATURE_PER_CH = ["mean", "var", "skew", "kurt", "rms", "fd",
                  "spec_ent", "mean_freq", "med_freq", "bp_4_13"]


def higuchi_fd(x: np.ndarray, k_max: int = 8) -> float:
    n = len(x)
    if n < k_max + 2:
        return 1.0
    lk = np.zeros(k_max)
    for k in range(1, k_max + 1):
        lm = []
        for m in range(k):
            idx = np.arange(m, n - k, k)
            if len(idx) < 2:
                continue
            length = np.sum(np.abs(np.diff(x[idx]))) * (n - 1) / (((n - m) // k) * k)
            lm.append(length)
        if lm:
            lk[k - 1] = np.mean(lm)
    if np.any(lk <= 0):
        return 1.0
    coeffs = np.polyfit(np.log(np.arange(1, k_max + 1)), np.log(lk), 1)
    return float(-coeffs[0])


def spectral_features(x: np.ndarray, fs: float) -> tuple[float, float, float, float]:
    spectrum = np.abs(rfft(x)) ** 2
    freqs = rfftfreq(len(x), d=1.0 / fs)
    spectrum = spectrum[1:]
    freqs = freqs[1:]
    if spectrum.sum() < EPS:
        return 0.0, 0.0, 0.0, 0.0
    psd_norm = spectrum / spectrum.sum()
    spec_ent = -np.sum(psd_norm * np.log2(psd_norm + EPS))
    mean_f = float(np.sum(freqs * psd_norm))
    cum = np.cumsum(spectrum)
    median_f = float(freqs[np.searchsorted(cum, cum[-1] / 2)])
    band_mask = (freqs >= 4.0) & (freqs <= 13.0)
    band_power = float(spectrum[band_mask].sum() / spectrum.sum())
    return float(spec_ent), mean_f, median_f, band_power


def channel_features(x: np.ndarray, fs: float) -> np.ndarray:
    var = float(x.var())
    has_var = var > EPS
    return np.array([
        float(x.mean()),
        var,
        float(stats.skew(x)) if has_var else 0.0,
        float(stats.kurtosis(x)) if has_var else 0.0,
        float(np.sqrt((x ** 2).mean())),
        higuchi_fd(x),
        *spectral_features(x, fs),
    ], dtype=np.float32)


def main() -> int:
    print(f"Loading windows from {WINDOWS_FILE}...")
    data = np.load(WINDOWS_FILE, allow_pickle=True)
    X_eeg = data["X_eeg"]
    X_mov = data["X_mov"]
    y = data["y"]
    t_start = data["t_start"]
    fs = float(data["target_fs"])
    eeg_ch = [str(s) for s in data["eeg_ch_names"]]
    mov_ch = [str(s) for s in data["mov_ch_names"]]

    n_windows = X_eeg.shape[0]
    n_eeg_ch = X_eeg.shape[2]
    n_mov_ch = X_mov.shape[2]
    n_total_ch = n_eeg_ch + n_mov_ch
    n_features = n_total_ch * len(FEATURE_PER_CH)
    print(f"  Windows  : {n_windows}")
    print(f"  Channels : {n_eeg_ch} EEG + {n_mov_ch} MOV = {n_total_ch}")
    print(f"  Features : {len(FEATURE_PER_CH)} per channel x {n_total_ch} = {n_features}")
    print(f"  Sampling : {fs} Hz")

    feat_names: list[str] = []
    for ch in eeg_ch + mov_ch:
        ch_safe = ch.replace(" ", "_")
        for f in FEATURE_PER_CH:
            feat_names.append(f"{ch_safe}__{f}")

    X = np.zeros((n_windows, n_features), dtype=np.float32)

    print(f"\nExtracting features (this may take a couple of minutes)...")
    progress_step = max(1, n_windows // 20)
    for i in range(n_windows):
        feats: list[np.ndarray] = []
        for c in range(n_eeg_ch):
            feats.append(channel_features(X_eeg[i, :, c], fs))
        for c in range(n_mov_ch):
            feats.append(channel_features(X_mov[i, :, c], fs))
        X[i] = np.concatenate(feats)
        if (i + 1) % progress_step == 0:
            print(f"  {i + 1:6d} / {n_windows} ({100 * (i + 1) / n_windows:5.1f} %)")

    print(f"\nFeature matrix shape : {X.shape}")
    nan_count = int(np.isnan(X).sum())
    inf_count = int(np.isinf(X).sum())
    print(f"NaN count : {nan_count}, Inf count : {inf_count}")
    if nan_count or inf_count:
        print("  WARNING : replacing NaN/Inf with 0")
        X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)

    print(f"\nClass-conditional statistics (label 0 vs 1) on selected features :")
    eeg0_var = 0 * len(FEATURE_PER_CH) + 1
    eeg0_fd = 0 * len(FEATURE_PER_CH) + 5
    mov0_var = n_eeg_ch * len(FEATURE_PER_CH) + 1
    mov0_bp = n_eeg_ch * len(FEATURE_PER_CH) + 9
    mov_head_acc_var_indices = [
        n_eeg_ch * len(FEATURE_PER_CH) + i * len(FEATURE_PER_CH) + 1 for i in range(3)
    ]
    mov_head_acc_var = X[:, mov_head_acc_var_indices].mean(axis=1)

    for col, name in [
        (eeg0_var, "EEG_ch0 var"),
        (eeg0_fd, "EEG_ch0 fd"),
        (mov0_var, "MOV_ch0 var (head ACC X)"),
        (mov0_bp, "MOV_ch0 bp_4_13 (head ACC X)"),
    ]:
        neg = X[y == 0, col]
        pos = X[y == 1, col]
        ratio = pos.mean() / (abs(neg.mean()) + EPS)
        print(f"  {name:30s}  neg={neg.mean():+.3e}  pos={pos.mean():+.3e}  ratio={ratio:+.2f}")

    head_acc_neg = mov_head_acc_var[y == 0].mean()
    head_acc_pos = mov_head_acc_var[y == 1].mean()
    print(f"  {'MOV head ACC var (mean X/Y/Z)':30s}  neg={head_acc_neg:+.3e}  "
          f"pos={head_acc_pos:+.3e}  ratio={head_acc_pos / (head_acc_neg + EPS):+.2f}")

    OUT_NPZ.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(OUT_NPZ, X=X, y=y, t_start=t_start)
    OUT_JSON.write_text(
        json.dumps(
            {
                "feat_names": feat_names,
                "n_features": n_features,
                "n_windows": int(n_windows),
                "fs": fs,
                "window_sec": 2.56,
                "n_eeg_ch": n_eeg_ch,
                "n_mov_ch": n_mov_ch,
                "feature_per_channel": FEATURE_PER_CH,
                "n_positives": int(y.sum()),
                "n_negatives": int((y == 0).sum()),
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    size_mb = OUT_NPZ.stat().st_size / (1024 * 1024)
    print(f"\nSaved arrays : {OUT_NPZ} ({size_mb:.1f} MB)")
    print(f"Saved meta   : {OUT_JSON}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
