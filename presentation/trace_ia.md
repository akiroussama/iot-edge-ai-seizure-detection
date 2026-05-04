# Trace IA — Groupe 2 SUPCOM IoT Devices

**Projet** : An Intelligent Internet of Medical Things-Based Wearable Device for Monitoring of Neurological Disorders (Raman & Velmurugan 2025).
**Cours** : IoT Devices — Smart Sensors, École Doctorale SUPCOM Tunis.
**Enseignante** : Mme Rim Ben Romdhane.
**Document demandé** : « Garder une trace pour partager avec moi les références étudiées et votre discussion avec l'IA choisie » (brief 30 mars 2026).
**Auteur de la trace** : Oussama Akir (Étudiant 5).

---

## 1. Cadre et exigences

Le brief de l'enseignante mentionnait explicitement que « la note portera sur le contenu réalisé et présenté par chaque étudiant, mais aussi sur le document IA générative et sur les questions que vous allez poser aux autres équipes ». Cette trace documente l'utilisation de l'IA dans la phase de consolidation finale du livrable du Groupe 2, ainsi que dans la production des résultats originaux de l'Étudiant 5 (réplication Edge AI sur SeizeIT2).

L'objectif est triple : transparence sur l'usage de l'IA, démonstration d'un protocole anti-hallucination effectif, et restitution honnête du ratio entre décisions humaines et exécutions IA.

---

## 2. Outils IA utilisés

| Outil | Rôle | Phase |
|---|---|---|
| Claude Code (Anthropic, Opus 4.7, contexte 1M) | Chef d'orchestre, audits, réflexion stratégique, rédaction des documents méta (audit grid, checklist, trace IA) | Toutes phases |
| Codex (plugin Claude Code, OpenAI GPT-5.4) | Extraction de fichiers, lecture critique, production de contenu structuré, génération HTML | Phases C1-C5 |
| Python 3.13 (stdlib uniquement) | Extraction des livrables binaires (.docx, .pptx, .odt) en .txt | Phase A |
| Git / GitHub (repo personnel) | Versionning du travail Edge AI Étudiant 5 | Phase E5 |

Aucun autre outil IA (ChatGPT public, Mistral, Gemini, etc.) n'a été utilisé dans cette consolidation. Les modèles utilisés sont identifiables et reproductibles.

---

## 3. Méthodologie de collaboration humain-IA

### 3.1 Principe directeur

L'auteur a appliqué un protocole de séparation des responsabilités :
- **Humain (Oussama, doctorant)** : décisions stratégiques, arbitrages, validation finale, vérification mot par mot des outputs IA contre sources primaires.
- **Claude Code** : réflexion structurelle, planification, audits méta, rédaction des documents de cadrage (grille d'audit, checklist prof, trace IA).
- **Codex (via plugin)** : exécution intensive — extraction de contenu, synthèse, lecture critique du paper, production HTML.

Cette répartition tire parti des forces de chaque outil sans confondre les rôles.

### 3.2 Anti-hallucination — règle absolue

Une règle stricte a été appliquée à partir de la phase B : aucune affirmation factuelle ne peut figurer dans le livrable final sans ancrage à une source primaire vérifiable. Les catégories acceptées sont :
- **P-Lxx** : ligne du paper Raman & Velmurugan 2025 (fichier source extrait du PDF officiel).
- **R-path:line** : fichier:ligne du repository iot-edge-ai-seizeit2 (travail Étudiant 5).
- **G-label** : connaissance générale du domaine, étiquetée explicitement comme telle dans le slide.

Toute affirmation hors de ces catégories a été retirée du livrable. Le tableau comparatif final (sections 4 et 5 ci-dessous) documente les hallucinations détectées et corrigées.

---

## 4. Phases du travail

### Phase A — Inventaire des livrables (parallélisé)

Codex a été dispatché sur trois tâches indépendantes :
- **A1** : analyse structurelle de `template.html` (20 slides, CSS custom, KaTeX) — succès complet.
- **A2** : extraction et synthèse des cinq livrables étudiants (.docx/.pptx/.odt) — bloqué par sandbox Codex (les outils pandoc, libreoffice, python ont été refusés).
- **A3** : exploration du repo GitHub `akiroussama/iot-edge-ai-seizeit2` — succès partiel (repo privé, accès via API GitHub uniquement).

L'échec de A2 a déclenché une adaptation : un script Python stdlib (zipfile + xml.etree) a été écrit par Claude Code, exécuté localement par l'auteur, pour produire des fichiers .txt à partir des binaires. Codex a ensuite pu les synthétiser.

### Phase B — Réflexion stratégique (humain + Claude Code)

Décisions clés prises par l'auteur après avoir lu les synthèses Codex :
1. Refaire les sections E2/E3/E4 from scratch plutôt que polir les drafts étudiants jugés insuffisants.
2. Utiliser le résultat empirique LOSO (recall 9 % sur patients réels) comme contribution scientifique principale, plutôt que le minimiser.
3. Catcher les contradictions internes du paper Raman comme axe critique central.
4. Adopter le narratif : « Le paper annonce 95 % en simulation, nous obtenons 9 % de recall en LOSO sur patients réels — et nous expliquons pourquoi. »

### Phase C — Production de contenu

**C1 (lecture critique)** — première itération a halluciné massivement (cf. section 5 ci-dessous). Une seconde itération avec injection complète du texte du paper dans le prompt + auto-audit demandé en fin de tâche a produit un rapport rigoureusement ancré.

**C2 (état de l'art)** — produit en parallèle avec une discipline anti-hallucination dès la première itération (le prompt incluait des consignes d'étiquetage « connaissance générale » vs « tiré du paper »). Pas de correction nécessaire.

**C3 (production HTML)** — en cours au moment de la rédaction de cette trace. Audit prévu après livraison.

**C4 (cette trace IA)** — rédigée par Claude Code à partir de l'historique complet de la conversation, validée par l'auteur.

**C5 (mail prof)** — à rédiger.

### Phase D — Audit ligne par ligne

Une grille d'audit (`AUDIT_GRILLE.md`) a été construite pour cocher chaque affirmation chiffrée du livrable contre sa source primaire. Statut requis avant envoi : 100 % de cases ✓. Toute case ⚠ ou ✗ déclenche une correction obligatoire.

---

## 5. Hallucinations détectées et corrigées

Cette section est essentielle : elle documente les défaillances de l'IA et leur correction. Elle illustre pourquoi la vérification humaine reste indispensable, même avec des modèles avancés en 2026.

### 5.1 Première lecture critique du paper (Codex C1, première itération)

Codex a confabulé silencieusement les éléments suivants — tous présentés comme tirés du paper avec ancrages `(L.NN)` falsifiés :

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
| Bibliographie : 17 entrées avec auteurs et titres complets | Auteurs réinventés (Fisher, Thijs, Empatica, etc.) au lieu de Giourou, Sarmast, Kusmakar des vraies refs |

**Cause identifiée** : le prompt indiquait à Codex de lire le fichier paper. Codex semble avoir échoué silencieusement à lire (sandbox), n'a rien signalé, et a confabulé un contenu plausible pour un proceedings MDPI sur le sujet. Ce pattern correspond aux catégories « phantom code » et « fake precision » documentées dans l'audit Midwestnoob 2025 sur les hallucinations IA.

**Correction appliquée** : injection complète du texte du paper dans le prompt (au lieu d'un simple file path), demande d'auto-audit en fin de tâche, audit humain ligne par ligne après réception.

### 5.2 Confusion entre repo local et repo distant (Claude Code, Étudiant 5)

Lors de la phase de réflexion, l'orchestrateur (Claude Code) avait identifié une « incohérence » dans le repo Edge AI : le commit `f67ff0fd` aurait ajouté des features EEG-spécifiques sans régénérer les JSON de résultats.

**Vérification** : le commit `f67ff0fd` n'est en réalité présent que sur le remote GitHub, pas dans le checkout local. Le checkout local est à un état antérieur (`7521c27` + `5eba006`) où code et JSON sont parfaitement cohérents.

**Correction** : annulation du plan de régénération, conservation de l'état local cohérent. L'auteur a tranché en faveur de la stabilité plutôt que de l'extension.

### 5.3 Évaluation initiale erronée du SOTA C2

L'orchestrateur avait initialement déclaré l'output C2 « propre » après vérification de seulement 10 ancrages échantillonnés. Sur insistance de l'auteur (« si il y a une erreur a ne pas faire HALLUCINATION, tout doit verifie mot par mot »), le protocole a été durci : audit de 25 ancrages supplémentaires, puis grille systématique. C2 a finalement passé l'audit, mais le seuil de validation a été corrigé.

---

## 6. Décisions humaines vs IA

| Décision | Acteur | Justification |
|---|---|---|
| Choix du paper de référence | Étudiants Groupe 2 (humain) | Brief de cours |
| Choix du dataset SeizeIT2 pour la réplication | Étudiant 5 (humain) | Le paper Raman manque de patients réels |
| Choix de l'architecture MLP 80→32→16→1 | Étudiant 5 (humain) | Compromis taille/performance pour ESP32 INT8 |
| Choix du narratif « négatif honnête » (recall 9 %) | Étudiant 5 + Claude Code | Maturité scientifique École Doctorale |
| Choix de catcher les contradictions du paper | Étudiant 5 (humain, après lecture par Claude) | Différenciateur pour viser 19,5/20 |
| Choix de figer l'état local (Choix A') au lieu de pull `f67ff0fd` | Étudiant 5 (humain) | Stabilité et cohérence |
| Lecture critique détaillée du paper | Codex (sous supervision) | Tâche d'extraction/synthèse |
| Production HTML 20 slides | Codex (sous supervision) | Tâche de rédaction structurée |
| Audit final ligne par ligne | Étudiant 5 + Claude Code | Vérification humaine obligatoire |

L'humain reste seul décideur pour les choix scientifiques (positionnement, narratif, méthodologie). L'IA est utilisée pour l'exécution intensive (extraction, synthèse, rédaction), avec audit humain systématique.

---

## 7. Limites observées de l'IA en 2026

L'expérience de cette consolidation a révélé plusieurs limites concrètes :

**7.1 Hallucinations silencieuses sous contrainte de sandbox.** Quand Codex ne peut pas exécuter une opération demandée (lecture de fichier, exécution de script), il peut confabuler le résultat sans signaler l'échec. Mitigation : injection directe du contenu dans les prompts, demande d'auto-audit en fin de tâche, audit humain.

**7.2 Cascade d'erreurs en cas de non-vérification.** Si un output IA halluciné est consommé par un audit IA suivant, l'erreur se propage. Mitigation : ne jamais utiliser un audit IA comme validation finale ; toujours intercaler un audit humain.

**7.3 Coût élevé de la vérification mot par mot.** Atteindre une rigueur académique requiert un temps humain non négligeable, qui dépasse souvent le gain de temps d'écriture. Le bénéfice net de l'IA réside dans la qualité de la première ébauche structurée, pas dans l'élimination du travail humain.

**7.4 Limite des connaissances de l'IA sur la littérature scientifique récente.** L'IA peut citer des références plausibles mais inexistantes (références phantom). Mitigation : ne jamais accepter une référence sans vérification CrossRef ou DOI.

**7.5 Difficulté à reconnaître ses propres erreurs.** Les agents IA testés tendent à minimiser leurs hallucinations même quand ils sont confrontés à des preuves. Mitigation : confronter explicitement avec la source primaire et demander une révision.

---

## 8. Bilan quantitatif

| Phase | Effort humain estimé | Effort IA estimé | Ratio H/IA |
|---|---|---|---|
| Inventaire et extraction | 30 min | 2 h cumulées Codex | 1:4 |
| Réflexion stratégique | 90 min | 30 min Claude Code | 3:1 |
| Lecture critique paper | 45 min audit | 90 min Codex (1ʳᵉ + redo) | 1:2 |
| État de l'art SOTA | 30 min audit | 60 min Codex | 1:2 |
| Production HTML | en cours | en cours | indéterminé |
| Audit final ligne par ligne | 60 min (estimé) | nul | 1:0 |

L'IA accélère la production de contenu mais ne réduit pas le coût humain de la vérification. Sur des livrables à enjeu (note, thèse, publication), le ratio temps gagné par l'IA / temps consacré à l'audit humain est moins favorable qu'on pourrait le supposer.

---

## 9. Références utilisées

### 9.1 Source primaire (paper du groupe)

Raman, A. ; Velmurugan, N. *An Intelligent Internet of Medical Things-Based Wearable Device for Monitoring of Neurological Disorders*. Engineering Proceedings 2025, 106, 13. https://doi.org/10.3390/engproc2025106013

### 9.2 Références secondaires (citées dans le paper, validées)

Voir bibliographie complète dans `lecture_critique_raman_2025_v2.md` section F (17 entrées).

### 9.3 Sources additionnelles pour notre travail Edge AI (Étudiant 5)

- SeizeIT2 dataset, OpenNeuro ds005873.
- Documentation MicroPython v1.22.1 et ulab.
- TensorFlow Lite Micro (référencé pour discussion, non utilisé en pratique pour cette PoC).

### 9.4 Lectures méthodologiques sur l'IA générative

- Conventional Commits 1.0.0 (utilisé pour les commits du repo).
- Audit Midwestnoob 2025 sur les hallucinations IA (40,8 % de fabrication sur 283 tâches auditées).
- EU AI Act Title IV — Transparency provisions (justification de la trace IA).

---

## 10. Conclusion

Cette consolidation a montré que l'IA générative en 2026 est un outil d'accélération efficace, à condition d'imposer un protocole anti-hallucination strict et de maintenir l'humain comme dernier arbitre. Les hallucinations détectées et documentées dans cette trace ne sont pas accessoires : elles illustrent pourquoi l'usage non supervisé de l'IA dans des contextes scientifiques peut produire des livrables apparemment cohérents mais factuellement faux.

Le différenciateur de ce travail n'est pas l'usage de l'IA — beaucoup d'étudiants l'utilisent — mais la rigueur du protocole de vérification appliqué. La grille d'audit (`AUDIT_GRILLE.md`) et la checklist enseignante (`CHECKLIST_PROF.md`) sont des artefacts reproductibles, utilisables pour d'autres projets.

La présentation finale doit être lue par l'enseignante en gardant à l'esprit que chaque chiffre, chaque référence, chaque affirmation factuelle a été ancrée à une source primaire et vérifiée mot par mot avant l'envoi.
