from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from src.datasets.schemas import validate_events, validate_recordings
from src.utils.io import read_table, write_table

TABLE_SUFFIXES = {".csv", ".tsv", ".parquet"}
SKIP_DIRS = {".git", ".mypy_cache", ".pytest_cache", ".ruff_cache", ".venv", "__pycache__"}
SOURCE_ROLES = ("recordings", "events")


@dataclass(frozen=True)
class GateCSourceDiscovery:
    summary: dict[str, Any]
    candidates: pd.DataFrame
    markdown: str


def _role_error(df: pd.DataFrame, role: str) -> str | None:
    try:
        if role == "recordings":
            validate_recordings(df, allow_empty=False)
        elif role == "events":
            validate_events(df, allow_empty=False)
        else:
            raise ValueError(f"unknown source role {role}")
    except ValueError as exc:
        return str(exc)
    return None


def _iter_table_files(roots: tuple[str | Path, ...], *, max_bytes: int) -> list[Path]:
    files: list[Path] = []
    for root_value in roots:
        root = Path(root_value)
        if not root.exists():
            continue
        if root.is_file():
            if root.suffix in TABLE_SUFFIXES and root.stat().st_size <= max_bytes:
                files.append(root)
            continue
        for path in root.rglob("*"):
            if any(part in SKIP_DIRS for part in path.parts):
                continue
            if path.is_file() and path.suffix in TABLE_SUFFIXES and path.stat().st_size <= max_bytes:
                files.append(path)
    return sorted(set(files))


def _candidate_row(path: Path) -> dict[str, Any]:
    row: dict[str, Any] = {
        "path": str(path),
        "bytes": int(path.stat().st_size),
        "read_status": "ok",
        "row_count": None,
        "column_count": None,
        "columns": None,
    }
    try:
        table = read_table(path)
    except Exception as exc:
        row["read_status"] = "read_error"
        row["read_error"] = str(exc)
        for role in SOURCE_ROLES:
            row[f"{role}_ready"] = False
            row[f"{role}_reason"] = "table could not be read"
        row["candidate_roles"] = ""
        return row

    row["row_count"] = int(len(table))
    row["column_count"] = int(len(table.columns))
    row["columns"] = ",".join(str(column) for column in table.columns)
    roles = []
    for role in SOURCE_ROLES:
        error = _role_error(table, role)
        row[f"{role}_ready"] = error is None
        row[f"{role}_reason"] = "ok" if error is None else error
        if error is None:
            roles.append(role)
    row["candidate_roles"] = ",".join(roles)
    return row


def _summary(candidates: pd.DataFrame, roots: tuple[str | Path, ...]) -> dict[str, Any]:
    role_counts = {
        role: int(candidates[f"{role}_ready"].fillna(False).astype(bool).sum())
        if f"{role}_ready" in candidates.columns
        else 0
        for role in SOURCE_ROLES
    }
    role_files = {
        role: candidates.loc[candidates[f"{role}_ready"].fillna(False), "path"].tolist()
        if f"{role}_ready" in candidates.columns
        else []
        for role in SOURCE_ROLES
    }
    missing_roles = [role for role, count in role_counts.items() if count == 0]
    return {
        "scan_status": "gate_c_sources_available"
        if not missing_roles
        else "blocked_missing_gate_c_sources",
        "roots": [str(root) for root in roots],
        "files_scanned": int(len(candidates)),
        "readable_tables": int(candidates["read_status"].eq("ok").sum()) if len(candidates) else 0,
        "role_ready_counts": role_counts,
        "candidate_files_by_role": role_files,
        "missing_roles": missing_roles,
    }


def _candidate_table_markdown(candidates: pd.DataFrame) -> str:
    table = candidates.loc[
        candidates["candidate_roles"].fillna("").ne(""),
        ["path", "candidate_roles", "row_count"],
    ]
    if table.empty:
        return "_No Gate C source-ready candidate files found._"
    rows = ["| path | candidate_roles | row_count |", "| --- | --- | --- |"]
    for _, row in table.iterrows():
        rows.append(
            "| "
            + " | ".join(
                [
                    str(row["path"]).replace("|", "\\|"),
                    str(row["candidate_roles"]).replace("|", "\\|"),
                    str(row["row_count"]).replace("|", "\\|"),
                ]
            )
            + " |"
        )
    return "\n".join(rows)


def _markdown(summary: dict[str, Any], candidates: pd.DataFrame) -> str:
    role_lines = "\n".join(
        f"- {role}: {summary['role_ready_counts'][role]}" for role in SOURCE_ROLES
    )
    missing = summary["missing_roles"] or ["none"]
    return f"""# Gate C Source Discovery

**Status:** `{summary["scan_status"]}`

This report scans local tables for source artifacts that can feed
`scripts/materialize_gate_c_inputs.py`. It does not materialize labels, freeze
splits, or make any benchmark row citable.

## Summary

- Files scanned: `{summary["files_scanned"]}`
- Readable tables: `{summary["readable_tables"]}`
- Missing source roles: `{", ".join(missing)}`

## Source-Ready Counts

{role_lines}

## Candidate Source Files

{_candidate_table_markdown(candidates)}

## Next Action

If either source role is missing, recover or generate real `recordings` and
`events` tables before running `scripts/materialize_gate_c_inputs.py`.
"""


def discover_gate_c_sources(
    roots: tuple[str | Path, ...],
    *,
    max_bytes: int = 128 * 1024 * 1024,
) -> GateCSourceDiscovery:
    rows = [_candidate_row(path) for path in _iter_table_files(roots, max_bytes=max_bytes)]
    candidates = pd.DataFrame(rows)
    if candidates.empty:
        candidates = pd.DataFrame(
            columns=[
                "path",
                "bytes",
                "read_status",
                "row_count",
                "column_count",
                "columns",
                "recordings_ready",
                "recordings_reason",
                "events_ready",
                "events_reason",
                "candidate_roles",
            ]
        )
    summary = _summary(candidates, roots)
    return GateCSourceDiscovery(
        summary=summary,
        candidates=candidates,
        markdown=_markdown(summary, candidates),
    )


def write_gate_c_source_discovery(discovery: GateCSourceDiscovery, out_dir: str | Path) -> dict[str, str]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "summary": str(out_dir / "gate_c_source_discovery.json"),
        "candidates": str(out_dir / "gate_c_source_candidates.csv"),
        "markdown": str(out_dir / "gate_c_source_discovery.md"),
    }
    Path(paths["summary"]).write_text(json.dumps(discovery.summary, indent=2), encoding="utf-8")
    write_table(discovery.candidates, paths["candidates"])
    Path(paths["markdown"]).write_text(discovery.markdown, encoding="utf-8")
    return paths
