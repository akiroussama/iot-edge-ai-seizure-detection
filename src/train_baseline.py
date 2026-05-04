"""
Reproduction du pipeline ML de Raman & Velmurugan 2025 sur SeizeIT2 sub-001 run-07.

3 modeles compares : Decision Tree, SVM (RBF), Random Forest.

Protocole :
- 5-fold StratifiedKFold (random_state=42) pour respecter la proportion de
  classes dans chaque split malgre le desequilibre 0.49% positifs
- class_weight='balanced' obligatoire pour DT, RF, SVM
- StandardScaler fit sur train, applied sur test pour eviter le leakage
- Metriques : accuracy, precision, recall, f1, FPR, ROC AUC
- IC Wilson 95% sur les metriques de proportion (accuracy, recall, FPR)

Sortie :
    results/baseline_run07.csv             -- 1 ligne par (model, fold)
    results/baseline_run07_summary.json    -- mean +- std agreges par modele
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (confusion_matrix, f1_score, precision_score,
                             recall_score, roc_auc_score)
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

FEATURES_NPZ = Path(__file__).resolve().parent.parent / "data" / "sub-001_run-07_features.npz"
RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

RANDOM_STATE = 42
N_FOLDS = 5


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


def evaluate_kfold(X: np.ndarray, y: np.ndarray) -> list[dict]:
    skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=RANDOM_STATE)
    rows: list[dict] = []
    for fold_idx, (train_idx, test_idx) in enumerate(skf.split(X, y)):
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]
        scaler = StandardScaler()
        X_train_s = scaler.fit_transform(X_train)
        X_test_s = scaler.transform(X_test)

        for model_name, model in make_models().items():
            print(f"  fold {fold_idx + 1}/{N_FOLDS} - {model_name}...")
            model.fit(X_train_s, y_train)
            y_pred = model.predict(X_test_s)
            if hasattr(model, "predict_proba"):
                y_score = model.predict_proba(X_test_s)[:, 1]
            elif hasattr(model, "decision_function"):
                y_score = model.decision_function(X_test_s)
            else:
                y_score = y_pred.astype(float)

            m = metrics_with_ci(y_test, y_pred, y_score)
            m.update({"model": model_name, "fold": int(fold_idx),
                      "n_train": int(len(y_train)), "n_test": int(len(y_test)),
                      "n_test_pos": int((y_test == 1).sum())})
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
        summary[model_name] = agg
    return summary


def main() -> int:
    print(f"Loading features from {FEATURES_NPZ}...")
    data = np.load(FEATURES_NPZ, allow_pickle=False)
    X = data["X"].astype(np.float32)
    y = data["y"].astype(np.int8)
    print(f"  X shape : {X.shape}")
    print(f"  y       : {int((y == 1).sum())} positives / {len(y)} ({100 * y.mean():.2f} %)")

    print(f"\nRunning {N_FOLDS}-fold stratified CV (random_state={RANDOM_STATE})...")
    rows = evaluate_kfold(X, y)

    csv_lines = ["model,fold,accuracy,acc_lo,acc_hi,precision,recall,rec_lo,rec_hi,f1,fpr,fpr_lo,fpr_hi,roc_auc,tp,tn,fp,fn,n_test_pos"]
    for r in rows:
        csv_lines.append(
            f"{r['model']},{r['fold']},{r['accuracy']:.4f},{r['accuracy_ci_lo']:.4f},"
            f"{r['accuracy_ci_hi']:.4f},{r['precision']:.4f},{r['recall']:.4f},"
            f"{r['recall_ci_lo']:.4f},{r['recall_ci_hi']:.4f},{r['f1']:.4f},"
            f"{r['fpr']:.4f},{r['fpr_ci_lo']:.4f},{r['fpr_ci_hi']:.4f},"
            f"{r['roc_auc']:.4f},{r['tp']},{r['tn']},{r['fp']},{r['fn']},"
            f"{r['n_test_pos']}"
        )
    (RESULTS_DIR / "baseline_run07.csv").write_text("\n".join(csv_lines), encoding="utf-8")

    summary = aggregate(rows)
    summary_path = RESULTS_DIR / "baseline_run07_summary.json"
    summary_path.write_text(json.dumps({
        "dataset": "SeizeIT2 sub-001 ses-01 run-07",
        "n_windows": int(len(y)),
        "n_positives": int((y == 1).sum()),
        "n_features": int(X.shape[1]),
        "n_folds": N_FOLDS,
        "random_state": RANDOM_STATE,
        "models": summary,
    }, indent=2), encoding="utf-8")

    print("\n" + "=" * 80)
    print(" SUMMARY (5-fold CV, mean +/- std)")
    print("=" * 80)
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

    print(f"\nSaved : {RESULTS_DIR / 'baseline_run07.csv'}")
    print(f"Saved : {summary_path}")
    print("\nReminder paper Raman 2025 (for comparison) :")
    print("  Decision Tree : acc=0.85 prec=0.86 recall=0.83 fpr=0.13")
    print("  Random Forest : acc=0.95 prec=0.93 recall=1.00 fpr=0.15")
    print("  SVM          : acc=0.90 prec=0.909 recall=0.909 fpr=0.11")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
