# Vérification du recall RF — réponse au feedback de Mme Manel

Date : 2026-05-09
Source brute : `04_improve/results/multirun_loso.csv` (CSV par sujet) et `04_improve/results/multirun_loso_summary.json` (agrégé).
Pipeline : `04_improve/src/train_multirun.py` (LOSO 6 sujets SeizeIT2).

## 1. Le feedback de la prof

> « Pour Recall du RF, je pense qu'il y a une erreur dans votre calcul. Revérifiez SVP. »

Confirmé : ce qu'on a annoncé (recall ≈ 9 %) est la **macro-moyenne par sujet**, pas la sensibilité globale. La vraie sensibilité globale (micro / pooled) est **3.25 %**, plus défavorable.

## 2. Données brutes par sujet (RF, LOSO)

Extrait direct de `multirun_loso.csv`, lignes 4, 7, 10, 13, 16, 19 :

| Sujet | TP | FN | n_test_pos | Recall sujet (TP / n_test_pos) |
|---|---:|---:|---:|---:|
| sub-001 | 0 | 114 | 114 | 0.0000 |
| sub-032 | 0 | 116 | 116 | 0.0000 |
| sub-085 | 23 | 35 | 58 | 0.3966 |
| sub-096 | 5 | 32 | 37 | 0.1351 |
| sub-124 | 1 | 344 | 345 | 0.0029 |
| sub-125 | 0 | 223 | 223 | 0.0000 |
| **Σ** | **29** | **864** | **893** | — |

## 3. Les deux agrégats possibles

### 3.1 Macro recall (ce qu'on a publié)

```
recall_macro = mean(recall_par_sujet)
             = (0.0000 + 0.0000 + 0.3966 + 0.1351 + 0.0029 + 0.0000) / 6
             = 0.5346 / 6
             = 0.08910
             ≈ 8.9 %
```

Code source : `train_multirun.py:153-157` — `np.mean(vals)` sur la liste des recalls par sujet.

Std associé : 0.146 — supérieur à la moyenne. Distribution **fortement skewed** : 4 sujets à 0 %, sub-085 à 39.66 %, sub-096 à 13.51 %.

### 3.2 Micro recall (pooled)

```
recall_micro = sum(TP) / sum(n_test_pos)
             = (0 + 0 + 23 + 5 + 1 + 0) / (114 + 116 + 58 + 37 + 345 + 223)
             = 29 / 893
             = 0.03247
             ≈ 3.25 %
```

Sémantique : « Sur les 893 fenêtres de crise réelles dans le dataset, combien le RF en a-t-il détectées ? » → 29 sur 893.

## 4. Pourquoi les deux divergent autant

Le micro recall pondère chaque fenêtre de crise de la même manière. Le macro recall pondère chaque **sujet** identiquement, peu importe le nombre de crises.

- Sub-085 (58 positives, 6.5 % du total) atteint 39.66 % de recall et tire la macro vers le haut.
- Sub-124 (345 positives, 38.6 % du total) plafonne à 0.29 % de recall et tire la micro vers le bas.

En contexte clinique IoMT (« on veut détecter les crises réelles avant qu'elles affectent le patient »), c'est le **micro recall** qui répond à la bonne question.

## 5. Conséquence sur le narratif

Avant correction :

> « Sur SeizeIT2 LOSO, RF atteint un recall de 9 %, contre 100 % annoncé par les auteurs. »

Après correction (à propager dans tous les artefacts) :

> « Sur SeizeIT2 LOSO, RF détecte 29 crises sur 893 (recall pooled = 3.25 %), contre 100 % annoncé par les auteurs.
> En macro per-subject, le recall moyen est 8.9 % avec un écart-type de 14.6, dominé par un seul sujet (sub-085) à 39.7 %. »

Le résultat reste cohérent avec notre critique du paper : la méthode des auteurs ne généralise pas en LOSO sur patients réels. La correction renforce le diagnostic, ne le contredit pas.

## 6. Sanity check croisé : la cohérence accuracy / recall / prévalence

Prévalence positives : 893 / 33925 = 2.63 %.
Baseline trivial « tout négatif » : accuracy = 1 - 0.0263 = 0.9737 = 97.37 %.

Accuracy pooled RF (recalculée à partir du CSV) :

```
TP + TN total = 29 + (22919 + 2181 + 2695 + 2227 + 1996 + 984)
             = 29 + 33002
             = 33031
accuracy_pooled = 33031 / 33925 = 0.97366 ≈ 97.4 %
```

L'accuracy macro publiée (93.06 %) est l'agrégat moyenné par sujet, qui sous-représente l'accuracy pooled. Même phénomène que pour le recall.

**Constat important** : le RF en pooled atteint exactement le baseline trivial (≈97.4 %) — autrement dit, il prédit presque toujours « pas de crise ». Cohérent avec un recall de 3.25 % et une FPR de 0.04 %.

## 6 bis. Cause profonde de l'erreur (analyse honnête)

Ce n'était PAS une hallucination de Claude. Le 9 % vient d'un fichier réel sorti d'un pipeline qui a tourné, et l'arithmétique `(0+0+0.3966+0.1351+0.0029+0)/6 = 0.0891` est correcte.

C'est une erreur méthodologique en 4 fautes empilées :

1. **Choix de l'agrégateur dans le script** (`train_multirun.py:153-157`).
   Le code calcule `np.mean(per_subject_recalls)` par réflexe sklearn (équivalent de `cross_val_score`). Pour un problème clinique très déséquilibré multi-patients, le bon agrégateur est micro/pooled (`sum(TP)/sum(N_pos)`). Le choix n'a pas été questionné au moment de l'écrire.

2. **Sanity check baseline jamais appliqué.**
   Prévalence 2,63 % → baseline trivial "tout négatif" = 97,37 %. Notre RF accuracy macro 93,06 % est SOUS le baseline. C'est un signal d'alarme cardinal en imbalanced classification, jamais vérifié avant publication.

3. **Variance ignorée.**
   `recall_std = 0.146 > recall_mean = 0.089`. Quand l'écart-type dépasse la moyenne, la distribution est trop skewed pour qu'une moyenne ait un sens. Le signal était dans le JSON ligne 16, à côté du 0.089. Personne ne s'y est arrêté.

4. **Propagation sans vérification croisée.**
   Le 9 % a été repris dans la slide, le speech, le mail, le Teams et le briefing Codex. À aucune étape la valeur n'a été recroisée avec le CSV brut par sujet, alors que la discipline anti-hallucination du briefing l'exigeait.

Responsabilité : Codex pour le choix d'agrégateur par défaut dans le script ; Claude orchestrateur pour l'absence de sanity check baseline et la propagation aveugle dans 5 artefacts. Pas une hallucination ponctuelle, mais une erreur méthodologique propagée — plus traîtresse car interne-cohérente.

Garde-fou à ajouter dans le pipeline pour la suite : `from sklearn.dummy import DummyClassifier` comme baseline systématique, et exposition côte à côte de macro et micro dans le JSON.

## 7. Action items

1. ✅ Document de vérification produit (ce fichier).
2. ⏳ Mettre à jour le narratif dans `presentation_groupe2_v1.html` (slides résultats E5).
3. ⏳ Mettre à jour `TRACE_IA.md` (ajouter une entrée « erreur détectée par la prof, corrigée »).
4. ⏳ Mettre à jour le `README.md` du repo `iot-edge-ai-seizure-detection`.
5. ⏳ Modifier `train_multirun.py` pour exposer micro ET macro dans le JSON (rigueur scientifique).
6. ⏳ Ajouter une slide ou une note de bas de page expliquant la distinction.
7. ⏳ Réponse honnête à la prof sur Teams.

## 8. Ancrages anti-hallucination

- Source brute par sujet : `D:\doctorat\cours\iot\groupe2\04_improve\results\multirun_loso.csv` lignes 4, 7, 10, 13, 16, 19 (RF uniquement).
- Source agrégée : `D:\doctorat\cours\iot\groupe2\04_improve\results\multirun_loso_summary.json` lignes 11-22.
- Code agrégation : `D:\doctorat\cours\iot\groupe2\04_improve\src\train_multirun.py:148-162`.
- Tous les TP/FN cités dans la table §2 sont vérifiables ligne par ligne dans le CSV.
