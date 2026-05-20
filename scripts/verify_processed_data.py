#!/usr/bin/env python
"""Processed-data integrity check (Phase C pre-freeze gate).

Read-only. Loads every processed parquet under data/processed/{msg,seizeit2},
reports row/col counts, NaN counts per column, timestamp-ordering sanity, and
label/exclusion distributions. Exits non-zero if it flags an anomaly that would
corrupt the Phase C split freeze (a read failure or a timestamp-ordering
violation). NaN in nullable metadata columns is reported, not flagged.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
PROCESSED = {"msg": REPO / "data/processed/msg", "seizeit2": REPO / "data/processed/seizeit2"}
anomalies: list[str] = []


def _flag(msg: str) -> None:
    anomalies.append(msg)
    print(f"    ANOMALY: {msg}")


def check(dataset: str, root: Path) -> None:
    print(f"\n===== {dataset}  ({root}) =====")
    if not root.exists():
        _flag(f"{dataset}: processed directory missing")
        return
    for pq in sorted(root.glob("*.parquet")):
        try:
            df = pd.read_parquet(pq)
        except Exception as exc:  # noqa: BLE001 - report any read failure
            _flag(f"{dataset}/{pq.name}: read failed: {exc}")
            continue
        print(f"  {pq.name}: {len(df)} rows x {len(df.columns)} cols")
        nan_cols = {c: int(df[c].isna().sum()) for c in df.columns if df[c].isna().any()}
        if nan_cols:
            print(f"    NaN columns: {nan_cols}")
        if {"seizure_start", "seizure_end"}.issubset(df.columns) and len(df):
            bad = int((pd.to_datetime(df["seizure_end"]) < pd.to_datetime(df["seizure_start"])).sum())
            if bad:
                _flag(f"{dataset}/{pq.name}: {bad} rows with seizure_end < seizure_start")
        if {"recording_start", "recording_end"}.issubset(df.columns) and len(df):
            bad = int((pd.to_datetime(df["recording_end"]) <= pd.to_datetime(df["recording_start"])).sum())
            if bad:
                _flag(f"{dataset}/{pq.name}: {bad} rows with recording_end <= recording_start")
        if {"window_start", "window_end"}.issubset(df.columns) and len(df):
            bad = int((pd.to_datetime(df["window_end"]) <= pd.to_datetime(df["window_start"])).sum())
            if bad:
                _flag(f"{dataset}/{pq.name}: {bad} rows with window_end <= window_start")
        if "forecast_label" in df.columns and len(df):
            pos = int(df["forecast_label"].astype(bool).sum())
            print(f"    forecast_label: {pos} positive / {len(df)} ({100 * pos / len(df):.2f}%)")
        if "is_excluded" in df.columns and len(df):
            exc = int(df["is_excluded"].astype(bool).sum())
            print(f"    is_excluded: {exc} / {len(df)} ({100 * exc / len(df):.2f}%)")
        if "patient_id" in df.columns and len(df):
            print(f"    distinct patient_id: {df['patient_id'].nunique()}")


def main() -> None:
    for name, root in PROCESSED.items():
        check(name, root)
    print("\n===== summary =====")
    if anomalies:
        print(f"{len(anomalies)} anomaly/anomalies flagged:")
        for a in anomalies:
            print(f"  - {a}")
        sys.exit(1)
    print("no anomalies: processed parquets are schema-sane for Phase C")


if __name__ == "__main__":
    main()
