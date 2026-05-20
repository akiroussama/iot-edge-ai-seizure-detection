# Fused Task Scoring — Codex Challenge Of Claude Ranking

Date: 2026-05-20
Author: Codex
Base: `origin/main@873e299`
Input document: `docs/research/2026-05-20_consolidated_task_scoring.md`
Status: decision support for next implementation tasks.

## Purpose

Claude produced a consolidated 27-task ranking with a 100-point rubric. This
document challenges that ranking from the perspective of the post-Task-5 main
branch, then computes a fused score:

```text
fused_score = 0.5 * claude_score + 0.5 * codex_score
```

The output is meant to choose the next TOP 3-5 tasks to implement and
integrate, not to choose side-paper ideas in isolation.

## Current Main State

As of this document, Task 5 is merged on main:

- PR #7 merged as `873e299 feat(reports): add calibration bss reports (#7)`.
- Calibration/BSS/null-corrected reporting exists.
- Task 4 constrained nulls exist.
- Task 3 leaderboard runner exists.

This changes the dependency map. Any task that was blocked only on Task 5 is
now at least methodologically unblocked, although real-data claims remain
blocked by Gate C.

## Challenge To Claude's Ranking

Claude's ranking is useful, but I disagree with three structural choices.

First, W1 is over-scored for the immediate thesis path. AI-assisted workflow
documentation is interesting and cheap, but it is a side-methodology paper. It
does not unlock citable seizure-forecasting results, Gate C, model comparison,
or the main benchmark thesis. I lower W1 materially.

Second, Gate C and benchmark-comparison tasks are under-scored. A Q1 reviewer
will not accept pre-freeze exploratory numbers, and they will not accept a
paper without strong external comparison. Task 6, Task 10, Task 11, Task 17,
and Task 18 are therefore more central than Claude's table suggests.

Third, high-trend/pivot tasks are over-scored. Diffusion synthetic data,
federation, LLM clinical interfaces, causal discovery, and sparse
autoencoders may become good thesis branches later, but they are not the
shortest path to a publishable extension of the current EpiTwin benchmark.

## Codex Rescoring Principles

I used the same 100-point spirit as Claude, but shifted the emphasis:

- Reward tasks that unlock citable benchmark claims after Task 5.
- Reward tasks that strengthen the main EpiTwin-Open paper, not only a side
  paper.
- Penalize regulatory, privacy, interpretability, or causality tasks when they
  require a trained model, private data, or assumptions not yet available.
- Treat "unblocked engineering" and "citable result" separately.
- Keep negative-result value high: failure taxonomy, observability, and
  clinical utility are not secondary; they are how the paper becomes honest.

## Fused Ranking

| Rank | Task | Source | Claude | Codex | Fused | Current status |
|---:|---|---|---:|---:|---:|---|
| 1 | **Task 8 — Forecastability Atlas** | Codex | 90 | 93 | **91.5** | blocked on Task 6 |
| 2 | **W2 — Active labeling for audit** | Claude | 83 | 86 | **84.5** | unblocked |
| 3 | **P2 — Conformal prediction** | Claude | 85 | 79 | **82.0** | unblocked methodology |
| 4 | **Task 18 — Clinical utility analysis** | Codex | 77 | 86 | **81.5** | unblocked after Task 5; citable after Task 6 |
| 5 | **Task 11 — SeizeIT2 full-benchmark track** | Codex | 72 | 87 | **79.5** | unblocked |
| 6 | **Task 9 — Multiday cycle features** | Codex | 73 | 84 | **78.5** | unblocked |
| 7 | **Task 6 — Gate C freeze + registry** | Codex | 70 | 87 | **78.5** | urgent; human-gated |
| 8 | **Task 19 — Failure taxonomy** | Codex | 71 | 82 | **76.5** | best after Task 8 / Task 18 |
| 9 | **W1 — AI-assisted workflow doc** | Claude | 89 | 63 | **76.0** | unblocked, but side paper |
| 10 | **Task 5 — Calibration/BSS report** | Codex | 76 | 76 | **76.0** | done / merged |
| 11 | **Task 12 — Observability/missingness** | Codex | 74 | 78 | **76.0** | partly blocked on frozen artifacts |
| 12 | **Task 17 — Statistical robustness** | Codex | 66 | 84 | **75.0** | unblocked after Task 5; citable after Task 6 |
| 13 | **M1 — Sparse autoencoders** | Claude | 82 | 64 | **73.0** | blocked on Task 14 |
| 14 | **Task 7 — Audit workbench UI** | Codex | 62 | 81 | **71.5** | unblocked |
| 15 | **Task 16 — Edge-aware ablation** | Codex | 71 | 72 | **71.5** | blocked on trained models |
| 16 | **Task 10 — External SOTA reproduction** | Codex | 53 | 88 | **70.5** | unblocked for at least one family |
| 17 | **P1 — Test-time adaptation** | Claude | 76 | 61 | **68.5** | blocked on Task 14; leakage risk |
| 18 | **Task 13 — Patient-adaptive hierarchical baselines** | Codex | 58 | 78 | **68.0** | unblocked methodology |
| 19 | **Task 20 — Paper artifact package** | Codex | 59 | 74 | **66.5** | blocked on core results |
| 20 | **Task 14 — Small supervised model ladder** | Codex | 54 | 79 | **66.5** | blocked on Task 6 for citable runs |
| 21 | **Task 15 — Foundation-model transfer** | Codex | 66 | 61 | **63.5** | blocked on Task 14 / licensing |
| 22 | **P3 — N=1 longitudinal deep dive** | Claude | 59 | 66 | **62.5** | blocked on Gate C / patient selection |
| 23 | **M3 — Counterfactual probing** | Claude | 62 | 58 | **60.0** | blocked on Task 14 |
| 24 | **M2 — Causal discovery** | Claude | 72 | 47 | **59.5** | high-risk assumptions |
| 25 | **F2 — Federated benchmark protocol** | Claude | 60 | 54 | **57.0** | blocked; pivot risk |
| 26 | **F1 — Diffusion synthetic data** | Claude | 71 | 41 | **56.0** | blocked; pivot/privacy burden |
| 27 | **W3 — LLM clinical interface** | Claude | 67 | 43 | **55.0** | blocked; regulatory/pivot risk |

## Top 5 Overall By Fused Score

These are the highest-value tasks regardless of blocker:

1. **Task 8 — Forecastability Atlas** (`91.5`)
2. **W2 — Active labeling for audit** (`84.5`)
3. **P2 — Conformal prediction** (`82.0`)
4. **Task 18 — Clinical utility analysis** (`81.5`)
5. **Task 11 — SeizeIT2 full-benchmark track** (`79.5`)

Interpretation: Task 8 is still the future headline figure, but it is not the
first implementation task because it needs Gate C/frozen artifacts. The
highest-value unblocked scientific-engineering work is W2, P2, T18, and T11.

## Top 5 To Execute Now

This list is not the same as the global ranking. It accounts for blockers and
for the fact that Task 5 is now merged.

### 1. Task 6 — Gate C freeze + registry

Fused score: `78.5`

Why first despite not being the highest score: it unlocks citable results and
unblocks Task 8. Without Task 6, everything remains "pre-Gate-C exploratory".
It is not glamorous, but it is the gate between infrastructure and publishable
science.

Immediate implementation shape:

- artifact registry schema;
- split manifest;
- checksum/row-count/event-count verifier;
- guardrail that refuses citable leaderboard rows without frozen artifacts;
- synthetic tests first, real freeze only after human audit approval.

### 2. W2 — Active labeling for audit

Fused score: `84.5`

Why now: it attacks the human bottleneck directly. It should not replace the
audit workbench; it should decide what the audit workbench shows first.

Immediate implementation shape:

- `src/active/audit_selection.py`;
- acquisition scores: uncertainty, disagreement vs nulls, high clinical
  leverage, censoring/edge-case density;
- CLI `scripts/select_audit_targets.py`;
- output CSV for clinician review budget K;
- synthetic test showing active-K catches injected label defects better than
  random-K.

### 3. P2 — Conformal prediction

Fused score: `82.0`

Why now: Task 5 created the calibration/BSS layer; conformal prediction is the
next formal uncertainty layer. It strengthens clinical interpretability without
requiring large models.

Immediate implementation shape:

- split conformal and patient-calibrated conformal utilities;
- CLI consuming prediction tables;
- empirical coverage tests on synthetic data;
- report fields that remain explicitly pre-Gate-C unless frozen artifacts are
  supplied.

### 4. Task 18 — Clinical utility analysis

Fused score: `81.5`

Why now: after Task 5, we can evaluate not only "skill" but usefulness under
alarm burden. Clinical utility turns calibration and false alarms into a
decision-relevant figure/table.

Immediate implementation shape:

- utility curves over sensitivity, FAR/day, TIW, lead time, and BSS;
- configurable cost assumptions;
- alarm policy consolidation;
- no clinical recommendation, only decision-support analysis.

### 5. Task 9 — Multiday cycle features

Fused score: `78.5`

Why now over W1: it strengthens the core seizure-forecasting science. Long-term
cycles are central in wearable forecasting, and Task 4 currently only covers
hour-of-day nulls. This is a direct extension, not a side paper.

Immediate implementation shape:

- circadian/weekly/multiday phase features;
- rolling-origin fit to avoid future leakage;
- randomized-time negative control;
- comparison against Task 4 hour-of-day null.

## What I Would Not Do Next

I would not start W1 as an engineering priority. It is useful, but it should be
handled as a writing/forensics stream in parallel, not as the main next code
task.

I would not start M1, P1, M2, M3, F1, F2, W3, or foundation-model transfer
until we have frozen artifacts and at least one stable supervised model ladder.
They are thesis-expansion tasks, not next-integration tasks.

I would not delay Gate C for another attractive modeling idea. The largest
scientific risk is still that the project accumulates impressive pre-freeze
artifacts that remain uncitable.

## Recommended Execution Plan

If we take command fully and stop waiting for Claude review, the next sequence
should be:

1. **Task 6 — Gate C registry engineering scaffold.**
2. **W2 — Active audit target selection.**
3. **P2 — Conformal prediction layer.**
4. **Task 18 — Clinical utility report.**
5. **Task 9 — Multiday cycle features.**
6. **Task 8 — Forecastability Atlas** as soon as Task 6 makes outputs citable.

This sequence preserves the core Q1 thesis:

```text
frozen public wearable benchmark
+ constrained nulls
+ calibration/BSS
+ active clinical audit
+ formal uncertainty
+ clinical utility
+ multiday cycles
+ forecastability atlas and publishable benchmark paper
```

## Final Decision

The next code task should be **Task 6 — Gate C freeze + registry**, even though
its fused score is lower than W2/P2. Reason: it unlocks the highest-value task
overall, Task 8, and turns the project from "well-engineered exploratory
benchmark" into "citable scientific artifact".

If the user wants the most immediately novel method instead of the strongest
benchmark unlock, choose **W2 active audit selection**.
