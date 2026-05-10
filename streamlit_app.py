"""SeizureGuard Live — interactive demo for the IoT Devices defense.

Run with:  streamlit run streamlit_app.py

Four tabs:
1. Signal & context     — synthetic-but-realistic IMU with a tonic-clonic burst
2. Model arena          — replay 4 models on a real SeizeIT2 fold (window by window)
3. ESP32 cost dashboard — interactive RAM / latency / energy estimator
4. Trade-off explorer   — Pareto scatter AUC vs RAM, the deployable region

All numbers come from results/ in this repository (CSV + JSON), themselves
produced by src/ pipeline scripts. No live training, no live inference: the
demo replays the empirical per-fold counts from multirun_loso.csv and
mlp_loso.csv as a window-by-window timeline.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# --------------------------------------------------------------------- config
ROOT = Path(__file__).parent
RESULTS = ROOT / "results"
ESP32_SRAM_KB = 520
ESP32_FREQ_MHZ = 160
ESP32_ACTIVE_MW = 70.0

st.set_page_config(
    page_title="SeizureGuard Live",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------------------------------------------- data layer
@st.cache_data(show_spinner=False)
def load_pooled() -> dict:
    return json.loads((RESULTS / "multirun_loso_pooled.json").read_text(encoding="utf-8"))


@st.cache_data(show_spinner=False)
def load_cost() -> dict:
    return json.loads((RESULTS / "esp32_cost_estimate.json").read_text(encoding="utf-8"))


@st.cache_data(show_spinner=False)
def load_per_fold() -> tuple[pd.DataFrame, pd.DataFrame]:
    classical = pd.read_csv(RESULTS / "multirun_loso.csv")
    mlp = pd.read_csv(RESULTS / "mlp_loso.csv")
    return classical, mlp


@st.cache_data(show_spinner=False)
def load_mlp_summary() -> dict:
    return json.loads((RESULTS / "mlp_loso_summary.json").read_text(encoding="utf-8"))


# ------------------------------------------------------------------- helpers
MODEL_LABELS = {
    "decision_tree": "Decision Tree",
    "svm_rbf": "SVM (RBF)",
    "random_forest": "Random Forest",
    "mlp_80_32_16_1": "MLP TinyML",
}
MODEL_COLORS = {
    "decision_tree": "#7e8a96",
    "svm_rbf": "#a07cd0",
    "random_forest": "#d96a4f",
    "mlp_80_32_16_1": "#2ea27e",
}


def synth_imu(n_windows: int, seizure_window_indices: np.ndarray, seed: int = 42):
    """Synthetic accel-like trace at 25 Hz, 64 samples per 2.56 s window.

    Background: low-amplitude pink-ish noise + slow drift.
    During seizure windows: superimpose a 5–6 Hz rhythmic burst with a bell
    envelope, characteristic of a tonic-clonic event.
    """
    fs = 25
    spw = 64
    rng = np.random.default_rng(seed)

    n_samples = n_windows * spw
    t = np.arange(n_samples) / fs

    sig = 0.04 * rng.standard_normal(n_samples)
    sig += 0.02 * np.sin(2 * np.pi * 0.07 * t + 0.3)

    if len(seizure_window_indices) > 0:
        s_start = int(seizure_window_indices.min()) * spw
        s_end = int(seizure_window_indices.max() + 1) * spw
        seg = np.arange(s_start, s_end)
        envelope = np.sin(np.pi * np.linspace(0.0, 1.0, len(seg))) ** 2
        burst = 0.45 * envelope * np.sin(2 * np.pi * 5.5 * t[seg])
        burst += 0.12 * envelope * rng.standard_normal(len(seg))
        sig[seg] += burst

    return t, sig


def replay_predictions(n_windows: int, pos_idx: np.ndarray, tp: int, fp: int, seed: int):
    """Lay out tp positives and fp negatives along a deterministic timeline.

    The model fires (predicts seizure) on `tp` of the `len(pos_idx)` positive
    windows (chosen deterministically) and on `fp` of the negative windows.
    Returns a binary array of length n_windows.
    """
    rng = np.random.default_rng(seed)
    preds = np.zeros(n_windows, dtype=int)

    if tp > 0 and len(pos_idx) > 0:
        chosen_pos = rng.choice(pos_idx, size=min(tp, len(pos_idx)), replace=False)
        preds[chosen_pos] = 1

    neg_idx = np.setdiff1d(np.arange(n_windows), pos_idx, assume_unique=False)
    if fp > 0 and len(neg_idx) > 0:
        chosen_neg = rng.choice(neg_idx, size=min(fp, len(neg_idx)), replace=False)
        preds[chosen_neg] = 1

    return preds


# -------------------------------------------------------------------- header
def render_sidebar():
    st.sidebar.title("SeizureGuard Live")
    st.sidebar.caption("Démonstration projet — IoT Devices, SUP'COM 2026")
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        """
**Paper de référence**
Raman & Velmurugan 2025 — *IoMT Wearable Device for Neurological Disorders*
([DOI 10.3390/engproc2025106013](https://doi.org/10.3390/engproc2025106013))

**Dataset**
SeizeIT2 (KU Leuven) — OpenNeuro `ds005873`
6 patients, **33 925 fenêtres**, **893 fenêtres de crise**

**Question scientifique**
Le pipeline du paper, transposé sur des données cliniques réelles avec
validation inter-patient (LOSO), tient-il sur un ESP32 ?

**Réponse courte (à découvrir dans les onglets)**
Le RF rate 97 % des crises en LOSO. Pire : il ne tient pas en RAM. Le MLP
TinyML est 56 × plus petit ET détecte plus de crises.
"""
    )
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        "**Repository**  \n"
        "[github.com/akiroussama/iot-edge-ai-seizure-detection]"
        "(https://github.com/akiroussama/iot-edge-ai-seizure-detection)"
    )


# ---------------------------------------------------------------- tab 1 view
def tab_signal(pooled: dict, classical: pd.DataFrame):
    st.header("1 — Signal et contexte")
    st.markdown(
        """
Une fenêtre de **2,56 s** échantillonnée à 25 Hz contient 64 mesures par axe.
Le signal ci-dessous est une trace accélérométrique synthétique calée sur la
sémiologie d'une crise tonico-clonique : **fond bas-niveau** sur une baseline
calme, puis **rafale rythmique 5–6 Hz** d'amplitude croissante puis décroissante
(enveloppe en cloche, durée typique 30–90 s).
"""
    )

    col1, col2 = st.columns([3, 1])
    with col2:
        n_windows = st.slider(
            "Durée totale (fenêtres de 2,56 s)", 100, 400, 220, step=20
        )
        seiz_start = st.slider("Début crise (fenêtre)", 20, n_windows - 40, 90)
        seiz_dur = st.slider("Durée crise (fenêtres)", 10, 80, 35)

    seiz_idx = np.arange(seiz_start, min(seiz_start + seiz_dur, n_windows))
    t, sig = synth_imu(n_windows, seiz_idx)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=t, y=sig, mode="lines",
            line=dict(color="#1c7ed6", width=1),
            name="Accel (axe Z, simulé)",
        )
    )
    fig.add_vrect(
        x0=seiz_start * 2.56, x1=(seiz_start + seiz_dur) * 2.56,
        fillcolor="#d96a4f", opacity=0.18, line_width=0,
        annotation_text="crise tonico-clonique",
        annotation_position="top left",
    )
    fig.update_layout(
        height=380, margin=dict(l=20, r=20, t=30, b=40),
        xaxis_title="Temps (s)", yaxis_title="Accélération (g, normalisée)",
        plot_bgcolor="#fafafa", paper_bgcolor="#ffffff", showlegend=False,
    )
    col1.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Mesures empiriques sur les 6 patients SeizeIT2")
    summary = []
    for _, row in classical.groupby("held_out_subject").first().reset_index().iterrows():
        summary.append(
            {
                "Patient": row["held_out_subject"],
                "Fenêtres totales": int(row["n_test"]),
                "Fenêtres crise": int(row["n_test_pos"]),
                "Prévalence (%)": f"{100 * row['n_test_pos'] / row['n_test']:.2f}",
            }
        )
    st.dataframe(pd.DataFrame(summary), use_container_width=True, hide_index=True)

    bag = pooled["models"]["random_forest"]
    st.info(
        f"**Constat global** : sur les {bag['n_total']} fenêtres totales, "
        f"{bag['n_positives']} sont des fenêtres de crise (prévalence "
        f"{100 * bag['n_positives'] / bag['n_total']:.2f} %). Un classifieur "
        f"trivial qui prédit toujours 'pas de crise' atteint déjà "
        f"{pooled['trivial_baseline_dummy_classifier']['accuracy_baseline']*100:.2f} % "
        "d'accuracy. Toute métrique d'accuracy proche de cette valeur trahit "
        "un modèle dégénéré."
    )


# ---------------------------------------------------------------- tab 2 view
def tab_arena(classical: pd.DataFrame, mlp: pd.DataFrame, pooled: dict):
    st.header("2 — Model arena : 4 modèles classent en direct")
    st.markdown(
        """
On rejoue la **timeline empirique** d'un patient mis en *test* (LOSO). Pour
chaque fenêtre, les 4 modèles donnent leur verdict ; les détections (TP) et
fausses alarmes (FP) viennent des comptages mesurés dans
`results/multirun_loso.csv` et `results/mlp_loso.csv`. Cliquez sur **Lancer
la lecture** pour voir le drame se dérouler.
"""
    )

    subjects = sorted(classical["held_out_subject"].unique())
    col_top1, col_top2, col_top3 = st.columns([2, 2, 1])
    subj = col_top1.selectbox(
        "Patient mis en test (held-out)", subjects, index=0,
        help="Le modèle est entraîné sur les 5 autres patients et testé sur celui-ci.",
    )
    speed = col_top2.select_slider(
        "Vitesse de lecture", options=["Lent", "Normal", "Rapide", "Instantané"],
        value="Rapide",
    )
    sleep_per_step = {"Lent": 0.04, "Normal": 0.015, "Rapide": 0.005, "Instantané": 0.0}[speed]

    # Per-subject row for each model
    subj_rows = classical[classical["held_out_subject"] == subj].set_index("model")
    mlp_row = mlp[mlp["held_out_subject"] == subj].iloc[0]

    n_test = int(subj_rows.iloc[0]["n_test"])
    n_pos = int(subj_rows.iloc[0]["n_test_pos"])
    rng = np.random.default_rng(hash(subj) % (2**31))
    pos_idx = np.sort(rng.choice(n_test, size=n_pos, replace=False))

    model_data = {
        "decision_tree": dict(
            tp=int(subj_rows.loc["decision_tree", "tp"]),
            fp=int(subj_rows.loc["decision_tree", "fp"]),
            fn=int(subj_rows.loc["decision_tree", "fn"]),
        ),
        "svm_rbf": dict(
            tp=int(subj_rows.loc["svm_rbf", "tp"]),
            fp=int(subj_rows.loc["svm_rbf", "fp"]),
            fn=int(subj_rows.loc["svm_rbf", "fn"]),
        ),
        "random_forest": dict(
            tp=int(subj_rows.loc["random_forest", "tp"]),
            fp=int(subj_rows.loc["random_forest", "fp"]),
            fn=int(subj_rows.loc["random_forest", "fn"]),
        ),
        "mlp_80_32_16_1": dict(
            tp=int(mlp_row["tp"]),
            fp=int(mlp_row["fp"]),
            fn=int(mlp_row["fn"]),
        ),
    }

    # Pre-compute timelines (deterministic per subject)
    timelines = {
        m: replay_predictions(n_test, pos_idx, d["tp"], d["fp"], seed=hash(m) % (2**31))
        for m, d in model_data.items()
    }

    col_top3.metric("Fenêtres", f"{n_test:,}")
    col_top3.metric("Crises (positives)", f"{n_pos}")

    play = st.button("Lancer la lecture", type="primary")
    st.caption(
        "Avant lecture : valeurs finales (somme sur toute la timeline). Pendant "
        "la lecture : compteur incrémental visualisant l'arrivée des fenêtres."
    )

    bars = st.empty()
    counters = st.empty()
    progress = st.progress(0.0)

    def render_state(step: int):
        step = max(0, min(step, n_test - 1))
        with counters.container():
            cols = st.columns(4)
            for i, (m, d) in enumerate(model_data.items()):
                seen = np.arange(step + 1)
                fired = timelines[m][:step + 1] == 1
                pos_mask = np.isin(seen, pos_idx)
                tp_now = int(np.sum(fired & pos_mask))
                fp_now = int(np.sum(fired & ~pos_mask))
                pos_seen = int(np.sum(pos_mask))

                with cols[i]:
                    st.metric(
                        MODEL_LABELS[m],
                        f"{tp_now} / {pos_seen}",
                        delta=f"{fp_now} fausses alarmes",
                        delta_color="inverse",
                    )
        # Bar chart of running recall for the 4 models
        recalls, fprs = [], []
        for m in model_data.keys():
            seen = np.arange(step + 1)
            fired = timelines[m][:step + 1] == 1
            pos_mask = np.isin(seen, pos_idx)
            n_pos_seen = max(1, int(np.sum(pos_mask)))
            n_neg_seen = max(1, int(np.sum(~pos_mask)))
            tp_now = int(np.sum(fired & pos_mask))
            fp_now = int(np.sum(fired & ~pos_mask))
            recalls.append(100 * tp_now / n_pos_seen)
            fprs.append(100 * fp_now / n_neg_seen)

        bar_fig = go.Figure()
        bar_fig.add_trace(go.Bar(
            x=[MODEL_LABELS[m] for m in model_data.keys()],
            y=recalls,
            marker_color=[MODEL_COLORS[m] for m in model_data.keys()],
            text=[f"{r:.1f} %" for r in recalls],
            textposition="outside",
            name="Recall (%)",
        ))
        bar_fig.update_layout(
            height=320, margin=dict(l=20, r=20, t=40, b=20),
            yaxis=dict(title="Recall % (sur fenêtres crise vues)", range=[0, max(60, max(recalls) * 1.2)]),
            title=f"Sensibilité courante — fenêtre {step + 1} / {n_test}",
            plot_bgcolor="#fafafa", paper_bgcolor="#ffffff", showlegend=False,
        )
        bars.plotly_chart(bar_fig, use_container_width=True, key=f"arena_bars_{subj}_{step}")

    if play:
        # Step in chunks for speed
        chunk = max(1, n_test // 200)
        for step in range(0, n_test, chunk):
            render_state(step)
            progress.progress(min(1.0, (step + chunk) / n_test))
            if sleep_per_step:
                time.sleep(sleep_per_step)
        render_state(n_test - 1)
        progress.progress(1.0)
        st.success(
            f"Lecture terminée. Sur les {n_pos} crises de **{subj}**, "
            f"RF en a détecté **{model_data['random_forest']['tp']}**, "
            f"MLP en a détecté **{model_data['mlp_80_32_16_1']['tp']}**, "
            f"DT **{model_data['decision_tree']['tp']}**, "
            f"SVM **{model_data['svm_rbf']['tp']}**."
        )
    else:
        render_state(n_test - 1)

    with st.expander("Pourquoi cette timeline et pas une autre ?"):
        st.markdown(
            """
Le tirage des indices positifs et la position des fausses alarmes sont
**déterministes par patient** (seed = `hash(subj)`). La séquence n'est pas la
trace temporelle exacte du dataset (qui n'est pas redistribuée pour des
raisons de licence et de poids), mais elle restitue **fidèlement les
comptages empiriques** de chaque modèle (TP, FP, FN, TN) tirés de
`results/multirun_loso.csv` et `results/mlp_loso.csv`. Toute métrique
courante converge vers la métrique mesurée à la fin de la lecture.
"""
        )


# ---------------------------------------------------------------- tab 3 view
def tab_cost(cost: dict):
    st.header("3 — ESP32 cost dashboard : ça tient ou pas ?")
    st.markdown(
        """
Les modèles entraînés ont des tailles très différentes. Sur un microcontrôleur
ESP32 (520 kB de SRAM, 160 MHz), le simple stockage du modèle peut **dépasser
la mémoire physique disponible**. Le tableau ci-dessous donne l'estimation
analytique pour les 4 modèles, en précision pleine (FP32) et quantifiés en
8 bits (INT8).
"""
    )

    rows = []
    for m_key, info in cost["models"].items():
        for q in ("fp32", "int8"):
            d = info[q]
            rows.append(
                {
                    "Modèle": MODEL_LABELS.get(m_key, m_key),
                    "Quantif.": q.upper(),
                    "Params": d["params"],
                    "RAM (KB)": d["ram_kb_total"],
                    "% SRAM": d["ram_pct_esp32"],
                    "Latence (µs)": d["latency_us"],
                    "Énergie (µJ)": d["energy_uj"],
                    "Tient sur ESP32": "OUI" if d["ram_pct_esp32"] <= 100 else "NON",
                }
            )
    df_cost = pd.DataFrame(rows)

    def _color_sram_pct(val: float) -> str:
        # Manual gradient (no matplotlib dependency): green → amber → red.
        try:
            v = float(val)
        except (TypeError, ValueError):
            return ""
        if v > 100:
            return "background-color: #d96a4f; color: white;"
        if v > 50:
            return "background-color: #f59e0b; color: white;"
        if v > 10:
            return "background-color: #f7c873; color: #333;"
        return "background-color: #2ea27e; color: white;"

    styler = df_cost.style.map(_color_sram_pct, subset=["% SRAM"])
    st.dataframe(styler, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("Vue visuelle : barre de remplissage SRAM")
    cols = st.columns(2)
    for col, q in zip(cols, ["fp32", "int8"]):
        with col:
            st.markdown(f"**Quantification {q.upper()}**")
            for m_key, info in cost["models"].items():
                pct = info[q]["ram_pct_esp32"]
                ram_kb = info[q]["ram_kb_total"]
                bar_color = "#2ea27e" if pct <= 100 else "#d96a4f"
                clamped = min(pct, 200)
                st.markdown(
                    f"<div style='font-size:0.85rem;margin-bottom:2px;'>"
                    f"<b>{MODEL_LABELS.get(m_key, m_key)}</b> — {ram_kb:.1f} KB ({pct:.1f}% SRAM)"
                    "</div>"
                    f"<div style='background:#eef2f5;border-radius:4px;height:18px;width:100%;position:relative;'>"
                    f"<div style='background:{bar_color};height:100%;width:{min(100, pct)}%;border-radius:4px;'></div>"
                    f"{'<div style=\"position:absolute;left:100%;top:0;height:100%;border-left:2px dashed #c92a2a;\"></div>' if pct > 100 else ''}"
                    "</div>"
                    "<div style='height:10px;'></div>",
                    unsafe_allow_html=True,
                )
            st.caption(
                f"Plafond physique ESP32 = {ESP32_SRAM_KB} KB de SRAM. La barre rouge "
                "passe la ligne pointillée = NE TIENT PAS."
            )

    st.markdown("---")
    st.subheader("Calculateur interactif (jouez avec les sliders)")
    st.markdown(
        "Estimez le coût d'un modèle alternatif. Les formules sont celles de "
        "`src/estimate_esp32_cost.py` — paramètres × 4 octets en FP32, ÷ 4 en INT8 ; "
        "MACs × 1,5 cycles ÷ 160 MHz pour la latence."
    )

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**Random Forest hypothétique**")
        rf_n_trees = st.slider("Nombre d'arbres", 10, 200, 100, step=10, key="rf_n")
        rf_depth = st.slider("Profondeur moyenne", 5, 40, 30, key="rf_d")
        rf_nodes = rf_n_trees * (2 ** min(rf_depth, 12))
        rf_params = rf_nodes * 4
        rf_ram_fp32 = rf_params * 4 / 1024 * 2  # arena = 2x params
        rf_ram_int8 = rf_params * 1 / 1024 * 2
        rf_macs = rf_n_trees * rf_depth
        rf_lat_int8 = rf_macs * 1.5 / ESP32_FREQ_MHZ
        rf_energy = rf_lat_int8 * ESP32_ACTIVE_MW / 1000
        rf_pct = 100 * rf_ram_int8 / ESP32_SRAM_KB
        st.metric("RAM INT8", f"{rf_ram_int8:.1f} KB", f"{rf_pct:.1f} % SRAM")
        st.metric("Latence INT8", f"{rf_lat_int8:.1f} µs")
        st.metric("Énergie INT8", f"{rf_energy:.2f} µJ")
        verdict = "TIENT" if rf_pct <= 100 else "NE TIENT PAS"
        verdict_color = "#2ea27e" if rf_pct <= 100 else "#d96a4f"
        st.markdown(
            f"<div style='background:{verdict_color};color:white;padding:8px;"
            f"border-radius:4px;text-align:center;font-weight:bold;'>"
            f"Verdict : {verdict}</div>", unsafe_allow_html=True
        )

    with col_b:
        st.markdown("**MLP hypothétique**")
        mlp_in = st.slider("Entrée (features)", 10, 200, 80, step=10, key="mlp_in")
        mlp_h1 = st.slider("Couche cachée 1", 8, 64, 32, step=4, key="mlp_h1")
        mlp_h2 = st.slider("Couche cachée 2", 4, 32, 16, step=2, key="mlp_h2")
        mlp_out = 1
        mlp_params = mlp_in * mlp_h1 + mlp_h1 + mlp_h1 * mlp_h2 + mlp_h2 + mlp_h2 * mlp_out + mlp_out
        mlp_ram_int8 = mlp_params * 1 / 1024 * 2
        mlp_macs = mlp_in * mlp_h1 + mlp_h1 * mlp_h2 + mlp_h2 * mlp_out
        mlp_lat_int8 = mlp_macs * 1.0 / ESP32_FREQ_MHZ
        mlp_energy = mlp_lat_int8 * ESP32_ACTIVE_MW / 1000
        mlp_pct = 100 * mlp_ram_int8 / ESP32_SRAM_KB
        st.metric("Paramètres", f"{mlp_params:,}")
        st.metric("RAM INT8", f"{mlp_ram_int8:.2f} KB", f"{mlp_pct:.2f} % SRAM")
        st.metric("Latence INT8", f"{mlp_lat_int8:.1f} µs")
        st.metric("Énergie INT8", f"{mlp_energy:.3f} µJ")
        verdict = "TIENT" if mlp_pct <= 100 else "NE TIENT PAS"
        verdict_color = "#2ea27e" if mlp_pct <= 100 else "#d96a4f"
        st.markdown(
            f"<div style='background:{verdict_color};color:white;padding:8px;"
            f"border-radius:4px;text-align:center;font-weight:bold;'>"
            f"Verdict : {verdict}</div>", unsafe_allow_html=True
        )


# ---------------------------------------------------------------- tab 4 view
def tab_pareto(pooled: dict, cost: dict):
    st.header("4 — Trade-off explorer : où est la frontière de Pareto ?")
    st.markdown(
        """
Sur deux axes — **AUC ROC** (perf) et **RAM ESP32 INT8** (coût mémoire) —
chaque modèle est un point. Le bon modèle est en haut à gauche : meilleure
perf, plus petite empreinte. La zone hachurée à droite (> 100 % SRAM)
contient les modèles **physiquement non-déployables** sur ESP32.
"""
    )

    # AUC pooled isn't in the pooled JSON; use macro mean from CSV as a proxy.
    classical_csv = pd.read_csv(RESULTS / "multirun_loso.csv")
    mlp_csv = pd.read_csv(RESULTS / "mlp_loso.csv")
    auc_by_model = {
        "decision_tree": classical_csv[classical_csv["model"] == "decision_tree"]["roc_auc"].mean(),
        "svm_rbf": classical_csv[classical_csv["model"] == "svm_rbf"]["roc_auc"].mean(),
        "random_forest": classical_csv[classical_csv["model"] == "random_forest"]["roc_auc"].mean(),
        "mlp_80_32_16_1": mlp_csv["roc_auc"].mean(),
    }

    rows = []
    for m_key, auc in auc_by_model.items():
        for q in ("fp32", "int8"):
            d = cost["models"][m_key][q]
            recall_pooled = pooled["models"][m_key]["recall_pooled"]
            rows.append(
                {
                    "model": MODEL_LABELS.get(m_key, m_key),
                    "quantif": q.upper(),
                    "ram_kb": d["ram_kb_total"],
                    "auc": float(auc),
                    "recall_pooled": float(recall_pooled),
                    "deployable": d["ram_pct_esp32"] <= 100,
                    "label": f"{MODEL_LABELS.get(m_key, m_key)} {q.upper()}",
                }
            )
    df_pareto = pd.DataFrame(rows)

    fig = go.Figure()
    fig.add_vrect(
        x0=ESP32_SRAM_KB, x1=df_pareto["ram_kb"].max() * 1.1,
        fillcolor="#d96a4f", opacity=0.10, line_width=0,
        annotation_text="hors limites ESP32 (520 KB SRAM)",
        annotation_position="top right",
    )
    for _, row in df_pareto.iterrows():
        marker_color = "#2ea27e" if row["deployable"] else "#d96a4f"
        symbol = "circle" if row["quantif"] == "INT8" else "square"
        fig.add_trace(
            go.Scatter(
                x=[row["ram_kb"]], y=[row["auc"]],
                mode="markers+text",
                marker=dict(size=18, color=marker_color, symbol=symbol, line=dict(color="white", width=2)),
                text=[row["label"]], textposition="top center",
                hovertemplate=(
                    f"<b>{row['model']} {row['quantif']}</b><br>"
                    f"RAM = {row['ram_kb']:.1f} KB<br>"
                    f"AUC = {row['auc']:.3f}<br>"
                    f"Recall pooled = {row['recall_pooled']*100:.2f} %<br>"
                    f"Déployable : {'OUI' if row['deployable'] else 'NON'}"
                    "<extra></extra>"
                ),
                showlegend=False,
            )
        )
    fig.update_xaxes(title="RAM ESP32 (KB, échelle log)", type="log")
    fig.update_yaxes(title="AUC ROC moyen (LOSO)", range=[0.4, 0.85])
    fig.update_layout(
        height=520, margin=dict(l=20, r=20, t=20, b=40),
        plot_bgcolor="#fafafa", paper_bgcolor="#ffffff",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        """
**Lecture du graphe**
- Les **carrés** sont les modèles en FP32, les **cercles** en INT8.
- Les points **rouges** sortent de l'enveloppe ESP32 — on peut les évaluer en
  laboratoire mais pas les embarquer.
- Les points **verts** sont déployables en pratique.
- Le **MLP TinyML INT8** (cercle vert en bas à gauche) est le seul point qui
  combine déployabilité ET recall pooled supérieur au RF.
"""
    )


# ------------------------------------------------------------- tab 5 view
def tab_wizard(pooled: dict, classical: pd.DataFrame, mlp: pd.DataFrame, cost: dict):
    st.header("5 — Pipeline complet : du paper à l'ESP32")
    st.caption(
        "Visite guidée du travail réalisé, étape par étape. Chaque étape précise "
        "ce qu'on a fait, pourquoi, et le fichier du repo qui l'implémente."
    )

    steps = [
        ("Problématique",            _wiz_problem),
        ("Dataset SeizeIT2",         _wiz_dataset),
        ("Préprocessing",            _wiz_preproc),
        ("Fenêtrage + étiquetage",   _wiz_windowing),
        ("Features (80 par fenêtre)", _wiz_features),
        ("Modèles testés",           _wiz_models),
        ("Méthodologie LOSO",        _wiz_loso),
        ("Métriques (et leurs pièges)", _wiz_metrics),
        ("Résultats LOSO",           _wiz_results),
        ("Coût ESP32",               _wiz_esp32),
        ("Conclusion + perspectives", _wiz_conclusion),
    ]
    total = len(steps)

    if "wizard_step" not in st.session_state:
        st.session_state.wizard_step = 0

    def _go_prev():
        new = max(0, st.session_state.wizard_step - 1)
        st.session_state.wizard_step = new
        st.session_state.wiz_jump = new

    def _go_next():
        new = min(total - 1, st.session_state.wizard_step + 1)
        st.session_state.wizard_step = new
        st.session_state.wiz_jump = new

    def _on_jump():
        st.session_state.wizard_step = st.session_state.wiz_jump

    cur = max(0, min(st.session_state.wizard_step, total - 1))
    if "wiz_jump" not in st.session_state:
        st.session_state.wiz_jump = cur
    title, render_fn = steps[cur]

    st.progress((cur + 1) / total, text=f"Étape {cur + 1} / {total} — {title}")

    col_prev, _, col_jump, _, col_next = st.columns([1.4, 0.4, 2, 0.4, 1.4])
    col_prev.button(
        "◀  Précédent",
        disabled=cur == 0,
        key="wiz_prev",
        use_container_width=True,
        on_click=_go_prev,
    )
    with col_jump:
        st.selectbox(
            "Aller à",
            options=list(range(total)),
            format_func=lambda i: f"{i + 1}. {steps[i][0]}",
            key="wiz_jump",
            label_visibility="collapsed",
            on_change=_on_jump,
        )
    col_next.button(
        "Suivant  ▶",
        disabled=cur == total - 1,
        key="wiz_next",
        use_container_width=True,
        on_click=_go_next,
    )

    st.markdown("---")
    render_fn(pooled, classical, mlp, cost)


def _wiz_problem(pooled, classical, mlp, cost):
    st.subheader("Question scientifique")
    st.markdown(
        """
**Paper de référence** : Raman & Velmurugan 2025 — *An Intelligent IoMT Wearable
Device for Monitoring of Neurological Disorders*, Engineering Proceedings 106(1) 13.

**Promesse du paper** : un bracelet ESP32 + IMU sur le tibia, ML embarqué
(Decision Tree, SVM, Random Forest), détecte les crises tonico-cloniques avec
**95 % d'accuracy** et **100 % de recall**.

**Notre question** : si on prend leur chaîne de traitement telle quelle et qu'on
la teste sur des patients épileptiques réels (vs des sujets sains qui miment),
est-ce que la performance tient ?
"""
    )

    st.subheader("4 contradictions internes du paper qu'on a identifiées")
    contradictions = [
        ("Capteur", "Abstract dit MPU6500, §3.1 dit LSM9DS1, §4 dit iPhone 11. Trois capteurs pour un même prototype."),
        ("FPR", "Abstract annonce < 4 %. Table 1 donne 11-15 %. Le RF déployé est même à 15 %."),
        ("Domain shift", "Entraînement sur iPhone, déploiement annoncé sur LSM9DS1 tibial. Aucune validation du transfert."),
        ("Discussion vs Table 1", "La discussion affirme « RF sans FPR ». Or Table 1 attribue au RF le FPR le plus élevé."),
    ]
    for label, body in contradictions:
        st.markdown(f"**{label}** — {body}")

    st.subheader("Approche choisie")
    st.markdown(
        """
1. **Repartir des sources** : prendre un dataset hospitalier de patients épileptiques réels.
2. **Reproduire le pipeline** : DT, SVM, RF avec features statistiques sur fenêtres glissantes.
3. **Évaluer en LOSO inter-patient** : entraîner sur 5 patients, tester sur le 6ᵉ que le modèle n'a jamais vu.
4. **Mesurer le coût Edge AI** : RAM, latence, énergie pour les 4 modèles sur ESP32.
5. **Proposer une amélioration** : MLP TinyML quantifié INT8 vs RF du paper.
"""
    )


def _wiz_dataset(pooled, classical, mlp, cost):
    rf = pooled["models"]["random_forest"]
    n_pos = rf["n_positives"]
    n_neg = rf["n_total"] - n_pos
    fig = go.Figure(
        data=[
            go.Pie(
                labels=["Fenêtres hors-crise", "Fenêtres-crise"],
                values=[n_neg, n_pos],
                hole=0.55,
                marker_colors=["#cdd5df", "#d96a4f"],
                textinfo="label+percent",
                textposition="outside",
                pull=[0, 0.06],
            )
        ]
    )
    fig.update_layout(
        title=f"Prévalence sur 6 patients : {n_pos} crises sur {rf['n_total']:,} fenêtres".replace(",", " "),
        height=360,
        margin=dict(t=60, b=20, l=20, r=20),
        showlegend=False,
        annotations=[dict(text=f"{100*n_pos/rf['n_total']:.2f}%<br><span style='font-size:11px;color:#666'>positives</span>", x=0.5, y=0.5, font_size=20, showarrow=False)],
    )
    st.plotly_chart(fig, use_container_width=True, key="wiz_fig_prevalence")

    st.subheader("SeizeIT2 — pourquoi ce dataset")
    st.markdown(
        """
- **Source officielle** : OpenNeuro `ds005873` ([DOI 10.18112/openneuro.ds005873.v1.1.0](https://openneuro.org/datasets/ds005873)).
- **Producteur** : KU Leuven Hospital, Belgique.
- **Licence** : CC0 (domaine public).
- **Format** : BIDS 1.8.0 standard.
- **Pourquoi celui-là** : seul dataset public à combiner **IMU + 2 EEG** sur **patients épileptiques réels** — ce que demande explicitement le syllabus du cours.
"""
    )

    st.subheader("Caractéristiques techniques")
    st.dataframe(
        pd.DataFrame(
            [
                ["Patients disponibles", "125"],
                ["Patients utilisés (PoC)", "6 (sub-001, 032, 085, 096, 124, 125)"],
                ["Critère de sélection", "Présence de crises focal-to-bilateral tonico-cloniques"],
                ["IMU", "12 canaux @ 25 Hz (3 ACC + 3 GYRO × 2 SensorDots : cou + poitrine)"],
                ["EEG", "2 canaux behind-the-ear @ 256 Hz"],
                ["ECG + EMG", "Présents, non utilisés ici"],
                ["Hardware capture", "Byteflies SensorDot (basse consommation)"],
                ["Annotations", "events.tsv BIDS — onset, duration, eventType, lateralization"],
                ["Durée par run", "~18 heures"],
                ["Accès", "S3 public, sans login"],
            ],
            columns=["Élément", "Valeur"],
        ),
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Exemple d'annotation crise (events.tsv)")
    st.code(
        "onset\tduration\teventType\tlateralization\n"
        "5421.32\t87.5\tsz_foc_f2b\tleft\n"
        "...",
        language="text",
    )
    st.caption("`sz_foc_f2b` = focal-to-bilateral seizure. C'est le code utilisé par les neurologues du KU Leuven Hospital pour étiqueter les fenêtres de crise.")

    st.subheader("Fichier du repo")
    st.code("src/load_data.py", language="text")
    st.markdown("Indexe les EDF et events.tsv via l'API OpenNeuro S3, charge en mémoire via `mne.io.read_raw_edf`.")


def _wiz_preproc(pooled, classical, mlp, cost):
    fs = 25
    rng = np.random.default_rng(42)
    t = np.arange(fs * 8) / fs
    base = 0.45 * np.sin(2 * np.pi * 2 * t)
    high_freq = 0.20 * np.sin(2 * np.pi * 18 * t)
    noise = 0.25 * rng.standard_normal(len(t))
    noisy = base + high_freq + noise
    w = 5
    filtered = np.convolve(noisy, np.ones(w) / w, mode="same")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=t, y=noisy, name="Signal brut (bruité)", line=dict(color="#a0a8b1", width=1.2)))
    fig.add_trace(go.Scatter(x=t, y=filtered, name="Après passe-bas", line=dict(color="#2ea27e", width=2.4)))
    fig.update_layout(
        title="Effet du filtre passe-bas : élimination du bruit > 10 Hz, conservation de la composante 0–5 Hz",
        xaxis_title="Temps (s)",
        yaxis_title="Accélération normalisée (g)",
        height=340,
        margin=dict(t=60, b=40, l=40, r=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig, use_container_width=True, key="wiz_fig_filter")

    st.subheader("Pré-traitement du signal")
    st.markdown(
        """
Le signal brut contient du bruit haute-fréquence (60 Hz secteur, parasites moteurs,
gel d'électrodes) qu'il faut supprimer avant l'extraction de features.
"""
    )

    st.subheader("Filtre Butterworth passe-bas")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**EEG**")
        st.markdown("- Coupure : **20 Hz**")
        st.markdown("- Ordre : 4")
        st.markdown("- Justification : la bande utile pour les crises est 0,5–13 Hz (thêta + alpha). Au-delà de 20 Hz = bruit musculaire et secteur.")
    with col_b:
        st.markdown("**IMU (accéléromètre + gyroscope)**")
        st.markdown("- Coupure : **10 Hz**")
        st.markdown("- Ordre : 4")
        st.markdown("- Justification : la marche est à 1–3 Hz, les secousses myocloniques à 4–7 Hz. Au-delà de 10 Hz = vibrations parasites.")

    st.subheader("Downsampling EEG")
    st.markdown(
        """
- EEG natif : 256 Hz. IMU natif : 25 Hz.
- On **resample l'EEG à 25 Hz** pour aligner les deux modalités sur la même horloge.
- C'est un **choix volontairement différent du paper Raman** (qui travaille à 50 Hz) : on s'aligne sur le hardware basse-consommation Byteflies, pas sur l'iPhone.
"""
    )

    st.subheader("Fichier du repo")
    st.code("src/preprocess.py", language="text")
    st.markdown("`scipy.signal.butter` + `scipy.signal.filtfilt` (filtrage zéro-phase) + downsampling polyphasique via `scipy.signal.resample_poly`.")


def _wiz_windowing(pooled, classical, mlp, cost):
    fs = 25
    rng = np.random.default_rng(7)
    t = np.arange(fs * 16) / fs
    sig = 0.04 * rng.standard_normal(len(t))
    crisis_start, crisis_end = 6.0, 12.0
    mask = (t >= crisis_start) & (t <= crisis_end)
    env = np.where(mask, np.sin(np.pi * (t - crisis_start) / (crisis_end - crisis_start)) ** 2, 0)
    sig += 0.55 * env * np.sin(2 * np.pi * 5.5 * t)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=t, y=sig, name="Signal accel (ex.)", line=dict(color="#1c7ed6", width=1.4)))
    fig.add_vrect(
        x0=crisis_start, x1=crisis_end,
        fillcolor="#d96a4f", opacity=0.18, line_width=0,
        annotation_text="Crise (events.tsv)",
        annotation_position="top left",
        annotation_font_color="#a13b1f",
    )
    win_size = 2.56
    step = 1.28
    win_starts = np.arange(0, t.max() - win_size + 1e-9, step)
    for i, ws in enumerate(win_starts):
        we = ws + win_size
        overlaps_crisis = (we > crisis_start) and (ws < crisis_end)
        color = "rgba(217,106,79,0.65)" if overlaps_crisis else "rgba(150,162,170,0.4)"
        fig.add_shape(
            type="rect", x0=ws, x1=we, y0=-1.05, y1=-0.92,
            line=dict(color=color, width=0), fillcolor=color,
        )
    fig.add_annotation(x=t.max() / 2, y=-1.18, text="fenêtres 2,56 s (rose = label 1, gris = label 0)", showarrow=False, font_size=11, font_color="#555")
    fig.update_layout(
        title="Étiquetage par chevauchement : une fenêtre est positive si elle touche un intervalle de crise",
        xaxis_title="Temps (s)",
        yaxis_title="Accélération (g, normalisée)",
        yaxis_range=[-1.35, 0.95],
        height=400,
        margin=dict(t=60, b=40, l=40, r=20),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True, key="wiz_fig_window")

    st.subheader("Découpage en fenêtres glissantes")
    st.markdown(
        """
Le ML supervisé classifie une **fenêtre temporelle**, pas un signal continu. On
découpe donc chaque enregistrement en petites tranches.
"""
    )

    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Durée fenêtre", "2,56 s", "= 64 samples @ 25 Hz")
    col_b.metric("Recouvrement", "50 %", "= pas de 1,28 s")
    col_c.metric("Canaux", "8", "= 6 IMU + 2 EEG après alignement")

    st.subheader("Étiquetage : crise ou pas crise ?")
    st.markdown(
        """
On consulte le fichier `events.tsv` du dataset. Pour chaque fenêtre `[t, t+2,56s]` :

- Si l'intervalle **chevauche** un `(onset, onset+duration)` annoté comme crise → étiquette **1**.
- Sinon → étiquette **0**.
"""
    )

    st.subheader("Volume final sur les 6 patients")
    rf = pooled["models"]["random_forest"]
    col_x, col_y, col_z = st.columns(3)
    col_x.metric("Fenêtres totales", f"{rf['n_total']:,}".replace(",", " "))
    col_y.metric("Fenêtres-crise (positives)", f"{rf['n_positives']}")
    col_z.metric("Prévalence", f"{100 * rf['n_positives'] / rf['n_total']:.2f} %")

    st.info(
        "Lecture : **2,63 % des fenêtres** contiennent un morceau de crise. C'est ce "
        "déséquilibre qui rend l'accuracy trompeuse et oblige à regarder le recall et le F1."
    )

    st.subheader("Fichier du repo")
    st.code("src/pipeline_multirun.py", language="text")
    st.markdown("Boucle sur les 6 patients, applique le fenêtrage 2,56 s × 50 % overlap, génère les paires `(X_features, y_label)`.")


def _wiz_features(pooled, classical, mlp, cost):
    st.subheader("10 features statistiques par canal")
    st.markdown(
        """
Chaque fenêtre est transformée en un **vecteur de 80 features** (10 features × 8
canaux : 6 IMU + 2 EEG). C'est ce vecteur qui sert d'entrée aux modèles ML.
"""
    )

    features_df = pd.DataFrame(
        [
            ["mean", "Moyenne temporelle", "Centre du signal — varie pendant une crise"],
            ["variance", "Dispersion autour de la moyenne", "Amplitude des oscillations — explose en crise"],
            ["skewness", "Asymétrie de la distribution", "Asymétrie temporelle — discrimine secousses"],
            ["kurtosis", "Aplatissement / queue lourde", "Pics extrêmes — typiques des secousses myocloniques"],
            ["RMS", "Root Mean Square (énergie)", "Énergie globale — crise = énergie élevée"],
            ["Higuchi fractal dim.", "Complexité du signal", "Régularité — décroît en crise"],
            ["spectral entropy", "Entropie du spectre de Fourier", "Désordre fréquentiel — crise = plus régulier"],
            ["mean frequency", "Fréquence moyenne FFT", "Centre de masse spectral"],
            ["median frequency", "Fréquence médiane FFT", "Robuste aux pics — discrimine bandes thêta vs delta"],
            ["band power 4–13 Hz", "Énergie dans thêta + alpha", "Signature directe des crises tonico-cloniques"],
        ],
        columns=["Feature", "Définition", "Pourquoi pertinent en détection de crise"],
    )
    st.dataframe(features_df, use_container_width=True, hide_index=True)

    st.subheader("Reproduction des 6 features du paper Raman")
    st.markdown(
        """
Les 6 premiers features (variance, skewness, fractal dim, spectral entropy, mean
freq, median freq) sont **strictement ceux du paper**. On a ajouté 4 features
classiques de la communauté HAR (mean, kurtosis, RMS, band power) pour comparer
honnêtement et garder une base d'analyse en cas de défaillance des 6 originaux.
"""
    )

    st.subheader("Fichier du repo")
    st.code("src/features.py", language="text")
    st.markdown("`numpy` + `scipy.stats` pour les features temporelles, `scipy.fft` pour les fréquentielles, implémentation manuelle de la Higuchi fractal dimension (algorithme O(N log N)).")


def _wiz_models(pooled, classical, mlp, cost):
    st.subheader("4 modèles évalués en parallèle")
    st.markdown(
        "Trois modèles **issus du paper** + un **modèle Edge AI** qu'on propose comme amélioration."
    )

    models_df = pd.DataFrame(
        [
            ["Decision Tree", "Référence Raman", "max_depth=40, sklearn.tree", "Interprétable, baseline rapide"],
            ["SVM RBF", "Référence Raman", "kernel='rbf', C=1.0, sklearn.svm", "Bon classifieur dense, mais lourd en SRAM"],
            ["Random Forest", "Référence Raman + modèle champion du paper", "n_estimators=100, max_depth≈30, sklearn.ensemble", "Robuste mais énorme en mémoire"],
            ["MLP TinyML", "Notre proposition Edge AI", "80 → 32 → 16 → 1 (3 137 params), tensorflow.keras", "Compromis taille / sensibilité ; quantifiable INT8 trivialement"],
        ],
        columns=["Modèle", "Origine", "Architecture", "Justification"],
    )
    st.dataframe(models_df, use_container_width=True, hide_index=True)

    st.subheader("Pourquoi un MLP plutôt qu'un CNN 1D ou un Transformer ?")
    st.markdown(
        """
- **Contrainte hardware** : ESP32 a 520 KB de SRAM. Un CNN 1D simple (16 filtres × 3 couches) dépasse déjà 50-100 KB ; un Transformer plus de 200 KB.
- **Contrainte data** : 6 patients d'entraînement, c'est peu. Un modèle profond risque le sur-paramétrage.
- **MLP 80→32→16→1** : 3 137 paramètres, comparable au RF en surface mais 56× plus compact en INT8. Et il prend directement les **mêmes 80 features** que les baselines (pas de feature engineering séparé).
- CNN 1D / LSTM / Transformer sont dans les **perspectives** une fois le dataset étendu à 30-50 patients.
"""
    )

    st.subheader("Fichiers du repo")
    st.code("src/train_multirun.py  ←  DT, SVM, RF\nsrc/train_mlp.py        ←  MLP TinyML", language="text")


def _wiz_loso(pooled, classical, mlp, cost):
    subjects_short = ["sub-001", "sub-032", "sub-085", "sub-096", "sub-124", "sub-125"]
    n = len(subjects_short)
    matrix = np.zeros((n, n), dtype=int)
    for i in range(n):
        matrix[i, i] = 1
    cell_text = [["TEST" if c == 1 else "train" for c in row] for row in matrix]
    fig = go.Figure(
        data=go.Heatmap(
            z=matrix,
            x=subjects_short,
            y=[f"Fold {i + 1}" for i in range(n)],
            colorscale=[[0, "#2ea27e"], [1, "#d96a4f"]],
            showscale=False,
            text=cell_text,
            texttemplate="%{text}",
            textfont=dict(size=12, color="white"),
            xgap=2, ygap=2,
        )
    )
    fig.update_layout(
        title="Matrice LOSO : à chaque fold, un seul patient est mis en test",
        xaxis_title="Patient (colonne)",
        yaxis_title="Fold (ligne)",
        height=380,
        margin=dict(t=60, b=40, l=40, r=20),
    )
    st.plotly_chart(fig, use_container_width=True, key="wiz_fig_loso")

    st.subheader("Leave-One-Subject-Out (LOSO)")
    st.markdown(
        """
**Principe** : pour chaque patient `i` du jeu, on entraîne le modèle sur les **5 autres patients**, et on **teste sur `i`** que le modèle n'a jamais vu. On répète 6 fois.

C'est la seule méthodologie qui **simule le déploiement réel** d'un wearable médical : quand le bracelet arrive chez un nouveau patient, il doit fonctionner *sans avoir été entraîné sur ses propres crises*.
"""
    )

    fold_df = pd.DataFrame(
        [
            ["Fold 1", "sub-032, sub-085, sub-096, sub-124, sub-125", "sub-001"],
            ["Fold 2", "sub-001, sub-085, sub-096, sub-124, sub-125", "sub-032"],
            ["Fold 3", "sub-001, sub-032, sub-096, sub-124, sub-125", "sub-085"],
            ["Fold 4", "sub-001, sub-032, sub-085, sub-124, sub-125", "sub-096"],
            ["Fold 5", "sub-001, sub-032, sub-085, sub-096, sub-125", "sub-124"],
            ["Fold 6", "sub-001, sub-032, sub-085, sub-096, sub-124", "sub-125"],
        ],
        columns=["Fold", "Patients d'entraînement (5)", "Patient de test (1)"],
    )
    st.dataframe(fold_df, use_container_width=True, hide_index=True)

    st.subheader("Pourquoi pas une k-fold classique ?")
    st.markdown(
        """
La cross-validation 5-fold standard (comme dans le paper Raman) mélange les
**fenêtres de tous les sujets** dans train et test. Conséquence : le modèle voit
en entraînement des fenêtres du sujet sur lequel il sera testé → il apprend la
**signature individuelle** plutôt que la signature **générique** de crise.

Sur un wearable médical, c'est **trompeur** : un nouveau patient n'aura jamais
été vu en entraînement. LOSO élimine ce biais.
"""
    )

    st.subheader("Paramètres figés pour reproductibilité")
    st.code("random_state = 42  # partout\nStratifiedKFold à l'intérieur d'un fold (si k-fold intra-train est utilisé)\nrequirements-pipeline.txt pinned versions", language="text")

    st.subheader("Fichier du repo")
    st.code("src/train_multirun.py  →  boucle LOSO 6 folds × 3 modèles", language="text")


def _wiz_metrics(pooled, classical, mlp, cost):
    rows_metric = []
    for m_key in ["decision_tree", "svm_rbf", "random_forest", "mlp_80_32_16_1"]:
        m = pooled["models"][m_key]
        tp, fn, fp = m["tp"], m["fn"], m["fp"]
        f1_v = (2 * tp) / (2 * tp + fp + fn) if (2 * tp + fp + fn) > 0 else 0.0
        rows_metric.append({
            "Modèle": MODEL_LABELS[m_key],
            "Accuracy (%)": 100 * m["accuracy_pooled"],
            "Recall (%)": 100 * m["recall_pooled"],
            "F1 (%)": 100 * f1_v,
        })
    df_m = pd.DataFrame(rows_metric)
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Accuracy", x=df_m["Modèle"], y=df_m["Accuracy (%)"], marker_color="#7e8a96",
                         text=[f"{v:.1f}" for v in df_m["Accuracy (%)"]], textposition="outside"))
    fig.add_trace(go.Bar(name="Recall (pooled)", x=df_m["Modèle"], y=df_m["Recall (%)"], marker_color="#d96a4f",
                         text=[f"{v:.1f}" for v in df_m["Recall (%)"]], textposition="outside"))
    fig.add_trace(go.Bar(name="F1 (pooled)", x=df_m["Modèle"], y=df_m["F1 (%)"], marker_color="#2ea27e",
                         text=[f"{v:.1f}" for v in df_m["F1 (%)"]], textposition="outside"))
    fig.add_hline(
        y=100 * pooled["trivial_baseline_dummy_classifier"]["accuracy_baseline"],
        line_dash="dash", line_color="#c92a2a", line_width=1.5,
        annotation_text="baseline trivial (predict always negative) = 97,37 %",
        annotation_position="top right",
        annotation_font_color="#c92a2a",
    )
    fig.update_layout(
        title="Le paradoxe d'accuracy : très élevée pour tous, mais c'est le baseline trivial",
        yaxis_title="%",
        barmode="group",
        height=420,
        margin=dict(t=60, b=40, l=40, r=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig, use_container_width=True, key="wiz_fig_metrics")

    st.subheader("Quelles métriques on calcule, et pourquoi celles-là")

    st.markdown(
        """
On rapporte **5 métriques** pour les 4 modèles. Voici les formules canoniques
et leur sens clinique.
"""
    )

    formula_df = pd.DataFrame(
        [
            ["Accuracy", "(TP + TN) / Total", "Fraction de prédictions correctes. ⚠ Trompeuse sous déséquilibre."],
            ["Recall (sensibilité)", "TP / (TP + FN)", "Fraction de crises réelles détectées. **Critère médical principal**."],
            ["Precision", "TP / (TP + FP)", "Fraction des alertes qui sont de vraies crises. Inverse de la nuisance."],
            ["F1", "2·P·R / (P + R)", "Moyenne harmonique. Compromis honnête sous déséquilibre."],
            ["FPR", "FP / (FP + TN)", "Fraction de fenêtres-non-crise faussement signalées. Lié à FAR/h."],
        ],
        columns=["Métrique", "Formule", "Lecture clinique"],
    )
    st.dataframe(formula_df, use_container_width=True, hide_index=True)

    st.subheader("Le piège du déséquilibre : pourquoi l'accuracy est trompeuse")
    rf = pooled["models"]["random_forest"]
    baseline = pooled["trivial_baseline_dummy_classifier"]["accuracy_baseline"]
    rf_acc = (rf["tp"] + rf["tn"]) / rf["n_total"]
    st.markdown(
        f"""
- Prévalence des positives = **{100 * rf['n_positives'] / rf['n_total']:.2f} %**.
- Un **classifieur idiot** qui prédit toujours « pas de crise » atteint **{100 * baseline:.2f} %** d'accuracy.
- Notre RF a **{100 * rf_acc:.2f} %** d'accuracy → **pile le baseline trivial** (±0,01 point). Le modèle est dégénéré.
- C'est pour ça qu'on regarde le **recall** et le **F1**, pas l'accuracy.
"""
    )

    st.subheader("Pourquoi pooled (micro) plutôt que macro ?")
    st.markdown(
        """
- **Macro** : moyenne arithmétique des recalls par patient. Chaque patient pèse 1/6, peu importe le nombre de crises.
- **Pooled (micro)** : `Σ TP / Σ (TP+FN)`. Chaque fenêtre-crise pèse pareil.

Sur nos 6 patients, sub-124 a 345 fenêtres-crise (38 % du total) et sub-085 en a
58 (6 %). Si on prend la macro, sub-085 (avec son 39,7 % de recall) tire la
moyenne vers le haut artificiellement. Pooled, c'est sub-124 qui domine — et
c'est lui qui reflète vraiment la sensibilité globale du système.

> **Correction post-feedback Mme Manel BEN ROMDHANE** : on rapportait initialement le macro (8,9 %). Elle a flaggé l'erreur, on a recalculé en pooled (3,25 %).
"""
    )

    st.subheader("Fichier du repo")
    st.code("src/compute_pooled_metrics.py", language="text")


def _wiz_results(pooled, classical, mlp, cost):
    rf_pf = classical[classical["model"] == "random_forest"].copy()
    rf_pf["recall_pct"] = rf_pf["recall"] * 100
    rf_pooled = pooled["models"]["random_forest"]["recall_pooled"] * 100
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=rf_pf["held_out_subject"],
            y=rf_pf["recall_pct"],
            marker_color="#d96a4f",
            text=[f"{r:.1f} %<br><span style='font-size:10px'>{int(tp)}/{int(np_)}</span>"
                  for r, tp, np_ in zip(rf_pf["recall_pct"], rf_pf["tp"], rf_pf["n_test_pos"])],
            textposition="outside",
        )
    )
    fig.add_hline(
        y=rf_pooled, line_dash="dash", line_color="black", line_width=1.5,
        annotation_text=f"pooled global = {rf_pooled:.2f} %",
        annotation_position="right",
    )
    fig.update_layout(
        title="Random Forest LOSO : recall par patient held-out — sub-085 sauve l'honneur, les 5 autres s'effondrent",
        xaxis_title="Patient en held-out",
        yaxis_title="Recall (%)",
        yaxis_range=[0, max(50.0, rf_pf["recall_pct"].max() * 1.25)],
        height=420,
        margin=dict(t=60, b=40, l=40, r=20),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True, key="wiz_fig_results")

    st.subheader("Résultats LOSO pooled sur les 4 modèles")

    rows = []
    for m_key, m_data in pooled["models"].items():
        tp = m_data["tp"]
        fn = m_data["fn"]
        fp = m_data["fp"]
        tn = m_data["tn"]
        recall = m_data["recall_pooled"]
        precision = m_data["precision_pooled"]
        accuracy = m_data["accuracy_pooled"]
        f1 = (2 * tp) / (2 * tp + fp + fn) if (2 * tp + fp + fn) > 0 else 0.0
        rows.append(
            {
                "Modèle": MODEL_LABELS.get(m_key, m_key),
                "Accuracy": f"{100 * accuracy:.2f} %",
                "Recall": f"{100 * recall:.2f} %",
                "Precision": f"{100 * precision:.2f} %",
                "F1": f"{100 * f1:.2f} %",
                "TP": tp,
                "FN": fn,
                "FP": fp,
            }
        )
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    st.subheader("Détail par patient (Random Forest)")
    rf_per_subject = (
        classical[classical["model"] == "random_forest"][
            ["held_out_subject", "tp", "fn", "fp", "tn", "n_test_pos", "recall"]
        ]
        .copy()
    )
    rf_per_subject["recall_%"] = (rf_per_subject["recall"] * 100).round(2)
    rf_per_subject = rf_per_subject[["held_out_subject", "tp", "fn", "fp", "tn", "n_test_pos", "recall_%"]]
    rf_per_subject.columns = ["Patient", "TP", "FN", "FP", "TN", "n_positives", "Recall (%)"]
    sum_row = pd.DataFrame(
        [["Σ", rf_per_subject["TP"].sum(), rf_per_subject["FN"].sum(),
          rf_per_subject["FP"].sum(), rf_per_subject["TN"].sum(),
          rf_per_subject["n_positives"].sum(),
          round(100 * rf_per_subject["TP"].sum() / rf_per_subject["n_positives"].sum(), 2)]],
        columns=rf_per_subject.columns,
    )
    st.dataframe(pd.concat([rf_per_subject, sum_row], ignore_index=True), use_container_width=True, hide_index=True)

    st.subheader("Le constat scientifique majeur")
    st.markdown(
        """
- Le RF du paper annonce **100 % de recall** sur 30 cas mimés.
- Notre RF en LOSO inter-patient sur patients réels : **3,25 % de recall** (29 / 893).
- Effondrement de facteur ~30. Et **F1 < 10 %** pour les 4 modèles.
- **Conclusion** : la méthodologie du paper ne généralise pas en conditions cliniques. Le 100 % est un artefact du test set artificiellement équilibré.
"""
    )


def _wiz_esp32(pooled, classical, mlp, cost):
    model_order = ["decision_tree", "svm_rbf", "random_forest", "mlp_80_32_16_1"]
    labels = [MODEL_LABELS[k] for k in model_order]
    ram_fp32 = [cost["models"][k]["fp32"]["ram_kb_total"] for k in model_order]
    ram_int8 = [cost["models"][k]["int8"]["ram_kb_total"] for k in model_order]
    fig = go.Figure()
    fig.add_trace(go.Bar(name="FP32", x=labels, y=ram_fp32, marker_color="#d96a4f",
                         text=[f"{v:.1f}" for v in ram_fp32], textposition="outside"))
    fig.add_trace(go.Bar(name="INT8", x=labels, y=ram_int8, marker_color="#2ea27e",
                         text=[f"{v:.1f}" for v in ram_int8], textposition="outside"))
    fig.add_hline(
        y=520, line_dash="dash", line_color="#c92a2a", line_width=2,
        annotation_text="Plafond ESP32 = 520 KB SRAM",
        annotation_position="top right",
        annotation_font_color="#c92a2a",
    )
    fig.update_layout(
        title="Empreinte RAM (échelle log) : RF FP32 déborde, MLP INT8 utilise 1,2 % de la SRAM",
        yaxis_title="RAM totale (KB) — log",
        yaxis_type="log",
        barmode="group",
        height=420,
        margin=dict(t=60, b=40, l=40, r=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig, use_container_width=True, key="wiz_fig_ram")

    st.subheader("Estimation analytique du coût ESP32")
    st.markdown(
        """
On ne déploie pas physiquement sur ESP32 (PoC, pas de hardware), mais on
**estime analytiquement** RAM / latence / énergie à partir du nombre de paramètres,
du nombre de MACs et des spec constructeur (160 MHz, 520 KB SRAM, 70 mW actif).
"""
    )

    rows = []
    for m_key, info in cost["models"].items():
        d_fp = info["fp32"]
        d_q = info["int8"]
        rows.append({
            "Modèle": MODEL_LABELS.get(m_key, m_key),
            "Params": d_fp["params"],
            "RAM FP32": f"{d_fp['ram_kb_total']:.1f} KB ({d_fp['ram_pct_esp32']:.1f}%)",
            "RAM INT8": f"{d_q['ram_kb_total']:.1f} KB ({d_q['ram_pct_esp32']:.1f}%)",
            "Latence INT8": f"{d_q['latency_us']:.1f} µs",
            "Énergie INT8": f"{d_q['energy_uj']:.2f} µJ",
            "INT8 tient ?": "OUI" if d_q["ram_pct_esp32"] <= 100 else "NON",
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    st.subheader("Les 2 enseignements")
    col_a, col_b = st.columns(2)
    with col_a:
        st.error(
            "**Random Forest FP32 = 1 427 KB** sur ESP32 (520 KB SRAM).\n\n"
            "Soit **274 %** de la mémoire physique. **Ne tient pas**, même quantifié INT8 il prend 69 %."
        )
    with col_b:
        st.success(
            "**MLP TinyML INT8 = 6,4 KB** sur ESP32.\n\n"
            "Soit **1,2 %** de la mémoire. **56× plus léger que RF INT8**, latence et énergie comparables."
        )

    st.subheader("Limite assumée")
    st.markdown(
        """
C'est une **estimation analytique**, pas une mesure sur hardware réel. Sources
d'erreur possibles : (1) overhead MicroPython ~100 KB non capturé, (2) latence
MicroPython 5-10× plus lente que C natif, (3) énergie radio (WiFi alerte)
dominant en pratique. À mesurer en perspective.
"""
    )

    st.subheader("Fichier du repo")
    st.code("src/estimate_esp32_cost.py", language="text")


def _wiz_conclusion(pooled, classical, mlp, cost):
    st.subheader("Ce qu'on retient en 4 points")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(
            """
**Contribution scientifique**
- Quantification de l'écart simulation/réalité : 100 % → 3,25 % de recall.
- Identification de 4 contradictions internes dans le paper.
- Premier benchmark public DT/SVM/RF/MLP sur SeizeIT2 LOSO.

**Contribution Edge AI**
- MLP TinyML INT8 viable sur ESP32 (1,2 % SRAM).
- 56× plus léger que RF tout en captant plus de crises en LOSO.
"""
        )
    with col_b:
        st.markdown(
            """
**Limites assumées**
- 6 patients d'entraînement, c'est peu.
- Estimation ESP32 analytique, pas mesurée.
- Pas de mesure FAR/h ni de recall event-level.
- Pipeline reste fidèle au protocole Raman — pas de techniques classe minoritaire.

**Perspectives**
- Extension à 30-50 patients sur les 125 disponibles dans SeizeIT2.
- Class weighting, focal loss, SMOTE, ou approche anomalie.
- Recall event-level (1 fenêtre détectée sur 30 = alerte clinique).
- Mesure hardware réelle sur ESP32-S3 + LSM6DSO.
"""
        )

    st.subheader("Reproductibilité")
    st.markdown(
        """
- **Repo public** : [github.com/akiroussama/iot-edge-ai-seizure-detection](https://github.com/akiroussama/iot-edge-ai-seizure-detection)
- **Données brutes** : OpenNeuro `ds005873` (téléchargement S3 public).
- **Versions pinées** : `requirements-pipeline.txt`.
- **Random state fixé** : 42 partout.
- **5 scripts à lancer en séquence** : `load_data.py` → `preprocess.py` → `pipeline_multirun.py` → `train_multirun.py` (et `train_mlp.py`) → `compute_pooled_metrics.py` → `estimate_esp32_cost.py`.

Le pipeline complet tourne en ~10 min sur une machine standard une fois les
données téléchargées.
"""
    )

    st.success(
        "**Bravo, vous avez parcouru le pipeline complet.** Onglets 1-4 disponibles pour "
        "explorer la donnée brute (signal, model arena, coût ESP32, scatter Pareto)."
    )


# ------------------------------------------------------------- legacy tab 5 (paper vs reality, kept dormant)
def tab_paper_vs_reality(pooled: dict):
    st.header("5 — Paper vs Réalité : la promesse vs le déploiement")
    st.markdown(
        """
Deux protocoles, **un seul modèle** : le Random Forest, mêmes poids, mêmes
features. À gauche, le test set du paper Raman (sujets sains qui miment,
prévalence artificielle 50 %). À droite, notre LOSO sur SeizeIT2 (patients
épileptiques réels, prévalence clinique 2,63 %). On échantillonne 30 fenêtres
de crise sur chaque protocole et on regarde comment le RF s'en sort.

Cliquez sur **Lancer la comparaison** pour voir les deux tableaux se remplir
côte à côte. *Spoiler* : c'est le même modèle, mais l'écart de sensibilité
dépasse 30×.
"""
    )

    rf_pool = pooled["models"]["random_forest"]
    real_recall_full = rf_pool["recall_pooled"]
    real_n_pos_full = rf_pool["n_positives"]
    real_tp_full = rf_pool["tp"]

    N_SHOW = 30
    real_tp_show = max(1, round(real_recall_full * N_SHOW))

    rng = np.random.default_rng(2026)
    real_tp_positions = set(rng.choice(N_SHOW, size=real_tp_show, replace=False).tolist())

    speed = st.select_slider(
        "Vitesse",
        options=["Lent", "Normal", "Rapide", "Instantané"],
        value="Normal",
        key="pvr_speed",
    )
    sleep_per_step = {"Lent": 0.35, "Normal": 0.18, "Rapide": 0.07, "Instantané": 0.0}[speed]

    play = st.button("Lancer la comparaison", type="primary", key="pvr_play")

    left_col, right_col = st.columns(2, gap="large")

    with left_col:
        st.markdown("### Protocole paper (Raman 2025)")
        st.caption("Sujets sains qui miment · test 30/60 · **prévalence 50 %**")
        paper_grid = st.empty()
        paper_metric = st.empty()

    with right_col:
        st.markdown("### Déploiement réel (SeizeIT2 LOSO)")
        st.caption(f"Patients épileptiques · test pooled 893/33 925 · **prévalence 2,63 %**")
        real_grid = st.empty()
        real_metric = st.empty()

    def grid_html(predictions: list[bool | None]) -> str:
        cells_html = []
        for p in predictions:
            if p is True:
                cells_html.append(
                    "<div style='aspect-ratio:1;display:flex;align-items:center;"
                    "justify-content:center;background:#2ea27e;color:white;"
                    "border-radius:8px;font-size:28px;font-weight:800;'>&#10003;</div>"
                )
            elif p is False:
                cells_html.append(
                    "<div style='aspect-ratio:1;display:flex;align-items:center;"
                    "justify-content:center;background:#d96a4f;color:white;"
                    "border-radius:8px;font-size:28px;font-weight:800;'>&#10007;</div>"
                )
            else:
                cells_html.append(
                    "<div style='aspect-ratio:1;display:flex;align-items:center;"
                    "justify-content:center;background:#eef2f5;color:#bbb;"
                    "border-radius:8px;font-size:22px;font-weight:600;'>&middot;</div>"
                )
        return (
            "<div style='display:grid;grid-template-columns:repeat(6, 1fr);gap:6px;'>"
            + "".join(cells_html) + "</div>"
        )

    def metric_html(caught: int, done: int, color: str) -> str:
        pct = (100.0 * caught / done) if done > 0 else 0.0
        return (
            f"<div style='margin-top:18px;text-align:center;'>"
            f"<div style='font-size:42px;font-weight:800;color:{color};line-height:1;'>"
            f"{caught} / {done}</div>"
            f"<div style='font-size:18px;color:#555;margin-top:4px;'>"
            f"recall = {pct:.1f} %</div></div>"
        )

    def render(step: int):
        paper_preds = [True if i < step else None for i in range(N_SHOW)]
        real_preds = [
            (i in real_tp_positions) if i < step else None for i in range(N_SHOW)
        ]
        paper_grid.markdown(grid_html(paper_preds), unsafe_allow_html=True)
        real_grid.markdown(grid_html(real_preds), unsafe_allow_html=True)

        paper_caught = step
        real_caught = sum(1 for i in range(step) if i in real_tp_positions)
        paper_metric.markdown(
            metric_html(paper_caught, step, "#2ea27e"), unsafe_allow_html=True
        )
        real_metric.markdown(
            metric_html(real_caught, step, "#d96a4f"), unsafe_allow_html=True
        )

    if play:
        for step in range(N_SHOW + 1):
            render(step)
            if sleep_per_step:
                time.sleep(sleep_per_step)
    else:
        render(N_SHOW)

    st.markdown("---")
    st.markdown(
        """
<div style="background: linear-gradient(135deg, #1c2942 0%, #2c1747 100%);
            color: white; padding: 28px 32px; border-radius: 14px;
            text-align: center; margin-top: 8px;">
  <div style="font-size: 26px; font-weight: 800; letter-spacing: 0.04em;">
    MÊME MODÈLE &nbsp;·&nbsp; MÊMES POIDS &nbsp;·&nbsp; ÉCART &asymp; 30&times;
  </div>
  <div style="font-size: 17px; font-weight: 400; margin-top: 14px;
              line-height: 1.5; max-width: 720px; margin-left:auto;margin-right:auto;
              opacity: 0.92;">
    La promesse d'un papier ne survit pas toujours à son d&eacute;ploiement.<br>
    Le 100 % recall de Raman tient sur 30 fen&ecirc;tres mim&eacute;es &agrave; pr&eacute;valence 50 %.<br>
    Sur de vrais patients en LOSO &agrave; pr&eacute;valence 2,63 %, le m&ecirc;me Random Forest
    d&eacute;tecte 29 fen&ecirc;tres-crise sur 893.
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    with st.expander("Comment on calibre l'écart ?"):
        st.markdown(
            f"""
- **Côté paper** : 100 % de recall annoncé sur 30 fenêtres-crise mimées
  ⇒ par construction, RF détecte 30 sur 30 (tous les carrés verts).
- **Côté réel** : recall pooled mesuré = {real_recall_full:.4f}
  (= {real_tp_full} TP / {real_n_pos_full} fenêtres-crise sur les 6 patients LOSO).
- **Échantillonnage** : on tire 30 fenêtres au hasard parmi les 893 réelles
  (seed = 2026 pour reproductibilité visuelle). Espérance du nombre de TP
  dans l'échantillon = 30 × {real_recall_full:.4f} = {30 * real_recall_full:.2f},
  arrondi à **{real_tp_show}**. C'est exactement ce que l'animation montre.
- **Écart**: 100 % / {real_recall_full*100:.2f} % ≈ **{1 / max(real_recall_full, 1e-6):.0f}×**.
  Le facteur 30 du bandeau est l'arrondi rond de cet écart.
"""
        )


# ---------------------------------------------------------------------- main
def main():
    render_sidebar()

    st.title("SeizureGuard Live")
    st.caption(
        "Reproduction du paper Raman 2025 sur SeizeIT2 + Edge AI TinyML — "
        "Étudiant 5, Groupe 2, IoT Devices SUP'COM 2026"
    )

    pooled = load_pooled()
    cost = load_cost()
    classical, mlp = load_per_fold()

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "1 — Signal & contexte",
            "2 — Model arena (live)",
            "3 — ESP32 cost dashboard",
            "4 — Trade-off explorer",
            "5 — Pipeline complet (wizard A → Z)",
        ]
    )

    with tab1:
        tab_signal(pooled, classical)
    with tab2:
        tab_arena(classical, mlp, pooled)
    with tab3:
        tab_cost(cost)
    with tab4:
        tab_pareto(pooled, cost)
    with tab5:
        tab_wizard(pooled, classical, mlp, cost)


if __name__ == "__main__":
    main()
