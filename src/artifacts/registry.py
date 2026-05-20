from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pandas as pd

from src.utils.io import read_table

REGISTRY_SCHEMA_VERSION = "gate_c.registry.v1"
ARTIFACT_ROLES = {
    "raw",
    "processed",
    "events",
    "windows",
    "labels",
    "features",
    "splits",
    "predictions",
    "metadata",
}
GATE_C_STATUSES = {"not_started", "partial", "passed", "failed"}
FREEZE_STATUSES = {"engineering_scaffold", "pending_human_audit", "frozen", "failed"}


def sha256_file(path: str | Path) -> str:
    path = Path(path)
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _artifact_path(path: str | Path, root: str | Path | None = None) -> Path:
    path = Path(path)
    if path.is_absolute() or root is None:
        return path
    return Path(root) / path


def _table_stats(path: Path, role: str, split_col: str) -> dict[str, Any]:
    stats: dict[str, Any] = {}
    if path.suffix not in {".csv", ".tsv", ".parquet"}:
        return stats
    table = read_table(path)
    stats["row_count"] = int(len(table))
    if role == "events":
        stats["event_count"] = int(len(table))
    elif role == "labels" and "forecast_label" in table.columns:
        valid = ~table.get("is_excluded", pd.Series(False, index=table.index)).fillna(False).astype(bool)
        stats["positive_windows"] = int(table.loc[valid, "forecast_label"].fillna(False).astype(bool).sum())
    if split_col in table.columns:
        stats["split_counts"] = {
            str(key): int(value)
            for key, value in table[split_col].astype(str).value_counts().sort_index().items()
        }
    return stats


def build_artifact_record(
    *,
    name: str,
    path: str | Path,
    role: str,
    root: str | Path | None = None,
    split_col: str = "split",
) -> dict[str, Any]:
    if role not in ARTIFACT_ROLES:
        raise ValueError(f"unknown artifact role {role!r}; expected one of {sorted(ARTIFACT_ROLES)}")
    full_path = _artifact_path(path, root)
    if not full_path.exists():
        raise FileNotFoundError(f"artifact not found: {full_path}")
    record: dict[str, Any] = {
        "name": name,
        "role": role,
        "path": str(path),
        "sha256": sha256_file(full_path),
        "bytes": int(full_path.stat().st_size),
    }
    record.update(_table_stats(full_path, role, split_col))
    return record


def build_gate_c_registry(
    *,
    registry_id: str,
    dataset: str,
    dataset_version: str,
    source_uri: str,
    generation_command: str,
    artifacts: list[dict[str, Any]],
    split_manifest: dict[str, Any],
    gate_c_status: str = "not_started",
    freeze_status: str = "engineering_scaffold",
    doi_or_prereg_uri: str | None = None,
    notes: str | None = None,
) -> dict[str, Any]:
    if gate_c_status not in GATE_C_STATUSES:
        raise ValueError(f"gate_c_status must be one of {sorted(GATE_C_STATUSES)}")
    if freeze_status not in FREEZE_STATUSES:
        raise ValueError(f"freeze_status must be one of {sorted(FREEZE_STATUSES)}")
    if gate_c_status == "passed" and freeze_status != "frozen":
        raise ValueError("gate_c_status='passed' requires freeze_status='frozen'")
    if not artifacts:
        raise ValueError("registry requires at least one artifact")
    required_manifest = {"split_policy", "split_ids", "split_ref"}
    missing_manifest = sorted(required_manifest - set(split_manifest))
    if missing_manifest:
        raise ValueError(f"split_manifest missing required keys: {missing_manifest}")
    if not split_manifest["split_ids"]:
        raise ValueError("split_manifest.split_ids must not be empty")
    return {
        "schema_version": REGISTRY_SCHEMA_VERSION,
        "registry_id": registry_id,
        "dataset": dataset,
        "dataset_version": dataset_version,
        "source_uri": source_uri,
        "gate_c_status": gate_c_status,
        "freeze_status": freeze_status,
        "doi_or_prereg_uri": doi_or_prereg_uri,
        "generation_command": generation_command,
        "split_manifest": split_manifest,
        "artifacts": artifacts,
        "notes": notes,
    }


def load_registry(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _verify_artifact(record: dict[str, Any], root: Path, split_col: str) -> list[str]:
    errors: list[str] = []
    missing = [key for key in ("name", "role", "path", "sha256", "bytes") if key not in record]
    if missing:
        return [f"artifact record missing keys {missing}: {record}"]
    path = _artifact_path(record["path"], root)
    if not path.exists():
        return [f"artifact {record['name']} missing file: {path}"]
    actual_sha = sha256_file(path)
    if actual_sha != record["sha256"]:
        errors.append(f"artifact {record['name']} sha256 mismatch")
    actual_bytes = int(path.stat().st_size)
    if actual_bytes != int(record["bytes"]):
        errors.append(f"artifact {record['name']} byte size mismatch")
    actual_stats = _table_stats(path, str(record["role"]), split_col)
    for key in ("row_count", "event_count", "positive_windows", "split_counts"):
        if key in record and actual_stats.get(key) != record[key]:
            errors.append(f"artifact {record['name']} {key} mismatch")
    return errors


def verify_gate_c_registry(
    registry: dict[str, Any],
    *,
    root: str | Path | None = None,
    require_frozen: bool = False,
    split_col: str = "split",
) -> dict[str, Any]:
    errors: list[str] = []
    root_path = Path("." if root is None else root)
    if registry.get("schema_version") != REGISTRY_SCHEMA_VERSION:
        errors.append(
            f"schema_version mismatch: expected {REGISTRY_SCHEMA_VERSION}, got {registry.get('schema_version')}"
        )
    artifacts = registry.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        errors.append("registry.artifacts must be a non-empty list")
        artifacts = []
    split_manifest = registry.get("split_manifest")
    if not isinstance(split_manifest, dict):
        errors.append("registry.split_manifest must be an object")
    elif not split_manifest.get("split_ids"):
        errors.append("registry.split_manifest.split_ids must be non-empty")
    if require_frozen:
        if registry.get("gate_c_status") != "passed":
            errors.append("frozen/citable outputs require registry.gate_c_status='passed'")
        if registry.get("freeze_status") != "frozen":
            errors.append("frozen/citable outputs require registry.freeze_status='frozen'")
    for record in artifacts:
        errors.extend(_verify_artifact(record, root_path, split_col))
    return {
        "ok": not errors,
        "errors": errors,
        "registry_id": registry.get("registry_id"),
        "dataset": registry.get("dataset"),
        "gate_c_status": registry.get("gate_c_status"),
        "freeze_status": registry.get("freeze_status"),
        "artifact_count": len(artifacts),
    }


def registry_is_frozen_and_clean(registry: dict[str, Any], *, root: str | Path | None = None) -> bool:
    return bool(verify_gate_c_registry(registry, root=root, require_frozen=True)["ok"])
