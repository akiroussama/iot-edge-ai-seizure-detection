from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT_DIR = REPO_ROOT / "reports" / "epibench_reviewer_packet"
EVIDENCE_DIR = REPO_ROOT / "reports" / "epibench_evidence_panels"
COVERAGE_DIR = REPO_ROOT / "reports" / "epibench_coverage_audit"
OVERCLAIM_DIR = REPO_ROOT / "reports" / "epibench_overclaim_audit"
WEIGHT_SENSITIVITY_DIR = REPO_ROOT / "reports" / "epibench_weight_sensitivity"
READINESS_PATH = REPO_ROOT / "reports" / "epibench_submission_readiness_result.json"
INTER_REVIEWER_PATH = REPO_ROOT / "reports" / "epibench_inter_reviewer_report.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a reviewer-facing EpiBench evidence packet.")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    args = parser.parse_args()

    result = build_reviewer_packet(out_dir=args.out_dir)
    print(
        "Built reviewer packet with "
        f"{result['attack_count']} attacks, {result['open_count']} open, "
        f"{result['partial_count']} partial, {result['strong_count']} strong"
    )
    return 0


def build_reviewer_packet(
    *,
    out_dir: Path,
    evidence_dir: Path = EVIDENCE_DIR,
    coverage_dir: Path = COVERAGE_DIR,
    overclaim_dir: Path = OVERCLAIM_DIR,
    weight_sensitivity_dir: Path = WEIGHT_SENSITIVITY_DIR,
    readiness_path: Path = READINESS_PATH,
    inter_reviewer_path: Path = INTER_REVIEWER_PATH,
) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    metrics = _collect_metrics(
        evidence_dir=evidence_dir,
        coverage_dir=coverage_dir,
        overclaim_dir=overclaim_dir,
        weight_sensitivity_dir=weight_sensitivity_dir,
        readiness_path=readiness_path,
        inter_reviewer_path=inter_reviewer_path,
    )
    attacks = _build_attack_matrix(metrics)
    actions = _build_action_register(attacks)
    evidence_index = _build_evidence_index(metrics)

    _write_csv(out_dir / "reviewer_attack_matrix.csv", attacks)
    _write_csv(out_dir / "pre_submission_action_register.csv", actions)
    _write_csv(out_dir / "evidence_index.csv", evidence_index)
    (out_dir / "README.md").write_text(_render_readme(metrics, attacks, actions), encoding="utf-8")

    status_counts = _counts(row["defense_status"] for row in attacks)
    return {
        "attack_count": len(attacks),
        "strong_count": status_counts.get("strong", 0),
        "partial_count": status_counts.get("partial", 0),
        "open_count": status_counts.get("open", 0),
        "out_dir": str(out_dir),
    }


def _collect_metrics(
    *,
    evidence_dir: Path,
    coverage_dir: Path,
    overclaim_dir: Path,
    weight_sensitivity_dir: Path,
    readiness_path: Path,
    inter_reviewer_path: Path,
) -> dict[str, Any]:
    bundles = _read_csv(evidence_dir / "bundle_summary.csv")
    rank_comparison = _read_csv(evidence_dir / "rank_comparison.csv")
    sensitivity = _read_csv(evidence_dir / "sensitivity_only_leaderboard.csv")
    failures = _read_csv(evidence_dir / "failure_matrix.csv")
    coverage_gaps = _read_csv(coverage_dir / "coverage_gaps.csv")
    overclaims = _read_csv(overclaim_dir / "overclaim_findings.csv")
    weight_summary = _read_csv(weight_sensitivity_dir / "weight_sensitivity_summary.csv")
    weight_stability = _read_csv(weight_sensitivity_dir / "weight_sensitivity_rank_stability.csv")
    readiness = _read_json(readiness_path)
    inter_reviewer = _read_json(inter_reviewer_path)

    final_claims = _counts(row.get("final_claim", "") for row in bundles)
    tracks = sorted({row.get("track", "") for row in bundles if row.get("track")})
    high_score_downgrades = [
        row for row in rank_comparison if row.get("interpretation") == "high_or_mid_score_claim_limited_by_evidence_gate"
    ]
    promoted_by_claim_gate = [
        row for row in rank_comparison if row.get("interpretation") == "claim_gate_promotes_more_defensible_evidence"
    ]
    top_sensitivity_e1 = [
        row
        for row in sensitivity[:5]
        if row.get("final_claim") == "E1" or _as_float(row.get("false_alarms_per_24h")) > 24
    ]
    present_failures = [row for row in failures if row.get("present") == "True"]
    critical_failures = [row for row in present_failures if row.get("severity") == "critical"]
    hardware_failures = [row for row in present_failures if row.get("sentinel_code") == "HARDWARE_UNMEASURED"]
    warning_failures = [row for row in present_failures if row.get("sentinel_code") == "POST_EVENT_ALARM"]
    far_failures = [row for row in present_failures if row.get("sentinel_code") == "FAR_EXPLOSION"]
    szcore_bundles = [row for row in bundles if "szcore_bridge" in row.get("bundle_path", "")]
    waveform_bundles = [
        row
        for row in bundles
        if "waveform" in row.get("dataset_id", "") or "signal_threshold" in row.get("model_family", "")
    ]
    patient_dependent = [row for row in bundles if row.get("split_policy") == "patient_dependent"]
    real_packages = [row for row in bundles if "demo-not-a-real-result" not in row.get("model_family", "")]
    operational_packages = [row for row in bundles if row.get("final_claim") in {"E2-PI", "E3", "E4"}]
    overclaim_review = [row for row in overclaims if row.get("classification") == "requires_review"]
    critical_overclaim_review = [row for row in overclaim_review if row.get("severity") == "critical"]
    max_score_rank_range = max((_as_int(row.get("score_rank_range")) for row in weight_stability), default=0)
    max_claim_rank_range = max((_as_int(row.get("claim_gated_rank_range")) for row in weight_stability), default=0)
    scenarios_with_e1_top3 = sum(1 for row in weight_summary if _as_int(row.get("e1_runs_in_top3_by_score")) > 0)

    return {
        "bundle_count": len(bundles),
        "claim_distribution": final_claims,
        "tracks": tracks,
        "track_count": len(tracks),
        "high_score_downgrade_count": len(high_score_downgrades),
        "claim_gate_promotion_count": len(promoted_by_claim_gate),
        "top_sensitivity_problem_count": len(top_sensitivity_e1),
        "present_failure_count": len(present_failures),
        "critical_failure_count": len(critical_failures),
        "hardware_failure_count": len(hardware_failures),
        "warning_failure_count": len(warning_failures),
        "far_failure_count": len(far_failures),
        "szcore_bundle_count": len(szcore_bundles),
        "waveform_bundle_count": len(waveform_bundles),
        "waveform_claims": _counts(row.get("final_claim", "") for row in waveform_bundles),
        "patient_dependent_count": len(patient_dependent),
        "real_package_count": len(real_packages),
        "operational_package_count": len(operational_packages),
        "coverage_gap_count": len(coverage_gaps),
        "major_coverage_gap_count": sum(1 for row in coverage_gaps if row.get("severity") == "major"),
        "overclaim_review_count": len(overclaim_review),
        "critical_overclaim_review_count": len(critical_overclaim_review),
        "weight_sensitivity_exists": bool(weight_summary and weight_stability),
        "weight_sensitivity_scenario_count": len(weight_summary),
        "weight_sensitivity_max_score_rank_range": max_score_rank_range,
        "weight_sensitivity_max_claim_rank_range": max_claim_rank_range,
        "weight_sensitivity_e1_top3_scenarios": scenarios_with_e1_top3,
        "readiness_status": readiness.get("status", "missing"),
        "readiness_submission_grade_count": readiness.get("submission_grade_count", 0),
        "readiness_operational_package_count": readiness.get("operational_package_count", 0),
        "inter_reviewer_status": inter_reviewer.get("status", "missing"),
        "inter_reviewer_dataset_count": inter_reviewer.get("dataset_count", 0),
    }


def _build_attack_matrix(metrics: dict[str, Any]) -> list[dict[str, Any]]:
    rows = [
        _attack(
            "A01",
            "EpiBench-certified could be misread as clinical or regulatory approval.",
            "critical",
            "partial" if metrics["critical_overclaim_review_count"] else "strong",
            "reports/epibench_overclaim_audit/README.md",
            f"{metrics['critical_overclaim_review_count']} critical wording findings require review.",
            "Resolve or explicitly waive every critical overclaim finding before manuscript freeze.",
        ),
        _attack(
            "A02",
            "This is just another leaderboard, not a scientific evidence protocol.",
            "critical",
            "strong" if metrics["high_score_downgrade_count"] >= 3 else "partial",
            "reports/epibench_evidence_panels/rank_comparison.csv",
            f"{metrics['high_score_downgrade_count']} high/mid-score runs are claim-limited by evidence gates.",
            "Use the downgrade cases as central figures, not supplementary anecdotes.",
        ),
        _attack(
            "A03",
            "Sensitivity or AUROC-like rankings are enough; EpiBench adds complexity without value.",
            "high",
            "strong" if metrics["top_sensitivity_problem_count"] >= 3 else "partial",
            "reports/epibench_evidence_panels/sensitivity_only_leaderboard.csv",
            f"{metrics['top_sensitivity_problem_count']} top sensitivity entries are E1 or alarm-burden limited.",
            "Keep false alarms/day and event-level claim gates adjacent to every sensitivity table.",
        ),
        _attack(
            "A04",
            "The protocol reinvents existing seizure event scoring such as SzCORE.",
            "critical",
            "partial" if metrics["szcore_bundle_count"] >= 1 else "open",
            "examples/epibench/szcore_bridge_demo/result_bundle.yaml",
            f"{metrics['szcore_bundle_count']} SzCORE-bridge bundle is present.",
            "Replace or supplement the demonstration import with official external scorer output.",
        ),
        _attack(
            "A05",
            "MTS and DSI are subjective and not reproducible between reviewers.",
            "critical",
            "partial" if metrics["inter_reviewer_status"] == "passed" else "open",
            "reports/epibench_inter_reviewer_report.json",
            f"Inter-reviewer report status {metrics['inter_reviewer_status']} on {metrics['inter_reviewer_dataset_count']} datasets.",
            "Run independent clinical/methods reviewers and report adjudicated rubric changes.",
        ),
        _attack(
            "A06",
            "Real evidence is too thin; examples are mostly demos.",
            "critical",
            "partial" if metrics["readiness_status"] == "passed" else "open",
            "reports/epibench_submission_readiness_result.json",
            (
                f"Submission gate {metrics['readiness_status']} with "
                f"{metrics['readiness_submission_grade_count']} submission-grade packages; "
                f"{metrics['waveform_bundle_count']} waveform-derived package(s) with claims "
                f"{metrics['waveform_claims']}."
            ),
            "Upgrade CHB-MIT from metadata/null baseline to waveform-derived patient-independent result.",
        ),
        _attack(
            "A07",
            "Detection, early warning, forecasting, and embedded viability are conflated.",
            "high",
            "strong" if metrics["track_count"] >= 4 and metrics["warning_failure_count"] else "partial",
            "reports/epibench_coverage_audit/protocol_use_case_coverage.csv",
            f"Covered tracks: {', '.join(metrics['tracks'])}; POST_EVENT_ALARM cases: {metrics['warning_failure_count']}.",
            "Preserve track-specific figures and avoid pooling D/W/F/E results into a single claim.",
        ),
        _attack(
            "A08",
            "Failure sentinels are punitive or arbitrary rather than informative.",
            "high",
            "strong" if metrics["present_failure_count"] >= 5 else "partial",
            "reports/epibench_evidence_panels/failure_matrix.csv",
            (
                f"{metrics['present_failure_count']} visible failure rows, "
                f"{metrics['critical_failure_count']} critical."
            ),
            "Add a short rationale table for each sentinel-to-claim consequence in the paper.",
        ),
        _attack(
            "A09",
            "Patient-dependent results may be overread as patient-independent generalization.",
            "high",
            "strong" if metrics["patient_dependent_count"] >= 1 else "partial",
            "reports/epibench_evidence_panels/claim_gate_waterfall.csv",
            f"{metrics['patient_dependent_count']} patient-dependent package is explicitly claim-capped.",
            "Keep E2-PD and E2-PI badges visually distinct in tables and figure legends.",
        ),
        _attack(
            "A10",
            "Edge or real-time claims are not supported by measured hardware.",
            "high",
            "partial" if metrics["hardware_failure_count"] >= 1 else "open",
            "reports/epibench_evidence_panels/failure_matrix.csv",
            f"{metrics['hardware_failure_count']} HARDWARE_UNMEASURED sentinel is visible.",
            "Either add measured target hardware results or remove edge-readiness as a demonstrated claim.",
        ),
        _attack(
            "A11",
            "The Epi-Score weights are arbitrary and could change conclusions.",
            "high",
            "strong" if metrics["weight_sensitivity_exists"] else "open",
            "reports/epibench_weight_sensitivity/README.md",
            (
                f"{metrics['weight_sensitivity_scenario_count']} scenarios; "
                f"max score-rank range {metrics['weight_sensitivity_max_score_rank_range']}; "
                f"max claim-gated rank range {metrics['weight_sensitivity_max_claim_rank_range']}."
            ),
            "Include the weight-sensitivity panel and keep claim-gated interpretation dominant.",
        ),
        _attack(
            "A12",
            "The standard is not yet community-adoptable from a clean checkout.",
            "high",
            "partial",
            "docs/EPIBENCH_IMPLEMENTATION_INDEX.md",
            "CLI, schemas, examples, tests, panels, and reports exist; DOI/release/external run remain open.",
            "Freeze v1.0-rc, archive DOI, and document one-command reproduction for external users.",
        ),
    ]
    return rows


def _attack(
    attack_id: str,
    reviewer_attack: str,
    severity: str,
    defense_status: str,
    primary_evidence: str,
    quantitative_indicator: str,
    required_action: str,
) -> dict[str, str]:
    return {
        "attack_id": attack_id,
        "reviewer_attack": reviewer_attack,
        "severity": severity,
        "defense_status": defense_status,
        "primary_evidence": primary_evidence,
        "quantitative_indicator": quantitative_indicator,
        "required_action": required_action,
    }


def _build_action_register(attacks: list[dict[str, Any]]) -> list[dict[str, str]]:
    priority = {"open": 0, "partial": 1, "strong": 2}
    rows = []
    for attack in sorted(attacks, key=lambda row: (priority[row["defense_status"]], row["attack_id"])):
        if attack["defense_status"] == "strong":
            continue
        rows.append(
            {
                "attack_id": attack["attack_id"],
                "defense_status": attack["defense_status"],
                "severity": attack["severity"],
                "required_action": attack["required_action"],
                "evidence_to_update": attack["primary_evidence"],
            }
        )
    return rows


def _build_evidence_index(metrics: dict[str, Any]) -> list[dict[str, str]]:
    return [
        {
            "evidence_family": "evidence_panels",
            "path": "reports/epibench_evidence_panels/README.md",
            "summary": f"{metrics['bundle_count']} bundles across claims {metrics['claim_distribution']}.",
        },
        {
            "evidence_family": "coverage_audit",
            "path": "reports/epibench_coverage_audit/README.md",
            "summary": f"{metrics['coverage_gap_count']} gaps, {metrics['major_coverage_gap_count']} major.",
        },
        {
            "evidence_family": "overclaim_audit",
            "path": "reports/epibench_overclaim_audit/README.md",
            "summary": (
                f"{metrics['overclaim_review_count']} wording findings require review; "
                f"{metrics['critical_overclaim_review_count']} critical."
            ),
        },
        {
            "evidence_family": "weight_sensitivity",
            "path": "reports/epibench_weight_sensitivity/README.md",
            "summary": (
                f"{metrics['weight_sensitivity_scenario_count']} scenarios; "
                f"max_score_rank_range={metrics['weight_sensitivity_max_score_rank_range']}; "
                f"max_claim_gated_rank_range={metrics['weight_sensitivity_max_claim_rank_range']}."
            ),
        },
        {
            "evidence_family": "submission_readiness",
            "path": "reports/epibench_submission_readiness_result.json",
            "summary": (
                f"status={metrics['readiness_status']}; "
                f"submission_grade={metrics['readiness_submission_grade_count']}; "
                f"operational={metrics['readiness_operational_package_count']}."
            ),
        },
        {
            "evidence_family": "inter_reviewer",
            "path": "reports/epibench_inter_reviewer_report.json",
            "summary": (
                f"status={metrics['inter_reviewer_status']}; "
                f"datasets={metrics['inter_reviewer_dataset_count']}."
            ),
        },
    ]


def _render_readme(
    metrics: dict[str, Any],
    attacks: list[dict[str, Any]],
    actions: list[dict[str, Any]],
) -> str:
    status_counts = _counts(row["defense_status"] for row in attacks)
    severity_counts = _counts(row["severity"] for row in attacks)
    open_or_partial = "\n".join(
        f"- `{row['attack_id']}` {row['defense_status']}: {row['required_action']}" for row in actions
    ) or "- None"
    return f"""# EpiBench Reviewer Evidence Packet

Generated from EpiBench evidence panels, coverage audit, overclaim audit, submission-readiness gate,
and inter-reviewer report.

## Purpose

This packet is a pre-submission defense matrix. It does not claim that the paper will be accepted.
It identifies the reviewer attacks that remain scientifically plausible and links each attack to a
specific artefact, quantitative indicator, and required action.

## Summary

- Reviewer attacks tracked: `{len(attacks)}`.
- Defense status: `{_format_counts(status_counts)}`.
- Severity distribution: `{_format_counts(severity_counts)}`.
- Result bundles represented in evidence panels: `{metrics['bundle_count']}`.
- Protocol tracks represented: `{', '.join(metrics['tracks'])}`.
- Submission-readiness gate: `{metrics['readiness_status']}`.
- Open or partial action count: `{len(actions)}`.

## Files Generated

- `reviewer_attack_matrix.csv`: one row per major reviewer objection.
- `pre_submission_action_register.csv`: only unresolved or partially resolved reviewer risks.
- `evidence_index.csv`: map from evidence families to concrete report files.

## Highest-Priority Remaining Actions

{open_or_partial}

## Boundary

This packet is an internal scientific risk-control artefact. It is not clinical validation, regulatory
clearance, or a guarantee of Q1 acceptance. It is meant to make the remaining rejection risks explicit
before manuscript freeze.
"""


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _counts(values: Any) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        key = str(value)
        counts[key] = counts.get(key, 0) + 1
    return counts


def _format_counts(counts: dict[str, int]) -> str:
    return ", ".join(f"{key}={value}" for key, value in sorted(counts.items()))


def _as_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _as_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
