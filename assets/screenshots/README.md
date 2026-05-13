# Screenshots du portfolio

Le portfolio Streamlit s'affiche correctement même si ce dossier est vide. Les
images optionnelles sont chargées automatiquement par `render_screenshots()`
dans `streamlit_app.py`.

## Fichiers attendus

| Nom du fichier | Description |
|---|---|
| `portfolio_home.png` | Page d'accueil du portfolio Streamlit (onglet Projet). |
| `portfolio_results.png` | Onglet Résultats avec recall pooled. |
| `portfolio_edge_ai.png` | Onglet Edge AI / ESP32. |
| `colab_running.png` | Notebook Colab `launch_streamlit_colab.ipynb` (démo) en cours d'exécution. |
| `colab_reproduce.png` | Notebook Colab `reproduce_pipeline_colab.ipynb` (reproduction pipeline) — cellule §10 affichant les verdicts MATCH. |

## Comment générer les screenshots

1. Lancer l'app localement : `streamlit run streamlit_app.py`.
2. Naviguer dans chaque onglet, attendre le rendu complet des graphes Plotly.
3. Faire une capture (Windows : `Win + Shift + S`, macOS : `Cmd + Shift + 4`).
4. Enregistrer dans ce dossier avec les noms exacts ci-dessus.
5. Optionnel : exporter à 1600×900 pour homogénéiser.

Pour le screenshot Colab, ouvrir le notebook `notebooks/launch_streamlit_colab.ipynb`
sur `colab.research.google.com` et capturer la cellule qui affiche l'URL
`trycloudflare.com`.
