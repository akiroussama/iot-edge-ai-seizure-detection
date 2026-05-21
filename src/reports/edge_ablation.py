from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
from typing import Any

import numpy as np
import pandas as pd


EDGE_REQUIRED_COLUMNS = {
    "model_name",
    "edge_target",
    "quantization",
    "parameter_count",
    "model_size_kb",
    "ram_kb",
    "flash_kb",
    "latency_ms",
    "energy_mj_per_inference",
    "profiling_method",
    "evidence_uri",
}
EDGE_COST_COLUMNS = [
    "parameter_count",
    "model_size_kb",
    "ram_kb",
    "flash_kb",
    "latency_ms",
    "energy_mj_per_inference",
]
SKILL_METRIC_PRIORITY = (
    "brier_skill_score",
    "auroc",
    "auprc",
    "sensitivity",
)
PRE_GATE_C_STATUSES = {
    "pre_gate_c_exploratory_not_citable",
    "synthetic_smoke_test_not_citable",
}


@dataclass(frozen=True)
class EdgeAblationConfig:
    skill_metric: str = "auto"
    latency_budget_ms: float = 100.0
    ram_budget_kb: float = 512.0
    flash_budget_kb: float = 1024.0
    energy_budget_mj: float = 1.0
    model_size_budget_kb: float = 1024.0
    parameter_budget: float = 100_000.0
    require_traceability: bool = True


@dataclass(frozen=True)
class EdgeAblationReport:
    table: pd.DataFrame
    pareto: pd.DataFrame
    warnings: pd.DataFrame
    manifest: pd.DataFrame
    metadata: dict[str, Any]


def _require_columns(df: pd.DataFrame, required: set[str], name: str) -> None:
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"{name} missing required columns: {missing}")


def _clean_text(series: pd.Series) -> pd.Series:
    return series.astype("string").fillna("").str.strip()


def _validate_config(config: EdgeAblationConfig) -> None:
    if config.skill_metric != "auto" and config.skill_metric not in SKILL_METRIC_PRIORITY:
        raise ValueError(
            f"skill_metric must be 'auto' or one of {sorted(SKILL_METRIC_PRIORITY)}"
        )
    budgets = {
        "latency_budget_ms": config.latency_budget_ms,
        "ram_budget_kb": config.ram_budget_kb,
        "flash_budget_kb": config.flash_budget_kb,
        "energy_budget_mj": config.energy_budget_mj,
        "model_size_budget_kb": config.model_size_budget_kb,
        "parameter_budget": config.parameter_budget,
    }
    bad = [name for name, value in budgets.items() if value <= 0]
    if bad:
        raise ValueError(f"edge budgets must be positive: {bad}")


def validate_edge_profiles(
    edge_profiles: pd.DataFrame,
    *,
    require_traceability: bool = True,
) -> pd.DataFrame:
    _require_columns(edge_profiles, EDGE_REQUIRED_COLUMNS, "edge_profiles")
    out = edge_profiles.copy()
    out["model_name"] = _clean_text(out["model_name"])
    out["edge_target"] = _clean_text(out["edge_target"])
    out["quantization"] = _clean_text(out["quantization"])
    out["profiling_method"] = _clean_text(out["profiling_method"])
    out["evidence_uri"] = _clean_text(out["evidence_uri"])
    empty_keys = out["model_name"].eq("") | out["edge_target"].eq("") | out["quantization"].eq("")
    if empty_keys.any():
        raise ValueError("edge_profiles model_name, edge_target, and quantization cannot be empty")

    duplicate_keys = out.duplicated(["model_name", "edge_target", "quantization"], keep=False)
    if duplicate_keys.any():
        examples = out.loc[
            duplicate_keys,
            ["model_name", "edge_target", "quantization"],
        ].head(3).to_dict(orient="records")
        raise ValueError(f"edge_profiles contains duplicate profile keys, examples={examples}")

    for column in EDGE_COST_COLUMNS:
        values = pd.to_numeric(out[column], errors="coerce")
        if values.isna().any():
            raise ValueError(f"edge_profiles column {column!r} contains non-numeric values")
        if values.lt(0).any():
            raise ValueError(f"edge_profiles column {column!r} contains negative values")
        out[column] = values.astype(float)

    if require_traceability:
        missing_trace = out["profiling_method"].eq("") | out["evidence_uri"].eq("")
        if missing_trace.any():
            examples = out.loc[
                missing_trace,
                ["model_name", "edge_target", "quantization"],
            ].head(3).to_dict(orient="records")
            raise ValueError(
                "edge_profiles require non-empty profiling_method and evidence_uri, "
                f"examples={examples}"
            )
    return out


def _prepare_clinical_rows(clinical_rows: pd.DataFrame) -> pd.DataFrame:
    _require_columns(clinical_rows, {"model_name"}, "clinical_rows")
    out = clinical_rows.copy()
    out["model_name"] = _clean_text(out["model_name"])
    if out["model_name"].eq("").any():
        raise ValueError("clinical_rows model_name cannot be empty")
    duplicate_models = out.duplicated(["model_name"], keep=False)
    if duplicate_models.any():
        examples = out.loc[duplicate_models, ["model_name"]].head(3).to_dict(orient="records")
        raise ValueError(f"clinical_rows contains duplicate model_name rows, examples={examples}")
    return out


def _choose_skill_metric(table: pd.DataFrame, configured: str) -> str:
    if configured != "auto":
        if configured not in table.columns:
            raise ValueError(f"configured skill metric {configured!r} is missing")
        return configured
    for metric in SKILL_METRIC_PRIORITY:
        if metric in table.columns and pd.to_numeric(table[metric], errors="coerce").notna().any():
            return metric
    raise ValueError(
        "clinical_rows must contain at least one numeric skill metric: "
        f"{list(SKILL_METRIC_PRIORITY)}"
    )


def _edge_cost_index(table: pd.DataFrame, config: EdgeAblationConfig) -> pd.Series:
    components = pd.DataFrame(
        {
            "parameter_cost": table["parameter_count"] / config.parameter_budget,
            "model_size_cost": table["model_size_kb"] / config.model_size_budget_kb,
            "ram_cost": table["ram_kb"] / config.ram_budget_kb,
            "flash_cost": table["flash_kb"] / config.flash_budget_kb,
            "latency_cost": table["latency_ms"] / config.latency_budget_ms,
            "energy_cost": table["energy_mj_per_inference"] / config.energy_budget_mj,
        },
        index=table.index,
    )
    return components.mean(axis=1)


def _pareto_efficient(table: pd.DataFrame) -> pd.Series:
    score = pd.to_numeric(table["clinical_score"], errors="coerce").to_numpy(dtype=float)
    costs = table[EDGE_COST_COLUMNS].to_numpy(dtype=float)
    efficient = np.ones(len(table), dtype=bool)
    for idx in range(len(table)):
        if not np.isfinite(score[idx]) or not np.isfinite(costs[idx]).all():
            efficient[idx] = False
            continue
        better_or_equal = score >= score[idx]
        lower_or_equal_costs = np.all(costs <= costs[idx], axis=1)
        strict = (score > score[idx]) | np.any(costs < costs[idx], axis=1)
        dominated = better_or_equal & lower_or_equal_costs & strict
        dominated[idx] = False
        efficient[idx] = not dominated.any()
    return pd.Series(efficient, index=table.index)


def _warning_rows(table: pd.DataFrame, skill_metric: str) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    if "result_status" in table.columns:
        pre_gate = table["result_status"].astype("string").isin(PRE_GATE_C_STATUSES)
        for _, row in table.loc[pre_gate].iterrows():
            rows.append(
                {
                    "warning_code": "clinical_score_not_citable",
                    "model_name": row["model_name"],
                    "edge_target": row["edge_target"],
                    "quantization": row["quantization"],
                    "message": "Clinical score is pre-Gate-C or synthetic and must not be cited.",
                }
            )
    estimated = table["profiling_method"].astype("string").str.contains("estimate", case=False, na=False)
    for _, row in table.loc[estimated].iterrows():
        rows.append(
            {
                "warning_code": "edge_cost_estimated",
                "model_name": row["model_name"],
                "edge_target": row["edge_target"],
                "quantization": row["quantization"],
                "message": "Edge cost is documented as an estimate, not hardware measurement.",
            }
        )
    missing_skill = pd.to_numeric(table[skill_metric], errors="coerce").isna()
    for _, row in table.loc[missing_skill].iterrows():
        rows.append(
            {
                "warning_code": "missing_clinical_score",
                "model_name": row["model_name"],
                "edge_target": row["edge_target"],
                "quantization": row["quantization"],
                "message": f"Selected clinical skill metric {skill_metric!r} is missing.",
            }
        )
    return pd.DataFrame(
        rows,
        columns=["warning_code", "model_name", "edge_target", "quantization", "message"],
    )


def _jsonable(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return value.round(10).tolist()
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, dict):
        return {str(key): _jsonable(val) for key, val in value.items()}
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    return value


def _stable_hash(payload: Any) -> str:
    import json

    data = json.dumps(_jsonable(payload), sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256(data).hexdigest()


def _dataframe_hash(df: pd.DataFrame) -> str:
    return sha256(df.to_csv(index=False).encode("utf-8")).hexdigest()


def build_edge_ablation_report(
    clinical_rows: pd.DataFrame,
    edge_profiles: pd.DataFrame,
    *,
    config: EdgeAblationConfig | None = None,
    report_name: str = "edge_aware_ablation",
) -> EdgeAblationReport:
    cfg = config or EdgeAblationConfig()
    _validate_config(cfg)
    clinical = _prepare_clinical_rows(clinical_rows)
    edge = validate_edge_profiles(edge_profiles, require_traceability=cfg.require_traceability)
    table = edge.merge(
        clinical,
        on="model_name",
        how="left",
        validate="many_to_one",
        suffixes=("", "_clinical"),
        indicator=True,
    )
    missing_clinical = table["_merge"].ne("both")
    if missing_clinical.any():
        examples = table.loc[
            missing_clinical,
            ["model_name", "edge_target", "quantization"],
        ].head(3).to_dict(orient="records")
        raise ValueError(
            "edge_profiles contain models without matching clinical_rows, "
            f"examples={examples}"
        )
    table = table.drop(columns=["_merge"])

    skill_metric = _choose_skill_metric(table, cfg.skill_metric)
    table["clinical_score_metric"] = skill_metric
    table["clinical_score"] = pd.to_numeric(table[skill_metric], errors="coerce")
    if table["clinical_score"].isna().all():
        raise ValueError(f"selected clinical skill metric {skill_metric!r} has no numeric values")
    table["edge_cost_index"] = _edge_cost_index(table, cfg)
    table["skill_per_cost_index"] = table["clinical_score"] / table["edge_cost_index"].replace(0, np.nan)
    table["pareto_efficient"] = _pareto_efficient(table)
    table["edge_claim_status"] = np.where(
        table["profiling_method"].astype("string").str.contains("measure", case=False, na=False),
        "measured",
        "estimated_documented",
    )
    table["paper_claim_status"] = np.where(
        table.get("citation_status", pd.Series("", index=table.index)).eq("citable_after_gate_c"),
        "edge_cost_with_citable_clinical_score",
        "edge_cost_with_non_citable_clinical_score",
    )
    ordered_columns = [
        "model_name",
        "model_family",
        "edge_target",
        "quantization",
        "clinical_score_metric",
        "clinical_score",
        "parameter_count",
        "model_size_kb",
        "ram_kb",
        "flash_kb",
        "latency_ms",
        "energy_mj_per_inference",
        "edge_cost_index",
        "skill_per_cost_index",
        "pareto_efficient",
        "edge_claim_status",
        "paper_claim_status",
        "profiling_method",
        "evidence_uri",
        "result_status",
        "citation_status",
        "gate_c_status",
    ]
    table = table[[column for column in ordered_columns if column in table.columns] + [
        column for column in table.columns if column not in ordered_columns
    ]]
    pareto = table.loc[table["pareto_efficient"]].sort_values(
        ["clinical_score", "edge_cost_index"],
        ascending=[False, True],
    ).reset_index(drop=True)
    warnings = _warning_rows(table, skill_metric)
    clinical_hash = _dataframe_hash(clinical)
    edge_hash = _dataframe_hash(edge)
    table_hash = _dataframe_hash(table)
    artifact_hash = _stable_hash(
        {
            "report_name": report_name,
            "config": asdict(cfg),
            "clinical_hash": clinical_hash,
            "edge_hash": edge_hash,
            "table_hash": table_hash,
        }
    )
    metadata = {
        "report_name": report_name,
        "n_models": int(table["model_name"].nunique()),
        "n_edge_profiles": int(len(edge)),
        "n_pareto_profiles": int(len(pareto)),
        "skill_metric": skill_metric,
        "clinical_rows_hash": clinical_hash,
        "edge_profiles_hash": edge_hash,
        "edge_ablation_table_hash": table_hash,
        "training_artifact_hash": artifact_hash,
        "result_status": "edge_ablation_pre_gate_c_not_citable",
        "claim_scope": "clinical_score_and_edge_cost_are_reported_separately",
    }
    manifest = pd.DataFrame([metadata | {"config": asdict(cfg)}])
    return EdgeAblationReport(
        table=table.reset_index(drop=True),
        pareto=pareto,
        warnings=warnings,
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


def edge_ablation_markdown(
    report: EdgeAblationReport,
    *,
    title: str = "Edge-Aware Ablation Report",
) -> str:
    return f"""# {title}

**Citation status:** not citable as a benchmark result before Gate C.

## Metadata

- Report: `{report.metadata["report_name"]}`
- Models: `{report.metadata["n_models"]}`
- Edge profiles: `{report.metadata["n_edge_profiles"]}`
- Pareto profiles: `{report.metadata["n_pareto_profiles"]}`
- Skill metric: `{report.metadata["skill_metric"]}`
- Claim scope: `{report.metadata["claim_scope"]}`
- Artifact hash: `{report.metadata["training_artifact_hash"]}`

## Edge-Aware Table

{_markdown_table(report.table)}

## Pareto Frontier

{_markdown_table(report.pareto)}

## Warnings

{_markdown_table(report.warnings)}
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
