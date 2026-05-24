from __future__ import annotations

from pathlib import Path
from typing import Any

from src.epibench.scoring import compute_epi_score
from src.epibench.spec import load_spec, min_claim
from src.epibench.validation import SchemaValidationError, load_schema, validate_against_schema, validate_artifact


def certify_result_bundle(
    result_bundle_path: str | Path,
    spec_path: str | Path | None = None,
) -> dict[str, Any]:
    spec = load_spec(spec_path) if spec_path else load_spec()
    bundle_path = Path(result_bundle_path)
    bundle = validate_artifact("result-bundle", bundle_path)
    base_dir = bundle_path.parent

    dataset_card = validate_artifact("dataset-card", _resolve_artifact(base_dir, bundle["dataset_card_path"]))
    split_manifest = validate_artifact("split", _resolve_artifact(base_dir, bundle["split_manifest_path"]))
    failure_trace_path = _resolve_artifact(base_dir, bundle["failure_trace_path"])
    failure_trace = validate_artifact("failure-trace", failure_trace_path)
    _validate_cross_artifact_consistency(bundle, dataset_card, split_manifest, failure_trace)

    score = compute_epi_score(bundle, spec)
    dataset_tier_evaluation = evaluate_dataset_tier(dataset_card, spec)
    ceilings, blocking_reasons, forbidden_phrases = _compute_ceilings(
        bundle=bundle,
        dataset_card=dataset_card,
        dataset_tier_evaluation=dataset_tier_evaluation,
        split_manifest=split_manifest,
        failure_trace=failure_trace,
        spec=spec,
    )
    final_claim = min_claim(list(ceilings.values()) + [bundle["requested_claim"]], spec)
    badges = _compute_badges(
        final_claim=final_claim,
        bundle=bundle,
        dataset_card=dataset_card,
        dataset_tier_evaluation=dataset_tier_evaluation,
        split_manifest=split_manifest,
        failure_trace=failure_trace,
        validation_complete=True,
    )
    report = {
        "schema_version": "epibench.claim_eligibility.v1",
        "run_id": bundle["run_id"],
        "epibench_version": spec["epibench_version"],
        "requested_claim": bundle["requested_claim"],
        "final_claim": final_claim,
        "ceilings": ceilings,
        "score": {
            "epi_score": score["epi_score"],
            "axis_scores": score["axis_scores"],
            "floor_penalty_applied": score["floor_penalty_applied"],
        },
        "dataset_tier_evaluation": dataset_tier_evaluation,
        "badges": badges,
        "blocking_reasons": blocking_reasons,
        "forbidden_phrases": forbidden_phrases,
    }

    _validate_generated_claim_report(report)
    return report


def render_markdown_report(report: dict[str, Any]) -> str:
    badges = " ".join(f"`{badge}`" for badge in report["badges"]) or "None"
    blockers = "\n".join(f"- {reason}" for reason in report["blocking_reasons"]) or "- None"
    forbidden = "\n".join(f"- {phrase}" for phrase in report["forbidden_phrases"]) or "- None"
    ceilings = "\n".join(f"- {name}: `{claim}`" for name, claim in report["ceilings"].items())
    axes = "\n".join(
        f"- {axis}: {value:.3f}" for axis, value in report["score"]["axis_scores"].items()
    )
    tier_eval = report["dataset_tier_evaluation"]
    missing_core = ", ".join(tier_eval["missing_core_mts_items"]) or "None"
    return f"""# EpiBench Claim Eligibility Report

Run: `{report['run_id']}`  
EpiBench version: `{report['epibench_version']}`  
Requested claim: `{report['requested_claim']}`  
Final claim: `{report['final_claim']}`  
Epi-Score: `{report['score']['epi_score']:.3f}`

## Badges

{badges}

## Claim Ceilings

{ceilings}

## Score Axes

{axes}

Floor penalty applied: `{report['score']['floor_penalty_applied']}`

## Dataset Tier Evaluation

- Declared tier: `{tier_eval['declared_tier']}`
- Effective tier: `{tier_eval['effective_tier']}`
- MTS mean: `{tier_eval['mts_mean']:.3f}`
- MTS item floor: `{tier_eval['mts_item_floor']}`
- Missing core MTS items: `{missing_core}`
- Downgraded: `{tier_eval['downgraded']}`

## Blocking Reasons

{blockers}

## Forbidden Phrases

{forbidden}

## Certification Boundary

EpiBench-certified means scientifically certified under EpiBench evidence rules. It does not mean
clinically approved, clinically safe, regulatory approved, or ready for deployment as a medical
device.
"""


def _resolve_artifact(base_dir: Path, raw_path: str) -> Path:
    path = Path(raw_path)
    return path if path.is_absolute() else base_dir / path


def _validate_cross_artifact_consistency(
    bundle: dict[str, Any],
    dataset_card: dict[str, Any],
    split_manifest: dict[str, Any],
    failure_trace: dict[str, Any],
) -> None:
    errors = []
    if bundle["run_id"] != failure_trace["run_id"]:
        errors.append("result bundle run_id does not match failure trace run_id")
    if dataset_card["dataset_id"] != split_manifest["dataset_id"]:
        errors.append("dataset card dataset_id does not match split manifest dataset_id")
    if bundle["track"] != split_manifest["track"]:
        errors.append("result bundle track does not match split manifest track")
    if errors:
        rendered = "\n".join(f"- {error}" for error in errors)
        raise SchemaValidationError(f"EpiBench cross-artifact consistency failed:\n{rendered}")


def evaluate_dataset_tier(dataset_card: dict[str, Any], spec: dict[str, Any]) -> dict[str, Any]:
    """Compute the effective dataset tier from MTS evidence, fail-closed.

    The author-declared tier is preserved for audit, but it does not control certification.
    """
    declared = dataset_card["tier"]["declared"]
    mts_items = dataset_card.get("mts", {})
    core_items = spec.get("dataset_tier_assignment", {}).get("core_mts_items", [])
    missing_score = int(spec.get("dataset_tier_assignment", {}).get("missing_core_mts_item_score", 0))

    scores_by_item: dict[str, int] = {}
    for name, item in mts_items.items():
        scores_by_item[name] = int(item["score"])
    missing_core = [name for name in core_items if name not in scores_by_item]
    for name in missing_core:
        scores_by_item[name] = missing_score

    if not scores_by_item:
        mts_mean = 0.0
        mts_item_floor = 0
    else:
        values = list(scores_by_item.values())
        mts_mean = sum(values) / len(values)
        mts_item_floor = min(values)

    effective = "T3"
    for tier in ("T1", "T2", "T3"):
        tier_spec = spec["dataset_tiers"][tier]
        if (
            mts_mean >= float(tier_spec["minimum_mts_mean"])
            and mts_item_floor >= int(tier_spec["minimum_mts_item_floor"])
        ):
            effective = tier
            break

    rank = {"T3": 0, "T2": 1, "T1": 2}
    return {
        "declared_tier": declared,
        "effective_tier": effective,
        "mts_mean": round(mts_mean, 3),
        "mts_item_floor": mts_item_floor,
        "missing_core_mts_items": missing_core,
        "downgraded": rank[effective] < rank[declared],
    }


def _compute_ceilings(
    bundle: dict[str, Any],
    dataset_card: dict[str, Any],
    dataset_tier_evaluation: dict[str, Any],
    split_manifest: dict[str, Any],
    failure_trace: dict[str, Any],
    spec: dict[str, Any],
) -> tuple[dict[str, str], list[str], list[str]]:
    ceilings: dict[str, str] = {}
    blocking_reasons: list[str] = []
    forbidden_phrases: list[str] = []

    tier = dataset_tier_evaluation["effective_tier"]
    if dataset_tier_evaluation["downgraded"]:
        blocking_reasons.append(
            "Declared dataset tier exceeded effective MTS-derived tier; certification used effective tier."
        )
    split_policy = split_manifest["split_policy"]
    if split_policy in {"external_dataset", "leave_one_site_out"}:
        dataset_ceiling_key = "allowed_claim_ceiling_with_external_validation"
    elif split_policy == "prospective_multisite":
        dataset_ceiling_key = "allowed_claim_ceiling_with_prospective_validation"
    else:
        dataset_ceiling_key = "allowed_claim_ceiling_without_external_validation"
    ceilings["dataset_tier"] = spec["dataset_tiers"][tier][dataset_ceiling_key]
    ceilings["split_policy"] = spec["split_claim_ceilings"][split_policy]
    ceilings["label_audit"] = spec["label_audit_claim_ceilings"][dataset_card["labels"]["audit_status"]]

    if split_manifest["leakage_checks"]["status"] != "passed":
        ceilings["leakage_audit"] = "E1"
        blocking_reasons.append("Split leakage audit did not pass.")
    elif split_manifest["leakage_checks"]["patient_overlap"] or split_manifest["leakage_checks"]["temporal_overlap"]:
        ceilings["leakage_audit"] = "E1"
        blocking_reasons.append("Split manifest reports patient or temporal overlap.")
    else:
        ceilings["leakage_audit"] = "E4"

    if split_manifest["threshold_selection_policy"]["uses_test_labels"]:
        ceilings["threshold_policy"] = "E1"
        blocking_reasons.append("Threshold selection uses test labels.")
    else:
        ceilings["threshold_policy"] = "E4"

    failure_ceiling = "E4"
    for sentinel in failure_trace["sentinels"]:
        if not sentinel["present"]:
            continue
        code = sentinel["code"]
        severity = sentinel["severity"]
        if code in {"PATIENT_LEAKAGE", "TEMPORAL_LEAKAGE", "SPLIT_NONCOMPLIANT", "NAN_OR_INF_OUTPUT", "LABEL_UNAUDITED"}:
            failure_ceiling = min_claim([failure_ceiling, "E1"], spec)
            blocking_reasons.append(f"Blocking sentinel present: {code}.")
        elif code == "FAR_EXPLOSION" and severity in {"major", "critical"}:
            failure_ceiling = min_claim([failure_ceiling, "E1"], spec)
            blocking_reasons.append("False alarm burden exceeds blocking budget.")
        elif code == "POST_EVENT_ALARM" and bundle["track"] == "W":
            failure_ceiling = min_claim([failure_ceiling, "E1"], spec)
            blocking_reasons.append("Early-warning track contains post-event alarms counted as success.")
        elif severity == "critical":
            failure_ceiling = min_claim([failure_ceiling, "E1"], spec)
            blocking_reasons.append(f"Critical sentinel present: {code}.")

        if code == "HARDWARE_UNMEASURED":
            forbidden_phrases.extend(["real-time", "on-device", "edge-ready"])
        if code == "LATENCY_BUDGET_EXCEEDED":
            forbidden_phrases.extend(["real-time", "edge-ready"])
    ceilings["failure_status"] = failure_ceiling

    if bundle["track"] == "E":
        hardware = bundle.get("hardware")
        if not hardware or hardware.get("latency_ms_p95") is None:
            ceilings["hardware_evidence"] = "E1"
            blocking_reasons.append("Embedded viability track lacks measured p95 hardware latency.")
            forbidden_phrases.extend(["real-time", "on-device", "edge-ready"])
        else:
            ceilings["hardware_evidence"] = "E4"
    elif _hardware_unmeasured(failure_trace):
        ceilings["hardware_evidence"] = "E4"
        forbidden_phrases.extend(["real-time", "on-device", "edge-ready"])
    elif _hardware_evidence_non_citable(bundle):
        ceilings["hardware_evidence"] = "E4"
        forbidden_phrases.extend(["real-time", "on-device", "edge-ready"])
    else:
        ceilings["hardware_evidence"] = "E4"

    if not _track_consistency(bundle, split_manifest):
        ceilings["track_consistency"] = "E1"
        blocking_reasons.append("Result bundle track does not match split manifest track.")
    else:
        ceilings["track_consistency"] = "E4"

    return ceilings, sorted(set(blocking_reasons)), sorted(set(forbidden_phrases))


def _compute_badges(
    final_claim: str,
    bundle: dict[str, Any],
    dataset_card: dict[str, Any],
    dataset_tier_evaluation: dict[str, Any],
    split_manifest: dict[str, Any],
    failure_trace: dict[str, Any],
    validation_complete: bool,
) -> list[str]:
    badges = [f"EpiBench-Dataset-{dataset_tier_evaluation['effective_tier']}"]
    if validation_complete and failure_trace["failure_policy"] == "preserve_all":
        badges.append("EpiBench-Run-Complete")
        badges.append("EpiBench-Failure-Transparent")
    if final_claim in {"E1", "E2-PD", "E2-PI", "E3", "E4"}:
        badges.append(f"EpiBench-Claim-{final_claim}")
    if _leakage_checked(split_manifest, failure_trace):
        badges.append("EpiBench-Leakage-Checked")
    hardware = bundle.get("hardware")
    if (
        hardware
        and hardware.get("latency_ms_p95") is not None
        and not _sentinel_present(failure_trace, "HARDWARE_UNMEASURED")
        and not _hardware_evidence_non_citable(bundle)
    ):
        badges.append("EpiBench-Edge-Measured")
    return badges


def _leakage_checked(split_manifest: dict[str, Any], failure_trace: dict[str, Any]) -> bool:
    checks = split_manifest["leakage_checks"]
    return (
        checks["status"] == "passed"
        and not checks["patient_overlap"]
        and not checks["temporal_overlap"]
        and not _sentinel_present(failure_trace, "PATIENT_LEAKAGE")
        and not _sentinel_present(failure_trace, "TEMPORAL_LEAKAGE")
    )


def _sentinel_present(failure_trace: dict[str, Any], code: str) -> bool:
    return any(sentinel["code"] == code and sentinel["present"] for sentinel in failure_trace["sentinels"])


def _hardware_unmeasured(failure_trace: dict[str, Any]) -> bool:
    return _sentinel_present(failure_trace, "HARDWARE_UNMEASURED")


def _hardware_evidence_non_citable(bundle: dict[str, Any]) -> bool:
    hardware = bundle.get("hardware")
    if not hardware:
        return False
    target = str(hardware.get("target", "")).casefold()
    commit = str(bundle.get("model", {}).get("commit_sha", "")).casefold()
    platform = str(bundle.get("environment", {}).get("platform", "")).casefold()
    return "demo" in target or commit.startswith("demo-") or "demo" in commit or "demo" in platform


def _track_consistency(bundle: dict[str, Any], split_manifest: dict[str, Any]) -> bool:
    return bundle["track"] == split_manifest["track"]


def _validate_generated_claim_report(report: dict[str, Any]) -> None:
    """Validate a generated claim report before returning it to the CLI."""
    schema = load_schema("claim-eligibility")
    errors = validate_against_schema(report, schema)
    if errors:
        rendered = "\n".join(f"- {error}" for error in errors)
        raise SchemaValidationError(f"Generated claim eligibility report is invalid:\n{rendered}")
