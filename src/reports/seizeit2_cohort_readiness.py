from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
from typing import Any

import pandas as pd


CLAIM_STATUS = "seizeit2_cohort_readiness_pre_gate_c_not_citable"
DEFAULT_REQUIRED_SPLITS = ("train", "val", "test")
DEFAULT_REQUIRED_TASKS = ("ictal_detection", "short_early_warning", "long_horizon_forecasting")
DEFAULT_REQUIRED_MODALITY_TRACKS = ("ecg", "acc", "bte_eeg", "multimodal")


@dataclass(frozen=True)
class SeizeIT2CohortReadinessConfig:
    min_patients_for_full_cohort: int = 100
    min_events_for_full_cohort: int = 100
    required_splits: tuple[str, ...] = DEFAULT_REQUIRED_SPLITS
    required_task_names: tuple[str, ...] = DEFAULT_REQUIRED_TASKS
    required_modality_tracks: tuple[str, ...] = DEFAULT_REQUIRED_MODALITY_TRACKS
    require_expected_counts: bool = True


@dataclass(frozen=True)
class SeizeIT2CohortReadinessReport:
    summary: pd.DataFrame
    blockers: pd.DataFrame
    warnings: pd.DataFrame
    manifest: pd.DataFrame
    metadata: dict[str, Any]


def _require_columns(frame: pd.DataFrame, required: set[str], name: str) -> None:
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"{name} missing required columns: {missing}")


def _validate_config(config: SeizeIT2CohortReadinessConfig) -> None:
    if config.min_patients_for_full_cohort < 1:
        raise ValueError("min_patients_for_full_cohort must be >= 1")
    if config.min_events_for_full_cohort < 1:
        raise ValueError("min_events_for_full_cohort must be >= 1")
    if not config.required_splits:
        raise ValueError("required_splits cannot be empty")
    if not config.required_task_names:
        raise ValueError("required_task_names cannot be empty")
    if not config.required_modality_tracks:
        raise ValueError("required_modality_tracks cannot be empty")


def _dataframe_hash(frame: pd.DataFrame) -> str:
    return sha256(frame.to_csv(index=False).encode("utf-8")).hexdigest()


def _numeric_metric(count_summary: pd.DataFrame, metric: str) -> int | None:
    row = count_summary.loc[count_summary["metric"].astype(str).eq(metric)]
    if row.empty:
        return None
    value = pd.to_numeric(row.iloc[0].get("observed"), errors="coerce")
    if pd.isna(value):
        return None
    return int(value)


def _count_status(count_summary: pd.DataFrame, metric: str) -> str | None:
    row = count_summary.loc[count_summary["metric"].astype(str).eq(metric)]
    if row.empty:
        return None
    value = row.iloc[0].get("count_status")
    return None if pd.isna(value) else str(value)


def _append_issue(
    rows: list[dict[str, Any]],
    *,
    issue_code: str,
    severity: str,
    detail: str,
    affected_rows: int | None = None,
) -> None:
    rows.append(
        {
            "issue_code": issue_code,
            "severity": severity,
            "detail": detail,
            "affected_rows": affected_rows,
            "claim_status": CLAIM_STATUS,
        }
    )


def _missing_values(values: set[str], required: tuple[str, ...]) -> list[str]:
    return [value for value in required if value not in values]


def _clean_value(value: Any) -> Any:
    if value is pd.NA or value is pd.NaT:
        return None
    if isinstance(value, float) and pd.isna(value):
        return None
    if hasattr(value, "item"):
        try:
            return value.item()
        except ValueError:
            return value
    return value


def table_records(frame: pd.DataFrame) -> list[dict[str, Any]]:
    records = []
    for record in frame.to_dict(orient="records"):
        records.append({key: _clean_value(value) for key, value in record.items()})
    return records


def build_seizeit2_cohort_readiness_report(
    track_df: pd.DataFrame,
    count_summary: pd.DataFrame,
    *,
    gate_b_status: str = "not_started",
    gate_c_status: str = "not_started",
    config: SeizeIT2CohortReadinessConfig | None = None,
) -> SeizeIT2CohortReadinessReport:
    """Assess whether SeizeIT2 artifacts support a full-cohort claim.

    This is a guardrail over readiness/count tables. It does not evaluate model
    predictions and cannot make a benchmark result citable.
    """
    cfg = config or SeizeIT2CohortReadinessConfig()
    _validate_config(cfg)
    _require_columns(
        track_df,
        {
            "split_name",
            "task_name",
            "modality_track",
            "official_split_status",
            "track_ready",
        },
        "track_df",
    )
    _require_columns(count_summary, {"metric", "observed", "count_status"}, "count_summary")

    blockers: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []

    if gate_b_status != "passed":
        _append_issue(
            blockers,
            issue_code="gate_b_not_passed",
            severity="blocker",
            detail=f"Gate B status is {gate_b_status!r}; human label audit is not complete.",
        )
    if gate_c_status != "passed":
        _append_issue(
            blockers,
            issue_code="gate_c_not_passed",
            severity="blocker",
            detail=f"Gate C status is {gate_c_status!r}; artifacts are not frozen/citable.",
        )

    patients = _numeric_metric(count_summary, "patients")
    events = _numeric_metric(count_summary, "events")
    if patients is None:
        _append_issue(
            blockers,
            issue_code="patients_count_missing",
            severity="blocker",
            detail="Count summary does not include a patients metric.",
        )
    elif patients < cfg.min_patients_for_full_cohort:
        _append_issue(
            blockers,
            issue_code="patients_below_full_cohort_threshold",
            severity="blocker",
            detail=(
                f"Observed patients={patients}; required minimum is "
                f"{cfg.min_patients_for_full_cohort} for a full-cohort claim."
            ),
            affected_rows=patients,
        )
    if events is None:
        _append_issue(
            blockers,
            issue_code="events_count_missing",
            severity="blocker",
            detail="Count summary does not include an events metric.",
        )
    elif events < cfg.min_events_for_full_cohort:
        _append_issue(
            blockers,
            issue_code="events_below_full_cohort_threshold",
            severity="blocker",
            detail=(
                f"Observed events={events}; required minimum is "
                f"{cfg.min_events_for_full_cohort} for a full-cohort claim."
            ),
            affected_rows=events,
        )

    if cfg.require_expected_counts:
        for metric in ("patients", "recordings", "events"):
            status = _count_status(count_summary, metric)
            if status is None:
                _append_issue(
                    blockers,
                    issue_code=f"{metric}_expected_count_missing",
                    severity="blocker",
                    detail=f"Count summary does not include expected-count status for {metric}.",
                )
            elif status == "expected_count_not_provided":
                _append_issue(
                    blockers,
                    issue_code=f"{metric}_expected_count_not_provided",
                    severity="blocker",
                    detail=f"Expected published count for {metric} was not supplied.",
                )
            elif status != "matches_expected_count":
                _append_issue(
                    blockers,
                    issue_code=f"{metric}_count_mismatch",
                    severity="blocker",
                    detail=f"Expected-count check for {metric} has status {status!r}.",
                )

    split_statuses = set(track_df["official_split_status"].dropna().astype(str))
    if split_statuses != {"official_manifest_applied"}:
        bad_rows = int(track_df["official_split_status"].ne("official_manifest_applied").sum())
        _append_issue(
            blockers,
            issue_code="official_split_manifest_not_clean",
            severity="blocker",
            detail=f"Official split statuses present: {sorted(split_statuses)}.",
            affected_rows=bad_rows,
        )

    split_values = set(track_df["split_name"].dropna().astype(str))
    missing_splits = _missing_values(split_values, cfg.required_splits)
    if missing_splits:
        _append_issue(
            blockers,
            issue_code="required_splits_missing",
            severity="blocker",
            detail=f"Missing required splits: {missing_splits}.",
            affected_rows=len(missing_splits),
        )

    task_values = set(track_df["task_name"].dropna().astype(str))
    missing_tasks = _missing_values(task_values, cfg.required_task_names)
    if missing_tasks:
        _append_issue(
            blockers,
            issue_code="required_tasks_missing",
            severity="blocker",
            detail=f"Missing required tasks: {missing_tasks}.",
            affected_rows=len(missing_tasks),
        )

    modality_values = set(track_df["modality_track"].dropna().astype(str))
    missing_modalities = _missing_values(modality_values, cfg.required_modality_tracks)
    if missing_modalities:
        _append_issue(
            blockers,
            issue_code="required_modality_tracks_missing",
            severity="blocker",
            detail=f"Missing required modality tracks: {missing_modalities}.",
            affected_rows=len(missing_modalities),
        )

    ready = track_df["track_ready"].fillna(False).astype(bool)
    ready_df = track_df.loc[ready]
    for split_name in cfg.required_splits:
        for task_name in cfg.required_task_names:
            rows = ready_df.loc[
                ready_df["split_name"].astype(str).eq(split_name)
                & ready_df["task_name"].astype(str).eq(task_name)
            ]
            if rows.empty:
                _append_issue(
                    blockers,
                    issue_code="required_ready_track_missing",
                    severity="blocker",
                    detail=f"No ready track for split={split_name}, task={task_name}.",
                )

    not_ready_rows = int((~ready).sum())
    if not_ready_rows:
        _append_issue(
            warnings,
            issue_code="non_ready_track_rows_present",
            severity="warning",
            detail="Some task/modality/split rows are not ready; keep them as negative readiness rows.",
            affected_rows=not_ready_rows,
        )

    blockers_df = pd.DataFrame(
        blockers,
        columns=["issue_code", "severity", "detail", "affected_rows", "claim_status"],
    )
    warnings_df = pd.DataFrame(
        warnings,
        columns=["issue_code", "severity", "detail", "affected_rows", "claim_status"],
    )
    readiness_status = "ready_for_gate_c_review" if blockers_df.empty else "blocked"
    full_cohort_claim_status = (
        "candidate_after_gate_b_c" if blockers_df.empty else "blocked_not_full_cohort_ready"
    )
    summary = pd.DataFrame(
        [
            {
                "readiness_status": readiness_status,
                "full_cohort_claim_status": full_cohort_claim_status,
                "gate_b_status": gate_b_status,
                "gate_c_status": gate_c_status,
                "patients_observed": patients,
                "events_observed": events,
                "track_rows": int(len(track_df)),
                "ready_track_rows": int(ready.sum()),
                "blockers": int(len(blockers_df)),
                "warnings": int(len(warnings_df)),
                "claim_status": CLAIM_STATUS,
            }
        ]
    )
    metadata: dict[str, Any] = {
        "claim_status": CLAIM_STATUS,
        "result_status": "cohort_readiness_guardrail_not_model_result",
        "gate_b_status": gate_b_status,
        "gate_c_status": gate_c_status,
        "config": asdict(cfg),
        "track_hash": _dataframe_hash(track_df),
        "count_summary_hash": _dataframe_hash(count_summary),
        "summary_hash": _dataframe_hash(summary),
        "blockers_hash": _dataframe_hash(blockers_df),
        "warnings_hash": _dataframe_hash(warnings_df),
    }
    manifest = pd.DataFrame([metadata])
    return SeizeIT2CohortReadinessReport(
        summary=summary,
        blockers=blockers_df,
        warnings=warnings_df,
        manifest=manifest,
        metadata=metadata,
    )


def _markdown_table(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "_No rows._"
    headers = [str(column) for column in frame.columns]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for _, row in frame.iterrows():
        lines.append("| " + " | ".join("" if pd.isna(row[col]) else str(row[col]) for col in frame.columns) + " |")
    return "\n".join(lines)


def seizeit2_cohort_readiness_markdown(
    report: SeizeIT2CohortReadinessReport,
    *,
    title: str = "SeizeIT2 Cohort Readiness",
) -> str:
    return f"""# {title}

**Citation status:** not citable as a benchmark result before Gate C.

This report is a full-cohort claim guardrail. It consumes SeizeIT2 readiness
tables and count summaries, then records why a cohort-level claim is blocked or
ready for Gate C review. It does not train or score a model.

## Summary

{_markdown_table(report.summary)}

## Blockers

{_markdown_table(report.blockers)}

## Warnings

{_markdown_table(report.warnings)}

## Interpretation Rules

- `blocked_not_full_cohort_ready` means the current artifacts cannot support a
  full SeizeIT2 cohort claim.
- Count mismatches or missing expected counts must be resolved before any paper
  wording claims full-cohort comparability.
- Gate B and Gate C must both pass before any citable SeizeIT2 result is reported.
- Non-ready track rows are negative readiness findings, not hidden exclusions.

## Manifest

- Claim status: `{report.metadata["claim_status"]}`
- Result status: `{report.metadata["result_status"]}`
- Track hash: `{report.metadata["track_hash"]}`
- Count-summary hash: `{report.metadata["count_summary_hash"]}`
"""
