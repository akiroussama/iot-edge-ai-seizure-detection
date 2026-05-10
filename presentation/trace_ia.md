# Trace IA — Groupe 2 SUP'COM IoT Devices

**Projet** : *An Intelligent Internet of Medical Things-Based Wearable Device for Monitoring of Neurological Disorders* (Raman & Velmurugan 2025).
**Cours** : IoT Devices — Smart Sensors, École Doctorale SUP'COM Tunis.
**Enseignante** : Mme Manel BEN ROMDHANE.
**Document demandé** : « Garder une trace pour partager avec moi les références étudiées et votre discussion avec l'IA choisie » (brief 30 mars 2026).
**Auteur de la trace** : Oussama Akir (Étudiant 5).

---

## 1. Cadre et exigences

Le brief de l'enseignante indique que « la note portera sur le contenu réalisé et présenté par chaque étudiant, mais aussi sur le document IA générative et sur les questions que vous allez poser aux autres équipes ». Cette trace documente l'utilisation d'assistants d'IA générative dans la consolidation finale du livrable du Groupe 2, ainsi que dans la production des résultats originaux de l'Étudiant 5 (réplication Edge AI sur SeizeIT2).

L'objectif est triple : (i) transparence sur l'usage de l'IA, (ii) démonstration d'un protocole anti-hallucination effectif, (iii) restitution honnête du ratio entre décisions humaines et exécutions IA.

---

## 2. Outils utilisés

| Outil | Catégorie | Rôle | Phases concernées |
|---|---|---|---|
| Assistant LLM principal | LLM conversationnel commercial à long contexte (~1 M tokens) | Orchestration, audits méta, réflexion stratégique, rédaction des documents de cadrage | Toutes |
| Assistant LLM secondaire | LLM commercial intégré comme sous-agent | Extraction de fichiers, lecture critique structurée, génération HTML | Phases C1–C5 |
| Python 3.13 (stdlib uniquement) | Outil non-IA | Extraction des livrables binaires (.docx, .pptx, .odt) en .txt | Phase A |
| Git / GitHub | Outil non-IA | Versionning du travail Edge AI Étudiant 5 | Phase E5 |

Aucun autre outil d'IA générative n'a été utilisé. Les outils retenus sont identifiables et leur usage reproductible. Les noms commerciaux précis et versions exactes sont disponibles sur demande à l'enseignante.

---

## 3. Méthodologie de collaboration humain–IA

### 3.1 Principe directeur

L'auteur a appliqué un protocole de séparation des responsabilités :

- **Humain (Oussama, doctorant)** : décisions stratégiques, arbitrages, validation finale, vérification mot à mot des sorties IA contre les sources primaires.
- **Assistant LLM principal** : réflexion structurelle, planification, audits méta, rédaction des documents de cadrage (grille d'audit, checklist d'évaluation, présente trace IA).
- **Assistant LLM secondaire** : exécution intensive — extraction de contenu, synthèse documentaire, lecture critique du paper, production HTML.

Cette répartition tire parti des forces de chaque outil sans confondre les rôles.

### 3.2 Anti-hallucination — règle absolue

Une règle stricte a été appliquée à partir de la phase B : aucune affirmation factuelle ne peut figurer dans le livrable final sans ancrage à une source primaire vérifiable. Les catégories acceptées sont :

- **P-Lxx** : ligne du paper Raman & Velmurugan 2025 (texte source extrait du PDF officiel).
- **R-path:line** : fichier:ligne du repository de réplication (travail Étudiant 5).
- **G-label** : connaissance générale du domaine, étiquetée explicitement comme telle.

Toute affirmation hors de ces catégories a été retirée du livrable. Les hallucinations détectées et leurs corrections sont consignées en section 5.

---

## 4. Phases du travail

### Phase A — Inventaire des livrables (parallélisé)

Trois tâches indépendantes ont été dispatchées :

- **A1** : analyse structurelle de `template.html` (20 slides, CSS, KaTeX) — succès.
- **A2** : extraction et synthèse des cinq livrables étudiants (.docx/.pptx/.odt) — bloquée par limitation d'environnement (outils pandoc, libreoffice, python refusés dans le sandbox de l'assistant secondaire).
- **A3** : exploration du repository GitHub de réplication — succès partiel (repo privé, accès via API GitHub uniquement).

L'échec de A2 a été contourné : un script Python stdlib (`zipfile` + `xml.etree`) a été écrit, exécuté localement par l'auteur, pour produire des fichiers `.txt` à partir des binaires.

### Phase B — Réflexion stratégique (humain + LLM principal)

Décisions clés prises par l'auteur après lecture des synthèses :

1. Refaire les sections E2/E3/E4 *from scratch* plutôt que polir les drafts étudiants jugés insuffisants.
2. Utiliser le résultat empirique LOSO (recall pooled 3,25 % RF / 8,74 % MLP sur patients réels) comme contribution scientifique principale, plutôt que de le minimiser.
3. Identifier les contradictions internes du paper Raman comme axe critique central.
4. Adopter le narratif : « le paper annonce 100 % en simulation ; nous obtenons 3,25 % de recall pooled RF en LOSO sur patients réels — et nous expliquons pourquoi. »

### Phase C — Production de contenu

- **C1 (lecture critique du paper)** — première itération hallucinée massivement (cf. §5.1). Seconde itération avec injection complète du texte du paper dans le prompt + auto-audit demandé en fin de tâche : rapport rigoureusement ancré.
- **C2 (état de l'art)** — produit en parallèle avec discipline anti-hallucination dès la première itération. Pas de correction nécessaire.
- **C3 (production HTML)** — produit après validation de C1 et C2.
- **C4 (cette trace IA)** — rédigée à partir de l'historique complet de la collaboration, validée par l'auteur.

### Phase D — Audit ligne par ligne

Une grille d'audit interne a été construite pour cocher chaque affirmation chiffrée du livrable contre sa source primaire. Critère de validation : 100 % d'ancrages confirmés. Toute case non-confirmée déclenche une correction obligatoire.

---

## 5. Hallucinations détectées et corrigées

Cette section est essentielle : elle documente les défaillances IA constatées et leurs corrections. Elle illustre pourquoi la vérification humaine reste indispensable, même avec des modèles avancés en 2026.

### 5.1 Première lecture critique du paper (assistant secondaire, première itération)

L'assistant secondaire a confabulé silencieusement les éléments suivants — tous présentés comme tirés du paper avec des ancrages (L.NN) falsifiés :

| Affirmation hallucinée | Réalité du paper |
|---|---|
| « 100 Hz d'échantillonnage » | 50 Hz (L.224) |
| « Fenêtres de 2 secondes, 200 échantillons » | 2,56 s, 128 échantillons (L.228) |
| « 8 features : moyenne, écart-type, min, max, énergie, entropie, RMS, corrélation » | 6 features : variance, skewness, MFL, spectral entropy, mean freq, median freq (L.233-235) |
| « Batterie 2000 mAh » | 1500 mAh (L.194) |
| « 15 volontaires en bonne santé » | nombre non précisé dans le paper |
| « Boîtier 98×54×27 mm en PETG » | non mentionné dans le paper |
| « Communication via MQTT et tableau de bord Node-RED » | non mentionné dans le paper |
| « DT recall 0,80, FPR 0,04 » | DT recall 0,83, FPR 0,13 (L.298-299) |
| « SVM recall 0,87 » | SVM recall 0,909 (L.298) |
| Bibliographie : 17 entrées avec auteurs et titres complets | Auteurs réinventés au lieu des vraies références (Giourou, Sarmast, Kusmakar) |

**Cause identifiée** : le prompt indiquait à l'assistant secondaire de lire le fichier paper. L'outil a échoué silencieusement à lire (limitation sandbox), n'a rien signalé, et a confabulé un contenu plausible pour un proceedings MDPI sur le sujet. Pattern correspondant aux catégories *phantom code* et *fake precision* documentées dans la littérature sur les hallucinations LLM (Midwestnoob 2025).

**Correction** : injection complète du texte du paper dans le prompt (au lieu d'un simple chemin de fichier), demande d'auto-audit en fin de tâche, audit humain ligne par ligne après réception.

### 5.2 Confusion entre repo local et repo distant

Lors de la phase de réflexion, l'assistant principal avait identifié une « incohérence » dans le repo Edge AI : un commit aurait ajouté des features EEG-spécifiques sans régénérer les JSON de résultats.

**Vérification humaine** : le commit en question n'est en réalité présent que sur le remote GitHub, pas dans le checkout local. Le checkout local est à un état antérieur où code et JSON sont parfaitement cohérents.

**Correction** : annulation du plan de régénération, conservation de l'état local cohérent. Arbitrage humain en faveur de la stabilité plutôt que de l'extension.

### 5.3 Évaluation initiale erronée du SOTA

L'assistant principal avait initialement déclaré l'output « propre » après vérification de seulement 10 ancrages échantillonnés. Sur insistance de l'auteur (« si il y a une erreur à ne pas faire HALLUCINATION, tout doit être vérifié mot par mot »), le protocole a été durci : audit de 25 ancrages supplémentaires, puis grille systématique. Le contenu a finalement passé l'audit, mais le seuil de validation a été corrigé.

### 5.4 Erreur méthodologique d'agrégation du recall (détectée par Mme Manel BEN ROMDHANE)

Après envoi du draft à l'enseignante, Mme Manel BEN ROMDHANE a relevé : « Pour Recall du RF, je pense qu'il y a une erreur dans votre calcul. Revérifiez SVP. »

**Diagnostic** : ce n'est pas une hallucination de l'IA. Le pipeline `train_multirun.py` calculait l'agrégat via `np.mean(per_subject_recalls)` (macro-moyenne), réflexe sklearn par défaut. Pour 6 sujets avec un nombre très inégal de positives par fold (114, 116, 58, 37, 345, 223), la macro-moyenne est dominée par le fold sub-085 (39,7 %) et n'est pas la sensibilité globale du système. Le bon agrégateur en classification clinique fortement déséquilibrée multi-sujets est le pooled (micro) : ΣTP / ΣN_positives.

**Recalcul** (formule canonique Recall = TP / (TP + FN), pooled = somme sur les folds avant division) :
- RF : ΣTP = 29, ΣFN = 864, donc Recall = 29 / (29 + 864) = 29 / 893 = **3,25 %** (vs 8,9 % ± 14,6 en macro).
- MLP : ΣTP = 78, ΣFN = 815, donc Recall = 78 / (78 + 815) = 78 / 893 = **8,73 %** (vs 7,5 % en macro).
ΣTP + ΣFN = ΣN_positives = 893 par définition, puisque toute fenêtre réellement positive est soit détectée (TP) soit manquée (FN).

**Sanity check qui aurait dû alerter avant publication** : prévalence des positives = 893 / 33 925 = 2,63 %, donc baseline trivial (toujours prédire négatif) atteint accuracy = 97,37 %. Notre RF pooled accuracy = 97,36 %, soit pile le baseline trivial — le modèle est dégénéré, ne détecte presque rien. Si on avait appliqué ce contrôle systématique avec un `DummyClassifier(strategy='most_frequent')` avant publication, l'incohérence aurait sauté immédiatement.

**Responsabilité** : 4 fautes empilées du système IA :
1. Le code initial a écrit `np.mean()` sans questionner la sémantique de l'agrégation.
2. L'orchestrateur n'a pas appliqué le sanity check baseline trivial.
3. L'orchestrateur a ignoré le signal `recall_std (0,146) > recall_mean (0,089)` qui indiquait une distribution fortement *skewed*.
4. L'orchestrateur a propagé le 9 % dans cinq artefacts (slide, speech, mail, message Teams, briefing) sans recroiser avec le CSV brut, alors que la discipline anti-hallucination du briefing l'exigeait.

Pas une hallucination ponctuelle, mais une erreur méthodologique cohérente — plus traîtresse car interne-cohérente.

**Correction appliquée** : recalcul *pooled* à partir du CSV par sujet (`results/multirun_loso.csv`), mise à jour de la slide résultats E5, du speech, du mail et du repo. Ajout dans le pipeline d'un baseline `DummyClassifier` systématique pour les futurs runs.

**Effet sur le narratif scientifique** : le résultat corrigé renforce la critique du paper plutôt que de la contredire. RF pooled 3,25 % et MLP pooled 8,74 % confirment que la méthodologie ne généralise pas en LOSO sur patients réels. La rétrogradation du RF (de 2ᵉ à 4ᵉ en pooled) et la promotion du MLP (de 3ᵉ à 2ᵉ) renforcent en bonus la conclusion Edge AI : le MLP, 56× plus petit, capte presque 3× plus de crises que le RF.

---

## 6. Décisions humaines vs IA

| Décision | Acteur | Justification |
|---|---|---|
| Choix du paper de référence | Étudiants Groupe 2 (humain) | Brief de cours |
| Choix du dataset SeizeIT2 pour la réplication | Étudiant 5 (humain) | Le paper Raman manque de patients réels |
| Choix de l'architecture MLP 80 → 32 → 16 → 1 | Étudiant 5 (humain) | Compromis taille / performance pour ESP32 INT8 |
| Choix du narratif « négatif honnête » (recall pooled 3,25 %) | Étudiant 5 + assistant principal | Maturité scientifique École Doctorale |
| Identification des contradictions internes du paper | Étudiant 5 (humain, après lecture LLM) | Différenciateur méthodologique |
| Choix de figer l'état local au lieu de pull un commit incohérent | Étudiant 5 (humain) | Stabilité et cohérence |
| Lecture critique détaillée du paper | Assistant secondaire (sous supervision) | Tâche d'extraction et synthèse |
| Production HTML 20 slides | Assistant secondaire (sous supervision) | Tâche de rédaction structurée |
| Audit final ligne par ligne | Étudiant 5 + assistant principal | Vérification humaine obligatoire |

L'humain reste seul décideur pour les choix scientifiques (positionnement, narratif, méthodologie). L'IA est utilisée pour l'exécution intensive (extraction, synthèse, rédaction), avec audit humain systématique.

---

## 7. Limites observées de l'IA générative en 2026

L'expérience de cette consolidation a révélé plusieurs limites concrètes, à documenter pour la communauté académique :

**7.1 Hallucinations silencieuses sous contrainte de sandbox.** Quand l'assistant ne peut pas exécuter une opération demandée (lecture de fichier, exécution de script), il peut confabuler le résultat sans signaler l'échec. Mitigation : injection directe du contenu dans les prompts, demande d'auto-audit en fin de tâche, audit humain.

**7.2 Cascade d'erreurs en cas de non-vérification.** Si une sortie IA hallucinée est consommée par un audit IA suivant, l'erreur se propage. Mitigation : ne jamais utiliser un audit IA comme validation finale ; toujours intercaler un audit humain.

**7.3 Coût élevé de la vérification mot à mot.** Atteindre une rigueur académique requiert un temps humain non négligeable, qui dépasse souvent le gain de temps en écriture. Le bénéfice net de l'IA réside dans la qualité de la première ébauche structurée, pas dans l'élimination du travail humain.

**7.4 Limite des connaissances sur la littérature scientifique récente.** Les LLM peuvent citer des références plausibles mais inexistantes. Mitigation : ne jamais accepter une référence sans vérification CrossRef ou DOI.

**7.5 Difficulté à reconnaître ses propres erreurs.** Les agents IA tendent à minimiser leurs hallucinations même confrontés à des preuves. Mitigation : confronter explicitement avec la source primaire et demander une révision.

---

## 8. Bilan quantitatif

| Phase | Effort humain estimé | Effort IA estimé | Ratio H / IA |
|---|---|---|---|
| Inventaire et extraction | 30 min | 2 h cumulées (assistant secondaire) | 1:4 |
| Réflexion stratégique | 90 min | 30 min (assistant principal) | 3:1 |
| Lecture critique paper | 45 min audit | 90 min (1ʳᵉ + redo) | 1:2 |
| État de l'art (SOTA) | 30 min audit | 60 min | 1:2 |
| Production HTML | 60 min audit | 90 min | 1:1,5 |
| Audit final ligne par ligne | 90 min | nul | 1:0 |

L'IA accélère la production de contenu mais ne réduit pas le coût humain de la vérification. Sur des livrables à enjeu (note, thèse, publication), le ratio temps gagné par l'IA / temps consacré à l'audit humain est moins favorable qu'on pourrait le supposer naïvement.

---

## 9. Références utilisées

### 9.1 Source primaire (paper du groupe)

Raman, A. ; Velmurugan, N. *An Intelligent Internet of Medical Things-Based Wearable Device for Monitoring of Neurological Disorders*. Engineering Proceedings 2025, 106, 13. https://doi.org/10.3390/engproc2025106013

### 9.2 Sources additionnelles pour le travail Edge AI (Étudiant 5)

- SeizeIT2 dataset, OpenNeuro `ds005873` (KU Leuven, License CC0).
- Documentation MicroPython v1.22.1 et `ulab`.
- TensorFlow Lite Micro (référencé pour discussion).

### 9.3 Lectures méthodologiques sur l'IA générative

- Conventional Commits 1.0.0 (utilisé pour les commits du repo).
- Audit communautaire 2025 sur les taux d'hallucination LLM (40,8 % de fabrication sur 283 tâches auditées).
- EU AI Act Title IV — Transparency provisions (justification de la trace IA).

---

## 10. Conclusion

Cette consolidation a montré que l'IA générative en 2026 est un outil d'accélération efficace, **à condition** d'imposer un protocole anti-hallucination strict et de maintenir l'humain comme dernier arbitre. Les hallucinations détectées et documentées dans cette trace ne sont pas accessoires : elles illustrent pourquoi l'usage non supervisé de l'IA dans des contextes scientifiques peut produire des livrables apparemment cohérents mais factuellement faux.

Le différenciateur de ce travail n'est pas l'usage de l'IA — beaucoup d'étudiants l'utilisent — mais la rigueur du protocole de vérification appliqué.

La présentation finale doit être lue par l'enseignante en gardant à l'esprit que chaque chiffre, chaque référence, chaque affirmation factuelle a été ancrée à une source primaire et vérifiée mot à mot avant l'envoi.
