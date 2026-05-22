from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from hashlib import sha256
from typing import Any

import numpy as np
import pandas as pd

RAW_LEVEL_COLUMNS = {
    "patient_id",
    "recording_id",
    "window_start",
    "window_end",
    "seizure_start",
    "seizure_end",
    "risk_score",
    "forecast_label",
    "alarm",
    "is_excluded",
}

FEDERATED_REQUIRED_COLUMNS = {
    "site_id",
    "dataset",
    "task_type",
    "model_name",
    "events_used_for_metrics",
    "prediction_rows",
    "valid_prediction_rows",
    "sensitivity",
    "false_alarm_rate_per_day",
    "time_in_warning",
    "brier_score",
    "brier_skill_score",
    "citation_status",
    "gate_c_status",
    "leakage_status",
    "split_frozen_status",
    "evidence_uri",
}

AGGREGATE_METRICS = (
    "sensitivity",
    "false_alarm_rate_per_day",
    "time_in_warning",
    "brier_score",
    "brier_skill_score",
    "expected_calibration_error",
    "auroc",
    "auprc",
)


@dataclass(frozen=True)
class FederatedBenchmarkConfig:
    site_col: str = "site_id"
    group_cols: tuple[str, ...] = ("dataset", "task_type", "model_name", "horizon_name")
    min_sites: int = 2
    weight_col: str = "events_used_for_metrics"
    require_clean_gate_c_for_citable: bool = True
    citation_status: str = "not_citable_pre_gate_c"
    gate_c_status: str = "not_started"
    privacy_status: str = "site_level_metrics_only_no_raw_windows"


@dataclass(frozen=True)
class FederatedBenchmarkReport:
    validated_sites: pd.DataFrame
    summary: pd.DataFrame
    manifest: pd.DataFrame
    metadata: dict[str, Any]


def _require_columns(df: pd.DataFrame, required: set[str], name: str) -> None:
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"{name} missing required columns: {missing}")


def _validate_config(config: FederatedBenchmarkConfig) -> None:
    if config.min_sites < 2:
        raise ValueError("min_sites must be at least 2 for a federated benchmark")
    if config.citation_status not in {"not_citable_pre_gate_c", "citable_after_gate_c"}:
        raise ValueError("citation_status must be not_citable_pre_gate_c or citable_after_gate_c")
    if config.gate_c_status not in {"not_started", "partial", "passed", "failed"}:
        raise ValueError("gate_c_status must be not_started, partial, passed, or failed")
    if config.citation_status == "citable_after_gate_c" and config.gate_c_status != "passed":
        raise ValueError("citable federated summaries require gate_c_status='passed'")


def validate_federated_site_results(
    site_results: pd.DataFrame,
    *,
    config: FederatedBenchmarkConfig | None = None,
) -> pd.DataFrame:
    cfg = config or FederatedBenchmarkConfig()
    _validate_config(cfg)
    required = (FEDERATED_REQUIRED_COLUMNS - {"site_id"}) | {cfg.site_col, cfg.weight_col}
    required |= set(cfg.group_cols)
    _require_columns(site_results, required, "site_results")
    raw_columns = sorted(RAW_LEVEL_COLUMNS & set(site_results.columns))
    if raw_columns:
        raise ValueError(f"federated site results must not contain raw row-level columns: {raw_columns}")
    out = site_results.copy()
    out[cfg.site_col] = out[cfg.site_col].astype("string").str.strip()
    if out[cfg.site_col].eq("").any():
        raise ValueError(f"{cfg.site_col} cannot contain empty site identifiers")
    for column in ["events_used_for_metrics", "prediction_rows", "valid_prediction_rows", cfg.weight_col]:
        values = pd.to_numeric(out[column], errors="coerce")
        if values.isna().any() or values.lt(0).any():
            raise ValueError(f"{column} must contain non-negative numeric values")
        out[column] = values.astype(float)
    for metric in AGGREGATE_METRICS:
        if metric in out.columns:
            out[metric] = pd.to_numeric(out[metric], errors="coerce")
    if cfg.require_clean_gate_c_for_citable and cfg.citation_status == "citable_after_gate_c":
        bad = out.loc[
            ~out["citation_status"].eq("citable_after_gate_c")
            | ~out["gate_c_status"].eq("passed")
            | ~out["leakage_status"].eq("clean")
            | ~out["split_frozen_status"].isin({"frozen_git_tag", "frozen_doi"})
        ]
        if not bad.empty:
            sites = bad[cfg.site_col].astype(str).tolist()
            raise ValueError(f"citable federated summary has non-citable or dirty site rows: {sites}")
    out["federated_input_status"] = "site_level_validated"
    return out


def _weighted_mean(values: pd.Series, weights: pd.Series) -> float | None:
    vals = pd.to_numeric(values, errors="coerce")
    w = pd.to_numeric(weights, errors="coerce")
    valid = vals.notna() & w.notna() & w.gt(0)
    if not valid.any():
        return None
    return float(np.average(vals.loc[valid], weights=w.loc[valid]))


def _metric_range(values: pd.Series) -> float | None:
    vals = pd.to_numeric(values, errors="coerce").dropna()
    if vals.empty:
        return None
    return float(vals.max() - vals.min())


def _dataframe_hash(df: pd.DataFrame) -> str:
    normalized = df.copy()
    return sha256(normalized.to_csv(index=False).encode("utf-8")).hexdigest()


def federated_benchmark_summary(
    site_results: pd.DataFrame,
    *,
    config: FederatedBenchmarkConfig | None = None,
) -> FederatedBenchmarkReport:
    cfg = config or FederatedBenchmarkConfig()
    validated = validate_federated_site_results(site_results, config=cfg)
    rows: list[dict[str, Any]] = []
    for group_key, group in validated.groupby(list(cfg.group_cols), dropna=False, sort=False):
        group_values = group_key if isinstance(group_key, tuple) else (group_key,)
        row = dict(zip(cfg.group_cols, group_values, strict=True))
        site_count = int(group[cfg.site_col].nunique())
        if site_count < cfg.min_sites:
            aggregate_status = "insufficient_sites"
        else:
            aggregate_status = "federated_summary_ready"
        row.update(
            {
                "aggregate_id": sha256(
                    json.dumps(row, sort_keys=True, default=str).encode("utf-8")
                ).hexdigest()[:16],
                "site_count": site_count,
                "site_ids": ",".join(sorted(group[cfg.site_col].astype(str).unique())),
                "total_events_used_for_metrics": int(group["events_used_for_metrics"].sum()),
                "total_prediction_rows": int(group["prediction_rows"].sum()),
                "total_valid_prediction_rows": int(group["valid_prediction_rows"].sum()),
                "aggregate_status": aggregate_status,
                "privacy_status": cfg.privacy_status,
                "citation_status": cfg.citation_status,
                "gate_c_status": cfg.gate_c_status,
                "federated_claim_status": "not_citable_until_all_sites_gate_c_clean"
                if cfg.citation_status != "citable_after_gate_c"
                else "citable_federated_summary",
            }
        )
        for metric in AGGREGATE_METRICS:
            if metric in group.columns:
                row[f"weighted_{metric}"] = _weighted_mean(group[metric], group[cfg.weight_col])
                row[f"unweighted_{metric}"] = (
                    float(group[metric].mean()) if group[metric].notna().any() else None
                )
                row[f"site_range_{metric}"] = _metric_range(group[metric])
        rows.append(row)
    summary = pd.DataFrame(rows)
    metadata = {
        "report_name": "federated_benchmark_protocol",
        "site_rows": int(len(validated)),
        "aggregate_rows": int(len(summary)),
        "input_hash": _dataframe_hash(validated),
        "summary_hash": _dataframe_hash(summary),
        "config_hash": sha256(json.dumps(asdict(cfg), sort_keys=True).encode("utf-8")).hexdigest(),
        "citation_status": cfg.citation_status,
        "gate_c_status": cfg.gate_c_status,
        "privacy_status": cfg.privacy_status,
        "analysis_status": "site_level_federated_benchmark_summary",
    }
    manifest = pd.DataFrame([metadata | {"config": asdict(cfg)}])
    return FederatedBenchmarkReport(
        validated_sites=validated,
        summary=summary,
        manifest=manifest,
        metadata=metadata,
    )


def federated_benchmark_markdown(
    report: FederatedBenchmarkReport,
    *,
    title: str = "Federated Benchmark Protocol",
) -> str:
    warning = ""
    if report.metadata["citation_status"] != "citable_after_gate_c":
        warning = "\n**Citation status:** not citable as a benchmark result before Gate C.\n"

    def table(df: pd.DataFrame, max_rows: int = 20) -> str:
        if df.empty:
            return "_No rows._"
        view = df.head(max_rows)
        lines = [
            "| " + " | ".join(str(column) for column in view.columns) + " |",
            "| " + " | ".join(["---"] * len(view.columns)) + " |",
        ]
        for _, row in view.iterrows():
            lines.append("| " + " | ".join(str(row[column]) for column in view.columns) + " |")
        return "\n".join(lines)

    return "\n".join(
        [
            f"# {title}",
            warning,
            "This protocol aggregates site-level benchmark rows, not raw patient windows.",
            "",
            "## Metadata",
            "",
            f"- Site rows: `{report.metadata['site_rows']}`",
            f"- Aggregate rows: `{report.metadata['aggregate_rows']}`",
            f"- Privacy status: `{report.metadata['privacy_status']}`",
            f"- Input hash: `{report.metadata['input_hash']}`",
            f"- Summary hash: `{report.metadata['summary_hash']}`",
            "",
            "## Federated Summary",
            "",
            table(report.summary),
            "",
            "## Guardrails",
            "",
            "- Inputs must be site-level metric rows, not patient/window rows.",
            "- Citable summaries require every site row to be Gate C passed, leakage-clean, and frozen.",
            "- Heterogeneity across sites is reported through site ranges, not hidden in pooled means.",
            "- Raw data sharing is not required for this report.",
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
            elif isinstance(value, np.integer):
                clean[key] = int(value)
            elif isinstance(value, np.floating):
                clean[key] = float(value)
            else:
                clean[key] = value
        records.append(clean)
    return records
