# EpiBench Phase 7 - Adoption Communautaire Et Gouvernance Du Standard

## Objectif

La phase 7 prépare l'adoption sans dépendre de l'auteur initial. Un standard communautaire ne doit pas être un document privé. Il doit être:

- versionné;
- citable;
- testable;
- extensible;
- gouverné;
- ouvert à la critique;
- compatible avec les métriques existantes.

## Release Candidate

Nom recommandé:

```text
EpiBench v1.0-rc1
```

Contenu minimal:

- `docs/EPIBENCH_SPEC_V1.md`;
- `configs/epibench/epibench_v1.yaml`;
- `schemas/epibench/*.schema.json`;
- `src/epibench/*`;
- exemples `examples/epibench/*`;
- rapports générés `reports/epibench_*_claim.*`;
- registre SOTA;
- documentation CLI;
- issue templates;
- changelog;
- versioning policy.

## DOI Et Archivage

La release candidate doit être archivée sur Zenodo ou équivalent avec:

- snapshot du code;
- hash commit;
- schémas;
- exemples;
- rapports générés;
- changelog;
- licence;
- citation file si possible.

Le DOI ne certifie pas la validité clinique. Il rend la version du standard citable.

## Gouvernance

### Rôles

- Scientific maintainer: cohérence épistémologique et claim gates.
- Clinical reviewer: pertinence neurologique, labels, risques d'overclaim.
- Benchmark maintainer: schémas, CLI, result bundles.
- SOTA steward: registre ADOPT/MAP/EXTEND/DIVERGE.
- Community reviewers: datasets, baselines, bug reports.

### Règles De Changement

Un changement est mineur s'il:

- ajoute un champ optionnel;
- clarifie une définition;
- ajoute un dataset pilote;
- corrige un bug sans changer un verdict publié.

Un changement est majeur s'il:

- modifie un poids Epi-Score;
- modifie un claim gate;
- modifie un tier dataset;
- change le verdict d'un bundle existant;
- ajoute ou supprime un sentinel bloquant.

Les changements majeurs exigent:

- justification scientifique;
- test de non-régression sur exemples;
- discussion publique;
- migration note.

## Politique De Versioning

Format:

```text
vMAJOR.MINOR.PATCH
```

- `MAJOR`: changement de verdict possible.
- `MINOR`: nouvelles capacités compatibles.
- `PATCH`: correction sans changement normatif.

Les result bundles doivent déclarer la version EpiBench utilisée.

## Issue Templates

Deux workflows communautaires sont requis:

1. Proposition de dataset.
2. Soumission de result bundle.

Chaque proposition doit indiquer:

- source officielle;
- licence;
- capteurs;
- labels;
- split;
- MTS/DSI préliminaire;
- limites;
- relationship SOTA.

## Compatibility Policy

EpiBench ne concurrence pas frontalement SzCORE. EpiBench doit pouvoir:

- consommer une sortie SzCORE lorsque le track est compatible;
- mapper sensitivity, precision, F1, false positives/day;
- ajouter autour de cette sortie les evidence cards, failure traces, hardware evidence, claim gates.

La règle de gouvernance:

> Si une métrique événementielle externe est validée et compatible, EpiBench doit l'adopter ou la mapper avant de définir une alternative.

## Adoption Checklist

Un groupe externe doit pouvoir adopter EpiBench en suivant:

1. Lire `docs/EPIBENCH_SPEC_V1.md`.
2. Remplir `dataset_card.yaml`.
3. Remplir `split_manifest.yaml`.
4. Générer `failure_trace.yaml`.
5. Générer `result_bundle.yaml`.
6. Exécuter `python scripts\epibench.py certify ...`.
7. Inclure le claim report dans l'article ou supplement.
8. Citer la version EpiBench.

## Risques D'Adoption

- Badge washing: utiliser le badge sans bundle vérifiable.
- Version drift: comparer des résultats certifiés avec versions différentes.
- Claim inflation: transformer `E2-PI` en "clinically ready".
- Dataset laundering: utiliser un tier T1 pour masquer un split faible.
- SOTA conflict: ignorer SzCORE ou guidelines existantes.

## Critère D'Acceptation

La phase 7 est acceptable si:

- un utilisateur externe peut certifier l'exemple sans contact direct;
- le repository contient templates de soumission;
- les règles de versioning existent;
- la relation à SzCORE/SOTA est explicite;
- une release `v1.0-rc1` peut être archivée avec DOI;
- les claims autorisés et interdits sont visibles dans chaque rapport.

## Sortie Phase 7

La sortie n'est pas seulement un article. C'est un paquet de standard scientifique prêt à être audité, cité et contesté.
