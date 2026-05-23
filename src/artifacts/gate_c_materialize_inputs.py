from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from src.artifacts.gate_c_freeze_package import validate_gate_c_freeze_inputs
from src.datasets.schemas import validate_events, validate_recordings
from src.labeling.sph_sop import label_forecast_windows
from src.preprocessing.windowing import generate_fixed_windows
from src.splits.leakage_checks import leakage_audit
from src.splits.patient_split import patient_wise_split
from src.splits.recording_split import recording_wise_split
from src.splits.temporal_split import temporal_split_per_patient
from src.utils.io import read_table, write_table

SPLIT_COLUMNS = ("patient_id", "recording_id", "window_start", "window_end", "split")


@dataclass(frozen=True)
class GateCMaterializationConfig:
    window_duration: str = "2min"
    stride: str = "30s"
    sph_minutes: float = 5.0
    sop_minutes: float = 30.0
    postictal_exclusion_minutes: float = 60.0
    postictal_anchor: str = "seizure_end"
    include_ictal: bool = False
    strategy: str = "temporal"
    train_fraction: float = 0.7
    val_fraction: float = 0.1
    test_fraction: float = 0.2
    seed: int = 42
    purge_overlap: bool = True
    temporal_unit: str = "window"
    temporal_basis: str = "elapsed_time"
    allow_duplicate_recording_time_ranges: bool = False


@dataclass(frozen=True)
class GateCMaterialization:
    events: pd.DataFrame
    labels: pd.DataFrame
    splits: pd.DataFrame
    leakage_audit_text: str
    manifest: dict[str, Any]
    output_paths: dict[str, str]


def _split_labels(labels: pd.DataFrame, cfg: GateCMaterializationConfig) -> pd.DataFrame:
    if cfg.strategy == "temporal":
        return temporal_split_per_patient(
            labels,
            train_fraction=cfg.train_fraction,
            val_fraction=cfg.val_fraction,
            purge_overlap=cfg.purge_overlap,
            split_unit=cfg.temporal_unit,
            split_basis=cfg.temporal_basis,
            allow_duplicate_recording_time_ranges=cfg.allow_duplicate_recording_time_ranges,
        )
    if cfg.strategy == "patient_wise":
        return patient_wise_split(
            labels,
            test_fraction=cfg.test_fraction,
            val_fraction=cfg.val_fraction,
            seed=cfg.seed,
        )
    if cfg.strategy == "recording_wise":
        return recording_wise_split(
            labels,
            test_fraction=cfg.test_fraction,
            val_fraction=cfg.val_fraction,
            seed=cfg.seed,
        )
    raise ValueError("strategy must be one of temporal, patient_wise, recording_wise")


def _split_strategy_name(cfg: GateCMaterializationConfig) -> str:
    if cfg.strategy == "temporal":
        return f"temporal_{cfg.temporal_unit}_{cfg.temporal_basis}"
    return cfg.strategy


def _normalize_recording_times(recordings: pd.DataFrame) -> pd.DataFrame:
    out = recordings.copy()
    start_numeric = pd.api.types.is_numeric_dtype(out["recording_start"])
    end_numeric = pd.api.types.is_numeric_dtype(out["recording_end"])
    if start_numeric and end_numeric:
        return out
    out["recording_start"] = pd.to_datetime(out["recording_start"], errors="raise")
    out["recording_end"] = pd.to_datetime(out["recording_end"], errors="raise")
    return out


def _manifest(
    *,
    recordings_path: str | Path,
    events_path: str | Path,
    events: pd.DataFrame,
    labels: pd.DataFrame,
    splits: pd.DataFrame,
    cfg: GateCMaterializationConfig,
    output_paths: dict[str, str],
) -> dict[str, Any]:
    valid_labels = ~labels["is_excluded"].fillna(False).astype(bool)
    split_counts = {
        str(split): int(count)
        for split, count in labels["split"].astype(str).value_counts().sort_index().items()
    }
    split_ids = sorted(split_counts)
    return {
        "materialization_status": "gate_c_inputs_materialized",
        "claim_status": "not_citable_until_gate_c_freeze_package",
        "recordings_path": str(recordings_path),
        "source_events_path": str(events_path),
        "events_rows": int(len(events)),
        "labels_rows": int(len(labels)),
        "splits_rows": int(len(splits)),
        "valid_label_rows": int(valid_labels.sum()),
        "positive_valid_windows": int(labels.loc[valid_labels, "forecast_label"].astype(bool).sum()),
        "split_ids": split_ids,
        "split_counts": split_counts,
        "window_duration": cfg.window_duration,
        "stride": cfg.stride,
        "horizon_name": f"SPH{cfg.sph_minutes:g}_SOP{cfg.sop_minutes:g}",
        "sph_minutes": float(cfg.sph_minutes),
        "sop_minutes": float(cfg.sop_minutes),
        "postictal_exclusion_minutes": float(cfg.postictal_exclusion_minutes),
        "postictal_anchor": cfg.postictal_anchor,
        "include_ictal": cfg.include_ictal,
        "split_strategy": _split_strategy_name(cfg),
        "output_paths": output_paths,
        "next_command": (
            "python scripts/build_gate_c_freeze_package.py "
            f"--events {output_paths['events']} "
            f"--labels {output_paths['labels']} "
            f"--splits {output_paths['splits']} "
            "--out-dir <gate-c-freeze-out> "
            "--registry-id <registry-id> "
            "--dataset <dataset> "
            "--dataset-version <version> "
            "--source-uri <source-uri> "
            "--generation-command <exact-command> "
            f"--split-policy {_split_strategy_name(cfg)} "
            f"--split-ref {output_paths['manifest']} "
            + " ".join(f"--split-id {split_id}" for split_id in split_ids)
            + f" --horizon-name SPH{cfg.sph_minutes:g}_SOP{cfg.sop_minutes:g} "
            f"--sph-minutes {cfg.sph_minutes:g} "
            f"--sop-minutes {cfg.sop_minutes:g} "
            "--doi-or-prereg-uri <doi-or-prereg-uri>"
        ),
    }


def materialize_gate_c_inputs(
    *,
    recordings_path: str | Path,
    events_path: str | Path,
    cfg: GateCMaterializationConfig,
) -> GateCMaterialization:
    recordings = read_table(recordings_path)
    events = read_table(events_path).copy()
    recordings = _normalize_recording_times(recordings)
    validate_recordings(recordings, allow_empty=False)
    validate_events(events, allow_empty=False)

    windows = generate_fixed_windows(
        recordings,
        window_duration=cfg.window_duration,
        stride=cfg.stride,
    )
    if windows.empty:
        raise ValueError("window generation produced no rows")
    labels = label_forecast_windows(
        windows,
        events,
        sph_minutes=cfg.sph_minutes,
        sop_minutes=cfg.sop_minutes,
        postictal_exclusion_minutes=cfg.postictal_exclusion_minutes,
        ictal_exclusion=not cfg.include_ictal,
        require_recording_end=True,
        postictal_anchor=cfg.postictal_anchor,
    )
    labels = _split_labels(labels, cfg)
    splits = labels.loc[:, SPLIT_COLUMNS].copy()
    split_ids = tuple(sorted(labels["split"].astype(str).unique()))
    validate_gate_c_freeze_inputs(
        events=events,
        labels=labels,
        splits=splits,
        expected_split_ids=split_ids,
    )
    audit = leakage_audit(labels, split_strategy=_split_strategy_name(cfg))
    return GateCMaterialization(
        events=events,
        labels=labels,
        splits=splits,
        leakage_audit_text=audit,
        manifest={},
        output_paths={},
    )


def write_gate_c_materialization(
    materialization: GateCMaterialization,
    *,
    out_dir: str | Path,
    recordings_path: str | Path,
    events_path: str | Path,
    cfg: GateCMaterializationConfig,
    suffix: str = ".csv",
) -> GateCMaterialization:
    if suffix not in {".csv", ".tsv", ".parquet"}:
        raise ValueError("suffix must be one of .csv, .tsv, .parquet")
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "events": str(out_dir / f"events{suffix}"),
        "labels": str(out_dir / f"labels{suffix}"),
        "splits": str(out_dir / f"splits{suffix}"),
        "leakage_audit": str(out_dir / "leakage_audit.txt"),
        "manifest": str(out_dir / "gate_c_input_materialization_manifest.json"),
    }
    write_table(materialization.events, paths["events"])
    write_table(materialization.labels, paths["labels"])
    write_table(materialization.splits, paths["splits"])
    Path(paths["leakage_audit"]).write_text(materialization.leakage_audit_text, encoding="utf-8")
    manifest = _manifest(
        recordings_path=recordings_path,
        events_path=events_path,
        events=materialization.events,
        labels=materialization.labels,
        splits=materialization.splits,
        cfg=cfg,
        output_paths=paths,
    )
    Path(paths["manifest"]).write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return GateCMaterialization(
        events=materialization.events,
        labels=materialization.labels,
        splits=materialization.splits,
        leakage_audit_text=materialization.leakage_audit_text,
        manifest=manifest,
        output_paths=paths,
    )
