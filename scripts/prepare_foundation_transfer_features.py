#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.features.foundation_transfer import (  # noqa: E402
    FoundationTransferConfig,
    build_foundation_transfer_features,
    foundation_transfer_markdown,
    table_records,
)
from src.utils.io import read_table, write_table  # noqa: E402


def _split_csv(value: str | None) -> tuple[str, ...]:
    if not value:
        return ()
    return tuple(item.strip() for item in value.split(",") if item.strip())


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Attach frozen foundation-model embeddings to window features."
    )
    parser.add_argument("--features", required=True)
    parser.add_argument("--embeddings", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--model-name", required=True)
    parser.add_argument("--source-name", required=True)
    parser.add_argument("--source-url", default=None)
    parser.add_argument("--source-doi", default=None)
    parser.add_argument("--license-name", required=True)
    parser.add_argument("--license-allows-research-use", action="store_true")
    parser.add_argument("--modality", required=True)
    parser.add_argument("--join-keys", default="patient_id,recording_id,window_start,window_end")
    parser.add_argument("--embedding-prefix", default="embedding_")
    parser.add_argument("--embedding-cols", default=None)
    parser.add_argument("--output-prefix", default="fm")
    parser.add_argument("--allow-missing-coverage", action="store_true")
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
    parser.add_argument("--title", default="Foundation-Model Transfer Baseline")
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    config = FoundationTransferConfig(
        model_name=args.model_name,
        source_name=args.source_name,
        source_url=args.source_url,
        source_doi=args.source_doi,
        license_name=args.license_name,
        license_allows_research_use=args.license_allows_research_use,
        modality=args.modality,
        join_keys=_split_csv(args.join_keys),
        embedding_prefix=args.embedding_prefix,
        embedding_cols=_split_csv(args.embedding_cols),
        output_prefix=args.output_prefix,
        require_complete_coverage=not args.allow_missing_coverage,
        gate_c_status=args.gate_c_status,
        citation_status=args.citation_status,
    )
    result = build_foundation_transfer_features(
        read_table(args.features),
        read_table(args.embeddings),
        config=config,
    )
    out_dir = Path(args.out_dir)
    write_table(result.features, out_dir / "foundation_transfer_features.csv")
    write_table(result.manifest, out_dir / "foundation_transfer_manifest.csv")
    (out_dir / "foundation_transfer_manifest.json").write_text(
        json.dumps(table_records(result.manifest), indent=2),
        encoding="utf-8",
    )
    (out_dir / "foundation_transfer_report.md").write_text(
        foundation_transfer_markdown(result, title=args.title),
        encoding="utf-8",
    )
    print(json.dumps(result.metadata, indent=2))


if __name__ == "__main__":
    main()
