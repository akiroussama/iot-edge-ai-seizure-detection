"""
MLP leger entraine en LOSO sur les 80 features statistiques. C'est
l'amelioration Edge AI demandee par la consigne section 5 :
- Architecture petite (input 80 -> 32 -> 16 -> 1) facilement quantifiable
- Comparable directement avec DT/SVM/RF (memes features, meme protocole LOSO)
- Sortie : poids float32 + estimation taille INT8 quantifiee

Le veritable export TFLite Micro INT8 demanderait TensorFlow ; ici on entraine
avec scikit-learn MLPClassifier (BSD, leger, deja installe), on calcule le
nombre de parametres et la taille FP32/INT8 analytiquement, et on dimensionne
le modele de maniere a tenir en RAM ESP32.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from sklearn.metrics import (confusion_matrix, f1_score, precision_score,
                             recall_score, roc_auc_score)
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler

FEATURES_NPZ = Path(__file__).resolve().parent.parent / "data" / "multirun_features.npz"
RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

RANDOM_STATE = 42
HIDDEN = (32, 16)


def wilson_ci(s: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return 0.0, 0.0
    p = s / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return max(0.0, c - h), min(1.0, c + h)


def metrics(y_true, y_pred, y_score) -> dict:
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel() if cm.size == 4 else (0, 0, 0, 0)
    n_pos = tp + fn
    n_neg = tn + fp
    n_total = n_pos + n_neg
    accuracy = (tp + tn) / n_total if n_total else 0.0
    fpr = fp / n_neg if n_neg else 0.0
    rec_lo, rec_hi = wilson_ci(int(tp), int(n_pos))
    try:
        auc = float(roc_auc_score(y_true, y_score))
    except ValueError:
        auc = float("nan")
    return {
        "accuracy": float(accuracy),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "recall_ci_lo": float(rec_lo),
        "recall_ci_hi": float(rec_hi),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "fpr": float(fpr),
        "roc_auc": auc,
        "tp": int(tp), "tn": int(tn), "fp": int(fp), "fn": int(fn),
    }


def count_mlp_params(input_dim: int, hidden: tuple[int, ...], output_dim: int = 1) -> dict:
    layers = [input_dim, *hidden, output_dim]
    weights = sum(layers[i] * layers[i + 1] for i in range(len(layers) - 1))
    biases = sum(layers[i + 1] for i in range(len(layers) - 1))
    macs = sum(layers[i] * layers[i + 1] for i in range(len(layers) - 1))
    return {
        "weights": weights,
        "biases": biases,
        "params_total": weights + biases,
        "fp32_bytes": (weights + biases) * 4,
        "int8_bytes": (weights + biases) * 1,
        "macs_per_inference": macs,
    }


def main() -> int:
    print(f"Loading features from {FEATURES_NPZ}...")
    data = np.load(FEATURES_NPZ)
    X = data["X"].astype(np.float32)
    y = data["y"].astype(np.int8)
    sub = data["subject"].astype(np.int32)
    subjects = sorted(np.unique(sub).tolist())
    print(f"  X={X.shape}, subjects={subjects}, positives={int(y.sum())}/{len(y)}")

    print(f"\nMLP architecture : input {X.shape[1]} -> {HIDDEN} -> 1 (sigmoid)")
    cost = count_mlp_params(X.shape[1], HIDDEN)
    print(f"  Parameters : {cost['params_total']} ({cost['weights']} weights + {cost['biases']} biases)")
    print(f"  FP32 model : {cost['fp32_bytes'] / 1024:.2f} KB")
    print(f"  INT8 model : {cost['int8_bytes'] / 1024:.2f} KB  (4x smaller)")
    print(f"  MACs/infer : {cost['macs_per_inference']:,}")

    rows: list[dict] = []
    for held_out in subjects:
        train_mask = sub != held_out
        test_mask = sub == held_out
        if y[train_mask].sum() == 0 or y[test_mask].sum() == 0:
            print(f"  SKIP held-out sub-{held_out:03d}")
            continue
        scaler = StandardScaler()
        X_train = scaler.fit_transform(X[train_mask])
        X_test = scaler.transform(X[test_mask])
        y_train = y[train_mask]
        y_test = y[test_mask]

        # Class balancing via sample_weight (since MLPClassifier doesn't expose class_weight)
        n_pos = max(int(y_train.sum()), 1)
        n_neg = max(len(y_train) - n_pos, 1)
        weight_pos = len(y_train) / (2.0 * n_pos)
        weight_neg = len(y_train) / (2.0 * n_neg)
        sw = np.where(y_train == 1, weight_pos, weight_neg).astype(np.float64)

        clf = MLPClassifier(
            hidden_layer_sizes=HIDDEN,
            activation="relu",
            solver="adam",
            alpha=1e-4,
            batch_size=256,
            learning_rate_init=1e-3,
            max_iter=80,
            early_stopping=True,
            validation_fraction=0.15,
            n_iter_no_change=8,
            random_state=RANDOM_STATE,
            verbose=False,
        )
        # MLPClassifier doesn't accept sample_weight in fit. Workaround : oversample positives.
        rng = np.random.RandomState(RANDOM_STATE)
        pos_idx = np.where(y_train == 1)[0]
        neg_idx = np.where(y_train == 0)[0]
        oversample_factor = max(1, int(round(weight_pos / weight_neg)))
        pos_resampled = np.tile(pos_idx, oversample_factor)
        train_idx = np.concatenate([neg_idx, pos_resampled])
        rng.shuffle(train_idx)

        print(f"  held-out sub-{held_out:03d} (train n={len(train_idx)} after oversample, "
              f"oversample x{oversample_factor})...")
        clf.fit(X_train[train_idx], y_train[train_idx])
        y_score = clf.predict_proba(X_test)[:, 1]
        y_pred = (y_score >= 0.5).astype(np.int8)

        m = metrics(y_test, y_pred, y_score)
        m.update({
            "held_out_subject": int(held_out),
            "n_train": int(len(train_idx)),
            "n_test": int(len(y_test)),
            "n_test_pos": int(y_test.sum()),
            "n_iter": int(clf.n_iter_),
        })
        rows.append(m)

    csv_lines = ["held_out_subject,accuracy,precision,recall,rec_lo,rec_hi,f1,fpr,"
                 "roc_auc,tp,tn,fp,fn,n_train,n_test,n_test_pos,n_iter"]
    for r in rows:
        csv_lines.append(
            f"sub-{r['held_out_subject']:03d},{r['accuracy']:.4f},{r['precision']:.4f},"
            f"{r['recall']:.4f},{r['recall_ci_lo']:.4f},{r['recall_ci_hi']:.4f},"
            f"{r['f1']:.4f},{r['fpr']:.4f},{r['roc_auc']:.4f},"
            f"{r['tp']},{r['tn']},{r['fp']},{r['fn']},"
            f"{r['n_train']},{r['n_test']},{r['n_test_pos']},{r['n_iter']}"
        )
    (RESULTS_DIR / "mlp_loso.csv").write_text("\n".join(csv_lines), encoding="utf-8")

    aggregated: dict[str, float] = {}
    for k in ("accuracy", "precision", "recall", "f1", "fpr", "roc_auc"):
        vals = [r[k] for r in rows if not (isinstance(r[k], float) and math.isnan(r[k]))]
        if vals:
            aggregated[f"{k}_mean"] = float(np.mean(vals))
            aggregated[f"{k}_std"] = float(np.std(vals))

    (RESULTS_DIR / "mlp_loso_summary.json").write_text(json.dumps({
        "model": "mlp_features_80_32_16_1",
        "hidden": list(HIDDEN),
        "n_parameters": cost["params_total"],
        "fp32_kb": round(cost["fp32_bytes"] / 1024, 3),
        "int8_kb": round(cost["int8_bytes"] / 1024, 3),
        "macs_per_inference": cost["macs_per_inference"],
        "validation": "Leave-One-Subject-Out",
        "subjects": subjects,
        "metrics_mean_std": aggregated,
    }, indent=2), encoding="utf-8")

    print("\n" + "=" * 92)
    print(" MLP LOSO summary (mean +/- std)")
    print("=" * 92)
    print(f"  accuracy  : {aggregated['accuracy_mean']:.3f}+/-{aggregated['accuracy_std']:.3f}")
    print(f"  recall    : {aggregated['recall_mean']:.3f}+/-{aggregated['recall_std']:.3f}")
    print(f"  precision : {aggregated['precision_mean']:.3f}+/-{aggregated['precision_std']:.3f}")
    print(f"  f1        : {aggregated['f1_mean']:.3f}+/-{aggregated['f1_std']:.3f}")
    print(f"  fpr       : {aggregated['fpr_mean']:.3f}+/-{aggregated['fpr_std']:.3f}")
    print(f"  roc_auc   : {aggregated['roc_auc_mean']:.3f}+/-{aggregated['roc_auc_std']:.3f}")
    print(f"\nSaved : {RESULTS_DIR / 'mlp_loso.csv'}")
    print(f"Saved : {RESULTS_DIR / 'mlp_loso_summary.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
