from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
from typing import Any

import numpy as np
import pandas as pd


DEFAULT_FAILURE_ID_COLUMNS = ("patient_id", "recording_id", "window_start", "window_end")


@dataclass(frozen=True)
class FailureTaxonomyConfig:
    risk_col: str = "risk_score"
    alarm_col: str = "alarm"
    label_col: str = "forecast_label"
    excluded_col: str = "is_excluded"
    patient_col: str = "patient_id"
    high_risk_threshold: float = 0.7
    low_risk_threshold: float = 0.3


@dataclass(frozen=True)
class FailureTaxonomyReport:
    rows: pd.DataFrame
    summary: pd.DataFrame
    patient_summary: pd.DataFrame
    warnings: pd.DataFrame
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


def _validate_config(config: FailureTaxonomyConfig) -> None:
    if not 0 <= config.low_risk_threshold <= config.high_risk_threshold <= 1:
        raise ValueError("risk thresholds must satisfy 0 <= low <= high <= 1")


def _severity(category: str, risk: float, label: bool, alarm: bool) -> float:
    if category == "missed_forecast_positive":
        return float(1.0 - risk)
    if category == "false_alarm_negative":
        return float(risk)
    if category == "excluded_alarm":
        return 1.0
    if category in {"observability_abstained", "observability_deficient"}:
        return 0.75
    if category == "true_positive_alarm":
        return float(max(0.0, 1.0 - risk) * 0.25)
    if category == "true_negative":
        return float(risk * 0.25)
    if label or alarm:
        return 0.5
    return 0.0


def _classify_row(row: pd.Series, config: FailureTaxonomyConfig) -> tuple[str, str]:
    risk = float(row[config.risk_col])
    label = bool(row[config.label_col])
    alarm = bool(row[config.alarm_col])
    excluded = bool(row[config.excluded_col])
    observable = row.get("is_observable", np.nan)
    abstain = row.get("abstain_for_observability", False)
    if excluded and alarm:
        return "excluded_alarm", "alarm emitted on an excluded/censored row"
    if excluded:
        return "excluded_row", "excluded/censored row not used for clinical scoring"
    if bool(abstain):
        return "observability_abstained", "prediction abstained because observability was insufficient"
    if pd.notna(observable) and not bool(observable):
        return "observability_deficient", "wearable signals marked deficient or non-observable"
    if label and alarm:
        if risk < config.high_risk_threshold:
            return "true_positive_low_margin", "positive row alarmed, but risk is below high-risk threshold"
        return "true_positive_alarm", "positive row alarmed"
    if label and not alarm:
        if risk <= config.low_risk_threshold:
            return "missed_low_risk_positive", "positive row missed with low risk score"
        return "missed_forecast_positive", "positive row missed by alarm policy"
    if not label and alarm:
        if risk >= config.high_risk_threshold:
            return "false_alarm_high_risk_negative", "negative row alarmed with high risk score"
        return "false_alarm_negative", "negative row alarmed"
    if risk >= config.high_risk_threshold:
        return "high_risk_true_negative", "negative row not alarmed but high risk score remains"
    return "true_negative", "negative row not alarmed"


def build_failure_taxonomy_rows(
    predictions: pd.DataFrame,
    *,
    config: FailureTaxonomyConfig | None = None,
    id_columns: tuple[str, ...] = DEFAULT_FAILURE_ID_COLUMNS,
) -> pd.DataFrame:
    cfg = config or FailureTaxonomyConfig()
    _validate_config(cfg)
    required = {cfg.risk_col, cfg.alarm_col, cfg.label_col, cfg.excluded_col, *id_columns}
    _require_columns(predictions, required, "predictions")
    out = predictions.copy()
    risk = pd.to_numeric(out[cfg.risk_col], errors="coerce")
    if risk.isna().any():
        raise ValueError(f"{cfg.risk_col} contains non-finite values")
    out[cfg.risk_col] = risk.clip(0.0, 1.0)
    out[cfg.alarm_col] = _bool_series(out, cfg.alarm_col)
    out[cfg.label_col] = _bool_series(out, cfg.label_col)
    out[cfg.excluded_col] = _bool_series(out, cfg.excluded_col)

    categories = []
    reasons = []
    severities = []
    for _, row in out.iterrows():
        category, reason = _classify_row(row, cfg)
        categories.append(category)
        reasons.append(reason)
        severities.append(
            _severity(
                category,
                float(row[cfg.risk_col]),
                bool(row[cfg.label_col]),
                bool(row[cfg.alarm_col]),
            )
        )
    out["failure_category"] = categories
    out["failure_reason"] = reasons
    out["failure_severity"] = severities
    out["failure_taxonomy_status"] = "post_hoc_descriptive_not_causal"
    return out


def summarize_failure_taxonomy(
    rows: pd.DataFrame,
    *,
    config: FailureTaxonomyConfig,
) -> pd.DataFrame:
    valid = ~_bool_series(rows, config.excluded_col)
    grouped = rows.groupby("failure_category", dropna=False)
    summary_rows = []
    for category, group in grouped:
        group_valid = valid.loc[group.index]
        labels = _bool_series(group, config.label_col)
        alarms = _bool_series(group, config.alarm_col)
        risks = pd.to_numeric(group[config.risk_col], errors="coerce")
        summary_rows.append(
            {
                "failure_category": category,
                "rows": int(len(group)),
                "valid_rows": int(group_valid.sum()),
                "positive_rows": int((labels & group_valid).sum()),
                "alarm_rows": int((alarms & group_valid).sum()),
                "mean_risk_score": float(risks.mean()),
                "mean_failure_severity": float(group["failure_severity"].mean()),
            }
        )
    out = pd.DataFrame(summary_rows)
    return out.sort_values(["mean_failure_severity", "rows"], ascending=[False, False]).reset_index(drop=True)


def summarize_failure_taxonomy_by_patient(
    rows: pd.DataFrame,
    *,
    config: FailureTaxonomyConfig,
) -> pd.DataFrame:
    if config.patient_col not in rows.columns:
        return pd.DataFrame()
    valid = ~_bool_series(rows, config.excluded_col)
    grouped = rows.groupby(config.patient_col, dropna=False)
    summary_rows = []
    for patient, group in grouped:
        group_valid = valid.loc[group.index]
        labels = _bool_series(group, config.label_col)
        alarms = _bool_series(group, config.alarm_col)
        severe = group["failure_category"].isin(
            [
                "missed_forecast_positive",
                "missed_low_risk_positive",
                "false_alarm_negative",
                "false_alarm_high_risk_negative",
                "observability_abstained",
                "observability_deficient",
                "excluded_alarm",
            ]
        )
        summary_rows.append(
            {
                "patient_id": patient,
                "rows": int(len(group)),
                "valid_rows": int(group_valid.sum()),
                "positive_rows": int((labels & group_valid).sum()),
                "alarm_rows": int((alarms & group_valid).sum()),
                "severe_failure_rows": int(severe.sum()),
                "mean_failure_severity": float(group["failure_severity"].mean()),
                "top_failure_category": str(group["failure_category"].mode().iloc[0]),
            }
        )
    return pd.DataFrame(summary_rows).sort_values(
        ["severe_failure_rows", "mean_failure_severity"],
        ascending=[False, False],
    ).reset_index(drop=True)


def _warning_rows(predictions: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    if "is_observable" not in predictions.columns:
        rows.append(
            {
                "warning_code": "observability_not_available",
                "message": "No is_observable column supplied; observability failures cannot be separated.",
            }
        )
    if "abstain_for_observability" not in predictions.columns:
        rows.append(
            {
                "warning_code": "observability_abstention_not_available",
                "message": "No abstain_for_observability column supplied.",
            }
        )
    return pd.DataFrame(rows, columns=["warning_code", "message"])


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


def build_failure_taxonomy_report(
    predictions: pd.DataFrame,
    *,
    config: FailureTaxonomyConfig | None = None,
    model_name: str = "failure_taxonomy_model",
    id_columns: tuple[str, ...] = DEFAULT_FAILURE_ID_COLUMNS,
) -> FailureTaxonomyReport:
    cfg = config or FailureTaxonomyConfig()
    rows = build_failure_taxonomy_rows(predictions, config=cfg, id_columns=id_columns)
    summary = summarize_failure_taxonomy(rows, config=cfg)
    patient_summary = summarize_failure_taxonomy_by_patient(rows, config=cfg)
    warnings = _warning_rows(predictions)
    input_hash = _dataframe_hash(predictions)
    rows_hash = _dataframe_hash(rows)
    artifact_hash = _stable_hash(
        {
            "model_name": model_name,
            "config": asdict(cfg),
            "id_columns": list(id_columns),
            "input_hash": input_hash,
            "rows_hash": rows_hash,
        }
    )
    metadata = {
        "model_name": model_name,
        "n_rows": int(len(rows)),
        "n_failure_categories": int(rows["failure_category"].nunique()),
        "input_prediction_hash": input_hash,
        "failure_rows_hash": rows_hash,
        "training_artifact_hash": artifact_hash,
        "result_status": "failure_taxonomy_pre_gate_c_not_citable",
        "taxonomy_status": "post_hoc_descriptive_not_causal",
    }
    manifest = pd.DataFrame([metadata | {"config": asdict(cfg)}])
    return FailureTaxonomyReport(
        rows=rows,
        summary=summary,
        patient_summary=patient_summary,
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


def failure_taxonomy_markdown(
    report: FailureTaxonomyReport,
    *,
    title: str = "Failure Taxonomy Report",
) -> str:
    return f"""# {title}

**Citation status:** not citable as a benchmark result before Gate C.

## Metadata

- Model: `{report.metadata["model_name"]}`
- Rows: `{report.metadata["n_rows"]}`
- Failure categories: `{report.metadata["n_failure_categories"]}`
- Taxonomy status: `{report.metadata["taxonomy_status"]}`
- Artifact hash: `{report.metadata["training_artifact_hash"]}`

## Failure Summary

{_markdown_table(report.summary)}

## Patient Summary

{_markdown_table(report.patient_summary)}

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
