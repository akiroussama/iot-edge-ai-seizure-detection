#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.artifacts.registry import load_registry, verify_gate_c_registry


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify a Gate C artifact registry.")
    parser.add_argument("--registry", required=True)
    parser.add_argument("--root", default=".")
    parser.add_argument("--split-col", default="split")
    parser.add_argument("--require-frozen", action="store_true")
    args = parser.parse_args()

    result = verify_gate_c_registry(
        load_registry(args.registry),
        root=args.root,
        require_frozen=args.require_frozen,
        split_col=args.split_col,
    )
    print(json.dumps(result, indent=2))
    if not result["ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
