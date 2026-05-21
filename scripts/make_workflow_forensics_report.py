#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.reports.workflow_forensics import (  # noqa: E402
    WorkflowForensicsConfig,
    build_workflow_forensics_report,
    table_records,
    workflow_forensics_markdown,
)
from src.utils.io import write_table  # noqa: E402


def _parse_globs(value: str | None) -> tuple[str, ...]:
    if not value:
        return ("docs/research/*.md", "docs/*.md")
    globs = tuple(item.strip() for item in value.split(",") if item.strip())
    if not globs:
        raise argparse.ArgumentTypeError("doc glob list cannot be empty")
    return globs


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Extract descriptive workflow-forensics tables from git history "
            "and repository research documents."
        )
    )
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--max-commits", type=int, default=200)
    parser.add_argument("--doc-globs", type=_parse_globs, default=("docs/research/*.md", "docs/*.md"))
    parser.add_argument("--no-merge-commits", action="store_true")
    parser.add_argument("--title", default="Workflow Forensics Report")
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    config = WorkflowForensicsConfig(
        max_commits=args.max_commits,
        doc_globs=args.doc_globs,
        include_merge_commits=not args.no_merge_commits,
    )
    report = build_workflow_forensics_report(args.repo_root, config=config)
    out_dir = Path(args.out_dir)
    write_table(report.commits, out_dir / "workflow_commits.csv")
    write_table(report.task_docs, out_dir / "workflow_task_docs.csv")
    write_table(report.artifact_summary, out_dir / "workflow_artifact_summary.csv")
    write_table(report.validation_summary, out_dir / "workflow_validation_summary.csv")
    write_table(report.manifest, out_dir / "workflow_forensics_manifest.csv")
    payload = {
        "metadata": report.metadata,
        "artifact_summary": table_records(report.artifact_summary),
        "validation_summary": table_records(report.validation_summary),
        "commits": table_records(report.commits),
        "task_docs": table_records(report.task_docs),
    }
    (out_dir / "workflow_forensics_report.json").write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )
    (out_dir / "workflow_forensics_report.md").write_text(
        workflow_forensics_markdown(report, title=args.title),
        encoding="utf-8",
    )
    print(json.dumps({"out_dir": str(out_dir), **report.metadata}, indent=2))


if __name__ == "__main__":
    main()
