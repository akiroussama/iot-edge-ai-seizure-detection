from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from src.metrics.calibration import (
    brier_score,
    brier_skill_score,
    expected_calibration_error,
    reliability_table,
)

DEFAULT_ID_COLUMNS = ("patient_id", "recording_id", "window_start", "window_end")


@dataclass(frozen=True)
class CalibrationSkillReport:
    summary: pd.DataFrame
    skill: pd.DataFrame
    reliability: pd.DataFrame
    bootstrap: pd.DataFrame
    metadata: dict[str, Any]


def _valid_mask(df: pd.DataFrame) -> pd.Series:
    return ~df.get("is_excluded", pd.Series(False, index=df.index)).fillna(False).astype(bool)


def _required_prediction_columns(df: pd.DataFrame, name: str) -> None:
    missing = sorted({"risk_score", "forecast_label"} - set(df.columns))
    if missing:
        raise ValueError(f"{name} missing required prediction columns: {missing}")


def _indexed(df: pd.DataFrame, id_columns: tuple[str, ...], name: str) -> pd.DataFrame:
    missing = [col for col in id_columns if col not in df.columns]
    if missing:
        raise ValueError(f"{name} missing alignment columns: {missing}")
    duplicated = df.duplicated(list(id_columns), keep=False)
    if duplicated.any():
        example = df.loc[duplicated, list(id_columns)].head(3).to_dict(orient="records")
        raise ValueError(f"{name} contains duplicate alignment keys, examples={example}")
    return df.set_index(list(id_columns), drop=False)


def align_reference_predictions(
    predictions: pd.DataFrame,
    reference_predictions: pd.DataFrame,
    *,
    id_columns: tuple[str, ...] = DEFAULT_ID_COLUMNS,
    reference_name: str = "reference",
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return model/reference predictions aligned by identity columns.

    The function fails closed on missing rows or label/exclusion mismatches.
    BSS is only meaningful when model and null predictions score the same
    forecast windows.
    """
    _required_prediction_columns(predictions, "predictions")
    _required_prediction_columns(reference_predictions, reference_name)
    model = _indexed(predictions, id_columns, "predictions")
    reference = _indexed(reference_predictions, id_columns, reference_name)

    model_keys = set(model.index)
    reference_keys = set(reference.index)
    missing_from_reference = model_keys - reference_keys
    extra_in_reference = reference_keys - model_keys
    if missing_from_reference or extra_in_reference:
        raise ValueError(
            f"{reference_name} row mismatch: "
            f"missing_reference_rows={len(missing_from_reference)}, "
            f"extra_reference_rows={len(extra_in_reference)}"
        )

    reference = reference.loc[model.index]
    for col in ("forecast_label", "is_excluded"):
        if col in model.columns and col in reference.columns:
            model_values = model[col].fillna(False).astype(bool)
            reference_values = reference[col].fillna(False).astype(bool)
            if not model_values.equals(reference_values):
                raise ValueError(f"{reference_name} column {col!r} does not match predictions")

    return model.reset_index(drop=True), reference.reset_index(drop=True)


def align_reference_set(
    predictions: pd.DataFrame,
    references: dict[str, pd.DataFrame],
    *,
    id_columns: tuple[str, ...] = DEFAULT_ID_COLUMNS,
) -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    aligned_model = predictions.copy().reset_index(drop=True)
    aligned_references: dict[str, pd.DataFrame] = {}
    for reference_name, reference in references.items():
        aligned_model, aligned_reference = align_reference_predictions(
            aligned_model,
            reference,
            id_columns=id_columns,
            reference_name=reference_name,
        )
        aligned_references[reference_name] = aligned_reference
    return aligned_model, aligned_references


def _series_summary(df: pd.DataFrame, *, series_name: str, series_role: str, n_bins: int) -> dict[str, Any]:
    _required_prediction_columns(df, series_name)
    valid = df.loc[_valid_mask(df)]
    if valid.empty:
        raise ValueError(f"{series_name} has no valid non-excluded prediction rows")
    y = valid["forecast_label"].fillna(False).astype(bool)
    risk = valid["risk_score"].astype(float).clip(0, 1)
    return {
        "series_name": series_name,
        "series_role": series_role,
        "prediction_rows": int(len(df)),
        "valid_prediction_rows": int(len(valid)),
        "positive_windows": int(y.sum()),
        "empirical_rate": float(y.mean()),
        "mean_risk_score": float(risk.mean()),
        "brier_score": brier_score(df),
        "expected_calibration_error": expected_calibration_error(df, n_bins=n_bins),
    }


def build_summary_table(
    predictions: pd.DataFrame,
    references: dict[str, pd.DataFrame],
    *,
    model_name: str,
    n_bins: int = 10,
) -> pd.DataFrame:
    rows = [_series_summary(predictions, series_name=model_name, series_role="model", n_bins=n_bins)]
    rows.extend(
        _series_summary(reference, series_name=name, series_role="reference", n_bins=n_bins)
        for name, reference in references.items()
    )
    return pd.DataFrame(rows)


def build_skill_table(
    predictions: pd.DataFrame,
    references: dict[str, pd.DataFrame],
    *,
    model_name: str,
    n_bins: int = 10,
) -> pd.DataFrame:
    model_brier = brier_score(predictions)
    model_ece = expected_calibration_error(predictions, n_bins=n_bins)
    rows = []
    for reference_name, reference in references.items():
        reference_brier = brier_score(reference)
        rows.append(
            {
                "model_name": model_name,
                "reference_name": reference_name,
                "model_brier_score": model_brier,
                "reference_brier_score": reference_brier,
                "brier_skill_score": brier_skill_score(predictions, reference),
                "model_expected_calibration_error": model_ece,
                "reference_expected_calibration_error": expected_calibration_error(
                    reference,
                    n_bins=n_bins,
                ),
                "valid_prediction_rows": int(_valid_mask(predictions).sum()),
            }
        )
    return pd.DataFrame(rows)


def build_reliability_tables(
    predictions: pd.DataFrame,
    references: dict[str, pd.DataFrame],
    *,
    model_name: str,
    n_bins: int = 10,
) -> pd.DataFrame:
    frames = []
    for series_name, series_role, df in [(model_name, "model", predictions)] + [
        (name, "reference", reference) for name, reference in references.items()
    ]:
        table = reliability_table(df, n_bins=n_bins).copy()
        table.insert(0, "series_role", series_role)
        table.insert(0, "series_name", series_name)
        frames.append(table)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def _group_positions(df: pd.DataFrame, group_col: str, scope: str) -> dict[Any, np.ndarray]:
    if group_col not in df.columns:
        raise ValueError(f"{scope} bootstrap requested but group column {group_col!r} is missing")
    valid = _valid_mask(df)
    groups = df.loc[valid, group_col].dropna().unique().tolist()
    if not groups:
        raise ValueError(f"{scope} bootstrap has no valid groups in column {group_col!r}")
    return {group: np.flatnonzero(valid.to_numpy() & df[group_col].eq(group).to_numpy()) for group in groups}


def _bootstrap_indices(
    positions_by_group: dict[Any, np.ndarray],
    rng: np.random.Generator,
) -> np.ndarray:
    groups = list(positions_by_group)
    sampled_groups = rng.choice(groups, size=len(groups), replace=True)
    return np.concatenate([positions_by_group[group] for group in sampled_groups])


def bootstrap_skill_intervals(
    predictions: pd.DataFrame,
    references: dict[str, pd.DataFrame],
    *,
    scope: str,
    group_col: str,
    n_bootstrap: int = 1000,
    seed: int = 42,
    ci: float = 0.95,
) -> pd.DataFrame:
    if n_bootstrap <= 0:
        raise ValueError("n_bootstrap must be positive")
    positions_by_group = _group_positions(predictions, group_col, scope)
    rng = np.random.default_rng(seed)
    alpha = (1.0 - ci) / 2.0
    rows = []
    for reference_name, reference in references.items():
        values = []
        for _ in range(n_bootstrap):
            idx = _bootstrap_indices(positions_by_group, rng)
            values.append(brier_skill_score(predictions.iloc[idx], reference.iloc[idx]))
        arr = np.asarray(values, dtype=float)
        rows.append(
            {
                "scope": scope,
                "group_col": group_col,
                "reference_name": reference_name,
                "metric": "brier_skill_score",
                "n_groups": int(len(positions_by_group)),
                "n_bootstrap": int(n_bootstrap),
                "mean": float(np.mean(arr)),
                "ci_low": float(np.quantile(arr, alpha)),
                "ci_high": float(np.quantile(arr, 1.0 - alpha)),
            }
        )
    return pd.DataFrame(rows)


def build_bootstrap_table(
    predictions: pd.DataFrame,
    references: dict[str, pd.DataFrame],
    *,
    patient_col: str | None = "patient_id",
    event_col: str | None = "event_id",
    n_bootstrap: int = 1000,
    seed: int = 42,
) -> pd.DataFrame:
    frames = []
    if patient_col is not None:
        frames.append(
            bootstrap_skill_intervals(
                predictions,
                references,
                scope="patient",
                group_col=patient_col,
                n_bootstrap=n_bootstrap,
                seed=seed,
            )
        )
    if event_col is not None:
        frames.append(
            bootstrap_skill_intervals(
                predictions,
                references,
                scope="event",
                group_col=event_col,
                n_bootstrap=n_bootstrap,
                seed=seed + 1,
            )
        )
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def build_calibration_skill_report(
    predictions: pd.DataFrame,
    references: dict[str, pd.DataFrame],
    *,
    model_name: str,
    id_columns: tuple[str, ...] = DEFAULT_ID_COLUMNS,
    n_bins: int = 10,
    n_bootstrap: int = 1000,
    seed: int = 42,
    patient_col: str | None = "patient_id",
    event_col: str | None = "event_id",
    result_status: str = "pre_gate_c_exploratory_not_citable",
    citation_status: str = "not_citable_pre_gate_c",
    gate_c_status: str = "not_started",
) -> CalibrationSkillReport:
    if not references:
        raise ValueError("at least one reference prediction table is required")
    if citation_status == "citable_after_gate_c" and gate_c_status != "passed":
        raise ValueError("citable calibration reports require gate_c_status='passed'")
    aligned_predictions, aligned_references = align_reference_set(
        predictions,
        references,
        id_columns=id_columns,
    )
    metadata = {
        "model_name": model_name,
        "reference_names": list(aligned_references),
        "id_columns": list(id_columns),
        "n_bins": int(n_bins),
        "n_bootstrap": int(n_bootstrap),
        "seed": int(seed),
        "patient_col": patient_col,
        "event_col": event_col,
        "result_status": result_status,
        "citation_status": citation_status,
        "gate_c_status": gate_c_status,
    }
    return CalibrationSkillReport(
        summary=build_summary_table(
            aligned_predictions,
            aligned_references,
            model_name=model_name,
            n_bins=n_bins,
        ),
        skill=build_skill_table(
            aligned_predictions,
            aligned_references,
            model_name=model_name,
            n_bins=n_bins,
        ),
        reliability=build_reliability_tables(
            aligned_predictions,
            aligned_references,
            model_name=model_name,
            n_bins=n_bins,
        ),
        bootstrap=build_bootstrap_table(
            aligned_predictions,
            aligned_references,
            patient_col=patient_col,
            event_col=event_col,
            n_bootstrap=n_bootstrap,
            seed=seed,
        ),
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
