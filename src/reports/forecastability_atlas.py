from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


ATLAS_COLUMNS = [
    "atlas_id",
    "atlas_scope",
    "dataset",
    "cohort",
    "patient_id",
    "modality",
    "model_name",
    "model_family",
    "split_name",
    "horizon_name",
    "sph_minutes",
    "sop_minutes",
    "events_used_for_metrics",
    "valid_prediction_rows",
    "sensitivity",
    "false_alarm_rate_per_day",
    "time_in_warning",
    "brier_skill_score",
    "brier_skill_score_ci_low",
    "brier_skill_score_ci_high",
    "bss_reference",
    "null_delta_brier_skill_score",
    "expected_calibration_error",
    "reliability_slope",
    "citation_status",
    "gate_c_status",
    "forecastability_label",
    "claim_status",
    "paper_table_ready",
    "forecastability_reason",
]


@dataclass(frozen=True)
class ForecastabilityThresholds:
    min_events: int = 5
    min_valid_prediction_rows: int = 100
    min_brier_skill_score: float = 0.0
    max_false_alarm_rate_per_day: float | None = None


def _require_columns(df: pd.DataFrame, required: set[str], name: str) -> None:
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"{name} missing required columns: {missing}")


def _numeric(row: pd.Series, column: str) -> float:
    value = row.get(column, np.nan)
    try:
        return float(value)
    except (TypeError, ValueError):
        return float("nan")


def _string_or_none(row: pd.Series, column: str) -> str | None:
    value = row.get(column)
    if value is None or pd.isna(value):
        return None
    return str(value)


def _atlas_scope(row: pd.Series) -> str:
    patient = _string_or_none(row, "patient_id")
    if patient:
        return "per_patient"
    cohort = (_string_or_none(row, "cohort") or "").lower()
    if cohort.startswith("patient:") or cohort.startswith("patient_"):
        return "per_patient"
    return "pooled"


def _atlas_id(row: pd.Series) -> str:
    parts = [
        _string_or_none(row, "dataset") or "dataset",
        _string_or_none(row, "cohort") or _string_or_none(row, "patient_id") or "pooled",
        _string_or_none(row, "modality") or "modality",
        _string_or_none(row, "horizon_name") or "horizon",
        _string_or_none(row, "model_name") or "model",
    ]
    safe_parts = []
    for part in parts:
        safe = "".join(ch.lower() if ch.isalnum() else "_" for ch in part)
        safe = "_".join(piece for piece in safe.split("_") if piece)
        safe_parts.append(safe or "na")
    return "__".join(safe_parts)


def _claim_status(row: pd.Series, *, gate_c_required: bool) -> str:
    citation_status = _string_or_none(row, "citation_status")
    gate_c_status = _string_or_none(row, "gate_c_status")
    if citation_status == "citable_after_gate_c" and gate_c_status != "passed":
        raise ValueError("citable atlas rows require gate_c_status='passed'")
    if gate_c_required and citation_status != "citable_after_gate_c":
        return "not_citable_pre_gate_c"
    if gate_c_required and gate_c_status != "passed":
        return "not_citable_pre_gate_c"
    if citation_status == "citable_after_gate_c" and gate_c_status == "passed":
        return "citable_after_gate_c"
    return "exploratory_not_citable"


def _forecastability_label(
    row: pd.Series,
    *,
    thresholds: ForecastabilityThresholds,
    gate_c_required: bool,
) -> tuple[str, str, bool, str]:
    claim_status = _claim_status(row, gate_c_required=gate_c_required)
    if claim_status == "not_citable_pre_gate_c":
        return (
            "not_citable_pre_gate_c",
            claim_status,
            False,
            "Gate C/frozen citation guardrail blocks paper-table claim",
        )

    events = _numeric(row, "events_used_for_metrics")
    valid_rows = _numeric(row, "valid_prediction_rows")
    if np.isfinite(events) and events < thresholds.min_events:
        return (
            "underpowered",
            claim_status,
            False,
            f"events_used_for_metrics={events:g} < min_events={thresholds.min_events}",
        )
    if np.isfinite(valid_rows) and valid_rows < thresholds.min_valid_prediction_rows:
        return (
            "underpowered",
            claim_status,
            False,
            "valid_prediction_rows="
            f"{valid_rows:g} < min_valid_prediction_rows={thresholds.min_valid_prediction_rows}",
        )

    bss = _numeric(row, "brier_skill_score")
    ci_low = _numeric(row, "brier_skill_score_ci_low")
    ci_high = _numeric(row, "brier_skill_score_ci_high")
    if not np.isfinite(bss):
        return (
            "unassessed_no_null",
            claim_status,
            False,
            "missing brier_skill_score against a null reference",
        )

    if thresholds.max_false_alarm_rate_per_day is not None:
        far = _numeric(row, "false_alarm_rate_per_day")
        if np.isfinite(far) and far > thresholds.max_false_alarm_rate_per_day:
            return (
                "forecastable_but_alarm_burden_high",
                claim_status,
                False,
                f"FAR/day={far:g} exceeds max_false_alarm_rate_per_day="
                f"{thresholds.max_false_alarm_rate_per_day:g}",
            )

    if np.isfinite(ci_low) and np.isfinite(ci_high):
        if ci_low > thresholds.min_brier_skill_score:
            return (
                "forecastable_above_null",
                claim_status,
                claim_status == "citable_after_gate_c",
                "BSS confidence interval is above null",
            )
        if ci_low <= thresholds.min_brier_skill_score <= ci_high:
            return (
                "unforecastable_null_overlap",
                claim_status,
                False,
                "BSS confidence interval overlaps null",
            )
        return (
            "unforecastable_not_above_null",
            claim_status,
            False,
            "BSS confidence interval is not above null",
        )

    if bss > thresholds.min_brier_skill_score:
        return (
            "exploratory_positive_no_ci",
            claim_status,
            False,
            "BSS is above null but confidence interval is missing",
        )
    return (
        "unforecastable_not_above_null",
        claim_status,
        False,
        "BSS is not above null",
    )


def reliability_slope_table(
    reliability_df: pd.DataFrame,
    *,
    series_col: str = "series_name",
) -> pd.DataFrame:
    """Estimate calibration reliability slope from reliability-bin tables."""
    _require_columns(
        reliability_df,
        {series_col, "mean_score", "empirical_rate", "count"},
        "reliability_df",
    )
    rows = []
    for series_name, group in reliability_df.groupby(series_col, dropna=False):
        x = pd.to_numeric(group["mean_score"], errors="coerce").to_numpy(dtype=float)
        y = pd.to_numeric(group["empirical_rate"], errors="coerce").to_numpy(dtype=float)
        w = pd.to_numeric(group["count"], errors="coerce").fillna(0).to_numpy(dtype=float)
        mask = np.isfinite(x) & np.isfinite(y) & np.isfinite(w) & (w > 0)
        if mask.sum() < 2:
            slope = float("nan")
        else:
            x, y, w = x[mask], y[mask], w[mask]
            x_mean = float(np.average(x, weights=w))
            y_mean = float(np.average(y, weights=w))
            denom = float(np.sum(w * (x - x_mean) ** 2))
            slope = float(np.sum(w * (x - x_mean) * (y - y_mean)) / denom) if denom else float("nan")
        rows.append({"model_name": series_name, "reliability_slope": slope})
    return pd.DataFrame(rows)


def _attach_reliability_slope(
    atlas: pd.DataFrame,
    reliability_df: pd.DataFrame | None,
) -> pd.DataFrame:
    if reliability_df is None or reliability_df.empty:
        atlas["reliability_slope"] = np.nan
        return atlas
    slopes = reliability_slope_table(reliability_df)
    return atlas.merge(slopes, on="model_name", how="left", validate="many_to_one")


def build_forecastability_atlas(
    leaderboard_df: pd.DataFrame,
    *,
    reliability_df: pd.DataFrame | None = None,
    thresholds: ForecastabilityThresholds | None = None,
    gate_c_required: bool = True,
) -> pd.DataFrame:
    """Build a paper-oriented forecastability atlas from leaderboard rows."""
    if leaderboard_df.empty:
        return pd.DataFrame(columns=ATLAS_COLUMNS)
    required = {
        "dataset",
        "cohort",
        "modality",
        "model_name",
        "model_family",
        "split_name",
        "horizon_name",
        "sph_minutes",
        "sop_minutes",
        "events_used_for_metrics",
        "valid_prediction_rows",
        "sensitivity",
        "false_alarm_rate_per_day",
        "time_in_warning",
        "brier_skill_score",
        "bss_reference",
        "expected_calibration_error",
        "citation_status",
        "gate_c_status",
    }
    _require_columns(leaderboard_df, required, "leaderboard_df")
    thresholds = thresholds or ForecastabilityThresholds()
    rows = []
    for _, source in leaderboard_df.iterrows():
        label, claim_status, paper_ready, reason = _forecastability_label(
            source,
            thresholds=thresholds,
            gate_c_required=gate_c_required,
        )
        rows.append(
            {
                "atlas_id": _atlas_id(source),
                "atlas_scope": _atlas_scope(source),
                "dataset": source.get("dataset"),
                "cohort": source.get("cohort"),
                "patient_id": source.get("patient_id", pd.NA),
                "modality": source.get("modality"),
                "model_name": source.get("model_name"),
                "model_family": source.get("model_family"),
                "split_name": source.get("split_name"),
                "horizon_name": source.get("horizon_name"),
                "sph_minutes": source.get("sph_minutes"),
                "sop_minutes": source.get("sop_minutes"),
                "events_used_for_metrics": source.get("events_used_for_metrics"),
                "valid_prediction_rows": source.get("valid_prediction_rows"),
                "sensitivity": source.get("sensitivity"),
                "false_alarm_rate_per_day": source.get("false_alarm_rate_per_day"),
                "time_in_warning": source.get("time_in_warning"),
                "brier_skill_score": source.get("brier_skill_score"),
                "brier_skill_score_ci_low": source.get("brier_skill_score_ci_low", np.nan),
                "brier_skill_score_ci_high": source.get("brier_skill_score_ci_high", np.nan),
                "bss_reference": source.get("bss_reference"),
                "null_delta_brier_skill_score": source.get("brier_skill_score"),
                "expected_calibration_error": source.get("expected_calibration_error"),
                "citation_status": source.get("citation_status"),
                "gate_c_status": source.get("gate_c_status"),
                "forecastability_label": label,
                "claim_status": claim_status,
                "paper_table_ready": bool(paper_ready),
                "forecastability_reason": reason,
            }
        )
    atlas = pd.DataFrame(rows)
    atlas = _attach_reliability_slope(atlas, reliability_df)
    return atlas[ATLAS_COLUMNS]


def forecastability_atlas_markdown(
    atlas: pd.DataFrame,
    *,
    title: str = "Forecastability Atlas",
) -> str:
    """Render a compact Markdown atlas with explicit claim-status language."""

    def cell(value: object) -> str:
        if pd.isna(value):
            return ""
        if isinstance(value, float):
            if value.is_integer():
                return str(int(value))
            return f"{value:.3f}"
        return str(value)

    if atlas.empty:
        table = "_No rows._"
    else:
        visible = [
            "atlas_scope",
            "dataset",
            "cohort",
            "modality",
            "horizon_name",
            "model_name",
            "brier_skill_score",
            "brier_skill_score_ci_low",
            "brier_skill_score_ci_high",
            "sensitivity",
            "false_alarm_rate_per_day",
            "time_in_warning",
            "reliability_slope",
            "forecastability_label",
            "claim_status",
            "paper_table_ready",
        ]
        view = atlas[[column for column in visible if column in atlas.columns]]
        headers = [str(column) for column in view.columns]
        lines = [
            "| " + " | ".join(headers) + " |",
            "| " + " | ".join(["---"] * len(headers)) + " |",
        ]
        for _, row in view.iterrows():
            lines.append("| " + " | ".join(cell(row[column]) for column in view.columns) + " |")
        table = "\n".join(lines)

    counts = (
        atlas["forecastability_label"].value_counts().sort_index().to_dict()
        if not atlas.empty
        else {}
    )
    count_lines = [f"- `{label}`: {count}" for label, count in counts.items()]
    return "\n".join(
        [
            f"# {title}",
            "",
            "This atlas is a forecastability synthesis, not a new model metric.",
            "Rows marked non-citable must not be used as benchmark claims before Gate C.",
            "",
            "## Label Counts",
            "",
            "\n".join(count_lines) if count_lines else "_No rows._",
            "",
            "## Atlas",
            "",
            table,
            "",
            "Interpretation:",
            "",
            "- `forecastable_above_null` requires BSS confidence bounds above the null baseline.",
            "- `unforecastable_null_overlap` keeps negative findings visible.",
            "- `paper_table_ready` is true only for citable Gate-C-passed rows.",
            "- Rows without confidence intervals remain exploratory even when BSS is positive.",
        ]
    )
