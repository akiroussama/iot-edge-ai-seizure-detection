# EpiBench Phase 2 - Single Source Of Truth Normatif

## Position

La phase 2 transforme EpiBench d'un protocole argumentatif en standard vérifiable par machine. Le document Markdown explique le standard, mais il ne doit pas être la seule autorité. La source de vérité opérationnelle est maintenant:

- `configs/epibench/epibench_v1.yaml`: règles, claims, poids, budgets, gates et badges.
- `schemas/epibench/*.schema.json`: contrats d'artefacts.
- `configs/epibench/sota_registry_v1.yaml`: registre SOTA, pour éviter de réinventer les métriques et guidelines existantes.
- `src/epibench/*`: implémentation de référence appliquant ces règles.

Ce choix est central. Un protocole scientifique de haut niveau ne peut pas dépendre d'une lecture libre du texte. Les claims doivent être produits par des règles déterministes.

## Principe Normatif

EpiBench suit une hiérarchie d'autorité:

1. Le Markdown donne la justification scientifique.
2. Le YAML donne les paramètres normatifs.
3. Les JSON Schemas définissent les contrats d'entrée et de sortie.
4. Le CLI applique les règles et génère le verdict.

Si un résultat ne passe pas les schémas, il n'est pas EpiBench-valid. Si un résultat passe les schémas mais échoue aux gates, il peut rester informatif, mais son claim est abaissé.

## Artefacts Créés

### YAML Normatif

Fichier: `configs/epibench/epibench_v1.yaml`

Contenu normatif:

- tracks `D`, `W`, `F`, `E`;
- claims `E0`, `E1`, `E2-PD`, `E2-PI`, `E3`, `E4`;
- tiers dataset `T1`, `T2`, `T3`;
- plafonds de claims par type de split;
- plafonds de claims par audit de labels;
- formule Epi-Score;
- poids des axes;
- budgets de faux positifs, latence, missingness;
- conséquences des sentinels;
- badges de certification;
- claim gates;
- règles anti-overclaim;
- exigences minimales de registre SOTA.

### Schémas

Fichiers:

- `schemas/epibench/dataset_evidence_card.schema.json`;
- `schemas/epibench/split_manifest.schema.json`;
- `schemas/epibench/failure_trace.schema.json`;
- `schemas/epibench/result_bundle.schema.json`;
- `schemas/epibench/claim_eligibility.schema.json`;
- `schemas/epibench/sota_registry.schema.json`.

Ces schémas ne prétendent pas capturer toute la vérité clinique. Ils capturent le minimum nécessaire pour empêcher les claims non auditables.

### Registre SOTA

Fichier: `configs/epibench/sota_registry_v1.yaml`

Le registre impose que chaque élément d'EpiBench soit classé:

- `ADOPT`: EpiBench reprend directement une règle ou une nomenclature.
- `MAP`: EpiBench accepte un résultat externe et le mappe dans un champ EpiBench.
- `EXTEND`: EpiBench ajoute une couche de preuve non couverte.
- `DIVERGE`: EpiBench diverge explicitement avec justification.

Sources déjà intégrées:

- ILAE 2017 pour la nomenclature des types de crises.
- SzCORE pour les métriques événementielles de détection.
- SeizeIT2 et TUSZ comme datasets pilotes possibles.
- TRIPOD+AI, STARD-AI, DECIDE-AI, CONSORT-AI, FUTURE-AI pour la discipline de reporting.
- FDA CDS guidance pour la prudence réglementaire et l'anti-overclaim.

## Critères D'Acceptation

La phase 2 est acceptable si:

- un dataset card valide passe le schéma;
- un split manifest valide passe le schéma;
- un result bundle valide passe le schéma;
- un failure trace valide passe le schéma;
- un registre SOTA valide passe le schéma;
- une erreur de champ obligatoire provoque un échec explicite;
- un claim eligibility report est lui-même validable par schéma;
- les valeurs normatives ne sont pas dupliquées dans plusieurs fichiers divergents.

## Décisions Verrouillées

- Le claim final est généré, pas choisi par l'auteur.
- L'absence de preuve abaisse le claim.
- `EpiBench-certified` veut dire certification scientifique du bundle, pas validation clinique ni réglementaire.
- Les tracks détection, early warning, forecasting et embedded viability ne sont pas interchangeables.
- Les métriques existantes comme SzCORE doivent être réutilisées ou mappées lorsque compatibles.

## Tests Requis

Tests minimaux:

```powershell
python scripts\epibench.py validate-dataset-card examples\epibench\pilot_t1_eeg\dataset_card.yaml
python scripts\epibench.py validate-split examples\epibench\pilot_t1_eeg\split_manifest.yaml
python scripts\epibench.py validate-result-bundle examples\epibench\pilot_t1_eeg\result_bundle.yaml
python scripts\epibench.py validate-sota-registry configs\epibench\sota_registry_v1.yaml
```

Test scientifique:

- deux reviewers doivent pouvoir lire le même dataset card et retrouver le même ceiling de claim;
- si ce n'est pas le cas, la rubrique MTS/DSI est trop subjective et doit être resserrée.

## Risques

- Un YAML trop flexible peut devenir une décoration au lieu d'une norme.
- Des schémas trop faibles peuvent laisser passer des claims vagues.
- Des schémas trop rigides peuvent bloquer des datasets utiles mais imparfaits.
- Le registre SOTA doit être maintenu, sinon EpiBench risque de dériver vers un standard isolé.

## Sortie Phase 2

La sortie attendue est atteinte lorsque le protocole peut refuser mécaniquement un artefact incomplet avant même de discuter de performance.
