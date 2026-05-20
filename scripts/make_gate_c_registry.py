#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.artifacts.registry import build_artifact_record, build_gate_c_registry


def _parse_artifact(value: str) -> tuple[str, str, Path]:
    parts = value.split("=", maxsplit=1)
    if len(parts) != 2 or ":" not in parts[1]:
        raise argparse.ArgumentTypeError("--artifact must be formatted as NAME=ROLE:PATH")
    name = parts[0].strip()
    role, path = parts[1].split(":", maxsplit=1)
    role = role.strip()
    if not name or not role or not path:
        raise argparse.ArgumentTypeError("--artifact must be formatted as NAME=ROLE:PATH")
    return name, role, Path(path)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create a Gate C artifact registry JSON.")
    parser.add_argument("--out", required=True)
    parser.add_argument("--registry-id", required=True)
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--dataset-version", required=True)
    parser.add_argument("--source-uri", required=True)
    parser.add_argument("--generation-command", required=True)
    parser.add_argument(
        "--artifact",
        action="append",
        type=_parse_artifact,
        required=True,
        help="Artifact entry formatted as NAME=ROLE:PATH. Repeat for multiple artifacts.",
    )
    parser.add_argument("--split-policy", required=True)
    parser.add_argument("--split-ref", required=True)
    parser.add_argument("--split-id", action="append", required=True)
    parser.add_argument("--horizon-name", default=None)
    parser.add_argument("--sph-minutes", type=float, default=None)
    parser.add_argument("--sop-minutes", type=float, default=None)
    parser.add_argument(
        "--gate-c-status",
        choices=["not_started", "partial", "passed", "failed"],
        default="not_started",
    )
    parser.add_argument(
        "--freeze-status",
        choices=["engineering_scaffold", "pending_human_audit", "frozen", "failed"],
        default="engineering_scaffold",
    )
    parser.add_argument("--doi-or-prereg-uri", default=None)
    parser.add_argument("--notes", default=None)
    parser.add_argument("--root", default=".")
    parser.add_argument("--split-col", default="split")
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    artifacts = [
        build_artifact_record(
            name=name,
            role=role,
            path=path,
            root=args.root,
            split_col=args.split_col,
        )
        for name, role, path in args.artifact
    ]
    registry = build_gate_c_registry(
        registry_id=args.registry_id,
        dataset=args.dataset,
        dataset_version=args.dataset_version,
        source_uri=args.source_uri,
        generation_command=args.generation_command,
        artifacts=artifacts,
        split_manifest={
            "split_policy": args.split_policy,
            "split_ids": args.split_id,
            "split_ref": args.split_ref,
            "horizon_name": args.horizon_name,
            "sph_minutes": args.sph_minutes,
            "sop_minutes": args.sop_minutes,
        },
        gate_c_status=args.gate_c_status,
        freeze_status=args.freeze_status,
        doi_or_prereg_uri=args.doi_or_prereg_uri,
        notes=args.notes,
    )
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(registry, indent=2), encoding="utf-8")
    print(json.dumps({"out": str(out), "artifacts": len(artifacts)}, indent=2))


if __name__ == "__main__":
    main()
