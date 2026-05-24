from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any

import yaml

from src.epibench.validation import load_structured, validate_artifact


SZCORE_TO_EPIBENCH_METRICS = {
    "sensitivity": "event_sensitivity",
    "event_sensitivity": "event_sensitivity",
    "precision": "event_precision",
    "event_precision": "event_precision",
    "f1": "event_f1",
    "f1_score": "event_f1",
    "event_f1": "event_f1",
    "false_positives_per_day": "false_alarms_per_24h",
    "false_alarms_per_24h": "false_alarms_per_24h",
    "false_alarm_rate_per_day": "false_alarms_per_24h",
    "detection_delay_seconds_median": "detection_latency_seconds_median",
    "detection_delay_seconds_p95": "detection_latency_seconds_p95",
}

SZCORE_OFFICIAL_EVENT_RESULTS_TO_EPIBENCH_METRICS = {
    "sensitivity": "event_sensitivity",
    "precision": "event_precision",
    "f1": "event_f1",
    "fpRate": "false_alarms_per_24h",
}


def map_szcore_metrics_to_result_bundle(
    szcore_metrics_path: str | Path,
    base_bundle_path: str | Path,
    output_path: str | Path,
) -> dict[str, Any]:
    """Map compatible seizure event-scoring outputs into an EpiBench Result Bundle.

    This bridge intentionally does not replace SzCORE. It consumes an already-produced event
    scoring output and records the mapped values inside an EpiBench bundle so that dataset
    evidence, failures, and claim gates can be applied.
    """
    szcore_metrics = load_structured(szcore_metrics_path)
    base_bundle_path = Path(base_bundle_path)
    base_dir = base_bundle_path.parent
    base_bundle = validate_artifact("result-bundle", base_bundle_path)
    mapped = deepcopy(base_bundle)
    mapped.setdefault("metrics", {})

    official_event_results = szcore_metrics.get("event_results")
    if isinstance(official_event_results, dict):
        source_metrics = official_event_results
        metric_map = SZCORE_OFFICIAL_EVENT_RESULTS_TO_EPIBENCH_METRICS
        source_prefix = "event_results."
        mapped["metrics"]["external_event_scoring_official_contract"] = (
            "szcore-evaluation.evaluate_dataset:event_results"
        )
        mapped["metrics"]["event_scoring_source"] = "szcore-evaluation official output contract"
    else:
        source_metrics = szcore_metrics.get("metrics", szcore_metrics)
        metric_map = SZCORE_TO_EPIBENCH_METRICS
        source_prefix = ""
    if not isinstance(source_metrics, dict):
        raise ValueError("SzCORE metrics input must be a mapping or contain a 'metrics' mapping")

    mapped_fields: dict[str, str] = {}
    for source_key, target_key in metric_map.items():
        if source_key in source_metrics:
            mapped["metrics"][target_key] = source_metrics[source_key]
            mapped_fields[f"{source_prefix}{source_key}"] = target_key

    if "event_matching_rule" in szcore_metrics:
        mapped["metrics"]["event_matching_rule"] = szcore_metrics["event_matching_rule"]
    if "scoring_tool" in szcore_metrics:
        mapped["metrics"]["event_scoring_source"] = _format_scoring_tool(szcore_metrics["scoring_tool"])

    mapped["metrics"]["external_event_scoring_mapped"] = True
    mapped["metrics"]["external_event_scoring_relationship"] = "MAP"
    mapped["metrics"]["external_event_scoring_mapped_fields"] = ",".join(
        f"{source}->{target}" for source, target in sorted(mapped_fields.items())
    )
    for path_key in ("dataset_card_path", "split_manifest_path", "failure_trace_path"):
        raw_path = Path(str(mapped[path_key]))
        if not raw_path.is_absolute():
            mapped[path_key] = str((base_dir / raw_path).resolve())

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(yaml.safe_dump(mapped, sort_keys=False), encoding="utf-8")
    validate_artifact("result-bundle", output_path)
    return mapped


def _format_scoring_tool(scoring_tool: Any) -> str:
    if isinstance(scoring_tool, str):
        return scoring_tool
    if isinstance(scoring_tool, dict):
        name = scoring_tool.get("name")
        version = scoring_tool.get("version")
        if name and version:
            return f"{name}=={version}"
        return json.dumps(scoring_tool, sort_keys=True)
    return str(scoring_tool)


def import_szcore_metrics_as_result_bundle(
    szcore_metrics_path: str | Path,
    dataset_card_path: str | Path,
    split_manifest_path: str | Path,
    failure_trace_path: str | Path,
    output_path: str | Path,
    run_id: str,
    requested_claim: str,
    model_name: str,
    model_family: str,
    commit_sha: str,
    subscores: dict[str, float],
) -> dict[str, Any]:
    split_manifest = validate_artifact("split", split_manifest_path)
    validate_artifact("dataset-card", dataset_card_path)
    validate_artifact("failure-trace", failure_trace_path)
    required_axes = {"performance", "clinical_safety", "robustness", "stability", "latency"}
    missing_axes = sorted(required_axes - set(subscores))
    if missing_axes:
        raise ValueError(f"Missing required Epi-Score subscores for SzCORE import: {missing_axes}")

    base_bundle = {
        "schema_version": "epibench.result_bundle.v1",
        "run_id": run_id,
        "track": split_manifest["track"],
        "requested_claim": requested_claim,
        "dataset_card_path": str(Path(dataset_card_path).resolve()),
        "split_manifest_path": str(Path(split_manifest_path).resolve()),
        "failure_trace_path": str(Path(failure_trace_path).resolve()),
        "model": {
            "name": model_name,
            "family": model_family,
            "commit_sha": commit_sha,
        },
        "environment": {
            "python": "external-import",
            "platform": "external-szcore-compatible-output",
            "dependencies": ["szcore-compatible-event-scoring-export"],
        },
        "inputs": [{"path": str(Path(szcore_metrics_path).resolve()), "sha256": None}],
        "outputs": [],
        "metrics": {},
        "score_inputs": {"subscores": subscores},
        "hardware": None,
        "reproduction": {
            "command": "external SzCORE-compatible event scoring followed by epibench import-szcore",
            "container_or_env": "external",
            "checksums": [],
        },
    }
    temp_path = Path(output_path).with_suffix(".base.tmp.yaml")
    temp_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path.write_text(yaml.safe_dump(base_bundle, sort_keys=False), encoding="utf-8")
    try:
        return map_szcore_metrics_to_result_bundle(szcore_metrics_path, temp_path, output_path)
    finally:
        temp_path.unlink(missing_ok=True)
