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
        bars.plotly_chart(bar_fig, use_container_width=True)

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

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "1 — Signal & contexte",
            "2 — Model arena (live)",
            "3 — ESP32 cost dashboard",
            "4 — Trade-off explorer",
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


if __name__ == "__main__":
    main()
