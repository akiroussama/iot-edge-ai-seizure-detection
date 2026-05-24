# EpiBench Phase 3 - Certification Scientifique Et Claim Gates

## Thèse

La certification EpiBench n'est pas un label clinique. Elle répond à une question beaucoup plus précise:

> Etant donné un dataset, un split, un audit de labels, un result bundle, une failure trace et des métriques, quel est le claim scientifique maximal autorisé?

Cette phase est le coeur BSEBench-like du standard. Le score n'est pas supprimé, mais il n'est plus souverain. Il devient un élément interprété sous contrainte de preuve.

## Badges Normatifs

Les badges exposent la nature de la preuve:

- `EpiBench-Dataset-T1`: dataset fort, traçable, annoté, mais pas automatiquement généralisable.
- `EpiBench-Dataset-T2`: dataset utile mais incomplet.
- `EpiBench-Dataset-T3`: dataset exploratoire, inventaire ou preuve faible.
- `EpiBench-Run-Complete`: result bundle complet, split manifest présent, failure trace présente.
- `EpiBench-Claim-E1`: validité structurelle seulement.
- `EpiBench-Claim-E2-PD`: claim opérationnel patient-dependent.
- `EpiBench-Claim-E2-PI`: claim opérationnel patient-independent.
- `EpiBench-Claim-E3`: validation externe, multisite ou leave-site-out.
- `EpiBench-Failure-Transparent`: les échecs sont conservés.
- `EpiBench-Leakage-Checked`: fuite patient et temporelle auditée.
- `EpiBench-Edge-Measured`: latence ou coûts hardware mesurés.

Un badge doit être généré par la reference implementation, pas ajouté manuellement dans un article.

## Claim Gates

### Gate 1 - Dataset Tier

Le tier dataset fixe un plafond:

- `T1`: peut soutenir `E2-PI`; peut aller vers `E3` seulement avec validation externe; peut aller vers `E4` seulement avec prospective evidence.
- `T2`: peut soutenir un claim étroit, mais ses limites doivent rester visibles.
- `T3`: ne peut pas soutenir de claim opérationnel fort.

### Gate 2 - Split

Règles verrouillées:

- pas de `E2-PI` sans split patient-independent ou LOSO;
- pas de `E3` sans external dataset, leave-site-out ou multisite;
- patient-dependent ne peut pas être maquillé en généralisation;
- un split inconnu ou non conforme tombe à `E1`.

### Gate 3 - Label Audit

Un résultat de détection de crise dépend de la vérité de timing. EpiBench distingue:

- onset et offset expert-adjudicated;
- onset expert mais offset absent;
- clinical record sans timing précis;
- proxy wearable ou self-report;
- labels non audités.

Un label proxy ne peut pas produire un claim clinique fort, même avec un AUROC élevé.

### Gate 4 - Failure Trace

Les failures ne sont pas des notes de bas de page. Elles changent le claim:

- leakage patient ou temporel bloque `E2+`;
- split non conforme bloque `Run-Complete`;
- NaN ou sorties manquantes systématiques abaissent le claim;
- alarme après onset ne peut pas être revendiquée comme early warning;
- faux positifs massifs bloquent l'interprétation clinique;
- absence de mesure hardware interdit les phrases `real-time`, `on-device`, `edge-ready`.

### Gate 5 - Track Consistency

Chaque run a un track primaire:

- `D`: detection;
- `W`: early warning;
- `F`: forecasting;
- `E`: embedded viability.

Un modèle peut être évalué sur plusieurs tracks, mais chaque track produit son propre verdict.

## Exemple De Certification

Run valide:

```powershell
python scripts\epibench.py certify examples\epibench\pilot_t1_eeg\result_bundle.yaml --out reports\epibench_pilot_claim.json --report reports\epibench_pilot_claim.md
```

Résultat attendu:

- final claim: `E2-PI`;
- badges: dataset T1, run complete, failure transparent, leakage checked, edge measured;
- score: informatif mais non suffisant pour monter à `E3`.

Run avec leakage:

```powershell
python scripts\epibench.py certify examples\epibench\failure_leakage\result_bundle.yaml --out reports\epibench_leakage_claim.json --report reports\epibench_leakage_claim.md
```

Résultat attendu:

- score élevé;
- final claim abaissé à `E1`;
- raisons bloquantes: patient leakage, split non conforme, threshold choisi sur test.

Cette démonstration est la preuve pédagogique la plus importante: EpiBench doit pouvoir montrer qu'un excellent score naïf peut perdre son claim.

## Definition Of Done

La phase 3 est terminée si:

- le claim final est entièrement généré par règles;
- les badges sont générés par règles;
- un run avec leakage tombe mécaniquement à `E1`;
- un run patient-dependent ne peut pas obtenir `E2-PI`;
- un run sans validation externe ne peut pas obtenir `E3`;
- un run sans hardware ne peut pas revendiquer temps réel;
- les raisons bloquantes sont imprimées dans le rapport.

## Risques Scientifiques

- Transformer la certification en label marketing.
- Laisser croire qu'un claim `E3` signifie sécurité clinique.
- Masquer les failures derrière un score agrégé.
- Confondre claim ceiling et qualité absolue du modèle.
- Rendre les gates trop faciles pour favoriser l'adoption rapide.

## Sortie Phase 3

La sortie est un système de certification scientifique reproductible: les auteurs ne disent plus "notre modèle est généralisable"; ils soumettent un bundle, et EpiBench dit quel claim est autorisé.
