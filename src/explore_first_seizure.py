"""
Visualisation du 1er événement crise sur sub-001 ses-01 run-07.

Sortie : results/figures/sub-001_run-07_seizure.png
Affiche 2 canaux EEG behind-the-ear + 3 canaux ACC du capteur tete,
avec une fenetre de 60 s autour de la crise (30 s avant, 30 s apres
le debut de la crise et zone crise marquee en rouge).
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import mne
import numpy as np

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "sub-001_run-07"
FIG_DIR = Path(__file__).resolve().parent.parent / "results" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

WIN_PRE = 30.0
WIN_POST = 30.0


def first_seizure(events_path: Path) -> dict | None:
    with events_path.open(encoding="utf-8") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            if row["eventType"].startswith("sz") and row["eventType"] not in ("bckg", "impd"):
                return row
    return None


def slice_window(raw: mne.io.BaseRaw, start_s: float, end_s: float) -> tuple[np.ndarray, np.ndarray]:
    sf = raw.info["sfreq"]
    i0 = max(0, int(start_s * sf))
    i1 = min(len(raw.times), int(end_s * sf))
    data = raw.get_data()[:, i0:i1]
    t = raw.times[i0:i1]
    return t, data


def main() -> int:
    seizure = first_seizure(DATA_DIR / "events.tsv")
    if not seizure:
        print("No seizure in this run.")
        return 1

    sz_onset = float(seizure["onset"])
    sz_dur = float(seizure["duration"])
    sz_end = sz_onset + sz_dur
    win_start = sz_onset - WIN_PRE
    win_end = sz_end + WIN_POST

    print(f"Seizure type   : {seizure['eventType']}")
    print(f"Lateralization : {seizure['lateralization']}")
    print(f"Localization   : {seizure['localization']}")
    print(f"Vigilance      : {seizure['vigilance']}")
    print(f"Onset          : {sz_onset:.1f} s")
    print(f"Duration       : {sz_dur:.1f} s")
    print(f"Plotting window: [{win_start:.1f} ; {win_end:.1f}] s")

    raw_eeg = mne.io.read_raw_edf(DATA_DIR / "eeg.edf", preload=True, verbose="ERROR")
    raw_mov = mne.io.read_raw_edf(DATA_DIR / "mov.edf", preload=True, verbose="ERROR")

    t_eeg, d_eeg = slice_window(raw_eeg, win_start, win_end)
    t_mov, d_mov = slice_window(raw_mov, win_start, win_end)

    eeg_names = raw_eeg.ch_names
    head_acc_idx = [
        raw_mov.ch_names.index(n)
        for n in ("EEG SD ACC X", "EEG SD ACC Y", "EEG SD ACC Z")
    ]

    fig, axes = plt.subplots(5, 1, figsize=(12, 9), sharex=True)
    fig.suptitle(
        f"sub-001 ses-01 run-07 — seizure {seizure['eventType']} "
        f"(left temporal, awake) — onset={sz_onset:.0f}s",
        fontsize=11,
    )

    for ax, ch_idx, name in zip(axes[:2], range(2), eeg_names):
        ax.plot(t_eeg, d_eeg[ch_idx] * 1e6, lw=0.4, color="black")
        ax.set_ylabel(f"{name}\n(uV)", fontsize=8)
        ax.axvspan(sz_onset, sz_end, color="red", alpha=0.18, label="seizure")
        ax.legend(loc="upper right", fontsize=8)
        ax.grid(alpha=0.3)

    for ax, idx, axis_name in zip(axes[2:5], head_acc_idx, ("X", "Y", "Z")):
        ax.plot(t_mov, d_mov[idx], lw=0.6, color="navy")
        ax.set_ylabel(f"ACC head {axis_name}\n(g)", fontsize=8)
        ax.axvspan(sz_onset, sz_end, color="red", alpha=0.18)
        ax.grid(alpha=0.3)

    axes[-1].set_xlabel("Time (s)")
    plt.tight_layout(rect=[0, 0, 1, 0.97])

    out = FIG_DIR / "sub-001_run-07_seizure.png"
    plt.savefig(out, dpi=130)
    print(f"\nSaved : {out}")
    print(f"Size  : {out.stat().st_size / 1024:.1f} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
