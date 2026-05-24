from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT_DIR = REPO_ROOT / "reports" / "epibench_q1_hardening_register"
REVIEWER_PACKET = REPO_ROOT / "reports" / "epibench_reviewer_packet" / "reviewer_attack_matrix.csv"
RELEASE_REPRODUCTION = REPO_ROOT / "reports" / "epibench_release_candidate" / "reproduction_result.json"
HARDWARE_REPORT = REPO_ROOT / "reports" / "epibench_hardware_measurement" / "local_hardware_report.json"
CLINICAL_PACKET = REPO_ROOT / "reports" / "epibench_clinical_review_packet" / "review_execution_manifest.yaml"
SZCORE_REPORT = REPO_ROOT / "reports" / "epibench_szcore_official_contract_report.md"
WEIGHT_REPORT = REPO_ROOT / "reports" / "epibench_weight_sensitivity" / "README.md"
COVERAGE_REPORT = REPO_ROOT / "reports" / "epibench_coverage_audit" / "protocol_use_case_coverage.csv"
REAL_EVIDENCE_REPORT = REPO_ROOT / "reports" / "epibench_real_evidence_progression" / "README.md"
OVERCLAIM_REPORT = REPO_ROOT / "reports" / "epibench_overclaim_audit" / "README.md"
PAPER_DRAFT = REPO_ROOT / "docs" / "paper" / "EPIBENCH_NPJ_DIGITAL_MEDICINE_DRAFT.md"


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the top-tier Q1 rejection hardening register.")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    args = parser.parse_args()

    result = build_q1_hardening_register(out_dir=args.out_dir)
    print(
        "Built Q1 hardening register with "
        f"{result['angle_count']} angles, {result['uncontrolled_count']} uncontrolled, "
        f"{result['external_dependency_count']} external dependencies"
    )
    return 0 if result["uncontrolled_count"] == 0 else 1


def build_q1_hardening_register(*, out_dir: Path = DEFAULT_OUT_DIR) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    reviewer = {row["attack_id"]: row for row in _read_csv(REVIEWER_PACKET)}
    release = _read_json(RELEASE_REPRODUCTION)
    hardware = _read_json(HARDWARE_REPORT)
    paper_text = PAPER_DRAFT.read_text(encoding="utf-8") if PAPER_DRAFT.exists() else ""

    angles = _build_angles(reviewer=reviewer, release=release, hardware=hardware, paper_text=paper_text)
    summary = _summarize(angles)
    actions = _build_external_action_register(angles)

    _write_csv(out_dir / "q1_hardening_matrix.csv", angles)
    _write_csv(out_dir / "external_dependency_action_register.csv", actions)
    _write_json(out_dir / "q1_hardening_summary.json", summary)
    (out_dir / "README.md").write_text(_render_readme(summary, angles, actions), encoding="utf-8")
    return summary


def _build_angles(
    *,
    reviewer: dict[str, dict[str, str]],
    release: dict[str, Any],
    hardware: dict[str, Any],
    paper_text: str,
) -> list[dict[str, str]]:
    return [
        _angle(
            "Q1-01",
            "Too much protocol, not enough real proof.",
            _status_from_reviewer(reviewer, "A06", fallback="external_dependency"),
            _rel(REAL_EVIDENCE_REPORT),
            reviewer.get("A06", {}).get("quantitative_indicator", "real evidence report missing"),
            "Do not claim clinical performance; present current packages as protocol evidence and require full-scale EEG evidence before stronger claims.",
            "Full-scale signal-derived EEG package, preferably CHB-MIT/TUSZ, with patient-independent event scoring and per-patient distributions.",
        ),
        _angle(
            "Q1-02",
            "No third-party adoption or independent reproduction.",
            "external_dependency"
            if release.get("external_reproduction_status") != "completed_external_lab_run"
            else "closed_by_evidence",
            _rel(RELEASE_REPRODUCTION),
            (
                f"release={release.get('status', 'missing')}; "
                f"matched={release.get('matched_count', 0)}/{release.get('claim_count', 0)}; "
                f"external={release.get('external_reproduction_status', 'missing')}"
            ),
            "Do not claim adoption; claim only one-command reproducibility from this checkout until an external lab submits a run.",
            "At least one independent clean-checkout reproduction report from a lab not involved in EpiBench development.",
        ),
        _angle(
            "Q1-03",
            "No independent clinical review.",
            "external_dependency" if CLINICAL_PACKET.exists() else "uncontrolled",
            _rel(CLINICAL_PACKET),
            f"clinical review packet exists={CLINICAL_PACKET.exists()}",
            "Do not state that clinical review is complete; keep clinical claim gates as proposed until signed forms are returned.",
            "Two independent reviewers, including clinical epilepsy/neurophysiology expertise, with adjudicated item-level MTS/DSI register.",
        ),
        _angle(
            "Q1-04",
            "EpiBench reinvents SzCORE.",
            "closed_by_evidence" if SZCORE_REPORT.exists() and reviewer.get("A04", {}).get("defense_status") == "strong" else "uncontrolled",
            _rel(SZCORE_REPORT),
            reviewer.get("A04", {}).get("quantitative_indicator", "SzCORE report missing"),
            "Describe EpiBench as a claim-gating layer that consumes official scoring outputs; never as an event scorer replacement.",
            "Preferably add a full real EEG official SzCORE run, but API-contract reinvention risk is closed.",
        ),
        _angle(
            "Q1-05",
            "Universal certification is overclaimed.",
            "neutralized_by_scope" if _contains_all(paper_text, ["not clinical approval", "bounded claim"]) else "uncontrolled",
            _rel(PAPER_DRAFT),
            "paper contains explicit certification boundary and bounded-claim language",
            "Use scientific claim eligibility under EpiBench, not universal clinical certification.",
            "No external closure needed unless manuscript or badges reintroduce universal-certification wording.",
        ),
        _angle(
            "Q1-06",
            "MTS/DSI remain subjective.",
            "external_dependency" if CLINICAL_PACKET.exists() and reviewer.get("A05", {}).get("defense_status") == "partial" else "uncontrolled",
            _rel(CLINICAL_PACKET),
            reviewer.get("A05", {}).get("quantitative_indicator", "clinical review packet missing"),
            "Treat rubric stability as pending external review; do not claim institutional reproducibility yet.",
            "Independent inter-reviewer agreement with no unresolved score difference greater than one point.",
        ),
        _angle(
            "Q1-07",
            "Epi-Score weights are arbitrary.",
            "closed_by_evidence" if WEIGHT_REPORT.exists() and reviewer.get("A11", {}).get("defense_status") == "strong" else "uncontrolled",
            _rel(WEIGHT_REPORT),
            reviewer.get("A11", {}).get("quantitative_indicator", "weight sensitivity report missing"),
            "Keep Epi-Score subordinate to claim gates; include sensitivity panel in main or supplementary results.",
            "No external closure needed for v1; future community governance can revise weights prospectively.",
        ),
        _angle(
            "Q1-08",
            "No real target hardware evidence for edge or real-time claims.",
            "neutralized_by_scope" if hardware.get("edge_claim_authorized") is False else "uncontrolled",
            _rel(HARDWARE_REPORT),
            (
                f"local_measurement={bool(hardware)}; "
                f"edge_authorized={hardware.get('edge_claim_authorized', 'missing')}; "
                f"scope={hardware.get('measurement_scope', 'missing')}"
            ),
            "Keep local timing as reference only; forbid edge-ready, on-device, and real-time wording without target hardware.",
            "Measure declared final model on target IoT hardware with p95 latency, RAM, and energy or remove embedded claim.",
        ),
        _angle(
            "Q1-09",
            "No prospective clinical evidence.",
            "neutralized_by_scope" if _contains_all(paper_text, ["not a clinical validation pathway", "prospective"]) else "uncontrolled",
            _rel(PAPER_DRAFT),
            "paper limits E4/prospective evidence and excludes clinical approval",
            "Present E4 as a future/prospective evidence class, not an achieved result.",
            "Prospective multisite study or trial-grade evidence package.",
        ),
        _angle(
            "Q1-10",
            "Detection, warning, forecasting, and embedded viability are too broad.",
            "closed_by_evidence" if COVERAGE_REPORT.exists() and reviewer.get("A07", {}).get("defense_status") == "strong" else "uncontrolled",
            _rel(COVERAGE_REPORT),
            reviewer.get("A07", {}).get("quantitative_indicator", "coverage report missing"),
            "Keep one primary track per result bundle and forbid pooled claims across D/W/F/E.",
            "No external closure needed unless new tracks are added without separate metrics and claim gates.",
        ),
    ]


def _angle(
    angle_id: str,
    reviewer_attack: str,
    closure_status: str,
    primary_evidence: str,
    current_evidence: str,
    manuscript_control: str,
    true_closure_requirement: str,
) -> dict[str, str]:
    if closure_status == "closed_by_evidence":
        residual_rejection_risk = "low"
        interpretation = "Attack is materially answered by executable evidence."
    elif closure_status == "neutralized_by_scope":
        residual_rejection_risk = "low_to_medium"
        interpretation = "Attack does not apply if the manuscript keeps the bounded scope."
    elif closure_status == "external_dependency":
        residual_rejection_risk = "medium_to_high"
        interpretation = "Attack cannot be fully closed internally; it is converted into an explicit pre-submission dependency."
    else:
        residual_rejection_risk = "high"
        interpretation = "Uncontrolled rejection risk."
    return {
        "angle_id": angle_id,
        "reviewer_attack": reviewer_attack,
        "closure_status": closure_status,
        "residual_rejection_risk": residual_rejection_risk,
        "primary_evidence": primary_evidence,
        "current_evidence": current_evidence,
        "manuscript_control": manuscript_control,
        "true_closure_requirement": true_closure_requirement,
        "interpretation": interpretation,
    }


def _status_from_reviewer(
    reviewer: dict[str, dict[str, str]], attack_id: str, *, fallback: str
) -> str:
    status = reviewer.get(attack_id, {}).get("defense_status")
    if status == "strong":
        return "closed_by_evidence"
    if status == "partial":
        return "external_dependency"
    return fallback


def _summarize(angles: list[dict[str, str]]) -> dict[str, Any]:
    counts = _counts(angle["closure_status"] for angle in angles)
    uncontrolled = counts.get("uncontrolled", 0)
    return {
        "schema_version": "epibench.q1_hardening_summary.v1",
        "angle_count": len(angles),
        "closed_by_evidence_count": counts.get("closed_by_evidence", 0),
        "neutralized_by_scope_count": counts.get("neutralized_by_scope", 0),
        "external_dependency_count": counts.get("external_dependency", 0),
        "uncontrolled_count": uncontrolled,
        "status": "controlled_with_external_dependencies" if uncontrolled == 0 else "failed",
        "boundary": (
            "A controlled register does not mean the paper is guaranteed acceptable. It means every "
            "major rejection angle is either answered by evidence, neutralized by bounded scope, or "
            "made explicit as an external pre-submission dependency."
        ),
    }


def _build_external_action_register(angles: list[dict[str, str]]) -> list[dict[str, str]]:
    rows = []
    for angle in angles:
        if angle["closure_status"] != "external_dependency":
            continue
        rows.append(
            {
                "angle_id": angle["angle_id"],
                "priority": "P0" if angle["residual_rejection_risk"] == "medium_to_high" else "P1",
                "required_action": angle["true_closure_requirement"],
                "evidence_to_update": angle["primary_evidence"],
                "manuscript_control_until_closed": angle["manuscript_control"],
            }
        )
    return rows


def _render_readme(
    summary: dict[str, Any],
    angles: list[dict[str, str]],
    actions: list[dict[str, str]],
) -> str:
    rows = "\n".join(
        "- `{angle_id}` {closure_status}: {reviewer_attack}".format(**angle) for angle in angles
    )
    action_rows = "\n".join(
        "- `{angle_id}` {priority}: {required_action}".format(**action) for action in actions
    ) or "- None"
    return f"""# EpiBench Q1 Rejection Hardening Register

Status: `{summary['status']}`

## Purpose

This register answers the ten most plausible attacks from a severe Q1 reviewer. It is intentionally
stricter than the manuscript narrative. An angle is not considered controlled by optimism; it must be
closed by executable evidence, neutralized by explicit manuscript scope, or listed as an external
dependency before submission.

## Summary

- Angles tracked: `{summary['angle_count']}`.
- Closed by evidence: `{summary['closed_by_evidence_count']}`.
- Neutralized by scope: `{summary['neutralized_by_scope_count']}`.
- External dependencies: `{summary['external_dependency_count']}`.
- Uncontrolled: `{summary['uncontrolled_count']}`.

## Angle Status

{rows}

## External Actions Still Required

{action_rows}

## Boundary

{summary['boundary']}
"""


def _contains_all(text: str, phrases: list[str]) -> bool:
    normalized = text.casefold()
    return all(phrase.casefold() in normalized for phrase in phrases)


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
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _counts(values: Any) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        key = str(value)
        counts[key] = counts.get(key, 0) + 1
    return counts


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
