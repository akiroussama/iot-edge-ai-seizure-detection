"""SeizureGuard Portfolio — site Streamlit global pour le projet IoT / Edge AI.

Objectif
--------
Ce fichier transforme le dépôt GitHub en mini-site web de soutenance :
présentation, rapport, résultats reproductibles, dashboard ESP32, trace IA
et lancement Google Colab.

Lancement local :
    streamlit run streamlit_app.py

Lancement Colab :
    voir notebooks/launch_streamlit_colab.ipynb

Le code est volontairement robuste : si certains fichiers ne sont pas encore
présents dans le dépôt, l'application affiche un message clair et continue avec
les valeurs de synthèse du README.
"""

from __future__ import annotations

import base64
import json
import math
import re
import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ---------------------------------------------------------------------------
# Configuration générale
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
ESP32_SRAM_KB = 520.0
REPO_URL = "https://github.com/akiroussama/iot-edge-ai-seizure-detection"
COLAB_URL = (
    "https://colab.research.google.com/github/akiroussama/"
    "iot-edge-ai-seizure-detection/blob/main/notebooks/launch_streamlit_colab.ipynb"
)

MODEL_LABELS = {
    "decision_tree": "Decision Tree",
    "svm_rbf": "SVM RBF",
    "random_forest": "Random Forest",
    "mlp_80_32_16_1": "MLP TinyML",
    "MLP TinyML": "MLP TinyML",
    "Random Forest": "Random Forest",
    "Decision Tree": "Decision Tree",
    "SVM RBF": "SVM RBF",
}

FALLBACK_RESULTS = pd.DataFrame(
    [
        {
            "model_key": "decision_tree",
            "Modèle": "Decision Tree",
            "Régime": "LOSO réel",
            "Recall pooled (%)": 11.0,
            "TP / N_pos": "98 / 893",
            "Accuracy pooled (%)": 94.5,
            "RAM ESP32 INT8 (KB)": np.nan,
            "Latence (µs)": np.nan,
            "Note": "meilleur recall, mais moins central pour Edge AI",
        },
        {
            "model_key": "svm_rbf",
            "Modèle": "SVM RBF",
            "Régime": "LOSO réel",
            "Recall pooled (%)": 6.5,
            "TP / N_pos": "58 / 893",
            "Accuracy pooled (%)": 96.2,
            "RAM ESP32 INT8 (KB)": np.nan,
            "Latence (µs)": np.nan,
            "Note": "coût d'inférence moins favorable sur MCU",
        },
        {
            "model_key": "random_forest",
            "Modèle": "Random Forest",
            "Régime": "LOSO réel",
            "Recall pooled (%)": 3.3,
            "TP / N_pos": "29 / 893",
            "Accuracy pooled (%)": 97.4,
            "RAM ESP32 INT8 (KB)": 357.0,
            "Latence (µs)": 18.5,
            "Note": "proche du baseline toujours négatif",
        },
        {
            "model_key": "mlp_80_32_16_1",
            "Modèle": "MLP TinyML",
            "Régime": "LOSO réel",
            "Recall pooled (%)": 8.7,
            "TP / N_pos": "78 / 893",
            "Accuracy pooled (%)": 91.6,
            "RAM ESP32 INT8 (KB)": 6.4,
            "Latence (µs)": 19.3,
            "Note": "56× plus petit que le RF et recall supérieur",
        },
    ]
)

FALLBACK_COST = pd.DataFrame(
    [
        {
            "model_key": "decision_tree",
            "Modèle": "Decision Tree",
            "Quantification": "INT8",
            "RAM (KB)": 24.0,
            "% SRAM ESP32": 4.6,
            "Latence (µs)": 5.0,
            "Énergie (µJ)": 0.35,
            "Déployable": "Oui",
        },
        {
            "model_key": "svm_rbf",
            "Modèle": "SVM RBF",
            "Quantification": "INT8",
            "RAM (KB)": 128.0,
            "% SRAM ESP32": 24.6,
            "Latence (µs)": 80.0,
            "Énergie (µJ)": 5.60,
            "Déployable": "Oui, mais marge plus faible",
        },
        {
            "model_key": "random_forest",
            "Modèle": "Random Forest",
            "Quantification": "INT8",
            "RAM (KB)": 357.0,
            "% SRAM ESP32": 68.7,
            "Latence (µs)": 18.5,
            "Énergie (µJ)": 1.30,
            "Déployable": "Limite",
        },
        {
            "model_key": "mlp_80_32_16_1",
            "Modèle": "MLP TinyML",
            "Quantification": "INT8",
            "RAM (KB)": 6.4,
            "% SRAM ESP32": 1.2,
            "Latence (µs)": 19.3,
            "Énergie (µJ)": 1.35,
            "Déployable": "Oui",
        },
    ]
)

PRESENTATION_CANDIDATES = [
    ROOT / "assets" / "presentation_iot.pdf",
    ROOT / "assets" / "presentation_iot_uploaded.pdf",
    ROOT / "presentation" / "presentation_iot.pdf",
    ROOT / "presentation" / "presentation.pdf",
    ROOT / "presentation" / "slides.pdf",
    ROOT / "presentaitonIot.pdf",
    ROOT / "presentationIot.pdf",
]

REPORT_CANDIDATES = [
    ROOT / "assets" / "report_iot.pdf",
    ROOT / "docs" / "report_iot.pdf",
    ROOT / "report_iot.pdf",
    ROOT / "presentation" / "report_iot.pdf",
]

TRACE_CANDIDATES = [
    ROOT / "presentation" / "trace_ia.md",
    ROOT / "trace_ia.md",
    ROOT / "docs" / "trace_ia.md",
    ROOT / "assets" / "trace_ia.md",
]

REPRODUCTION_CANDIDATES = [
    ROOT / "docs" / "REPRODUCTION.md",
    ROOT / "REPRODUCTION.md",
]

# ---------------------------------------------------------------------------
# Page config + style
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="SeizureGuard — IoMT, épilepsie et Edge AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
:root {
    --sg-blue: #1f4e79;
    --sg-green: #1f9d75;
    --sg-red: #c2410c;
    --sg-muted: #64748b;
    --sg-card: #ffffff;
    --sg-bg: #f8fafc;
}
.block-container { padding-top: 1.2rem; padding-bottom: 3rem; }
.sg-hero {
    padding: 1.35rem 1.45rem;
    border-radius: 18px;
    background: linear-gradient(135deg, #e0f2fe 0%, #eef2ff 55%, #f8fafc 100%);
    border: 1px solid #dbeafe;
    margin-bottom: 1rem;
}
.sg-hero h1 { margin: 0 0 .25rem 0; color: #0f172a; font-size: 2.2rem; }
.sg-hero p { margin: .2rem 0 0 0; color: #334155; font-size: 1.02rem; }
.sg-card {
    background: #ffffff;
    padding: 1rem 1rem;
    border-radius: 14px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 1px 2px rgba(15, 23, 42, .04);
    min-height: 128px;
}
.sg-card h3 { margin: 0 0 .35rem 0; font-size: 1.02rem; color: #0f172a; }
.sg-card p { color: #475569; margin: 0; font-size: .92rem; line-height: 1.45; }
.sg-badge {
    display:inline-block; padding:.18rem .55rem; border-radius:999px;
    background:#e0f2fe; color:#075985; border:1px solid #bae6fd;
    font-size:.78rem; font-weight:600; margin-right:.35rem;
}
.sg-warning {
    border-left: 4px solid #f97316; background: #fff7ed; padding: .8rem 1rem;
    border-radius: 8px; color: #7c2d12;
}
.sg-ok {
    border-left: 4px solid #10b981; background: #ecfdf5; padding: .8rem 1rem;
    border-radius: 8px; color: #064e3b;
}
.sg-code-title { font-weight: 700; color: #334155; margin-bottom: .25rem; }
.small-muted { color: #64748b; font-size: .86rem; }
</style>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Helpers fichiers / données
# ---------------------------------------------------------------------------

def first_existing(candidates: Iterable[Path]) -> Path | None:
    for path in candidates:
        if path.exists():
            return path
    return None


@st.cache_data(show_spinner=False)
def read_text_cached(path_str: str) -> str:
    path = Path(path_str)
    return path.read_text(encoding="utf-8", errors="replace")


@st.cache_data(show_spinner=False)
def read_json_cached(path_str: str) -> dict:
    return json.loads(Path(path_str).read_text(encoding="utf-8"))


@st.cache_data(show_spinner=False)
def read_csv_cached(path_str: str) -> pd.DataFrame:
    return pd.read_csv(path_str)


def safe_pct(num: float, den: float) -> float:
    return 0.0 if den == 0 else 100.0 * float(num) / float(den)


def normalize_model_label(model_key: str) -> str:
    return MODEL_LABELS.get(model_key, model_key.replace("_", " ").title())


@st.cache_data(show_spinner=False)
def load_results_summary() -> pd.DataFrame:
    """Load pooled model metrics from CSV/JSON when possible.

    Priority:
    1. results/multirun_loso.csv + results/mlp_loso.csv, because they allow
       exact pooled recall via ΣTP / (ΣTP + ΣFN).
    2. Fallback values from the README.
    """
    classical_path = RESULTS / "multirun_loso.csv"
    mlp_path = RESULTS / "mlp_loso.csv"
    if classical_path.exists() and mlp_path.exists():
        rows: list[dict] = []
        classical = pd.read_csv(classical_path)
        mlp = pd.read_csv(mlp_path)

        for model_key, group in classical.groupby("model"):
            tp = int(group["tp"].sum()) if "tp" in group else 0
            fp = int(group["fp"].sum()) if "fp" in group else 0
            fn = int(group["fn"].sum()) if "fn" in group else 0
            if "tn" in group:
                tn = int(group["tn"].sum())
            elif "n_test" in group:
                tn = int(group["n_test"].sum()) - tp - fp - fn
            else:
                tn = 0
            n_total = tp + fp + fn + tn
            n_pos = tp + fn
            rows.append(
                {
                    "model_key": model_key,
                    "Modèle": normalize_model_label(model_key),
                    "Régime": "LOSO réel",
                    "Recall pooled (%)": safe_pct(tp, n_pos),
                    "TP / N_pos": f"{tp} / {n_pos}",
                    "Accuracy pooled (%)": safe_pct(tp + tn, n_total),
                    "RAM ESP32 INT8 (KB)": np.nan,
                    "Latence (µs)": np.nan,
                    "Note": "calculé depuis CSV",
                }
            )

        # MLP CSV: sometimes one row per fold without a model column.
        if len(mlp):
            tp = int(mlp["tp"].sum()) if "tp" in mlp else 0
            fp = int(mlp["fp"].sum()) if "fp" in mlp else 0
            fn = int(mlp["fn"].sum()) if "fn" in mlp else 0
            if "tn" in mlp:
                tn = int(mlp["tn"].sum())
            elif "n_test" in mlp:
                tn = int(mlp["n_test"].sum()) - tp - fp - fn
            else:
                tn = 0
            n_total = tp + fp + fn + tn
            n_pos = tp + fn
            rows.append(
                {
                    "model_key": "mlp_80_32_16_1",
                    "Modèle": "MLP TinyML",
                    "Régime": "LOSO réel",
                    "Recall pooled (%)": safe_pct(tp, n_pos),
                    "TP / N_pos": f"{tp} / {n_pos}",
                    "Accuracy pooled (%)": safe_pct(tp + tn, n_total),
                    "RAM ESP32 INT8 (KB)": 6.4,
                    "Latence (µs)": 19.3,
                    "Note": "calculé depuis CSV",
                }
            )

        df = pd.DataFrame(rows)
        if not df.empty:
            # Complete RAM/latency if the cost JSON is available.
            cost = load_cost_summary()
            for _, cost_row in cost.iterrows():
                mask = (df["Modèle"] == cost_row["Modèle"]) & (cost_row["Quantification"] == "INT8")
                df.loc[mask, "RAM ESP32 INT8 (KB)"] = cost_row["RAM (KB)"]
                df.loc[mask, "Latence (µs)"] = cost_row["Latence (µs)"]
            order = ["Decision Tree", "SVM RBF", "Random Forest", "MLP TinyML"]
            df["_order"] = df["Modèle"].apply(lambda x: order.index(x) if x in order else 99)
            return df.sort_values("_order").drop(columns="_order")

    return FALLBACK_RESULTS.copy()


@st.cache_data(show_spinner=False)
def load_cost_summary() -> pd.DataFrame:
    cost_path = RESULTS / "esp32_cost_estimate.json"
    if cost_path.exists():
        try:
            cost = json.loads(cost_path.read_text(encoding="utf-8"))
            rows = []
            for model_key, info in cost.get("models", {}).items():
                for q_key, q_info in info.items():
                    if not isinstance(q_info, dict):
                        continue
                    rows.append(
                        {
                            "model_key": model_key,
                            "Modèle": normalize_model_label(model_key),
                            "Quantification": q_key.upper(),
                            "RAM (KB)": float(q_info.get("ram_kb_total", np.nan)),
                            "% SRAM ESP32": float(q_info.get("ram_pct_esp32", np.nan)),
                            "Latence (µs)": float(q_info.get("latency_us", np.nan)),
                            "Énergie (µJ)": float(q_info.get("energy_uj", np.nan)),
                            "Déployable": "Oui" if float(q_info.get("ram_pct_esp32", 9999)) <= 100 else "Non",
                        }
                    )
            if rows:
                df = pd.DataFrame(rows)
                order = ["Decision Tree", "SVM RBF", "Random Forest", "MLP TinyML"]
                df["_order"] = df["Modèle"].apply(lambda x: order.index(x) if x in order else 99)
                return df.sort_values(["_order", "Quantification"]).drop(columns="_order")
        except Exception:
            pass
    return FALLBACK_COST.copy()


@st.cache_data(show_spinner=False)
def load_trace_text() -> tuple[str, Path | None]:
    trace = first_existing(TRACE_CANDIDATES)
    if trace:
        return trace.read_text(encoding="utf-8", errors="replace"), trace
    return "", None


@st.cache_data(show_spinner=False)
def load_reproduction_text() -> tuple[str, Path | None]:
    repro = first_existing(REPRODUCTION_CANDIDATES)
    if repro:
        return repro.read_text(encoding="utf-8", errors="replace"), repro
    return "", None


def embed_pdf(path: Path, height: int = 760) -> None:
    """Embed a local PDF with a download button."""
    data = path.read_bytes()
    b64 = base64.b64encode(data).decode("utf-8")
    st.download_button(
        label=f"Télécharger {path.name}",
        data=data,
        file_name=path.name,
        mime="application/pdf",
    )
    st.components.v1.html(
        f"""
        <iframe
            src="data:application/pdf;base64,{b64}#toolbar=1&navpanes=0"
            width="100%"
            height="{height}px"
            style="border: 1px solid #e2e8f0; border-radius: 12px;"
        ></iframe>
        """,
        height=height + 20,
    )


def metric_card(title: str, value: str, caption: str = "") -> None:
    st.markdown(
        f"""
<div class="sg-card">
  <h3>{title}</h3>
  <p style="font-size:1.65rem;font-weight:800;color:#0f172a;margin:.15rem 0;">{value}</p>
  <p>{caption}</p>
</div>
""",
        unsafe_allow_html=True,
    )


def code_block(title: str, code: str, language: str = "bash") -> None:
    st.markdown(f"<div class='sg-code-title'>{title}</div>", unsafe_allow_html=True)
    st.code(textwrap.dedent(code).strip(), language=language)


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

def render_sidebar() -> None:
    st.sidebar.title("🧠 SeizureGuard")
    st.sidebar.caption("Portfolio IoT / IoMT / Edge AI — Groupe 2")
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        """
**Paper analysé**  
Raman & Velmurugan 2025  
*IoMT wearable device for neurological disorders*

**Dataset de réplication**  
SeizeIT2 — patients réels, protocole LOSO

**Message clé**  
La simulation parfaite du paper ne généralise pas directement sur patients réels.
"""
    )
    st.sidebar.markdown("---")
    st.sidebar.link_button("GitHub repository", REPO_URL)
    st.sidebar.link_button("Ouvrir le Colab", COLAB_URL)
    st.sidebar.markdown("---")
    st.sidebar.caption(
        "Astuce : pour Streamlit Cloud, le fichier principal doit rester nommé "
        "`streamlit_app.py`."
    )


# ---------------------------------------------------------------------------
# Onglets
# ---------------------------------------------------------------------------

def render_home(results: pd.DataFrame) -> None:
    st.markdown(
        """
<div class="sg-hero">
  <span class="sg-badge">IoMT</span>
  <span class="sg-badge">Épilepsie</span>
  <span class="sg-badge">SeizeIT2</span>
  <span class="sg-badge">TinyML / ESP32</span>
  <h1>Site web global du projet IoT — Groupe 2</h1>
  <p>Un point d'entrée unique pour la présentation, la réplication, les résultats Edge AI, la trace IA générative et le lancement Google Colab.</p>
</div>
""",
        unsafe_allow_html=True,
    )

    rf = results[results["Modèle"] == "Random Forest"]
    mlp = results[results["Modèle"] == "MLP TinyML"]
    rf_recall = float(rf["Recall pooled (%)"].iloc[0]) if len(rf) else 3.3
    mlp_recall = float(mlp["Recall pooled (%)"].iloc[0]) if len(mlp) else 8.7
    mlp_ram = float(mlp["RAM ESP32 INT8 (KB)"].iloc[0]) if len(mlp) and pd.notna(mlp["RAM ESP32 INT8 (KB)"].iloc[0]) else 6.4

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Fenêtres test", "33 925", "LOSO sur 6 patients SeizeIT2")
    with c2:
        metric_card("Fenêtres crise", "893", "positives cliniques utilisées pour le recall")
    with c3:
        metric_card("RF recall pooled", f"{rf_recall:.1f} %", "le RF se rapproche du baseline toujours négatif")
    with c4:
        metric_card("MLP RAM INT8", f"{mlp_ram:.1f} KB", "≈ 1,2 % de la SRAM ESP32")

    st.markdown("### Ce que le site regroupe")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            """
<div class="sg-card">
<h3>1. Livrables</h3>
<p>Présentation, rapport, dépôt GitHub, README et guide de reproduction.</p>
</div>
""",
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            """
<div class="sg-card">
<h3>2. Résultats reproductibles</h3>
<p>Comparaison RF, SVM, DT et MLP TinyML avec recall pooled, accuracy et coût Edge.</p>
</div>
""",
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            """
<div class="sg-card">
<h3>3. Trace IA</h3>
<p>Documentation des outils IA, hallucinations détectées, corrections et décisions humaines.</p>
</div>
""",
            unsafe_allow_html=True,
        )

    st.markdown("### Narratif scientifique conseillé")
    st.markdown(
        """
<div class="sg-ok">
<strong>Formulation courte :</strong> le paper annonce des performances parfaites en simulation, mais la validation externe sur des patients réels montre un fort problème de généralisation. Le MLP TinyML ne résout pas le problème clinique, mais il améliore le compromis Edge AI : beaucoup moins de mémoire que le Random Forest et un recall pooled supérieur.
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown("### Plan de présentation conforme au brief")
    st.dataframe(
        pd.DataFrame(
            [
                ["Étudiant 1", "Contexte, problématique, conclusion et compromis"],
                ["Étudiant 2", "État de l'art : méthodes classiques, IA, Edge AI"],
                ["Étudiant 3", "Conception du paper : architecture, données, traitement"],
                ["Étudiant 4", "Résultats du paper et analyse critique"],
                ["Étudiant 5", "Réplication, SeizeIT2, amélioration TinyML, site/Colab"],
            ],
            columns=["Responsable", "Contenu"],
        ),
        use_container_width=True,
        hide_index=True,
    )


def render_deliverables() -> None:
    st.header("📄 Livrables et ressources")
    st.markdown(
        "Cette page sert de portail : elle donne accès aux documents, au repo, au README, au guide de reproduction et aux exports PDF."
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.link_button("Repository GitHub", REPO_URL, use_container_width=True)
    with col2:
        st.link_button("Notebook Google Colab", COLAB_URL, use_container_width=True)
    with col3:
        st.link_button("DOI du paper de référence", "https://doi.org/10.3390/engproc2025106013", use_container_width=True)

    st.markdown("---")
    pres_path = first_existing(PRESENTATION_CANDIDATES)
    report_path = first_existing(REPORT_CANDIDATES)

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Présentation")
        if pres_path:
            st.success(f"Fichier trouvé : `{pres_path.relative_to(ROOT) if pres_path.is_relative_to(ROOT) else pres_path}`")
            if "uploaded" in pres_path.name or "presentaiton" in pres_path.name.lower():
                st.warning(
                    "Ce fichier semble être la version uploadée. Vérifiez l'orientation paysage et le rognage avant de l'utiliser comme version finale."
                )
            if st.checkbox("Afficher la présentation PDF", value=False):
                embed_pdf(pres_path, height=720)
        else:
            st.info(
                "Aucun PDF de présentation trouvé. Placez la version finale dans `assets/presentation_iot.pdf` "
                "ou `presentation/presentation_iot.pdf`."
            )

    with c2:
        st.subheader("Rapport / document IA")
        if report_path:
            st.success(f"Fichier trouvé : `{report_path.relative_to(ROOT) if report_path.is_relative_to(ROOT) else report_path}`")
            if st.checkbox("Afficher le rapport PDF", value=False):
                embed_pdf(report_path, height=720)
        else:
            st.info(
                "Aucun rapport PDF trouvé. Placez-le dans `assets/report_iot.pdf` ou `docs/report_iot.pdf`."
            )

    st.markdown("---")
    st.subheader("Guide de reproduction")
    repro_text, repro_path = load_reproduction_text()
    if repro_text:
        st.caption(f"Source : `{repro_path.relative_to(ROOT) if repro_path and repro_path.is_relative_to(ROOT) else repro_path}`")
        with st.expander("Afficher docs/REPRODUCTION.md", expanded=False):
            st.markdown(repro_text)
    else:
        st.info("Le guide `docs/REPRODUCTION.md` n'est pas encore présent dans cette copie locale.")

    st.subheader("Commandes essentielles")
    code_block(
        "Lancement local du site",
        """
        pip install -r requirements.txt
        streamlit run streamlit_app.py
        """,
    )
    code_block(
        "Pipeline complet, uniquement si les données SeizeIT2 sont déjà placées dans data/",
        """
        pip install -r requirements-pipeline.txt
        python src/pipeline_multirun.py
        python src/train_multirun.py
        python src/train_mlp.py
        python src/estimate_esp32_cost.py
        python src/make_figures.py
        """,
    )


def render_results(results: pd.DataFrame) -> None:
    st.header("📊 Résultats de réplication et analyse critique")
    st.markdown(
        "La métrique principale est le **recall pooled** : `ΣTP / (ΣTP + ΣFN)` sur les 6 folds LOSO. "
        "Cette agrégation répond à la question clinique : parmi toutes les fenêtres de crise réelles, combien sont détectées ?"
    )

    show_cols = [
        "Modèle",
        "Régime",
        "Recall pooled (%)",
        "TP / N_pos",
        "Accuracy pooled (%)",
        "RAM ESP32 INT8 (KB)",
        "Latence (µs)",
        "Note",
    ]
    st.dataframe(
        results[show_cols].style.format(
            {
                "Recall pooled (%)": "{:.2f}",
                "Accuracy pooled (%)": "{:.2f}",
                "RAM ESP32 INT8 (KB)": "{:.2f}",
                "Latence (µs)": "{:.2f}",
            },
            na_rep="—",
        ),
        use_container_width=True,
        hide_index=True,
    )

    c1, c2 = st.columns([1.2, 1.0])
    with c1:
        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=results["Modèle"],
                y=results["Recall pooled (%)"],
                text=[f"{v:.1f} %" for v in results["Recall pooled (%)"]],
                textposition="outside",
                name="Recall pooled",
            )
        )
        fig.update_layout(
            height=390,
            title="Recall pooled LOSO — patients réels",
            yaxis_title="Recall (%)",
            xaxis_title="",
            margin=dict(l=20, r=20, t=55, b=40),
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=results["Modèle"],
                y=results["Accuracy pooled (%)"],
                text=[f"{v:.1f} %" for v in results["Accuracy pooled (%)"]],
                textposition="outside",
                name="Accuracy pooled",
            )
        )
        fig.add_hline(
            y=97.37,
            line_dash="dash",
            annotation_text="baseline toujours négatif ≈ 97,37 %",
            annotation_position="top left",
        )
        fig.update_layout(
            height=390,
            title="Accuracy : attention au baseline trivial",
            yaxis_title="Accuracy (%)",
            yaxis_range=[85, 101],
            xaxis_title="",
            margin=dict(l=20, r=20, t=55, b=40),
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Lecture critique")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            """
<div class="sg-warning">
<strong>Pourquoi l'accuracy est trompeuse ?</strong><br>
La prévalence des fenêtres de crise est faible. Un modèle qui prédit toujours « pas de crise » atteint déjà environ 97,37 % d'accuracy. Le recall est donc beaucoup plus informatif pour la détection de crise.
</div>
""",
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            """
<div class="sg-ok">
<strong>Conclusion expérimentale :</strong><br>
Le MLP TinyML reste cliniquement insuffisant, mais il donne un meilleur compromis embarqué que le Random Forest : mémoire très réduite, rappel supérieur, latence comparable.
</div>
""",
            unsafe_allow_html=True,
        )

    with st.expander("Contradictions / points de reproductibilité à mentionner sobrement"):
        st.markdown(
            """
- Incohérence de terminologie capteur dans le paper : à présenter comme un problème de reproductibilité, pas comme une attaque.
- FPR contradictoire entre abstract et tableau : à montrer avec les citations exactes si vous l'affichez en slide.
- Dataset de simulation très petit : les 100 % annoncés ne doivent pas être comparés directement à une validation externe LOSO.
- Variables temps réel, consommation et mémoire : les claims de précision doivent être relus avec les contraintes Edge AI.
"""
        )


def render_edge_ai(results: pd.DataFrame, cost: pd.DataFrame) -> None:
    st.header("🧠 Dashboard Edge AI / ESP32")
    st.markdown(
        "Cette page regroupe les contraintes d'implémentation embarquée : SRAM, latence, énergie et compromis performance/ressources."
    )

    st.subheader("Coût mémoire, latence et énergie")
    st.dataframe(
        cost.style.format(
            {
                "RAM (KB)": "{:.2f}",
                "% SRAM ESP32": "{:.2f}",
                "Latence (µs)": "{:.2f}",
                "Énergie (µJ)": "{:.3f}",
            },
            na_rep="—",
        ),
        use_container_width=True,
        hide_index=True,
    )

    int8_cost = cost[cost["Quantification"].astype(str).str.upper() == "INT8"].copy()
    if not int8_cost.empty:
        c1, c2 = st.columns([1.1, 1.0])
        with c1:
            fig = go.Figure()
            fig.add_trace(
                go.Bar(
                    x=int8_cost["Modèle"],
                    y=int8_cost["RAM (KB)"],
                    text=[f"{v:.1f} KB" for v in int8_cost["RAM (KB)"]],
                    textposition="outside",
                )
            )
            fig.add_hline(
                y=ESP32_SRAM_KB,
                line_dash="dash",
                annotation_text="SRAM ESP32 = 520 KB",
                annotation_position="top left",
            )
            fig.update_layout(
                height=390,
                title="RAM estimée en INT8",
                yaxis_title="KB",
                xaxis_title="",
                margin=dict(l=20, r=20, t=55, b=40),
            )
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            merged = results.merge(int8_cost[["Modèle", "RAM (KB)"]], on="Modèle", how="left")
            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=merged["RAM (KB)"],
                    y=merged["Recall pooled (%)"],
                    mode="markers+text",
                    text=merged["Modèle"],
                    textposition="top center",
                    marker=dict(size=18),
                    hovertemplate="%{text}<br>RAM=%{x:.2f} KB<br>Recall=%{y:.2f}%<extra></extra>",
                )
            )
            fig.update_xaxes(title="RAM INT8 (KB)", type="log")
            fig.update_yaxes(title="Recall pooled (%)")
            fig.update_layout(
                height=390,
                title="Compromis performance / mémoire",
                margin=dict(l=20, r=20, t=55, b=40),
            )
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Estimateur interactif MLP TinyML")
    st.markdown(
        "Jouez avec les dimensions du MLP pour expliquer le compromis modèle / mémoire / latence pendant la soutenance."
    )
    c1, c2, c3 = st.columns(3)
    with c1:
        n_in = st.slider("Features d'entrée", 10, 200, 80, step=10)
    with c2:
        h1 = st.slider("Couche cachée 1", 8, 128, 32, step=8)
    with c3:
        h2 = st.slider("Couche cachée 2", 4, 64, 16, step=4)

    params = n_in * h1 + h1 + h1 * h2 + h2 + h2 * 1 + 1
    ram_int8_kb = 2 * params / 1024.0  # poids + buffer simple, approximation volontairement conservative
    macs = n_in * h1 + h1 * h2 + h2
    latency_us = macs / 160.0  # 1 cycle/MAC à 160 MHz, approximation pédagogique
    energy_uj = latency_us * 70.0 / 1000.0
    deployable = ram_int8_kb <= ESP32_SRAM_KB

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Paramètres", f"{params:,}")
    c2.metric("RAM INT8 estimée", f"{ram_int8_kb:.2f} KB", f"{100*ram_int8_kb/ESP32_SRAM_KB:.2f} % SRAM")
    c3.metric("Latence estimée", f"{latency_us:.2f} µs")
    c4.metric("Énergie estimée", f"{energy_uj:.3f} µJ")
    if deployable:
        st.success("Verdict : le modèle tient dans l'enveloppe mémoire ESP32 selon cette estimation.")
    else:
        st.error("Verdict : le modèle dépasse l'enveloppe mémoire ESP32 selon cette estimation.")


def render_colab() -> None:
    st.header("🔁 Google Colab et déploiement Streamlit")
    st.markdown(
        "Le notebook Colab sert à lancer le site web sans installation locale. Il clone le repo, installe les dépendances Streamlit, lance l'app et expose une URL temporaire avec Cloudflare Tunnel."
    )

    st.link_button("Ouvrir le notebook Colab", COLAB_URL, use_container_width=False)

    st.subheader("Mode 1 — Lancer seulement le site Streamlit")
    code_block(
        "Cellule Colab : cloner le repo",
        f"""
        !rm -rf iot-edge-ai-seizure-detection
        !git clone --depth 1 {REPO_URL}.git
        %cd iot-edge-ai-seizure-detection
        """,
        language="python",
    )
    code_block(
        "Cellule Colab : installer et lancer Streamlit",
        """
        !pip install -q -r requirements.txt
        !nohup streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0 > /tmp/streamlit.log 2>&1 &
        !sleep 3
        !tail -n 20 /tmp/streamlit.log
        """,
        language="python",
    )
    code_block(
        "Cellule Colab : obtenir une URL publique temporaire",
        """
        !wget -q -O /tmp/cloudflared https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
        !chmod +x /tmp/cloudflared
        !nohup /tmp/cloudflared tunnel --url http://127.0.0.1:8501 --no-autoupdate > /tmp/cloudflared.log 2>&1 &
        !sleep 8
        !grep -o 'https://[-a-zA-Z0-9.]*trycloudflare.com' /tmp/cloudflared.log | head -1
        """,
        language="python",
    )

    st.subheader("Mode 2 — Reproduire les résultats")
    st.markdown(
        "Ce mode nécessite les données SeizeIT2 dans `data/`. Sans les fichiers EDF, le pipeline complet ne peut pas s'exécuter."
    )
    code_block(
        "Pipeline complet après ajout des données",
        """
        !pip install -q -r requirements-pipeline.txt
        !python src/load_data.py
        !python src/preprocess.py
        !python src/pipeline_multirun.py
        !python src/train_multirun.py
        !python src/train_mlp.py
        !python src/estimate_esp32_cost.py
        !python src/make_figures.py
        """,
        language="python",
    )

    st.markdown("### Déploiement Streamlit Cloud")
    st.markdown(
        """
1. Pousser `streamlit_app.py`, `.streamlit/config.toml` et `notebooks/launch_streamlit_colab.ipynb` sur GitHub.
2. Aller sur Streamlit Community Cloud.
3. Choisir le repo `akiroussama/iot-edge-ai-seizure-detection`.
4. Main file path : `streamlit_app.py`.
5. Requirements file : `requirements.txt`.
"""
    )


def render_trace() -> None:
    st.header("🧾 Empreinte IA générative")
    trace_text, trace_path = load_trace_text()
    if not trace_text:
        st.info("Aucune trace IA locale trouvée. Placez le fichier dans `presentation/trace_ia.md`.")
        return

    st.success(f"Trace IA trouvée : `{trace_path.relative_to(ROOT) if trace_path and trace_path.is_relative_to(ROOT) else trace_path}`")
    st.download_button(
        "Télécharger trace_ia.md",
        data=trace_text.encode("utf-8"),
        file_name="trace_ia.md",
        mime="text/markdown",
    )

    # Small automatic summary extracted from the markdown.
    hallucination_count = len(re.findall(r"hallucin", trace_text, flags=re.IGNORECASE))
    correction_count = len(re.findall(r"correction|corrig", trace_text, flags=re.IGNORECASE))
    c1, c2, c3 = st.columns(3)
    c1.metric("Occurrences 'hallucination'", hallucination_count)
    c2.metric("Occurrences correction/corrigé", correction_count)
    c3.metric("Statut", "documenté")

    with st.expander("Résumé pour la soutenance", expanded=True):
        st.markdown(
            """
- L'IA a été utilisée pour accélérer l'extraction, la synthèse, la rédaction et l'audit.
- Les décisions scientifiques finales restent humaines : choix du dataset réel, protocole LOSO, narratif critique et validation finale.
- Les hallucinations détectées sont présentées comme une preuve de rigueur : elles ont été corrigées contre les sources primaires.
- La trace montre un protocole anti-hallucination : ancrage aux sources, audit ligne par ligne, distinction entre aide IA et décision humaine.
"""
        )

    with st.expander("Afficher le document complet", expanded=False):
        st.markdown(trace_text)


def render_questions() -> None:
    st.header("❓ Questions à poser aux autres équipes")
    st.markdown(
        "La note inclut aussi les questions posées aux autres groupes. Voici une banque de questions directement utilisables."
    )

    questions = pd.DataFrame(
        [
            [
                "Reproductibilité",
                "Votre paper donne-t-il assez de détails pour reproduire exactement le preprocessing, le split train/test et les hyperparamètres ?",
            ],
            [
                "Validation clinique",
                "La validation est-elle faite sur patients réels, sur simulation, ou sur un dataset public ? Comment cela affecte-t-il la généralisation ?",
            ],
            [
                "Métriques",
                "Dans un problème déséquilibré, pourquoi avez-vous choisi l'accuracy plutôt que le recall, la sensibilité, le FPR ou l'AUC ?",
            ],
            [
                "Edge AI",
                "Avez-vous estimé la RAM, la Flash, la latence et la consommation énergétique du modèle sur la cible embarquée ?",
            ],
            [
                "Temps réel",
                "Quelle est la taille de fenêtre utilisée, et quel délai minimal avant détection cela impose-t-il au système ?",
            ],
            [
                "Robustesse",
                "Le modèle a-t-il été testé sur des sujets absents du train set ou seulement avec un split aléatoire intra-sujet ?",
            ],
            [
                "Capteurs",
                "Que se passe-t-il si le capteur est mal positionné, bruité, ou si un canal est manquant ?",
            ],
            [
                "IA générative",
                "Comment avez-vous vérifié que les références et chiffres proposés par l'IA n'étaient pas halluciné(e)s ?",
            ],
        ],
        columns=["Thème", "Question"],
    )
    st.dataframe(questions, use_container_width=True, hide_index=True)

    st.markdown("### Question forte à poser si vous n'en gardez qu'une")
    st.markdown(
        """
<div class="sg-ok">
<strong>Dans votre protocole, quel résultat changerait si vous remplaciez le split aléatoire par une validation leave-one-subject-out ?</strong><br>
Cette question teste directement la généralisation, qui est souvent le point faible des papiers IoMT/IA embarquée.
</div>
""",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    render_sidebar()
    results = load_results_summary()
    cost = load_cost_summary()

    tabs = st.tabs(
        [
            "🏠 Vue d'ensemble",
            "📄 Livrables",
            "📊 Résultats",
            "🧠 Edge AI",
            "🔁 Colab / déploiement",
            "🧾 Trace IA",
            "❓ Questions",
        ]
    )
    with tabs[0]:
        render_home(results)
    with tabs[1]:
        render_deliverables()
    with tabs[2]:
        render_results(results)
    with tabs[3]:
        render_edge_ai(results, cost)
    with tabs[4]:
        render_colab()
    with tabs[5]:
        render_trace()
    with tabs[6]:
        render_questions()


if __name__ == "__main__":
    main()
