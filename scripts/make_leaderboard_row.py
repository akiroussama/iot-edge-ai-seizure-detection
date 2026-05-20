#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import numpy as np
import pandas as pd

from scripts.make_dataset_report import (
    _events_coverable_by_predictions,
    _filter_events,
    _filter_rows,
    _metric_event_units,
    _requires_bias_acknowledgement,
)
from src.metrics import (
    brier_score,
    event_level_sensitivity,
    expected_calibration_error,
    false_alarm_rate_per_day,
    false_alarm_rate_per_hour,
    median_lead_time,
    monitored_time_seconds,
    time_in_warning,
)
from src.artifacts.registry import load_registry, verify_gate_c_registry
from src.utils.io import read_table, write_table

SCHEMA_PATH = REPO_ROOT / "schemas" / "leaderboard_entry.schema.json"
TEMPLATE_PATH = REPO_ROOT / "schemas" / "leaderboard_template.csv"


def _canonical_columns() -> list[str]:
    with TEMPLATE_PATH.open(encoding="utf-8") as handle:
        return handle.readline().strip().split(",")


def _schema() -> dict[str, Any]:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _clean(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        value = float(value)
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    return value


def _metric_or_none(fn, *args) -> float | None:
    try:
        return _clean(fn(*args))
    except (KeyError, ValueError, TypeError):
        return None


def _valid_prediction_mask(predictions: pd.DataFrame) -> pd.Series:
    return ~predictions.get("is_excluded", pd.Series(False, index=predictions.index)).fillna(False).astype(bool)


def _positive_windows(predictions: pd.DataFrame) -> int | None:
    if "forecast_label" not in predictions.columns:
        return None
    valid = predictions.loc[_valid_prediction_mask(predictions)]
    return int(valid["forecast_label"].fillna(False).astype(bool).sum())


def _window_precision_f1(predictions: pd.DataFrame) -> tuple[float | None, float | None]:
    if not {"forecast_label", "alarm"}.issubset(predictions.columns):
        return None, None
    valid = predictions.loc[_valid_prediction_mask(predictions)]
    if valid.empty:
        return None, None
    y = valid["forecast_label"].fillna(False).astype(bool)
    alarm = valid["alarm"].fillna(False).astype(bool)
    tp = int((alarm & y).sum())
    fp = int((alarm & ~y).sum())
    fn = int((~alarm & y).sum())
    precision = tp / (tp + fp) if tp + fp else None
    recall = tp / (tp + fn) if tp + fn else None
    if precision is None or recall is None or precision + recall == 0:
        return precision, None
    return precision, 2 * precision * recall / (precision + recall)


def _rank_average(values: np.ndarray) -> np.ndarray:
    order = np.argsort(values)
    ranks = np.empty(len(values), dtype=float)
    pos = 0
    while pos < len(values):
        end = pos + 1
        while end < len(values) and values[order[end]] == values[order[pos]]:
            end += 1
        avg_rank = (pos + 1 + end) / 2.0
        ranks[order[pos:end]] = avg_rank
        pos = end
    return ranks


def _auroc(predictions: pd.DataFrame) -> float | None:
    if not {"forecast_label", "risk_score"}.issubset(predictions.columns):
        return None
    valid = predictions.loc[_valid_prediction_mask(predictions)]
    y = valid["forecast_label"].fillna(False).astype(int).to_numpy()
    scores = valid["risk_score"].astype(float).to_numpy()
    positives = int(y.sum())
    negatives = len(y) - positives
    if positives == 0 or negatives == 0:
        return None
    ranks = _rank_average(scores)
    rank_sum_positive = float(ranks[y == 1].sum())
    return (rank_sum_positive - positives * (positives + 1) / 2.0) / (positives * negatives)


def _auprc(predictions: pd.DataFrame) -> float | None:
    if not {"forecast_label", "risk_score"}.issubset(predictions.columns):
        return None
    valid = predictions.loc[_valid_prediction_mask(predictions)]
    y = valid["forecast_label"].fillna(False).astype(int).to_numpy()
    scores = valid["risk_score"].astype(float).to_numpy()
    positives = int(y.sum())
    if positives == 0:
        return None
    order = np.argsort(-scores)
    y_sorted = y[order]
    tp = np.cumsum(y_sorted)
    fp = np.cumsum(1 - y_sorted)
    precision = tp / np.maximum(tp + fp, 1)
    return float((precision * y_sorted).sum() / positives)


def _brier_skill_score(predictions: pd.DataFrame, reference_predictions: pd.DataFrame | None) -> float | None:
    if reference_predictions is None:
        return None
    model_brier = _metric_or_none(brier_score, predictions)
    reference_brier = _metric_or_none(brier_score, reference_predictions)
    if model_brier is None or reference_brier in {None, 0}:
        return None
    return 1.0 - float(model_brier) / float(reference_brier)


def _current_commit() -> str | None:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--short=12", "HEAD"],
            cwd=REPO_ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        return out or None
    except Exception:
        return None


def _validate_row_keys(row: dict[str, Any]) -> None:
    columns = _canonical_columns()
    schema = _schema()
    if columns != schema["required"]:
        raise ValueError("leaderboard template header does not match JSON schema required fields")
    missing = [col for col in columns if col not in row]
    extra = sorted(set(row) - set(columns))
    if missing or extra:
        raise ValueError(f"leaderboard row shape mismatch; missing={missing}, extra={extra}")


def _requires_gate_c_registry(row: dict[str, Any]) -> bool:
    return (
        row["result_status"] == "gate_c_frozen_citable"
        or row["citation_status"] == "citable_after_gate_c"
        or row["gate_c_status"] == "passed"
        or row["split_frozen_status"] in {"frozen_git_tag", "frozen_doi"}
    )


def _validate_gate_c_registry_for_row(row: dict[str, Any], registry_path: str | None) -> None:
    registry_required = _requires_gate_c_registry(row)
    if registry_path is None:
        if registry_required:
            raise ValueError("citable/frozen leaderboard rows require --artifact-registry")
        return

    registry = load_registry(registry_path)
    result = verify_gate_c_registry(
        registry,
        root=REPO_ROOT,
        require_frozen=registry_required,
    )
    if not result["ok"]:
        raise ValueError(f"artifact registry verification failed: {result['errors']}")
    if row["dataset"] != registry.get("dataset"):
        raise ValueError(
            f"artifact registry dataset {registry.get('dataset')!r} does not match row dataset {row['dataset']!r}"
        )
    manifest = registry.get("split_manifest", {})
    registry_split_ref = manifest.get("split_ref")
    if row["split_ref"] and registry_split_ref and row["split_ref"] != registry_split_ref:
        raise ValueError(
            f"artifact registry split_ref {registry_split_ref!r} does not match row split_ref {row['split_ref']!r}"
        )


def build_leaderboard_row(
    *,
    predictions: pd.DataFrame,
    events: pd.DataFrame,
    args: argparse.Namespace,
    reference_predictions: pd.DataFrame | None = None,
) -> dict[str, Any]:
    if _requires_bias_acknowledgement(args.event_filter) and not args.acknowledge_event_filter_bias:
        raise ValueError("event filters require --acknowledge-event-filter-bias")

    filtered_events = _filter_events(events, args.event_filter)
    metric_units = _metric_event_units(
        filtered_events,
        event_unit=args.event_unit,
        cluster_gap_minutes=args.cluster_gap_minutes,
    )
    selected_predictions = _filter_rows(predictions, args.prediction_filter, "prediction")
    selected_reference = (
        _filter_rows(reference_predictions, args.prediction_filter, "reference prediction")
        if reference_predictions is not None
        else None
    )

    sph_minutes = args.sph_minutes or 0.0
    sop_minutes = args.sop_minutes or 0.0
    if args.restrict_events_to_prediction_coverage:
        metric_events = _events_coverable_by_predictions(
            selected_predictions,
            metric_units,
            sph_minutes=sph_minutes,
            sop_minutes=sop_minutes,
        )
    else:
        metric_events = metric_units

    sensitivity = event_level_sensitivity(
        selected_predictions,
        metric_events,
        sph_minutes,
        sop_minutes,
    )
    precision, f1 = _window_precision_f1(selected_predictions)
    monitored_seconds = _metric_or_none(monitored_time_seconds, selected_predictions)
    row: dict[str, Any] = {
        "schema_version": "leaderboard.v1",
        "result_id": args.result_id,
        "result_status": args.result_status,
        "citation_status": args.citation_status,
        "task_type": args.task_type,
        "dataset": args.dataset,
        "cohort": args.cohort,
        "modality": args.modality,
        "model_name": args.model_name,
        "model_family": args.model_family,
        "split_name": args.split_name,
        "split_policy": args.split_policy,
        "split_ref": args.split_ref,
        "horizon_name": args.horizon_name,
        "sph_minutes": args.sph_minutes,
        "sop_minutes": args.sop_minutes,
        "window_seconds": args.window_seconds,
        "stride_seconds": args.stride_seconds,
        "event_unit": args.event_unit,
        "events_source_total": len(events),
        "events_after_filter": len(filtered_events),
        "events_used_for_metrics": len(metric_events),
        "metric_units_used_for_metrics": len(metric_events),
        "prediction_rows": len(selected_predictions),
        "valid_prediction_rows": int(_valid_prediction_mask(selected_predictions).sum()),
        "positive_windows": _positive_windows(selected_predictions),
        "monitored_hours": monitored_seconds / 3600.0 if monitored_seconds is not None else None,
        "n_forecasted_or_detected": sensitivity["n_forecasted"],
        "sensitivity": sensitivity["sensitivity"],
        "false_alarm_rate_per_day": _metric_or_none(
            false_alarm_rate_per_day,
            selected_predictions,
            metric_events,
            sph_minutes,
            sop_minutes,
        ),
        "false_alarm_rate_per_hour": _metric_or_none(
            false_alarm_rate_per_hour,
            selected_predictions,
            metric_events,
            sph_minutes,
            sop_minutes,
        ),
        "time_in_warning": _metric_or_none(time_in_warning, selected_predictions),
        "precision": precision,
        "f1_score": f1,
        "median_lead_time_seconds": _metric_or_none(
            median_lead_time,
            selected_predictions,
            metric_events,
            sph_minutes,
            sop_minutes,
        ),
        "brier_score": _metric_or_none(brier_score, selected_predictions),
        "brier_skill_score": _brier_skill_score(selected_predictions, selected_reference),
        "bss_reference": args.bss_reference if selected_reference is not None else None,
        "expected_calibration_error": _metric_or_none(expected_calibration_error, selected_predictions),
        "auroc": _auroc(selected_predictions),
        "auprc": _auprc(selected_predictions),
        "label_audit_status": args.label_audit_status,
        "gate_b_status": args.gate_b_status,
        "gate_c_status": args.gate_c_status,
        "leakage_status": args.leakage_status,
        "split_frozen_status": args.split_frozen_status,
        "doi_or_prereg_uri": args.doi_or_prereg_uri,
        "edge_target": args.edge_target,
        "quantization": args.quantization,
        "model_size_kb": args.model_size_kb,
        "ram_kb": args.ram_kb,
        "flash_kb": args.flash_kb,
        "latency_ms": args.latency_ms,
        "energy_mj_per_inference": args.energy_mj_per_inference,
        "repo_commit": args.repo_commit or _current_commit(),
        "evidence_uri": args.evidence_uri,
        "notes": args.notes,
    }
    row = {key: _clean(value) for key, value in row.items()}
    _validate_row_keys(row)
    _validate_gate_c_registry_for_row(row, getattr(args, "artifact_registry", None))
    return row


def _write_markdown(row: dict[str, Any], path: Path) -> None:
    status_warning = ""
    if row["citation_status"] != "citable_after_gate_c":
        status_warning = "\n\n**Citation status:** this row is not citable as a benchmark result.\n"
    text = f"""# Leaderboard Row - {row["result_id"]}

{status_warning}
## Identity

- Dataset: `{row["dataset"]}`
- Task: `{row["task_type"]}`
- Model: `{row["model_name"]}`
- Split: `{row["split_name"]}` / `{row["split_policy"]}`
- Horizon: `{row["horizon_name"]}`

## Denominator

- Source events: `{row["events_source_total"]}`
- Events after filter: `{row["events_after_filter"]}`
- Events used for metrics: `{row["events_used_for_metrics"]}`
- Valid prediction rows: `{row["valid_prediction_rows"]}`

## Metrics

- Sensitivity: `{row["sensitivity"]}`
- Forecasted/detected: `{row["n_forecasted_or_detected"]}`
- FAR/day: `{row["false_alarm_rate_per_day"]}`
- TIW: `{row["time_in_warning"]}`
- Brier score: `{row["brier_score"]}`
- Brier Skill Score: `{row["brier_skill_score"]}`
- ECE: `{row["expected_calibration_error"]}`

## Gates

- Label audit: `{row["label_audit_status"]}`
- Gate B: `{row["gate_b_status"]}`
- Gate C: `{row["gate_c_status"]}`
- Leakage: `{row["leakage_status"]}`
- Split frozen: `{row["split_frozen_status"]}`

## Evidence

- Commit: `{row["repo_commit"]}`
- Evidence URI: `{row["evidence_uri"]}`
- Notes: `{row["notes"]}`
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_outputs(row: dict[str, Any], out_csv: Path, out_json: Path | None, out_md: Path | None) -> None:
    columns = _canonical_columns()
    write_table(pd.DataFrame([{col: row[col] for col in columns}]), out_csv)
    if out_json:
        out_json.parent.mkdir(parents=True, exist_ok=True)
        out_json.write_text(json.dumps(row, indent=2), encoding="utf-8")
    if out_md:
        _write_markdown(row, out_md)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Write one leaderboard.v1 row from predictions/events.")
    parser.add_argument("--predictions", required=True)
    parser.add_argument("--events", required=True)
    parser.add_argument("--out-csv", required=True)
    parser.add_argument("--out-json", default=None)
    parser.add_argument("--out-md", default=None)
    parser.add_argument("--reference-predictions", default=None)
    parser.add_argument("--bss-reference", default=None)
    parser.add_argument(
        "--artifact-registry",
        default=None,
        help="Gate C artifact registry JSON. Required for citable/frozen leaderboard rows.",
    )
    parser.add_argument("--result-id", required=True)
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--model-name", required=True)
    parser.add_argument("--task-type", choices=["detection", "forecasting", "edge_cost", "external_context"], default="forecasting")
    parser.add_argument("--cohort", default=None)
    parser.add_argument("--modality", default=None)
    parser.add_argument("--model-family", default=None)
    parser.add_argument("--split-name", default=None)
    parser.add_argument(
        "--split-policy",
        choices=[
            "patient_wise",
            "temporal_recording",
            "recording_wise",
            "loso",
            "external_paper",
            "synthetic",
            "not_applicable",
        ],
        default="patient_wise",
    )
    parser.add_argument("--split-ref", default=None)
    parser.add_argument("--horizon-name", default=None)
    parser.add_argument("--sph-minutes", type=float, default=None)
    parser.add_argument("--sop-minutes", type=float, default=None)
    parser.add_argument("--window-seconds", type=float, default=None)
    parser.add_argument("--stride-seconds", type=float, default=None)
    parser.add_argument("--event-unit", choices=["seizure", "cluster"], default="seizure")
    parser.add_argument("--cluster-gap-minutes", type=float, default=None)
    parser.add_argument("--event-filter", default=None)
    parser.add_argument("--prediction-filter", default=None)
    parser.add_argument("--acknowledge-event-filter-bias", action="store_true")
    parser.add_argument("--restrict-events-to-prediction-coverage", action="store_true")
    parser.add_argument(
        "--result-status",
        choices=[
            "pre_gate_c_exploratory_not_citable",
            "gate_c_frozen_citable",
            "external_sota_context",
            "synthetic_smoke_test_not_citable",
            "invalid_or_retracted",
        ],
        default="pre_gate_c_exploratory_not_citable",
    )
    parser.add_argument(
        "--citation-status",
        choices=[
            "not_citable_pre_gate_c",
            "citable_after_gate_c",
            "external_reported_not_recomputed",
            "synthetic_not_citable",
            "invalid_do_not_use",
        ],
        default="not_citable_pre_gate_c",
    )
    parser.add_argument(
        "--label-audit-status",
        choices=[
            "not_started",
            "sampled_human_attested",
            "full_human_audited",
            "external_reported",
            "not_applicable",
            "failed",
        ],
        default="not_started",
    )
    parser.add_argument("--gate-b-status", choices=["not_started", "partial", "passed", "not_applicable_external", "failed"], default="not_started")
    parser.add_argument("--gate-c-status", choices=["not_started", "partial", "passed", "not_applicable_external", "failed"], default="not_started")
    parser.add_argument(
        "--leakage-status",
        choices=["not_run", "clean", "known_issue", "external_unknown", "not_applicable", "failed"],
        default="not_run",
    )
    parser.add_argument(
        "--split-frozen-status",
        choices=["not_frozen", "frozen_git_tag", "frozen_doi", "external_reported", "not_applicable"],
        default="not_frozen",
    )
    parser.add_argument("--doi-or-prereg-uri", default=None)
    parser.add_argument("--edge-target", default=None)
    parser.add_argument("--quantization", default=None)
    parser.add_argument("--model-size-kb", type=float, default=None)
    parser.add_argument("--ram-kb", type=float, default=None)
    parser.add_argument("--flash-kb", type=float, default=None)
    parser.add_argument("--latency-ms", type=float, default=None)
    parser.add_argument("--energy-mj-per-inference", type=float, default=None)
    parser.add_argument("--repo-commit", default=None)
    parser.add_argument("--evidence-uri", default=None)
    parser.add_argument("--notes", default=None)
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    predictions = read_table(args.predictions)
    events = read_table(args.events)
    reference_predictions = read_table(args.reference_predictions) if args.reference_predictions else None
    row = build_leaderboard_row(
        predictions=predictions,
        events=events,
        reference_predictions=reference_predictions,
        args=args,
    )
    write_outputs(
        row,
        out_csv=Path(args.out_csv),
        out_json=Path(args.out_json) if args.out_json else None,
        out_md=Path(args.out_md) if args.out_md else None,
    )
    print(json.dumps(row, indent=2))


if __name__ == "__main__":
    main()
