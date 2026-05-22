from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from src.active.audit_selection import (
    DEFAULT_AUDIT_ID_COLUMNS,
    DEFAULT_AUDIT_SELECTION_WEIGHTS,
    build_audit_target_table,
    select_audit_targets,
)
from src.reports.label_audit import REVIEW_DECISION_COLUMNS


@dataclass(frozen=True)
class GateBAuditPackage:
    candidates: pd.DataFrame
    review_sheet: pd.DataFrame
    manifest: dict[str, Any]
    markdown: str


def _clean_value(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        value = float(value)
    if isinstance(value, float) and (np.isnan(value) or np.isinf(value)):
        return None
    if isinstance(value, (pd.Timestamp,)):
        return value.isoformat()
    if isinstance(value, (list, tuple)):
        return [_clean_value(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _clean_value(item) for key, item in value.items()}
    if pd.isna(value):
        return None
    return value


def _value_counts(df: pd.DataFrame, column: str) -> dict[str, int]:
    if column not in df.columns or df.empty:
        return {}
    counts = df[column].fillna("missing").astype(str).value_counts().sort_index()
    return {str(key): int(value) for key, value in counts.items()}


def _score_summary(df: pd.DataFrame) -> dict[str, Any]:
    if df.empty or "active_audit_score" not in df.columns:
        return {
            "min": None,
            "median": None,
            "max": None,
        }
    scores = pd.to_numeric(df["active_audit_score"], errors="coerce")
    return {
        "min": _clean_value(scores.min()),
        "median": _clean_value(scores.median()),
        "max": _clean_value(scores.max()),
    }


def _selected_preview(review_sheet: pd.DataFrame, max_rows: int = 12) -> str:
    if review_sheet.empty:
        return "_No events selected._"
    columns = [
        column
        for column in (
            "audit_rank",
            "patient_id",
            "recording_id",
            "seizure_start",
            "active_audit_score",
            "dominant_acquisition",
            "selection_reason",
        )
        if column in review_sheet.columns
    ]
    rows = review_sheet[columns].head(max_rows).copy()
    if "active_audit_score" in rows.columns:
        rows["active_audit_score"] = pd.to_numeric(
            rows["active_audit_score"],
            errors="coerce",
        ).map(lambda value: "" if pd.isna(value) else f"{value:.3f}")
    header = "| " + " | ".join(columns) + " |"
    divider = "| " + " | ".join("---" for _ in columns) + " |"
    body = []
    for _, row in rows.iterrows():
        values = []
        for column in columns:
            value = _clean_value(row[column])
            values.append("" if value is None else str(value).replace("|", "\\|"))
        body.append("| " + " | ".join(values) + " |")
    return "\n".join([header, divider, *body])


def gate_b_audit_package_markdown(
    *,
    manifest: dict[str, Any],
    review_sheet: pd.DataFrame,
    review_sheet_path: str | None = None,
    candidates_path: str | None = None,
    validation_path: str | None = None,
) -> str:
    review_sheet_path = review_sheet_path or "gate_b_audit_review_sheet.csv"
    candidates_path = candidates_path or "gate_b_audit_candidates.csv"
    validation_path = validation_path or "gate_b_audit_validation.csv"
    reference_names = manifest.get("reference_prediction_names") or []
    reference_text = ", ".join(reference_names) if reference_names else "none"
    min_events = manifest["min_events_required"]
    return f"""# Gate B Audit Acceleration Package

**Status:** pending human review; this is not a Gate B pass.

## Scope

- Dataset: `{manifest["dataset"]}`
- Audit source: `{manifest.get("audit_source") or "not recorded"}`
- Prediction source: `{manifest.get("prediction_source") or "not provided"}`
- Reference predictions: `{reference_text}`
- Selection strategy: `{manifest["selection_strategy"]}`
- Requested budget: `{manifest["requested_budget"]}`
- Selected events: `{manifest["selected_events"]}`
- Candidate events: `{manifest["candidate_events"]}`
- Unique selected patients: `{manifest["selected_unique_patients"]}`
- Minimum event budget met: `{manifest["minimum_event_budget_met"]}`

## Why These Events Were Selected

Acquisition mix:

```text
{manifest["dominant_acquisition_counts"]}
```

Active-score summary:

```text
{manifest["selected_score_summary"]}
```

## Selected Review Queue

{_selected_preview(review_sheet)}

## Human Review Instructions

Fill every reviewer decision column in `{review_sheet_path}`:

- `source_onset_verified`
- `source_recording_verified`
- `sph_sop_labels_pass`
- `ictal_exclusion_pass`
- `postictal_exclusion_pass`
- `right_censoring_pass`
- `decision`

Allowed decisions are `PASS`, `FAIL`, `UNCERTAIN`, and `NEEDS_SOURCE_REVIEW`.
The selector never marks labels as correct; it only decides what the human
should inspect first.

After review, run:

```bash
python scripts/check_label_audit_review.py --review-sheet {review_sheet_path} --out {validation_path} --min-events {min_events}
```

If any row fails or needs source review, correct the parser/labels first, then
regenerate labels, windows, splits, leakage audits, and this package. Only a
completed and passing human review can support Gate B.

## Files

- Selected review sheet: `{review_sheet_path}`
- Full candidate scores: `{candidates_path}`
- Validation output after human review: `{validation_path}`

## Guardrails

- This package is audit prioritization only.
- It is not a benchmark result.
- It is not citable as model performance.
- Gate C remains blocked until Gate B is complete and frozen artifacts are
  registered.
"""


def build_gate_b_audit_package(
    audit_df: pd.DataFrame,
    *,
    dataset: str,
    predictions_df: pd.DataFrame | None = None,
    reference_predictions: dict[str, pd.DataFrame] | None = None,
    budget: int = 10,
    selection_strategy: str = "patient_spread",
    id_columns: tuple[str, ...] = DEFAULT_AUDIT_ID_COLUMNS,
    weights: dict[str, float] | None = None,
    min_events_required: int = 5,
    audit_source: str | None = None,
    prediction_source: str | None = None,
) -> GateBAuditPackage:
    if budget <= 0:
        raise ValueError("budget must be positive")
    if min_events_required <= 0:
        raise ValueError("min_events_required must be positive")
    references = reference_predictions or {}
    candidates = build_audit_target_table(
        audit_df,
        predictions_df=predictions_df,
        reference_predictions=references,
        id_columns=id_columns,
        weights=weights,
    )
    review_sheet = select_audit_targets(
        candidates,
        budget=budget,
        selection_strategy=selection_strategy,
    )
    selected_events = int(len(review_sheet))
    candidate_events = int(len(candidates))
    selected_unique_patients = (
        int(review_sheet["patient_id"].nunique(dropna=True))
        if "patient_id" in review_sheet.columns
        else 0
    )
    manifest = {
        "package_status": "pending_human_review_not_gate_b_pass",
        "result_status": "audit_prioritization_not_citable",
        "dataset": dataset,
        "audit_source": audit_source,
        "prediction_source": prediction_source,
        "reference_prediction_names": sorted(references),
        "selection_strategy": selection_strategy,
        "requested_budget": int(budget),
        "candidate_events": candidate_events,
        "selected_events": selected_events,
        "selected_unique_patients": selected_unique_patients,
        "min_events_required": int(min_events_required),
        "minimum_event_budget_met": bool(selected_events >= min_events_required),
        "id_columns": list(id_columns),
        "weights": dict(weights or DEFAULT_AUDIT_SELECTION_WEIGHTS),
        "dominant_acquisition_counts": _value_counts(review_sheet, "dominant_acquisition"),
        "selected_score_summary": _score_summary(review_sheet),
        "required_human_decision_columns": list(REVIEW_DECISION_COLUMNS),
        "gate_b_status": "not_passed_pending_human_review",
        "gate_c_status": "blocked_until_gate_b_and_freeze",
        "citation_status": "not_citable_audit_prioritization",
    }
    manifest = {key: _clean_value(value) for key, value in manifest.items()}
    markdown = gate_b_audit_package_markdown(
        manifest=manifest,
        review_sheet=review_sheet,
    )
    return GateBAuditPackage(
        candidates=candidates,
        review_sheet=review_sheet,
        manifest=manifest,
        markdown=markdown,
    )
