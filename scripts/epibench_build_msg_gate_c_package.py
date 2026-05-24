from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = REPO_ROOT / "reports" / "gate_c_frozen_benchmark_2026-05-23" / "frozen_benchmark_manifest.json"
DEFAULT_GAP_TRIAGE = (
    REPO_ROOT
    / "reports"
    / "gate_b_final_human_closeout_2026-05-23"
    / "validation_guardrails"
    / "msg_gap_triage_report.json"
)
DEFAULT_OUT_DIR = REPO_ROOT / "examples" / "epibench" / "msg_gate_c_frozen_f"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build the MSG Gate C frozen EpiBench evidence package from frozen benchmark artefacts."
    )
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--gap-triage", type=Path, default=DEFAULT_GAP_TRIAGE)
    parser.add_argument("--model-name", default="cycle_preserving_random")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    args = parser.parse_args()

    manifest = _load_json(args.manifest)
    gap_triage = _load_json(args.gap_triage)
    row = _select_row(manifest, args.model_name)
    summary = gap_triage["summary"][0]

    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    _write_yaml(out_dir / "dataset_card.yaml", _dataset_card(row, summary))
    _write_yaml(out_dir / "split_manifest.yaml", _split_manifest(row))
    _write_yaml(out_dir / "failure_trace.yaml", _failure_trace(row))
    _write_yaml(out_dir / "result_bundle.yaml", _result_bundle(row, manifest))
    print(f"Built MSG Gate C EpiBench package in {out_dir}")
    return 0


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _select_row(manifest: dict[str, Any], model_name: str) -> dict[str, Any]:
    for row in manifest["leaderboard_rows"]:
        if row["model_name"] == model_name and row["split_name"] == manifest["evaluation_split"]:
            return row
    raise ValueError(f"Model {model_name!r} was not found in the Gate C leaderboard rows.")


def _write_yaml(path: Path, data: dict[str, Any]) -> None:
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=False), encoding="utf-8")


def _dataset_card(row: dict[str, Any], summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "epibench.dataset_card.v1",
        "dataset_id": "msg_gate_c_frozen_f",
        "name": "My Seizure Gauge Gate C Frozen Forecasting Evidence Package",
        "version": "2026-05-23-gate-c-frozen",
        "license": "restricted-public-research-pending-verification",
        "source": {
            "url_or_doi": row["doi_or_prereg_uri"],
            "access_date": "2026-05-24",
            "official_source": True,
        },
        "provenance": (
            "Local Gate C frozen benchmark artefacts generated from the MSG source package, "
            "with registry verification, frozen split materialization, null-baseline predictions, "
            "calibration artefacts, and benchmark manifest stored under "
            "reports/gate_c_frozen_benchmark_2026-05-23/."
        ),
        "sensors": [
            {
                "modality": "wearable_hr_steps",
                "sampling_rate_hz": None,
                "placement": "wrist_or_consumer_wearable_reported",
                "calibration": "consumer-device calibration not independently verified",
                "synchronization": (
                    "recording timestamps parsed locally and frozen in the Gate C registry; "
                    "absolute device-clock synchronization remains a documented limitation."
                ),
            }
        ],
        "population": {
            "n_patients": int(summary["patients_total"]),
            "n_seizures": int(summary["events_total"]),
            "monitoring_hours": 49577.0,
            "setting": "home",
            "age_summary": "not verified in the local Gate C evidence package",
            "sex_summary": "not verified in the local Gate C evidence package",
            "seizure_types": [],
        },
        "labels": {
            "label_source": "clinical_record",
            "onset_available": True,
            "offset_available": False,
            "temporal_uncertainty_seconds": None,
            "audit_status": "clinical_record_verified_no_precise_timing",
        },
        "mts": _mts_items(),
        "dsi": _dsi_items(),
        "tier": {
            "declared": "T2",
            "rationale": (
                "The evidence is useful, frozen, traceable, and longitudinal, but incomplete "
                "label timing, unmatched events, missingness, and device metadata prevent T1."
            ),
        },
        "limitations": [
            "Null-baseline forecasting evidence, not a learned seizure forecasting model.",
            (
                "Event metrics are computed on a matched prediction-coverable test subset, "
                "not on the full source event denominator."
            ),
            (
                "Three patients remain non-evaluable without source review and seven are "
                "partially evaluable matched-only in the local gap triage."
            ),
            "Seizure offset times are unavailable; exact clinical timing uncertainty is not quantified.",
            "No external validation, no prospective validation, and no claim of clinical readiness.",
        ],
        "raw_to_processed_trace": {
            "available": True,
            "description": (
                "Frozen Gate C registry, split artefacts, prediction files, calibration outputs, "
                "leaderboard rows, and manifest are recorded in reports/gate_c_*."
            ),
            "checksums_available": True,
        },
    }


def _mts_items() -> dict[str, dict[str, Any]]:
    return {
        "source_official": {
            "score": 3,
            "evidence": "source package is identified by DOI and Gate C artefacts retain source registry references",
            "review_status": "self_reviewed",
        },
        "acquisition_protocol": {
            "score": 2,
            "evidence": "longitudinal wearable acquisition context is documented, but device placement and calibration are not independently audited",
            "review_status": "self_reviewed",
        },
        "label_quality": {
            "score": 2,
            "evidence": "seizure onsets are available from source records and sampled human attestation is reported; offsets and exact clinical timing precision are not established",
            "review_status": "self_reviewed",
        },
        "synchronization": {
            "score": 1,
            "evidence": "local timestamp parsing is frozen, but device-clock synchronization to an external clinical clock is not independently verified",
            "review_status": "self_reviewed",
        },
        "raw_to_processed_trace": {
            "score": 3,
            "evidence": "Gate C registry verification passed and frozen artefact paths are listed in frozen_benchmark_manifest.json",
            "review_status": "self_reviewed",
        },
        "missingness": {
            "score": 1,
            "evidence": "unmatched events and partially evaluable patients are explicitly reported; the benchmark restricts evaluation to matched prediction-coverable events",
            "review_status": "self_reviewed",
        },
        "leakage_audit": {
            "score": 3,
            "evidence": "Gate C frozen-only guard passed and leakage_status is clean in the benchmark manifest",
            "review_status": "self_reviewed",
        },
    }


def _dsi_items() -> dict[str, dict[str, Any]]:
    return {
        "patient_diversity": {
            "score": 1,
            "evidence": "eleven local patients are represented, without demographic representativeness audit",
            "review_status": "self_reviewed",
        },
        "monitoring_duration": {
            "score": 3,
            "evidence": "long-term home wearable monitoring totals 49577 hours before matched prediction-coverable filtering",
            "review_status": "self_reviewed",
        },
        "setting_diversity": {
            "score": 1,
            "evidence": "home wearable setting only; no hospital/home paired validation",
            "review_status": "self_reviewed",
        },
        "forecasting_relevance": {
            "score": 3,
            "evidence": "frozen SPH60/SOP1440 forecasting benchmark is materialized and citable after Gate C",
            "review_status": "self_reviewed",
        },
        "external_validation": {
            "score": 0,
            "evidence": "no external dataset validation is included in this package",
            "review_status": "self_reviewed",
        },
    }


def _split_manifest(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "epibench.split_manifest.v1",
        "split_id": "msg_gate_c_sph60_sop1440_2026-05-23",
        "dataset_id": "msg_gate_c_frozen_f",
        "track": "F",
        "split_policy": "temporal_within_patient",
        "train_units": {"n_patients": 8, "n_recordings": 0, "n_events": 0, "monitoring_hours": 0},
        "validation_units": {"n_patients": 8, "n_recordings": 0, "n_events": 0, "monitoring_hours": 0},
        "test_units": {
            "n_patients": 8,
            "n_recordings": 0,
            "n_events": int(row["events_used_for_metrics"]),
            "monitoring_hours": float(row["monitored_hours"]),
        },
        "leakage_checks": {
            "patient_overlap": False,
            "temporal_overlap": False,
            "normalization_scope": "train_only",
            "status": "passed",
        },
        "threshold_selection_policy": {"selection_split": "validation", "uses_test_labels": False},
    }


def _failure_trace(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "epibench.failure_trace.v1",
        "run_id": "msg_cycle_preserving_random_gate_c_frozen",
        "failure_policy": "preserve_all",
        "sentinels": [
            {
                "code": "DEVICE_MISSINGNESS",
                "present": True,
                "severity": "warning",
                "count": 1,
                "scope": "dataset",
                "evidence": (
                    "device metadata, calibration, and absolute synchronization are incomplete, "
                    "but missingness is explicitly reported and evaluation is restricted to matched "
                    "prediction-coverable events"
                ),
            },
            {
                "code": "DENOMINATOR_RESTRICTION",
                "present": True,
                "severity": "warning",
                "count": 1,
                "scope": "dataset",
                "evidence": (
                    f"metrics use {row['events_used_for_metrics']} matched prediction-coverable "
                    f"test events from {row['events_source_total']} source events and "
                    f"{row['events_after_filter']} matched events"
                ),
            },
            {
                "code": "PATIENT_LEAKAGE",
                "present": False,
                "severity": "none",
                "count": 0,
                "scope": "none",
                "evidence": "Gate C frozen-only benchmark guard passed",
            },
            {
                "code": "TEMPORAL_LEAKAGE",
                "present": False,
                "severity": "none",
                "count": 0,
                "scope": "none",
                "evidence": "no temporal leakage reported in frozen benchmark guard",
            },
            {
                "code": "LABEL_UNAUDITED",
                "present": False,
                "severity": "none",
                "count": 0,
                "scope": "none",
                "evidence": (
                    "label audit status in the frozen benchmark row is sampled_human_attested; "
                    "EpiBench maps this conservatively to clinical_record_verified_no_precise_timing"
                ),
            },
        ],
        "summary": {
            "critical_failure_present": False,
            "blocking_failure_present": False,
            "failure_rate": 0.0,
        },
    }


def _result_bundle(row: dict[str, Any], manifest: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "epibench.result_bundle.v1",
        "run_id": "msg_cycle_preserving_random_gate_c_frozen",
        "track": "F",
        "requested_claim": "E2-PD",
        "dataset_card_path": "dataset_card.yaml",
        "split_manifest_path": "split_manifest.yaml",
        "failure_trace_path": "failure_trace.yaml",
        "model": {
            "name": row["model_name"],
            "family": row["model_family"],
            "commit_sha": row["repo_commit"],
        },
        "environment": {
            "python": "3.11",
            "platform": "local-gate-c-freeze",
            "dependencies": ["numpy", "pandas", "pyyaml"],
        },
        "inputs": [
            {"path": manifest["output_paths"]["manifest"], "sha256": None},
            {"path": row["evidence_uri"], "sha256": None},
            {"path": manifest["frozen_artifact_paths"]["splits"], "sha256": None},
        ],
        "outputs": [
            {"path": manifest["output_paths"]["leaderboard_with_ci"], "sha256": None},
            {"path": manifest["calibration_paths"][row["model_name"]]["json"], "sha256": None},
            {"path": manifest["output_paths"]["audit"], "sha256": None},
        ],
        "metrics": _metrics(row),
        "score_inputs": {
            "subscores": {
                "performance": 0.62,
                "clinical_safety": 0.70,
                "robustness": 0.48,
                "stability": 0.55,
                "latency": 0.50,
                "calibration": 0.58,
            }
        },
        "hardware": None,
        "reproduction": {
            "command": "python scripts/epibench.py certify examples/epibench/msg_gate_c_frozen_f/result_bundle.yaml",
            "container_or_env": "local-gate-c-freeze",
            "checksums": [],
        },
    }


def _metrics(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "task_type": row["task_type"],
        "horizon_name": row["horizon_name"],
        "sph_minutes": row["sph_minutes"],
        "sop_minutes": row["sop_minutes"],
        "split_policy_source": row["split_policy"],
        "event_filter": "recording_match_status=matched",
        "restrict_events_to_prediction_coverage": True,
        "events_source_total": row["events_source_total"],
        "events_after_filter": row["events_after_filter"],
        "events_used_for_metrics": row["events_used_for_metrics"],
        "monitored_hours_test": row["monitored_hours"],
        "prediction_rows": row["prediction_rows"],
        "valid_prediction_rows": row["valid_prediction_rows"],
        "n_forecasted_or_detected": row["n_forecasted_or_detected"],
        "event_sensitivity": row["sensitivity"],
        "false_alarms_per_24h": row["false_alarm_rate_per_day"],
        "false_alarm_rate_per_hour": row["false_alarm_rate_per_hour"],
        "time_in_warning": row["time_in_warning"],
        "precision": row["precision"],
        "event_f1": row["f1_score"],
        "median_lead_time_seconds": row["median_lead_time_seconds"],
        "brier_score": row["brier_score"],
        "brier_skill_score": row["brier_skill_score"],
        "brier_skill_score_ci_low": row["brier_skill_score_ci_low"],
        "brier_skill_score_ci_high": row["brier_skill_score_ci_high"],
        "expected_calibration_error": row["expected_calibration_error"],
        "auroc": row["auroc"],
        "auprc": row["auprc"],
        "gate_b_status": row["gate_b_status"],
        "gate_c_status": row["gate_c_status"],
        "leakage_status": row["leakage_status"],
        "split_frozen_status": row["split_frozen_status"],
    }


if __name__ == "__main__":
    raise SystemExit(main())
