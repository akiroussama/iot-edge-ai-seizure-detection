from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import argparse

from src.datasets.msg_loader import inspect_msg_raw_layout, prepare_mock_msg_tables, prepare_msg_tables


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare supported My Seizure Gauge metadata tables.")
    parser.add_argument("--raw-dir", default=None)
    parser.add_argument("--processed-dir", required=True)
    parser.add_argument("--inspect-only", action="store_true")
    parser.add_argument("--mock", action="store_true", help="Write deterministic mock artifacts.")
    parser.add_argument(
        "--duplicate-recording-policy",
        choices=["error", "drop_exact"],
        default="error",
        help="MSG duplicate recording time-range policy. Use drop_exact only after documenting duplicated files.",
    )
    args = parser.parse_args()

    if args.mock:
        written = prepare_mock_msg_tables(args.processed_dir)
        print({"mode": "mock", "written": {key: str(path) for key, path in written.items()}})
        return
    if not args.raw_dir:
        raise SystemExit("Provide --raw-dir unless using --mock")
    layout = inspect_msg_raw_layout(args.raw_dir)
    print(layout)
    if args.inspect_only:
        return
    try:
        written = prepare_msg_tables(
            args.raw_dir,
            args.processed_dir,
            duplicate_time_range_policy=args.duplicate_recording_policy,
        )
    except (FileNotFoundError, ValueError) as exc:
        raise SystemExit(f"My Seizure Gauge preparation failed: {exc}") from exc
    print({key: str(path) for key, path in written.items()})


if __name__ == "__main__":
    main()
