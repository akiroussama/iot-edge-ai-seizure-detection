# EpiBench Phase 1 Detailed Plan

Date: 2026-05-24  
Phase: 1 - Durcissement epistemologique du protocole  
Statut: plan d'execution detaille, pre-implementation  
Document parent: `docs/EPIBENCH_Q1_STANDARD_ROADMAP.md`  
Document source a durcir: `docs/EPIBENCH_PROTOCOL.md`

## These centrale de la Phase 1

La Phase 1 doit transformer EpiBench d'un protocole conceptuel en protocole normatif.

Le resultat attendu n'est pas un texte plus long. Le resultat attendu est une structure de preuve dans laquelle:

- deux reviewers independants appliquent les memes rubriques et arrivent au meme claim ceiling;
- un dataset ne peut pas etre surinterprete au-dela de sa qualite metrologique;
- un split patient-dependent ne peut pas etre lu comme une generalisation patient-independent;
- un bon score algorithmique ne peut pas compenser des labels faibles, une leakage failure, une absence de failure trace ou une absence de FAR/day;
- chaque faille critique a une consequence explicite sur le claim autorise.

Formule courte:

> Phase 1 = supprimer l'ambiguite scientifique avant d'ecrire le code.

## Definition of Done globale

La Phase 1 est terminee uniquement si les conditions suivantes sont toutes satisfaites:

1. `EPIBENCH_PROTOCOL.md` est aligne avec un vocabulaire normatif stable.
2. Les axes MTS et DSI ont chacun une grille 0/1/2/3 itemisee.
3. Les criteres T1/T2/T3 sont derives de MTS, DSI et des regles fail-closed.
4. Les tracks `D`, `W`, `F`, `E` sont separes avec question scientifique, entrees, sorties, metriques primaires et claims autorises.
5. Le claim ladder est scinde en `E0`, `E1`, `E2-PD`, `E2-PI`, `E3`, `E4`.
6. Une table de claim ceiling determine le claim maximal a partir de la qualite dataset, du split, de l'audit label, des failures, de la validation externe et de l'evidence hardware.
7. Chaque sentinel/failure critique a une consequence explicite: score impact, badge impact, claim impact ou invalidation.
8. Un worked example de Phase 1 montre comment deux reviewers appliquent les rubriques au meme dataset et obtiennent le meme verdict.
9. Le plan d'acceptation inclut une review scientifique, une review clinique et une review reproducibility.
10. Aucune phrase ne permet de confondre certification EpiBench avec validation clinique ou reglementaire.

Une Phase 1 "presque terminee" n'est pas terminee si elle laisse encore aux auteurs la possibilite de choisir leur claim apres avoir vu les resultats.

## Non-objectifs de la Phase 1

La Phase 1 ne doit pas encore:

- implementer le CLI `epibench`;
- creer tous les JSON Schemas finaux;
- calculer l'Epi-Score complet;
- executer les datasets pilotes;
- soumettre le papier;
- revendiquer une certification clinique;
- produire un leaderboard final.

Ces elements appartiennent aux phases 2 a 7. La Phase 1 doit produire le socle epistemologique qui les rendra possibles.

## Inputs obligatoires

Avant de demarrer la Phase 1, les documents suivants doivent etre relus:

- `docs/EPIBENCH_PROTOCOL.md`
- `docs/EPIBENCH_Q1_STANDARD_ROADMAP.md`
- `docs/PUBLICATION_PROPOSAL.md`
- `docs/HUMAN_LABEL_AUDIT_PROTOCOL.md`
- `docs/RISK_REGISTER.md`
- rapports existants de label audit, failure taxonomy, leakage audit et dataset report quand disponibles.

## Outputs attendus de la Phase 1

La Phase 1 doit produire ou modifier les artefacts suivants:

| Artefact | Type | Role |
| --- | --- | --- |
| `docs/EPIBENCH_SPEC_V1.md` | nouveau document normatif | source textuelle principale de la spec v1 |
| `docs/EPIBENCH_PROTOCOL.md` | document existant a aligner | protocole scientifique lisible et coherent avec la spec |
| `docs/EPIBENCH_PHASE1_REVIEW_CHECKLIST.md` | nouveau checklist | controle qualite avant passage Phase 2 |
| `docs/EPIBENCH_PHASE1_ADJUDICATION_EXAMPLES.md` | nouveau document optionnel mais recommande | exemples de scoring MTS/DSI et claim ceiling |
| SOTA alignment matrix | section spec | indique ADOPT/MAP/EXTEND/DIVERGE pour les references existantes |
| tableau MTS | section spec | rubriques 0/1/2/3 itemisees |
| tableau DSI | section spec | rubriques 0/1/2/3 itemisees |
| claim ceiling matrix | section spec | mapping deterministe vers E0-E4 |
| failure consequence matrix | section spec | impact de chaque sentinel |
| track definitions | section spec | separation D/W/F/E |

## Quality bar

La Phase 1 doit satisfaire un niveau de qualite "jury Q1":

- **Normativite**: une regle doit etre formulable comme condition verifiable.
- **Reproductibilite**: deux reviewers doivent pouvoir appliquer la regle de la meme maniere.
- **Conservatisme scientifique**: en cas d'ambiguite, le protocole doit abaisser le claim, pas l'augmenter.
- **Anti-overclaim**: chaque claim interdit doit etre nomme explicitement.
- **Auditabilite**: toute note MTS/DSI doit etre justifiee par une evidence referencee.
- **Separation des preuves**: qualite dataset, performance modele, failures, latence et claims ne doivent pas etre fusionnes dans un score unique.
- **Compatibilite future**: les decisions de Phase 1 doivent pouvoir etre encodees en YAML et JSON Schema en Phase 2.
- **Non-reinvention**: toute nouvelle regle EpiBench doit adopter, mapper, etendre ou justifier sa divergence par rapport au SOTA existant.

## Work Package 0 - Ancrage SOTA et non-reinvention

### Objectif

Empecher EpiBench de reinventer ce que la communaute a deja defini correctement.

EpiBench doit etre construit comme une couche d'evidence governance au-dessus ou a cote des standards existants, pas comme un remplacement gratuit de frameworks etablis.

### Principe

Avant d'ajouter une metrique, une regle de reporting, un champ de result bundle, une gate clinique ou une exigence IoT, on doit repondre:

```text
Existe-t-il deja une reference fiable que nous devons adopter ou mapper?
```

Si oui, EpiBench doit choisir l'une des quatre relations:

| Relation | Signification |
| --- | --- |
| ADOPT | EpiBench reprend directement la regle, metrique ou terminologie |
| MAP | EpiBench accepte la sortie existante et la mappe vers un champ EpiBench |
| EXTEND | EpiBench ajoute une couche de preuve non couverte |
| DIVERGE | EpiBench diverge, avec justification explicite |

### Sources SOTA minimales a integrer

| Source | Usage EpiBench |
| --- | --- |
| ILAE seizure classification | vocabulaire clinique des types de crises |
| SzCORE / event-based scoring | metriques evenementielles et FAR/day si compatibles |
| TUSZ / Temple EEG tooling | contexte EEG detection, annotation, evaluation |
| CHB-MIT | dataset EEG historique pour exemples/evidence cards |
| SeizeIT2 | dataset wearable multimodal focal epilepsy |
| My Seizure Gauge | dataset wearable longitudinal pour forecasting |
| TRIPOD+AI | reporting model development/validation |
| STARD-AI | diagnostic accuracy studies using AI |
| DECIDE-AI | early-stage live clinical evaluation of AI decision support |
| SPIRIT-AI / CONSORT-AI | prospective trial protocol/reporting, uniquement si Phase E4 |
| FUTURE-AI | trustworthy/deployable healthcare AI principles |
| FDA CDS guidance | prudence reglementaire autour des alertes critiques et signaux medicaux |

### Taches

1. Creer une section "SOTA alignment and non-reinvention rule" dans `EPIBENCH_SPEC_V1.md`.
2. Definir le vocabulaire `ADOPT`, `MAP`, `EXTEND`, `DIVERGE`.
3. Ajouter une table des sources SOTA minimales et leur role.
4. Ajouter une exigence de `SOTA registry` pour Phase 2.
5. Relier les metriques event-based existantes a EpiBench au lieu de les renommer inutilement.
6. Documenter ce qu'EpiBench ajoute vraiment: Evidence Card, MTS/DSI, claim gates, failure preservation, embedded viability, result bundles.
7. Ajouter une review checklist SOTA.

### Output

- Section SOTA dans `docs/EPIBENCH_SPEC_V1.md`.
- Table ADOPT/MAP/EXTEND/DIVERGE.
- Requirement `sota_registry_entries` pour Phase 2.
- Checklist de review SOTA.

### Definition of Done

- Aucune metrique EpiBench n'est introduite sans comparaison a une reference existante.
- SzCORE-style event scoring est explicitement reutilise ou mappe quand compatible.
- TRIPOD+AI, STARD-AI, DECIDE-AI, CONSORT-AI/SPIRIT-AI et FUTURE-AI sont positionnes correctement.
- Les sources SOTA utilisees ont un statut de citation integrity.
- EpiBench est formule comme couche complementaire, pas concurrent gratuit.

### Tests et validation

- Pour chaque nouvelle regle Phase 1, indiquer ADOPT/MAP/EXTEND/DIVERGE.
- Verifier qu'aucune divergence n'existe sans justification.
- Verifier que les sources SOTA citees existent et correspondent au claim.

### Review

- Review bibliographique: pas de citation fantome, pas de SOTA obsoletement ignore.
- Review methodologique: EpiBench complete les frameworks existants au lieu de les dupliquer.
- Review strategic/Q1: la nouveaute est claire sans pretendre que tout le champ repart de zero.

## Work Package 1 - Normaliser le vocabulaire de preuve

### Objectif

Stabiliser le langage EpiBench avant de construire les rubriques.

### Taches

1. Definir les termes normatifs:
   - `dataset evidence`;
   - `algorithm behavior`;
   - `claim eligibility`;
   - `claim ceiling`;
   - `fail-closed`;
   - `failure trace`;
   - `sentinel`;
   - `track`;
   - `result bundle`;
   - `scientific certification`.
2. Interdire les termes ambigus:
   - `clinical certification`;
   - `clinically approved`;
   - `safe model`;
   - `universal clinical standard`;
   - `real-time` sans definition hardware;
   - `generalizable` sans split et validation externe.
3. Ajouter une section "Normative language" dans `EPIBENCH_SPEC_V1.md`.
4. Ajouter une section "Forbidden interpretations" dans `EPIBENCH_PROTOCOL.md`.

### Output

Une mini-ontologie EpiBench, stable et citables dans le papier.

### Definition of Done

- Chaque terme cle a une definition d'une ou deux phrases.
- Les termes interdits ont une alternative recommandee.
- Aucun terme ne laisse croire qu'EpiBench remplace une evaluation clinique prospective.

### Tests et validation

- Search textuel dans les docs pour `clinical certified`, `clinically certified`, `safe`, `ready`, `universal`.
- Toute occurrence doit etre soit interdite explicitement, soit reformulee.

### Review

- Review scientifique: verifier que les termes ne permettent pas d'overclaim.
- Review clinique: verifier que les termes ne suggerent pas une validation medicale.

## Work Package 2 - Construire les rubriques MTS

### Objectif

Transformer le Metrological Trustworthiness Score en grille de scoring reproductible.

### Principe

MTS mesure la qualite metrologique de la preuve. Il ne mesure pas la diversite du domaine ni la performance du modele.

MTS repond a la question:

> Les donnees et labels sont-ils assez fiables pour soutenir le type de preuve revendique?

### Items MTS obligatoires

1. Source officielle et version stable.
2. Licence et conditions d'acces.
3. Raw signals disponibles ou transformation raw-to-canonical auditable.
4. Checksums et provenance.
5. Protocole d'acquisition.
6. Type de capteur et placement.
7. Sampling rate et resolution.
8. Synchronisation temporelle.
9. Calibration ou specification instrumentale.
10. Annotateur et qualification.
11. Onset disponible.
12. Offset disponible.
13. Incertitude temporelle label.
14. Taxonomie des crises.
15. Nombre de patients.
16. Nombre de crises.
17. Duree interictale.
18. Missing data quantifiee.
19. Artifacts quantifies.
20. Split manifest disponible.
21. Raw-to-processed pipeline reproductible.

### Rubrique generique 0/1/2/3

| Score | Definition generale |
| --- | --- |
| 0 | absent, non documente, contradictoire ou impossible a verifier |
| 1 | present mais faible, incomplet, infere ou non auditable |
| 2 | documente et utilisable, mais limite pour des claims forts |
| 3 | complet, traçable, versionne, verifiable et adapte au claim vise |

### Rubrique itemisee attendue

Chaque item MTS doit etre detaille sous ce format:

```text
Item: onset availability
0 = aucun onset exploitable ou source contradictoire
1 = onset approximatif, derive, non verifie ou uniquement proxy
2 = onset disponible, source documentee, mais incertitude non bornee ou non adjudiquee
3 = onset neurologue/expert ou video-EEG confirme, source tracee, incertitude bornee
Fail-closed: si onset absent, detection/early warning claim max E1
Evidence required: annotation file, data dictionary, audit row, source reference
```

### Sortie MTS

Produire:

```text
MTS_raw = sum(item_scores)
MTS_max = 3 * n_items
MTS_scaled = 100 * MTS_raw / MTS_max
MTS_tier_candidate = T1/T2/T3 according to thresholds
```

### Regles MTS fail-closed

Certaines conditions doivent bloquer T1 ou E2+, meme si le score numerique est eleve:

| Condition | Effet |
| --- | --- |
| licence non claire | dataset non certifiable publiquement |
| labels non auditables | claim max E1 |
| onset absent pour detection | track D claim max E1 |
| split manifest absent | claim max E1 |
| raw-to-processed non traceable | T1 interdit |
| duree interictale insuffisante | low-FAR claim interdit |
| missingness non quantifiee | T1 interdit |

### Definition of Done

- Les 21 items MTS ont une rubrique 0/1/2/3.
- Chaque item a un champ `Evidence required`.
- Chaque item indique s'il peut declencher un fail-closed.
- Le calcul MTS est explicitement donne.
- La difference entre score numerique et fail-closed est claire.

### Tests et validation

- Appliquer la grille a un dataset fictif T1.
- Appliquer la grille a un dataset fictif T2.
- Appliquer la grille a un dataset fictif T3.
- Verifier que les fail-closed bloquent correctement un dataset avec bon score mais labels non auditables.

### Review

- Review metrologique: les items capturent-ils vraiment la qualite de mesure?
- Review clinique: les labels onset/offset et la taxonomie sont-ils correctement ponderes?
- Review reproducibility: les preuves requises sont-elles verifiables?

## Work Package 3 - Construire les rubriques DSI

### Objectif

Transformer le Domain Stress Index en grille reproductible qui mesure la diversite et la difficulte du domaine.

### Principe

DSI ne mesure pas la qualite des labels. DSI mesure le stress de generalisation.

DSI repond a la question:

> Le dataset teste-t-il assez de variabilite clinique, capteur et contexte pour soutenir le claim vise?

### Items DSI obligatoires

1. Diversite patients.
2. Age.
3. Sexe.
4. Epilepsy syndrome ou phenotype clinique.
5. Types de crises.
6. Convulsif versus non convulsif.
7. Nocturne versus diurne.
8. Sleep versus wake.
9. Hospitalier versus domicile.
10. Mouvement et activites de vie reelle.
11. Artifacts physiologiques et capteurs.
12. Multi-capteurs.
13. Cross-device.
14. Multi-site.
15. Long-term monitoring.
16. Medication/context metadata.
17. Patient-independent split possible.
18. Leave-site-out ou external validation possible.
19. Prospective setting possible.
20. Real wearable placement variability.

### Rubrique generique 0/1/2/3

| Score | Definition generale |
| --- | --- |
| 0 | dimension absente ou non documentee |
| 1 | dimension presente marginalement, non equilibree ou non stratifiable |
| 2 | dimension presente, analysable, mais limitee |
| 3 | dimension substantiellement couverte, stratifiable et pertinente pour le claim |

### Rubrique itemisee attendue

Exemple:

```text
Item: home versus hospital context
0 = contexte non documente ou uniquement artificiel
1 = contexte documente mais unique, ex. hospital-only
2 = plusieurs contextes ou ambulatoire partiel, mais stratification limitee
3 = hospital + home/ambulatory documentes, stratifiables, avec durees suffisantes
Claim effect: home deployment claim interdit si score < 2
Evidence required: recording context metadata, site/protocol description
```

### Regles DSI

- DSI eleve ne peut jamais compenser MTS faible.
- DSI faible limite les claims externes, meme si MTS est eleve.
- E3 requiert au minimum DSI medium sur les dimensions pertinentes au claim.
- Home deployment claim requiert evidence home/ambulatory.
- Cross-device claim requiert cross-device evidence.
- Multi-site claim requiert site metadata et split site-aware.

### Definition of Done

- Les 20 items DSI ont une rubrique 0/1/2/3.
- Chaque item a un effet potentiel sur claims ou forbidden claims.
- Les dimensions DSI pertinentes par track sont identifiees.
- Une table montre comment DSI limite E3.

### Tests et validation

- Dataset hospitalier propre mais monosite: MTS peut etre haut, DSI limite E3.
- Dataset home riche mais labels faibles: DSI peut etre haut, MTS limite E2+.
- Dataset wearable multi-capteurs mais sans patient-independent split: DSI ne doit pas autoriser E2-PI.

### Review

- Review clinique: les dimensions capturent-elles la variabilite epilepsie pertinente?
- Review IoT: les dimensions capteur, placement, artifacts, missingness sont-elles suffisantes?

## Work Package 4 - Definir les tiers dataset T1/T2/T3

### Objectif

Relier MTS, DSI et fail-closed a des tiers dataset clairs.

### Principe

Le tier dataset n'est pas un jugement de valeur sur les auteurs du dataset. C'est un jugement sur ce que le dataset permet de prouver dans EpiBench.

### Tiers attendus

| Tier | Definition |
| --- | --- |
| T1 | dataset cliniquement fort, traceable, labels experts, onset/offset exploitables, split clair, limitations documentees |
| T2 | dataset utile mais incomplet, exploitable pour claims etroits sous conditions |
| T3 | dataset exploratoire, inventaire ou preuve structurelle seulement |

### Regles proposees

```text
T1 candidate: MTS >= 80 and no T1-blocking fail-closed
T2 candidate: MTS >= 60 and no certification-blocking failure
T3 candidate: MTS < 60 or exploratory-only evidence
```

DSI ne definit pas directement T1/T2/T3, mais limite les claims de generalisation.

### Definition of Done

- T1/T2/T3 sont derives de regles explicites.
- Les fail-closed peuvent abaisser le tier ou limiter le claim.
- Le role de DSI est separe de MTS.
- Une table donne `dataset tier -> default claim ceiling`.

### Tests et validation

- Dataset MTS 85 mais labels non auditables: T1 interdit.
- Dataset MTS 82, DSI faible: T1 possible mais E3 interdit.
- Dataset MTS 58, DSI haut: T3 ou T2-conditional, claim max E1/E2 tres etroit.

### Review

- Reviewer externe doit comprendre qu'un T2 peut etre scientifiquement utile.
- Reviewer clinique doit valider que T1 ne promet pas E4 par lui-meme.

## Work Package 5 - Separations des tracks D/W/F/E

### Objectif

Eviter la confusion entre detection, early warning, forecasting et embedded viability.

### Tracks

| Track | Nom | Question | Unite principale | Claim interdit si absent |
| --- | --- | --- | --- | --- |
| D | Detection | detecter une crise presente ou proche onset | event detection | forecasting claim |
| W | Early warning | alarmer avant une fenetre utile | alarm episode + lead time | detection-only claim comme warning |
| F | Forecasting | estimer risque futur SPH/SOP | calibrated risk window | detection claim direct |
| E | Embedded viability | executer sur contrainte IoT | latency/memory/energy | real-time/edge claim |

### Sorties par track

Track D:

- event sensitivity;
- false alarms/24h;
- detection delay;
- event precision/F1;
- missed seizures;
- per-patient distribution.

Track W:

- event warning sensitivity;
- useful warning lead time;
- false warnings/24h;
- time-in-warning;
- alarm burden;
- missed useful warning.

Track F:

- SPH/SOP definition;
- event sensitivity under alarm budget;
- time-in-warning;
- Brier score;
- ECE;
- calibration curve;
- right-censoring report.

Track E:

- p50/p95 runtime;
- RAM;
- CPU;
- energy proxy or measured energy;
- storage;
- connectivity dependency;
- causal streaming feasibility.

### Definition of Done

- Chaque track a une question scientifique.
- Chaque track a metriques primaires et secondaires.
- Chaque track a claims autorises et claims interdits.
- Un result bundle doit declarer son track.
- Un meme modele evalue sur deux tracks produit deux verdicts separes.

### Tests et validation

- Un result de forecasting ne peut pas etre certifie comme detection sans outputs event detection.
- Un result detection ne peut pas revendiquer early warning sans lead-time positif et definition utile.
- Un result non mesure hardware ne peut pas obtenir claim E.

### Review

- Review clinique: les distinctions D/W/F correspondent-elles a des usages reels?
- Review ML: les metrics par track sont-elles compatibles avec outputs existants?

## Work Package 6 - Clarifier le claim ladder E0/E1/E2-PD/E2-PI/E3/E4

### Objectif

Supprimer l'ambiguite de E2 dans le draft initial.

### Claim ladder normatif

| Claim | Nom court | Definition | Exemples autorises |
| --- | --- | --- | --- |
| E0 | no claim | artefact non probant | mock data, run incomplet |
| E1 | structural validity | pipeline/protocole fonctionne | labels/splits/test logic valides sur donnees non claimables |
| E2-PD | patient-dependent narrow operation | claim intra-patient ou personnalise | "within-patient detection under this dataset and sensor" |
| E2-PI | patient-independent narrow operation | claim nouveaux patients dans domaine borne | "patient-independent detection on this dataset/sensor/seizure scope" |
| E3 | external generalization | claim externe/multisite | "generalizes across dataset/site under declared scope" |
| E4 | prospective clinical-grade evidence | evidence prospective et clinique | "prospectively validated under intended-use protocol" |

### Regles minimales

- E0 si mock/synthetic uniquement, labels absents, result bundle incomplet.
- E1 si pipeline structurel valide mais evidence clinique insuffisante.
- E2-PD requiert split patient-dependent correct, labels audites, FAR/day, failures, pas de leakage.
- E2-PI requiert patient-independent split, labels audites, FAR/day, failures, pas de leakage.
- E3 requiert E2-PI + external dataset, cross-site ou leave-site-out.
- E4 requiert prospective evidence, clinician-adjudicated ground truth, intended-use protocol et risk analysis.

### Definition of Done

- Chaque claim a conditions necessaires.
- Chaque claim a phrases autorisees et interdites.
- E2-PD et E2-PI sont separes partout.
- E4 est explicitement hors de portee des datasets publics retrospectifs seuls.

### Tests et validation

- Patient-dependent only: E2-PD max.
- Patient-independent no external: E2-PI max.
- External validation failed: E3 interdit.
- Prospective absent: E4 interdit.

### Review

- Review clinique obligatoire pour E4 wording.
- Review scientific reproducibility pour E2-PD/E2-PI.

## Work Package 7 - Construire la claim ceiling matrix

### Objectif

Construire une matrice deterministe:

```text
claim_ceiling = min(dataset_ceiling, split_ceiling, label_ceiling, failure_ceiling, validation_ceiling, hardware_ceiling, track_ceiling)
```

### Dimensions

1. Dataset tier.
2. MTS fail-closed.
3. DSI domain coverage.
4. Track.
5. Split.
6. Label audit.
7. Failure status.
8. External validation.
9. Prospective evidence.
10. Hardware evidence.

### Table minimale attendue

| Condition | Max claim |
| --- | --- |
| mock/synthetic only | E0/E1 |
| dataset T3 | E1 |
| labels unaudited | E1 |
| leakage detected | E1 |
| patient-dependent only | E2-PD |
| patient-independent, no external | E2-PI |
| patient-independent + external | E3 |
| prospective clinical evidence | E4 candidate |
| no hardware report | no edge/real-time claim |

### Definition of Done

- La matrice couvre tous les claims.
- La logique `min ceiling` est explicite.
- Les conditions bloquantes sont prioritaires sur les scores.
- Les claims interdits sont generes avec raison.

### Tests et validation

Construire au moins 8 scenarios de validation:

1. mock data complete -> E1 max.
2. T3 real dataset -> E1 max.
3. T2 patient-dependent clean -> E2-PD.
4. T2 patient-independent clean -> E2-PI.
5. T1 patient-independent + external -> E3.
6. T1 retrospective only -> E4 interdit.
7. leakage failure -> E1 max.
8. missing failure trace -> Run-Complete bloque.

### Review

- Reviewer externe doit pouvoir appliquer la matrice sans demander aux auteurs.

## Work Package 8 - Relier failures et sentinels aux consequences

### Objectif

Faire des failures des observations scientifiques, pas des notes de bas de page.

### Sentinel consequence matrix

Chaque sentinel doit definir:

- detection condition;
- severity;
- score impact;
- claim impact;
- required report field;
- whether run is invalidated;
- whether badge is blocked.

### Sentinels minimales

- `PREDICTION_MISSING`
- `SEGMENT_CRASH`
- `NAN_OR_INF_OUTPUT`
- `LATENCY_BUDGET_EXCEEDED`
- `POST_EVENT_ALARM`
- `FAR_EXPLOSION`
- `PATIENT_LEAKAGE`
- `TEMPORAL_LEAKAGE`
- `SPLIT_NONCOMPLIANT`
- `LABEL_UNAUDITED`
- `DEVICE_MISSINGNESS`
- `HARDWARE_UNMEASURED`

### Exemple attendu

```text
Sentinel: TEMPORAL_LEAKAGE
Severity: critical
Score impact: score not reportable as certified performance
Claim impact: E2+ blocked, max claim E1
Badge impact: Leakage-Checked blocked
Required report: affected patients, recordings, windows, leakage mechanism
Resolution: fix split or preprocessing; rerun
```

### Definition of Done

- Toutes les sentinels ont consequences explicites.
- Les leakage sentinels bloquent E2+.
- Missing failure trace bloque Run-Complete.
- Hardware unmeasured bloque real-time/edge claims.
- Les failures sont incluses dans le denominator ou dans un failure denominator specifique.

### Tests et validation

- Scenario avec NaN output: run partiellement invalide.
- Scenario avec patient missing: failure rate non nul et claim baisse si seuil depasse.
- Scenario avec FAR explosion: safety axis penalise et claim low false positives interdit.

### Review

- Review engineering: les conditions sont detectables par code en Phase 3/4.
- Review scientifique: les consequences sont proportionnees.

## Work Package 9 - Redefinir le worked example de Phase 1

### Objectif

Preparer l'exemple pedagogique qui demontrera la valeur du protocole.

### Contenu attendu

Le worked example doit contenir:

- dataset evidence summary;
- naive leaderboard;
- event-based leaderboard;
- failure-aware table;
- claim-gated ranking;
- interpretation.

### Table minimale

| Model | Naive rank | Event rank | Failure status | EpiBench claim | Why claim changes |
| --- | ---: | ---: | --- | --- | --- |
| A | 1 | 1 | FAR explosion | E1/E2 blocked | high sensitivity but unsafe alarm burden |
| B | 2 | 3 | clean | E2-PI | moderate score, stronger evidence |
| C | 3 | 2 | hardware measured | E2-PI + edge | operationally stronger |
| D | 4 | 4 | clean baseline | E1 | sanity floor |

### Definition of Done

- L'exemple montre que le meilleur score naive ne gagne pas forcement.
- L'exemple montre au moins une failure preservee.
- L'exemple montre au moins un claim interdit.
- L'exemple est compatible avec les tracks D/W/F/E.

### Tests et validation

- Un lecteur doit pouvoir expliquer en une phrase pourquoi le ranking change.
- Aucun chiffre ne doit etre presente comme resultat reel si l'exemple est illustratif.

### Review

- Review communication: l'exemple est clair pour un jury.
- Review anti-overclaim: aucune conclusion clinique excessive.

## Work Package 10 - Plan de review et adjudication

### Objectif

Mettre en place une review de Phase 1 avant de passer a la Phase 2.

### Reviewers recommandes

| Reviewer | Role |
| --- | --- |
| Scientific owner | coherence globale EpiBench/BSEBench |
| Clinical reviewer | labels, seizure taxonomy, intended use, clinical wording |
| Reproducibility reviewer | rubriques, split logic, claim gates |
| IoT reviewer | latency, edge, sensor missingness, hardware claims |
| External dry-run reviewer | applicabilite sans aide des auteurs |

### Review checklist

1. Les rubriques MTS sont-elles appliquees de maniere reproductible?
2. Les rubriques DSI separent-elles bien stress du domaine et qualite metrologique?
3. Les tracks D/W/F/E sont-ils non ambigus?
4. E2-PD et E2-PI sont-ils separes partout?
5. Les failures critiques bloquent-elles les claims appropries?
6. Les claims interdits sont-ils explicites?
7. Le protocole reste-t-il utile meme avec des resultats faibles?
8. Les termes "certification" et "clinical" sont-ils correctement bornes?
9. La Phase 2 peut-elle encoder ces decisions en YAML/schema?

### Definition of Done

- Toutes les reviews ont un statut: `PASS`, `PASS_WITH_MINOR_REVISIONS`, `BLOCKED`.
- Aucun `BLOCKED` ne reste ouvert.
- Les divergences entre reviewers sont adjudiquees dans un log.
- La decision "go to Phase 2" est documentee.

### Output

Un document `docs/EPIBENCH_PHASE1_REVIEW_CHECKLIST.md` avec:

- checklist;
- reviewer;
- decision;
- notes;
- blocking issues;
- resolution.

## Plan de tests de la Phase 1

La Phase 1 etant principalement normative/documentaire, les tests sont des tests de coherence, d'adjudication et de falsification.

### Test 1 - Reproductibilite inter-reviewer

Procedure:

1. Donner la meme Evidence Card fictive a deux reviewers.
2. Chaque reviewer score MTS et DSI.
3. Comparer MTS, DSI, tier et claim ceiling.

Acceptance:

- difference MTS <= 5 points;
- difference DSI <= 8 points;
- meme dataset tier;
- meme claim ceiling.

### Test 2 - Fail-closed labels

Scenario:

- dataset riche;
- MTS numerique eleve;
- labels non auditables.

Acceptance:

- T1 interdit;
- claim max E1;
- raison explicite: `labels unaudited`.

### Test 3 - Patient-dependent ambiguity

Scenario:

- performance forte;
- split patient-dependent seulement;
- no leakage;
- labels audites.

Acceptance:

- E2-PD possible;
- E2-PI interdit;
- E3 interdit;
- phrase "generalizes to new patients" interdite.

### Test 4 - External validation gate

Scenario:

- T1;
- patient-independent split;
- no external validation.

Acceptance:

- E2-PI max;
- E3 interdit avec raison.

### Test 5 - Hardware claim gate

Scenario:

- model reports "real-time";
- no hardware report.

Acceptance:

- real-time claim interdit;
- Edge-Measured interdit;
- Track E non certifie.

### Test 6 - Failure preservation

Scenario:

- 5% patients missing predictions.

Acceptance:

- failure trace obligatoire;
- survivor-only average interdit sans caveat;
- stability ou robustness impact defini.

### Test 7 - Track separation

Scenario:

- forecasting SPH/SOP outputs;
- no event detection outputs.

Acceptance:

- Track F certifiable si conditions remplies;
- Track D claim interdit.

### Test 8 - Anti-overclaim language

Procedure:

Search dans les docs:

- `clinical-ready`;
- `clinically certified`;
- `safe`;
- `detects epilepsy`;
- `generalizable`;
- `real-time`.

Acceptance:

- chaque occurrence est soit dans une section "forbidden", soit accompagnee de conditions strictes.

## Validation scientifique finale

La Phase 1 doit se terminer par un "Phase 1 closeout" contenant:

```text
Phase 1 status: PASS / BLOCKED
SOTA alignment: PASS
MTS rubrics: PASS
DSI rubrics: PASS
Track separation: PASS
Claim ladder: PASS
Claim ceiling matrix: PASS
Failure consequence matrix: PASS
Worked example: PASS
Clinical wording: PASS
Ready for Phase 2: YES/NO
```

## Critere de passage a la Phase 2

On passe a la Phase 2 uniquement si:

- les rubriques sont suffisamment precises pour etre encodees;
- les claim gates sont suffisamment deterministes pour etre testes;
- les fields necessaires aux schemas sont identifies;
- les contradictions entre protocole, roadmap et publication proposal sont resolues;
- le superviseur clinique ou son proxy a valide le wording des claims cliniques.

## Risques majeurs de Phase 1

| Risque | Consequence | Mitigation |
| --- | --- | --- |
| Rubriques trop subjectives | standard non reproductible | exemples d'adjudication + inter-reviewer test |
| Trop de rigidite | adoption difficile | claims gradues, T2 utile, warnings non bloquants |
| Trop de souplesse | leaderboard illusion | fail-closed et claim ceiling |
| Confusion detection/forecasting | reviewers attaquent la validite | tracks D/W/F/E |
| Certification mal comprise | risque clinique/reglementaire | wording strict scientific certification |
| E2 ambigu | overclaim generalisation | scission E2-PD/E2-PI |
| Failures decoratives | meme probleme que leaderboard | consequences mecaniques |

## Timeline proposee pour Phase 1

Version intensive: 5 jours ouvrables.

| Jour | Objectif |
| --- | --- |
| J1 | vocabulaire normatif + MTS draft |
| J2 | DSI draft + dataset tier rules |
| J3 | tracks D/W/F/E + claim ladder |
| J4 | claim ceiling matrix + failure consequence matrix |
| J5 | worked example + review checklist + closeout |

Version prudente: 2 semaines.

| Periode | Objectif |
| --- | --- |
| S1-J1/J2 | MTS/DSI rubrics |
| S1-J3/J4 | tracks + claims |
| S1-J5 | failure consequences |
| S2-J1/J2 | worked examples |
| S2-J3 | review externe |
| S2-J4 | adjudication |
| S2-J5 | closeout |

## Ordre d'execution recommande

1. Creer `docs/EPIBENCH_SPEC_V1.md` avec squelette Phase 1.
2. Ajouter SOTA alignment et non-reinvention rule.
3. Ajouter vocabulaire normatif.
4. Ajouter MTS rubrics.
5. Ajouter DSI rubrics.
6. Ajouter dataset tiers.
7. Ajouter tracks D/W/F/E.
8. Ajouter claim ladder.
9. Ajouter claim ceiling matrix.
10. Ajouter sentinel consequence matrix.
11. Ajouter worked examples.
12. Creer review checklist.
13. Aligner `EPIBENCH_PROTOCOL.md`.
14. Faire closeout.

## Mode de decision

En cas de conflit entre ambition et prudence:

- choisir la prudence pour les claims;
- choisir la precision pour les rubriques;
- choisir la transparence pour les failures;
- choisir la compatibilite future pour les schemas;
- choisir la valeur scientifique plutot que l'effet marketing.

## Phrase de sortie attendue

La Phase 1 est reussie lorsque l'on peut dire:

> EpiBench v1.0 dispose maintenant d'un modele de preuve normatif: la qualite dataset, le stress domaine, le type de split, les failures, les tracks et les claims sont definis de maniere suffisamment deterministe pour etre encodes en YAML, schemas et CLI lors de la Phase 2.
