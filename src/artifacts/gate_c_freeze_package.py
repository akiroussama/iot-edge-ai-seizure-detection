from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from src.artifacts.registry import build_artifact_record, build_gate_c_registry
from src.datasets.schemas import validate_events
from src.reports.gate_c_dry_run import build_gate_c_dry_run_report
from src.utils.io import read_table, write_table
from src.utils.validation import (
    ColumnSpec,
    TableSchema,
    validate_no_null_ids,
    validate_table_schema,
    validate_time_order,
)

REQUIRED_GATE_C_FREEZE_ROLES = ("events", "labels", "splits")

LABELS_SCHEMA = TableSchema(
    name="labels",
    columns=(
        ColumnSpec("patient_id", "string"),
        ColumnSpec("recording_id", "string"),
        ColumnSpec("window_start", "datetime"),
        ColumnSpec("window_end", "datetime"),
        ColumnSpec("split", "string"),
        ColumnSpec("forecast_label", "boolean"),
        ColumnSpec("is_excluded", "boolean"),
    ),
)

SPLITS_SCHEMA = TableSchema(
    name="splits",
    columns=(
        ColumnSpec("split", "string"),
        ColumnSpec("patient_id", "string", required=False, nullable=True),
        ColumnSpec("recording_id", "string", required=False, nullable=True),
        ColumnSpec("window_start", "datetime", required=False, nullable=True),
        ColumnSpec("window_end", "datetime", required=False, nullable=True),
    ),
)

SPLIT_ALIGNMENT_KEY_CANDIDATES = (
    ("patient_id", "recording_id", "window_start", "window_end"),
    ("patient_id", "recording_id"),
    ("patient_id",),
)


@dataclass(frozen=True)
class GateCFreezePackage:
    registry: dict[str, Any]
    dry_run_diagnostics: dict[str, Any]
    dry_run_markdown: str
    artifact_summary: pd.DataFrame
    manifest: dict[str, Any]
    output_paths: dict[str, str]


def _split_values(df: pd.DataFrame, *, table_name: str) -> set[str]:
    values = df["split"].astype(str).str.strip()
    if values.eq("").any():
        raise ValueError(f"{table_name}.split contains empty split identifiers")
    return set(values)


def _validate_expected_splits(
    df: pd.DataFrame,
    *,
    table_name: str,
    expected_split_ids: tuple[str, ...],
) -> None:
    expected = set(expected_split_ids)
    present = _split_values(df, table_name=table_name)
    missing = sorted(expected - present)
    unexpected = sorted(present - expected)
    if missing:
        raise ValueError(f"{table_name} missing expected split ids: {missing}")
    if unexpected:
        raise ValueError(f"{table_name} contains unexpected split ids: {unexpected}")


def _validate_labels(labels: pd.DataFrame, *, expected_split_ids: tuple[str, ...]) -> None:
    validate_table_schema(labels, LABELS_SCHEMA, allow_empty=False)
    validate_no_null_ids(labels, ("patient_id", "recording_id"), "labels")
    validate_time_order(labels, "window_start", "window_end", "labels")
    _validate_expected_splits(
        labels,
        table_name="labels",
        expected_split_ids=expected_split_ids,
    )
    key = ["patient_id", "recording_id", "window_start", "window_end"]
    duplicate_rows = int(labels.duplicated(key).sum())
    if duplicate_rows:
        raise ValueError(f"labels contains duplicate patient/recording/window rows: {duplicate_rows}")
    valid = ~labels["is_excluded"].fillna(False).astype(bool)
    if not valid.any():
        raise ValueError("labels contains no valid non-excluded windows")
    positives = int(labels.loc[valid, "forecast_label"].fillna(False).astype(bool).sum())
    if positives == 0:
        raise ValueError("labels contains no positive valid forecast windows")


def _select_split_alignment_key(labels: pd.DataFrame, splits: pd.DataFrame) -> tuple[str, ...]:
    for key in SPLIT_ALIGNMENT_KEY_CANDIDATES:
        if set(key).issubset(labels.columns) and set(key).issubset(splits.columns):
            return key
    raise ValueError(
        "splits must share an alignment key with labels: "
        "patient_id, patient_id+recording_id, or patient_id+recording_id+window_start+window_end"
    )


def _validate_splits(
    labels: pd.DataFrame,
    splits: pd.DataFrame,
    *,
    expected_split_ids: tuple[str, ...],
) -> None:
    validate_table_schema(splits, SPLITS_SCHEMA, allow_empty=False)
    _validate_expected_splits(
        splits,
        table_name="splits",
        expected_split_ids=expected_split_ids,
    )
    key = _select_split_alignment_key(labels, splits)
    validate_no_null_ids(splits, key, "splits")
    if "window_start" in key and "window_end" in key:
        validate_time_order(splits, "window_start", "window_end", "splits")
    duplicate_rows = int(splits.duplicated(list(key)).sum())
    if duplicate_rows:
        raise ValueError(f"splits contains duplicate alignment keys {list(key)}: {duplicate_rows}")

    split_lookup = splits.set_index(list(key))["split"].astype(str)
    label_lookup = labels.set_index(list(key))["split"].astype(str)
    missing_keys = label_lookup.index.difference(split_lookup.index)
    if len(missing_keys):
        raise ValueError(f"splits missing alignment rows for labels: {len(missing_keys)}")
    aligned_splits = split_lookup.loc[label_lookup.index]
    mismatches = int((aligned_splits.to_numpy() != label_lookup.to_numpy()).sum())
    if mismatches:
        raise ValueError(f"splits disagrees with labels split assignments: {mismatches} rows")


def validate_gate_c_freeze_inputs(
    *,
    events: pd.DataFrame,
    labels: pd.DataFrame,
    splits: pd.DataFrame,
    expected_split_ids: tuple[str, ...],
) -> None:
    validate_events(events, allow_empty=False)
    _validate_labels(labels, expected_split_ids=expected_split_ids)
    _validate_splits(labels, splits, expected_split_ids=expected_split_ids)


def _artifact_records(
    *,
    events_path: str | Path,
    labels_path: str | Path,
    splits_path: str | Path,
    metadata_artifacts: tuple[tuple[str, str | Path], ...],
    root: str | Path,
    split_col: str,
) -> list[dict[str, Any]]:
    records = [
        build_artifact_record(
            name="events",
            role="events",
            path=events_path,
            root=root,
            split_col=split_col,
        ),
        build_artifact_record(
            name="labels",
            role="labels",
            path=labels_path,
            root=root,
            split_col=split_col,
        ),
        build_artifact_record(
            name="splits",
            role="splits",
            path=splits_path,
            root=root,
            split_col=split_col,
        ),
    ]
    for name, path in metadata_artifacts:
        records.append(
            build_artifact_record(
                name=name,
                role="metadata",
                path=path,
                root=root,
                split_col=split_col,
            )
        )
    return records


def _manifest(registry: dict[str, Any], diagnostics: dict[str, Any]) -> dict[str, Any]:
    return {
        "freeze_package_status": "gate_c_frozen_citable",
        "registry_id": registry["registry_id"],
        "dataset": registry["dataset"],
        "dataset_version": registry["dataset_version"],
        "gate_c_status": registry["gate_c_status"],
        "freeze_status": registry["freeze_status"],
        "doi_or_prereg_uri": registry["doi_or_prereg_uri"],
        "citable_ready": bool(diagnostics["citable_ready"]),
        "readiness_status": diagnostics["readiness_status"],
        "required_roles": diagnostics["required_roles"],
        "present_roles": diagnostics["present_roles"],
        "blockers": diagnostics["blockers"],
        "warnings": diagnostics["warnings"],
    }


def build_gate_c_freeze_package(
    *,
    events_path: str | Path,
    labels_path: str | Path,
    splits_path: str | Path,
    registry_id: str,
    dataset: str,
    dataset_version: str,
    source_uri: str,
    generation_command: str,
    split_policy: str,
    split_ref: str,
    split_ids: tuple[str, ...],
    horizon_name: str,
    sph_minutes: float,
    sop_minutes: float,
    doi_or_prereg_uri: str,
    gate_b_status: str = "passed",
    notes: str | None = None,
    metadata_artifacts: tuple[tuple[str, str | Path], ...] = (),
    root: str | Path = ".",
    split_col: str = "split",
) -> GateCFreezePackage:
    if not doi_or_prereg_uri:
        raise ValueError("doi_or_prereg_uri is required for a Gate C freeze package")
    if not split_ids:
        raise ValueError("split_ids must not be empty")

    events = read_table(Path(root) / events_path if not Path(events_path).is_absolute() else events_path)
    labels = read_table(Path(root) / labels_path if not Path(labels_path).is_absolute() else labels_path)
    splits = read_table(Path(root) / splits_path if not Path(splits_path).is_absolute() else splits_path)
    validate_gate_c_freeze_inputs(
        events=events,
        labels=labels,
        splits=splits,
        expected_split_ids=tuple(str(split_id) for split_id in split_ids),
    )

    registry = build_gate_c_registry(
        registry_id=registry_id,
        dataset=dataset,
        dataset_version=dataset_version,
        source_uri=source_uri,
        generation_command=generation_command,
        artifacts=_artifact_records(
            events_path=events_path,
            labels_path=labels_path,
            splits_path=splits_path,
            metadata_artifacts=metadata_artifacts,
            root=root,
            split_col=split_col,
        ),
        split_manifest={
            "split_policy": split_policy,
            "split_ids": list(split_ids),
            "split_ref": split_ref,
            "horizon_name": horizon_name,
            "sph_minutes": float(sph_minutes),
            "sop_minutes": float(sop_minutes),
        },
        gate_c_status="passed",
        freeze_status="frozen",
        doi_or_prereg_uri=doi_or_prereg_uri,
        notes=notes,
    )
    dry_run = build_gate_c_dry_run_report(
        registry,
        root=root,
        gate_b_status=gate_b_status,
        required_roles=REQUIRED_GATE_C_FREEZE_ROLES,
        require_prereg=True,
        split_col=split_col,
    )
    if dry_run.diagnostics["blockers"]:
        raise ValueError("Gate C freeze package blocked: " + "; ".join(dry_run.diagnostics["blockers"]))

    return GateCFreezePackage(
        registry=registry,
        dry_run_diagnostics=dry_run.diagnostics,
        dry_run_markdown=dry_run.markdown,
        artifact_summary=dry_run.artifact_summary,
        manifest=_manifest(registry, dry_run.diagnostics),
        output_paths={},
    )


def write_gate_c_freeze_package(package: GateCFreezePackage, out_dir: str | Path) -> GateCFreezePackage:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "registry": str(out_dir / "gate_c_registry.json"),
        "dry_run_json": str(out_dir / "gate_c_dry_run.json"),
        "dry_run_md": str(out_dir / "gate_c_dry_run.md"),
        "artifact_summary": str(out_dir / "gate_c_artifact_summary.csv"),
        "manifest": str(out_dir / "gate_c_freeze_manifest.json"),
    }
    Path(paths["registry"]).write_text(json.dumps(package.registry, indent=2), encoding="utf-8")
    Path(paths["dry_run_json"]).write_text(
        json.dumps(package.dry_run_diagnostics, indent=2),
        encoding="utf-8",
    )
    Path(paths["dry_run_md"]).write_text(package.dry_run_markdown, encoding="utf-8")
    write_table(package.artifact_summary, paths["artifact_summary"])
    manifest = {**package.manifest, "output_paths": paths}
    Path(paths["manifest"]).write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return GateCFreezePackage(
        registry=package.registry,
        dry_run_diagnostics=package.dry_run_diagnostics,
        dry_run_markdown=package.dry_run_markdown,
        artifact_summary=package.artifact_summary,
        manifest=manifest,
        output_paths=paths,
    )
