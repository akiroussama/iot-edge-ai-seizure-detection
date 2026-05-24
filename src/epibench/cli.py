from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from src.epibench.certification import certify_result_bundle, render_markdown_report
from src.epibench.scoring import compute_epi_score
from src.epibench.inter_reviewer import build_inter_reviewer_report
from src.epibench.spec import load_spec
from src.epibench.submission_readiness import assess_submission_readiness
from src.epibench.szcore_bridge import (
    import_szcore_metrics_as_result_bundle,
    map_szcore_metrics_to_result_bundle,
)
from src.epibench.validation import load_structured, validate_artifact


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="epibench", description="EpiBench reference CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    _add_validate_command(sub, "validate-dataset-card", "dataset-card")
    _add_validate_command(sub, "validate-split", "split")
    _add_validate_command(sub, "validate-result-bundle", "result-bundle")
    _add_validate_command(sub, "validate-failure-trace", "failure-trace")
    _add_validate_command(sub, "validate-sota-registry", "sota-registry")

    score_parser = sub.add_parser("score", help="Compute the Epi-Score for a result bundle")
    score_parser.add_argument("result_bundle")
    score_parser.add_argument("--spec", default=None)

    certify_parser = sub.add_parser("certify", help="Generate a claim eligibility report")
    certify_parser.add_argument("result_bundle")
    certify_parser.add_argument("--spec", default=None)
    certify_parser.add_argument("--out", default=None, help="Optional JSON output path")
    certify_parser.add_argument("--report", default=None, help="Optional Markdown report path")

    render_parser = sub.add_parser("render-report", help="Render a JSON claim report to Markdown")
    render_parser.add_argument("claim_report")
    render_parser.add_argument("--out", required=True)

    conformance_parser = sub.add_parser("run-conformance-suite", help="Run EpiBench conformance cases")
    conformance_parser.add_argument("suite")
    conformance_parser.add_argument("--out", default=None)

    map_szcore_parser = sub.add_parser("map-szcore", help="Map compatible SzCORE-style metrics into an EpiBench Result Bundle")
    map_szcore_parser.add_argument("--metrics", required=True)
    map_szcore_parser.add_argument("--base-bundle", required=True)
    map_szcore_parser.add_argument("--out", required=True)

    import_szcore_parser = sub.add_parser("import-szcore", help="Create an EpiBench Result Bundle from a SzCORE-style metric export")
    import_szcore_parser.add_argument("--metrics", required=True)
    import_szcore_parser.add_argument("--dataset-card", required=True)
    import_szcore_parser.add_argument("--split-manifest", required=True)
    import_szcore_parser.add_argument("--failure-trace", required=True)
    import_szcore_parser.add_argument("--run-id", required=True)
    import_szcore_parser.add_argument("--requested-claim", required=True)
    import_szcore_parser.add_argument("--model-name", required=True)
    import_szcore_parser.add_argument("--model-family", required=True)
    import_szcore_parser.add_argument("--commit-sha", required=True)
    import_szcore_parser.add_argument("--subscore", action="append", default=[], help="Axis score as axis=value")
    import_szcore_parser.add_argument("--out", required=True)

    readiness_parser = sub.add_parser("assess-submission-readiness", help="Assess real evidence packages against a Q1 submission gate")
    readiness_parser.add_argument("--gate", default="configs/epibench/submission_readiness_gate_v1.yaml")
    readiness_parser.add_argument("--bundle", action="append", required=True)
    readiness_parser.add_argument("--out", default=None)

    inter_parser = sub.add_parser("inter-reviewer-report", help="Compute MTS/DSI inter-reviewer agreement")
    inter_parser.add_argument("reviews")
    inter_parser.add_argument("--out", default=None)

    args = parser.parse_args(argv)
    if args.command.startswith("validate-"):
        data = validate_artifact(args.artifact_type, args.path)
        print(json.dumps({"status": "valid", "schema_version": data.get("schema_version")}, indent=2))
        return 0
    if args.command == "score":
        spec = load_spec(args.spec) if args.spec else load_spec()
        bundle = validate_artifact("result-bundle", args.result_bundle)
        print(json.dumps(compute_epi_score(bundle, spec), indent=2))
        return 0
    if args.command == "certify":
        report = certify_result_bundle(args.result_bundle, args.spec)
        _write_or_print_json(report, args.out)
        if args.report:
            _write_text(args.report, render_markdown_report(report))
        return 0
    if args.command == "render-report":
        report = load_structured(args.claim_report)
        _write_text(args.out, render_markdown_report(report))
        return 0
    if args.command == "run-conformance-suite":
        result = run_conformance_suite(args.suite)
        _write_or_print_json(result, args.out)
        return 0 if result["status"] == "passed" else 1
    if args.command == "map-szcore":
        mapped = map_szcore_metrics_to_result_bundle(args.metrics, args.base_bundle, args.out)
        print(json.dumps({"status": "mapped", "run_id": mapped["run_id"], "out": args.out}, indent=2))
        return 0
    if args.command == "import-szcore":
        bundle = import_szcore_metrics_as_result_bundle(
            szcore_metrics_path=args.metrics,
            dataset_card_path=args.dataset_card,
            split_manifest_path=args.split_manifest,
            failure_trace_path=args.failure_trace,
            output_path=args.out,
            run_id=args.run_id,
            requested_claim=args.requested_claim,
            model_name=args.model_name,
            model_family=args.model_family,
            commit_sha=args.commit_sha,
            subscores=_parse_subscores(args.subscore),
        )
        print(json.dumps({"status": "imported", "run_id": bundle["run_id"], "out": args.out}, indent=2))
        return 0
    if args.command == "assess-submission-readiness":
        report = assess_submission_readiness(args.bundle, args.gate)
        _write_or_print_json(report, args.out)
        return 0 if report["status"] == "passed" else 1
    if args.command == "inter-reviewer-report":
        report = build_inter_reviewer_report(args.reviews)
        _write_or_print_json(report, args.out)
        return 0 if report["status"] == "passed" else 1
    raise AssertionError(args.command)


def _add_validate_command(sub: Any, name: str, artifact_type: str) -> None:
    parser = sub.add_parser(name, help=f"Validate an EpiBench {artifact_type} artifact")
    parser.add_argument("path")
    parser.set_defaults(artifact_type=artifact_type)


def _write_or_print_json(data: dict[str, Any], out: str | None) -> None:
    text = json.dumps(data, indent=2)
    if out:
        _write_text(out, text + "\n")
    else:
        print(text)


def _write_text(path: str | Path, text: str) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _parse_subscores(raw_values: list[str]) -> dict[str, float]:
    subscores: dict[str, float] = {}
    for raw in raw_values:
        if "=" not in raw:
            raise ValueError(f"Invalid --subscore value, expected axis=value: {raw}")
        axis, value = raw.split("=", 1)
        subscores[axis] = float(value)
    return subscores


def run_conformance_suite(suite_path: str | Path) -> dict[str, Any]:
    suite_path = Path(suite_path)
    suite = load_structured(suite_path)
    base_dir = suite_path.parent
    repo_root = Path(__file__).resolve().parents[2]
    case_results = []
    for case in suite.get("cases", []):
        bundle_path = Path(case["result_bundle"])
        if not bundle_path.is_absolute():
            candidate = base_dir / bundle_path
            bundle_path = candidate if candidate.exists() else repo_root / bundle_path
        report = certify_result_bundle(bundle_path)
        expected_claim = case["expected_final_claim"]
        expected_badges = set(case.get("expected_badges", []))
        actual_badges = set(report["badges"])
        missing_badges = sorted(expected_badges - actual_badges)
        expected_forbidden = set(case.get("expected_forbidden_phrases", []))
        actual_forbidden = set(report["forbidden_phrases"])
        missing_forbidden = sorted(expected_forbidden - actual_forbidden)
        expected_effective_tier = case.get("expected_effective_tier")
        effective_tier = report["dataset_tier_evaluation"]["effective_tier"]
        tier_passed = expected_effective_tier is None or effective_tier == expected_effective_tier
        passed = (
            report["final_claim"] == expected_claim
            and not missing_badges
            and not missing_forbidden
            and tier_passed
        )
        case_results.append(
            {
                "id": case["id"],
                "passed": passed,
                "expected_final_claim": expected_claim,
                "actual_final_claim": report["final_claim"],
                "missing_badges": missing_badges,
                "missing_forbidden_phrases": missing_forbidden,
                "expected_effective_tier": expected_effective_tier,
                "actual_effective_tier": effective_tier,
            }
        )
    status = "passed" if all(case["passed"] for case in case_results) else "failed"
    return {
        "schema_version": "epibench.conformance_result.v1",
        "suite_id": suite.get("suite_id"),
        "epibench_version": suite.get("epibench_version"),
        "status": status,
        "cases": case_results,
    }


if __name__ == "__main__":
    raise SystemExit(main())
