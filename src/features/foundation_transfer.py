from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from hashlib import sha256
from typing import Any

import numpy as np
import pandas as pd

from src.utils.time import ensure_datetime

FOUNDATION_FORBIDDEN_COLUMNS = {
    "forecast_label",
    "is_ictal",
    "is_postictal",
    "is_excluded",
    "is_right_censored",
    "right_censoring_applied",
    "alarm",
    "risk_score",
    "time_to_next_seizure_seconds",
    "time_since_last_seizure_seconds",
    "split",
}


@dataclass(frozen=True)
class FoundationTransferConfig:
    model_name: str
    source_name: str
    source_url: str | None
    source_doi: str | None
    license_name: str
    license_allows_research_use: bool
    modality: str
    join_keys: tuple[str, ...] = ("patient_id", "recording_id", "window_start", "window_end")
    embedding_prefix: str = "embedding_"
    embedding_cols: tuple[str, ...] = ()
    output_prefix: str = "fm"
    require_complete_coverage: bool = True
    gate_c_status: str = "not_started"
    citation_status: str = "not_citable_pre_gate_c"


@dataclass(frozen=True)
class FoundationTransferResult:
    features: pd.DataFrame
    manifest: pd.DataFrame
    metadata: dict[str, Any]


def _require_nonempty(value: str | None, name: str) -> str:
    if value is None or not str(value).strip():
        raise ValueError(f"{name} must be provided")
    return str(value).strip()


def validate_foundation_transfer_config(config: FoundationTransferConfig) -> None:
    _require_nonempty(config.model_name, "model_name")
    _require_nonempty(config.source_name, "source_name")
    _require_nonempty(config.license_name, "license_name")
    _require_nonempty(config.modality, "modality")
    if not config.source_url and not config.source_doi:
        raise ValueError("at least one of source_url or source_doi must be provided")
    if not config.license_allows_research_use:
        raise ValueError("foundation embedding license must allow this research use")
    if not config.join_keys:
        raise ValueError("join_keys must not be empty")
    if config.gate_c_status not in {"not_started", "partial", "passed", "failed"}:
        raise ValueError("gate_c_status must be one of not_started, partial, passed, failed")
    if config.citation_status == "citable_after_gate_c" and config.gate_c_status != "passed":
        raise ValueError("citable foundation-transfer outputs require gate_c_status='passed'")


def _require_columns(df: pd.DataFrame, required: set[str], name: str) -> None:
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"{name} missing required columns: {missing}")


def _normalize_time_keys(df: pd.DataFrame, keys: tuple[str, ...]) -> pd.DataFrame:
    out = df.copy()
    for key in keys:
        if key in {"window_start", "window_end"}:
            out[key] = ensure_datetime(out[key])
    return out


def _safe_name(value: str) -> str:
    cleaned = re.sub(r"[^0-9A-Za-z_]+", "_", value.strip())
    return cleaned.strip("_").lower() or "embedding"


def select_foundation_embedding_columns(
    embeddings: pd.DataFrame,
    *,
    config: FoundationTransferConfig,
) -> list[str]:
    if config.embedding_cols:
        missing = [column for column in config.embedding_cols if column not in embeddings.columns]
        if missing:
            raise ValueError(f"requested embedding columns are missing: {missing}")
        selected = list(config.embedding_cols)
    else:
        selected = [
            column
            for column in embeddings.columns
            if column.startswith(config.embedding_prefix)
            and pd.api.types.is_numeric_dtype(embeddings[column])
        ]
    if not selected:
        raise ValueError("no numeric foundation embedding columns selected")
    forbidden = sorted(FOUNDATION_FORBIDDEN_COLUMNS & (set(embeddings.columns) - set(config.join_keys)))
    if forbidden:
        raise ValueError(f"foundation embedding table contains forbidden leakage columns: {forbidden}")
    return selected


def _dataframe_hash(df: pd.DataFrame) -> str:
    normalized = df.copy()
    for column in normalized.columns:
        if pd.api.types.is_datetime64_any_dtype(normalized[column]):
            normalized[column] = normalized[column].astype(str)
    return sha256(normalized.to_csv(index=False).encode("utf-8")).hexdigest()


def _stable_hash(payload: Any) -> str:
    data = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return sha256(data).hexdigest()


def build_foundation_transfer_features(
    features: pd.DataFrame,
    embeddings: pd.DataFrame,
    *,
    config: FoundationTransferConfig,
) -> FoundationTransferResult:
    """Attach frozen foundation-model embeddings to leakage-screened window features."""
    validate_foundation_transfer_config(config)
    _require_columns(features, set(config.join_keys), "features")
    _require_columns(embeddings, set(config.join_keys), "embeddings")
    embedding_cols = select_foundation_embedding_columns(embeddings, config=config)
    feature_keys = _normalize_time_keys(features, config.join_keys)
    embedding_keys = _normalize_time_keys(embeddings, config.join_keys)
    if embedding_keys.duplicated(list(config.join_keys)).any():
        raise ValueError("embeddings contain duplicate join keys")

    rename_map = {
        column: f"{config.output_prefix}_{_safe_name(config.model_name)}_{_safe_name(column)}"
        for column in embedding_cols
    }
    right = embedding_keys[list(config.join_keys) + embedding_cols].rename(columns=rename_map)
    out = feature_keys.merge(right, on=list(config.join_keys), how="left", indicator=True)
    matched = out["_merge"].eq("both")
    if config.require_complete_coverage and not matched.all():
        missing = int((~matched).sum())
        raise ValueError(f"foundation embeddings missing for {missing} feature rows")
    output_embedding_cols = list(rename_map.values())
    out["foundation_transfer_status"] = np.where(matched, "embedding_attached", "missing_embedding")
    out["foundation_model_name"] = config.model_name
    out["foundation_model_source"] = config.source_name
    out["foundation_model_license"] = config.license_name
    out["foundation_model_modality"] = config.modality
    out = out.drop(columns=["_merge"])

    embedding_hash = _dataframe_hash(right)
    provenance_hash = _stable_hash(
        {
            "config": asdict(config),
            "embedding_columns": output_embedding_cols,
            "embedding_hash": embedding_hash,
        }
    )
    metadata = {
        "model_name": config.model_name,
        "source_name": config.source_name,
        "source_url": config.source_url,
        "source_doi": config.source_doi,
        "license_name": config.license_name,
        "license_allows_research_use": config.license_allows_research_use,
        "modality": config.modality,
        "feature_rows": int(len(features)),
        "matched_rows": int(matched.sum()),
        "missing_embedding_rows": int((~matched).sum()),
        "embedding_columns": ",".join(output_embedding_cols),
        "embedding_column_count": int(len(output_embedding_cols)),
        "embedding_hash": embedding_hash,
        "foundation_transfer_hash": provenance_hash,
        "gate_c_status": config.gate_c_status,
        "citation_status": config.citation_status,
        "analysis_status": "frozen_foundation_embedding_transfer_baseline",
        "result_status": "pre_gate_c_transfer_baseline_not_citable"
        if config.gate_c_status != "passed"
        else "gate_c_transfer_baseline",
    }
    manifest = pd.DataFrame([metadata])
    return FoundationTransferResult(features=out, manifest=manifest, metadata=metadata)


def foundation_transfer_markdown(
    result: FoundationTransferResult,
    *,
    title: str = "Foundation-Model Transfer Baseline",
) -> str:
    meta = result.metadata
    warning = ""
    if meta["citation_status"] != "citable_after_gate_c":
        warning = "\n**Citation status:** not citable as a benchmark result before Gate C.\n"
    return "\n".join(
        [
            f"# {title}",
            warning,
            "This report documents frozen embedding transfer, not foundation-model training.",
            "",
            "## Provenance",
            "",
            f"- Model: `{meta['model_name']}`",
            f"- Source: `{meta['source_name']}`",
            f"- DOI: `{meta['source_doi']}`",
            f"- URL: `{meta['source_url']}`",
            f"- License: `{meta['license_name']}`",
            f"- Modality: `{meta['modality']}`",
            "",
            "## Coverage",
            "",
            f"- Feature rows: `{meta['feature_rows']}`",
            f"- Matched rows: `{meta['matched_rows']}`",
            f"- Missing embedding rows: `{meta['missing_embedding_rows']}`",
            f"- Embedding columns: `{meta['embedding_column_count']}`",
            f"- Transfer hash: `{meta['foundation_transfer_hash']}`",
            "",
            "## Guardrails",
            "",
            "- Embedding generation must not read seizure labels.",
            "- Embedding tables containing label, alarm, split, or future-event columns are rejected.",
            "- License and modality compatibility must be documented before use.",
            "- Results are transfer baselines, not claims that this project trained a foundation model.",
            "",
        ]
    )


def table_records(df: pd.DataFrame) -> list[dict[str, Any]]:
    records = []
    for record in df.to_dict(orient="records"):
        clean = {}
        for key, value in record.items():
            if isinstance(value, float) and (np.isnan(value) or np.isinf(value)):
                clean[key] = None
            elif value is pd.NA or value is pd.NaT:
                clean[key] = None
            elif isinstance(value, pd.Timestamp):
                clean[key] = value.isoformat()
            elif isinstance(value, np.integer):
                clean[key] = int(value)
            elif isinstance(value, np.floating):
                clean[key] = float(value)
            else:
                clean[key] = value
        records.append(clean)
    return records
