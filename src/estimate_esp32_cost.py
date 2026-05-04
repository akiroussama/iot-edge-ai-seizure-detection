"""
Estimation analytique des couts d'inference sur ESP32 (160 MHz, 520 KB SRAM)
pour les modeles entraines (DT, SVM, RF, MLP).

Methode :
- MACs (Multiply-Accumulate) comptes par modele :
    MLP   : sum(in_dim * out_dim) sur les couches denses
    DT    : depth_max * 1 comparaison (pas de MAC)
    RF    : n_estimators * depth_max comparaisons
    SVM   : n_support_vectors * n_features (RBF kernel)
- Cycles par MAC (ESP32, references croisees) :
    FP32 : 1.5 cycles/MAC (FPU + memory access)
    INT8 : 1.0 cycle/MAC (theorique, sans SIMD c'est rarement atteint)
- Latence = cycles / 160 MHz
- Energie = puissance_active * latence
    Puissance active : 70 mW @ 160 MHz (datasheet ESP32, mode CPU only)
- RAM = parametres (FP32 4 octets, INT8 1 octet) + buffer input

Sources :
- Datasheet ESP32 (Espressif rev 4.6, 2025) section 5.2 Power consumption
- MLPerf Tiny benchmark methodology (Banbury 2021, NeurIPS)
- TFLite Micro tensor arena dimensioning rule (typically 2x model size)
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

FEATURES_NPZ = Path(__file__).resolve().parent.parent / "data" / "multirun_features.npz"
RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

ESP32_FREQ_HZ = 160_000_000
ESP32_ACTIVE_MW = 70.0
CYCLES_PER_MAC_FP32 = 1.5
CYCLES_PER_MAC_INT8 = 1.0
TENSOR_ARENA_OVERHEAD = 2.0


def estimate_inference(macs: int, params: int, dtype: str = "fp32") -> dict:
    cycles_per_mac = CYCLES_PER_MAC_FP32 if dtype == "fp32" else CYCLES_PER_MAC_INT8
    bytes_per_param = 4 if dtype == "fp32" else 1
    cycles = macs * cycles_per_mac
    latency_s = cycles / ESP32_FREQ_HZ
    latency_us = latency_s * 1e6
    energy_uj = ESP32_ACTIVE_MW * 1e-3 * latency_s * 1e6
    model_size_kb = (params * bytes_per_param) / 1024.0
    arena_kb = model_size_kb * TENSOR_ARENA_OVERHEAD
    ram_total_kb = arena_kb + (80 * 4) / 1024.0  # input feature buffer
    return {
        "dtype": dtype,
        "params": int(params),
        "macs": int(macs),
        "cycles": int(round(cycles)),
        "latency_us": round(latency_us, 2),
        "energy_uj": round(energy_uj, 4),
        "model_kb": round(model_size_kb, 3),
        "arena_kb": round(arena_kb, 3),
        "ram_kb_total": round(ram_total_kb, 3),
        "ram_pct_esp32": round(100 * ram_total_kb / 520, 2),
    }


def cost_mlp(input_dim: int, hidden: tuple[int, ...], output_dim: int = 1) -> dict:
    layers = [input_dim, *hidden, output_dim]
    weights = sum(layers[i] * layers[i + 1] for i in range(len(layers) - 1))
    biases = sum(layers[i + 1] for i in range(len(layers) - 1))
    macs = sum(layers[i] * layers[i + 1] for i in range(len(layers) - 1))
    params = weights + biases
    return {
        "model": f"MLP ({input_dim} -> {hidden} -> {output_dim})",
        "fp32": estimate_inference(macs, params, "fp32"),
        "int8": estimate_inference(macs, params, "int8"),
    }


def cost_decision_tree(clf: DecisionTreeClassifier) -> dict:
    n_nodes = clf.tree_.node_count
    depth = int(clf.get_depth())
    macs = depth
    params = n_nodes * 4
    return {
        "model": f"DecisionTree (depth={depth}, nodes={n_nodes})",
        "fp32": estimate_inference(macs, params, "fp32"),
        "int8": estimate_inference(macs, params, "int8"),
    }


def cost_random_forest(clf: RandomForestClassifier) -> dict:
    n_estim = len(clf.estimators_)
    depths = [int(t.get_depth()) for t in clf.estimators_]
    nodes = [int(t.tree_.node_count) for t in clf.estimators_]
    macs = sum(depths)
    params = sum(nodes) * 4
    return {
        "model": f"RandomForest (n={n_estim}, mean_depth={np.mean(depths):.1f}, total_nodes={sum(nodes)})",
        "fp32": estimate_inference(macs, params, "fp32"),
        "int8": estimate_inference(macs, params, "int8"),
    }


def cost_svm_rbf(clf: SVC, n_features: int) -> dict:
    n_sv = int(clf.support_vectors_.shape[0])
    macs = n_sv * n_features
    params = n_sv * n_features + n_sv
    return {
        "model": f"SVM-RBF (n_support_vectors={n_sv})",
        "fp32": estimate_inference(macs, params, "fp32"),
        "int8": estimate_inference(macs, params, "int8"),
    }


def main() -> int:
    print("Loading features for fitting reference models...")
    data = np.load(FEATURES_NPZ)
    X = data["X"].astype(np.float32)
    y = data["y"].astype(np.int8)
    sub = data["subject"].astype(np.int32)
    held_out = sorted(np.unique(sub).tolist())[0]
    train_mask = sub != held_out
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X[train_mask])
    y_train = y[train_mask]

    print(f"Fitting reference models on {train_mask.sum()} train samples...")
    dt = DecisionTreeClassifier(class_weight="balanced", random_state=42).fit(X_train, y_train)
    rf = RandomForestClassifier(n_estimators=100, class_weight="balanced", n_jobs=-1, random_state=42).fit(X_train, y_train)
    svm = SVC(kernel="rbf", C=1.0, class_weight="balanced", random_state=42).fit(X_train, y_train)

    estimates = {
        "esp32_freq_mhz": ESP32_FREQ_HZ / 1e6,
        "esp32_sram_kb": 520,
        "esp32_active_mw": ESP32_ACTIVE_MW,
        "models": {
            "decision_tree": cost_decision_tree(dt),
            "svm_rbf": cost_svm_rbf(svm, X.shape[1]),
            "random_forest": cost_random_forest(rf),
            "mlp_80_32_16_1": cost_mlp(X.shape[1], (32, 16)),
        },
    }

    out = RESULTS_DIR / "esp32_cost_estimate.json"
    out.write_text(json.dumps(estimates, indent=2), encoding="utf-8")

    print("\n" + "=" * 100)
    print(" ESP32 cost estimate (160 MHz, 520 KB SRAM, 70 mW active power)")
    print("=" * 100)
    print(f"{'model':<60s} {'dtype':<6s} {'lat_us':>8s} {'eng_uJ':>8s} "
          f"{'model_kB':>9s} {'RAM_kB':>8s} {'RAM_%':>7s}")
    for model_name, cost in estimates["models"].items():
        for dtype in ("fp32", "int8"):
            c = cost[dtype]
            print(f"{cost['model'][:60]:<60s} {dtype:<6s} {c['latency_us']:>8.1f} "
                  f"{c['energy_uj']:>8.3f} {c['model_kb']:>9.2f} "
                  f"{c['ram_kb_total']:>8.2f} {c['ram_pct_esp32']:>6.2f} %")
    print(f"\nSaved : {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
