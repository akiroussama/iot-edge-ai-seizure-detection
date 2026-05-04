"""
Genere 2 figures principales pour les slides :
1. ROC curves (LOSO pooled) des 4 modeles : DT, SVM, RF, MLP
2. Bar chart perf (recall LOSO) vs RAM ESP32 INT8

Sortie : results/figures/roc_loso.png et results/figures/perf_vs_ram.png
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, roc_curve
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

ROOT = Path(__file__).resolve().parent.parent
FEATURES_NPZ = ROOT / "data" / "multirun_features.npz"
ESP32_JSON = ROOT / "results" / "esp32_cost_estimate.json"
FIG_DIR = ROOT / "results" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)
RANDOM_STATE = 42


def loso_pooled_scores(model_factory, X, y, sub):
    y_true_all, y_score_all = [], []
    for ho in sorted(np.unique(sub).tolist()):
        train_mask = sub != ho
        test_mask = sub == ho
        if y[train_mask].sum() == 0 or y[test_mask].sum() == 0:
            continue
        scaler = StandardScaler()
        X_train = scaler.fit_transform(X[train_mask])
        X_test = scaler.transform(X[test_mask])
        y_train = y[train_mask]
        y_test = y[test_mask]
        model = model_factory()
        if isinstance(model, MLPClassifier):
            n_pos = max(int(y_train.sum()), 1)
            n_neg = max(len(y_train) - n_pos, 1)
            wp = len(y_train) / (2.0 * n_pos)
            wn = len(y_train) / (2.0 * n_neg)
            rng = np.random.RandomState(RANDOM_STATE)
            pos_idx = np.where(y_train == 1)[0]
            neg_idx = np.where(y_train == 0)[0]
            factor = max(1, int(round(wp / wn)))
            train_idx = np.concatenate([neg_idx, np.tile(pos_idx, factor)])
            rng.shuffle(train_idx)
            model.fit(X_train[train_idx], y_train[train_idx])
        else:
            model.fit(X_train, y_train)
        if hasattr(model, "predict_proba"):
            scores = model.predict_proba(X_test)[:, 1]
        else:
            scores = model.decision_function(X_test)
        y_true_all.append(y_test)
        y_score_all.append(scores)
    return np.concatenate(y_true_all), np.concatenate(y_score_all)


def make_roc_figure(X, y, sub):
    print("Computing pooled ROC for 4 models (LOSO)...")
    factories = {
        "Decision Tree": lambda: DecisionTreeClassifier(class_weight="balanced", random_state=RANDOM_STATE),
        "SVM RBF": lambda: SVC(kernel="rbf", class_weight="balanced", probability=True, random_state=RANDOM_STATE),
        "Random Forest": lambda: RandomForestClassifier(n_estimators=100, class_weight="balanced", n_jobs=-1, random_state=RANDOM_STATE),
        "MLP 80->32->16->1": lambda: MLPClassifier(
            hidden_layer_sizes=(32, 16),
            activation="relu", solver="adam",
            max_iter=80, early_stopping=True, validation_fraction=0.15,
            n_iter_no_change=8, random_state=RANDOM_STATE,
        ),
    }
    fig, ax = plt.subplots(figsize=(7.5, 6))
    colors = {"Decision Tree": "tab:gray", "SVM RBF": "tab:orange",
              "Random Forest": "tab:green", "MLP 80->32->16->1": "tab:blue"}
    for name, factory in factories.items():
        print(f"  {name}...")
        y_t, y_s = loso_pooled_scores(factory, X, y, sub)
        fpr, tpr, _ = roc_curve(y_t, y_s)
        auc = roc_auc_score(y_t, y_s)
        ax.plot(fpr, tpr, lw=2, color=colors[name], label=f"{name}  (AUC={auc:.3f})")
    ax.plot([0, 1], [0, 1], "k--", lw=1, alpha=0.6, label="random")
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate (Sensitivity)")
    ax.set_title("ROC LOSO pooled (6 patients SeizeIT2, 33 925 windows)")
    ax.legend(loc="lower right", fontsize=10)
    ax.grid(alpha=0.3)
    out = FIG_DIR / "roc_loso.png"
    plt.tight_layout()
    plt.savefig(out, dpi=140)
    plt.close()
    print(f"  Saved : {out}")
    return out


def make_perf_ram_figure():
    print("Building perf vs RAM figure...")
    esp32 = json.loads(ESP32_JSON.read_text(encoding="utf-8"))
    multirun = json.loads((ROOT / "results" / "multirun_loso_summary.json").read_text(encoding="utf-8"))
    mlp = json.loads((ROOT / "results" / "mlp_loso_summary.json").read_text(encoding="utf-8"))

    models = ["decision_tree", "svm_rbf", "random_forest", "mlp_80_32_16_1"]
    labels = ["Decision Tree", "SVM RBF", "Random Forest", "MLP TinyML"]
    auc = [
        multirun["models"]["decision_tree"]["roc_auc_mean"],
        multirun["models"]["svm_rbf"]["roc_auc_mean"],
        multirun["models"]["random_forest"]["roc_auc_mean"],
        mlp["metrics_mean_std"]["roc_auc_mean"],
    ]
    ram_int8 = [esp32["models"][m]["int8"]["ram_kb_total"] for m in models]
    ram_fp32 = [esp32["models"][m]["fp32"]["ram_kb_total"] for m in models]

    fig, ax1 = plt.subplots(figsize=(9, 5.5))
    x = np.arange(len(labels))
    width = 0.35
    ax1.bar(x - width / 2, ram_fp32, width, label="RAM FP32 (kB)",
            color="tab:red", alpha=0.65)
    ax1.bar(x + width / 2, ram_int8, width, label="RAM INT8 (kB)",
            color="tab:blue", alpha=0.85)
    ax1.axhline(520, color="black", linestyle="--", lw=1.2,
                label="ESP32 SRAM ceiling (520 kB)")
    ax1.set_ylabel("RAM (kB)  -- log scale", fontsize=10)
    ax1.set_yscale("log")
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, fontsize=10)
    ax1.legend(loc="upper left", fontsize=9)
    ax1.grid(alpha=0.3, which="both")

    ax2 = ax1.twinx()
    ax2.plot(x, auc, marker="D", color="darkgreen", lw=2, ms=10,
             label="LOSO ROC AUC")
    ax2.set_ylabel("LOSO ROC AUC (LOSO inter-patient)", color="darkgreen", fontsize=10)
    ax2.set_ylim(0.4, 1.0)
    ax2.tick_params(axis="y", labelcolor="darkgreen")
    for xi, auci in zip(x, auc):
        ax2.annotate(f"{auci:.3f}", (xi, auci), textcoords="offset points",
                     xytext=(0, 10), ha="center", color="darkgreen", fontsize=10)
    ax2.legend(loc="upper right", fontsize=9)

    plt.title("Performance LOSO vs empreinte RAM ESP32  --  RF/SVM ne tiennent pas en FP32",
              fontsize=11)
    plt.tight_layout()
    out = FIG_DIR / "perf_vs_ram.png"
    plt.savefig(out, dpi=140)
    plt.close()
    print(f"  Saved : {out}")
    return out


def main() -> int:
    print(f"Loading features from {FEATURES_NPZ}...")
    data = np.load(FEATURES_NPZ)
    X = data["X"].astype(np.float32)
    y = data["y"].astype(np.int8)
    sub = data["subject"].astype(np.int32)
    print(f"  X={X.shape}, positives={int(y.sum())}, subjects={len(np.unique(sub))}")

    make_roc_figure(X, y, sub)
    make_perf_ram_figure()
    print("\nDone. Figures in", FIG_DIR)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
