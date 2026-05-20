from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.utils.io import read_table


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize forecast labels for human audit.")
    parser.add_argument("--labels", required=True)
    parser.add_argument("--events", default=None)
    args = parser.parse_args()
    labels = read_table(args.labels)
    print("rows", len(labels))
    for col in ["forecast_label", "is_ictal", "is_postictal", "is_excluded"]:
        if col in labels.columns:
            print(col, labels[col].mean(), labels[col].sum())
    if "patient_id" in labels.columns:
        print("\npositive windows per patient")
        print(labels.groupby("patient_id")["forecast_label"].sum().describe())
    if args.events:
        events = read_table(args.events)
        print("\nevents", len(events))
        if "patient_id" in events.columns:
            print(events.groupby("patient_id").size().describe())
    cols = [
        c
        for c in [
            "patient_id",
            "recording_id",
            "window_start",
            "window_end",
            "time_to_next_seizure_seconds",
            "forecast_label",
            "is_excluded",
        ]
        if c in labels
    ]
    print("\nfirst positive windows")
    print(labels.loc[labels["forecast_label"]].head(20)[cols].to_string(index=False))


if __name__ == "__main__":
    main()
