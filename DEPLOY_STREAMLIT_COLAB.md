# Déploiement du site Streamlit + Google Colab

Ce package ajoute un mini-site web au dépôt `iot-edge-ai-seizure-detection`.

Il regroupe :

- un site Streamlit principal : `streamlit_app.py` ;
- deux notebooks Google Colab :
  - `notebooks/launch_streamlit_colab.ipynb` (démo Streamlit, 1 min, aucune donnée nécessaire) ;
  - `notebooks/reproduce_pipeline_colab.ipynb` (reproduction complète de la pipeline scientifique sur SeizeIT2, 20–60 min) ;
- une page statique optionnelle GitHub Pages : `docs/index.html` ;
- une configuration Streamlit : `.streamlit/config.toml` ;
- un dossier `assets/` pour intégrer le rapport et la présentation ;
- une checklist de déploiement : `docs/DEPLOYMENT_CHECKLIST.md`.

Le fichier d'empreinte IA générative existe déjà dans le repo : `presentation/trace_ia.md`. Le site le lit automatiquement.

## 1. Copier les fichiers dans le repo

Depuis votre machine :

```bash
cd iot-edge-ai-seizure-detection

# Optionnel mais conseillé : garder l'app demo actuelle avant remplacement
# cp streamlit_app.py streamlit_demo_live.py
mkdir -p notebooks .streamlit assets docs

# Copier depuis le package fourni :
cp /chemin/package/streamlit_app.py .
cp /chemin/package/requirements.txt .
cp /chemin/package/.streamlit/config.toml .streamlit/config.toml
cp /chemin/package/notebooks/launch_streamlit_colab.ipynb notebooks/
cp /chemin/package/docs/index.html docs/index.html
cp /chemin/package/docs/DEPLOYMENT_CHECKLIST.md docs/
cp /chemin/package/DEPLOY_STREAMLIT_COLAB.md .

# Optionnel : intégrer les PDF uploadés
cp /chemin/package/assets/report_iot.pdf assets/report_iot.pdf
cp /chemin/package/assets/presentation_iot_uploaded.pdf assets/presentation_iot_uploaded.pdf
```

## 2. Commit Git conseillé

```bash
git status
# Si vous avez sauvegardé l'ancienne app :
# git add streamlit_demo_live.py

git add streamlit_app.py requirements.txt .streamlit/config.toml \
        notebooks/launch_streamlit_colab.ipynb \
        docs/index.html docs/DEPLOYMENT_CHECKLIST.md \
        DEPLOY_STREAMLIT_COLAB.md

# Ajouter les PDF seulement si vous voulez les embarquer dans le repo :
git add assets/report_iot.pdf assets/presentation_iot_uploaded.pdf

git commit -m "feat(streamlit): add project portfolio website and Colab launcher"
git push origin main
```

## 3. Lancement local

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## 4. Lancement dans Google Colab

Une fois le notebook poussé dans le repo :

```text
https://colab.research.google.com/github/akiroussama/iot-edge-ai-seizure-detection/blob/main/notebooks/launch_streamlit_colab.ipynb
```

Le notebook :

1. clone le repo ;
2. installe `requirements.txt` ;
3. lance `streamlit_app.py` ;
4. expose une URL temporaire `trycloudflare.com`.

## 5. Déploiement Streamlit Community Cloud

1. Aller sur Streamlit Community Cloud.
2. Créer une nouvelle app.
3. Sélectionner le repo `akiroussama/iot-edge-ai-seizure-detection`.
4. Branch : `main`.
5. Main file path : `streamlit_app.py`.
6. Requirements file : `requirements.txt`.
7. Déployer.

## 6. GitHub Pages optionnel

Le fichier `docs/index.html` est une landing page statique. Pour l'activer :

1. GitHub repo → Settings → Pages.
2. Source : `Deploy from a branch`.
3. Branch : `main`.
4. Folder : `/docs`.
5. Save.

## 7. Remplacement du PDF de présentation

La version PDF uploadée initialement semblait exportée avec un problème d'orientation/rognage. Pour la version finale :

```bash
mv assets/presentation_iot_uploaded.pdf assets/presentation_iot_old.pdf
cp /chemin/vers/presentation_finale.pdf assets/presentation_iot.pdf
git add assets/presentation_iot.pdf assets/presentation_iot_old.pdf
git commit -m "docs: add final presentation pdf"
git push
```

Le site cherche d'abord `assets/presentation_iot.pdf`, puis utilise `assets/presentation_iot_uploaded.pdf` seulement si la version finale n'existe pas.

## 8. Reproduction complète

Le mode site ne nécessite pas le dataset brut. Pour refaire les simulations :

```bash
pip install -r requirements-pipeline.txt
python src/load_data.py
python src/preprocess.py
python src/pipeline_multirun.py
python src/train_multirun.py
python src/train_mlp.py
python src/estimate_esp32_cost.py
python src/make_figures.py
```

Les données SeizeIT2 doivent être placées dans `data/`. Elles ne sont pas incluses dans le repo.
