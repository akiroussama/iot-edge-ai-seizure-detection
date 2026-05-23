#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.artifacts.gate_c_freeze_package import (  # noqa: E402
    build_gate_c_freeze_package,
    write_gate_c_freeze_package,
)


def _parse_metadata(value: str) -> tuple[str, Path]:
    parts = value.split("=", maxsplit=1)
    if len(parts) != 2:
        raise argparse.ArgumentTypeError("--metadata must be formatted as NAME=PATH")
    name = parts[0].strip()
    path = parts[1].strip()
    if not name or not path:
        raise argparse.ArgumentTypeError("--metadata must be formatted as NAME=PATH")
    return name, Path(path)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a verified Gate C frozen/citable artifact package."
    )
    parser.add_argument("--events", required=True, help="Frozen events table")
    parser.add_argument("--labels", required=True, help="Frozen labeled windows table")
    parser.add_argument("--splits", required=True, help="Frozen split assignment table")
    parser.add_argument("--out-dir", required=True, help="Output package directory")
    parser.add_argument("--registry-id", required=True)
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--dataset-version", required=True)
    parser.add_argument("--source-uri", required=True)
    parser.add_argument("--generation-command", required=True)
    parser.add_argument("--split-policy", required=True)
    parser.add_argument("--split-ref", required=True)
    parser.add_argument("--split-id", action="append", required=True)
    parser.add_argument("--horizon-name", required=True)
    parser.add_argument("--sph-minutes", type=float, required=True)
    parser.add_argument("--sop-minutes", type=float, required=True)
    parser.add_argument("--doi-or-prereg-uri", required=True)
    parser.add_argument(
        "--gate-b-status",
        choices=["not_started", "partial", "passed", "failed"],
        default="passed",
    )
    parser.add_argument("--metadata", action="append", type=_parse_metadata, default=[])
    parser.add_argument("--notes", default=None)
    parser.add_argument("--root", default=".")
    parser.add_argument("--split-col", default="split")
    return parser


def main() -> None:
    args = _build_parser().parse_args()
    try:
        package = build_gate_c_freeze_package(
            events_path=args.events,
            labels_path=args.labels,
            splits_path=args.splits,
            registry_id=args.registry_id,
            dataset=args.dataset,
            dataset_version=args.dataset_version,
            source_uri=args.source_uri,
            generation_command=args.generation_command,
            split_policy=args.split_policy,
            split_ref=args.split_ref,
            split_ids=tuple(args.split_id),
            horizon_name=args.horizon_name,
            sph_minutes=args.sph_minutes,
            sop_minutes=args.sop_minutes,
            doi_or_prereg_uri=args.doi_or_prereg_uri,
            gate_b_status=args.gate_b_status,
            notes=args.notes,
            metadata_artifacts=tuple(args.metadata),
            root=args.root,
            split_col=args.split_col,
        )
        package = write_gate_c_freeze_package(package, args.out_dir)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    print(
        json.dumps(
            {
                "out_dir": args.out_dir,
                "registry": package.output_paths["registry"],
                "dry_run_json": package.output_paths["dry_run_json"],
                "manifest": package.output_paths["manifest"],
                "readiness_status": package.dry_run_diagnostics["readiness_status"],
                "citable_ready": package.dry_run_diagnostics["citable_ready"],
                "artifact_count": len(package.registry["artifacts"]),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
