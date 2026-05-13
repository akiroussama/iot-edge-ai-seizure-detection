# Checklist de déploiement — Groupe 2

## Avant push GitHub

- [ ] `streamlit_app.py` existe à la racine du dépôt.
- [ ] `.streamlit/config.toml` existe.
- [ ] `requirements.txt` contient `streamlit`, `plotly`, `pandas`, `numpy`.
- [ ] `notebooks/launch_streamlit_colab.ipynb` existe (démo Streamlit).
- [ ] `notebooks/reproduce_pipeline_colab.ipynb` existe (reproduction pipeline).
- [ ] `assets/project_workflow_infographic.svg` existe (affiché dans l'onglet Projet).
- [ ] `presentation/trace_ia.md` existe déjà dans le dépôt.
- [ ] `docs/REPRODUCTION.md` existe déjà dans le dépôt.
- [ ] `results/multirun_loso.csv`, `results/mlp_loso.csv` et `results/esp32_cost_estimate.json` existent.
- [ ] Remplacer `assets/presentation_iot_uploaded.pdf` par `assets/presentation_iot.pdf` lorsque la présentation finale est réexportée proprement.

## Test local

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Vérifier les onglets :

- [ ] Projet (avec infographie SVG visible).
- [ ] Méthodologie.
- [ ] Résultats.
- [ ] Edge AI.
- [ ] Livrables (section screenshots accessible, même si vide).
- [ ] Google Colab.
- [ ] Trace IA.
- [ ] Conclusion.
- [ ] Questions.

## Streamlit Cloud

- [ ] Repository : `akiroussama/iot-edge-ai-seizure-detection`.
- [ ] Branch : `main`.
- [ ] Main file path : `streamlit_app.py`.
- [ ] Requirements file : `requirements.txt`.
- [ ] Ajouter l'URL Streamlit dans l'e-mail final.

## Google Colab

- [ ] Démo Streamlit — ouvrir : `https://colab.research.google.com/github/akiroussama/iot-edge-ai-seizure-detection/blob/main/notebooks/launch_streamlit_colab.ipynb`.
- [ ] La cellule Cloudflare affiche une URL `trycloudflare.com`.
- [ ] Le site s'ouvre via l'URL temporaire.
- [ ] Reproduction pipeline — ouvrir : `https://colab.research.google.com/github/akiroussama/iot-edge-ai-seizure-detection/blob/main/notebooks/reproduce_pipeline_colab.ipynb`.
- [ ] Cellule §10 affiche `MATCH` pour les 4 modèles (TP = 29, 78, 98, 58).
