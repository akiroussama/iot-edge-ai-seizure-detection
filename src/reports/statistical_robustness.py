from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from src.metrics.calibration import brier_skill_score
from src.reports.calibration_skill import DEFAULT_ID_COLUMNS, align_reference_set


@dataclass(frozen=True)
class StatisticalRobustnessReport:
    intervals: pd.DataFrame
    permutation: pd.DataFrame
    multiplicity: pd.DataFrame
    warnings: pd.DataFrame
    metadata: dict[str, Any]


def _valid_mask(df: pd.DataFrame) -> pd.Series:
    return ~df.get("is_excluded", pd.Series(False, index=df.index)).fillna(False).astype(bool)


def _require_columns(df: pd.DataFrame, required: set[str], name: str) -> None:
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"{name} missing required columns: {missing}")


def _loss_frame(
    predictions: pd.DataFrame,
    reference: pd.DataFrame,
    *,
    reference_name: str,
) -> pd.DataFrame:
    _require_columns(predictions, {"risk_score", "forecast_label"}, "predictions")
    _require_columns(reference, {"risk_score", "forecast_label"}, reference_name)
    valid = _valid_mask(predictions)
    labels = predictions.loc[valid, "forecast_label"].astype(float)
    model_risk = pd.to_numeric(predictions.loc[valid, "risk_score"], errors="coerce").clip(0, 1)
    reference_risk = pd.to_numeric(reference.loc[valid, "risk_score"], errors="coerce").clip(0, 1)
    finite = labels.notna() & model_risk.notna() & reference_risk.notna()
    if not finite.all():
        raise ValueError(f"{reference_name} has non-finite labels or risk scores on valid rows")
    if labels.empty:
        raise ValueError(f"{reference_name} has no valid rows for robustness analysis")

    frame = predictions.loc[valid].copy().reset_index(drop=True)
    frame["forecast_label"] = labels.to_numpy(dtype=float)
    frame["model_risk_score"] = model_risk.to_numpy(dtype=float)
    frame["reference_risk_score"] = reference_risk.to_numpy(dtype=float)
    frame["model_brier_loss"] = (frame["model_risk_score"] - frame["forecast_label"]) ** 2
    frame["reference_brier_loss"] = (
        frame["reference_risk_score"] - frame["forecast_label"]
    ) ** 2
    frame["brier_loss_delta"] = frame["reference_brier_loss"] - frame["model_brier_loss"]
    return frame


def _bss_from_losses(losses: pd.DataFrame) -> float:
    reference_brier = float(losses["reference_brier_loss"].mean())
    if reference_brier == 0:
        raise ValueError("reference Brier score is zero; Brier Skill Score is undefined")
    model_brier = float(losses["model_brier_loss"].mean())
    return float(1.0 - model_brier / reference_brier)


def _group_positions(df: pd.DataFrame, group_col: str, scope: str) -> dict[Any, np.ndarray]:
    if group_col not in df.columns:
        raise ValueError(f"{scope} bootstrap requested but group column {group_col!r} is missing")
    groups = df[group_col].dropna().unique().tolist()
    if not groups:
        raise ValueError(f"{scope} bootstrap has no valid groups in column {group_col!r}")
    return {group: np.flatnonzero(df[group_col].eq(group).to_numpy()) for group in groups}


def _bootstrap_indices(
    positions_by_group: dict[Any, np.ndarray],
    rng: np.random.Generator,
) -> np.ndarray:
    groups = list(positions_by_group)
    sampled_groups = rng.choice(groups, size=len(groups), replace=True)
    return np.concatenate([positions_by_group[group] for group in sampled_groups])


def bootstrap_brier_skill_score_interval(
    predictions: pd.DataFrame,
    reference: pd.DataFrame,
    *,
    reference_name: str,
    scope: str,
    group_col: str,
    n_bootstrap: int = 1000,
    seed: int = 42,
    ci: float = 0.95,
) -> dict[str, Any]:
    if n_bootstrap <= 0:
        raise ValueError("n_bootstrap must be positive")
    if not 0 < ci < 1:
        raise ValueError("ci must be in (0, 1)")
    losses = _loss_frame(predictions, reference, reference_name=reference_name)
    positions_by_group = _group_positions(losses, group_col, scope)
    rng = np.random.default_rng(seed)
    alpha = (1.0 - ci) / 2.0
    values = []
    for _ in range(n_bootstrap):
        idx = _bootstrap_indices(positions_by_group, rng)
        values.append(_bss_from_losses(losses.iloc[idx]))
    arr = np.asarray(values, dtype=float)
    observed = _bss_from_losses(losses)
    ci_low = float(np.quantile(arr, alpha))
    ci_high = float(np.quantile(arr, 1.0 - alpha))
    return {
        "scope": scope,
        "group_col": group_col,
        "reference_name": reference_name,
        "metric": "brier_skill_score",
        "n_rows": int(len(losses)),
        "n_groups": int(len(positions_by_group)),
        "n_bootstrap": int(n_bootstrap),
        "ci": float(ci),
        "observed": float(observed),
        "bootstrap_mean": float(np.mean(arr)),
        "ci_low": ci_low,
        "ci_high": ci_high,
        "ci_width": float(ci_high - ci_low),
    }


def bootstrap_brier_skill_score_intervals(
    predictions: pd.DataFrame,
    references: dict[str, pd.DataFrame],
    *,
    scope: str,
    group_col: str,
    n_bootstrap: int = 1000,
    seed: int = 42,
    ci: float = 0.95,
) -> pd.DataFrame:
    rows = []
    for offset, (reference_name, reference) in enumerate(references.items()):
        rows.append(
            bootstrap_brier_skill_score_interval(
                predictions,
                reference,
                reference_name=reference_name,
                scope=scope,
                group_col=group_col,
                n_bootstrap=n_bootstrap,
                seed=seed + offset,
                ci=ci,
            )
        )
    return pd.DataFrame(rows)


def paired_brier_permutation_test(
    predictions: pd.DataFrame,
    reference: pd.DataFrame,
    *,
    reference_name: str,
    group_col: str | None = "patient_id",
    n_permutations: int = 1000,
    seed: int = 42,
    alternative: str = "greater",
) -> dict[str, Any]:
    """Paired sign-flip test on Brier-loss deltas.

    Positive deltas mean the model has lower Brier loss than the reference. If
    ``group_col`` is available, signs are flipped by group to respect patient
    clustering; otherwise each row is treated as its own paired unit.
    """
    if n_permutations <= 0:
        raise ValueError("n_permutations must be positive")
    if alternative not in {"greater", "less", "two-sided"}:
        raise ValueError("alternative must be 'greater', 'less', or 'two-sided'")

    losses = _loss_frame(predictions, reference, reference_name=reference_name)
    delta = losses["brier_loss_delta"].to_numpy(dtype=float)
    observed = float(delta.mean())
    rng = np.random.default_rng(seed)

    if group_col is not None and group_col in losses.columns:
        groups = losses[group_col].dropna().unique().tolist()
        if groups:
            group_values = losses[group_col].to_numpy()
            units = len(groups)
            simulated = []
            for _ in range(n_permutations):
                signs_by_group = dict(
                    zip(groups, rng.choice([-1.0, 1.0], size=units), strict=True)
                )
                signs = np.asarray([signs_by_group.get(group, 1.0) for group in group_values])
                simulated.append(float(np.mean(delta * signs)))
            permutation_unit = group_col
        else:
            units = int(len(delta))
            simulated = [float(np.mean(delta * rng.choice([-1.0, 1.0], size=units))) for _ in range(n_permutations)]
            permutation_unit = "row"
    else:
        units = int(len(delta))
        simulated = [float(np.mean(delta * rng.choice([-1.0, 1.0], size=units))) for _ in range(n_permutations)]
        permutation_unit = "row"

    arr = np.asarray(simulated, dtype=float)
    if alternative == "greater":
        p_value = (float(np.sum(arr >= observed)) + 1.0) / (n_permutations + 1.0)
    elif alternative == "less":
        p_value = (float(np.sum(arr <= observed)) + 1.0) / (n_permutations + 1.0)
    else:
        p_value = (float(np.sum(np.abs(arr) >= abs(observed))) + 1.0) / (
            n_permutations + 1.0
        )

    return {
        "reference_name": reference_name,
        "metric": "paired_brier_loss_delta",
        "alternative": alternative,
        "permutation_unit": permutation_unit,
        "n_rows": int(len(losses)),
        "n_permutation_units": int(units),
        "n_permutations": int(n_permutations),
        "observed_mean_delta": observed,
        "model_brier_score": float(losses["model_brier_loss"].mean()),
        "reference_brier_score": float(losses["reference_brier_loss"].mean()),
        "observed_brier_skill_score": brier_skill_score(predictions, reference),
        "p_value": float(p_value),
    }


def adjust_p_values(
    results: pd.DataFrame,
    *,
    p_col: str = "p_value",
    method: str = "benjamini_hochberg",
    alpha: float = 0.05,
) -> pd.DataFrame:
    if method not in {"benjamini_hochberg", "bonferroni"}:
        raise ValueError("method must be 'benjamini_hochberg' or 'bonferroni'")
    if not 0 < alpha < 1:
        raise ValueError("alpha must be in (0, 1)")
    if p_col not in results.columns:
        raise ValueError(f"p-value column {p_col!r} is missing")

    out = results.copy()
    out["multiplicity_method"] = method
    out["multiplicity_alpha"] = float(alpha)
    out["p_value_adjusted"] = np.nan
    p_values = pd.to_numeric(out[p_col], errors="coerce")
    valid = p_values.notna()
    m = int(valid.sum())
    if m == 0:
        out["reject_adjusted_alpha"] = False
        out["reject_adjusted_0_05"] = False
        return out

    if method == "bonferroni":
        adjusted = np.minimum(p_values.loc[valid].to_numpy(dtype=float) * m, 1.0)
        out.loc[valid, "p_value_adjusted"] = adjusted
    else:
        order = np.argsort(p_values.loc[valid].to_numpy(dtype=float))
        sorted_p = p_values.loc[valid].to_numpy(dtype=float)[order]
        ranks = np.arange(1, m + 1, dtype=float)
        sorted_adjusted = np.minimum.accumulate((sorted_p * m / ranks)[::-1])[::-1]
        sorted_adjusted = np.minimum(sorted_adjusted, 1.0)
        adjusted = np.empty(m, dtype=float)
        adjusted[order] = sorted_adjusted
        out.loc[valid, "p_value_adjusted"] = adjusted

    out["reject_adjusted_alpha"] = out["p_value_adjusted"].le(alpha).fillna(False)
    out["reject_adjusted_0_05"] = out["p_value_adjusted"].le(0.05).fillna(False)
    return out


def _robustness_warnings(
    intervals: pd.DataFrame,
    permutation: pd.DataFrame,
    *,
    min_groups: int,
    max_ci_width: float,
) -> pd.DataFrame:
    rows = []
    for _, row in intervals.iterrows():
        base = {
            "scope": row["scope"],
            "reference_name": row["reference_name"],
            "metric": row["metric"],
        }
        if row["n_groups"] < min_groups:
            rows.append(
                {
                    **base,
                    "warning_code": "tiny_n_groups",
                    "severity": "warning",
                    "message": (
                        f"{row['scope']} bootstrap has {row['n_groups']} groups; "
                        f"minimum requested is {min_groups}."
                    ),
                }
            )
        if row["ci_width"] > max_ci_width:
            rows.append(
                {
                    **base,
                    "warning_code": "wide_confidence_interval",
                    "severity": "warning",
                    "message": (
                        f"{row['scope']} bootstrap CI width {row['ci_width']:.4f} "
                        f"exceeds {max_ci_width:.4f}."
                    ),
                }
            )
        if row["ci_low"] <= 0 <= row["ci_high"]:
            rows.append(
                {
                    **base,
                    "warning_code": "skill_ci_crosses_zero",
                    "severity": "info",
                    "message": (
                        f"{row['scope']} bootstrap CI includes zero skill; "
                        "treat superiority claims as unsupported."
                    ),
                }
            )
    for _, row in permutation.iterrows():
        if row["n_permutation_units"] < min_groups:
            rows.append(
                {
                    "scope": row["permutation_unit"],
                    "reference_name": row["reference_name"],
                    "metric": row["metric"],
                    "warning_code": "tiny_n_permutation_units",
                    "severity": "warning",
                    "message": (
                        f"Permutation test has {row['n_permutation_units']} paired units; "
                        f"minimum requested is {min_groups}."
                    ),
                }
            )
    return pd.DataFrame(
        rows,
        columns=["scope", "reference_name", "metric", "warning_code", "severity", "message"],
    )


def build_statistical_robustness_report(
    predictions: pd.DataFrame,
    references: dict[str, pd.DataFrame],
    *,
    model_name: str,
    id_columns: tuple[str, ...] = DEFAULT_ID_COLUMNS,
    patient_col: str | None = "patient_id",
    event_col: str | None = "event_id",
    n_bootstrap: int = 1000,
    n_permutations: int = 1000,
    seed: int = 42,
    ci: float = 0.95,
    min_groups: int = 5,
    max_ci_width: float = 0.5,
    multiplicity_method: str = "benjamini_hochberg",
    permutation_alternative: str = "greater",
    result_status: str = "pre_gate_c_exploratory_not_citable",
    citation_status: str = "not_citable_pre_gate_c",
    gate_c_status: str = "not_started",
) -> StatisticalRobustnessReport:
    if not references:
        raise ValueError("at least one reference prediction table is required")
    if citation_status == "citable_after_gate_c" and gate_c_status != "passed":
        raise ValueError("citable robustness reports require gate_c_status='passed'")
    if min_groups <= 0:
        raise ValueError("min_groups must be positive")
    if max_ci_width <= 0:
        raise ValueError("max_ci_width must be positive")

    aligned_predictions, aligned_references = align_reference_set(
        predictions,
        references,
        id_columns=id_columns,
    )

    interval_frames = []
    if patient_col is not None:
        interval_frames.append(
            bootstrap_brier_skill_score_intervals(
                aligned_predictions,
                aligned_references,
                scope="patient",
                group_col=patient_col,
                n_bootstrap=n_bootstrap,
                seed=seed,
                ci=ci,
            )
        )
    if event_col is not None:
        interval_frames.append(
            bootstrap_brier_skill_score_intervals(
                aligned_predictions,
                aligned_references,
                scope="event",
                group_col=event_col,
                n_bootstrap=n_bootstrap,
                seed=seed + 10_000,
                ci=ci,
            )
        )
    intervals = (
        pd.concat(interval_frames, ignore_index=True)
        if interval_frames
        else pd.DataFrame(
            columns=[
                "scope",
                "group_col",
                "reference_name",
                "metric",
                "n_rows",
                "n_groups",
                "n_bootstrap",
                "ci",
                "observed",
                "bootstrap_mean",
                "ci_low",
                "ci_high",
                "ci_width",
            ]
        )
    )

    permutation = pd.DataFrame(
        [
            paired_brier_permutation_test(
                aligned_predictions,
                reference,
                reference_name=reference_name,
                group_col=patient_col,
                n_permutations=n_permutations,
                seed=seed + 20_000 + offset,
                alternative=permutation_alternative,
            )
            for offset, (reference_name, reference) in enumerate(aligned_references.items())
        ]
    )
    multiplicity = adjust_p_values(permutation, method=multiplicity_method)
    warnings = _robustness_warnings(
        intervals,
        permutation,
        min_groups=min_groups,
        max_ci_width=max_ci_width,
    )

    metadata = {
        "model_name": model_name,
        "reference_names": list(aligned_references),
        "id_columns": list(id_columns),
        "patient_col": patient_col,
        "event_col": event_col,
        "n_bootstrap": int(n_bootstrap),
        "n_permutations": int(n_permutations),
        "seed": int(seed),
        "ci": float(ci),
        "min_groups": int(min_groups),
        "max_ci_width": float(max_ci_width),
        "multiplicity_method": multiplicity_method,
        "permutation_alternative": permutation_alternative,
        "result_status": result_status,
        "citation_status": citation_status,
        "gate_c_status": gate_c_status,
    }
    return StatisticalRobustnessReport(
        intervals=intervals,
        permutation=permutation,
        multiplicity=multiplicity,
        warnings=warnings,
        metadata=metadata,
    )


def statistical_robustness_markdown(
    report: StatisticalRobustnessReport,
    *,
    title: str = "Statistical Robustness Report",
) -> str:
    warning = ""
    if report.metadata["citation_status"] != "citable_after_gate_c":
        warning = "\n**Citation status:** not citable as a benchmark result.\n"
    warning_count = int(len(report.warnings))
    return f"""# {title}
{warning}
## Metadata

- Model: `{report.metadata["model_name"]}`
- References: `{", ".join(report.metadata["reference_names"])}`
- Result status: `{report.metadata["result_status"]}`
- Citation status: `{report.metadata["citation_status"]}`
- Gate C status: `{report.metadata["gate_c_status"]}`
- Bootstrap samples: `{report.metadata["n_bootstrap"]}`
- Permutations: `{report.metadata["n_permutations"]}`
- Multiplicity method: `{report.metadata["multiplicity_method"]}`
- Warning rows: `{warning_count}`

## Bootstrap Confidence Intervals

{_markdown_table(report.intervals)}

## Paired Permutation Tests

{_markdown_table(report.permutation)}

## Multiple-Comparison Correction

{_markdown_table(report.multiplicity)}

## Robustness Warnings

{_markdown_table(report.warnings)}
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
            elif isinstance(value, np.integer):
                clean[key] = int(value)
            elif isinstance(value, np.floating):
                clean[key] = float(value)
            else:
                clean[key] = value
        records.append(clean)
    return records
