"""
Leave-One-Subject-Out evaluation of DT/SVM/RF on multirun SeizeIT2 features.

Pour chaque sujet S :
  - Train sur tous les sujets sauf S
  - Test sur S
  - Calcule accuracy, recall (sensitivity), precision, FPR, F1, ROC AUC
  - IC Wilson 95% sur metriques de proportion

C'est l'evaluation la plus rigoureuse pour de la detection de crise wearable :
elle simule le scenario reel ou le modele est deploye sur un patient jamais
vu pendant l'entrainement.

Sortie :
    results/multirun_loso.csv             -- 1 ligne par (model, subject)
    results/multirun_loso_summary.json    -- mean +- std agreges par modele
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (confusion_matrix, f1_score, precision_score,
                             recall_score, roc_auc_score)
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

FEATURES_NPZ = Path(__file__).resolve().parent.parent / "data" / "multirun_features.npz"
RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

RANDOM_STATE = 42


def wilson_ci(successes: int, total: int, z: float = 1.96) -> tuple[float, float]:
    if total == 0:
        return 0.0, 0.0
    p = successes / total
    denom = 1 + z * z / total
    centre = (p + z * z / (2 * total)) / denom
    half = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / denom
    return max(0.0, centre - half), min(1.0, centre + half)


def metrics_with_ci(y_true: np.ndarray, y_pred: np.ndarray, y_score: np.ndarray) -> dict:
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel() if cm.size == 4 else (0, 0, 0, 0)
    n_pos = int(tp + fn)
    n_neg = int(tn + fp)
    n_total = n_pos + n_neg
    n_correct = int(tp + tn)
    accuracy = n_correct / n_total if n_total else 0.0
    acc_lo, acc_hi = wilson_ci(n_correct, n_total)
    rec_lo, rec_hi = wilson_ci(int(tp), n_pos) if n_pos else (0.0, 0.0)
    fpr_lo, fpr_hi = wilson_ci(int(fp), n_neg) if n_neg else (0.0, 0.0)
    precision = precision_score(y_true, y_pred, zero_division=0)
    recall = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    fpr = fp / n_neg if n_neg else 0.0
    if len(np.unique(y_true)) == 2 and y_score is not None:
        try:
            auc = float(roc_auc_score(y_true, y_score))
        except ValueError:
            auc = float("nan")
    else:
        auc = float("nan")
    return {
        "accuracy": float(accuracy),
        "accuracy_ci_lo": float(acc_lo),
        "accuracy_ci_hi": float(acc_hi),
        "precision": float(precision),
        "recall": float(recall),
        "recall_ci_lo": float(rec_lo),
        "recall_ci_hi": float(rec_hi),
        "f1": float(f1),
        "fpr": float(fpr),
        "fpr_ci_lo": float(fpr_lo),
        "fpr_ci_hi": float(fpr_hi),
        "roc_auc": auc,
        "tp": int(tp), "tn": int(tn), "fp": int(fp), "fn": int(fn),
    }


def make_models() -> dict[str, object]:
    return {
        "decision_tree": DecisionTreeClassifier(
            class_weight="balanced", random_state=RANDOM_STATE
        ),
        "svm_rbf": SVC(
            kernel="rbf",
            C=1.0,
            class_weight="balanced",
            probability=True,
            random_state=RANDOM_STATE,
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=100,
            class_weight="balanced",
            n_jobs=-1,
            random_state=RANDOM_STATE,
        ),
    }


def evaluate_loso(X: np.ndarray, y: np.ndarray, sub: np.ndarray) -> list[dict]:
    rows: list[dict] = []
    subjects = sorted(np.unique(sub).tolist())
    for held_out in subjects:
        train_mask = sub != held_out
        test_mask = sub == held_out
        X_train, y_train = X[train_mask], y[train_mask]
        X_test, y_test = X[test_mask], y[test_mask]
        if y_test.sum() == 0 or y_train.sum() == 0:
            print(f"  SKIP held-out sub-{held_out:03d} (no positives in train or test)")
            continue
        scaler = StandardScaler()
        X_train_s = scaler.fit_transform(X_train)
        X_test_s = scaler.transform(X_test)

        for model_name, model in make_models().items():
            print(f"  held-out sub-{held_out:03d} - {model_name}...")
            model.fit(X_train_s, y_train)
            y_pred = model.predict(X_test_s)
            if hasattr(model, "predict_proba"):
                y_score = model.predict_proba(X_test_s)[:, 1]
            elif hasattr(model, "decision_function"):
                y_score = model.decision_function(X_test_s)
            else:
                y_score = y_pred.astype(float)
            m = metrics_with_ci(y_test, y_pred, y_score)
            m.update({
                "model": model_name,
                "held_out_subject": int(held_out),
                "n_train": int(len(y_train)),
                "n_test": int(len(y_test)),
                "n_test_pos": int(y_test.sum()),
                "n_train_pos": int(y_train.sum()),
            })
            rows.append(m)
    return rows


def aggregate(rows: list[dict]) -> dict:
    summary: dict[str, dict] = {}
    for model_name in {r["model"] for r in rows}:
        sub = [r for r in rows if r["model"] == model_name]
        agg: dict[str, float] = {}
        for k in ("accuracy", "precision", "recall", "f1", "fpr", "roc_auc"):
            vals = [r[k] for r in sub if not (isinstance(r[k], float) and math.isnan(r[k]))]
            if vals:
                agg[f"{k}_mean"] = float(np.mean(vals))
                agg[f"{k}_std"] = float(np.std(vals))
            else:
                agg[f"{k}_mean"] = float("nan")
                agg[f"{k}_std"] = float("nan")
        # Pooled (micro) aggregation: sum confusion-matrix cells across folds, then derive.
        # For very imbalanced multi-subject clinical detection the macro mean above is
        # dominated by single folds and overstates global sensitivity. Reported alongside
        # so the reader picks the right aggregator for the question being asked.
        tp = sum(int(r["tp"]) for r in sub)
        fn = sum(int(r["fn"]) for r in sub)
        fp = sum(int(r["fp"]) for r in sub)
        tn = sum(int(r["tn"]) for r in sub)
        n_pos = tp + fn
        n_neg = tn + fp
        n_total = n_pos + n_neg
        agg["recall_pooled"] = (tp / n_pos) if n_pos else 0.0
        agg["precision_pooled"] = (tp / (tp + fp)) if (tp + fp) else 0.0
        agg["fpr_pooled"] = (fp / n_neg) if n_neg else 0.0
        agg["accuracy_pooled"] = ((tp + tn) / n_total) if n_total else 0.0
        agg["tp_total"] = tp
        agg["fn_total"] = fn
        agg["fp_total"] = fp
        agg["tn_total"] = tn
        agg["n_positives"] = n_pos
        agg["n_negatives"] = n_neg
        summary[model_name] = agg
    return summary


def main() -> int:
    print(f"Loading features from {FEATURES_NPZ}...")
    data = np.load(FEATURES_NPZ)
    X = data["X"].astype(np.float32)
    y = data["y"].astype(np.int8)
    sub = data["subject"].astype(np.int32)
    subjects = sorted(np.unique(sub).tolist())
    print(f"  X shape    : {X.shape}")
    print(f"  Subjects   : {subjects}")
    print(f"  Positives  : {int(y.sum())} / {len(y)} ({100 * y.mean():.2f} %)")

    print(f"\nRunning Leave-One-Subject-Out (LOSO) CV with {len(subjects)} folds...")
    rows = evaluate_loso(X, y, sub)

    csv_lines = ["model,held_out_subject,accuracy,acc_lo,acc_hi,precision,"
                 "recall,rec_lo,rec_hi,f1,fpr,fpr_lo,fpr_hi,roc_auc,tp,tn,fp,fn,"
                 "n_train,n_test,n_test_pos,n_train_pos"]
    for r in rows:
        csv_lines.append(
            f"{r['model']},sub-{r['held_out_subject']:03d},"
            f"{r['accuracy']:.4f},{r['accuracy_ci_lo']:.4f},{r['accuracy_ci_hi']:.4f},"
            f"{r['precision']:.4f},{r['recall']:.4f},"
            f"{r['recall_ci_lo']:.4f},{r['recall_ci_hi']:.4f},{r['f1']:.4f},"
            f"{r['fpr']:.4f},{r['fpr_ci_lo']:.4f},{r['fpr_ci_hi']:.4f},"
            f"{r['roc_auc']:.4f},{r['tp']},{r['tn']},{r['fp']},{r['fn']},"
            f"{r['n_train']},{r['n_test']},{r['n_test_pos']},{r['n_train_pos']}"
        )
    (RESULTS_DIR / "multirun_loso.csv").write_text("\n".join(csv_lines), encoding="utf-8")

    summary = aggregate(rows)
    (RESULTS_DIR / "multirun_loso_summary.json").write_text(json.dumps({
        "dataset": "SeizeIT2 multirun (sub-001, 032, 085, 096, 124, 125)",
        "n_subjects": len(subjects),
        "n_windows": int(len(y)),
        "n_positives": int(y.sum()),
        "n_features": int(X.shape[1]),
        "validation": "Leave-One-Subject-Out",
        "random_state": RANDOM_STATE,
        "models": summary,
    }, indent=2), encoding="utf-8")

    print("\n" + "=" * 92)
    print(" SUMMARY (Leave-One-Subject-Out, mean +/- std across held-out subjects)")
    print("=" * 92)
    print(f"{'model':<16s} {'accuracy':<14s} {'recall':<14s} {'precision':<14s} "
          f"{'f1':<14s} {'fpr':<14s} {'roc_auc':<10s}")
    for name, agg in summary.items():
        print(f"{name:<16s} "
              f"{agg['accuracy_mean']:.3f}+/-{agg['accuracy_std']:.3f}   "
              f"{agg['recall_mean']:.3f}+/-{agg['recall_std']:.3f}   "
              f"{agg['precision_mean']:.3f}+/-{agg['precision_std']:.3f}   "
              f"{agg['f1_mean']:.3f}+/-{agg['f1_std']:.3f}   "
              f"{agg['fpr_mean']:.3f}+/-{agg['fpr_std']:.3f}   "
              f"{agg['roc_auc_mean']:.3f}")

    print(f"\nReminder paper Raman 2025 (intra-subject, 60 test windows) :")
    print(f"  Decision Tree : acc=0.85 prec=0.86 recall=0.83 fpr=0.13")
    print(f"  Random Forest : acc=0.95 prec=0.93 recall=1.00 fpr=0.15")
    print(f"  SVM          : acc=0.90 prec=0.909 recall=0.909 fpr=0.11")
    print(f"\nNote : LOSO is more demanding than Raman's 80/20 random split.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
