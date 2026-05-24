from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.epibench.certification import certify_result_bundle
from src.epibench.spec import claim_ranks, load_spec
from src.epibench.validation import validate_artifact


DEFAULT_EXAMPLES_ROOT = REPO_ROOT / "examples" / "epibench"
DEFAULT_OUT_DIR = REPO_ROOT / "reports" / "epibench_evidence_panels"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build manuscript-ready EpiBench evidence panels from result bundles."
    )
    parser.add_argument("--examples-root", type=Path, default=DEFAULT_EXAMPLES_ROOT)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument(
        "--bundle",
        action="append",
        default=None,
        help="Optional explicit result_bundle.yaml path. May be repeated.",
    )
    args = parser.parse_args()

    bundle_paths = [Path(path) for path in args.bundle] if args.bundle else _discover_bundles(args.examples_root)
    result = build_evidence_panels(bundle_paths=bundle_paths, out_dir=args.out_dir)
    print(f"Built {result['bundle_count']} EpiBench evidence-panel bundle rows in {args.out_dir}")
    return 0


def build_evidence_panels(bundle_paths: list[Path], out_dir: Path) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    spec = load_spec()
    ranks = claim_ranks(spec)
    records = [_collect_record(path, ranks) for path in sorted(bundle_paths)]

    summary_rows = _summary_rows(records)
    naive_rows = _rank_rows(summary_rows, ranks, mode="naive")
    claim_gated_rows = _rank_rows(summary_rows, ranks, mode="claim_gated")
    rank_comparison_rows = _rank_comparison(naive_rows, claim_gated_rows)
    waterfall_rows = _waterfall_rows(records, ranks)
    failure_rows = _failure_rows(records)
    score_axis_rows = _score_axis_rows(records)

    _write_csv(out_dir / "bundle_summary.csv", summary_rows)
    _write_csv(out_dir / "naive_score_leaderboard.csv", naive_rows)
    _write_csv(out_dir / "claim_gated_leaderboard.csv", claim_gated_rows)
    _write_csv(out_dir / "rank_comparison.csv", rank_comparison_rows)
    _write_csv(out_dir / "claim_gate_waterfall.csv", waterfall_rows)
    _write_csv(out_dir / "failure_matrix.csv", failure_rows)
    _write_csv(out_dir / "score_axis_matrix.csv", score_axis_rows)
    (out_dir / "README.md").write_text(_render_readme(records, rank_comparison_rows), encoding="utf-8")
    return {"bundle_count": len(records), "out_dir": str(out_dir)}


def _discover_bundles(examples_root: Path) -> list[Path]:
    return sorted(examples_root.glob("*/result_bundle.yaml"))


def _collect_record(bundle_path: Path, ranks: dict[str, int]) -> dict[str, Any]:
    bundle = validate_artifact("result-bundle", bundle_path)
    base_dir = bundle_path.parent
    dataset = validate_artifact("dataset-card", base_dir / bundle["dataset_card_path"])
    split = validate_artifact("split", base_dir / bundle["split_manifest_path"])
    failure_trace = validate_artifact("failure-trace", base_dir / bundle["failure_trace_path"])
    report = certify_result_bundle(bundle_path)
    final_claim = report["final_claim"]
    bundle_id = f"{bundle_path.parent.name}:{bundle['run_id']}"
    return {
        "bundle_id": bundle_id,
        "bundle_path": bundle_path,
        "run_id": bundle["run_id"],
        "dataset_id": dataset["dataset_id"],
        "track": bundle["track"],
        "model_name": bundle["model"]["name"],
        "model_family": bundle["model"]["family"],
        "requested_claim": bundle["requested_claim"],
        "final_claim": final_claim,
        "claim_rank": ranks[final_claim],
        "effective_tier": report["dataset_tier_evaluation"]["effective_tier"],
        "split_policy": split["split_policy"],
        "label_audit": dataset["labels"]["audit_status"],
        "epi_score": report["score"]["epi_score"],
        "floor_penalty_applied": report["score"]["floor_penalty_applied"],
        "axis_scores": report["score"]["axis_scores"],
        "ceilings": report["ceilings"],
        "blocking_reasons": report["blocking_reasons"],
        "forbidden_phrases": report["forbidden_phrases"],
        "badges": report["badges"],
        "metrics": bundle["metrics"],
        "failure_trace": failure_trace,
    }


def _summary_rows(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for record in records:
        metrics = record["metrics"]
        rows.append(
            {
                "run_id": record["run_id"],
                "bundle_id": record["bundle_id"],
                "dataset_id": record["dataset_id"],
                "track": record["track"],
                "model_name": record["model_name"],
                "model_family": record["model_family"],
                "requested_claim": record["requested_claim"],
                "final_claim": record["final_claim"],
                "effective_tier": record["effective_tier"],
                "split_policy": record["split_policy"],
                "label_audit": record["label_audit"],
                "epi_score": record["epi_score"],
                "floor_penalty_applied": record["floor_penalty_applied"],
                "event_sensitivity": metrics.get("event_sensitivity"),
                "false_alarms_per_24h": metrics.get("false_alarms_per_24h"),
                "event_f1": metrics.get("event_f1"),
                "brier_skill_score": metrics.get("brier_skill_score"),
                "blocking_reason_count": len(record["blocking_reasons"]),
                "forbidden_phrase_count": len(record["forbidden_phrases"]),
                "badge_count": len(record["badges"]),
                "bundle_path": _repo_relative(record["bundle_path"]),
            }
        )
    return rows


def _rank_rows(
    rows: list[dict[str, Any]],
    ranks: dict[str, int],
    mode: str,
) -> list[dict[str, Any]]:
    if mode == "naive":
        sorted_rows = sorted(rows, key=lambda row: float(row["epi_score"]), reverse=True)
    elif mode == "claim_gated":
        sorted_rows = sorted(
            rows,
            key=lambda row: (ranks[row["final_claim"]], float(row["epi_score"])),
            reverse=True,
        )
    else:
        raise ValueError(f"Unknown ranking mode: {mode}")
    ranked = []
    for rank, row in enumerate(sorted_rows, start=1):
        item = dict(row)
        item["rank"] = rank
        item["ranking_mode"] = mode
        ranked.append(item)
    return ranked


def _rank_comparison(
    naive_rows: list[dict[str, Any]],
    claim_gated_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    naive_rank = {row["bundle_id"]: int(row["rank"]) for row in naive_rows}
    gated_by_run = {row["bundle_id"]: row for row in claim_gated_rows}
    rows = []
    for bundle_id, gated in gated_by_run.items():
        item = {
            "bundle_id": bundle_id,
            "run_id": gated["run_id"],
            "dataset_id": gated["dataset_id"],
            "track": gated["track"],
            "model_name": gated["model_name"],
            "epi_score": gated["epi_score"],
            "final_claim": gated["final_claim"],
            "naive_rank": naive_rank[bundle_id],
            "claim_gated_rank": int(gated["rank"]),
            "rank_delta_claim_gated_minus_naive": int(gated["rank"]) - naive_rank[bundle_id],
            "interpretation": _rank_interpretation(gated, naive_rank[bundle_id], int(gated["rank"])),
        }
        rows.append(item)
    return sorted(rows, key=lambda row: int(row["claim_gated_rank"]))


def _rank_interpretation(row: dict[str, Any], naive_rank: int, gated_rank: int) -> str:
    if row["final_claim"] == "E1" and gated_rank > naive_rank:
        return "high_or_mid_score_claim_limited_by_evidence_gate"
    if row["final_claim"] in {"E2-PI", "E3", "E4"} and float(row["epi_score"]) < 10:
        return "claim_structure_valid_but_performance_poor"
    if gated_rank < naive_rank:
        return "claim_gate_promotes_more_defensible_evidence"
    return "rank_stable_under_claim_gate"


def _waterfall_rows(records: list[dict[str, Any]], ranks: dict[str, int]) -> list[dict[str, Any]]:
    rows = []
    for record in records:
        final_rank = ranks[record["final_claim"]]
        for gate_name, ceiling in record["ceilings"].items():
            rows.append(
                {
                    "run_id": record["run_id"],
                    "bundle_id": record["bundle_id"],
                    "dataset_id": record["dataset_id"],
                    "gate": gate_name,
                    "ceiling": ceiling,
                    "ceiling_rank": ranks[ceiling],
                    "final_claim": record["final_claim"],
                    "is_active_ceiling": ranks[ceiling] == final_rank,
                }
            )
    return rows


def _failure_rows(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for record in records:
        for sentinel in record["failure_trace"]["sentinels"]:
            rows.append(
                {
                    "run_id": record["run_id"],
                    "bundle_id": record["bundle_id"],
                    "dataset_id": record["dataset_id"],
                    "final_claim": record["final_claim"],
                    "sentinel_code": sentinel["code"],
                    "present": sentinel["present"],
                    "severity": sentinel["severity"],
                    "count": sentinel["count"],
                    "scope": sentinel["scope"],
                    "evidence": sentinel["evidence"],
                }
            )
    return rows


def _score_axis_rows(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for record in records:
        for axis, score in record["axis_scores"].items():
            rows.append(
                {
                    "run_id": record["run_id"],
                    "bundle_id": record["bundle_id"],
                    "dataset_id": record["dataset_id"],
                    "final_claim": record["final_claim"],
                    "axis": axis,
                    "score": score,
                    "floor_penalty_applied": record["floor_penalty_applied"],
                }
            )
    return rows


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _render_readme(records: list[dict[str, Any]], rank_rows: list[dict[str, Any]]) -> str:
    highest_naive = max(records, key=lambda record: float(record["epi_score"]))
    highest_claim = max(records, key=lambda record: (record["claim_rank"], float(record["epi_score"])))
    claim_counts = _counts(record["final_claim"] for record in records)
    tier_counts = _counts(record["effective_tier"] for record in records)
    interpretations = _counts(row["interpretation"] for row in rank_rows)
    return f"""# EpiBench Evidence Panels

Generated from machine-certified EpiBench result bundles.

## Purpose

These panels are manuscript artefacts, not new certification rules. They summarize why a leaderboard
line must be interpreted through dataset evidence, split policy, label audit, failure transparency,
and claim eligibility.

## Generated Files

- `bundle_summary.csv`: one row per result bundle.
- `naive_score_leaderboard.csv`: ranking by Epi-Score only.
- `claim_gated_leaderboard.csv`: ranking by final claim, then Epi-Score.
- `rank_comparison.csv`: explicit naive versus claim-gated rank movement.
- `claim_gate_waterfall.csv`: all claim ceilings per run.
- `failure_matrix.csv`: sentinel visibility matrix.
- `score_axis_matrix.csv`: per-axis Epi-Score inputs.

## Audit Highlights

- Bundle count: `{len(records)}`.
- Highest naive Epi-Score: `{highest_naive['run_id']}` with score `{highest_naive['epi_score']}` and final claim `{highest_naive['final_claim']}`.
- Highest claim-gated result: `{highest_claim['run_id']}` with final claim `{highest_claim['final_claim']}` and score `{highest_claim['epi_score']}`.
- Claim distribution: `{_render_counts(claim_counts)}`.
- Dataset tier distribution: `{_render_counts(tier_counts)}`.
- Rank interpretation distribution: `{_render_counts(interpretations)}`.

## Scientific Boundary

These panels do not imply clinical approval, device readiness, or deployment fitness. They are
retrospective evidence summaries under EpiBench v1.0-draft.
"""


def _counts(values: Any) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        counts[str(value)] = counts.get(str(value), 0) + 1
    return dict(sorted(counts.items()))


def _render_counts(counts: dict[str, int]) -> str:
    return ", ".join(f"{key}={value}" for key, value in counts.items()) or "none"


def _repo_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
