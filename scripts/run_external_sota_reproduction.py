#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.make_leaderboard_row import build_leaderboard_row, write_outputs  # noqa: E402
from src.reports.external_sota_reproduction import (  # noqa: E402
    ExternalPredictionColumns,
    ExternalSOTAReference,
    build_external_sota_manifest,
    external_sota_reproduction_markdown,
    standardize_external_predictions,
)
from src.utils.io import read_table, write_table  # noqa: E402


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Normalize one external SOTA-family prediction table and score it with the EpiTwin leaderboard runner."
    )
    parser.add_argument("--predictions", required=True)
    parser.add_argument("--events", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--result-id", required=True)
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--model-name", required=True)
    parser.add_argument("--source-name", required=True)
    parser.add_argument("--source-citation", required=True)
    parser.add_argument("--source-url", default=None)
    parser.add_argument("--source-doi", default=None)
    parser.add_argument("--source-code-uri", default=None)
    parser.add_argument("--original-metric-summary", default=None)
    parser.add_argument("--license-notes", default=None)
    parser.add_argument("--reproduction-family", required=True)
    parser.add_argument(
        "--reproduction-status",
        choices=[
            "recomputed_under_epitwin_runner",
            "adapter_smoke_test_not_sota_claim",
            "blocked_modality_or_split_mismatch",
            "external_reported_not_recomputed",
        ],
        default="adapter_smoke_test_not_sota_claim",
    )
    parser.add_argument("--mismatch-notes", required=True)
    parser.add_argument("--patient-col", default="patient_id")
    parser.add_argument("--recording-col", default="recording_id")
    parser.add_argument("--window-start-col", default="window_start")
    parser.add_argument("--window-end-col", default="window_end")
    parser.add_argument("--risk-col", default="risk_score")
    parser.add_argument("--alarm-col", default="alarm")
    parser.add_argument("--no-alarm-col", action="store_true")
    parser.add_argument("--alarm-threshold", type=float, default=None)
    parser.add_argument("--label-col", default="forecast_label")
    parser.add_argument("--excluded-col", default="is_excluded")
    parser.add_argument("--no-excluded-col", action="store_true")
    parser.add_argument("--split-col", default="split")
    parser.add_argument("--no-split-col", action="store_true")
    parser.add_argument(
        "--task-type",
        choices=["detection", "forecasting", "edge_cost", "external_context"],
        default="forecasting",
    )
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
        default="external_paper",
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
    parser.add_argument("--reference-predictions", default=None)
    parser.add_argument("--bss-reference", default=None)
    parser.add_argument(
        "--result-status",
        choices=[
            "pre_gate_c_exploratory_not_citable",
            "gate_c_frozen_citable",
            "external_sota_context",
            "synthetic_smoke_test_not_citable",
            "invalid_or_retracted",
        ],
        default="external_sota_context",
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
    parser.add_argument(
        "--gate-b-status",
        choices=["not_started", "partial", "passed", "not_applicable_external", "failed"],
        default="not_started",
    )
    parser.add_argument(
        "--gate-c-status",
        choices=["not_started", "partial", "passed", "not_applicable_external", "failed"],
        default="not_started",
    )
    parser.add_argument(
        "--leakage-status",
        choices=["not_run", "clean", "known_issue", "external_unknown", "not_applicable", "failed"],
        default="external_unknown",
    )
    parser.add_argument(
        "--split-frozen-status",
        choices=["not_frozen", "frozen_git_tag", "frozen_doi", "external_reported", "not_applicable"],
        default="external_reported",
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
    parser.add_argument("--title", default="External SOTA Reproduction Dossier")
    return parser


def _leaderboard_args(args: argparse.Namespace) -> argparse.Namespace:
    return argparse.Namespace(
        predictions=None,
        events=None,
        out_csv=None,
        out_json=None,
        out_md=None,
        reference_predictions=args.reference_predictions,
        bss_reference=args.bss_reference,
        artifact_registry=None,
        result_id=args.result_id,
        dataset=args.dataset,
        model_name=args.model_name,
        task_type=args.task_type,
        cohort=args.cohort,
        modality=args.modality,
        model_family=args.model_family or args.reproduction_family,
        split_name=args.split_name,
        split_policy=args.split_policy,
        split_ref=args.split_ref,
        horizon_name=args.horizon_name,
        sph_minutes=args.sph_minutes,
        sop_minutes=args.sop_minutes,
        window_seconds=args.window_seconds,
        stride_seconds=args.stride_seconds,
        event_unit=args.event_unit,
        cluster_gap_minutes=args.cluster_gap_minutes,
        event_filter=args.event_filter,
        prediction_filter=args.prediction_filter,
        acknowledge_event_filter_bias=args.acknowledge_event_filter_bias,
        restrict_events_to_prediction_coverage=args.restrict_events_to_prediction_coverage,
        result_status=args.result_status,
        citation_status=args.citation_status,
        label_audit_status=args.label_audit_status,
        gate_b_status=args.gate_b_status,
        gate_c_status=args.gate_c_status,
        leakage_status=args.leakage_status,
        split_frozen_status=args.split_frozen_status,
        doi_or_prereg_uri=args.doi_or_prereg_uri,
        edge_target=args.edge_target,
        quantization=args.quantization,
        model_size_kb=args.model_size_kb,
        ram_kb=args.ram_kb,
        flash_kb=args.flash_kb,
        latency_ms=args.latency_ms,
        energy_mj_per_inference=args.energy_mj_per_inference,
        repo_commit=args.repo_commit,
        evidence_uri=args.evidence_uri,
        notes=args.notes or args.mismatch_notes,
    )


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    columns = ExternalPredictionColumns(
        patient_col=args.patient_col,
        recording_col=args.recording_col,
        window_start_col=args.window_start_col,
        window_end_col=args.window_end_col,
        risk_col=args.risk_col,
        alarm_col=None if args.no_alarm_col else args.alarm_col,
        label_col=args.label_col,
        excluded_col=None if args.no_excluded_col else args.excluded_col,
        split_col=None if args.no_split_col else args.split_col,
    )
    reference = ExternalSOTAReference(
        source_name=args.source_name,
        source_citation=args.source_citation,
        source_url=args.source_url,
        source_doi=args.source_doi,
        source_code_uri=args.source_code_uri,
        original_metric_summary=args.original_metric_summary,
        license_notes=args.license_notes,
        reproduction_family=args.reproduction_family,
        reproduction_status=args.reproduction_status,
        mismatch_notes=args.mismatch_notes,
    )
    standardized = standardize_external_predictions(
        read_table(args.predictions),
        columns=columns,
        alarm_threshold=args.alarm_threshold,
    )
    events = read_table(args.events)
    reference_predictions = read_table(args.reference_predictions) if args.reference_predictions else None
    leaderboard_row = build_leaderboard_row(
        predictions=standardized,
        events=events,
        reference_predictions=reference_predictions,
        args=_leaderboard_args(args),
    )

    out_dir = Path(args.out_dir)
    predictions_out = out_dir / "external_sota_predictions.csv"
    leaderboard_csv = out_dir / "external_sota_leaderboard_row.csv"
    leaderboard_json = out_dir / "external_sota_leaderboard_row.json"
    leaderboard_md = out_dir / "external_sota_leaderboard_row.md"
    manifest_csv = out_dir / "external_sota_manifest.csv"
    manifest_json = out_dir / "external_sota_manifest.json"
    report_md = out_dir / "external_sota_report.md"
    write_table(standardized, predictions_out)
    write_outputs(leaderboard_row, leaderboard_csv, leaderboard_json, leaderboard_md)
    manifest = build_external_sota_manifest(
        reference=reference,
        standardized_predictions=standardized,
        leaderboard_row=leaderboard_row,
    )
    write_table(manifest, manifest_csv)
    manifest_json.parent.mkdir(parents=True, exist_ok=True)
    manifest_json.write_text(
        json.dumps(manifest.to_dict(orient="records")[0], indent=2),
        encoding="utf-8",
    )
    report_md.write_text(
        external_sota_reproduction_markdown(manifest, title=args.title),
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "out_dir": str(out_dir),
                "result_id": args.result_id,
                "reproduction_status": args.reproduction_status,
                "leaderboard_csv": str(leaderboard_csv),
                "manifest_csv": str(manifest_csv),
                "report_md": str(report_md),
                "citation_status": leaderboard_row["citation_status"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
