#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.artifacts.gate_c_input_discovery import (  # noqa: E402
    discover_gate_c_inputs,
    write_gate_c_input_discovery,
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Discover local table files that can serve as Gate C freeze inputs."
    )
    parser.add_argument(
        "--root",
        action="append",
        default=None,
        help="Root directory or table file to scan. Defaults to data and reports.",
    )
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--max-file-mb", type=float, default=128.0)
    return parser


def main() -> None:
    args = _build_parser().parse_args()
    roots = tuple(args.root or ["data", "reports"])
    discovery = discover_gate_c_inputs(
        roots,
        max_bytes=int(args.max_file_mb * 1024 * 1024),
    )
    paths = write_gate_c_input_discovery(discovery, args.out_dir)
    print(
        json.dumps(
            {
                **discovery.summary,
                "output_paths": paths,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
