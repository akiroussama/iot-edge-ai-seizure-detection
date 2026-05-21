from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class ConformalCalibration:
    alpha: float
    method: str
    global_radius: float
    global_n: int
    patient_radii: dict[Any, float]
    patient_counts: dict[Any, int]
    min_patient_calibration: int
    score_col: str
    label_col: str
    patient_col: str


@dataclass(frozen=True)
class ConformalReport:
    intervals: pd.DataFrame
    summary: pd.DataFrame
    patient_summary: pd.DataFrame
    metadata: dict[str, Any]


def _valid_mask(df: pd.DataFrame) -> pd.Series:
    return ~df.get("is_excluded", pd.Series(False, index=df.index)).fillna(False).astype(bool)


def _require_columns(df: pd.DataFrame, required: set[str], name: str) -> None:
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"{name} missing required columns: {missing}")


def _validate_alpha(alpha: float) -> float:
    alpha = float(alpha)
    if not 0 < alpha < 1:
        raise ValueError("alpha must be in (0, 1)")
    return alpha


def _residuals(
    df: pd.DataFrame,
    *,
    score_col: str,
    label_col: str,
    name: str,
) -> np.ndarray:
    _require_columns(df, {score_col, label_col}, name)
    valid = _valid_mask(df)
    scores = pd.to_numeric(df.loc[valid, score_col], errors="coerce").clip(0, 1)
    labels = df.loc[valid, label_col].astype(float)
    residuals = (labels - scores).abs().to_numpy(dtype=float)
    residuals = residuals[np.isfinite(residuals)]
    if residuals.size == 0:
        raise ValueError(f"{name} has no valid finite calibration residuals")
    return residuals


def split_conformal_radius(
    calibration_df: pd.DataFrame,
    *,
    alpha: float = 0.1,
    score_col: str = "risk_score",
    label_col: str = "forecast_label",
) -> float:
    """Return the finite-sample split-conformal radius for binary risk scores."""
    alpha = _validate_alpha(alpha)
    residuals = np.sort(
        _residuals(
            calibration_df,
            score_col=score_col,
            label_col=label_col,
            name="calibration_df",
        )
    )
    n = residuals.size
    rank = int(np.ceil((n + 1) * (1.0 - alpha)))
    if rank > n:
        return 1.0
    return float(np.clip(residuals[rank - 1], 0.0, 1.0))


def fit_split_conformal(
    calibration_df: pd.DataFrame,
    *,
    alpha: float = 0.1,
    method: str = "patient",
    patient_col: str = "patient_id",
    score_col: str = "risk_score",
    label_col: str = "forecast_label",
    min_patient_calibration: int = 20,
) -> ConformalCalibration:
    """Fit global or patient-calibrated split-conformal radii."""
    alpha = _validate_alpha(alpha)
    if method not in {"global", "patient"}:
        raise ValueError("method must be 'global' or 'patient'")
    if min_patient_calibration <= 0:
        raise ValueError("min_patient_calibration must be positive")
    _require_columns(calibration_df, {score_col, label_col}, "calibration_df")
    if method == "patient":
        _require_columns(calibration_df, {patient_col}, "calibration_df")

    global_radius = split_conformal_radius(
        calibration_df,
        alpha=alpha,
        score_col=score_col,
        label_col=label_col,
    )
    global_n = int(len(_residuals(calibration_df, score_col=score_col, label_col=label_col, name="calibration_df")))

    patient_radii: dict[Any, float] = {}
    patient_counts: dict[Any, int] = {}
    if method == "patient":
        for patient, group in calibration_df.groupby(patient_col, dropna=False):
            try:
                residuals = _residuals(
                    group,
                    score_col=score_col,
                    label_col=label_col,
                    name=f"calibration_df patient={patient!r}",
                )
            except ValueError:
                continue
            patient_counts[patient] = int(residuals.size)
            if residuals.size >= min_patient_calibration:
                patient_radii[patient] = split_conformal_radius(
                    group,
                    alpha=alpha,
                    score_col=score_col,
                    label_col=label_col,
                )

    return ConformalCalibration(
        alpha=alpha,
        method=method,
        global_radius=global_radius,
        global_n=global_n,
        patient_radii=patient_radii,
        patient_counts=patient_counts,
        min_patient_calibration=int(min_patient_calibration),
        score_col=score_col,
        label_col=label_col,
        patient_col=patient_col,
    )


def _row_radius(row: pd.Series, calibration: ConformalCalibration) -> tuple[float, str, int]:
    if calibration.method == "global":
        return calibration.global_radius, "global", calibration.global_n
    patient = row.get(calibration.patient_col)
    if patient in calibration.patient_radii:
        return (
            calibration.patient_radii[patient],
            "patient_calibrated",
            calibration.patient_counts[patient],
        )
    return (
        calibration.global_radius,
        "global_fallback",
        calibration.patient_counts.get(patient, 0),
    )


def apply_conformal_intervals(
    predictions_df: pd.DataFrame,
    calibration: ConformalCalibration,
) -> pd.DataFrame:
    """Append conformal risk intervals to prediction rows."""
    _require_columns(predictions_df, {calibration.score_col}, "predictions_df")
    if calibration.method == "patient":
        _require_columns(predictions_df, {calibration.patient_col}, "predictions_df")
    out = predictions_df.copy()
    score = pd.to_numeric(out[calibration.score_col], errors="coerce").clip(0, 1)
    if score.isna().any():
        raise ValueError("predictions_df contains non-finite risk scores")

    radii = []
    variants = []
    calibration_counts = []
    for _, row in out.iterrows():
        radius, variant, count = _row_radius(row, calibration)
        radii.append(radius)
        variants.append(variant)
        calibration_counts.append(count)
    radius_series = pd.Series(radii, index=out.index, dtype=float)

    out["conformal_alpha"] = calibration.alpha
    out["conformal_nominal_coverage"] = 1.0 - calibration.alpha
    out["conformal_method"] = calibration.method
    out["conformal_radius"] = radius_series
    out["conformal_variant"] = variants
    out["conformal_calibration_n"] = calibration_counts
    out["risk_lower"] = (score - radius_series).clip(0, 1)
    out["risk_upper"] = (score + radius_series).clip(0, 1)
    out["conformal_interval_width"] = out["risk_upper"] - out["risk_lower"]

    if calibration.label_col in out.columns:
        labels = out[calibration.label_col].astype(float)
        covered = labels.between(out["risk_lower"], out["risk_upper"])
        valid = _valid_mask(out)
        out["label_in_conformal_interval"] = covered.where(valid, pd.NA)
    return out


def conformal_coverage_summary(
    intervals_df: pd.DataFrame,
    *,
    group_cols: tuple[str, ...] = (),
    label_col: str = "forecast_label",
) -> pd.DataFrame:
    """Summarize empirical label coverage for conformal risk intervals."""
    _require_columns(
        intervals_df,
        {"risk_lower", "risk_upper", "conformal_interval_width", label_col},
        "intervals_df",
    )
    valid = intervals_df.loc[_valid_mask(intervals_df)].copy()
    if valid.empty:
        raise ValueError("intervals_df has no valid rows for coverage summary")
    labels = valid[label_col].astype(float)
    valid["label_in_conformal_interval"] = labels.between(valid["risk_lower"], valid["risk_upper"])

    rows = []
    groups = [((), valid)] if not group_cols else valid.groupby(list(group_cols), dropna=False)
    for key, group in groups:
        if not isinstance(key, tuple):
            key = (key,)
        covered = group["label_in_conformal_interval"].astype(bool)
        row = {
            "rows": int(len(group)),
            "covered_rows": int(covered.sum()),
            "empirical_coverage": float(covered.mean()),
            "mean_interval_width": float(group["conformal_interval_width"].mean()),
            "median_interval_width": float(group["conformal_interval_width"].median()),
            "mean_risk_score": float(pd.to_numeric(group["risk_score"], errors="coerce").mean())
            if "risk_score" in group.columns
            else np.nan,
        }
        row.update({column: value for column, value in zip(group_cols, key, strict=True)})
        rows.append(row)
    columns = [
        *group_cols,
        "rows",
        "covered_rows",
        "empirical_coverage",
        "mean_interval_width",
        "median_interval_width",
        "mean_risk_score",
    ]
    return pd.DataFrame(rows, columns=columns)


def build_conformal_report(
    calibration_df: pd.DataFrame,
    evaluation_df: pd.DataFrame,
    *,
    alpha: float = 0.1,
    method: str = "patient",
    patient_col: str = "patient_id",
    score_col: str = "risk_score",
    label_col: str = "forecast_label",
    min_patient_calibration: int = 20,
    result_status: str = "pre_gate_c_exploratory_not_citable",
    citation_status: str = "not_citable_pre_gate_c",
    gate_c_status: str = "not_started",
) -> ConformalReport:
    if citation_status == "citable_after_gate_c" and gate_c_status != "passed":
        raise ValueError("citable conformal reports require gate_c_status='passed'")
    calibration = fit_split_conformal(
        calibration_df,
        alpha=alpha,
        method=method,
        patient_col=patient_col,
        score_col=score_col,
        label_col=label_col,
        min_patient_calibration=min_patient_calibration,
    )
    intervals = apply_conformal_intervals(evaluation_df, calibration)
    summary = conformal_coverage_summary(intervals, label_col=label_col)
    patient_summary = (
        conformal_coverage_summary(intervals, group_cols=(patient_col,), label_col=label_col)
        if patient_col in intervals.columns
        else pd.DataFrame()
    )
    metadata = {
        "alpha": calibration.alpha,
        "nominal_coverage": 1.0 - calibration.alpha,
        "method": calibration.method,
        "global_radius": calibration.global_radius,
        "global_calibration_n": calibration.global_n,
        "patient_calibrated_count": len(calibration.patient_radii),
        "patient_count": len(calibration.patient_counts),
        "min_patient_calibration": calibration.min_patient_calibration,
        "score_col": calibration.score_col,
        "label_col": calibration.label_col,
        "patient_col": calibration.patient_col,
        "result_status": result_status,
        "citation_status": citation_status,
        "gate_c_status": gate_c_status,
    }
    return ConformalReport(
        intervals=intervals,
        summary=summary,
        patient_summary=patient_summary,
        metadata=metadata,
    )


def table_records(df: pd.DataFrame) -> list[dict[str, Any]]:
    records = []
    for record in df.to_dict(orient="records"):
        clean = {}
        for key, value in record.items():
            if isinstance(value, float) and (np.isnan(value) or np.isinf(value)):
                clean[key] = None
            elif isinstance(value, np.integer):
                clean[key] = int(value)
            elif isinstance(value, np.floating):
                clean[key] = float(value)
            else:
                clean[key] = value
        records.append(clean)
    return records
