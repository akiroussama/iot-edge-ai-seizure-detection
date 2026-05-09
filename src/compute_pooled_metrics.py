"""Recompute pooled (micro) metrics from per-subject LOSO CSV.

Reads `results/multirun_loso.csv` and `results/mlp_loso.csv`, sums TP/FN/FP/TN
across all folds, then derives global accuracy / recall / FPR.

Why this script exists:
The original pipeline `train_multirun.py` aggregated metrics via
`np.mean(per_subject_metrics)` — i.e. macro-average. For an extremely imbalanced
multi-subject clinical detection task, the right aggregator is the pooled
(micro) one: `sum(TP) / sum(N_positives)`. The macro mean weights each fold
equally regardless of how many seizure windows it contains, which is misleading
when one fold has 345 positives and another has 37.

This script post-processes the existing CSV to compute the correct pooled
metrics WITHOUT re-running the (expensive) training pipeline.

Trigger: feedback from Mme Manel on 2026-05-09 indicating an inconsistency in
the reported RF recall.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"


def pool_multirun(csv_path: Path) -> dict:
    """Pool per-subject TP/FN/FP/TN across folds for each model in multirun_loso.csv."""
    by_model: dict[str, dict[str, int]] = {}
    with csv_path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            m = row["model"]
            agg = by_model.setdefault(m, {"tp": 0, "fn": 0, "fp": 0, "tn": 0, "n_pos": 0, "n_neg": 0})
            tp, fn, fp, tn = int(row["tp"]), int(row["fn"]), int(row["fp"]), int(row["tn"])
            agg["tp"] += tp
            agg["fn"] += fn
            agg["fp"] += fp
            agg["tn"] += tn
            agg["n_pos"] += tp + fn
            agg["n_neg"] += tn + fp

    pooled: dict[str, dict] = {}
    for m, c in by_model.items():
        n_total = c["tp"] + c["tn"] + c["fp"] + c["fn"]
        pooled[m] = {
            "tp": c["tp"], "fn": c["fn"], "fp": c["fp"], "tn": c["tn"],
            "n_positives": c["n_pos"], "n_negatives": c["n_neg"], "n_total": n_total,
            "recall_pooled": c["tp"] / c["n_pos"] if c["n_pos"] else 0.0,
            "precision_pooled": c["tp"] / (c["tp"] + c["fp"]) if (c["tp"] + c["fp"]) else 0.0,
            "fpr_pooled": c["fp"] / c["n_neg"] if c["n_neg"] else 0.0,
            "accuracy_pooled": (c["tp"] + c["tn"]) / n_total if n_total else 0.0,
        }
    return pooled


def pool_mlp(csv_path: Path) -> dict:
    """Pool per-subject TP/FN/FP/TN for the MLP CSV (single model)."""
    agg = {"tp": 0, "fn": 0, "fp": 0, "tn": 0, "n_pos": 0, "n_neg": 0}
    with csv_path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tp, fn, fp, tn = int(row["tp"]), int(row["fn"]), int(row["fp"]), int(row["tn"])
            agg["tp"] += tp
            agg["fn"] += fn
            agg["fp"] += fp
            agg["tn"] += tn
            agg["n_pos"] += tp + fn
            agg["n_neg"] += tn + fp
    n_total = agg["tp"] + agg["tn"] + agg["fp"] + agg["fn"]
    return {
        "mlp_80_32_16_1": {
            "tp": agg["tp"], "fn": agg["fn"], "fp": agg["fp"], "tn": agg["tn"],
            "n_positives": agg["n_pos"], "n_negatives": agg["n_neg"], "n_total": n_total,
            "recall_pooled": agg["tp"] / agg["n_pos"] if agg["n_pos"] else 0.0,
            "precision_pooled": agg["tp"] / (agg["tp"] + agg["fp"]) if (agg["tp"] + agg["fp"]) else 0.0,
            "fpr_pooled": agg["fp"] / agg["n_neg"] if agg["n_neg"] else 0.0,
            "accuracy_pooled": (agg["tp"] + agg["tn"]) / n_total if n_total else 0.0,
        }
    }


def trivial_baseline(n_pos: int, n_total: int) -> dict:
    """Accuracy of the dummy classifier that predicts the majority class."""
    n_neg = n_total - n_pos
    majority = max(n_pos, n_neg)
    return {
        "strategy": "predict majority class (always negative if n_neg > n_pos)",
        "accuracy_baseline": majority / n_total if n_total else 0.0,
        "recall_baseline": 0.0 if n_neg >= n_pos else 1.0,
    }


def main() -> int:
    multirun_csv = RESULTS_DIR / "multirun_loso.csv"
    mlp_csv = RESULTS_DIR / "mlp_loso.csv"

    pooled = pool_multirun(multirun_csv)
    pooled.update(pool_mlp(mlp_csv))

    rf_n_pos = pooled["random_forest"]["n_positives"]
    rf_n_total = pooled["random_forest"]["n_total"]
    baseline = trivial_baseline(rf_n_pos, rf_n_total)

    output = {
        "dataset": "SeizeIT2 multirun (sub-001, 032, 085, 096, 124, 125)",
        "validation": "Leave-One-Subject-Out, pooled metrics",
        "aggregation": "micro (sum TP/FP/FN/TN across folds, then derive)",
        "rationale": (
            "Replaces the macro-average per-subject aggregation in "
            "multirun_loso_summary.json (recall_mean, etc.). For imbalanced "
            "multi-subject clinical detection, the pooled (micro) recall "
            "answers the actually-relevant question: 'out of all the real "
            "seizure windows in the dataset, what fraction did the system "
            "detect?'. Macro mean is dominated by single subjects (e.g. "
            "RF sub-085 recall 39.7%) and overstates global sensitivity."
        ),
        "trivial_baseline_dummy_classifier": baseline,
        "models": pooled,
        "trigger": "feedback Mme Manel 2026-05-09 — RF recall recheck request",
    }

    out_path = RESULTS_DIR / "multirun_loso_pooled.json"
    out_path.write_text(json.dumps(output, indent=2), encoding="utf-8")

    print(f"Pooled metrics written to {out_path}")
    print()
    print(f"Trivial baseline (predict all negative): accuracy = {baseline['accuracy_baseline']:.4f}")
    print()
    print(f"{'model':<24s} {'recall_pooled':>14s} {'acc_pooled':>12s} {'fpr_pooled':>12s} {'TP':>5s} {'/':>2s} {'N_pos':>6s}")
    for m, v in pooled.items():
        print(f"{m:<24s} {v['recall_pooled']:>14.4f} {v['accuracy_pooled']:>12.4f} "
              f"{v['fpr_pooled']:>12.4f} {v['tp']:>5d} {'/':>2s} {v['n_positives']:>6d}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
