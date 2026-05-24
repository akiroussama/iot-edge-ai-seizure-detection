from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from statistics import mean
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.epibench.certification import certify_result_bundle, evaluate_dataset_tier
from src.epibench.spec import load_spec
from src.epibench.validation import validate_artifact


DEFAULT_EXAMPLES_ROOT = REPO_ROOT / "examples" / "epibench"
DEFAULT_OUT_DIR = REPO_ROOT / "reports" / "epibench_coverage_audit"
EXPECTED_TRACKS = ["D", "W", "F", "E"]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build EpiBench evidence-card and protocol coverage audit panels."
    )
    parser.add_argument("--examples-root", type=Path, default=DEFAULT_EXAMPLES_ROOT)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--bundle", action="append", default=None)
    args = parser.parse_args()

    bundle_paths = [Path(path) for path in args.bundle] if args.bundle else _discover_bundles(args.examples_root)
    result = build_coverage_audit(bundle_paths=bundle_paths, out_dir=args.out_dir)
    print(f"Built coverage audit for {result['bundle_count']} bundles and {result['dataset_count']} dataset cards")
    return 0


def build_coverage_audit(bundle_paths: list[Path], out_dir: Path) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    spec = load_spec()
    records = [_collect_record(path, spec) for path in sorted(bundle_paths)]
    dataset_records = _unique_dataset_records(records)

    dataset_matrix = _dataset_evidence_matrix(dataset_records, spec)
    rubric_coverage = _rubric_item_coverage(dataset_records)
    use_case_coverage = _use_case_coverage(records)
    gap_rows = _coverage_gaps(records, dataset_records, spec)

    _write_csv(out_dir / "dataset_evidence_matrix.csv", dataset_matrix)
    _write_csv(out_dir / "rubric_item_coverage.csv", rubric_coverage)
    _write_csv(out_dir / "protocol_use_case_coverage.csv", use_case_coverage)
    _write_csv(out_dir / "coverage_gaps.csv", gap_rows)
    (out_dir / "README.md").write_text(
        _render_readme(records, dataset_records, gap_rows),
        encoding="utf-8",
    )
    return {
        "bundle_count": len(records),
        "dataset_count": len(dataset_records),
        "gap_count": len(gap_rows),
        "out_dir": str(out_dir),
    }


def _discover_bundles(examples_root: Path) -> list[Path]:
    return sorted(examples_root.glob("*/result_bundle.yaml"))


def _collect_record(bundle_path: Path, spec: dict[str, Any]) -> dict[str, Any]:
    bundle = validate_artifact("result-bundle", bundle_path)
    base_dir = bundle_path.parent
    dataset_path = base_dir / bundle["dataset_card_path"]
    split_path = base_dir / bundle["split_manifest_path"]
    failure_path = base_dir / bundle["failure_trace_path"]
    dataset = validate_artifact("dataset-card", dataset_path)
    split = validate_artifact("split", split_path)
    failure_trace = validate_artifact("failure-trace", failure_path)
    claim_report = certify_result_bundle(bundle_path)
    return {
        "bundle_path": bundle_path,
        "dataset_path": dataset_path,
        "bundle": bundle,
        "dataset": dataset,
        "split": split,
        "failure_trace": failure_trace,
        "claim_report": claim_report,
        "dataset_tier": evaluate_dataset_tier(dataset, spec),
    }


def _unique_dataset_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    unique = []
    for record in records:
        key = f"{record['dataset']['dataset_id']}::{record['dataset_path']}"
        if key in seen:
            continue
        seen.add(key)
        unique.append(record)
    return unique


def _dataset_evidence_matrix(
    dataset_records: list[dict[str, Any]],
    spec: dict[str, Any],
) -> list[dict[str, Any]]:
    all_mts = sorted({item for record in dataset_records for item in record["dataset"]["mts"]})
    all_dsi = sorted({item for record in dataset_records for item in record["dataset"]["dsi"]})
    core_items = spec.get("dataset_tier_assignment", {}).get("core_mts_items", [])
    rows = []
    for record in dataset_records:
        dataset = record["dataset"]
        tier = record["dataset_tier"]
        row: dict[str, Any] = {
            "dataset_id": dataset["dataset_id"],
            "dataset_path": _repo_relative(record["dataset_path"]),
            "declared_tier": tier["declared_tier"],
            "effective_tier": tier["effective_tier"],
            "mts_mean": tier["mts_mean"],
            "mts_item_floor": tier["mts_item_floor"],
            "missing_core_mts_items": ";".join(tier["missing_core_mts_items"]),
            "core_complete": not tier["missing_core_mts_items"],
            "setting": dataset["population"]["setting"],
            "label_audit": dataset["labels"]["audit_status"],
        }
        for item in all_mts:
            row[f"mts_{item}"] = dataset["mts"].get(item, {}).get("score")
            row[f"mts_{item}_is_core"] = item in core_items
        for item in all_dsi:
            row[f"dsi_{item}"] = dataset["dsi"].get(item, {}).get("score")
        rows.append(row)
    return rows


def _rubric_item_coverage(dataset_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for domain in ("mts", "dsi"):
        items = sorted({item for record in dataset_records for item in record["dataset"][domain]})
        for item in items:
            scored = []
            independent_reviewed = 0
            for record in dataset_records:
                rubric_item = record["dataset"][domain].get(item)
                if not rubric_item:
                    continue
                scored.append(int(rubric_item["score"]))
                if rubric_item["review_status"] == "independent_reviewed":
                    independent_reviewed += 1
            rows.append(
                {
                    "domain": domain,
                    "item": item,
                    "dataset_count": len(scored),
                    "min_score": min(scored) if scored else None,
                    "max_score": max(scored) if scored else None,
                    "mean_score": round(mean(scored), 3) if scored else None,
                    "zero_score_count": sum(1 for score in scored if score == 0),
                    "independent_reviewed_count": independent_reviewed,
                }
            )
    return rows


def _use_case_coverage(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counters: dict[tuple[str, str], int] = {}
    for record in records:
        bundle = record["bundle"]
        dataset = record["dataset"]
        split = record["split"]
        claim_report = record["claim_report"]
        _count(counters, "track", bundle["track"])
        _count(counters, "final_claim", claim_report["final_claim"])
        _count(counters, "effective_tier", claim_report["dataset_tier_evaluation"]["effective_tier"])
        _count(counters, "split_policy", split["split_policy"])
        _count(counters, "label_audit", dataset["labels"]["audit_status"])
        for sentinel in record["failure_trace"]["sentinels"]:
            if sentinel["present"]:
                _count(counters, "present_sentinel", sentinel["code"])
    rows = [
        {"category": category, "value": value, "count": count}
        for (category, value), count in sorted(counters.items())
    ]
    return rows


def _coverage_gaps(
    records: list[dict[str, Any]],
    dataset_records: list[dict[str, Any]],
    spec: dict[str, Any],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    covered_tracks = {record["bundle"]["track"] for record in records}
    for track in EXPECTED_TRACKS:
        if track not in covered_tracks:
            rows.append(_gap("track", track, "major", "No result bundle covers this EpiBench track."))

    covered_claims = {record["claim_report"]["final_claim"] for record in records}
    for claim in spec["claims"]:
        if claim not in covered_claims and claim != "E0":
            rows.append(_gap("claim", claim, "minor", "No current example lands at this final claim."))

    covered_splits = {record["split"]["split_policy"] for record in records}
    for split_policy in ("patient_independent", "external_dataset", "prospective_multisite"):
        if split_policy not in covered_splits:
            rows.append(_gap("split_policy", split_policy, "major", "High-value split policy is not covered."))

    for record in dataset_records:
        tier = record["dataset_tier"]
        if tier["missing_core_mts_items"]:
            rows.append(
                _gap(
                    "dataset_core_mts",
                    record["dataset"]["dataset_id"],
                    "major",
                    f"Missing core MTS items: {', '.join(tier['missing_core_mts_items'])}.",
                )
            )
        if tier["mts_item_floor"] == 0:
            rows.append(
                _gap(
                    "dataset_mts_floor",
                    record["dataset"]["dataset_id"],
                    "major",
                    "At least one MTS item has score 0; tier and claims must remain fail-closed.",
                )
            )

    if not any(_has_independent_review(record) for record in dataset_records):
        rows.append(
            _gap(
                "review_process",
                "independent_mts_dsi_review",
                "major",
                "No Dataset Evidence Card contains independent_reviewed rubric items.",
            )
        )
    return rows


def _gap(category: str, value: str, severity: str, recommendation: str) -> dict[str, Any]:
    return {
        "category": category,
        "value": value,
        "severity": severity,
        "recommendation": recommendation,
    }


def _has_independent_review(record: dict[str, Any]) -> bool:
    dataset = record["dataset"]
    for domain in ("mts", "dsi"):
        if any(item["review_status"] == "independent_reviewed" for item in dataset[domain].values()):
            return True
    return False


def _count(counters: dict[tuple[str, str], int], category: str, value: str) -> None:
    key = (category, value)
    counters[key] = counters.get(key, 0) + 1


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _render_readme(
    records: list[dict[str, Any]],
    dataset_records: list[dict[str, Any]],
    gap_rows: list[dict[str, Any]],
) -> str:
    major_gaps = [row for row in gap_rows if row["severity"] == "major"]
    covered_tracks = sorted({record["bundle"]["track"] for record in records})
    covered_claims = sorted({record["claim_report"]["final_claim"] for record in records})
    return f"""# EpiBench Coverage Audit

Generated from Dataset Evidence Cards, Split Manifests, Failure Traces, and Claim Reports.

## Purpose

This audit measures protocol coverage. It does not score models. It answers whether the current
artifact set exercises enough tracks, claims, tiers, split policies, failure sentinels, and MTS/DSI
rubrics to support a serious methods paper.

## Generated Files

- `dataset_evidence_matrix.csv`: one row per unique Dataset Evidence Card.
- `rubric_item_coverage.csv`: MTS/DSI item coverage and score distribution.
- `protocol_use_case_coverage.csv`: coverage by track, claim, tier, split, label audit, and sentinel.
- `coverage_gaps.csv`: explicit gaps to close before a stronger Q1 submission.

## Summary

- Result bundles audited: `{len(records)}`.
- Unique Dataset Evidence Cards audited: `{len(dataset_records)}`.
- Covered tracks: `{', '.join(covered_tracks)}`.
- Covered final claims: `{', '.join(covered_claims)}`.
- Total coverage gaps: `{len(gap_rows)}`.
- Major coverage gaps: `{len(major_gaps)}`.

## Boundary

Coverage is not clinical validity. This report only shows which parts of EpiBench v1.0-draft are
currently exercised by the repository artefacts.
"""


def _repo_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
