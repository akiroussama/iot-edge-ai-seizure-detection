"""
Chargement et inspection d'un run SeizeIT2 (sub-001 ses-01 run-07).

Sortie :
- Récap EEG (sampling rate, channels, durée)
- Récap MOV (sampling rate, channels, durée)
- Liste des crises annotées dans events.tsv

Utilise mne 1.12.1 (parseur EDF natif, pas de pyedflib requis).
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import mne
import numpy as np

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "sub-001_run-07"

SEIZURE_PREFIX = "sz"
NON_SEIZURE_TYPES = {"bckg", "impd"}


def load_sidecar(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_events(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        return list(reader)


def is_seizure(event_type: str) -> bool:
    return event_type.startswith(SEIZURE_PREFIX) and event_type not in NON_SEIZURE_TYPES


def summarize_raw(label: str, raw: mne.io.BaseRaw, sidecar: dict) -> None:
    print(f"\n[{label}]")
    print(f"  Sampling freq (EDF) : {raw.info['sfreq']:.2f} Hz")
    sf_sidecar_keys = ["SamplingFrequency"]
    for k in sf_sidecar_keys:
        if k in sidecar:
            print(f"  Sampling freq (sidecar) : {sidecar[k]} Hz")
    if abs(raw.info["sfreq"] - sidecar.get("SamplingFrequency", raw.info["sfreq"])) > 0.5:
        print("  WARN : sidecar/EDF sampling rate mismatch")
    print(f"  Duration         : {raw.times[-1]:.1f} s ({raw.times[-1] / 3600:.2f} h)")
    print(f"  N samples        : {len(raw.times)}")
    print(f"  N channels       : {len(raw.ch_names)}")
    print(f"  Channel names    : {raw.ch_names}")
    print(f"  Channel types    : {raw.get_channel_types()}")
    data = raw.get_data()
    print(f"  Data shape       : {data.shape}")
    print(f"  Data dtype       : {data.dtype}")
    print(f"  Per-channel min/mean/max (first 4 channels) :")
    for i, name in enumerate(raw.ch_names[:4]):
        ch = data[i]
        print(f"    {name:12s} : {ch.min():+.3e}  {ch.mean():+.3e}  {ch.max():+.3e}")


def summarize_events(events: list[dict]) -> None:
    print(f"\n[Events]")
    print(f"  Total annotations : {len(events)}")
    seizures = [e for e in events if is_seizure(e["eventType"])]
    print(f"  Seizures (sz_*)   : {len(seizures)}")
    if not seizures:
        print("  -> no seizure in this run, pipeline can still be built on background")
        return
    for e in seizures:
        onset = float(e["onset"])
        duration = float(e["duration"])
        print(f"  - {e['eventType']:25s} onset={onset:.1f}s duration={duration:.1f}s "
              f"lat={e['lateralization']} loc={e['localization']} vig={e['vigilance']}")


def main() -> int:
    print("=" * 60)
    print(" SeizeIT2 — load_data.py — sub-001 ses-01 run-07")
    print("=" * 60)
    eeg_edf = DATA_DIR / "eeg.edf"
    mov_edf = DATA_DIR / "mov.edf"
    events_tsv = DATA_DIR / "events.tsv"
    eeg_json = DATA_DIR / "eeg.json"
    mov_json = DATA_DIR / "mov.json"

    for p in (eeg_edf, mov_edf, events_tsv, eeg_json, mov_json):
        if not p.exists():
            print(f"  MISSING : {p}")
            return 1

    eeg_sidecar = load_sidecar(eeg_json)
    mov_sidecar = load_sidecar(mov_json)
    events = load_events(events_tsv)

    print("\nLoading EEG.edf with mne...")
    raw_eeg = mne.io.read_raw_edf(eeg_edf, preload=True, verbose="ERROR")
    summarize_raw("EEG", raw_eeg, eeg_sidecar)

    print("\nLoading MOV.edf with mne...")
    raw_mov = mne.io.read_raw_edf(mov_edf, preload=True, verbose="ERROR")
    summarize_raw("MOV", raw_mov, mov_sidecar)

    summarize_events(events)

    print("\n[Sanity checks]")
    eeg_dur = raw_eeg.times[-1]
    mov_dur = raw_mov.times[-1]
    print(f"  EEG duration  : {eeg_dur:.1f} s")
    print(f"  MOV duration  : {mov_dur:.1f} s")
    print(f"  Sidecar dur   : {eeg_sidecar.get('RecordingDuration')} s")
    print(f"  Diff EEG-MOV  : {abs(eeg_dur - mov_dur):.2f} s "
          f"(<= 1 s expected for synchronized recording)")

    print("\nDone.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
