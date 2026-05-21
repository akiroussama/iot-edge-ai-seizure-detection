from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from src.utils.time import ensure_datetime


@dataclass(frozen=True)
class ClinicalUtilityAssumptions:
    detected_event_benefit: float = 1.0
    missed_event_cost: float = 1.0
    false_alarm_cost_per_day: float = 0.1
    warning_time_cost: float = 0.5
    lead_time_bonus_per_hour: float = 0.0
    brier_skill_score_weight: float = 0.0


@dataclass(frozen=True)
class ClinicalUtilityConstraints:
    max_far_per_day: float | None = None
    max_time_in_warning: float | None = None
    min_sensitivity: float | None = None


UTILITY_COLUMNS = [
    "utility_rank",
    "selected_under_assumptions",
    "policy_status",
    "threshold",
    "sensitivity",
    "miss_rate",
    "far_per_day",
    "time_in_warning",
    "median_lead_time_seconds",
    "brier_skill_score",
    "utility_score",
    "detected_event_benefit_component",
    "missed_event_cost_component",
    "false_alarm_cost_component",
    "warning_time_cost_component",
    "lead_time_bonus_component",
    "brier_skill_component",
    "constraint_reason",
]


def _numeric(series: pd.Series, default: float = 0.0) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").fillna(default).astype(float)


def _require_columns(df: pd.DataFrame, required: set[str], name: str) -> None:
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"{name} missing required columns: {missing}")


def _constraint_status(
    row: pd.Series,
    constraints: ClinicalUtilityConstraints,
) -> tuple[str, str]:
    reasons = []
    sensitivity = row.get("sensitivity")
    if pd.isna(sensitivity):
        reasons.append("missing sensitivity")
    far = row.get("far_per_day")
    if constraints.max_far_per_day is not None and pd.notna(far) and far > constraints.max_far_per_day:
        reasons.append(f"FAR/day {far:g} > {constraints.max_far_per_day:g}")
    tiw = row.get("time_in_warning")
    if (
        constraints.max_time_in_warning is not None
        and pd.notna(tiw)
        and tiw > constraints.max_time_in_warning
    ):
        reasons.append(f"TIW {tiw:g} > {constraints.max_time_in_warning:g}")
    if (
        constraints.min_sensitivity is not None
        and pd.notna(sensitivity)
        and sensitivity < constraints.min_sensitivity
    ):
        reasons.append(f"sensitivity {sensitivity:g} < {constraints.min_sensitivity:g}")
    if reasons:
        return "ineligible", "; ".join(reasons)
    return "eligible", "passes configured constraints"


def clinical_utility_table(
    sweep_df: pd.DataFrame,
    *,
    assumptions: ClinicalUtilityAssumptions | None = None,
    constraints: ClinicalUtilityConstraints | None = None,
) -> pd.DataFrame:
    """Score alarm policies under configurable decision-support assumptions."""
    _require_columns(
        sweep_df,
        {"threshold", "sensitivity", "far_per_day", "time_in_warning"},
        "sweep_df",
    )
    assumptions = assumptions or ClinicalUtilityAssumptions()
    constraints = constraints or ClinicalUtilityConstraints()
    out = sweep_df.copy()
    out["sensitivity"] = _numeric(out["sensitivity"], default=np.nan)
    out["miss_rate"] = 1.0 - out["sensitivity"]
    out["far_per_day"] = _numeric(out["far_per_day"], default=0.0)
    out["time_in_warning"] = _numeric(out["time_in_warning"], default=0.0)
    if "median_lead_time_seconds" not in out.columns:
        out["median_lead_time_seconds"] = np.nan
    if "brier_skill_score" not in out.columns:
        out["brier_skill_score"] = 0.0
    out["median_lead_time_seconds"] = _numeric(out["median_lead_time_seconds"], default=0.0)
    out["brier_skill_score"] = _numeric(out["brier_skill_score"], default=0.0)

    out["detected_event_benefit_component"] = (
        assumptions.detected_event_benefit * out["sensitivity"]
    )
    out["missed_event_cost_component"] = -(assumptions.missed_event_cost * out["miss_rate"])
    out["false_alarm_cost_component"] = -(
        assumptions.false_alarm_cost_per_day * out["far_per_day"]
    )
    out["warning_time_cost_component"] = -(assumptions.warning_time_cost * out["time_in_warning"])
    out["lead_time_bonus_component"] = (
        assumptions.lead_time_bonus_per_hour * out["median_lead_time_seconds"] / 3600.0
    )
    out["brier_skill_component"] = assumptions.brier_skill_score_weight * out["brier_skill_score"]
    component_cols = [
        "detected_event_benefit_component",
        "missed_event_cost_component",
        "false_alarm_cost_component",
        "warning_time_cost_component",
        "lead_time_bonus_component",
        "brier_skill_component",
    ]
    out["utility_score"] = out[component_cols].sum(axis=1)

    statuses = out.apply(lambda row: _constraint_status(row, constraints), axis=1)
    out["policy_status"] = [status for status, _ in statuses]
    out["constraint_reason"] = [reason for _, reason in statuses]
    out["selected_under_assumptions"] = False
    eligible = out.loc[out["policy_status"].eq("eligible") & out["utility_score"].notna()]
    if not eligible.empty:
        best_index = eligible.sort_values(
            ["utility_score", "sensitivity", "far_per_day", "time_in_warning", "threshold"],
            ascending=[False, False, True, True, False],
        ).index[0]
        out.loc[best_index, "selected_under_assumptions"] = True

    out = out.sort_values(
        ["selected_under_assumptions", "policy_status", "utility_score", "threshold"],
        ascending=[False, True, False, False],
    ).reset_index(drop=True)
    out.insert(0, "utility_rank", np.arange(1, len(out) + 1, dtype=int))
    passthrough = [column for column in out.columns if column not in UTILITY_COLUMNS]
    return out[UTILITY_COLUMNS + passthrough]


def apply_refractory_alarm_policy(
    predictions_df: pd.DataFrame,
    *,
    refractory_minutes: float,
) -> pd.DataFrame:
    """Suppress alarms inside a refractory period after a kept alarm episode."""
    if refractory_minutes < 0:
        raise ValueError("refractory_minutes must be non-negative")
    _require_columns(predictions_df, {"window_start", "window_end", "alarm"}, "predictions_df")
    out = predictions_df.copy()
    out["window_start"] = ensure_datetime(out["window_start"])
    out["window_end"] = ensure_datetime(out["window_end"])
    out["alarm"] = out["alarm"].fillna(False).astype(bool)
    out["alarm_before_refractory"] = out["alarm"]
    out["alarm_refractory_suppressed"] = False
    refractory = pd.Timedelta(minutes=refractory_minutes)
    group_cols = [
        column for column in ("patient_id", "recording_id") if column in out.columns
    ]
    sorted_index = out.sort_values(group_cols + ["window_start"] if group_cols else ["window_start"]).index
    groups = out.loc[sorted_index].groupby(group_cols, sort=False) if group_cols else [(None, out.loc[sorted_index])]
    for _, group in groups:
        suppress_until: pd.Timestamp | None = None
        for idx, row in group.iterrows():
            if not bool(row["alarm"]):
                continue
            if suppress_until is not None and row["window_start"] < suppress_until:
                out.loc[idx, "alarm"] = False
                out.loc[idx, "alarm_refractory_suppressed"] = True
                continue
            suppress_until = row["window_end"] + refractory
    return out


def _assumption_lines(assumptions: ClinicalUtilityAssumptions) -> list[str]:
    return [
        f"- Detected-event benefit: `{assumptions.detected_event_benefit}`",
        f"- Missed-event cost: `{assumptions.missed_event_cost}`",
        f"- False-alarm cost per day: `{assumptions.false_alarm_cost_per_day}`",
        f"- Warning-time cost: `{assumptions.warning_time_cost}`",
        f"- Lead-time bonus per hour: `{assumptions.lead_time_bonus_per_hour}`",
        f"- BSS weight: `{assumptions.brier_skill_score_weight}`",
    ]


def clinical_utility_markdown(
    utility_df: pd.DataFrame,
    *,
    assumptions: ClinicalUtilityAssumptions,
    constraints: ClinicalUtilityConstraints,
    title: str = "Clinical Utility Analysis",
    citation_status: str = "not_citable_pre_gate_c",
    gate_c_status: str = "not_started",
) -> str:
    def cell(value: object) -> str:
        if pd.isna(value):
            return ""
        if isinstance(value, float):
            if value.is_integer():
                return str(int(value))
            return f"{value:.3f}"
        return str(value)

    visible = [
        "utility_rank",
        "selected_under_assumptions",
        "policy_status",
        "threshold",
        "utility_score",
        "sensitivity",
        "far_per_day",
        "time_in_warning",
        "median_lead_time_seconds",
        "brier_skill_score",
        "constraint_reason",
    ]
    if utility_df.empty:
        table = "_No rows._"
    else:
        view = utility_df[[column for column in visible if column in utility_df.columns]]
        headers = [str(column) for column in view.columns]
        lines = [
            "| " + " | ".join(headers) + " |",
            "| " + " | ".join(["---"] * len(headers)) + " |",
        ]
        for _, row in view.iterrows():
            lines.append("| " + " | ".join(cell(row[column]) for column in view.columns) + " |")
        table = "\n".join(lines)

    constraint_lines = [
        f"- Max FAR/day: `{constraints.max_far_per_day}`",
        f"- Max TIW: `{constraints.max_time_in_warning}`",
        f"- Min sensitivity: `{constraints.min_sensitivity}`",
    ]
    warning = ""
    if citation_status != "citable_after_gate_c":
        warning = "\n**Citation status:** not citable as a benchmark result.\n"
    return "\n".join(
        [
            f"# {title}",
            warning,
            "This is decision-support analysis, not a clinical recommendation.",
            "",
            f"- Citation status: `{citation_status}`",
            f"- Gate C status: `{gate_c_status}`",
            "",
            "## Utility Assumptions",
            "",
            "\n".join(_assumption_lines(assumptions)),
            "",
            "## Constraints",
            "",
            "\n".join(constraint_lines),
            "",
            "## Policy Table",
            "",
            table,
            "",
            "Interpretation:",
            "",
            "- `selected_under_assumptions` is the best row under the configured costs only.",
            "- Changing costs or constraints can change the selected policy.",
            "- Rows before Gate C remain exploratory and not citable.",
        ]
    )
