#!/usr/bin/env python
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.reports.paper_artifact_package import (  # noqa: E402
    PaperArtifactPackageConfig,
    build_paper_artifact_package,
    manifest_json,
    paper_artifact_package_markdown,
)
from src.utils.io import read_table, write_table  # noqa: E402


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build a paper reproducibility artifact package with claim traceability."
    )
    parser.add_argument("--root", default=str(REPO_ROOT))
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--claims", default=None, help="Optional claim table CSV/TSV/parquet")
    parser.add_argument("--title", default="EpiTwin-Open Paper Artifact Package")
    parser.add_argument(
        "--package-status",
        default="pre_gate_c_reproducibility_package",
    )
    parser.add_argument(
        "--gate-c-status",
        choices=["not_started", "partial", "passed", "failed"],
        default="not_started",
    )
    parser.add_argument(
        "--citation-status",
        choices=["not_citable_pre_gate_c", "citable_after_gate_c"],
        default="not_citable_pre_gate_c",
    )
    parser.add_argument(
        "--all-files",
        action="store_true",
        help="Include matching files even when they are not tracked by git.",
    )
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    if args.citation_status == "citable_after_gate_c" and args.gate_c_status != "passed":
        raise SystemExit("citable paper artifact packages require --gate-c-status passed")
    config = PaperArtifactPackageConfig(
        title=args.title,
        package_status=args.package_status,
        gate_c_status=args.gate_c_status,
        citation_status=args.citation_status,
        tracked_only=not args.all_files,
    )
    claims = read_table(args.claims) if args.claims else None
    package = build_paper_artifact_package(root=args.root, config=config, claims=claims)
    out_dir = Path(args.out_dir)
    write_table(package.inventory, out_dir / "paper_artifact_inventory.csv")
    write_table(package.claims, out_dir / "paper_claim_traceability.csv")
    write_table(package.checklist, out_dir / "paper_reproducibility_checklist.csv")
    (out_dir / "paper_artifact_manifest.json").write_text(
        manifest_json(package),
        encoding="utf-8",
    )
    (out_dir / "paper_artifact_package.md").write_text(
        paper_artifact_package_markdown(package),
        encoding="utf-8",
    )
    print(manifest_json(package))


if __name__ == "__main__":
    main()
