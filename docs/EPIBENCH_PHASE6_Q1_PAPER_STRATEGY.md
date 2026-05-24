# EpiBench Phase 6 - Stratégie Paper Q1

## Positionnement Scientifique

EpiBench ne doit pas être soumis comme "nouveau modèle de détection de crises". Cette formulation serait faible et exposerait le papier à une compétition SOTA superficielle.

Le positionnement fort est:

> EpiBench est une infrastructure de preuve et de certification de claims pour l'IA de détection, early warning, forecasting et viabilité IoT en épilepsie.

Le papier reste défendable même si aucun modèle profond n'obtient une performance spectaculaire. C'est un papier de méthodologie scientifique, d'assurance de l'évidence et de reproductibilité.

## Contribution Principale

Le papier doit défendre quatre contributions:

1. Séparation explicite entre qualité dataset, performance modèle, failures et claim.
2. Evidence cards MTS/DSI pour datasets épilepsie.
3. Claim gates déterministes `E0` à `E4`, incluant `E2-PD` et `E2-PI`.
4. Reference implementation avec result bundles et worked examples.

La contribution n'est pas de remplacer SzCORE, TRIPOD+AI ou STARD-AI. Elle est de les connecter à une couche de claim eligibility spécifique à l'épilepsie et à l'IoT.

## Plan D'Article

1. **Scores alone are not evidence**
   - accuracy inutile en rare-event;
   - AUROC insuffisant si l'objectif est FAR/day;
   - sensitivity dangereuse sans alarm burden;
   - patient-dependent non généralisable;
   - latence et hardware souvent ignorés.

2. **Failure modes in seizure AI evaluation**
   - leakage patient;
   - temporal leakage;
   - labels onset/offset incertains;
   - split non déclaré;
   - threshold sur test;
   - failures supprimées;
   - confusion detection, warning, forecasting.

3. **EpiBench architecture**
   - dataset evidence card;
   - MTS/DSI;
   - tracks `D/W/F/E`;
   - result bundle;
   - claim eligibility.

4. **SOTA alignment**
   - ILAE pour vocabulaire crise;
   - SzCORE pour event scoring si compatible;
   - TRIPOD+AI/STARD-AI/DECIDE-AI/CONSORT-AI/FUTURE-AI pour reporting et évaluation;
   - EpiBench comme couche de preuve, pas remplacement.

5. **Dataset evidence cards**
   - rubriques;
   - reviewer agreement;
   - fail-closed;
   - exemples T1/T2/T3.

6. **Claim gates**
   - table déterministe;
   - examples;
   - anti-overclaim.

7. **Epi-Score**
   - formule géométrique;
   - axes;
   - penalty floor;
   - séparation score/claim.

8. **Reference implementation**
   - schemas;
   - YAML source of truth;
   - CLI;
   - reports.

9. **Worked examples**
   - naive ranking;
   - Epi-Score ranking;
   - claim-gated ranking;
   - failure-aware interpretation.

10. **Community adoption**
   - GitHub;
   - DOI;
   - governance;
   - compatibility with existing event scoring.

## Venues

### npj Digital Medicine

Angle:

- AI assurance;
- claim governance;
- reproducibility;
- clinical AI evidence.

Condition:

- clinique très solide;
- reviewer médical impliqué;
- discussion claire des limites réglementaires.

### IEEE Journal of Biomedical and Health Informatics

Angle:

- benchmark infrastructure;
- IoT/edge evaluation;
- reproducible biomedical AI.

Condition:

- reference implementation robuste;
- résultats pilotes avec tableaux quantitatifs.

### IEEE Transactions on Biomedical Engineering

Angle:

- méthodologie d'évaluation biomédicale;
- signal processing et IoT;
- hardware-aware evaluation.

Condition:

- formulation technique stricte;
- métriques événementielles et latence très propres.

### Epilepsia / Epilepsia Open

Angle:

- pertinence clinique;
- false alarms/day, missed seizures, annotation neurologue.

Condition:

- co-auteur clinique ou review neurologue fortement recommandé;
- langage non réglementaire irréprochable.

### Scientific Data

Angle:

- standard, evidence packages, resource reusable.

Condition:

- datasets/evidence packages publics et bien décrits;
- DOI Zenodo.

## Figures De Manuscrit

1. EpiBench evidence architecture.
2. Track timeline D/W/F/E.
3. Dataset Evidence Card schema and MTS/DSI axes.
4. Claim eligibility matrix.
5. Failure-preserving evaluation flow.
6. Epi-Score geometric axes.
7. Naive leaderboard versus EpiBench verdict.
8. Reference implementation CLI/report bundle.

## Reviewer Attacks Et Défenses

Attack: "Ce n'est pas un nouveau modèle."  
Defense: Le papier est une contribution méthodologique; il définit ce qu'un résultat a le droit de prouver.

Attack: "Les rubriques MTS/DSI sont subjectives."  
Defense: Rubriques 0/1/2/3, review indépendante, tests d'accord inter-reviewer, fail-closed.

Attack: "Vous réinventez SzCORE."  
Defense: EpiBench mappe/adopte les métriques événementielles compatibles; il ajoute dataset evidence, failures, claims et IoT viability.

Attack: "La certification est dangereuse."  
Defense: Certification scientifique du résultat, pas clinique, pas réglementaire, pas dispositif médical.

Attack: "Le score agrégé masque les risques."  
Defense: Le claim gate prime sur le score; les axes et failures restent visibles.

## Critère De Soumission

Le manuscrit est soumission-ready seulement si:

- deux evidence packages réels sont complets;
- un worked example négatif est inclus;
- un neurologue ou expert clinique a reviewé les claims;
- les scripts reproduisent les rapports;
- le registre SOTA est vérifié;
- les claims sont plus conservateurs que les résultats bruts;
- le repository public possède une release candidate.

## Sortie Phase 6

La sortie est un manuscrit dont la thèse reste vraie même en présence de résultats modestes: la valeur est dans la preuve auditable.
