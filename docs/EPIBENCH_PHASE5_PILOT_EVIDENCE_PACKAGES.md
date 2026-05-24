# EpiBench Phase 5 - Datasets Pilotes, Evidence Packages Et Worked Example

## Objectif

La phase 5 doit démontrer que le protocole change réellement l'interprétation scientifique. Un standard de preuve doit montrer au moins un cas où le classement naïf est trompeur.

Le but n'est pas d'obtenir le meilleur modèle. Le but est de prouver que:

- le protocole est exécutable;
- les datasets sont qualifiés séparément des algorithmes;
- les failures restent visibles;
- les claims sont bornés;
- les métriques événementielles et IoT sont interprétées ensemble.

## Datasets Pilotes Recommandés

### TUSZ ou CHB-MIT

Rôle:

- track `D`;
- EEG clinique;
- comparaison avec scoring événementiel existant;
- ancrage avec la littérature seizure detection.

Ce que EpiBench ajoute:

- evidence card;
- split manifest explicite;
- failure trace;
- claim ceiling.

### SeizeIT2

Rôle:

- wearable multimodal;
- pont clinique vers IoT;
- stress capteurs, missingness, mouvement, multimodalité.

Ce que EpiBench doit éviter:

- ne pas généraliser à domicile si l'évidence provient surtout d'un contexte hospitalier;
- ne pas confondre détection focal epilepsy wearable avec forecasting long terme.

### My Seizure Gauge ou longitudinal wearable équivalent

Rôle:

- track `F`;
- risque longitudinal, rythmes circadiens/multijours, SPH/SOP;
- calibration et alarm burden.

Ce que EpiBench doit éviter:

- ne pas appeler forecasting un simple détecteur;
- ne pas revendiquer predictability universelle.

## Evidence Package Minimal Par Dataset

Chaque dataset pilote doit fournir:

- `dataset_card.yaml`;
- MTS/DSI avec rubriques 0/1/2/3;
- claim ceiling dataset;
- `split_manifest.yaml`;
- label audit;
- baseline suite;
- `failure_trace.yaml`;
- `result_bundle.yaml`;
- `claim_eligibility_report.json`;
- rapport Markdown;
- commande de reproduction;
- registre des limites.

## Worked Example Pédagogique

Le dépôt contient deux exemples exécutables:

1. `examples/epibench/pilot_t1_eeg/result_bundle.yaml`
2. `examples/epibench/failure_leakage/result_bundle.yaml`

### Classement Naïf

| Modèle | Sensitivity | Precision | FAR/24h | Lecture naïve |
| --- | ---: | ---: | ---: | --- |
| LeakageHighMetric | 0.99 | 0.95 | 0.1 | meilleur |
| EdgeCNNDemo | 0.83 | 0.71 | 1.2 | second |

Lecture naïve: le modèle avec leakage gagne.

### Lecture EpiBench

| Modèle | Epi-Score | Failure | Split | Final claim | Interprétation |
| --- | ---: | --- | --- | --- | --- |
| LeakageHighMetric | 94.727 | patient leakage, split non conforme, threshold sur test | invalide | E1 | structure invalide, pas de claim opérationnel |
| EdgeCNNDemo | 74.158 | aucune failure bloquante | LOSO | E2-PI | claim patient-independent étroit |

Conclusion:

> Le meilleur score naïf n'est pas le meilleur résultat scientifique.

## Figures À Produire

Pour le papier:

1. Pipeline evidence package: raw data vers card, split, predictions, failure trace, claim report.
2. Claim gate waterfall: requested claim vers final claim.
3. Naive leaderboard versus claim-gated leaderboard.
4. Failure heatmap par patient/fold.
5. Sensitivity versus FAR/day.
6. Latency distribution median/p95.
7. Per-patient distribution avec worst-case patient.
8. Track separation timeline: detection, early warning, SPH/SOP forecasting.

## Critères D'Acceptation

Phase 5 est terminée si:

- au moins deux datasets réels sont qualifiés par evidence card;
- au moins un dataset wearable est inclus;
- au moins un exemple échoue de manière instructive;
- les baselines triviales sont présentes;
- le protocole reproduit une inversion d'interprétation entre leaderboard naïf et claim-gated ranking;
- les limites dataset sont aussi visibles que les métriques modèle.

## Risques

- Choisir seulement des exemples qui flattent le protocole.
- Eviter les failures au lieu de les montrer.
- Utiliser SeizeIT2 pour faire un claim domicile si le protocole d'acquisition ne le permet pas.
- Utiliser un dataset EEG clinique pour conclure sur un wearable IoT.
- Publier un Epi-Score sans claim report.

## Sortie Phase 5

La sortie est une démonstration reproductible que le protocole transforme un tableau de scores en preuve bornée.
