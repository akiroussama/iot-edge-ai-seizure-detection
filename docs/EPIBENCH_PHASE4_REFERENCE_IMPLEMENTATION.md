# EpiBench Phase 4 - Reference Implementation Fonctionnelle

## But

La phase 4 donne à la communauté un outil immédiatement testable. Le standard ne doit pas rester un PDF. Un reviewer, un étudiant ou un laboratoire externe doit pouvoir exécuter une commande et obtenir:

- validation des artefacts;
- Epi-Score;
- claim eligibility report;
- badges;
- raisons bloquantes;
- rapport Markdown.

## Interface CLI

Point d'entrée local:

```powershell
python scripts\epibench.py <command>
```

Commandes disponibles:

```text
validate-dataset-card
validate-split
validate-result-bundle
validate-failure-trace
validate-sota-registry
score
certify
render-report
```

Cette interface correspond à l'interface cible `epibench certify`. A terme, elle pourra être exposée comme console script dans `pyproject.toml`.

## Modules

- `src/epibench/spec.py`: chargement du YAML normatif et rangs de claims.
- `src/epibench/validation.py`: validateur JSON Schema minimal sans dépendance externe obligatoire.
- `src/epibench/scoring.py`: calcul du score géométrique pondéré.
- `src/epibench/certification.py`: application des claim gates et génération du rapport.
- `src/epibench/cli.py`: interface utilisateur.

## Propriétés Scientifiques

### Séparation Score/Claim

`compute_epi_score` calcule un score multi-axes. Il ne décide pas du claim.

`certify_result_bundle` décide du claim à partir de:

- dataset tier;
- split policy;
- label audit;
- failure sentinels;
- leakage checks;
- threshold selection policy;
- track consistency;
- hardware evidence.

Donc un score élevé ne peut pas compenser un leakage.

### Fail-Closed

Les artefacts invalides échouent explicitement. Le système ne remplit pas les champs manquants par hypothèse favorable.

### Sorties Auditables

Le rapport JSON est le résultat canonique. Le Markdown est une projection lisible.

## Exemple Minimal

Validation:

```powershell
python scripts\epibench.py validate-dataset-card examples\epibench\pilot_t1_eeg\dataset_card.yaml
python scripts\epibench.py validate-split examples\epibench\pilot_t1_eeg\split_manifest.yaml
python scripts\epibench.py validate-result-bundle examples\epibench\pilot_t1_eeg\result_bundle.yaml
```

Certification:

```powershell
python scripts\epibench.py certify examples\epibench\pilot_t1_eeg\result_bundle.yaml --out reports\epibench_pilot_claim.json --report reports\epibench_pilot_claim.md
```

Cas négatif:

```powershell
python scripts\epibench.py certify examples\epibench\failure_leakage\result_bundle.yaml --out reports\epibench_leakage_claim.json --report reports\epibench_leakage_claim.md
```

## Limites De L'Implementation Actuelle

Cette reference implementation est une base v1.0-draft:

- le validateur JSON Schema couvre le sous-ensemble utilisé par les schémas EpiBench;
- le score consomme des sous-scores déjà fournis dans le bundle;
- la connexion directe à SzCORE ou à des sorties événementielles externes est à implémenter en phase d'intégration;
- les checksums sont acceptés comme champs mais pas recalculés automatiquement;
- les rubriques MTS/DSI sont validées structurellement, pas encore recalculées à partir de preuves brutes.

Ces limites doivent être déclarées dans le papier. Elles ne disqualifient pas le standard; elles définissent le périmètre exact du release candidate.

## Definition Of Done

La phase 4 est acceptable si:

- un utilisateur externe peut valider et certifier l'exemple en moins de 10 minutes;
- les deux exemples pédagogiques produisent des verdicts différents malgré un score naïf meilleur dans le cas invalide;
- les rapports JSON et Markdown sont produits;
- les tests unitaires couvrent validation, score, et leakage gate;
- les erreurs sont explicites.

## Critère De Publication

Le papier ne doit pas présenter le CLI comme produit industriel. Il doit le présenter comme reference implementation permettant de reproduire les règles du protocole.
