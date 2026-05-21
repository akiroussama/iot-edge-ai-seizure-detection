from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from src.metrics.calibration import brier_score
from src.utils.time import ensure_datetime


@dataclass(frozen=True)
class ObservabilityConfig:
    modalities: tuple[str, ...] = ("hr", "acc")
    min_coverage_fraction: float = 0.7
    max_dropout_fraction: float = 0.3
    observable_threshold: float = 0.65
    coverage_weight: float = 0.5
    dropout_weight: float = 0.25
    plausibility_weight: float = 0.25


def _require_columns(df: pd.DataFrame, required: set[str], name: str) -> None:
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"{name} missing required columns: {missing}")


def _validate_config(config: ObservabilityConfig) -> None:
    if not config.modalities:
        raise ValueError("at least one modality is required")
    for value_name, value in [
        ("min_coverage_fraction", config.min_coverage_fraction),
        ("max_dropout_fraction", config.max_dropout_fraction),
        ("observable_threshold", config.observable_threshold),
    ]:
        if not 0 <= value <= 1:
            raise ValueError(f"{value_name} must be in [0, 1]")
    weights = [config.coverage_weight, config.dropout_weight, config.plausibility_weight]
    if any(value < 0 for value in weights) or sum(weights) <= 0:
        raise ValueError("observability weights must be non-negative with positive sum")


def _window_minutes(df: pd.DataFrame) -> pd.Series:
    if {"window_start", "window_end"}.issubset(df.columns):
        start = ensure_datetime(df["window_start"])
        end = ensure_datetime(df["window_end"])
        minutes = (end - start).dt.total_seconds() / 60.0
        return pd.to_numeric(minutes, errors="coerce").clip(lower=0)
    return pd.Series(0.0, index=df.index, dtype=float)


def _modality_feature_columns(df: pd.DataFrame, modality: str) -> list[str]:
    prefix = f"{modality}_"
    excluded_suffixes = (
        "_coverage_fraction",
        "_sample_count",
        "_expected_samples",
        "_dropout_fraction",
        "_plausible",
    )
    return [
        column
        for column in df.columns
        if column.startswith(prefix) and not column.endswith(excluded_suffixes)
    ]


def _coverage_fraction(df: pd.DataFrame, modality: str) -> pd.Series:
    explicit_col = f"{modality}_coverage_fraction"
    sample_col = f"{modality}_sample_count"
    expected_col = f"{modality}_expected_samples"
    if explicit_col in df.columns:
        return pd.to_numeric(df[explicit_col], errors="coerce").clip(0, 1).fillna(0.0)
    if {sample_col, expected_col}.issubset(df.columns):
        samples = pd.to_numeric(df[sample_col], errors="coerce").clip(lower=0)
        expected = pd.to_numeric(df[expected_col], errors="coerce").clip(lower=0)
        coverage = samples / expected.replace(0, np.nan)
        return coverage.clip(0, 1).fillna(0.0)
    feature_cols = _modality_feature_columns(df, modality)
    if not feature_cols:
        return pd.Series(0.0, index=df.index, dtype=float)
    finite = df[feature_cols].apply(pd.to_numeric, errors="coerce").notna()
    return finite.mean(axis=1).astype(float)


def _dropout_fraction(df: pd.DataFrame, modality: str, coverage: pd.Series) -> pd.Series:
    dropout_col = f"{modality}_dropout_fraction"
    if dropout_col in df.columns:
        return pd.to_numeric(df[dropout_col], errors="coerce").clip(0, 1).fillna(1.0)
    return (1.0 - coverage).clip(0, 1)


def _plausibility_score(df: pd.DataFrame, modality: str) -> pd.Series:
    explicit_col = f"{modality}_plausible"
    if explicit_col in df.columns:
        values = df[explicit_col]
        if pd.api.types.is_bool_dtype(values):
            return values.fillna(False).astype(float)
        normalized = values.astype("string").str.strip().str.lower()
        return normalized.isin({"true", "1", "yes", "y"}).astype(float)

    feature_cols = _modality_feature_columns(df, modality)
    if not feature_cols:
        return pd.Series(0.0, index=df.index, dtype=float)

    checks = []
    for column in feature_cols:
        values = pd.to_numeric(df[column], errors="coerce")
        if column in {"hr_mean", "hr_median"}:
            checks.append(values.between(30, 220))
        elif column in {"hr_min"}:
            checks.append(values.between(20, 240))
        elif column in {"hr_max"}:
            checks.append(values.between(30, 260))
        elif column.endswith("_energy"):
            checks.append(values.ge(0) & np.isfinite(values))
        else:
            checks.append(np.isfinite(values))
    if not checks:
        return pd.Series(0.0, index=df.index, dtype=float)
    return pd.concat(checks, axis=1).mean(axis=1).fillna(0.0).astype(float)


def add_observability_features(
    df: pd.DataFrame,
    *,
    config: ObservabilityConfig | None = None,
) -> pd.DataFrame:
    """Append sensor observability and deficiency fields without using labels."""
    cfg = config or ObservabilityConfig()
    _validate_config(cfg)
    out = df.copy()
    weights_sum = cfg.coverage_weight + cfg.dropout_weight + cfg.plausibility_weight
    coverage_cols = []
    dropout_cols = []
    plausibility_cols = []

    for modality in cfg.modalities:
        coverage = _coverage_fraction(out, modality)
        dropout = _dropout_fraction(out, modality, coverage)
        plausibility = _plausibility_score(out, modality)
        coverage_col = f"{modality}_observed_fraction"
        dropout_col = f"{modality}_deficient_fraction"
        plausibility_col = f"{modality}_plausibility_score"
        out[coverage_col] = coverage
        out[dropout_col] = dropout
        out[plausibility_col] = plausibility
        coverage_cols.append(coverage_col)
        dropout_cols.append(dropout_col)
        plausibility_cols.append(plausibility_col)

    coverage_score = out[coverage_cols].mean(axis=1).clip(0, 1)
    dropout_score = (1.0 - out[dropout_cols].mean(axis=1)).clip(0, 1)
    plausibility_score = out[plausibility_cols].mean(axis=1).clip(0, 1)
    observable_score = (
        cfg.coverage_weight * coverage_score
        + cfg.dropout_weight * dropout_score
        + cfg.plausibility_weight * plausibility_score
    ) / weights_sum

    out["sensor_coverage_score"] = coverage_score
    out["sensor_dropout_score"] = dropout_score
    out["physiological_plausibility_score"] = plausibility_score
    out["observable_score"] = observable_score.clip(0, 1)
    out["is_observable"] = out["observable_score"].ge(cfg.observable_threshold)
    minutes = _window_minutes(out)
    out["deficiency_time_minutes"] = minutes.where(~out["is_observable"], 0.0)
    out["deficiency_reason"] = _deficiency_reasons(out, cfg)
    return out


def _deficiency_reasons(df: pd.DataFrame, cfg: ObservabilityConfig) -> pd.Series:
    reasons = []
    for _, row in df.iterrows():
        row_reasons = []
        if row["sensor_coverage_score"] < cfg.min_coverage_fraction:
            row_reasons.append("low_sensor_coverage")
        if (1.0 - row["sensor_dropout_score"]) > cfg.max_dropout_fraction:
            row_reasons.append("high_dropout")
        if row["physiological_plausibility_score"] < cfg.observable_threshold:
            row_reasons.append("implausible_signal")
        if not row_reasons and row["is_observable"]:
            row_reasons.append("observable")
        elif not row_reasons:
            row_reasons.append("low_observable_score")
        reasons.append(";".join(row_reasons))
    return pd.Series(reasons, index=df.index)


def apply_observability_abstention(
    df: pd.DataFrame,
    *,
    max_abstention_fraction: float | None = None,
    threshold: float | None = None,
) -> pd.DataFrame:
    """Mark deficient windows for abstention under an optional fixed budget."""
    if "observable_score" not in df.columns or "is_observable" not in df.columns:
        raise ValueError("df must contain observable_score and is_observable")
    if max_abstention_fraction is not None and not 0 <= max_abstention_fraction <= 1:
        raise ValueError("max_abstention_fraction must be in [0, 1]")

    out = df.copy()
    score = pd.to_numeric(out["observable_score"], errors="coerce").fillna(0.0)
    deficient = ~out["is_observable"].fillna(False).astype(bool)
    if threshold is not None:
        deficient |= score.lt(float(threshold))
    abstain = pd.Series(False, index=out.index, dtype=bool)
    candidates = out.loc[deficient].copy()
    if max_abstention_fraction is None:
        abstain.loc[candidates.index] = True
    else:
        budget = int(np.floor(max_abstention_fraction * len(out)))
        if budget > 0 and not candidates.empty:
            selected = candidates.assign(_score=score.loc[candidates.index]).sort_values(
                ["_score"],
                ascending=True,
            ).head(budget)
            abstain.loc[selected.index] = True
    out["abstain_for_observability"] = abstain
    out["observability_policy"] = (
        "threshold_all_deficient"
        if max_abstention_fraction is None
        else f"budget_fraction_{max_abstention_fraction:.4f}"
    )
    return out


def observability_summary(
    df: pd.DataFrame,
    *,
    group_cols: tuple[str, ...] = (),
) -> pd.DataFrame:
    _require_columns(
        df,
        {"observable_score", "is_observable", "deficiency_time_minutes"},
        "df",
    )
    groups = [((), df)] if not group_cols else df.groupby(list(group_cols), dropna=False)
    rows = []
    for key, group in groups:
        if not isinstance(key, tuple):
            key = (key,)
        is_observable = group["is_observable"].fillna(False).astype(bool)
        abstain = (
            group["abstain_for_observability"].fillna(False).astype(bool)
            if "abstain_for_observability" in group.columns
            else pd.Series(False, index=group.index)
        )
        row = {
            "rows": int(len(group)),
            "observable_rows": int(is_observable.sum()),
            "deficient_rows": int((~is_observable).sum()),
            "abstained_rows": int(abstain.sum()),
            "observable_fraction": float(is_observable.mean()) if len(group) else np.nan,
            "mean_observable_score": float(group["observable_score"].mean()),
            "deficiency_time_minutes": float(group["deficiency_time_minutes"].sum()),
        }
        row.update({column: value for column, value in zip(group_cols, key, strict=True)})
        rows.append(row)
    return pd.DataFrame(rows)


def observability_metric_strata(
    predictions: pd.DataFrame,
    *,
    strata_col: str = "is_observable",
) -> pd.DataFrame:
    _require_columns(predictions, {strata_col}, "predictions")
    rows = []
    for value, group in predictions.groupby(strata_col, dropna=False):
        valid = ~group.get("is_excluded", pd.Series(False, index=group.index)).fillna(False).astype(bool)
        valid_group = group.loc[valid]
        row = {
            "stratum": "observable" if bool(value) else "deficient",
            "rows": int(len(group)),
            "valid_rows": int(len(valid_group)),
            "mean_observable_score": float(group["observable_score"].mean())
            if "observable_score" in group.columns
            else np.nan,
            "brier_score": brier_score(valid_group)
            if {"risk_score", "forecast_label"}.issubset(valid_group.columns)
            else np.nan,
            "positive_windows": int(valid_group["forecast_label"].fillna(False).astype(bool).sum())
            if "forecast_label" in valid_group.columns
            else 0,
        }
        rows.append(row)
    return pd.DataFrame(rows)


def observability_markdown(
    enriched: pd.DataFrame,
    summary: pd.DataFrame,
    strata: pd.DataFrame,
    *,
    title: str = "Observability And Missingness Report",
    citation_status: str = "not_citable_pre_gate_c",
    gate_c_status: str = "not_started",
) -> str:
    warning = ""
    if citation_status != "citable_after_gate_c":
        warning = "\n**Citation status:** not citable as a benchmark result.\n"
    return f"""# {title}
{warning}
This report describes whether prediction windows are observable enough for
wearable seizure-risk evaluation. It is a signal-quality artifact, not a model
performance claim.

## Gate Status

- Citation status: `{citation_status}`
- Gate C status: `{gate_c_status}`

## Summary

{_markdown_table(summary)}

## Metric Strata

{_markdown_table(strata)}

## Enriched Preview

{_markdown_table(enriched.head(20))}
"""


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
