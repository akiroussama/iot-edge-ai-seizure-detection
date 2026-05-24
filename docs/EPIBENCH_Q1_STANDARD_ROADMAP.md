# EpiBench Roadmap: From Protocol Draft To Community-Ready Scientific Standard

Date: 2026-05-24  
Statut: roadmap stratégique et technique pour transformer `EPIBENCH_PROTOCOL.md` en standard scientifique publiable.  
Ambition: paper Q1 + reference implementation + adoption communautaire immédiate.  
Principe directeur: le score ne vaut que par le protocole qui définit ce qu'il a le droit de prouver.

## Thèse centrale

EpiBench ne doit pas être présenté comme un leaderboard de détection de crises, ni comme un nouvel algorithme de seizure detection. EpiBench doit être présenté comme une infrastructure de preuve qui répond à une question plus fondamentale:

> Que peut-on légitimement revendiquer à partir d'un dataset, d'un protocole de labels, d'un split, d'un modèle, d'un budget d'alarme, d'une latence et d'une trace d'échec donnés?

La contribution attendue n'est donc pas "notre modèle détecte mieux les crises". La contribution attendue est:

> EpiBench transforme les résultats de détection, d'alerte précoce et de forecasting de crises en evidence packages auditables, reproductibles et bornés par des niveaux de claim explicites.

## Avertissement de certification

Le mot "certification" doit être utilisé avec précision.

`EpiBench-certified` ne signifie pas `clinically approved`.  
`EpiBench-certified` ne signifie pas dispositif médical validé.  
`EpiBench-certified` ne remplace pas une validation prospective, une évaluation réglementaire, un essai clinique, une analyse de risque ou une autorisation de mise sur le marché.

`EpiBench-certified` signifie uniquement:

> Ce résultat est scientifiquement certifié selon EpiBench v1.0: les données, les labels, les splits, les métriques, les failures, le score, la latence, les artefacts et les claims ont été vérifiés par un protocole public, versionné et reproductible.

Cette distinction est indispensable pour un paper Q1. Elle protège le projet contre deux dangers:

- l'overclaim clinique;
- la confusion entre benchmark scientifique et certification réglementaire.

## Positionnement BSEBench-like

BSEBench partait d'un constat: un RMSE seul ne prouve rien si le protocole expérimental n'est pas traçable. EpiBench part du même principe:

> Une accuracy, une sensitivity, un F1, un AUROC ou un false alarm rate ne sont pas une preuve si le dataset, les labels, les splits, les failures, la latence et le contexte d'usage ne sont pas audités.

Le parallélisme méthodologique est le suivant:

| Principe BSEBench | Transposition EpiBench |
| --- | --- |
| Dataset Evidence Card | Epilepsy Dataset Evidence Card |
| MTS | Metrological Trustworthiness Score for seizure datasets |
| DSI | Domain Stress Index for seizure detection and wearable stress |
| BSE-Score | Epi-Score multi-axes |
| Failure traces | Sentinel and failure-preserving seizure evaluation |
| Claim Eligibility | E0-E4 claim gate with patient-dependent and patient-independent separation |
| Result Bundle | EpiBench Result Bundle |
| Anti-RMSE-only | Anti-accuracy/AUROC-only and anti-leaderboard-only |

La roadmap ci-dessous vise à passer d'un protocole de haut niveau à un standard communautaire utilisable immédiatement après publication.

## Artefacts opérationnels phase 1 à phase 7

Cette roadmap est maintenant reliée à des artefacts exécutables ou directement actionnables:

| Phase | Artefact principal | Rôle |
| --- | --- | --- |
| 1 | `docs/EPIBENCH_SPEC_V1.md` | Spécification normative du modèle de preuve, des tracks, tiers, failures et claims |
| 2 | `configs/epibench/epibench_v1.yaml` + `schemas/epibench/*.schema.json` | Single source of truth machine-readable |
| 3 | `docs/EPIBENCH_PHASE3_CERTIFICATION_STANDARD.md` | Règles de certification scientifique, badges et claim gates |
| 4 | `src/epibench/*` + `scripts/epibench.py` | Reference implementation exécutable |
| 5 | `examples/epibench/*` + `reports/epibench_*_claim.*` | Evidence packages et worked example avant/après protocole |
| 6 | `docs/EPIBENCH_PHASE6_Q1_PAPER_STRATEGY.md` | Stratégie de manuscrit Q1 et défense reviewer |
| 7 | `docs/EPIBENCH_PHASE7_GOVERNANCE_ADOPTION.md` + issue templates | Gouvernance, adoption, versioning et release candidate |
| Transversal | `configs/epibench/conformance_suite_v1.yaml` | Suite de conformité prouvant que les claim gates sont exécutables |

Le document reste une roadmap. Les règles exécutables vivent dans le YAML, les schémas et le CLI.

## Définition du succès

EpiBench v1.0 est considéré comme prêt pour un paper Q1 et pour adoption communautaire si les conditions suivantes sont satisfaites:

1. Le protocole est normatif: il ne laisse pas aux auteurs la liberté de choisir leur claim après coup.
2. Le single source of truth est machine-readable: YAML + JSON Schemas + CLI.
3. Les scores sont calculables sans interprétation humaine ad hoc.
4. Les failures ont des conséquences mécaniques sur les métriques et les claims.
5. Les tracks detection, early warning, forecasting et embedded viability sont séparés.
6. Les claims E2-PD, E2-PI, E3 et E4 sont clairement différenciés.
7. Un result bundle non conforme échoue explicitement.
8. Un exemple public est certifiable en moins de 10 minutes.
9. Le paper reste fort même si les modèles deep learning ne produisent aucun résultat spectaculaire.
10. Un groupe externe peut adopter EpiBench sans contacter les auteurs.

## Faiblesses du draft à corriger explicitement

Le draft `EPIBENCH_PROTOCOL.md` est scientifiquement solide comme cadre conceptuel, mais il doit être durci sur six points avant de devenir un standard BSEBench-like:

1. **MTS/DSI trop subjectifs**  
   Les items sont listés, mais les rubriques 0/1/2/3 ne sont pas encore définies. Deux reviewers pourraient scorer différemment le même dataset.

2. **Epi-Score pas encore entièrement calculable**  
   Les axes et poids existent, mais les fonctions exactes qui transforment sensitivity, FAR/day, latency, failures, calibration et edge metrics en sous-scores ne sont pas encore normatives.

3. **Detection, early warning et forecasting encore trop proches**  
   Les tâches doivent être séparées en tracks, avec métriques et claims propres.

4. **E2 patient-dependent ambigu**  
   Un résultat patient-dependent ne doit jamais être lu comme preuve de généralisation. Il faut scinder E2 en `E2-PD` et `E2-PI`.

5. **Failures pas encore mécaniquement reliées aux claims**  
   Les sentinels sont listés, mais leur effet exact sur les scores et claim gates doit être déterministe.

6. **Worked example encore trop illustratif**  
   L'exemple doit montrer un basculement réel: naive rank, event rank, Epi-Score rank, claim level, failure status.

Les sept phases ci-dessous sont construites pour résoudre ces six faiblesses.

---

# Phase 1 - Durcissement épistémologique du protocole

## Objectif scientifique

Transformer `EPIBENCH_PROTOCOL.md` d'un excellent protocole conceptuel en protocole normatif, c'est-à-dire un protocole capable de produire le même claim ceiling lorsqu'il est appliqué par deux reviewers indépendants au même dataset et au même result bundle.

L'objectif n'est pas d'ajouter plus de texte. L'objectif est de supprimer l'ambiguïté scientifique.

## Justification BSEBench-like

BSEBench n'était pas seulement une liste de métriques batterie. Sa force venait de la séparation entre:

- qualité de la donnée;
- comportement de l'algorithme;
- claim autorisé.

EpiBench doit atteindre le même niveau: un résultat ne doit pas pouvoir monter dans le claim ladder uniquement parce qu'il obtient une bonne sensitivity ou un bon F1. Il doit monter uniquement si la donnée, le split, les labels, les failures, la latence et la reproductibilité le permettent.

## Changements normatifs à introduire

### 1. Rubriques MTS 0/1/2/3

Chaque item MTS doit être noté par une rubrique explicite:

| Score | Signification |
| --- | --- |
| 0 | absent, non documenté, non vérifiable ou contradictoire |
| 1 | présent mais faible, incomplet ou seulement inféré |
| 2 | documenté et utilisable, mais avec limites importantes |
| 3 | complet, traçable, versionné, vérifiable et adapté au claim visé |

Exemples d'items à rubricer:

- source officielle et version stable;
- licence et conditions d'accès;
- raw signals disponibles ou transform pipeline auditable;
- protocole d'acquisition;
- type de capteur, placement, sampling rate;
- synchronisation temporelle;
- calibration ou spécification instrumentale;
- annotateur neurologue ou expert;
- onset et offset disponibles;
- incertitude temporelle des labels;
- type de crise selon taxonomie compatible ILAE;
- nombre de patients;
- nombre de crises;
- durée interictale;
- missingness;
- artifacts;
- checksums et traçabilité raw-to-canonical.

### 2. Rubriques DSI 0/1/2/3

Chaque item DSI doit mesurer le stress de domaine:

| Score | Signification |
| --- | --- |
| 0 | domaine non couvert |
| 1 | domaine présent de façon marginale ou non stratifiable |
| 2 | domaine présent et analysable, mais limité |
| 3 | domaine substantiellement couvert, stratifiable et pertinent pour le claim |

Exemples d'items DSI:

- diversité patients;
- âge et sexe;
- types de crises;
- convulsif versus non convulsif;
- nocturne versus diurne;
- hospitalier versus domicile;
- mouvement et artifacts;
- sleep/wake;
- multi-capteurs;
- cross-device;
- multi-site;
- long-term monitoring;
- patient-independent split possible;
- external validation possible;
- prospective setting possible.

### 3. Règles fail-closed

Certains manques ne doivent pas seulement réduire le score; ils doivent bloquer un claim.

Exemples:

| Condition | Effet |
| --- | --- |
| labels non auditables | claim max E1 |
| split non conforme | claim max E1 |
| leakage détecté | E2+ bloqué |
| pas de failure trace | `Run-Complete` bloqué |
| pas de FAR/day | claim "low false positives" interdit |
| pas de latence hardware | claim edge/real-time interdit |
| pas de patient-independent split | E2-PI et E3 interdits |
| pas de validation externe | E3 interdit |
| uniquement rétrospectif public | E4 interdit |

### 4. Séparation des tracks

EpiBench doit séparer les tâches, car elles n'ont pas la même signification clinique.

| Track | Nom | Question scientifique | Exemple de claim autorisé |
| --- | --- | --- | --- |
| D | Detection | Le modèle détecte-t-il un événement ictal après ou près de l'onset? | Détection événementielle sur dataset/capteur/split donné |
| W | Early warning | Le modèle alarme-t-il avant une fenêtre cliniquement utile? | Alerte précoce bornée par délai et FAR/day |
| F | Forecasting | Le modèle estime-t-il un risque dans un horizon SPH/SOP? | Risque calibré pour un horizon donné |
| E | Embedded viability | Le modèle est-il viable sur cible IoT? | Viabilité mesurée sur hardware ou proxy déclaré |

Un modèle peut être évalué sur plusieurs tracks, mais les scores et claims doivent rester séparés.

### 5. Clarification du claim ladder

Le claim ladder doit devenir:

| Claim | Signification |
| --- | --- |
| E0 | no scientific claim |
| E1 | protocol structural validity |
| E2-PD | patient-dependent operational claim |
| E2-PI | patient-independent narrow operational claim |
| E3 | external or multisite generalization research claim |
| E4 | prospective clinical-grade evidence |

Règle critique:

> `E2-PD` n'est pas inférieur moralement à `E2-PI`; il répond simplement à une autre question. Mais `E2-PD` ne doit jamais être formulé comme généralisation à de nouveaux patients.

### 6. Claim ceiling déterministe

Créer une table déterministe:

```text
claim_ceiling = f(dataset_tier, MTS, DSI, track, split, label_audit, failure_status, external_validation, hardware_evidence)
```

Cette table doit être publiée dans `EPIBENCH_SPEC_V1.md` et encodée dans `epibench_v1.yaml`.

## Livrables concrets

- `docs/EPIBENCH_SPEC_V1.md` section normative `Evidence and Claim Model`.
- SOTA alignment matrix indiquant pour chaque reference existante si EpiBench
  l'adopte, la mappe, l'etend ou diverge avec justification.
- Rubriques MTS détaillées.
- Rubriques DSI détaillées.
- Table fail-closed.
- Table des tracks D/W/F/E.
- Claim ladder E0/E1/E2-PD/E2-PI/E3/E4.
- Claim ceiling table.
- Revision de `docs/EPIBENCH_PROTOCOL.md` pour aligner le vocabulaire avec la spec.

## Critères d'acceptation

- Deux reviewers indépendants obtiennent le même tier dataset et le même claim ceiling sur un exemple fourni.
- Chaque claim a des conditions nécessaires explicites.
- Aucun item critique ne repose sur "expert judgment" non encadré.
- Les tracks D/W/F/E sont impossibles à confondre dans les result bundles.
- Le protocole refuse automatiquement les overclaims connus.

## Risques scientifiques

- Rubriques trop strictes: risque de classer presque tous les datasets publics en T2/T3.
- Rubriques trop souples: risque de reproduire l'illusion des leaderboards existants.
- DSI élevé mais MTS faible: risque d'interpréter de la diversité comme de la preuve.
- MTS élevé mais DSI faible: risque d'interpréter un dataset propre mais étroit comme général.

## Décisions à verrouiller

- Seuils MTS: par défaut `T1 >= 80`, `T2 >= 60`, `T3 < 60`, avec fail-closed prioritaire.
- DSI ne doit jamais compenser un MTS faible.
- Un claim E3 requiert validation externe ou leave-site-out.
- Un claim E4 requiert prospective clinical-grade evidence et ne peut pas venir d'un paper rétrospectif public seul.

## Dépendances

- `docs/EPIBENCH_PROTOCOL.md`
- `docs/PUBLICATION_PROPOSAL.md`
- `docs/HUMAN_LABEL_AUDIT_PROTOCOL.md`
- modules existants de split, event metrics, leakage audit et failure taxonomy.

## Sortie attendue

Un protocole qui ne se contente plus de dire "ce qu'il faut regarder", mais qui produit un verdict scientifique:

```text
Dataset: T2
Track: Detection
Split: patient-independent
Failure status: transparent, non-leakage
Max claim: E2-PI
Forbidden claims: E3, E4, real-time, low false positives if FAR/day absent
```

---

# Phase 2 - Single Source of Truth normatif

## Objectif scientifique

Faire d'EpiBench une source de vérité machine-readable. Le standard ne doit pas dépendre d'une lecture informelle du paper ou du Markdown. Il doit être validable par des schemas et appliqué par un CLI.

## Justification BSEBench-like

Dans un protocole BSEBench-like, la reproductibilité ne repose pas sur la bonne foi. Elle repose sur des artefacts vérifiables:

- config;
- version;
- checksums;
- outputs;
- failure traces;
- règles de claim.

EpiBench doit donc séparer trois niveaux:

1. Le paper explique la philosophie.
2. La spec définit les règles.
3. Le YAML et les JSON Schemas font autorité.

## Principe de gouvernance

Le single source of truth est:

```text
epibench_v1.yaml + JSON Schemas + versioned CLI
```

Le Markdown est explicatif.  
Les schemas sont normatifs.  
Le CLI est exécutoire.

## Livrables concrets

### 1. YAML normatif

Créer `configs/epibench/epibench_v1.yaml`.

Contenu minimal:

```yaml
version: "1.0"
tracks:
  detection:
    id: "D"
  early_warning:
    id: "W"
  forecasting:
    id: "F"
  embedded_viability:
    id: "E"
evidence:
  mts_thresholds:
    t1_min: 80
    t2_min: 60
  dsi_thresholds:
    high_min: 70
    medium_min: 40
claims:
  levels:
    - E0
    - E1
    - E2-PD
    - E2-PI
    - E3
    - E4
score:
  weights:
    performance: 0.20
    clinical_safety: 0.25
    robustness: 0.15
    stability: 0.10
    latency: 0.10
    embedded_viability: 0.10
    calibration: 0.10
  floor_penalty:
    lambda: 2.0
    floor: 0.35
failure_policy:
  leakage_blocks_e2_plus: true
  missing_failure_trace_blocks_run_complete: true
```

Ce YAML doit devenir la base de tous les calculs de certification.

### 2. JSON Schemas

Créer les schemas suivants:

- `schemas/epibench/dataset_evidence_card.schema.json`
- `schemas/epibench/split_manifest.schema.json`
- `schemas/epibench/result_bundle.schema.json`
- `schemas/epibench/failure_trace.schema.json`
- `schemas/epibench/claim_eligibility.schema.json`
- `schemas/epibench/epibench_score.schema.json`
- `schemas/epibench/hardware_report.schema.json`

Chaque schema doit contenir:

- `schema_version`;
- `created_at`;
- `dataset_id` ou `run_id`;
- `provenance`;
- `checksums` quand applicable;
- `validation_status`;
- `warnings`;
- `failures`;
- champs nécessaires au claim gate.

### 3. Spec normative

Créer `docs/EPIBENCH_SPEC_V1.md`.

Ce document doit expliquer:

- quelles règles sont normatives;
- quels champs sont obligatoires;
- quelles validations sont fail-closed;
- comment versionner la spec;
- comment gérer une rupture de compatibilité;
- comment citer la spec dans un paper.

### 4. Mapping doc-code

Créer une section dans la spec:

```text
Normative source precedence:
1. JSON Schemas
2. epibench_v1.yaml
3. CLI implementation
4. Markdown explanatory docs
5. Paper narrative
```

En pratique, si le paper et le YAML divergent, le YAML versionné et la spec normative prévalent pour la certification.

## Critères d'acceptation

- Un result bundle incomplet échoue à la validation schema.
- Un claim interdit échoue au claim gate.
- Une failure critique bloque automatiquement E2+.
- Le YAML contient tous les poids et seuils utilisés par le score.
- Aucune règle de certification n'est hardcodée uniquement dans le texte du paper.

## Risques scientifiques

- Trop de rigidité peut freiner l'adoption par des équipes externes.
- Trop de souplesse peut rendre la certification non crédible.
- Si les schemas changent trop souvent, la communauté ne saura pas quelle version citer.
- Si le YAML est incomplet, les auteurs pourront retuner le protocole après résultats.

## Décisions à verrouiller

- Toute release du standard doit avoir un numéro de version.
- Les result bundles doivent déclarer la version EpiBench utilisée.
- Un result bundle validé en v1.0 doit rester vérifiable dans le futur.
- Toute modification de poids Epi-Score ou de claim gate doit déclencher au moins une version mineure, voire majeure.

## Dépendances

- Phase 1 pour les rubriques et claim gates.
- Existing schemas under `schemas/`.
- Existing report and artifact package infrastructure.

## Sortie attendue

Un standard qui peut être utilisé sans interprétation:

```powershell
epibench validate-result-bundle results/run_001 --spec configs/epibench/epibench_v1.yaml
epibench certify results/run_001
```

Sortie conceptuelle:

```text
Validation: FAILED
Reason: failure_trace.jsonl missing
Max claim: E1
Blocked badges: Run-Complete, E2-PD, E2-PI, E3, E4
```

---

# Phase 3 - Certification EpiBench et claim gates

## Objectif scientifique

Rendre la certification scientifique explicite, vérifiable et publiable. Le claim final ne doit pas être choisi par l'auteur; il doit être généré par les règles EpiBench.

## Justification BSEBench-like

Dans BSEBench, une donnée T3 ne permet pas une revendication forte, même si un estimateur obtient un bon RMSE. En EpiBench, un modèle ne doit pas obtenir un claim E3 parce qu'il a une bonne sensitivity sur un split patient-dependent.

La certification doit donc fonctionner comme une barrière anti-overclaim.

## Définition de la certification EpiBench

Une certification EpiBench est un verdict versionné:

```text
EpiBench v1.0 Certification
Dataset tier: T2
Track: D
Run completeness: complete
Leakage status: passed
Failure transparency: passed
Epi-Score: 71.4
Claim eligibility: E2-PI
Forbidden claims: E3, E4, clinically approved, real-time
```

## Badges à définir

### Dataset badges

- `EpiBench-Dataset-T1`
- `EpiBench-Dataset-T2`
- `EpiBench-Dataset-T3`

### Run badges

- `EpiBench-Run-Complete`
- `EpiBench-Failure-Transparent`
- `EpiBench-Leakage-Checked`
- `EpiBench-Reproducible-Bundle`

### Claim badges

- `EpiBench-Claim-E1`
- `EpiBench-Claim-E2-PD`
- `EpiBench-Claim-E2-PI`
- `EpiBench-Claim-E3`
- `EpiBench-Claim-E4`

### IoT badges

- `EpiBench-Edge-Profiled`
- `EpiBench-Edge-Measured`
- `EpiBench-Streaming-Feasible`

`Edge-Profiled` peut être obtenu avec estimation CPU/RAM/latence sur environnement contrôlé.  
`Edge-Measured` exige mesure sur hardware cible déclaré.  
`Streaming-Feasible` exige que le pipeline complet respecte causalité, mémoire et latence.

## Règles clés

| Règle | Effet |
| --- | --- |
| pas de patient-independent split | E2-PI interdit |
| pas de validation externe ou leave-site-out | E3 interdit |
| pas de prospective evidence | E4 interdit |
| leakage failure | E2+ interdit |
| pas de failure trace | Run-Complete interdit |
| pas de FAR/day | low-false-positive claim interdit |
| pas de latency report | real-time claim interdit |
| pas de hardware report | Edge-Measured interdit |
| labels non audités | claim max E1 |
| dataset T3 | claim max E1 |

## Claim gate déterministe

Le gate doit suivre une logique conservatrice:

1. Initialiser `max_claim = E4`.
2. Appliquer le ceiling du dataset.
3. Appliquer le ceiling du split.
4. Appliquer le ceiling du label audit.
5. Appliquer les failures bloquantes.
6. Appliquer la présence ou absence d'external validation.
7. Appliquer la présence ou absence de prospective evidence.
8. Appliquer les contraintes track-specific.
9. Retourner le minimum de tous les ceilings.

Important:

> Le claim final est le minimum des preuves disponibles, pas la moyenne des qualités observées.

## Gestion des failures

Chaque sentinel doit avoir un effet:

| Sentinel | Effet minimum |
| --- | --- |
| `PREDICTION_MISSING` | pénalise stability, report obligatoire |
| `SEGMENT_CRASH` | pénalise robustness et stability |
| `NAN_OR_INF_OUTPUT` | run invalid for affected outputs |
| `LATENCY_BUDGET_EXCEEDED` | bloque real-time et Edge-Measured |
| `FAR_EXPLOSION` | pénalise clinical safety, peut bloquer E2+ selon seuil |
| `PATIENT_LEAKAGE` | bloque E2+ |
| `TEMPORAL_LEAKAGE` | bloque E2+ |
| `SPLIT_NONCOMPLIANT` | claim max E1 |
| `LABEL_UNAUDITED` | claim max E1 |
| `HARDWARE_UNMEASURED` | bloque edge/real-time claim |

## Livrables concrets

- `claim_eligibility.schema.json`
- `failure_trace.schema.json`
- `docs/EPIBENCH_CLAIM_GATES.md`
- badge definitions in YAML
- markdown badge renderer
- claim eligibility report template

## Critères d'acceptation

- Le claim final est généré par règles.
- Le report explique chaque blocage.
- Un auteur ne peut pas masquer une failure en supprimant un patient.
- Les badges sont reproductibles.
- Le même result bundle donne le même verdict sur deux machines.

## Risques scientifiques

- Les badges peuvent être interprétés comme validation clinique.
- Des auteurs peuvent cherry-pick un track plus favorable.
- Une certification trop complexe peut réduire l'adoption.
- Une certification trop simple peut devenir un leaderboard déguisé.

## Décisions à verrouiller

- Badge wording: éviter `clinical`, `approved`, `safe`.
- Utiliser `scientifically certified under EpiBench v1.0`.
- Les badges doivent toujours afficher la version.
- Les claims doivent toujours afficher le track.

## Dépendances

- Phase 1 claim ladder.
- Phase 2 schemas and YAML.
- Existing failure taxonomy report infrastructure.

## Sortie attendue

Exemple de badge:

```markdown
![EpiBench Claim](https://img.shields.io/badge/EpiBench_v1.0-Claim_E2--PI-blue)
![Failure Transparent](https://img.shields.io/badge/EpiBench-Failure_Transparent-green)
```

Exemple de verdict:

```text
Requested claim: E3
Granted claim: E2-PI
Blocking reasons:
- no external dataset validation
- no leave-site-out validation
- retrospective evidence only
```

---

# Phase 4 - Reference implementation fonctionnelle

## Objectif scientifique

Fournir un outil que la communauté peut utiliser immédiatement. Un standard sans implémentation devient une recommandation. EpiBench doit être un protocole exécutable.

## Justification BSEBench-like

BSEBench tire sa force de la traçabilité du résultat. Pour EpiBench, la traçabilité doit être rendue concrète:

- un CLI valide les inputs;
- un score est calculé;
- un claim est généré;
- un report est rendu;
- un bundle peut être reproduit.

## Interface CLI minimale

Créer un entrypoint `epibench` avec les commandes suivantes:

```text
epibench validate-dataset-card <path>
epibench validate-split <path>
epibench validate-result-bundle <path>
epibench score <result_bundle>
epibench certify <result_bundle>
epibench render-report <result_bundle>
```

## Comportement attendu des commandes

### `validate-dataset-card`

Valide:

- conformité schema;
- présence MTS/DSI;
- présence des preuves sources;
- licence;
- raw-to-canonical traceability;
- label provenance;
- known limits;
- claim ceiling.

Sortie:

```text
PASS/FAIL
Dataset tier
MTS
DSI
Claim ceiling
Blocking issues
Warnings
```

### `validate-split`

Valide:

- type de split;
- absence de patient overlap;
- absence de temporal overlap;
- absence de recording overlap;
- fit scope;
- threshold scope;
- compatibility with requested claim.

### `validate-result-bundle`

Valide:

- présence des fichiers obligatoires;
- checksums;
- predictions;
- event detections;
- alarm episodes;
- metrics;
- failure traces;
- latency report;
- hardware report si claim edge;
- reproduction command.

### `score`

Calcule:

- sous-scores;
- Epi-Score;
- floor penalty;
- axes faibles;
- sensitivity versus FAR/day;
- per-patient worst-case summary.

### `certify`

Génère:

- claim eligibility;
- badges;
- forbidden claims;
- blocking reasons;
- warning reasons.

### `render-report`

Produit:

- `epibench_certification_report.md`;
- `epibench_score_report.json`;
- `epibench_badges.md`;
- `epibench_failure_summary.md`.

## Sorties attendues

Un result bundle certifié doit produire:

- score report;
- claim eligibility report;
- failure summary;
- badge Markdown;
- audit packet;
- reproducibility manifest;
- machine-readable certification JSON.

## Epi-Score calculable

Le CLI doit transformer les métriques brutes en sous-scores. Exemple de politique à formaliser:

```text
S_perf = weighted_geomean(event_sensitivity_score, event_f1_score, latency_detection_score)
S_safety = weighted_geomean(far_day_score, missed_seizure_score, alarm_burden_score)
S_robust = weighted_geomean(patient_independent_score, subgroup_min_score, artifact_stress_score)
S_stability = weighted_geomean(patient_variance_score, worst_patient_score, failure_rate_score)
S_latency = weighted_geomean(delay_median_score, delay_p95_score, runtime_p95_score)
S_edge = weighted_geomean(ram_score, cpu_score, energy_proxy_score, connectivity_score)
S_cal = weighted_geomean(brier_score_skill, ece_score, abstention_score)
```

Chaque transformation doit être dans `epibench_v1.yaml`, pas cachée dans le code.

## Livrables concrets

- Python package namespace `src/epibench/`.
- CLI entrypoint.
- Schema validator.
- Score engine.
- Claim gate engine.
- Badge renderer.
- Report renderer.
- Example result bundle.
- Minimal documentation page.

## Critères d'acceptation

- Un utilisateur externe peut certifier un exemple en moins de 10 minutes.
- Les commandes échouent avec des messages actionnables.
- Le score est reproductible.
- Les outputs sont machine-readable et human-readable.
- Le CLI ne permet pas de claim implicite non généré.

## Risques scientifiques

- Un CLI trop strict peut bloquer des datasets utiles mais incomplets.
- Un CLI trop permissif peut dégrader la crédibilité du standard.
- L'implémentation peut diverger du paper.
- Les utilisateurs peuvent ne citer que le score sans le claim report.

## Décisions à verrouiller

- Toute sortie `score` doit afficher aussi le `claim eligibility`.
- Toute sortie `certify` doit afficher les forbidden claims.
- Le CLI doit échouer fermé, pas échouer silencieusement.
- Le CLI doit conserver les failures dans les outputs.

## Dépendances

- Phase 2 schemas.
- Phase 3 claim gates.
- Existing metrics, reports and artifact package modules.

## Sortie attendue

Exemple:

```powershell
epibench certify examples/result_bundle_minimal
```

Sortie:

```text
EpiBench v1.0 certification
Status: PASS WITH LIMITATIONS
Track: D
Dataset tier: T2
Epi-Score: 68.2
Granted claim: E2-PI
Forbidden claims: E3, E4, real-time, clinically approved
Blocking issues: no external validation, no hardware measurement
```

---

# Phase 5 - Datasets pilotes et evidence packages

## Objectif scientifique

Démontrer qu'EpiBench fonctionne sur plusieurs réalités expérimentales, pas seulement sur un dataset favorable.

## Justification BSEBench-like

BSEBench montrait que le classement change lorsque l'on préserve les failures et que l'on distingue la qualité de la donnée de la performance algorithmique. EpiBench doit faire la même démonstration dans l'épilepsie:

- un modèle peut gagner en sensitivity mais perdre en claim;
- un dataset peut être propre mais étroit;
- un dataset peut être riche mais mal annoté;
- un résultat peut être intéressant sans être généralisable.

## Datasets pilotes recommandés

### 1. EEG clinique: CHB-MIT ou TUSZ

Rôle:

- ancrage EEG classique;
- comparaison avec littérature existante;
- démonstration event detection;
- mise en évidence des pièges patient-dependent.

Track principal:

- `D`: detection.

Claims possibles:

- E1 à E2-PI selon audit, split et labels.
- E3 seulement avec external validation ou cross-dataset strict.

### 2. Wearable multimodal: SeizeIT2

Rôle:

- ancrage IoT/wearable;
- multimodalité EEG behind-the-ear, ECG, EMG, ACC/GYR;
- stress capteur et réalités ambulatoires.

Tracks:

- `D`: detection;
- `W`: early warning si défini;
- `E`: embedded viability si profil hardware.

### 3. Longitudinal wearable: MSG ou équivalent

Rôle:

- temporalité longue;
- risque/forecasting;
- cycles patients;
- calibration et alarm burden.

Track:

- `F`: forecasting SPH/SOP.

Prudence:

- ne pas mélanger directement avec detection.
- ne pas overclaim si labels onset-only ou matching incomplet.

## Evidence package par dataset

Chaque dataset pilote doit produire:

- Evidence Card complète;
- MTS;
- DSI;
- dataset tier;
- claim ceiling;
- split manifest;
- label audit report;
- missingness report;
- artifact report;
- baseline suite;
- result bundle;
- claim eligibility report;
- limitations report.

## Baseline suite minimale

Pour chaque dataset, exécuter au minimum:

- always negative;
- random/prevalence alarm;
- rate-matched random;
- simple sensor threshold;
- transparent ML baseline;
- compact deep baseline;
- streaming IoT baseline si pertinent.

## Worked example obligatoire

Le paper doit contenir une démonstration avant/après:

| Model | Naive rank | Event rank | Epi-Score rank | Failure status | Granted claim | Interpretation |
| --- | ---: | ---: | ---: | --- | --- | --- |
| A | 1 | 1 | 4 | FAR explosion | E1 | high sensitivity, clinically unusable alarm burden |
| B | 2 | 3 | 2 | clean | E2-PI | lower sensitivity, stronger evidence |
| C | 3 | 2 | 1 | edge measured | E2-PI + Edge-Measured | best operational profile |
| D | 4 | 4 | 4 | clean | E1 | always-negative control |

Le message doit être:

> Le meilleur modèle naïf n'est pas nécessairement le résultat scientifiquement le plus défendable.

## Critères d'acceptation

- Au moins deux datasets de nature différente sont couverts.
- Au moins un cas montre un changement de classement après EpiBench.
- Au moins un result bundle public est certifiable.
- Les negative results sont conservés.
- Les failures sont visibles dans les tables et figures.
- Les claims sont plus faibles que les scores naïfs lorsque la preuve ne suit pas.

## Risques scientifiques

- Les datasets publics peuvent être insuffisants pour E3.
- Les annotations peuvent limiter les claims.
- Les résultats deep learning peuvent être faibles.
- Les reviewers peuvent demander pourquoi SzCORE ne suffit pas.
- Les comparaisons cross-dataset peuvent être injustes si les capteurs diffèrent.

## Décisions à verrouiller

- Ne pas chercher à forcer E3 si les données ne le permettent pas.
- Présenter EpiBench comme couche d'evidence and claim governance, pas comme remplacement des métriques événementielles existantes.
- Toujours séparer detection, early warning et forecasting.
- Toujours publier les failures.

## Dépendances

- Parsers dataset.
- Label audit.
- Split freeze.
- Baseline runners.
- Result bundle generator.
- CLI certification.

## Sortie attendue

Un dossier public:

```text
examples/
  chbmit_detection_bundle/
  seizeit2_wearable_bundle/
  msg_forecasting_bundle/
```

Chaque dossier doit être certifiable avec:

```powershell
epibench certify examples/seizeit2_wearable_bundle
```

---

# Phase 6 - Paper Q1 et stratégie de publication

## Objectif scientifique

Transformer EpiBench en contribution méthodologique Q1. Le paper doit être défendable même si aucun modèle deep learning ne produit un résultat spectaculaire.

## Positionnement du papier

Ne pas positionner le papier comme:

- un nouveau modèle;
- un nouveau SOTA;
- une preuve clinique;
- une promesse de déploiement IoT.

Positionner le papier comme:

> A scientific evidence and claim-certification framework for seizure detection, early warning, forecasting, and IoT seizure AI.

## Justification Q1

Le papier doit convaincre qu'il résout un problème structurel du champ:

- scores incompatibles;
- labels hétérogènes;
- splits non comparables;
- accuracy/AUROC trompeurs;
- failures invisibles;
- claims trop forts;
- latence et énergie ignorées;
- confusion detection/forecasting;
- manque d'evidence packages reproductibles.

## Contributions revendicables

1. Epilepsy Dataset Evidence Card.
2. MTS/DSI adaptés à la détection et au wearable seizure AI.
3. Claim Eligibility Matrix E0/E1/E2-PD/E2-PI/E3/E4.
4. Failure-preserving evaluation.
5. Epi-Score multi-axes.
6. Single source of truth YAML + JSON Schemas.
7. Reference implementation CLI.
8. Public worked examples.
9. Anti-overclaim governance.

## Plan de papier recommandé

1. Scores alone are not evidence.
2. Failure modes in seizure detection literature.
3. Relationship to existing event-based scoring and SzCORE-style frameworks.
4. EpiBench architecture.
5. Epilepsy Dataset Evidence Cards.
6. Claim Eligibility Matrix.
7. Failure-preserving evaluation.
8. Epi-Score.
9. Reference implementation.
10. Worked examples across EEG, wearable and longitudinal data.
11. Discussion: limits, clinical boundary, regulatory boundary, adoption.
12. Conclusion: leaderboard rows need claim eligibility.

## Figures obligatoires

1. EpiBench evidence pipeline.
2. Separation of tracks D/W/F/E.
3. Evidence Card MTS/DSI dashboard.
4. Claim gate flowchart.
5. Failure trace preservation.
6. Naive leaderboard versus EpiBench-certified ranking.
7. Sensitivity versus FAR/day.
8. Latency and edge viability plot.
9. Result bundle anatomy.
10. Community adoption workflow.

## Tables obligatoires

1. Comparison with existing benchmark/evaluation frameworks.
2. Dataset Evidence Card summary for pilot datasets.
3. Claim eligibility matrix.
4. Failure sentinel taxonomy and claim effects.
5. Epi-Score axis definitions.
6. Worked example before/after EpiBench.
7. Badge definitions.

## Cibles de publication

### Primary ambitious target: `npj Digital Medicine`

Condition:

- angle AI assurance, clinical evidence governance, reproducibility;
- external feedback from clinicians/researchers;
- strong public implementation;
- clear regulatory humility.

### Strong engineering/biomedical target: `IEEE Journal of Biomedical and Health Informatics`

Condition:

- strong technical implementation;
- reproducible benchmark;
- edge/IoT relevance;
- rigorous metrics.

### Strong methods target: `IEEE Transactions on Biomedical Engineering`

Condition:

- methodological rigor;
- signal processing and clinical evaluation depth;
- robust experiments.

### Clinical epilepsy target: `Epilepsia` or `Epilepsia Open`

Condition:

- stronger clinical co-authorship;
- ILAE-aligned seizure taxonomy;
- clinician-adjudicated interpretation.

### Resource target: `Scientific Data`

Condition:

- focus on standard, metadata, schemas, examples, result bundles.

## Reviewer attacks and defenses

| Attack | Defense |
| --- | --- |
| This is not a new model | Correct; contribution is benchmark evidence governance |
| SzCORE already exists | EpiBench complements event scoring with dataset evidence, failures, IoT viability and claim gates |
| Public datasets cannot prove clinical safety | Correct; EpiBench explicitly prevents clinical overclaim |
| The score weights are arbitrary | Weights are preregistered, sensitivity analyses are reported, and claim gates do not rely on score alone |
| The certification sounds regulatory | The paper explicitly defines certification as scientific/reproducibility certification only |
| Deep models are weak | Weak results are part of the evidence; the paper is not model-first |

## Critères d'acceptation

- Le paper reste convaincant sans hero result.
- Les claims sont plus prudents que les scores.
- L'implémentation est publique ou ready-to-release.
- Les examples sont reproductibles.
- Les limitations sont explicites.
- Les reviewers ne peuvent pas réduire le papier à "another seizure detector".

## Risques scientifiques

- Trop d'ambition peut faire paraître le standard prématuré.
- Sans adoption externe, le terme "community-ready" peut être contesté.
- Sans comparaison à SzCORE, le papier peut être perçu comme redondant.
- Sans clinicien co-auteur, les claim gates cliniques peuvent sembler artificiels.

## Décisions à verrouiller

- Le titre doit éviter "universal clinical certification".
- Le terme recommandé est "scientific claim certification".
- Le paper doit inclure un statement anti-overclaim.
- Le paper doit citer clairement les limites des datasets publics.

## Dépendances

- Phase 1 à 5.
- Clinical supervisor review.
- External dry-run by at least one independent user if possible.
- Public release candidate.

## Sortie attendue

Un manuscript Q1 avec accompanying repository:

```text
paper/
  manuscript.md
  figures/
  tables/
  supplementary/
docs/
  EPIBENCH_SPEC_V1.md
configs/epibench/
schemas/epibench/
examples/
```

---

# Phase 7 - Adoption communautaire et gouvernance du standard

## Objectif scientifique

Préparer l'adoption dès la publication. Le standard doit être utilisable par un groupe externe sans coordination directe avec les auteurs.

## Justification BSEBench-like

Un protocole devient un standard lorsqu'il est:

- stable;
- cité;
- utilisable;
- versionné;
- gouverné;
- capable d'accepter des contributions externes;
- capable de refuser des claims non conformes.

## Position stratégique

EpiBench ne doit pas concurrencer frontalement les frameworks d'event scoring existants. Il doit être positionné comme une couche complémentaire:

> EpiBench can consume event-based scoring outputs, but adds dataset evidence, IoT viability, failure preservation, result bundles, and claim eligibility.

Cela permet d'éviter un conflit inutile avec la communauté existante et de maximiser l'adoption.

## Livrables communautaires

- GitHub public propre.
- Release `v1.0-rc`.
- DOI Zenodo.
- Documentation utilisateur.
- Tutorial "certify your result".
- Example result bundles.
- Issue template pour proposer un dataset.
- Issue template pour soumettre un result bundle.
- Pull request template.
- Governance file.
- Versioning policy.
- Changelog.
- Compatibility policy with event-based scoring frameworks.
- Citation file.
- Code of conduct if public community project.

## Documentation minimale

La documentation doit répondre à cinq questions:

1. Comment remplir une Dataset Evidence Card?
2. Comment produire un Result Bundle?
3. Comment lancer `epibench certify`?
4. Comment interpréter un claim E2-PD versus E2-PI?
5. Comment citer EpiBench dans un paper?

## Gouvernance

Créer `GOVERNANCE.md` avec:

- maintainer roles;
- review process;
- standard change process;
- criteria for adding a dataset;
- criteria for changing score weights;
- criteria for changing claim gates;
- deprecation policy;
- conflict resolution;
- clinical advisory review recommendation.

## Versioning policy

Proposition:

- `v1.0.x`: bug fixes, no rule changes.
- `v1.1.x`: additive fields, backward compatible.
- `v2.0.0`: claim gate, scoring or schema breaking changes.

Tout result bundle doit déclarer:

```yaml
epibench_version: "1.0.0"
schema_version: "1.0.0"
certification_cli_version: "1.0.0"
```

## Adoption pre-submission

Avant soumission:

- obtenir feedback d'au moins un clinicien;
- obtenir feedback d'au moins un expert EEG/seizure detection;
- obtenir feedback d'au moins un chercheur ML/reproducibility;
- faire certifier un exemple par une personne externe au projet;
- documenter les retours et corrections.

## Critères d'acceptation

- Un groupe externe peut installer l'outil.
- Un groupe externe peut certifier un example bundle.
- Le standard a un DOI.
- Le repo explique les claims autorisés et interdits.
- Les badges sont générés automatiquement.
- Les breaking changes sont gouvernés.

## Risques scientifiques

- Adoption trop faible si le protocole paraît trop lourd.
- Adoption superficielle si les utilisateurs ne citent que le badge.
- Fragmentation si EpiBench ignore les frameworks existants.
- Confusion publique si "certified" est mal compris.

## Décisions à verrouiller

- Toujours inclure "scientific" ou "EpiBench v1.0" dans la certification.
- Ne jamais écrire "clinically certified".
- Maintenir une compatibility note avec event-based scoring.
- Garder les examples petits et reproductibles.

## Dépendances

- Phase 4 reference implementation.
- Phase 5 public examples.
- Phase 6 manuscript framing.

## Sortie attendue

Un standard publiable et adoptable:

```text
EpiBench v1.0-rc
DOI: assigned
CLI: installable
Examples: reproducible
Certification: deterministic
Governance: public
Paper: submitted
```

---

# Calendrier recommandé

## Version intensive 12 semaines

| Semaine | Objectif |
| --- | --- |
| 1-2 | Phase 1: rubriques, tracks, claims, fail-closed |
| 3-4 | Phase 2: YAML, schemas, spec normative |
| 5 | Phase 3: claim gates, badges, failure consequences |
| 6-7 | Phase 4: CLI minimal, score engine, certify engine |
| 8-9 | Phase 5: pilot bundles, worked examples |
| 10-11 | Phase 6: manuscript, figures, tables |
| 12 | Phase 7: release candidate, DOI, external dry-run |

## Version réaliste 20 semaines

| Période | Objectif |
| --- | --- |
| Semaines 1-3 | Protocole normatif |
| Semaines 4-6 | Single source of truth |
| Semaines 7-9 | Certification engine |
| Semaines 10-12 | Reference implementation |
| Semaines 13-15 | Datasets pilotes |
| Semaines 16-18 | Paper Q1 |
| Semaines 19-20 | Adoption, release, external feedback |

---

# RACI minimal

| Rôle | Responsabilité |
| --- | --- |
| PI / doctorant | ownership scientifique, protocole, paper |
| Superviseur médical | seizure taxonomy, clinical limits, intended use |
| ML/reproducibility reviewer | leakage, splits, result bundles |
| Signal processing reviewer | event detection metrics, latency, sensor issues |
| External dry-run user | adoption test |

Sans superviseur clinique ou reviewer médical, E4 doit rester explicitement hors scope.

---

# Checklist finale avant soumission Q1

- [ ] `EPIBENCH_PROTOCOL.md` aligné avec la spec v1.
- [ ] `EPIBENCH_SPEC_V1.md` créé.
- [ ] `epibench_v1.yaml` créé.
- [ ] JSON Schemas créés.
- [ ] CLI minimal fonctionne.
- [ ] Example result bundle certifiable.
- [ ] MTS/DSI déterministes.
- [ ] Epi-Score calculable.
- [ ] Claim gate déterministe.
- [ ] Failure traces obligatoires.
- [ ] Tracks D/W/F/E séparés.
- [ ] E2-PD et E2-PI séparés.
- [ ] Worked example avant/après inclus.
- [ ] Zenodo DOI préparé.
- [ ] Documentation adoption prête.
- [ ] Paper ne promet aucune certification clinique.
- [ ] External dry-run réalisé ou explicitement planifié.

---

# Phrase de conclusion stratégique

La réussite d'EpiBench ne dépendra pas du fait qu'un modèle obtienne une sensitivity spectaculaire. Elle dépendra du fait que la communauté puisse enfin lire un résultat de seizure detection, early warning ou forecasting et savoir exactement:

- quelle donnée le supporte;
- quel split le rend crédible;
- quelles failures ont été observées;
- quelle latence et quel coût IoT le bornent;
- quel claim est autorisé;
- quel claim est interdit.

Si EpiBench atteint cela, le paper ne sera pas seulement un article de benchmark. Il deviendra une proposition de standard scientifique pour rendre les résultats d'IA épilepsie auditables, comparables et honnêtes.
