from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
from typing import Any

import numpy as np
import pandas as pd

from src.interpretability.sparse_autoencoder import LEAKAGE_OR_METADATA_COLUMNS
from src.utils.time import ensure_datetime


DEFAULT_COUNTERFACTUAL_ID_COLUMNS = ("patient_id", "recording_id", "window_start", "window_end")
DATETIME_ALIGNMENT_COLUMNS = {"window_start", "window_end", "recording_start", "recording_end"}


@dataclass(frozen=True)
class CounterfactualConfig:
    fit_split: str | None = "train"
    split_col: str = "split"
    risk_col: str = "risk_score"
    alarm_col: str = "alarm"
    excluded_col: str = "is_excluded"
    threshold_col: str = "alarm_threshold"
    target_risk: float | None = None
    direction: str = "prevent_alarm"
    margin: float = 0.01
    ridge_alpha: float = 1e-3
    top_k_features: int = 3
    feature_cols: tuple[str, ...] = ()


@dataclass(frozen=True)
class CounterfactualReport:
    rows: pd.DataFrame
    feature_changes: pd.DataFrame
    summary: pd.DataFrame
    manifest: pd.DataFrame
    metadata: dict[str, Any]


def _require_columns(df: pd.DataFrame, required: set[str], name: str) -> None:
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"{name} missing required columns: {missing}")


def _bool_series(df: pd.DataFrame, column: str, default: bool = False) -> pd.Series:
    if column not in df.columns:
        return pd.Series(default, index=df.index, dtype=bool)
    series = df[column]
    if pd.api.types.is_bool_dtype(series):
        return series.fillna(default).astype(bool)
    if pd.api.types.is_numeric_dtype(series):
        return series.fillna(int(default)).astype(bool)
    normalized = series.astype("string").str.strip().str.lower()
    out = pd.Series(default, index=df.index, dtype=bool)
    out[normalized.isin({"true", "1", "yes", "y"})] = True
    out[normalized.isin({"false", "0", "no", "n", "", "nan", "<na>"})] = False
    return out


def _validate_config(config: CounterfactualConfig) -> None:
    if config.direction not in {"prevent_alarm", "trigger_alarm"}:
        raise ValueError("direction must be 'prevent_alarm' or 'trigger_alarm'")
    if config.target_risk is not None and not 0 < config.target_risk < 1:
        raise ValueError("target_risk must be in (0, 1)")
    if not 0 <= config.margin < 0.5:
        raise ValueError("margin must be in [0, 0.5)")
    if config.ridge_alpha < 0:
        raise ValueError("ridge_alpha must be non-negative")
    if config.top_k_features <= 0:
        raise ValueError("top_k_features must be positive")


def select_counterfactual_feature_columns(
    df: pd.DataFrame,
    requested: tuple[str, ...] = (),
) -> list[str]:
    if requested:
        missing = [column for column in requested if column not in df.columns]
        if missing:
            raise ValueError(f"requested feature columns are missing: {missing}")
        non_numeric = [
            column for column in requested if not pd.api.types.is_numeric_dtype(df[column])
        ]
        if non_numeric:
            raise ValueError(f"requested feature columns are non-numeric: {non_numeric}")
        return list(requested)
    return [
        column
        for column in df.columns
        if column not in LEAKAGE_OR_METADATA_COLUMNS
        and pd.api.types.is_numeric_dtype(df[column])
    ]


def _normalize_table(
    features: pd.DataFrame,
    *,
    id_columns: tuple[str, ...],
    config: CounterfactualConfig,
) -> pd.DataFrame:
    required = {config.risk_col, config.alarm_col, config.excluded_col, *id_columns}
    _require_columns(features, required, "features")
    out = features.copy()
    for column in id_columns:
        if column in DATETIME_ALIGNMENT_COLUMNS:
            out[column] = ensure_datetime(out[column])
    risk = pd.to_numeric(out[config.risk_col], errors="coerce")
    if risk.isna().any():
        raise ValueError(f"{config.risk_col} contains non-finite values")
    out[config.risk_col] = risk.clip(0.0, 1.0)
    out[config.alarm_col] = _bool_series(out, config.alarm_col)
    out[config.excluded_col] = _bool_series(out, config.excluded_col)
    duplicate_mask = out.duplicated(list(id_columns), keep=False)
    if duplicate_mask.any():
        examples = out.loc[duplicate_mask, list(id_columns)].head(3).to_dict(orient="records")
        raise ValueError(f"features contains duplicate alignment keys, examples={examples}")
    return out


def _fit_preprocessor(df: pd.DataFrame, feature_cols: list[str]) -> dict[str, np.ndarray]:
    values = df[feature_cols].apply(pd.to_numeric, errors="coerce")
    medians = values.median(axis=0).fillna(0.0).to_numpy(dtype=np.float64)
    filled = values.fillna(dict(zip(feature_cols, medians, strict=True)))
    means = filled.mean(axis=0).to_numpy(dtype=np.float64)
    scales = filled.std(axis=0).replace(0.0, 1.0).fillna(1.0).to_numpy(dtype=np.float64)
    return {"medians": medians, "means": means, "scales": scales}


def _transform(
    df: pd.DataFrame,
    feature_cols: list[str],
    preprocessor: dict[str, np.ndarray],
) -> np.ndarray:
    values = df[feature_cols].apply(pd.to_numeric, errors="coerce")
    values = values.fillna(dict(zip(feature_cols, preprocessor["medians"], strict=True)))
    return ((values.to_numpy(dtype=np.float64) - preprocessor["means"]) / preprocessor["scales"]).astype(
        np.float64
    )


def _sigmoid(x: np.ndarray | float) -> np.ndarray | float:
    return 1.0 / (1.0 + np.exp(-np.clip(x, -50, 50)))


def _logit(p: np.ndarray | float) -> np.ndarray | float:
    clipped = np.clip(p, 1e-6, 1.0 - 1e-6)
    return np.log(clipped / (1.0 - clipped))


def _fit_linear_surrogate(
    x: np.ndarray,
    risk: np.ndarray,
    *,
    ridge_alpha: float,
) -> dict[str, np.ndarray | float]:
    y = np.asarray(_logit(risk), dtype=np.float64)
    design = np.c_[x, np.ones(len(x), dtype=np.float64)]
    penalty = np.eye(design.shape[1], dtype=np.float64) * ridge_alpha
    penalty[-1, -1] = 0.0
    coef = np.linalg.solve(design.T @ design + penalty, design.T @ y)
    pred = np.asarray(_sigmoid(design @ coef), dtype=np.float64)
    mse = float(np.mean((pred - risk) ** 2))
    return {"weights": coef[:-1], "bias": float(coef[-1]), "fit_mse": mse}


def _fit_mask(df: pd.DataFrame, config: CounterfactualConfig) -> pd.Series:
    valid = ~_bool_series(df, config.excluded_col)
    if config.fit_split is not None and config.split_col in df.columns:
        valid &= df[config.split_col].astype(str).eq(str(config.fit_split))
    return valid


def _row_threshold(row: pd.Series, config: CounterfactualConfig) -> float:
    if config.target_risk is not None:
        return float(config.target_risk)
    if config.threshold_col in row and pd.notna(row[config.threshold_col]):
        return float(np.clip(float(row[config.threshold_col]), 1e-6, 1.0 - 1e-6))
    return 0.5


def _counterfactual_shift(
    x: np.ndarray,
    *,
    weights: np.ndarray,
    bias: float,
    threshold: float,
    config: CounterfactualConfig,
) -> tuple[np.ndarray, float, float, str]:
    current_logit = float(x @ weights + bias)
    current_risk = float(_sigmoid(current_logit))
    if config.direction == "prevent_alarm":
        target = float(np.clip(threshold - config.margin, 1e-6, 1.0 - 1e-6))
        if current_risk <= target:
            return np.zeros_like(x), current_risk, current_risk, "already_satisfies_target"
    else:
        target = float(np.clip(threshold + config.margin, 1e-6, 1.0 - 1e-6))
        if current_risk >= target:
            return np.zeros_like(x), current_risk, current_risk, "already_satisfies_target"

    norm_sq = float(weights @ weights)
    if norm_sq == 0:
        return np.zeros_like(x), current_risk, current_risk, "unavailable_zero_surrogate_gradient"
    target_logit = float(_logit(target))
    delta = ((target_logit - current_logit) / norm_sq) * weights
    counterfactual_risk = float(_sigmoid((x + delta) @ weights + bias))
    return delta, current_risk, counterfactual_risk, "computed"


def build_counterfactual_report(
    features: pd.DataFrame,
    *,
    config: CounterfactualConfig | None = None,
    model_name: str = "counterfactual_surrogate",
    id_columns: tuple[str, ...] = DEFAULT_COUNTERFACTUAL_ID_COLUMNS,
) -> CounterfactualReport:
    cfg = config or CounterfactualConfig()
    _validate_config(cfg)
    data = _normalize_table(features, id_columns=id_columns, config=cfg)
    feature_cols = select_counterfactual_feature_columns(data, cfg.feature_cols)
    if not feature_cols:
        raise ValueError("at least one numeric counterfactual feature column is required")
    fit_mask = _fit_mask(data, cfg)
    if not fit_mask.any():
        raise ValueError("fit split has no usable rows for counterfactual surrogate")
    preprocessor = _fit_preprocessor(data.loc[fit_mask], feature_cols)
    train_x = _transform(data.loc[fit_mask], feature_cols, preprocessor)
    train_risk = data.loc[fit_mask, cfg.risk_col].to_numpy(dtype=float)
    surrogate = _fit_linear_surrogate(train_x, train_risk, ridge_alpha=cfg.ridge_alpha)
    all_x = _transform(data, feature_cols, preprocessor)
    weights = np.asarray(surrogate["weights"], dtype=float)
    bias = float(surrogate["bias"])

    row_records: list[dict[str, Any]] = []
    change_records: list[dict[str, Any]] = []
    for row_idx, (_, row) in enumerate(data.iterrows()):
        threshold = _row_threshold(row, cfg)
        delta_z, surrogate_risk, counterfactual_risk, status = _counterfactual_shift(
            all_x[row_idx],
            weights=weights,
            bias=bias,
            threshold=threshold,
            config=cfg,
        )
        delta_original = delta_z * preprocessor["scales"]
        abs_order = np.argsort(-np.abs(delta_original))
        top_indices = abs_order[: min(cfg.top_k_features, len(feature_cols))]
        top_feature = feature_cols[int(top_indices[0])]
        top_delta = float(delta_original[int(top_indices[0])])
        original_value = float(pd.to_numeric(pd.Series([row[top_feature]]), errors="coerce").iloc[0])
        counterfactual_value = original_value + top_delta
        base = {column: row[column] for column in id_columns if column in row.index}
        row_records.append(
            {
                **base,
                "model_name": model_name,
                "counterfactual_direction": cfg.direction,
                "counterfactual_status": status,
                "risk_score": float(row[cfg.risk_col]),
                "alarm": bool(row[cfg.alarm_col]),
                "target_risk_threshold": threshold,
                "surrogate_risk_score": surrogate_risk,
                "counterfactual_surrogate_risk_score": counterfactual_risk,
                "required_l2_shift": float(np.linalg.norm(delta_z)),
                "top_counterfactual_feature": top_feature,
                "top_feature_delta": top_delta,
                "top_feature_original_value": original_value,
                "top_feature_counterfactual_value": counterfactual_value,
                "counterfactual_narrative": (
                    f"{cfg.direction} by changing {top_feature} by {top_delta:.6g} "
                    f"under a linear surrogate, not a causal claim"
                ),
                "counterfactual_explanation_status": "surrogate_post_hoc_not_causal",
            }
        )
        for rank, feature_idx in enumerate(top_indices, start=1):
            feature = feature_cols[int(feature_idx)]
            original = float(pd.to_numeric(pd.Series([row[feature]]), errors="coerce").iloc[0])
            delta = float(delta_original[int(feature_idx)])
            change_records.append(
                {
                    **base,
                    "model_name": model_name,
                    "feature_rank": rank,
                    "feature": feature,
                    "original_value": original,
                    "counterfactual_value": original + delta,
                    "delta": delta,
                    "abs_delta": abs(delta),
                    "standardized_delta": float(delta_z[int(feature_idx)]),
                    "surrogate_weight": float(weights[int(feature_idx)]),
                    "counterfactual_status": status,
                }
            )

    rows = pd.DataFrame(row_records)
    changes = pd.DataFrame(change_records)
    summary = pd.DataFrame(
        [
            {
                "model_name": model_name,
                "rows": int(len(rows)),
                "computed_rows": int(rows["counterfactual_status"].eq("computed").sum()),
                "already_satisfies_target_rows": int(
                    rows["counterfactual_status"].eq("already_satisfies_target").sum()
                ),
                "mean_required_l2_shift": float(rows["required_l2_shift"].mean()),
                "median_required_l2_shift": float(rows["required_l2_shift"].median()),
                "surrogate_fit_mse": float(surrogate["fit_mse"]),
            }
        ]
    )
    hash_columns = [
        *id_columns,
        *feature_cols,
        cfg.risk_col,
        cfg.alarm_col,
        cfg.excluded_col,
        cfg.threshold_col,
        cfg.split_col,
    ]
    hash_columns = [column for column in dict.fromkeys(hash_columns) if column in data.columns]
    input_hash = _dataframe_hash(data[hash_columns])
    rows_hash = _dataframe_hash(rows)
    artifact_hash = _stable_hash(
        {
            "model_name": model_name,
            "config": asdict(cfg),
            "id_columns": list(id_columns),
            "feature_cols": feature_cols,
            "preprocessor": preprocessor,
            "surrogate": surrogate,
            "input_hash": input_hash,
            "rows_hash": rows_hash,
        }
    )
    metadata = {
        "model_name": model_name,
        "id_columns": list(id_columns),
        "feature_columns": feature_cols,
        "n_rows": int(len(rows)),
        "fit_rows": int(fit_mask.sum()),
        "surrogate_fit_mse": float(surrogate["fit_mse"]),
        "input_table_hash": input_hash,
        "counterfactual_rows_hash": rows_hash,
        "training_artifact_hash": artifact_hash,
        "result_status": "counterfactual_probe_pre_gate_c_not_citable",
        "explanation_status": "surrogate_post_hoc_not_causal",
    }
    manifest = pd.DataFrame([metadata | {"config": asdict(cfg)}])
    return CounterfactualReport(
        rows=rows,
        feature_changes=changes,
        summary=summary,
        manifest=manifest,
        metadata=metadata,
    )


def _jsonable(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return value.round(10).tolist()
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
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
    normalized = df.copy()
    for column in normalized.columns:
        if column in DATETIME_ALIGNMENT_COLUMNS:
            normalized[column] = ensure_datetime(normalized[column]).astype(str)
    return sha256(normalized.to_csv(index=False).encode("utf-8")).hexdigest()


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


def counterfactual_markdown(
    report: CounterfactualReport,
    *,
    title: str = "Counterfactual Probing Report",
) -> str:
    return f"""# {title}

**Citation status:** not citable as a benchmark result before Gate C.

## Metadata

- Model: `{report.metadata["model_name"]}`
- Rows: `{report.metadata["n_rows"]}`
- Fit rows: `{report.metadata["fit_rows"]}`
- Surrogate fit MSE: `{report.metadata["surrogate_fit_mse"]}`
- Explanation status: `{report.metadata["explanation_status"]}`
- Artifact hash: `{report.metadata["training_artifact_hash"]}`

## Summary

{_markdown_table(report.summary)}

## Counterfactual Rows

{_markdown_table(report.rows)}

## Feature Changes

{_markdown_table(report.feature_changes)}
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
