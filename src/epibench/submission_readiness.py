from __future__ import annotations

from pathlib import Path
from typing import Any

from src.epibench.certification import certify_result_bundle
from src.epibench.spec import claim_at_or_above, load_spec
from src.epibench.validation import load_structured, validate_artifact


def assess_submission_readiness(
    bundle_paths: list[str | Path],
    gate_path: str | Path,
    spec_path: str | Path | None = None,
) -> dict[str, Any]:
    spec = load_spec(spec_path) if spec_path else load_spec()
    gate = load_structured(gate_path)
    package_reports = [
        _assess_one(Path(path), gate=gate, spec=spec, spec_path=spec_path) for path in bundle_paths
    ]
    submission_grade = [pkg for pkg in package_reports if pkg["submission_grade"]]
    operational = [
        pkg
        for pkg in package_reports
        if pkg["submission_grade"]
        and claim_at_or_above(pkg["claim_report"]["final_claim"], gate["minimum_operational_claim"], spec)
    ]
    status = (
        "passed"
        if len(submission_grade) >= int(gate["minimum_packages"])
        and len(operational) >= int(gate["minimum_operational_packages"])
        else "failed"
    )
    blockers: list[str] = []
    if len(submission_grade) < int(gate["minimum_packages"]):
        blockers.append(
            f"Only {len(submission_grade)} submission-grade package(s); "
            f"{gate['minimum_packages']} required."
        )
    if len(operational) < int(gate["minimum_operational_packages"]):
        blockers.append(
            f"Only {len(operational)} operational package(s) at "
            f"{gate['minimum_operational_claim']} or higher; "
            f"{gate['minimum_operational_packages']} required."
        )
    return {
        "schema_version": "epibench.submission_readiness_report.v1",
        "gate_id": gate["gate_id"],
        "epibench_version": gate["epibench_version"],
        "status": status,
        "package_count": len(package_reports),
        "submission_grade_count": len(submission_grade),
        "operational_package_count": len(operational),
        "blockers": blockers,
        "packages": package_reports,
    }


def _assess_one(
    bundle_path: Path,
    gate: dict[str, Any],
    spec: dict[str, Any],
    spec_path: str | Path | None,
) -> dict[str, Any]:
    bundle = validate_artifact("result-bundle", bundle_path)
    base_dir = bundle_path.parent
    dataset_card = validate_artifact("dataset-card", _resolve(base_dir, bundle["dataset_card_path"]))
    split_manifest = validate_artifact("split", _resolve(base_dir, bundle["split_manifest_path"]))
    validate_artifact("failure-trace", _resolve(base_dir, bundle["failure_trace_path"]))
    claim_report = certify_result_bundle(bundle_path, spec_path)

    blockers: list[str] = []
    warnings: list[str] = []
    track = bundle["track"]
    pop = dataset_card["population"]
    test_units = split_manifest["test_units"]

    if bundle["model"]["commit_sha"] in set(gate.get("disallowed_model_commit_values", [])):
        blockers.append("Model commit is a demo placeholder, not a real reproducible commit.")
    if split_manifest["split_policy"] in set(gate.get("disallowed_split_policies", [])):
        blockers.append(f"Split policy is not submission-grade: {split_manifest['split_policy']}.")
    if dataset_card["labels"]["audit_status"] in set(gate.get("blocking_label_audit_statuses", [])):
        blockers.append(f"Label audit is not submission-grade: {dataset_card['labels']['audit_status']}.")
    if claim_report["final_claim"] == "E1":
        blockers.append("Final claim is E1; package is useful but not operational submission-grade evidence.")
    if claim_report["blocking_reasons"]:
        blockers.extend(f"Certification blocker: {reason}" for reason in claim_report["blocking_reasons"])
    if claim_report["dataset_tier_evaluation"]["downgraded"]:
        blockers.append("Dataset tier was downgraded by MTS effective-tier calculation.")

    min_patients = int(gate["minimum_patients"].get(track, 0))
    min_events = int(gate["minimum_events"].get(track, 0))
    patient_count = max(int(pop["n_patients"]), int(test_units["n_patients"]))
    event_count = max(int(pop["n_seizures"]), int(test_units["n_events"]))
    if patient_count < min_patients:
        blockers.append(f"Insufficient patients for track {track}: {patient_count} < {min_patients}.")
    if event_count < min_events:
        blockers.append(f"Insufficient events for track {track}: {event_count} < {min_events}.")

    if track == "D" and gate.get("required_for_detection_track", {}).get(
        "require_event_scoring_mapping_or_native_event_fields", False
    ):
        metrics = bundle["metrics"]
        mapping_flag = gate["required_for_detection_track"]["accepted_external_mapping_flag"]
        native_fields = gate["required_for_detection_track"]["accepted_native_event_fields"]
        native_ok = all(field in metrics for field in native_fields)
        mapped_ok = bool(metrics.get(mapping_flag))
        if not native_ok and not mapped_ok:
            blockers.append("Detection package lacks native or mapped event-scoring fields.")

    if split_manifest["split_policy"] in {"patient_dependent", "temporal_within_patient"}:
        warnings.append("Package may be valid but cannot support patient-independent claims.")
    if dataset_card["population"]["setting"] == "hospital" and track in {"D", "W", "F"}:
        warnings.append("Hospital evidence must not be generalized to home IoT without external support.")

    return {
        "bundle_path": str(bundle_path),
        "run_id": bundle["run_id"],
        "track": track,
        "dataset_id": dataset_card["dataset_id"],
        "final_claim": claim_report["final_claim"],
        "effective_tier": claim_report["dataset_tier_evaluation"]["effective_tier"],
        "submission_grade": not blockers,
        "blockers": sorted(set(blockers)),
        "warnings": sorted(set(warnings)),
        "claim_report": claim_report,
    }


def _resolve(base_dir: Path, raw_path: str) -> Path:
    path = Path(raw_path)
    return path if path.is_absolute() else base_dir / path
