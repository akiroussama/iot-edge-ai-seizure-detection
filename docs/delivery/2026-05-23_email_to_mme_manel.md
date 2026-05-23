# Email To Mme Manel

Subject: Livraison du projet EpiTwin-Open et proposition d'article

Bonjour Madame Manel,

Je vous envoie un point de synthèse sur l'état final du travail EpiTwin-Open.
Nous avons décidé d'arrêter les améliorations techniques à ce stade afin de
figer une version livrable et de passer à la préparation de l'article.

Notre contribution principale est un benchmark ouvert, gelé et auditable pour
l'évaluation de la prévision du risque de crise d'épilepsie à partir de données
wearables publiques. Le projet ne se présente pas comme un simple modèle de
prédiction, mais comme une infrastructure scientifique de comparaison: données
gelées, splits explicites, garde-fous anti-fuite, métriques cliniques, baselines
nulles, calibration, Brier Skill Score, FAR/day, Time-in-Warning et atlas de
forecastability.

Le résultat gelé le plus important concerne le dataset My Seizure Gauge. Nous
avons figé un registre Gate C et exécuté un premier benchmark de baselines
nulles uniquement à partir des artefacts gelés. Le dénominateur d'évaluation est
délibérément strict: 54 événements test appariés et couverts par les fenêtres de
prédiction, sur 510 événements appariés après filtrage. La baseline
`cycle_preserving_random` obtient un Brier Skill Score de 0.070 avec un
intervalle bootstrap patient [0.034, 0.089], au-dessus de la climatologie. Cela
ne prouve pas qu'un modèle clinique est prêt, mais cela montre qu'une structure
temporelle/cyclique existe dans les données gelées et qu'un futur modèle appris
devra battre cette baseline cyclique, pas seulement une prévalence moyenne.

Par rapport au SOTA, nous avons volontairement adopté un cadrage prudent. Le
travail récent de Nasseri et al. dans Epilepsia 2025 a déjà montré une
prévision wearable non invasive à long terme avec fréquence cardiaque et pas
sur My Seizure Gauge. Nous ne revendiquons donc pas être les premiers à faire de
la prévision wearable. Notre apport est différent: rendre l'évaluation ouverte,
reproductible, anti-fuite, calibrée, comparable et honnête sur les cas
non-forecastables. Ce positionnement répond directement aux limites rapportées
dans les revues récentes: forte hétérogénéité des horizons, des métriques, des
splits et des protocoles d'évaluation.

Je pense que le projet est publiable si nous le soumettons comme un papier de
benchmark/méthodologie, et non comme un papier de performance clinique. Le titre
proposé est:

**EpiTwin-Open: A Frozen, Leakage-Aware Benchmark for Calibrated Wearable
Seizure-Risk Forecasting**

Les contributions proposées pour l'article sont:

1. Un protocole ouvert et gelé pour l'évaluation de la prévision du risque de
   crise sur données wearables.
2. Un registre Gate C et un harness de rerun qui refusent les données locales
   non gelées.
3. Un leaderboard unifié avec sensibilité événementielle, FAR/day,
   Time-in-Warning, Brier, BSS et calibration.
4. Une famille de baselines nulles, incluant une baseline cyclique.
5. Un Forecastability Atlas qui empêche de sur-vendre les horizons ou modèles
   non significatifs.
6. Une traçabilité complète des décisions, garde-fous, limitations et statuts
   citable/non-citable.

Pour la soumission, ma recommandation est:

- **Premier choix: IEEE Journal of Biomedical and Health Informatics (Q1)**,
  car le papier est très adapté à l'IA biomédicale, aux benchmarks, à la
  calibration et à la reproductibilité.
- **Alternative forte: Scientific Data**, si nous voulons insister sur le
  package gelé, les artefacts réutilisables et la valeur ressource/données.
- **Option clinique spécialiste: Epilepsia**, très prestigieuse en épilepsie,
  mais probablement plus exigeante sur l'interprétation clinique et la présence
  d'une validation épileptologique forte.
- **Stretch ambitieux: npj Digital Medicine**, possible mais risqué sans message
  clinique très large.
- **Fallback sérieux: Epilepsia Open ou IEEE Access**, si nous voulons une route
  plus sûre après un refus Q1.

Mon avis: viser d'abord IEEE JBHI est le meilleur compromis entre ambition Q1,
adéquation scientifique et probabilité réaliste d'acceptation. Le papier peut
être accepté si nous sommes rigoureux dans le cadrage: benchmark ouvert,
évaluation anti-fuite, baselines gelées, résultats nuls rapportés honnêtement et
absence de revendication clinique excessive.

Les documents principaux sont prêts dans le dépôt:

- `docs/delivery/2026-05-23_final_delivery_brief.md`
- `docs/delivery/2026-05-23_publication_strategy_and_sota.md`
- `docs/PUBLICATION_PROPOSAL.md`
- `docs/SOTA_REVIEW_2026.md`
- `docs/research/2026-05-23_gate_c_frozen_null_benchmark.md`
- `reports/gate_c_frozen_benchmark_2026-05-23/frozen_benchmark_audit.md`

La prochaine étape que je propose est de valider ensemble le cadrage et le
journal cible, puis de transformer cette base en manuscrit complet. A ce stade,
je recommande de ne plus ajouter de nouvelles expériences avant d'avoir une
première version structurée de l'article.

Bien cordialement,

O. Akir
