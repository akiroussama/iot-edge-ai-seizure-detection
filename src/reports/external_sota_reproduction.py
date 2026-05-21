from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import numpy as np
import pandas as pd

from src.utils.time import ensure_datetime

REPRODUCTION_STATUSES = {
    "recomputed_under_epitwin_runner",
    "adapter_smoke_test_not_sota_claim",
    "blocked_modality_or_split_mismatch",
    "external_reported_not_recomputed",
}


@dataclass(frozen=True)
class ExternalSOTAReference:
    source_name: str
    source_citation: str
    source_url: str | None
    source_doi: str | None
    reproduction_family: str
    reproduction_status: str
    mismatch_notes: str
    source_code_uri: str | None = None
    original_metric_summary: str | None = None
    license_notes: str | None = None


@dataclass(frozen=True)
class ExternalPredictionColumns:
    patient_col: str = "patient_id"
    recording_col: str = "recording_id"
    window_start_col: str = "window_start"
    window_end_col: str = "window_end"
    risk_col: str = "risk_score"
    alarm_col: str | None = "alarm"
    label_col: str = "forecast_label"
    excluded_col: str | None = "is_excluded"
    split_col: str | None = "split"


def _require_columns(df: pd.DataFrame, required: set[str], name: str) -> None:
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"{name} missing required columns: {missing}")


def _require_nonempty(value: str | None, name: str) -> str:
    if value is None or not str(value).strip():
        raise ValueError(f"{name} must be provided")
    return str(value).strip()


def validate_external_sota_reference(reference: ExternalSOTAReference) -> None:
    _require_nonempty(reference.source_name, "source_name")
    _require_nonempty(reference.source_citation, "source_citation")
    _require_nonempty(reference.reproduction_family, "reproduction_family")
    _require_nonempty(reference.mismatch_notes, "mismatch_notes")
    if reference.reproduction_status not in REPRODUCTION_STATUSES:
        raise ValueError(
            "reproduction_status must be one of "
            f"{sorted(REPRODUCTION_STATUSES)}, got {reference.reproduction_status!r}"
        )
    if not reference.source_url and not reference.source_doi:
        raise ValueError("at least one of source_url or source_doi must be provided")
    if reference.reproduction_status == "recomputed_under_epitwin_runner":
        if "unknown" in reference.mismatch_notes.lower():
            raise ValueError("recomputed reproductions need explicit, not unknown, mismatch notes")


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


def standardize_external_predictions(
    predictions: pd.DataFrame,
    *,
    columns: ExternalPredictionColumns | None = None,
    alarm_threshold: float | None = None,
) -> pd.DataFrame:
    """Normalize an external model's predictions to the EpiTwin leaderboard contract."""
    cols = columns or ExternalPredictionColumns()
    required = {
        cols.patient_col,
        cols.recording_col,
        cols.window_start_col,
        cols.window_end_col,
        cols.risk_col,
        cols.label_col,
    }
    if cols.alarm_col is not None:
        required.add(cols.alarm_col)
    elif alarm_threshold is None:
        raise ValueError("alarm_threshold is required when alarm_col is not provided")
    if cols.excluded_col is not None:
        required.add(cols.excluded_col)
    if cols.split_col is not None:
        required.add(cols.split_col)
    _require_columns(predictions, required, "external predictions")
    if alarm_threshold is not None and not 0 <= alarm_threshold <= 1:
        raise ValueError("alarm_threshold must be in [0, 1]")

    risk = pd.to_numeric(predictions[cols.risk_col], errors="coerce")
    if risk.isna().any():
        raise ValueError(f"{cols.risk_col} contains non-finite risk scores")
    clipped = risk.clip(0.0, 1.0)
    out = pd.DataFrame(
        {
            "patient_id": predictions[cols.patient_col].astype(str),
            "recording_id": predictions[cols.recording_col].astype(str),
            "window_start": ensure_datetime(predictions[cols.window_start_col]),
            "window_end": ensure_datetime(predictions[cols.window_end_col]),
            "risk_score": clipped.astype(float),
            "forecast_label": _bool_series(predictions, cols.label_col),
            "is_excluded": _bool_series(predictions, cols.excluded_col)
            if cols.excluded_col is not None
            else False,
            "external_sota_risk_was_clipped": risk.ne(clipped),
        }
    )
    if cols.alarm_col is not None:
        out["alarm"] = _bool_series(predictions, cols.alarm_col)
        out["external_sota_alarm_source"] = cols.alarm_col
    else:
        out["alarm"] = clipped.ge(float(alarm_threshold))
        out["external_sota_alarm_source"] = f"threshold_{alarm_threshold:g}"
    if cols.split_col is not None:
        out["split"] = predictions[cols.split_col].astype(str)

    used_source = {
        cols.patient_col,
        cols.recording_col,
        cols.window_start_col,
        cols.window_end_col,
        cols.risk_col,
        cols.label_col,
        cols.alarm_col,
        cols.excluded_col,
        cols.split_col,
    }
    used_source.discard(None)
    passthrough = [
        column
        for column in predictions.columns
        if column not in used_source and column not in out.columns
    ]
    for column in passthrough:
        out[column] = predictions[column]
    return out.sort_values(["patient_id", "recording_id", "window_start"], kind="mergesort").reset_index(
        drop=True
    )


def _valid_mask(predictions: pd.DataFrame) -> pd.Series:
    return ~predictions.get("is_excluded", pd.Series(False, index=predictions.index)).fillna(False).astype(bool)


def _clean(value: Any) -> Any:
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        value = float(value)
    if isinstance(value, float) and (np.isnan(value) or np.isinf(value)):
        return None
    if value is pd.NA or value is pd.NaT:
        return None
    return value


def build_external_sota_manifest(
    *,
    reference: ExternalSOTAReference,
    standardized_predictions: pd.DataFrame,
    leaderboard_row: dict[str, Any],
) -> pd.DataFrame:
    validate_external_sota_reference(reference)
    _require_columns(
        standardized_predictions,
        {"risk_score", "alarm", "forecast_label", "is_excluded"},
        "standardized_predictions",
    )
    valid = _valid_mask(standardized_predictions)
    computed_metrics = {
        "leaderboard_result_id": leaderboard_row.get("result_id"),
        "leaderboard_result_status": leaderboard_row.get("result_status"),
        "leaderboard_citation_status": leaderboard_row.get("citation_status"),
        "dataset": leaderboard_row.get("dataset"),
        "task_type": leaderboard_row.get("task_type"),
        "model_name": leaderboard_row.get("model_name"),
        "split_name": leaderboard_row.get("split_name"),
        "horizon_name": leaderboard_row.get("horizon_name"),
        "sensitivity": leaderboard_row.get("sensitivity"),
        "false_alarm_rate_per_day": leaderboard_row.get("false_alarm_rate_per_day"),
        "time_in_warning": leaderboard_row.get("time_in_warning"),
        "brier_score": leaderboard_row.get("brier_score"),
        "brier_skill_score": leaderboard_row.get("brier_skill_score"),
        "auroc": leaderboard_row.get("auroc"),
        "auprc": leaderboard_row.get("auprc"),
    }
    row = {
        **asdict(reference),
        "prediction_rows": int(len(standardized_predictions)),
        "valid_prediction_rows": int(valid.sum()),
        "positive_windows": int(standardized_predictions.loc[valid, "forecast_label"].sum()),
        "alarm_rows": int(standardized_predictions.loc[valid, "alarm"].sum()),
        "risk_clipped_rows": int(
            standardized_predictions.get(
                "external_sota_risk_was_clipped",
                pd.Series(False, index=standardized_predictions.index),
            )
            .fillna(False)
            .astype(bool)
            .sum()
        ),
        "analysis_status": "external_sota_reproduction_adapter",
        "sota_claim_status": "not_a_sota_claim_until_gate_c_and_faithful_reproduction",
        **computed_metrics,
    }
    return pd.DataFrame([{key: _clean(value) for key, value in row.items()}])


def external_sota_reproduction_markdown(
    manifest: pd.DataFrame,
    *,
    title: str = "External SOTA Reproduction Dossier",
) -> str:
    if manifest.empty:
        raise ValueError("manifest must contain one row")
    row = manifest.iloc[0]
    warning = ""
    if row.get("leaderboard_citation_status") != "citable_after_gate_c":
        warning = "\n**Citation status:** not citable as a benchmark comparison before Gate C.\n"
    metric_lines = [
        f"- Sensitivity: `{row.get('sensitivity')}`",
        f"- FAR/day: `{row.get('false_alarm_rate_per_day')}`",
        f"- TIW: `{row.get('time_in_warning')}`",
        f"- Brier score: `{row.get('brier_score')}`",
        f"- BSS: `{row.get('brier_skill_score')}`",
        f"- AUROC: `{row.get('auroc')}`",
        f"- AUPRC: `{row.get('auprc')}`",
    ]
    return "\n".join(
        [
            f"# {title}",
            warning,
            "This dossier records a reproducibility bridge, not a superiority claim.",
            "",
            "## Source",
            "",
            f"- Name: `{row.get('source_name')}`",
            f"- Citation: {row.get('source_citation')}",
            f"- DOI: `{row.get('source_doi')}`",
            f"- URL: `{row.get('source_url')}`",
            f"- Source code: `{row.get('source_code_uri')}`",
            f"- Family: `{row.get('reproduction_family')}`",
            f"- Status: `{row.get('reproduction_status')}`",
            "",
            "## Mismatch Notes",
            "",
            str(row.get("mismatch_notes")),
            "",
            "## Standardized Output",
            "",
            f"- Leaderboard result: `{row.get('leaderboard_result_id')}`",
            f"- Dataset: `{row.get('dataset')}`",
            f"- Task type: `{row.get('task_type')}`",
            f"- Model: `{row.get('model_name')}`",
            f"- Prediction rows: `{row.get('prediction_rows')}`",
            f"- Valid prediction rows: `{row.get('valid_prediction_rows')}`",
            f"- Risk-clipped rows: `{row.get('risk_clipped_rows')}`",
            "",
            "## Metrics Under EpiTwin Runner",
            "",
            *metric_lines,
            "",
            "## Guardrails",
            "",
            "- Detection, early-warning, and forecasting tasks must stay separated.",
            "- External reported metrics are context unless recomputed from row-level predictions.",
            "- Gate C frozen artifacts are required before citable benchmark comparison.",
            "- Any modality, split, label, or horizon mismatch must remain visible in this dossier.",
            "",
        ]
    )
