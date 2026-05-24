from __future__ import annotations

import argparse
import csv
import math
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.epibench.spec import claim_ranks, load_spec

DEFAULT_OUT_DIR = REPO_ROOT / "reports" / "epibench_weight_sensitivity"
DEFAULT_AXIS_MATRIX = REPO_ROOT / "reports" / "epibench_evidence_panels" / "score_axis_matrix.csv"

SCENARIOS: dict[str, dict[str, Any]] = {
    "normative": {"type": "multipliers", "multipliers": {}},
    "equal_available_axes": {"type": "equal"},
    "performance_plus50": {"type": "multipliers", "multipliers": {"performance": 1.50}},
    "clinical_safety_plus50": {"type": "multipliers", "multipliers": {"clinical_safety": 1.50}},
    "robustness_plus50": {"type": "multipliers", "multipliers": {"robustness": 1.50}},
    "stability_plus50": {"type": "multipliers", "multipliers": {"stability": 1.50}},
    "latency_plus50": {"type": "multipliers", "multipliers": {"latency": 1.50}},
    "embedded_plus50": {"type": "multipliers", "multipliers": {"embedded_viability": 1.50}},
    "calibration_plus50": {"type": "multipliers", "multipliers": {"calibration": 1.50}},
    "safety_and_performance_plus25": {
        "type": "multipliers",
        "multipliers": {"performance": 1.25, "clinical_safety": 1.25},
    },
    "deployment_axes_plus50": {
        "type": "multipliers",
        "multipliers": {"latency": 1.50, "embedded_viability": 1.50},
    },
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Epi-Score weight sensitivity panels.")
    parser.add_argument("--axis-matrix", type=Path, default=DEFAULT_AXIS_MATRIX)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    args = parser.parse_args()

    result = build_weight_sensitivity(axis_matrix_path=args.axis_matrix, out_dir=args.out_dir)
    print(
        "Built weight sensitivity panel with "
        f"{result['bundle_count']} bundles across {result['scenario_count']} scenarios; "
        f"max score-rank range {result['max_score_rank_range']}"
    )
    return 0


def build_weight_sensitivity(axis_matrix_path: Path, out_dir: Path) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    spec = load_spec()
    bundles = _load_axis_scores(axis_matrix_path)
    scenario_rows = _score_scenarios(bundles, spec)
    rank_rows = _rank_stability(scenario_rows)
    summary_rows = _scenario_summary(scenario_rows)

    _write_csv(out_dir / "weight_sensitivity_scores.csv", scenario_rows)
    _write_csv(out_dir / "weight_sensitivity_rank_stability.csv", rank_rows)
    _write_csv(out_dir / "weight_sensitivity_summary.csv", summary_rows)
    (out_dir / "README.md").write_text(
        _render_readme(
            bundles=bundles,
            scenario_rows=scenario_rows,
            rank_rows=rank_rows,
            summary_rows=summary_rows,
        ),
        encoding="utf-8",
    )

    max_score_rank_range = max((int(row["score_rank_range"]) for row in rank_rows), default=0)
    max_claim_gated_rank_range = max((int(row["claim_gated_rank_range"]) for row in rank_rows), default=0)
    return {
        "bundle_count": len(bundles),
        "scenario_count": len(SCENARIOS),
        "max_score_rank_range": max_score_rank_range,
        "max_claim_gated_rank_range": max_claim_gated_rank_range,
        "out_dir": str(out_dir),
    }


def _load_axis_scores(axis_matrix_path: Path) -> dict[str, dict[str, Any]]:
    rows = _read_csv(axis_matrix_path)
    bundles: dict[str, dict[str, Any]] = {}
    for row in rows:
        bundle_id = row["bundle_id"]
        bundle = bundles.setdefault(
            bundle_id,
            {
                "bundle_id": bundle_id,
                "run_id": row["run_id"],
                "dataset_id": row["dataset_id"],
                "final_claim": row["final_claim"],
                "axes": {},
            },
        )
        bundle["axes"][row["axis"]] = _as_float(row["score"])
    return bundles


def _score_scenarios(bundles: dict[str, dict[str, Any]], spec: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    ranks = claim_ranks(spec)
    for scenario_name, scenario in SCENARIOS.items():
        scenario_scores = []
        for bundle in bundles.values():
            epi_score = _score_bundle(bundle["axes"], spec, scenario)
            scenario_scores.append(
                {
                    "scenario": scenario_name,
                    "bundle_id": bundle["bundle_id"],
                    "run_id": bundle["run_id"],
                    "dataset_id": bundle["dataset_id"],
                    "final_claim": bundle["final_claim"],
                    "claim_rank": ranks[bundle["final_claim"]],
                    "epi_score": epi_score,
                }
            )

        score_ranked = sorted(scenario_scores, key=lambda row: (-row["epi_score"], row["bundle_id"]))
        claim_ranked = sorted(
            scenario_scores,
            key=lambda row: (-int(row["claim_rank"]), -row["epi_score"], row["bundle_id"]),
        )
        score_ranks = {row["bundle_id"]: rank for rank, row in enumerate(score_ranked, start=1)}
        claim_ranks_by_bundle = {row["bundle_id"]: rank for rank, row in enumerate(claim_ranked, start=1)}
        for row in scenario_scores:
            rows.append(
                {
                    "scenario": row["scenario"],
                    "bundle_id": row["bundle_id"],
                    "run_id": row["run_id"],
                    "dataset_id": row["dataset_id"],
                    "final_claim": row["final_claim"],
                    "epi_score": row["epi_score"],
                    "score_rank": score_ranks[row["bundle_id"]],
                    "claim_gated_rank": claim_ranks_by_bundle[row["bundle_id"]],
                }
            )
    return rows


def _score_bundle(axis_scores: dict[str, float], spec: dict[str, Any], scenario: dict[str, Any]) -> float:
    weights = _scenario_weights(axis_scores, spec, scenario)
    geometric = 1.0
    for axis, score in axis_scores.items():
        geometric *= max(score, 1e-12) ** weights[axis]
    min_axis = min(axis_scores.values())
    floor = float(spec["score"]["floor"])
    penalty_lambda = float(spec["score"]["lambda"])
    penalty = math.exp(-penalty_lambda * max(0.0, floor - min_axis))
    return round(100.0 * geometric * penalty, 3)


def _scenario_weights(axis_scores: dict[str, float], spec: dict[str, Any], scenario: dict[str, Any]) -> dict[str, float]:
    if scenario["type"] == "equal":
        raw = {axis: 1.0 for axis in axis_scores}
    else:
        multipliers = scenario.get("multipliers", {})
        raw = {
            axis: float(spec["score"]["axes"][axis]["weight"]) * float(multipliers.get(axis, 1.0))
            for axis in axis_scores
        }
    total = sum(raw.values())
    return {axis: value / total for axis, value in raw.items()}


def _rank_stability(scenario_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in scenario_rows:
        grouped.setdefault(row["bundle_id"], []).append(row)

    rows = []
    for bundle_id, rows_for_bundle in sorted(grouped.items()):
        base = next(row for row in rows_for_bundle if row["scenario"] == "normative")
        score_ranks = [int(row["score_rank"]) for row in rows_for_bundle]
        claim_gated_ranks = [int(row["claim_gated_rank"]) for row in rows_for_bundle]
        scores = [float(row["epi_score"]) for row in rows_for_bundle]
        rows.append(
            {
                "bundle_id": bundle_id,
                "run_id": base["run_id"],
                "dataset_id": base["dataset_id"],
                "final_claim": base["final_claim"],
                "normative_epi_score": base["epi_score"],
                "min_epi_score": round(min(scores), 3),
                "max_epi_score": round(max(scores), 3),
                "normative_score_rank": base["score_rank"],
                "min_score_rank": min(score_ranks),
                "max_score_rank": max(score_ranks),
                "score_rank_range": max(score_ranks) - min(score_ranks),
                "normative_claim_gated_rank": base["claim_gated_rank"],
                "min_claim_gated_rank": min(claim_gated_ranks),
                "max_claim_gated_rank": max(claim_gated_ranks),
                "claim_gated_rank_range": max(claim_gated_ranks) - min(claim_gated_ranks),
                "claim_invariant": True,
            }
        )
    return rows


def _scenario_summary(scenario_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in scenario_rows:
        grouped.setdefault(row["scenario"], []).append(row)

    rows = []
    for scenario, rows_for_scenario in grouped.items():
        top_score = min(rows_for_scenario, key=lambda row: int(row["score_rank"]))
        top_claim = min(rows_for_scenario, key=lambda row: int(row["claim_gated_rank"]))
        e1_in_top3 = sum(
            1 for row in rows_for_scenario if int(row["score_rank"]) <= 3 and row["final_claim"] == "E1"
        )
        rows.append(
            {
                "scenario": scenario,
                "top_score_run_id": top_score["run_id"],
                "top_score_final_claim": top_score["final_claim"],
                "top_score_value": top_score["epi_score"],
                "top_claim_gated_run_id": top_claim["run_id"],
                "top_claim_gated_final_claim": top_claim["final_claim"],
                "e1_runs_in_top3_by_score": e1_in_top3,
            }
        )
    return rows


def _render_readme(
    *,
    bundles: dict[str, dict[str, Any]],
    scenario_rows: list[dict[str, Any]],
    rank_rows: list[dict[str, Any]],
    summary_rows: list[dict[str, Any]],
) -> str:
    max_score_rank_range = max((int(row["score_rank_range"]) for row in rank_rows), default=0)
    max_claim_rank_range = max((int(row["claim_gated_rank_range"]) for row in rank_rows), default=0)
    scenarios_with_e1_top3 = sum(1 for row in summary_rows if int(row["e1_runs_in_top3_by_score"]) > 0)
    top_claims = sorted({row["top_claim_gated_final_claim"] for row in summary_rows})
    scenario_count = len({row["scenario"] for row in scenario_rows})
    return f"""# EpiBench Epi-Score Weight Sensitivity Panel

Generated from `reports/epibench_evidence_panels/score_axis_matrix.csv`.

## Purpose

This panel tests whether the paper's interpretation depends on a single convenient Epi-Score weight
choice. It perturbs the preregistered axis weights and compares score-only ranks with claim-gated
ranks. The claim itself is intentionally invariant because claim eligibility is controlled by dataset
evidence, split policy, label audit, failures, and hardware evidence rather than by score weights.

## Summary

- Bundles evaluated: `{len(bundles)}`.
- Weight scenarios: `{scenario_count}`.
- Maximum score-only rank range across scenarios: `{max_score_rank_range}`.
- Maximum claim-gated rank range across scenarios: `{max_claim_rank_range}`.
- Scenarios with at least one `E1` run in the score-only top 3: `{scenarios_with_e1_top3}`.
- Top claim-gated final claims observed across scenarios: `{', '.join(top_claims)}`.

## Generated Files

- `weight_sensitivity_scores.csv`: score and ranks for every bundle under every weight scenario.
- `weight_sensitivity_rank_stability.csv`: per-bundle score range and rank range across scenarios.
- `weight_sensitivity_summary.csv`: top score-only and top claim-gated run per scenario.

## Interpretation

If score-only ranks move under perturbation, that is expected and should be reported. The scientific
test is whether high-score but invalid runs can acquire stronger claims through reweighting. Under
EpiBench they cannot, because claim gates are not score-weight parameters.

## Boundary

This is a sensitivity analysis of a retrospective methodological score. It does not validate clinical
utility, regulatory safety, or deployment readiness.
"""


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _as_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


if __name__ == "__main__":
    raise SystemExit(main())
