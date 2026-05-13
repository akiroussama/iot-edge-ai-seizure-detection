# Assets du portfolio

## PDF de soutenance

- `report_iot.pdf` : rapport / document IA uploadé.
- `presentation_iot_uploaded.pdf` : PDF de présentation uploadé initialement.

Pour la version finale, ajouter à côté :

```text
assets/presentation_iot.pdf
```

Le portfolio charge en priorité `assets/presentation_iot.pdf` et retombe sur
`presentation_iot_uploaded.pdf` seulement si la version finale n'existe pas.

## Infographie

- `project_workflow_infographic.svg` : diagramme workflow complet du projet
  (paper → dataset → preprocessing → modèles → LOSO → résultats → Edge AI →
  livrables). Affiché dans l'onglet **Projet** du Streamlit.
- `project_workflow_infographic.png` (optionnel) : version raster pour
  intégration dans des slides ou des contextes qui ne rendent pas le SVG.
  Pour la générer à partir du SVG :

  ```bash
  # ImageMagick
  magick convert -density 200 assets/project_workflow_infographic.svg \
      assets/project_workflow_infographic.png

  # ou Inkscape
  inkscape assets/project_workflow_infographic.svg \
      --export-type=png --export-dpi=200 \
      --export-filename=assets/project_workflow_infographic.png
  ```

## Screenshots

Voir `assets/screenshots/README.md`. Le portfolio reste fonctionnel sans
screenshot ; les fichiers attendus sont listés dans ce sous-README.

