from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
import re
import subprocess

import numpy as np
import pandas as pd


FIELD_SEP = "\x1f"
COMMIT_SEP = "\x1e"
DEFAULT_DOC_GLOBS = (
    "docs/research/*.md",
    "docs/*.md",
)
VALIDATION_PATTERNS = (
    r"uv run",
    r"pytest",
    r"ruff",
    r"passed",
    r"validation",
)
GUARDRAIL_PATTERNS = (
    r"gate c",
    r"pre-gate-c",
    r"not citable",
    r"leakage",
    r"guardrail",
    r"frozen",
)


@dataclass(frozen=True)
class WorkflowForensicsConfig:
    max_commits: int = 200
    doc_globs: tuple[str, ...] = DEFAULT_DOC_GLOBS
    include_merge_commits: bool = True


@dataclass(frozen=True)
class WorkflowForensicsReport:
    commits: pd.DataFrame
    task_docs: pd.DataFrame
    artifact_summary: pd.DataFrame
    validation_summary: pd.DataFrame
    manifest: pd.DataFrame
    metadata: dict[str, Any]


def _run_git(repo_root: Path, args: list[str]) -> str:
    return subprocess.check_output(
        ["git", *args],
        cwd=repo_root,
        text=True,
        stderr=subprocess.DEVNULL,
    )


def _repo_commit(repo_root: Path) -> str | None:
    try:
        return _run_git(repo_root, ["rev-parse", "--short=12", "HEAD"]).strip()
    except Exception:
        return None


def _extract_pr_number(subject: str) -> int | None:
    match = re.search(r"\(#(\d+)\)", subject)
    return int(match.group(1)) if match else None


def _artifact_flags(paths: list[str]) -> dict[str, bool]:
    return {
        "touches_src": any(path.startswith("src/") for path in paths),
        "touches_scripts": any(path.startswith("scripts/") for path in paths),
        "touches_tests": any(path.startswith("tests/") for path in paths),
        "touches_docs": any(path.startswith("docs/") for path in paths),
        "touches_research_docs": any(path.startswith("docs/research/") for path in paths),
        "touches_configs": any(path.startswith("configs/") for path in paths),
        "touches_schemas": any(path.startswith("schemas/") for path in paths),
    }


def collect_git_commit_table(
    repo_root: str | Path,
    *,
    max_commits: int = 200,
    include_merge_commits: bool = True,
) -> pd.DataFrame:
    root = Path(repo_root)
    pretty = f"--pretty=format:{COMMIT_SEP}%H{FIELD_SEP}%h{FIELD_SEP}%ad{FIELD_SEP}%s"
    args = [
        "log",
        f"--max-count={max_commits}",
        "--date=iso-strict",
        pretty,
        "--name-only",
    ]
    if not include_merge_commits:
        args.insert(1, "--no-merges")
    raw = _run_git(root, args)
    rows = []
    for block in raw.split(COMMIT_SEP):
        block = block.strip("\n")
        if not block:
            continue
        lines = block.splitlines()
        fields = lines[0].split(FIELD_SEP)
        if len(fields) != 4:
            continue
        commit_sha, short_sha, date, subject = fields
        paths = [line.strip() for line in lines[1:] if line.strip()]
        flags = _artifact_flags(paths)
        rows.append(
            {
                "commit_sha": commit_sha,
                "short_sha": short_sha,
                "date": date,
                "subject": subject,
                "pr_number": _extract_pr_number(subject),
                "changed_files": len(paths),
                "changed_paths": ";".join(paths),
                **flags,
                "workflow_iteration": bool(_extract_pr_number(subject))
                or flags["touches_research_docs"],
            }
        )
    return pd.DataFrame(rows)


def _count_patterns(text: str, patterns: tuple[str, ...]) -> int:
    normalized = text.lower()
    return int(sum(len(re.findall(pattern, normalized, flags=re.IGNORECASE)) for pattern in patterns))


def _first_markdown_title(text: str, fallback: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def _task_label(path: Path) -> str:
    name = path.stem
    match = re.search(r"(task\d+|t\d+|p\d+|m\d+|w\d+|f\d+)", name, flags=re.IGNORECASE)
    return match.group(1).upper() if match else name


def scan_research_documents(
    repo_root: str | Path,
    *,
    doc_globs: tuple[str, ...] = DEFAULT_DOC_GLOBS,
) -> pd.DataFrame:
    root = Path(repo_root)
    paths: list[Path] = []
    for pattern in doc_globs:
        paths.extend(root.glob(pattern))
    unique_paths = sorted({path for path in paths if path.is_file()})
    rows = []
    for path in unique_paths:
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(root).as_posix()
        validation_mentions = _count_patterns(text, VALIDATION_PATTERNS)
        guardrail_mentions = _count_patterns(text, GUARDRAIL_PATTERNS)
        rows.append(
            {
                "path": rel,
                "task_label": _task_label(path),
                "title": _first_markdown_title(text, path.stem),
                "line_count": len(text.splitlines()),
                "validation_mentions": validation_mentions,
                "guardrail_mentions": guardrail_mentions,
                "has_validation_section": bool(re.search(r"^## Validation", text, re.MULTILINE)),
                "has_remaining_limits": bool(re.search(r"^## Remaining Limits", text, re.MULTILINE)),
                "mentions_gate_c": bool(re.search(r"gate c|gate-c", text, flags=re.IGNORECASE)),
                "mentions_not_citable": bool(re.search(r"not citable", text, flags=re.IGNORECASE)),
                "mentions_leakage": bool(re.search(r"leakage", text, flags=re.IGNORECASE)),
            }
        )
    return pd.DataFrame(rows)


def artifact_summary(commits: pd.DataFrame) -> pd.DataFrame:
    if commits.empty:
        return pd.DataFrame(columns=["artifact_class", "commits_touching", "fraction_of_commits"])
    flags = [
        "touches_src",
        "touches_scripts",
        "touches_tests",
        "touches_docs",
        "touches_research_docs",
        "touches_configs",
        "touches_schemas",
    ]
    rows = []
    denominator = max(len(commits), 1)
    for flag in flags:
        count = int(commits[flag].fillna(False).astype(bool).sum())
        rows.append(
            {
                "artifact_class": flag.removeprefix("touches_"),
                "commits_touching": count,
                "fraction_of_commits": float(count / denominator),
            }
        )
    return pd.DataFrame(rows)


def validation_summary(task_docs: pd.DataFrame) -> pd.DataFrame:
    if task_docs.empty:
        return pd.DataFrame(
            columns=[
                "document_count",
                "docs_with_validation_section",
                "docs_with_remaining_limits",
                "docs_mentioning_gate_c",
                "docs_mentioning_not_citable",
                "docs_mentioning_leakage",
                "total_validation_mentions",
                "total_guardrail_mentions",
            ]
        )
    return pd.DataFrame(
        [
            {
                "document_count": int(len(task_docs)),
                "docs_with_validation_section": int(task_docs["has_validation_section"].sum()),
                "docs_with_remaining_limits": int(task_docs["has_remaining_limits"].sum()),
                "docs_mentioning_gate_c": int(task_docs["mentions_gate_c"].sum()),
                "docs_mentioning_not_citable": int(task_docs["mentions_not_citable"].sum()),
                "docs_mentioning_leakage": int(task_docs["mentions_leakage"].sum()),
                "total_validation_mentions": int(task_docs["validation_mentions"].sum()),
                "total_guardrail_mentions": int(task_docs["guardrail_mentions"].sum()),
            }
        ]
    )


def build_workflow_forensics_report(
    repo_root: str | Path,
    *,
    config: WorkflowForensicsConfig | None = None,
) -> WorkflowForensicsReport:
    cfg = config or WorkflowForensicsConfig()
    if cfg.max_commits <= 0:
        raise ValueError("max_commits must be positive")
    root = Path(repo_root)
    commits = collect_git_commit_table(
        root,
        max_commits=cfg.max_commits,
        include_merge_commits=cfg.include_merge_commits,
    )
    docs = scan_research_documents(root, doc_globs=cfg.doc_globs)
    artifacts = artifact_summary(commits)
    validation = validation_summary(docs)
    metadata = {
        "repo_root": str(root),
        "repo_commit": _repo_commit(root),
        "max_commits": int(cfg.max_commits),
        "commit_rows": int(len(commits)),
        "workflow_iteration_commits": int(commits.get("workflow_iteration", pd.Series(dtype=bool)).sum())
        if not commits.empty
        else 0,
        "research_doc_rows": int(len(docs)),
        "doc_globs": list(cfg.doc_globs),
        "result_status": "workflow_forensics_descriptive_not_benchmark",
        "evidence_scope": "git_history_and_repository_docs_only",
    }
    manifest = pd.DataFrame([metadata | {"config": asdict(cfg)}])
    return WorkflowForensicsReport(
        commits=commits,
        task_docs=docs,
        artifact_summary=artifacts,
        validation_summary=validation,
        manifest=manifest,
        metadata=metadata,
    )


def _markdown_table(df: pd.DataFrame, max_rows: int = 20) -> str:
    if df.empty:
        return "_No rows._"
    view = df.head(max_rows)
    headers = [str(column) for column in view.columns]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for _, row in view.iterrows():
        lines.append("| " + " | ".join(str(row[column]) for column in view.columns) + " |")
    if len(df) > max_rows:
        lines.append(f"\n_Showing {max_rows} of {len(df)} rows._")
    return "\n".join(lines)


def workflow_forensics_markdown(
    report: WorkflowForensicsReport,
    *,
    title: str = "Workflow Forensics Report",
) -> str:
    return f"""# {title}

This report is descriptive methodology evidence, not a clinical benchmark.

## Metadata

- Repository commit: `{report.metadata["repo_commit"]}`
- Commit rows scanned: `{report.metadata["commit_rows"]}`
- Workflow-iteration commits: `{report.metadata["workflow_iteration_commits"]}`
- Research/document rows scanned: `{report.metadata["research_doc_rows"]}`
- Evidence scope: `{report.metadata["evidence_scope"]}`

## Artifact Summary

{_markdown_table(report.artifact_summary)}

## Validation And Guardrail Summary

{_markdown_table(report.validation_summary)}

## Recent Workflow Commits

{_markdown_table(report.commits)}

## Research Documents

{_markdown_table(report.task_docs)}
"""


def table_records(df: pd.DataFrame) -> list[dict[str, Any]]:
    records = []
    for record in df.to_dict(orient="records"):
        clean = {}
        for key, value in record.items():
            if isinstance(value, float) and (np.isnan(value) or np.isinf(value)):
                clean[key] = None
            elif value is pd.NA or value is pd.NaT:
                clean[key] = None
            elif isinstance(value, np.integer):
                clean[key] = int(value)
            elif isinstance(value, np.floating):
                clean[key] = float(value)
            else:
                clean[key] = value
        records.append(clean)
    return records
