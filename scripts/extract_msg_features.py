#!/usr/bin/env python
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.features.msg_empatica import extract_msg_empatica_window_features
from src.utils.io import read_table, write_table


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract MSG Empatica HR/ACC window features.")
    parser.add_argument("--raw-dir", required=True)
    parser.add_argument("--windows", required=True, help="Windows or labeled windows table.")
    parser.add_argument("--out", required=True)
    parser.add_argument("--modalities", nargs="+", default=["hr", "acc"], choices=["hr", "acc"])
    parser.add_argument(
        "--max-recordings",
        type=int,
        default=None,
        help="Optional development limit for fast parser checks. Omit for full extraction.",
    )
    args = parser.parse_args()

    windows = read_table(args.windows)
    features = extract_msg_empatica_window_features(
        args.raw_dir,
        windows,
        modalities=args.modalities,
        max_recordings=args.max_recordings,
    )
    write_table(features, args.out)
    populated = {
        col: int(features[col].notna().sum())
        for col in features.columns
        if col.endswith("_mean") or col.endswith("_energy")
    }
    print(
        {
            "out": args.out,
            "rows": len(features),
            "modalities": args.modalities,
            "feature_recordings_processed": int(features["feature_recordings_processed"].max())
            if "feature_recordings_processed" in features
            else 0,
            "populated_feature_counts": populated,
        }
    )


if __name__ == "__main__":
    main()
