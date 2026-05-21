from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from src.reports.workflow_forensics import (
    WorkflowForensicsConfig,
    build_workflow_forensics_report,
    collect_git_commit_table,
    scan_research_documents,
)
from src.utils.io import read_table


def _run(cmd: list[str], cwd: Path) -> None:
    subprocess.run(cmd, cwd=cwd, check=True, text=True, capture_output=True)


def _commit(repo: Path, message: str) -> None:
    _run(["git", "add", "."], repo)
    _run(["git", "commit", "-m", message], repo)


def _synthetic_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _run(["git", "init"], repo)
    _run(["git", "config", "user.email", "test@example.com"], repo)
    _run(["git", "config", "user.name", "Workflow Test"], repo)
    (repo / "docs" / "research").mkdir(parents=True)
    (repo / "docs" / "research" / "2026-05-21_t1_example.md").write_text(
        """# T1 Example

## Validation

```bash
uv run --extra dev ruff check .
uv run --extra dev pytest
```

Result: 2 passed.

## Remaining Limits

Pre-Gate-C, not citable, leakage guardrail documented.
""",
        encoding="utf-8",
    )
    _commit(repo, "docs: add task trace (#1)")
    (repo / "src").mkdir()
    (repo / "tests").mkdir()
    (repo / "scripts").mkdir()
    (repo / "src" / "example.py").write_text("VALUE = 1\n", encoding="utf-8")
    (repo / "tests" / "test_example.py").write_text("def test_value():\n    assert 1\n", encoding="utf-8")
    (repo / "scripts" / "run_example.py").write_text("print('ok')\n", encoding="utf-8")
    _commit(repo, "feat: add example implementation (#2)")
    return repo


def test_collect_git_commit_table_marks_artifact_classes(tmp_path) -> None:
    repo = _synthetic_repo(tmp_path)

    commits = collect_git_commit_table(repo, max_commits=10)

    assert len(commits) == 2
    assert commits["pr_number"].tolist() == [2, 1]
    assert bool(commits.loc[0, "touches_src"]) is True
    assert bool(commits.loc[0, "touches_tests"]) is True
    assert bool(commits.loc[1, "touches_research_docs"]) is True


def test_scan_research_documents_counts_validation_and_guardrails(tmp_path) -> None:
    repo = _synthetic_repo(tmp_path)

    docs = scan_research_documents(repo, doc_globs=("docs/research/*.md",))

    assert docs.loc[0, "task_label"] == "T1"
    assert bool(docs.loc[0, "has_validation_section"]) is True
    assert bool(docs.loc[0, "has_remaining_limits"]) is True
    assert bool(docs.loc[0, "mentions_gate_c"]) is True
    assert bool(docs.loc[0, "mentions_not_citable"]) is True
    assert bool(docs.loc[0, "mentions_leakage"]) is True
    assert docs.loc[0, "validation_mentions"] >= 3
    assert docs.loc[0, "guardrail_mentions"] >= 3


def test_workflow_forensics_report_summarizes_repo(tmp_path) -> None:
    repo = _synthetic_repo(tmp_path)

    report = build_workflow_forensics_report(
        repo,
        config=WorkflowForensicsConfig(max_commits=10, doc_globs=("docs/research/*.md",)),
    )

    assert report.metadata["commit_rows"] == 2
    assert report.metadata["research_doc_rows"] == 1
    assert report.artifact_summary.set_index("artifact_class").loc["src", "commits_touching"] == 1
    assert report.validation_summary.loc[0, "docs_with_validation_section"] == 1
    assert report.manifest.loc[0, "evidence_scope"] == "git_history_and_repository_docs_only"


def test_make_workflow_forensics_cli_writes_outputs(tmp_path) -> None:
    repo = _synthetic_repo(tmp_path)
    out_dir = tmp_path / "workflow"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/make_workflow_forensics_report.py",
            "--repo-root",
            str(repo),
            "--out-dir",
            str(out_dir),
            "--max-commits",
            "10",
            "--doc-globs",
            "docs/research/*.md",
        ],
        check=True,
        text=True,
        capture_output=True,
    )

    assert '"evidence_scope": "git_history_and_repository_docs_only"' in result.stdout
    commits = read_table(out_dir / "workflow_commits.csv")
    docs = read_table(out_dir / "workflow_task_docs.csv")
    validation = read_table(out_dir / "workflow_validation_summary.csv")
    manifest = read_table(out_dir / "workflow_forensics_manifest.csv")
    payload = json.loads((out_dir / "workflow_forensics_report.json").read_text(encoding="utf-8"))
    assert len(commits) == 2
    assert docs.loc[0, "task_label"] == "T1"
    assert validation.loc[0, "docs_mentioning_not_citable"] == 1
    assert manifest.loc[0, "commit_rows"] == 2
    assert payload["metadata"]["research_doc_rows"] == 1
    assert "descriptive methodology evidence" in (
        out_dir / "workflow_forensics_report.md"
    ).read_text(encoding="utf-8")
