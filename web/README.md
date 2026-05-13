# Portfolio web — Vercel deploy

Ce dossier contient la **landing page premium** du projet, prête pour
un déploiement Vercel statique. Elle sert de *single source of truth*
web et pointe vers tous les autres livrables (repository GitHub,
portfolio Streamlit, notebook Colab, rapport PDF, trace IA, dataset).

## Contenu

| Fichier | Rôle |
|---|---|
| `index.html` | Landing premium, autonome, mobile + dark mode. |
| `assets/project_workflow_infographic.svg` | Infographie workflow. |
| `vercel.json` | Headers de sécurité + cache long sur `/assets/*`. |

Pas de framework, pas de build step. Le site fonctionne tel quel
dans n'importe quel serveur statique.

## Test local

```bash
cd web
python -m http.server 8080
# Ouvrir http://localhost:8080
```

Ou avec Node :

```bash
cd web
npx --yes serve .
```

## Déploiement Vercel — recommandé (depuis la racine du repo)

Un `vercel.json` est présent **à la racine du repo** avec
`"outputDirectory": "web"`. Vercel sait donc déjà que le site
est servi depuis `web/`, sans avoir à choisir un Root Directory
particulier dans l'UI Vercel.

1. Pousser le repo sur GitHub :
   ```bash
   git add vercel.json web/ assets/project_workflow_infographic.svg \
           assets/README.md assets/screenshots/ \
           docs/assets/ docs/index.html docs/DEPLOYMENT_CHECKLIST.md \
           streamlit_app.py README.md
   git commit -m "feat(portfolio): add Vercel landing and SSOT structure"
   git push origin main
   ```
2. Aller sur https://vercel.com/new
3. Importer le repo `akiroussama/iot-edge-ai-seizure-detection`.
4. **Laisser Root Directory = `./`** (le `vercel.json` racine gère
   tout). Framework Preset : *Other*.
5. Cliquer *Deploy*. URL `*.vercel.app` disponible en < 30 s.

## Déploiement Vercel — variante "Root = web/"

Si tu préfères pointer Vercel directement sur `web/` :

1. Pousser le code (cf. ci-dessus).
2. Sur Vercel, sélectionner **Root Directory = `web`** dans
   les *Project Settings*.
3. Le `web/vercel.json` prend alors le relais. Le `vercel.json`
   racine est ignoré.

## Déploiement Vercel — CLI

```bash
npm install -g vercel
cd web
vercel --prod
```

Au premier déploiement, accepter les défauts proposés par Vercel
(framework: « Other », root: `./`, output: `./`).

## Mise à jour du contenu

Les chiffres scientifiques sont **codés en dur** dans `index.html`
pour garantir la cohérence avec :

- `results/multirun_loso_pooled.json` (source de vérité numérique)
- `streamlit_app.py` (portfolio interactif)
- `docs/index.html` (variante GitHub Pages)
- `README.md` (entrée GitHub)

Toute mise à jour d'un chiffre doit être propagée à **tous** ces
fichiers en même temps. Aucun calcul côté client.

## Domaines

Pour un domaine custom :

1. Vercel → Project Settings → Domains → Add.
2. Pointer le DNS vers `cname.vercel-dns.com`.
3. Le certificat TLS est provisionné automatiquement.

## Performance attendue

- Premier rendu < 1 s sur 4G.
- Score Lighthouse > 95 sur Performance/Accessibility/SEO.
- Pas de tracker tiers. Pas de JavaScript bloquant.
- Une seule famille de fonts Google chargée (Instrument Serif +
  IBM Plex Sans + IBM Plex Mono) avec `display=swap`.
