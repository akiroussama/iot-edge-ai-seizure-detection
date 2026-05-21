from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
from typing import Any

import numpy as np
import pandas as pd

from src.calibration.thresholding import quantile_threshold
from src.utils.time import ensure_datetime


DEFAULT_TTA_ID_COLUMNS = ("patient_id", "recording_id", "window_start", "window_end")
DATETIME_ALIGNMENT_COLUMNS = {"window_start", "window_end", "recording_start", "recording_end"}


@dataclass(frozen=True)
class TestTimeAdaptationConfig:
    __test__ = False

    method: str = "rolling_rank_blend"
    score_col: str = "risk_score"
    patient_col: str = "patient_id"
    time_col: str = "window_start"
    split_col: str = "split"
    threshold_split: str | None = "val"
    target_tiw: float = 0.1
    history_window: int = 48
    min_history: int = 6
    blend_alpha: float = 0.5


@dataclass(frozen=True)
class TestTimeAdaptationReport:
    __test__ = False

    predictions: pd.DataFrame
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


def _validate_config(config: TestTimeAdaptationConfig) -> None:
    if config.method != "rolling_rank_blend":
        raise ValueError("method must be 'rolling_rank_blend'")
    if not 0 <= config.target_tiw <= 1:
        raise ValueError("target_tiw must be in [0, 1]")
    if config.history_window <= 0:
        raise ValueError("history_window must be positive")
    if config.min_history < 0:
        raise ValueError("min_history must be non-negative")
    if not 0 <= config.blend_alpha <= 1:
        raise ValueError("blend_alpha must be in [0, 1]")


def _normalize_table(
    predictions: pd.DataFrame,
    *,
    config: TestTimeAdaptationConfig,
    id_columns: tuple[str, ...],
) -> pd.DataFrame:
    required = {config.score_col, config.patient_col, config.time_col, *id_columns}
    _require_columns(predictions, required, "predictions")
    out = predictions.copy()
    for column in set(id_columns) | {config.time_col}:
        if column in DATETIME_ALIGNMENT_COLUMNS:
            out[column] = ensure_datetime(out[column])
    scores = pd.to_numeric(out[config.score_col], errors="coerce")
    if scores.isna().any():
        raise ValueError(f"{config.score_col} contains non-finite values")
    out[config.score_col] = scores.clip(0.0, 1.0)
    duplicate_mask = out.duplicated(list(id_columns), keep=False)
    if duplicate_mask.any():
        examples = out.loc[duplicate_mask, list(id_columns)].head(3).to_dict(orient="records")
        raise ValueError(f"predictions contains duplicate alignment keys, examples={examples}")
    return out


def _history_rank(value: float, history: list[float]) -> float:
    arr = np.asarray(history, dtype=float)
    below = float(np.sum(arr < value))
    ties = float(np.sum(arr == value))
    return float((below + 0.5 * ties) / max(len(arr), 1))


def _adapt_one_patient(
    group: pd.DataFrame,
    *,
    config: TestTimeAdaptationConfig,
) -> pd.DataFrame:
    ordered = group.sort_values([config.time_col, "index"], kind="mergesort").copy()
    history: list[float] = []
    adapted = []
    history_count = []
    used_history = []
    valid = ~_bool_series(ordered, "is_excluded")
    for row_idx, (_, row) in enumerate(ordered.iterrows()):
        risk = float(row[config.score_col])
        count = len(history)
        if bool(valid.iloc[row_idx]) and count >= config.min_history:
            rank_score = _history_rank(risk, history)
            value = (1.0 - config.blend_alpha) * risk + config.blend_alpha * rank_score
            used = True
        else:
            value = risk
            used = False
        adapted.append(float(np.clip(value, 0.0, 1.0)))
        history_count.append(count)
        used_history.append(used)
        if bool(valid.iloc[row_idx]):
            history.append(risk)
            if len(history) > config.history_window:
                history = history[-config.history_window :]
    ordered["tta_adapted_risk_score"] = adapted
    ordered["tta_history_count"] = history_count
    ordered["tta_used_history"] = used_history
    return ordered.sort_values("index", kind="mergesort")


def _threshold_mask(df: pd.DataFrame, config: TestTimeAdaptationConfig) -> tuple[pd.Series, str]:
    valid = ~_bool_series(df, "is_excluded")
    if config.threshold_split is None or config.split_col not in df.columns:
        return valid, "all_rows"
    split_mask = df[config.split_col].astype(str).eq(str(config.threshold_split))
    mask = valid & split_mask
    if not mask.any():
        raise ValueError(f"threshold split {config.threshold_split!r} has no valid rows")
    return mask, str(config.threshold_split)


def apply_test_time_adaptation(
    predictions: pd.DataFrame,
    *,
    config: TestTimeAdaptationConfig | None = None,
    id_columns: tuple[str, ...] = DEFAULT_TTA_ID_COLUMNS,
) -> pd.DataFrame:
    cfg = config or TestTimeAdaptationConfig()
    _validate_config(cfg)
    normalized = _normalize_table(predictions, config=cfg, id_columns=id_columns)
    working = normalized.reset_index(names="index")
    adapted_chunks = [
        _adapt_one_patient(group, config=cfg)
        for _, group in working.groupby(cfg.patient_col, sort=False)
    ]
    adapted = (
        pd.concat(adapted_chunks, ignore_index=True)
        .sort_values("index", kind="mergesort")
        .drop(columns=["index"])
        .reset_index(drop=True)
    )
    adapted["pre_tta_risk_score"] = normalized[cfg.score_col].to_numpy(dtype=float)
    if "alarm" in adapted.columns:
        adapted["pre_tta_alarm"] = _bool_series(adapted, "alarm")
    threshold_mask, threshold_source = _threshold_mask(adapted, cfg)
    threshold = quantile_threshold(adapted.loc[threshold_mask, "tta_adapted_risk_score"], cfg.target_tiw)
    adapted["risk_score"] = adapted["tta_adapted_risk_score"].astype(float)
    adapted["alarm_threshold"] = float(threshold)
    adapted["alarm"] = adapted["risk_score"].ge(threshold) & ~_bool_series(adapted, "is_excluded")
    adapted["tta_method"] = cfg.method
    adapted["tta_history_window"] = int(cfg.history_window)
    adapted["tta_min_history"] = int(cfg.min_history)
    adapted["tta_blend_alpha"] = float(cfg.blend_alpha)
    adapted["tta_threshold_source_split"] = threshold_source
    adapted["tta_leakage_status"] = "rolling_origin_past_unlabeled_scores_only"
    return adapted


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

    encoded = json.dumps(_jsonable(payload), sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )
    return sha256(encoded).hexdigest()


def _dataframe_hash(df: pd.DataFrame) -> str:
    normalized = df.copy()
    for column in normalized.columns:
        if column in DATETIME_ALIGNMENT_COLUMNS:
            normalized[column] = ensure_datetime(normalized[column]).astype(str)
    return sha256(normalized.to_csv(index=False).encode("utf-8")).hexdigest()


def summarize_test_time_adaptation(
    adapted: pd.DataFrame,
    *,
    config: TestTimeAdaptationConfig,
) -> pd.DataFrame:
    valid = ~_bool_series(adapted, "is_excluded")
    grouped = adapted.groupby(config.patient_col, dropna=False)
    rows = []
    for patient, group in grouped:
        group_valid = valid.loc[group.index]
        delta = pd.to_numeric(group["risk_score"], errors="coerce") - pd.to_numeric(
            group["pre_tta_risk_score"],
            errors="coerce",
        )
        rows.append(
            {
                "patient_id": patient,
                "rows": int(len(group)),
                "valid_rows": int(group_valid.sum()),
                "tta_used_rows": int(group["tta_used_history"].fillna(False).astype(bool).sum()),
                "mean_pre_tta_risk_score": float(group.loc[group_valid, "pre_tta_risk_score"].mean()),
                "mean_tta_risk_score": float(group.loc[group_valid, "risk_score"].mean()),
                "mean_abs_tta_delta": float(delta.loc[group_valid].abs().mean()),
                "max_abs_tta_delta": float(delta.loc[group_valid].abs().max()),
                "alarm_rows": int(group.loc[group_valid, "alarm"].fillna(False).astype(bool).sum()),
            }
        )
    return pd.DataFrame(rows)


def build_test_time_adaptation_report(
    predictions: pd.DataFrame,
    *,
    config: TestTimeAdaptationConfig | None = None,
    model_name: str = "test_time_adapted_model",
    id_columns: tuple[str, ...] = DEFAULT_TTA_ID_COLUMNS,
) -> TestTimeAdaptationReport:
    cfg = config or TestTimeAdaptationConfig()
    adapted = apply_test_time_adaptation(predictions, config=cfg, id_columns=id_columns)
    summary = summarize_test_time_adaptation(adapted, config=cfg)
    input_hash = _dataframe_hash(predictions)
    output_hash = _dataframe_hash(adapted)
    artifact_hash = _stable_hash(
        {
            "model_name": model_name,
            "config": asdict(cfg),
            "id_columns": list(id_columns),
            "input_hash": input_hash,
            "output_hash": output_hash,
        }
    )
    metadata = {
        "model_name": model_name,
        "method": cfg.method,
        "id_columns": list(id_columns),
        "n_rows": int(len(adapted)),
        "n_patients": int(adapted[cfg.patient_col].nunique()),
        "tta_used_rows": int(adapted["tta_used_history"].fillna(False).astype(bool).sum()),
        "target_tiw": float(cfg.target_tiw),
        "threshold_source_split": str(adapted["tta_threshold_source_split"].iloc[0]),
        "alarm_threshold": float(adapted["alarm_threshold"].iloc[0]),
        "input_prediction_hash": input_hash,
        "output_prediction_hash": output_hash,
        "training_artifact_hash": artifact_hash,
        "result_status": "test_time_adaptation_pre_gate_c_not_citable",
        "leakage_status": "rolling_origin_past_unlabeled_scores_only",
    }
    manifest = pd.DataFrame([metadata | {"config": asdict(cfg)}])
    return TestTimeAdaptationReport(
        predictions=adapted,
        summary=summary,
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


def test_time_adaptation_markdown(
    report: TestTimeAdaptationReport,
    *,
    title: str = "Test-Time Adaptation Report",
) -> str:
    return f"""# {title}

**Citation status:** not citable as a benchmark result before Gate C.

## Metadata

- Model: `{report.metadata["model_name"]}`
- Method: `{report.metadata["method"]}`
- Rows: `{report.metadata["n_rows"]}`
- Patients: `{report.metadata["n_patients"]}`
- TTA-used rows: `{report.metadata["tta_used_rows"]}`
- Leakage status: `{report.metadata["leakage_status"]}`
- Result status: `{report.metadata["result_status"]}`
- Artifact hash: `{report.metadata["training_artifact_hash"]}`

## Per-Patient Summary

{_markdown_table(report.summary)}
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
