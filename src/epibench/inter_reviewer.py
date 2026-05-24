from __future__ import annotations

from itertools import combinations
from pathlib import Path
from typing import Any

from src.epibench.validation import load_structured


def build_inter_reviewer_report(reviews_path: str | Path) -> dict[str, Any]:
    reviews = load_structured(reviews_path)
    dataset_reports = [_dataset_agreement(dataset) for dataset in reviews.get("datasets", [])]
    status = "passed" if dataset_reports and all(report["status"] == "passed" for report in dataset_reports) else "failed"
    return {
        "schema_version": "epibench.inter_reviewer_report.v1",
        "review_id": reviews.get("review_id"),
        "status": status,
        "dataset_count": len(dataset_reports),
        "datasets": dataset_reports,
    }


def _dataset_agreement(dataset: dict[str, Any]) -> dict[str, Any]:
    reviewers = dataset.get("reviewers", [])
    if len(reviewers) < 2:
        return {
            "dataset_id": dataset.get("dataset_id"),
            "status": "failed",
            "blockers": ["At least two independent reviewers are required."],
        }
    pair_reports = [_pair_agreement(a, b) for a, b in combinations(reviewers, 2)]
    final_tiers = {reviewer["dataset_tier"] for reviewer in reviewers}
    claim_ceilings = {reviewer["claim_ceiling"] for reviewer in reviewers}
    blockers = []
    if len(final_tiers) != 1:
        blockers.append(f"Dataset tier disagreement: {sorted(final_tiers)}")
    if len(claim_ceilings) != 1:
        blockers.append(f"Claim ceiling disagreement: {sorted(claim_ceilings)}")
    severe_disagreements = [
        item
        for pair in pair_reports
        for item in pair["items_with_difference_gt_one"]
    ]
    if severe_disagreements:
        blockers.append(f"Rubric items differ by more than one point: {sorted(set(severe_disagreements))}")
    return {
        "dataset_id": dataset["dataset_id"],
        "status": "passed" if not blockers else "failed",
        "reviewer_count": len(reviewers),
        "dataset_tier_agreement": len(final_tiers) == 1,
        "claim_ceiling_agreement": len(claim_ceilings) == 1,
        "agreed_dataset_tier": next(iter(final_tiers)) if len(final_tiers) == 1 else None,
        "agreed_claim_ceiling": next(iter(claim_ceilings)) if len(claim_ceilings) == 1 else None,
        "pairwise": pair_reports,
        "blockers": blockers,
    }


def _pair_agreement(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    mts = _score_map_difference(a.get("mts", {}), b.get("mts", {}))
    dsi = _score_map_difference(a.get("dsi", {}), b.get("dsi", {}))
    severe = [f"mts.{item}" for item in mts["items_with_difference_gt_one"]]
    severe.extend(f"dsi.{item}" for item in dsi["items_with_difference_gt_one"])
    return {
        "reviewer_a": a["reviewer_id"],
        "reviewer_b": b["reviewer_id"],
        "same_dataset_tier": a["dataset_tier"] == b["dataset_tier"],
        "same_claim_ceiling": a["claim_ceiling"] == b["claim_ceiling"],
        "mts_mean_absolute_difference": mts["mean_absolute_difference"],
        "dsi_mean_absolute_difference": dsi["mean_absolute_difference"],
        "items_with_difference_gt_one": severe,
    }


def _score_map_difference(a: dict[str, int], b: dict[str, int]) -> dict[str, Any]:
    all_items = sorted(set(a) | set(b))
    if not all_items:
        return {"mean_absolute_difference": 0.0, "items_with_difference_gt_one": []}
    diffs = []
    severe = []
    for item in all_items:
        diff = abs(int(a.get(item, 0)) - int(b.get(item, 0)))
        diffs.append(diff)
        if diff > 1:
            severe.append(item)
    return {
        "mean_absolute_difference": round(sum(diffs) / len(diffs), 3),
        "items_with_difference_gt_one": severe,
    }
