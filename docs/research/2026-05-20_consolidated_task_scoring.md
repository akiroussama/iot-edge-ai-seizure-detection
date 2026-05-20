# Consolidated task scoring — 27 research tasks (Codex + Claude roadmaps)

Date: 2026-05-20
Author: Claude Code
Scope: rank every task proposed in
`2026-05-20_q1_publishable_task_roadmap.md` (Codex, 16 tasks) and
`2026-05-20_claude_complementary_research_roadmap.md` (Claude, 11 tasks)
on a multi-criteria 100-point scale. Output: full ranking + top 3 to start
immediately (no blocker, high score, complementary).

## Scoring rubric (100 points)

The user emphasized that any task should be a continuous extension of the
current work, not a pivot or rewrite. Integration is therefore the heaviest-
weighted criterion.

| Criterion | Max | What it measures |
|---|---:|---|
| **Integration / Continuity** | 25 | How cleanly the task extends the current main state (infrastructure, lessons, file layout). Higher = no pivot required, builds directly on what is already merged. |
| **Impact** | 20 | Scientific or clinical significance if successful. Whether reviewers and downstream readers would care. |
| **Novelty** | 15 | Methodological or scientific novelty in the seizure-forecasting context. |
| **Publishability** | 15 | Probability of acceptance at a Q1 venue, methodology + venue fit. |
| **Citation potential** | 15 | Likelihood to be cited (broad audience, useful tool, addresses a real gap). |
| **Trends / Recency** | 10 | Riding a research direction active in the last 12-24 months. |

Each task scored honestly with the full 0-max range used; ties broken by
explicit dependency analysis.

## Full ranked table

| Rank | Task | Source | Integ | Impact | Novel | Pub | Cite | Trend | **Total** | Status |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | **Task 8 — Forecastability Atlas** | Codex | 23 | 19 | 13 | 15 | 12 | 8 | **90** | blocked on 5+6 |
| 2 | **W1 — AI-assisted workflow doc** | Claude | 25 | 16 | 13 | 13 | 12 | 10 | **89** | **unblocked** |
| 3 | **P2 — Conformal prediction** | Claude | 20 | 18 | 11 | 14 | 12 | 10 | **85** | **unblocked** |
| 4 | **W2 — Active labeling for audit** | Claude | 22 | 19 | 11 | 13 | 11 | 7 | **83** | **unblocked** |
| 5 | **M1 — Sparse autoencoders** | Claude | 14 | 17 | 15 | 13 | 13 | 10 | **82** | blocked on 14 |
| 6 | Task 18 — Clinical utility analysis | Codex | 18 | 16 | 11 | 13 | 11 | 8 | **77** | blocked on 5 |
| 7 | P1 — Test-time adaptation | Claude | 14 | 16 | 13 | 12 | 11 | 10 | **76** | blocked on 14 |
| 7 | Task 5 — Calibration/BSS report | Codex | 23 | 17 | 7 | 13 | 9 | 7 | **76** | **in flight (Codex)** |
| 9 | Task 12 — Observability/missingness | Codex | 16 | 14 | 12 | 13 | 10 | 9 | **74** | blocked on 5+6 |
| 10 | Task 9 — Multiday cycle features | Codex | 19 | 14 | 10 | 12 | 10 | 8 | **73** | unblocked |
| 11 | Task 11 — SeizeIT2 full-benchmark track | Codex | 16 | 17 | 8 | 13 | 11 | 7 | **72** | unblocked |
| 11 | M2 — Causal discovery | Claude | 12 | 16 | 14 | 10 | 11 | 9 | **72** | blocked on 14 |
| 13 | Task 16 — Edge-aware ablation | Codex | 18 | 13 | 10 | 12 | 10 | 8 | **71** | blocked on 14 |
| 13 | Task 19 — Failure taxonomy | Codex | 18 | 14 | 11 | 12 | 10 | 6 | **71** | blocked on 5+8 |
| 13 | F1 — Diffusion synthetic data | Claude | 10 | 14 | 14 | 11 | 12 | 10 | **71** | blocked on 6 |
| 16 | Task 6 — Gate C freeze + registry | Codex | 23 | 18 | 4 | 10 | 9 | 6 | **70** | **unblocked but human-gated (Phase B)** |
| 17 | W3 — LLM clinical interface | Claude | 9 | 13 | 13 | 11 | 11 | 10 | **67** | blocked on 14+P2 |
| 17 | Task 15 — Foundation-model transfer | Codex | 12 | 12 | 11 | 11 | 11 | 9 | **66** | blocked on 14 |
| 17 | Task 17 — Statistical robustness | Codex | 20 | 17 | 4 | 13 | 7 | 5 | **66** | blocked on 5 |
| 20 | M3 — Counterfactual probing | Claude | 13 | 13 | 11 | 10 | 8 | 7 | **62** | blocked on 14 |
| 20 | Task 7 — Audit workbench UI | Codex | 20 | 17 | 7 | 7 | 6 | 5 | **62** | unblocked, but W2 is a stronger angle |
| 22 | F2 — Federated benchmark protocol | Claude | 8 | 14 | 11 | 10 | 10 | 7 | **60** | blocked on 6 |
| 23 | P3 — N=1 longitudinal deep dive | Claude | 16 | 11 | 9 | 9 | 7 | 7 | **59** | blocked on 14 |
| 23 | Task 20 — Paper artifact package | Codex | 20 | 13 | 3 | 13 | 5 | 5 | **59** | blocked on everything else |
| 25 | Task 13 — Patient-adaptive hierarchical baselines | Codex | 18 | 11 | 7 | 10 | 7 | 5 | **58** | blocked on 5 |
| 26 | Task 14 — Small supervised model ladder | Codex | 17 | 12 | 3 | 12 | 6 | 4 | **54** | blocked on 6 |
| 27 | Task 10 — External SOTA reproduction | Codex | 17 | 12 | 5 | 8 | 6 | 5 | **53** | blocked on 14 |

## Top 3 to do RIGHT NOW (unblocked + highest score)

**Selection criterion:** score ≥ 80 AND no blocker (no dependency on
unfinished Codex tasks, no Gate C dependency, can productively start today).

### 🥇 W1 — Document the AI-assisted workflow as methodology (89)

**Why right now:** zero infrastructure cost. The case study IS this project's
git history + chat transcripts, all already available. Codex doing Task 5 in
parallel is in fact additional case-study evidence as it accrues.

**Why high score:** Integration 25 (maximum — uses only existing artifacts);
Trends 10 (maximum — Karpathy autoresearch / AI Scientist / FunSearch
direction is among the hottest in 2025-2026 ML and AI-for-science venues);
Novelty 13 (the application to a real clinical benchmark with forensic-grade
audit trail is novel — most AI-for-science case studies are math / pure ML).

**What it delivers concretely:**
- Forensic extraction from git log + chat: who proposed what, what failed in
  review, what would have shipped without review.
- Quantified findings (e.g., "3/3 first SOTA-citation PRs had ≥1 integrity
  issue caught in review; Task 4 with explicit upfront work order merged with
  0 corrections and 18/18 tests passing").
- Methodology paper documenting the human-AI collaboration pattern as a
  reproducible workflow for safety-critical clinical infrastructure.

**Estimated effort:** 2-3 weeks of forensic analysis + writing.

### 🥈 P2 — Conformal Prediction with personal calibration (85)

**Why right now:** the Task 3 leaderboard runner is already on main. P2 can
be implemented as a new metric layer that consumes existing predictions
(null models from Task 4 + the existing MSG rule baselines) and emits
formal-coverage intervals. No need to wait for Gate C — methodology and
tests can be built on synthetic + the existing pre-freeze exploratory
predictions.

**Why high score:** Impact 18 (formal-coverage clinical risk intervals are
directly actionable — "patient X has 8% risk with 95% CI [3%, 15%]" is
clinically meaningful in a way that a single threshold isn't); well-
established theory (low risk); slots cleanly into the existing infrastructure.

**What it delivers concretely:**
- A new `src/calibration/conformal.py` module implementing split / online
  conformal with patient-level calibration.
- CLI: `scripts/run_conformal_calibration.py` that consumes prediction
  tables (same format as the leaderboard runner) and emits per-patient
  prediction intervals.
- Validation tests for empirical coverage (synthetic guarantees + a
  pre-Gate-C exploratory run on existing predictions, labeled as such).

**Estimated effort:** 2-3 weeks.

### 🥉 W2 — Active labeling for the clinical audit (83)

**Why right now:** double payoff. It addresses **this project's actual
current bottleneck (Phase B manual audit, currently "PASS partout" by
attestation only)** AND yields an independent methodology paper. The current
Phase B path needs ~20 lines of clinical observation notes per dataset
(per my prior review). Active labeling reduces "which seizures to audit"
from "all 883 + 768" to "the K most informative" — orders of magnitude less
clinician burden.

**Why high score:** Integration 22 (extends current Phase B infrastructure
+ uses Task 3 runner predictions); Impact 19 (unblocks the project's actual
gate); implementable today with the existing predictions + null models.

**What it delivers concretely:**
- A `src/active/uncertainty_sampling.py` module with multiple acquisition
  functions (max entropy, BALD, expected model change).
- CLI: `scripts/select_audit_targets.py` that takes a prediction table +
  audit budget K → outputs the K most informative seizures to review.
- Empirical validation: a synthetic test where the active-K audit catches
  the same proportion of label errors as the exhaustive N-audit.
- Direct usable artifact for closing this project's Phase B gate properly.

**Estimated effort:** 2-3 weeks.

## Honorable mentions — high score but blocked

These score in the top tier but cannot start "right now" because of a
dependency:

- **Task 8 — Forecastability Atlas (90)** — highest score overall, but
  blocked on Codex's Task 5 (in flight) and Task 6 (Gate C freeze, not
  started). Becomes the natural NEXT task after Codex finishes the
  calibration/BSS infrastructure.
- **M1 — Sparse autoencoders (82)** — needs a trained model (Task 14)
  before SAE training has anything to interpret. Highest scientific
  novelty in the entire list.
- **Task 18 — Clinical utility analysis (77)** — needs Task 5 calibration
  outputs.

## Path-dependence map (which tasks unlock which)

Critical path through the highest-scoring tasks:

```
Phase B audit (HUMAN, current bottleneck)
    │
    ├── Codex Task 5 (calibration/BSS, in flight)
    │       │
    │       ├── Codex Task 6 (Gate C freeze)
    │       │       │
    │       │       ├── Codex Task 8 (forecastability atlas) ←—— 90
    │       │       ├── Codex Task 14 (model ladder)
    │       │       │       │
    │       │       │       ├── M1 sparse autoencoders ←—— 82
    │       │       │       ├── P1 TTA ←—— 76
    │       │       │       └── M2 causal discovery ←—— 72
    │       │       │
    │       │       ├── F1 diffusion synthetic ←—— 71
    │       │       └── F2 federated ←—— 60
    │       │
    │       ├── Codex Task 18 clinical utility ←—— 77
    │       └── Codex Task 17 statistical robustness ←—— 66
    │
    └── W2 active labeling (UNBLOCKED, can run today) ←—— 83
            │
            └── reduces Phase B clinician burden → unblocks Gate C earlier

UNBLOCKED IN PARALLEL (no dependencies):
- W1 workflow methodology (89) — uses only existing artifacts
- P2 conformal prediction (85) — uses Task 3 runner already on main
- W2 active labeling (83) — uses existing predictions
- Codex Task 9 multiday cycle features (73) — extends null models
- Codex Task 11 SeizeIT2 full track (72) — uses raw data already on Hetzner
```

## Caveats on the scoring methodology

- The scores are an honest single-reviewer judgment, not a community
  consensus. A second reviewer (or an advisor) might shift ±5-10 points
  per task. The relative ranking (top-tier vs middle-tier vs bottom-tier)
  is more robust than the absolute number.
- "Citation potential" is the most speculative criterion — actual citation
  trajectory depends on venue, timing, and execution quality far more than
  on intrinsic merit.
- "Trends" weight is intentionally modest (10/100) to avoid chasing fashion
  at the expense of durable contribution.
- Integration weight is intentionally heavy (25/100) per the user's
  explicit "extension, not pivot" framing.
- Tasks scoring 50-65 are not bad; they are usually solid engineering
  components that don't shine alone but contribute to the paper package.

## Recommendation

**Start W1, P2, and W2 now in parallel.** They are independent of each
other and of Codex's in-flight Task 5; together they cover three distinct
contribution axes (methodology of AI-assisted science, formal-coverage
clinical prediction, audit-burden reduction) without duplicating Codex's
benchmark-paper track.

After Codex's Task 5 + Task 6 complete, the natural top priority becomes
**Task 8 (Forecastability Atlas, 90)** as the Q1 paper's headline figure,
followed by **Task 14 (model ladder)** to unlock M1 and P1.
