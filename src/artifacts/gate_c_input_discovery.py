from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from src.artifacts.gate_c_freeze_package import LABELS_SCHEMA, SPLITS_SCHEMA
from src.datasets.schemas import validate_events
from src.utils.io import read_table, write_table
from src.utils.validation import validate_no_null_ids, validate_table_schema, validate_time_order

TABLE_SUFFIXES = {".csv", ".tsv", ".parquet"}
SKIP_DIRS = {".git", ".mypy_cache", ".pytest_cache", ".ruff_cache", ".venv", "__pycache__"}
DISCOVERY_ROLES = ("events", "labels", "splits")
SPLIT_KEY_CANDIDATES = (
    ("patient_id", "recording_id", "window_start", "window_end"),
    ("patient_id", "recording_id"),
    ("patient_id",),
    ("recording_id",),
)


@dataclass(frozen=True)
class GateCInputDiscovery:
    summary: dict[str, Any]
    candidates: pd.DataFrame
    markdown: str


def _split_values(df: pd.DataFrame, table_name: str) -> None:
    values = df["split"].astype(str).str.strip()
    if values.eq("").any():
        raise ValueError(f"{table_name}.split contains empty split identifiers")


def _validate_label_candidate(df: pd.DataFrame) -> None:
    validate_table_schema(df, LABELS_SCHEMA, allow_empty=False)
    validate_no_null_ids(df, ("patient_id", "recording_id"), "labels")
    validate_time_order(df, "window_start", "window_end", "labels")
    _split_values(df, "labels")
    key = ["patient_id", "recording_id", "window_start", "window_end"]
    duplicates = int(df.duplicated(key).sum())
    if duplicates:
        raise ValueError(f"labels contains duplicate patient/recording/window rows: {duplicates}")
    valid = ~df["is_excluded"].fillna(False).astype(bool)
    if not valid.any():
        raise ValueError("labels contains no valid non-excluded windows")
    positives = int(df.loc[valid, "forecast_label"].fillna(False).astype(bool).sum())
    if positives == 0:
        raise ValueError("labels contains no positive valid forecast windows")


def _split_key(df: pd.DataFrame) -> tuple[str, ...]:
    for key in SPLIT_KEY_CANDIDATES:
        if set(key).issubset(df.columns):
            return key
    raise ValueError(
        "splits must contain split plus an alignment key: patient_id, recording_id, "
        "patient_id+recording_id, or patient_id+recording_id+window_start+window_end"
    )


def _validate_split_candidate(df: pd.DataFrame) -> None:
    validate_table_schema(df, SPLITS_SCHEMA, allow_empty=False)
    _split_values(df, "splits")
    key = _split_key(df)
    validate_no_null_ids(df, key, "splits")
    if "window_start" in key and "window_end" in key:
        validate_time_order(df, "window_start", "window_end", "splits")
    duplicates = int(df.duplicated(list(key)).sum())
    if duplicates:
        raise ValueError(f"splits contains duplicate alignment keys {list(key)}: {duplicates}")


def _role_error(df: pd.DataFrame, role: str) -> str | None:
    try:
        if role == "events":
            validate_events(df, allow_empty=False)
        elif role == "labels":
            _validate_label_candidate(df)
        elif role == "splits":
            _validate_split_candidate(df)
        else:
            raise ValueError(f"unknown role {role}")
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
        for role in DISCOVERY_ROLES:
            row[f"{role}_ready"] = False
            row[f"{role}_reason"] = "table could not be read"
        row["candidate_roles"] = ""
        return row

    row["row_count"] = int(len(table))
    row["column_count"] = int(len(table.columns))
    row["columns"] = ",".join(str(column) for column in table.columns)
    roles = []
    for role in DISCOVERY_ROLES:
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
        for role in DISCOVERY_ROLES
    }
    role_files = {
        role: candidates.loc[candidates[f"{role}_ready"].fillna(False), "path"].tolist()
        if f"{role}_ready" in candidates.columns
        else []
        for role in DISCOVERY_ROLES
    }
    missing_roles = [role for role, count in role_counts.items() if count == 0]
    return {
        "scan_status": "gate_c_inputs_available"
        if not missing_roles
        else "blocked_missing_gate_c_inputs",
        "roots": [str(root) for root in roots],
        "files_scanned": int(len(candidates)),
        "readable_tables": int(candidates["read_status"].eq("ok").sum()) if len(candidates) else 0,
        "role_ready_counts": role_counts,
        "candidate_files_by_role": role_files,
        "missing_roles": missing_roles,
    }


def _markdown(summary: dict[str, Any], candidates: pd.DataFrame) -> str:
    role_lines = "\n".join(
        f"- {role}: {summary['role_ready_counts'][role]}" for role in DISCOVERY_ROLES
    )
    missing = summary["missing_roles"] or ["none"]
    table = candidates.loc[
        candidates["candidate_roles"].fillna("").ne(""),
        ["path", "candidate_roles", "row_count"],
    ]
    if table.empty:
        candidate_table = "_No Gate C role-ready candidate files found._"
    else:
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
        candidate_table = "\n".join(rows)
    return f"""# Gate C Input Discovery

**Status:** `{summary["scan_status"]}`

This report scans local table artifacts for files that satisfy the minimum
Gate C role contracts. It does not freeze artifacts and it does not make any
benchmark row citable.

## Summary

- Files scanned: `{summary["files_scanned"]}`
- Readable tables: `{summary["readable_tables"]}`
- Missing roles: `{", ".join(missing)}`

## Role-Ready Counts

{role_lines}

## Candidate Files

{candidate_table}

## Next Action

If any required role is missing, materialize the real frozen `events`, `labels`,
and `splits` artifacts before running `scripts/build_gate_c_freeze_package.py`.
"""


def discover_gate_c_inputs(
    roots: tuple[str | Path, ...],
    *,
    max_bytes: int = 128 * 1024 * 1024,
) -> GateCInputDiscovery:
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
                "events_ready",
                "events_reason",
                "labels_ready",
                "labels_reason",
                "splits_ready",
                "splits_reason",
                "candidate_roles",
            ]
        )
    summary = _summary(candidates, roots)
    return GateCInputDiscovery(
        summary=summary,
        candidates=candidates,
        markdown=_markdown(summary, candidates),
    )


def write_gate_c_input_discovery(discovery: GateCInputDiscovery, out_dir: str | Path) -> dict[str, str]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "summary": str(out_dir / "gate_c_input_discovery.json"),
        "candidates": str(out_dir / "gate_c_input_candidates.csv"),
        "markdown": str(out_dir / "gate_c_input_discovery.md"),
    }
    Path(paths["summary"]).write_text(json.dumps(discovery.summary, indent=2), encoding="utf-8")
    write_table(discovery.candidates, paths["candidates"])
    Path(paths["markdown"]).write_text(discovery.markdown, encoding="utf-8")
    return paths
