from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.datasets.msg_loader import resolve_msg_duplicate_recording_ranges
from src.utils.io import read_table, write_table


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Resolve exact duplicate My Seizure Gauge recording time ranges in a processed recordings table."
    )
    parser.add_argument("--recordings", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument(
        "--duplicate-recording-policy",
        choices=["error", "drop_exact"],
        default="error",
        help="Use drop_exact only after documenting duplicated files; default fails closed.",
    )
    parser.add_argument(
        "--duplicates-out",
        default=None,
        help="Optional CSV/parquet table containing all duplicate-range rows before resolution.",
    )
    args = parser.parse_args()

    recordings = read_table(args.recordings)
    duplicate_cols = ["patient_id", "recording_start", "recording_end"]
    duplicates = recordings.loc[recordings.duplicated(duplicate_cols, keep=False)].copy()
    resolved = resolve_msg_duplicate_recording_ranges(recordings, args.duplicate_recording_policy)
    write_table(resolved, args.out)
    if args.duplicates_out:
        write_table(duplicates, args.duplicates_out)
    print(
        {
            "out": args.out,
            "policy": args.duplicate_recording_policy,
            "input_recordings": len(recordings),
            "output_recordings": len(resolved),
            "duplicate_rows": len(duplicates),
            "dropped_recordings": len(recordings) - len(resolved),
        }
    )


if __name__ == "__main__":
    main()
