from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
from typing import Any

import numpy as np
import pandas as pd

from src.utils.time import ensure_datetime


@dataclass(frozen=True)
class LongitudinalDeepDiveConfig:
    patient_id: str | None = None
    patient_col: str = "patient_id"
    time_col: str = "window_start"
    risk_col: str = "risk_score"
    alarm_col: str = "alarm"
    label_col: str = "forecast_label"
    excluded_col: str = "is_excluded"
    segments: int = 6
    event_neighborhood_rows: int = 3


@dataclass(frozen=True)
class LongitudinalDeepDiveReport:
    patient_selection: pd.DataFrame
    timeline: pd.DataFrame
    segment_summary: pd.DataFrame
    event_neighborhoods: pd.DataFrame
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


def _validate_config(config: LongitudinalDeepDiveConfig) -> None:
    if config.segments <= 0:
        raise ValueError("segments must be positive")
    if config.event_neighborhood_rows < 0:
        raise ValueError("event_neighborhood_rows must be non-negative")


def _prepare_predictions(
    predictions: pd.DataFrame,
    *,
    config: LongitudinalDeepDiveConfig,
) -> pd.DataFrame:
    _require_columns(
        predictions,
        {
            config.patient_col,
            config.time_col,
            config.risk_col,
            config.alarm_col,
            config.label_col,
            config.excluded_col,
        },
        "predictions",
    )
    out = predictions.copy()
    out[config.time_col] = ensure_datetime(out[config.time_col])
    risk = pd.to_numeric(out[config.risk_col], errors="coerce")
    if risk.isna().any():
        raise ValueError(f"{config.risk_col} contains non-finite values")
    out[config.risk_col] = risk.clip(0.0, 1.0)
    out[config.alarm_col] = _bool_series(out, config.alarm_col)
    out[config.label_col] = _bool_series(out, config.label_col)
    out[config.excluded_col] = _bool_series(out, config.excluded_col)
    return out.sort_values([config.patient_col, config.time_col], kind="mergesort").reset_index(drop=True)


def patient_selection_table(
    predictions: pd.DataFrame,
    *,
    config: LongitudinalDeepDiveConfig,
) -> pd.DataFrame:
    rows = []
    for patient, group in predictions.groupby(config.patient_col, dropna=False):
        valid = ~_bool_series(group, config.excluded_col)
        positives = _bool_series(group, config.label_col) & valid
        alarms = _bool_series(group, config.alarm_col) & valid
        start = group[config.time_col].min()
        end = group[config.time_col].max()
        duration_hours = (end - start).total_seconds() / 3600.0 if pd.notna(start) and pd.notna(end) else 0.0
        rows.append(
            {
                "patient_id": patient,
                "rows": int(len(group)),
                "valid_rows": int(valid.sum()),
                "positive_rows": int(positives.sum()),
                "alarm_rows": int(alarms.sum()),
                "start_time": start,
                "end_time": end,
                "duration_hours": float(duration_hours),
                "mean_risk_score": float(group.loc[valid, config.risk_col].mean()) if valid.any() else np.nan,
                "selection_score": float(duration_hours + 10.0 * positives.sum() + alarms.sum()),
            }
        )
    return pd.DataFrame(rows).sort_values(
        ["selection_score", "duration_hours", "positive_rows"],
        ascending=[False, False, False],
    ).reset_index(drop=True)


def _select_patient(selection: pd.DataFrame, requested: str | None) -> str:
    if selection.empty:
        raise ValueError("no patients available for longitudinal deep dive")
    if requested is None:
        return str(selection.loc[0, "patient_id"])
    if requested not in set(selection["patient_id"].astype(str)):
        raise ValueError(f"requested patient_id {requested!r} not found")
    return requested


def _timeline_table(patient_rows: pd.DataFrame, *, config: LongitudinalDeepDiveConfig) -> pd.DataFrame:
    timeline = patient_rows.copy().reset_index(drop=True)
    timeline["longitudinal_index"] = np.arange(len(timeline), dtype=int)
    valid = ~_bool_series(timeline, config.excluded_col)
    timeline["valid_for_clinical_metrics"] = valid
    risk = pd.to_numeric(timeline[config.risk_col], errors="coerce")
    timeline["risk_delta_from_previous"] = risk.diff().fillna(0.0)
    timeline["rolling_mean_risk_12"] = risk.rolling(12, min_periods=1).mean()
    if "failure_category" not in timeline.columns:
        timeline["failure_category"] = "not_available"
    if "is_observable" not in timeline.columns:
        timeline["is_observable"] = pd.NA
    return timeline


def _segment_summary(timeline: pd.DataFrame, *, config: LongitudinalDeepDiveConfig) -> pd.DataFrame:
    if timeline.empty:
        return pd.DataFrame()
    n_segments = min(config.segments, len(timeline))
    segment_id = pd.cut(
        timeline["longitudinal_index"],
        bins=n_segments,
        labels=False,
        include_lowest=True,
    )
    timeline = timeline.assign(longitudinal_segment=segment_id.astype(int))
    rows = []
    for segment, group in timeline.groupby("longitudinal_segment", dropna=False):
        valid = group["valid_for_clinical_metrics"].fillna(False).astype(bool)
        labels = _bool_series(group, config.label_col)
        alarms = _bool_series(group, config.alarm_col)
        risks = pd.to_numeric(group[config.risk_col], errors="coerce")
        rows.append(
            {
                "longitudinal_segment": int(segment),
                "rows": int(len(group)),
                "valid_rows": int(valid.sum()),
                "positive_rows": int((labels & valid).sum()),
                "alarm_rows": int((alarms & valid).sum()),
                "mean_risk_score": float(risks.loc[valid].mean()) if valid.any() else np.nan,
                "max_risk_score": float(risks.loc[valid].max()) if valid.any() else np.nan,
                "mean_abs_risk_delta": float(group["risk_delta_from_previous"].abs().mean()),
                "top_failure_category": str(group["failure_category"].mode().iloc[0]),
            }
        )
    return pd.DataFrame(rows)


def _event_neighborhoods(timeline: pd.DataFrame, *, config: LongitudinalDeepDiveConfig) -> pd.DataFrame:
    labels = _bool_series(timeline, config.label_col)
    event_indices = timeline.index[labels].tolist()
    rows = []
    radius = config.event_neighborhood_rows
    for event_number, event_idx in enumerate(event_indices, start=1):
        start = max(0, event_idx - radius)
        end = min(len(timeline) - 1, event_idx + radius)
        for idx in range(start, end + 1):
            row = timeline.loc[idx]
            rows.append(
                {
                    "event_number": event_number,
                    "event_longitudinal_index": int(event_idx),
                    "relative_row": int(idx - event_idx),
                    config.time_col: row[config.time_col],
                    config.risk_col: float(row[config.risk_col]),
                    config.alarm_col: bool(row[config.alarm_col]),
                    config.label_col: bool(row[config.label_col]),
                    "failure_category": row["failure_category"],
                    "risk_delta_from_previous": float(row["risk_delta_from_previous"]),
                }
            )
    return pd.DataFrame(rows)


def _jsonable(value: Any) -> Any:
    if isinstance(value, (pd.Timestamp,)):
        return value.isoformat()
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
    normalized = df.copy()
    for column in normalized.columns:
        if pd.api.types.is_datetime64_any_dtype(normalized[column]):
            normalized[column] = normalized[column].astype(str)
    return sha256(normalized.to_csv(index=False).encode("utf-8")).hexdigest()


def build_longitudinal_deep_dive_report(
    predictions: pd.DataFrame,
    *,
    config: LongitudinalDeepDiveConfig | None = None,
    report_name: str = "n1_longitudinal_deep_dive",
) -> LongitudinalDeepDiveReport:
    cfg = config or LongitudinalDeepDiveConfig()
    _validate_config(cfg)
    prepared = _prepare_predictions(predictions, config=cfg)
    selection = patient_selection_table(prepared, config=cfg)
    selected_patient = _select_patient(selection, cfg.patient_id)
    patient_rows = prepared.loc[prepared[cfg.patient_col].astype(str).eq(selected_patient)].copy()
    timeline = _timeline_table(patient_rows, config=cfg)
    segments = _segment_summary(timeline, config=cfg)
    neighborhoods = _event_neighborhoods(timeline, config=cfg)
    input_hash = _dataframe_hash(prepared)
    timeline_hash = _dataframe_hash(timeline)
    artifact_hash = _stable_hash(
        {
            "report_name": report_name,
            "config": asdict(cfg),
            "selected_patient": selected_patient,
            "input_hash": input_hash,
            "timeline_hash": timeline_hash,
        }
    )
    metadata = {
        "report_name": report_name,
        "selected_patient_id": selected_patient,
        "n_patients": int(selection["patient_id"].nunique()),
        "patient_rows": int(len(timeline)),
        "patient_positive_rows": int(_bool_series(timeline, cfg.label_col).sum()),
        "patient_alarm_rows": int(_bool_series(timeline, cfg.alarm_col).sum()),
        "input_prediction_hash": input_hash,
        "timeline_hash": timeline_hash,
        "training_artifact_hash": artifact_hash,
        "result_status": "n1_longitudinal_deep_dive_pre_gate_c_not_citable",
        "analysis_status": "descriptive_single_patient_not_generalizable",
    }
    manifest = pd.DataFrame([metadata | {"config": asdict(cfg)}])
    return LongitudinalDeepDiveReport(
        patient_selection=selection,
        timeline=timeline,
        segment_summary=segments,
        event_neighborhoods=neighborhoods,
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


def longitudinal_deep_dive_markdown(
    report: LongitudinalDeepDiveReport,
    *,
    title: str = "N=1 Longitudinal Deep Dive",
) -> str:
    return f"""# {title}

**Citation status:** not citable as a benchmark result before Gate C.

## Metadata

- Report: `{report.metadata["report_name"]}`
- Selected patient: `{report.metadata["selected_patient_id"]}`
- Patient rows: `{report.metadata["patient_rows"]}`
- Positive rows: `{report.metadata["patient_positive_rows"]}`
- Alarm rows: `{report.metadata["patient_alarm_rows"]}`
- Analysis status: `{report.metadata["analysis_status"]}`
- Artifact hash: `{report.metadata["training_artifact_hash"]}`

## Patient Selection

{_markdown_table(report.patient_selection)}

## Segment Summary

{_markdown_table(report.segment_summary)}

## Event Neighborhoods

{_markdown_table(report.event_neighborhoods)}
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
