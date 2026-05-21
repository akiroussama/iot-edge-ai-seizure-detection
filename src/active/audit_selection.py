from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import numpy as np
import pandas as pd

from src.reports.label_audit import build_label_audit_review_sheet
from src.utils.time import ensure_datetime

DEFAULT_AUDIT_ID_COLUMNS = ("patient_id", "recording_id", "window_start", "window_end")
DEFAULT_AUDIT_SELECTION_WEIGHTS = {
    "uncertainty": 0.30,
    "disagreement": 0.30,
    "clinical_leverage": 0.25,
    "edge_case": 0.15,
}
SCORE_COLUMNS = [
    "uncertainty_score",
    "disagreement_score",
    "clinical_leverage_score",
    "edge_case_score",
    "active_audit_score",
]
DATETIME_ALIGNMENT_COLUMNS = {"window_start", "window_end", "seizure_start", "seizure_end"}


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


def _require_columns(df: pd.DataFrame, required: set[str], name: str) -> None:
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"{name} missing required columns: {missing}")


def _normalize_alignment_columns(
    df: pd.DataFrame,
    id_columns: tuple[str, ...],
    name: str,
) -> pd.DataFrame:
    _require_columns(df, set(id_columns), name)
    out = df.copy()
    for column in id_columns:
        if column in DATETIME_ALIGNMENT_COLUMNS:
            out[column] = ensure_datetime(out[column])
    return out


def _prediction_columns(df: pd.DataFrame, name: str, prefix: str) -> pd.DataFrame:
    if "risk_score" not in df.columns:
        raise ValueError(f"{name} missing required prediction column: risk_score")
    columns = ["risk_score"]
    if "alarm" in df.columns:
        columns.append("alarm")
    return df[columns].rename(columns={column: f"{prefix}_{column}" for column in columns})


def _join_prediction_table(
    audit: pd.DataFrame,
    predictions: pd.DataFrame,
    *,
    id_columns: tuple[str, ...],
    name: str,
    prefix: str,
) -> pd.DataFrame:
    pred = _normalize_alignment_columns(predictions, id_columns, name)
    duplicate_mask = pred.duplicated(list(id_columns), keep=False)
    if duplicate_mask.any():
        examples = pred.loc[duplicate_mask, list(id_columns)].head(3).to_dict(orient="records")
        raise ValueError(f"{name} contains duplicate alignment keys, examples={examples}")

    payload = pd.concat([pred[list(id_columns)], _prediction_columns(pred, name, prefix)], axis=1)
    joined = audit.merge(
        payload,
        on=list(id_columns),
        how="left",
        validate="many_to_one",
        indicator=True,
    )
    missing = joined["_merge"].ne("both")
    if missing.any():
        examples = joined.loc[missing, list(id_columns)].head(3).to_dict(orient="records")
        raise ValueError(
            f"{name} missing prediction rows for audit windows: "
            f"missing_rows={int(missing.sum())}, examples={examples}"
        )
    return joined.drop(columns=["_merge"])


def _normalize_weights(weights: Mapping[str, float] | None) -> dict[str, float]:
    merged = dict(DEFAULT_AUDIT_SELECTION_WEIGHTS)
    if weights is not None:
        unknown = sorted(set(weights) - set(merged))
        if unknown:
            raise ValueError(f"unknown audit selection weight names: {unknown}")
        merged.update({key: float(value) for key, value in weights.items()})
    if any(value < 0 for value in merged.values()):
        raise ValueError("audit selection weights must be non-negative")
    total = sum(merged.values())
    if total <= 0:
        raise ValueError("at least one audit selection weight must be positive")
    return {key: value / total for key, value in merged.items()}


def _bounded_mean(values: pd.Series | np.ndarray) -> float:
    arr = np.asarray(values, dtype=float)
    arr = arr[np.isfinite(arr)]
    if arr.size == 0:
        return 0.0
    return float(np.clip(np.mean(arr), 0.0, 1.0))


def _risk_uncertainty(group: pd.DataFrame, valid: pd.Series) -> float:
    if "model_risk_score" not in group.columns:
        return 0.0
    risk = pd.to_numeric(group.loc[valid, "model_risk_score"], errors="coerce").clip(0, 1)
    return _bounded_mean(1.0 - np.abs(2.0 * risk - 1.0))


def _risk_disagreement(group: pd.DataFrame, valid: pd.Series) -> float:
    reference_columns = [
        column
        for column in group.columns
        if column.startswith("reference_") and column.endswith("_risk_score")
    ]
    if not reference_columns or "model_risk_score" not in group.columns:
        return 0.0
    model = pd.to_numeric(group.loc[valid, "model_risk_score"], errors="coerce").clip(0, 1)
    disagreements = []
    for column in reference_columns:
        reference = pd.to_numeric(group.loc[valid, column], errors="coerce").clip(0, 1)
        disagreements.append((model - reference).abs().to_numpy(dtype=float))
    if not disagreements:
        return 0.0
    stacked = np.vstack(disagreements)
    return _bounded_mean(np.nanmax(stacked, axis=0))


def _clinical_leverage(group: pd.DataFrame, valid: pd.Series) -> float:
    if "minutes_to_seizure" not in group.columns:
        return 0.0
    minutes = pd.to_numeric(group.loc[valid, "minutes_to_seizure"], errors="coerce")
    before_event = minutes.ge(0)
    if not before_event.any():
        return 0.0

    finite_minutes = minutes.loc[before_event & minutes.notna()]
    if finite_minutes.empty:
        return 0.0
    horizon = max(float(finite_minutes.max()), 1.0)
    closeness = (1.0 - (minutes.clip(lower=0, upper=horizon) / horizon)).where(before_event, 0.0)

    if "model_risk_score" in group.columns:
        risk = pd.to_numeric(group.loc[valid, "model_risk_score"], errors="coerce").clip(0, 1)
        risk_weighted = (risk * closeness).to_numpy(dtype=float)
    else:
        risk_weighted = np.array([], dtype=float)

    alarm = _bool_series(group, "model_alarm").loc[valid]
    forecast = _bool_series(group, "forecast_label").loc[valid]
    positive = alarm | forecast
    positive_closeness = closeness.loc[positive].to_numpy(dtype=float)
    candidates = []
    if risk_weighted.size:
        candidates.append(float(np.nanmax(risk_weighted)))
    if positive_closeness.size:
        candidates.append(float(np.nanmax(positive_closeness)))
    return float(np.clip(max(candidates, default=0.0), 0.0, 1.0))


def _edge_case_density(group: pd.DataFrame, valid: pd.Series) -> float:
    if group.empty:
        return 0.0
    denominator = max(len(group), 1)
    right_censored = _bool_series(group, "is_right_censored")
    ictal = _bool_series(group, "is_ictal")
    postictal = _bool_series(group, "is_postictal")
    excluded = _bool_series(group, "is_excluded")
    unexpected = (ictal & ~excluded) | (postictal & ~excluded)
    valid_forecast_positive = _bool_series(group, "forecast_label") & valid
    raw_density = (
        right_censored.sum()
        + 2.0 * unexpected.sum()
        + 0.5 * valid_forecast_positive.sum()
    ) / denominator
    return float(np.clip(raw_density, 0.0, 1.0))


def _score_group(group: pd.DataFrame, weights: Mapping[str, float]) -> dict[str, Any]:
    valid = ~_bool_series(group, "is_excluded")
    forecast = _bool_series(group, "forecast_label")
    alarm = _bool_series(group, "model_alarm")
    risk = (
        pd.to_numeric(group["model_risk_score"], errors="coerce").clip(0, 1)
        if "model_risk_score" in group.columns
        else pd.Series(np.nan, index=group.index)
    )
    components = {
        "uncertainty": _risk_uncertainty(group, valid),
        "disagreement": _risk_disagreement(group, valid),
        "clinical_leverage": _clinical_leverage(group, valid),
        "edge_case": _edge_case_density(group, valid),
    }
    active_score = float(sum(weights[name] * value for name, value in components.items()))
    dominant = max(components, key=components.get)
    ranked_reasons = sorted(components.items(), key=lambda item: (-item[1], item[0]))
    reasons = [
        f"{name}={value:.3f}"
        for name, value in ranked_reasons
        if value > 0
    ][:2]
    return {
        "timeline_rows": int(len(group)),
        "valid_timeline_rows": int(valid.sum()),
        "valid_alarm_rows": int((alarm & valid).sum()),
        "mean_risk_score": float(risk.mean()) if risk.notna().any() else np.nan,
        "max_risk_score": float(risk.max()) if risk.notna().any() else np.nan,
        "uncertainty_score": components["uncertainty"],
        "disagreement_score": components["disagreement"],
        "clinical_leverage_score": components["clinical_leverage"],
        "edge_case_score": components["edge_case"],
        "active_audit_score": active_score,
        "dominant_acquisition": dominant,
        "selection_reason": "; ".join(reasons) if reasons else "no_active_signal",
        "active_selection_label_issue_flag": bool(
            _bool_series(group, "injected_label_issue").any()
            if "injected_label_issue" in group.columns
            else False
        ),
        "valid_forecast_positive_rows_active": int((forecast & valid).sum()),
    }


def _safe_reference_prefix(reference_name: str) -> str:
    safe = "".join(ch.lower() if ch.isalnum() else "_" for ch in reference_name.strip())
    safe = "_".join(part for part in safe.split("_") if part)
    if not safe:
        raise ValueError("reference prediction name cannot be empty")
    return f"reference_{safe}"


def _event_score_table(
    enriched_audit: pd.DataFrame,
    *,
    weights: Mapping[str, float],
) -> pd.DataFrame:
    rows = []
    for event_index, group in enriched_audit.groupby("event_index", sort=False, dropna=False):
        first = group.iloc[0]
        rows.append(
            {
                "event_index": event_index,
                "patient_id": first.get("patient_id"),
                "recording_id": first.get("recording_id"),
                "seizure_start": first.get("seizure_start"),
                "seizure_end": first.get("seizure_end"),
                **_score_group(group, weights),
            }
        )
    return pd.DataFrame(rows)


def build_audit_target_table(
    audit_df: pd.DataFrame,
    predictions_df: pd.DataFrame | None = None,
    reference_predictions: Mapping[str, pd.DataFrame] | None = None,
    *,
    id_columns: tuple[str, ...] = DEFAULT_AUDIT_ID_COLUMNS,
    weights: Mapping[str, float] | None = None,
) -> pd.DataFrame:
    """Build an event-level manual-audit queue with active selection scores.

    The returned table preserves the human review columns from the label audit
    workflow and appends acquisition scores used only for prioritizing what a
    clinician should inspect first. It is not a benchmark metric and it does not
    mark any label as automatically correct.
    """
    if audit_df.empty:
        return pd.DataFrame()
    _require_columns(audit_df, {"event_index", "patient_id", "seizure_start", "seizure_end"}, "audit_df")
    normalized_weights = _normalize_weights(weights)
    audit = _normalize_alignment_columns(audit_df, id_columns, "audit_df")
    for column in ("seizure_start", "seizure_end"):
        if column in audit.columns:
            audit[column] = ensure_datetime(audit[column])

    enriched = audit.copy()
    if predictions_df is not None:
        enriched = _join_prediction_table(
            enriched,
            predictions_df,
            id_columns=id_columns,
            name="predictions_df",
            prefix="model",
        )
    elif "risk_score" in enriched.columns:
        enriched["model_risk_score"] = pd.to_numeric(enriched["risk_score"], errors="coerce").clip(0, 1)
        if "alarm" in enriched.columns:
            enriched["model_alarm"] = _bool_series(enriched, "alarm")

    references = reference_predictions or {}
    if references and "model_risk_score" not in enriched.columns:
        raise ValueError("reference_predictions require predictions_df or audit_df.risk_score")
    for reference_name, reference_df in references.items():
        prefix = _safe_reference_prefix(reference_name)
        enriched = _join_prediction_table(
            enriched,
            reference_df,
            id_columns=id_columns,
            name=f"reference_predictions[{reference_name}]",
            prefix=prefix,
        )

    review = build_label_audit_review_sheet(
        audit,
        max_events=None,
        selection_strategy="first",
    )
    scores = _event_score_table(enriched, weights=normalized_weights)
    if review.empty:
        return scores
    score_payload = scores.drop(
        columns=[
            column
            for column in scores.columns
            if column in set(review.columns) and column != "event_index"
        ]
    )
    merged = review.merge(
        score_payload,
        on="event_index",
        how="left",
        validate="one_to_one",
    )
    ordered_columns = [
        *review.columns,
        "valid_timeline_rows",
        "valid_alarm_rows",
        "mean_risk_score",
        "max_risk_score",
        *SCORE_COLUMNS,
        "dominant_acquisition",
        "selection_reason",
        "active_selection_label_issue_flag",
    ]
    passthrough_columns = [
        column
        for column in merged.columns
        if column not in ordered_columns and not column.endswith("_active")
    ]
    return merged[ordered_columns + passthrough_columns]


def _sort_targets(targets: pd.DataFrame) -> pd.DataFrame:
    sort_columns = ["active_audit_score"]
    ascending = [False]
    for column in ("patient_id", "recording_id", "seizure_start", "event_index"):
        if column in targets.columns:
            sort_columns.append(column)
            ascending.append(True)
    return targets.sort_values(sort_columns, ascending=ascending).reset_index(drop=True)


def _select_patient_spread(targets: pd.DataFrame, budget: int) -> pd.DataFrame:
    ranked = _sort_targets(targets)
    grouped = {patient: group.reset_index(drop=True) for patient, group in ranked.groupby("patient_id", sort=False)}
    patient_order = sorted(
        grouped,
        key=lambda patient: float(grouped[patient]["active_audit_score"].iloc[0]),
        reverse=True,
    )
    positions = {patient: 0 for patient in patient_order}
    selected = []
    while len(selected) < budget:
        progressed = False
        for patient in patient_order:
            group = grouped[patient]
            pos = positions[patient]
            if pos >= len(group):
                continue
            selected.append(group.iloc[pos])
            positions[patient] = pos + 1
            progressed = True
            if len(selected) >= budget:
                break
        if not progressed:
            break
    return pd.DataFrame(selected).reset_index(drop=True)


def select_audit_targets(
    target_table: pd.DataFrame,
    *,
    budget: int,
    selection_strategy: str = "top_score",
    seed: int = 42,
) -> pd.DataFrame:
    """Select a fixed-size clinician review queue from scored audit targets."""
    if budget <= 0:
        raise ValueError("budget must be positive")
    if target_table.empty:
        return target_table.copy()
    _require_columns(target_table, {"active_audit_score"}, "target_table")
    budget = min(int(budget), len(target_table))
    if selection_strategy == "top_score":
        selected = _sort_targets(target_table).head(budget).copy()
    elif selection_strategy == "patient_spread":
        if "patient_id" not in target_table.columns:
            raise ValueError("patient_spread selection requires patient_id")
        selected = _select_patient_spread(target_table, budget).copy()
    elif selection_strategy == "random":
        rng = np.random.default_rng(seed)
        positions = rng.permutation(len(target_table))[:budget]
        selected = target_table.iloc[positions].reset_index(drop=True).copy()
    else:
        raise ValueError("selection_strategy must be 'top_score', 'patient_spread', or 'random'")

    selected = selected.reset_index(drop=True)
    selected.insert(0, "audit_rank", np.arange(1, len(selected) + 1, dtype=int))
    selected.insert(1, "selection_strategy", selection_strategy)
    return selected
