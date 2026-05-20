# Claude Code — Complementary Q1 Research Roadmap

Date: 2026-05-20
Author: Claude Code
Status: proposal, not executed
Scope: complementary research directions that build on the same foundation as
Codex's `2026-05-20_q1_publishable_task_roadmap.md` but address different
scientific questions. Read Codex's doc first; this one is additive, not a
replacement.

## How this complements Codex's roadmap

Codex's roadmap converges on a single paper: an honest, leakage-safe benchmark
with forecastability atlas, calibration, null-corrected skill, and clinical
utility. That is a strong Q1 methodology contribution.

This document proposes **four additional paper directions**, each leveraging
the same infrastructure (frozen Gate C splits, null models, runner, calibration)
but answering a different scientific question. Each direction is anchored in a
research area that has advanced substantially in the last 12-24 months — in
some cases the last 3 months — and that Codex's track does not cover.

Each direction = one paper. Doing all four = thesis-level research program.

## Disclaimer on references

The recent literature pointers below are research DIRECTIONS, not phantom
citations. Each must be verified at the canonical primary source before
inclusion in any paper (PLAYBOOK §G phantom-citation rule, learned the hard
way in PR #2 review).

---

## Direction A — Mechanism: what does the model SEE?

Codex's track measures model performance honestly. This direction asks: when
the model predicts a seizure, what physiological signature is it actually
picking up? Mechanistic interpretability has become a frontier in ML
(Anthropic's sparse-autoencoder direction, the broader mechanistic
interpretability literature) but is essentially absent from wearable seizure
forecasting papers.

**Working paper title:** "Mechanistic Interpretability of Wearable Seizure
Forecasting: What the Model Sees and What the Clinician Should Believe"

**Why Q1:** wearable seizure-forecasting literature is data-rich but
mechanism-poor. A paper that opens the black box gets cited.

### Task M1 — Sparse autoencoders on the model encoder

Train sparse autoencoders (SAEs) on the hidden activations of the forecasting
model. Identify monosemantic features (HRV anomaly preceding seizure, circadian
phase shift, ACC stillness anomaly) and map them to clinical phenomena.

- Recency anchor: Anthropic SAE direction (2024 ongoing, more recent extensions
  to time-series).
- Effort: M. Risk: M (SAE training is sensitive to encoder quality).
- Deliverable: feature dictionary mapping SAE features → clinical narratives;
  ablation showing which features matter for correct vs incorrect predictions.

### Task M2 — Causal discovery on patient timelines

Apply causal discovery (PC, NOTEARS, neuro-symbolic causal methods) to identify
UPSTREAM causal factors of seizure occurrence beyond observational correlation.
"Sleep deprivation at night N causally precedes seizure on day N+1" is a
different claim than "correlation between sleep score and seizure."

- Recency anchor: causal time-series methods 2024-2026.
- Effort: L. Risk: H (causal inference on observational data is methodologically
  hard; assumptions matter).
- Deliverable: causal graph per patient or pooled, with documented assumptions
  and sensitivity analysis.

### Task M3 — Counterfactual probing

For each predicted seizure, what minimal alteration to the recent signal would
have prevented the alarm? Counterfactual explanations show which features the
model treats as causal vs spurious.

- Recency anchor: counterfactual explanation methods 2023-2026.
- Effort: M. Risk: M.
- Deliverable: per-prediction counterfactual narrative.

---

## Direction B — Personalization: each patient as their own benchmark

Wearable seizure forecasting is fundamentally per-patient. Standard ML treats
patients as IID; they are not. This direction takes per-patient individuality
seriously.

**Working paper title:** "Personalized Seizure Risk Estimation: Test-Time
Adaptation and Conformal Calibration for Wearable Devices"

**Why Q1:** matches the clinical reality of seizure forecasting; gives a
clinically actionable risk number with formal guarantees.

### Task P1 — Test-Time Adaptation (TTA) per patient

At deployment, the model adapts to the patient's recent data WITHOUT requiring
labels (entropy minimization, batch-norm statistics update, recent TTA methods
adapted for medical time-series). Pre-train on cohort; adapt online per patient.

- Recency anchor: TTA literature 2024-2026, including for medical time-series.
- Effort: M. Risk: M (TTA must not cross the leakage line — careful design
  required).
- Deliverable: TTA-equipped model with documented leakage-safe online updates;
  comparison to non-adapted baseline on per-patient sensitivity/FAR.

### Task P2 — Conformal Prediction with personal calibration

Output formal-coverage risk intervals: "patient X's seizure probability today
is 8% with 95% CI [3%, 15%]." Distribution-free guarantees under mild
assumptions. Critical for clinical safety.

- Recency anchor: conformal prediction under temporal/covariate shift,
  2024-2026 medical applications.
- Effort: M. Risk: L (well-established theory).
- Deliverable: per-patient conformal intervals; empirical coverage validation;
  clinical interpretation guide.

### Task P3 — Single-patient (N=1) longitudinal deep dive

Pick the longest-monitored MSG patient. Deep N=1 analysis: how does the
prediction evolve over months? Identify drift, distribution shift events,
adaptation behavior. Personalized-medicine N=1 methodology.

- Recency anchor: N=1 personalized medicine literature.
- Effort: S-M. Risk: L.
- Deliverable: longitudinal report per patient with annotated key events.

---

## Direction C — AI-assisted clinical science as a contribution itself

This is the meta-contribution. The work in this very repository — a human PI
plus multiple AI agents (Codex implements, Claude reviews) producing
forensic-quality clinical infrastructure — is itself novel and worth
documenting as a methodology paper. The Karpathy-style autoresearch direction
applied to a clinical case study.

**Working paper title:** "AI-Assisted Reproducible Clinical Benchmark
Development: A Case Study and Methodology" (target: methodology venue or
JMIR-class)

**Why Q1:** novel angle, no infrastructure cost (the case study IS this
project), aligns with the active AI-for-science direction.

### Task W1 — Document the AI-assisted workflow as a methodology

Extract from the project's git history and chat transcripts the explicit
collaboration pattern: who proposed what, who reviewed what, what failed in
review and was caught, what would have shipped without review. Quantify with
concrete numbers (e.g., for this session: "3/3 of the first SOTA-citation PRs
had at least one integrity issue caught in review — phantom URL, pre-Gate-C
labeling miss, silent-failure pattern. The 4th task, scoped via an explicit
written work order before implementation, merged with zero corrections and
18/18 tests passing.").

- Recency anchor: Karpathy autoresearch direction (2024-2025), FunSearch
  (DeepMind 2023+), AI Scientist (Sakana 2024), broader AI-for-science 2025.
- Effort: M (mostly forensic-trail analysis on existing artifacts).
- Risk: L.
- Deliverable: a methodology paper documenting the workflow with the project
  as the case study. The git history is the primary evidence.

### Task W2 — Active labeling for the clinical audit (also fixes our Phase B)

The current Phase B label audit is slow and expert-bound (and currently
"sampled human attestation, not full review"). Use uncertainty-aware sampling:
out of N candidate seizures to audit, which K (K << N) would be MOST
informative? Reduces clinician burden and DIRECTLY addresses this project's
current Phase B bottleneck.

- Recency anchor: active learning for medical data 2023-2026; uncertainty
  quantification + active sampling.
- Effort: M. Risk: L.
- Deliverable: a CLI that, given an audit budget K, selects the K most
  informative seizures to audit. Validation: synthetic + real showing the
  active-sampling audit catches the same label issues as the exhaustive audit
  with `N/K` × less clinician time.

This task pays off twice: it is an independent methodology contribution AND it
unblocks Phase B → Gate C.

### Task W3 — LLM-augmented clinical reasoning interface

Build a natural-language interface that grounds in the patient's data plus the
forecasting model. Patient or clinician asks: "I slept poorly last night, am
I at higher risk?" → system retrieves recent wearable data, queries the
forecasting model, generates a grounded response with uncertainty. Decision
support, not clinical recommendation (regulatory line).

- Recency anchor: clinical LLMs (Med-PaLM 2, Med42, clinical agent frameworks
  2025-2026).
- Effort: M-L. Risk: M (LLM hallucination risk; needs careful grounding).
- Deliverable: working prototype + evaluation against held-out reference
  responses.

---

## Direction D — Privacy and federation: scaling without exposing patients

Clinical data is jealously protected. A benchmark that hopes to scale needs to
handle data sovereignty. This is also the angle most aligned with the project's
IoT/edge identity.

**Working paper title:** "Privacy-Preserving Wearable Seizure Forecasting:
Federated Benchmark with Diffusion-Based Synthetic Augmentation"

**Why Q1:** clinically and policy-relevant; rides multiple active research
directions; differentiates the work from pure-modeling papers.

### Task F1 — Diffusion-based synthetic wearable trajectories

Train a diffusion model on real wearable signals that generates synthetic
trajectories preserving the statistical and temporal structure of real data
WITHOUT exposing individual patients. Validate that downstream forecasting
models trained on synthetic data perform similarly to real-trained models.

- Recency anchor: medical-data diffusion 2024-2026; synthetic clinical data
  privacy validation literature.
- Effort: L. Risk: M (diffusion training stability + privacy validation are
  both nontrivial).
- Deliverable: synthetic-data generator + privacy validation (no
  patient-identifiable patterns) + downstream performance comparison. Could
  be released as a dataset companion artifact.

### Task F2 — Federated benchmark protocol

Define a protocol where MSG, SeizeIT2, and future clinical sites can
participate WITHOUT sharing raw data. Local training, parameter aggregation,
optional differential privacy. Reference implementation against the existing
public datasets simulating local-only access.

- Recency anchor: federated medical ML 2024-2026; cross-cohort heterogeneity.
- Effort: L. Risk: M.
- Deliverable: protocol spec + reference implementation + comparison to
  centralized training on the same data (to quantify the cost of federation).

---

## Comparison with Codex's roadmap

| Dimension | Codex's emphasis | This document's emphasis |
|---|---|---|
| Number of papers | 1 (benchmark) | 4 (one per direction) |
| Posture | Retrospective: characterize what's there | Prospective: introduce new methodology |
| Engineering vs science | Engineering + statistics | Mechanism + personalization + AI workflow + privacy |
| Time horizon | 1-2 years (single paper) | 2-3 years (thesis-level program) |
| Risk profile | Lower; established methodology paper | Higher per direction; higher novelty per paper |
| Recency anchors | Forecasting reviews, SzCORE, SOTA in field | Mechanistic interpretability, TTA, conformal under shift, AI-for-science, diffusion privacy, federated medical |

These are complementary, not competing. Codex's roadmap delivers a foundational
benchmark paper; this roadmap turns that foundation into a research program.

## How these tasks couple to Codex's tasks

| Direction here | Depends on Codex's |
|---|---|
| M1/M2/M3 (mechanism) | Trained models from Task 14 (model ladder) + frozen Gate C (Task 6) |
| P1/P2/P3 (personalization) | Calibrated predictions from Task 5 + per-patient labels from frozen splits |
| W1 (workflow methodology) | None — uses existing git/chat history |
| W2 (active labeling) | Replaces or augments Codex's Task 7 (clinical timeline audit workbench) |
| W3 (LLM clinical interface) | Forecasting model from Task 14 + conformal calibration from Task P2 if used |
| F1/F2 (privacy/federation) | Frozen artifacts from Task 6 as the privacy-preservation reference |

## Suggested execution coupling

1. Codex executes its Tasks 5-8 (calibration, freeze, audit workbench, atlas).
2. In parallel, Task W1 (workflow methodology paper) — no engineering
   dependency, mostly forensic analysis on existing artifacts.
3. Task W2 (active labeling) is deployed BEFORE Task 7 (clinical timeline
   audit workbench) so the audit is bounded.
4. After Gate C: pick ONE among Direction A/B/D to anchor a second paper. The
   strongest scientific contribution is A (mechanism); the most patient-aligned
   is B (personalization); the most policy/IoT-aligned is D (privacy/federation).

## Minimum publishable units, ranked by feasibility

If single-paper Q1 push within 12 months:
- Codex's track is the highest-confidence single Q1 paper.
- W2 (active labeling) is the cleanest "novel + immediately implementable"
  parallel addition.

If two-paper push within 18-24 months:
- Codex's benchmark paper + W1 (AI-assisted workflow methodology) papered
  on top of it.

If thesis-level scope over 24-36 months:
- All four directions; each paper independent but sharing the same data
  and infrastructure base.

## Strongest individual recommendations

If I had to pick the top 3 tasks to start NOW (no Gate C dependency, immediate
value):

1. **W2 (active labeling for clinical audit).** Highest immediate utility:
   unblocks the project's actual current bottleneck (Phase B) AND yields a
   methodology paper. Win-win.
2. **W1 (AI-assisted workflow documentation).** Lowest cost (only forensic
   analysis on existing artifacts), genuinely novel angle (Karpathy
   autoresearch direction applied to a real clinical case study), high CV
   value for the PhD.
3. **P2 (conformal prediction with personal calibration).** Well-established
   theory, low risk, high clinical relevance. Slots cleanly into Codex's
   leaderboard runner via the `--reference-predictions` interface.

If aiming for the highest-novelty single contribution: **M1 (sparse
autoencoders on the encoder).** Highest scientific novelty per dollar of
effort; the seizure-forecasting literature has not opened the black box yet.

If aiming for the highest-policy-impact contribution: **F1 (diffusion-based
synthetic data).** Solves a real bottleneck in clinical AI (data sharing)
with a recent technical direction.

## Anti-patterns from this conversation — DO NOT reproduce in any of these papers

- No silent failure / silent fallback (Phase R C3 lesson).
- No phantom citation — every recent reference must be verified at canonical
  source before inclusion in any paper.
- No pre-Gate-C number presented as benchmark result.
- For Direction A especially: an interpretability claim is only as good as its
  verification that the interpretation matches the model's actual behavior.
  Don't ship plausible-but-untested interpretations.

## Conclusion

Codex's roadmap delivers a strong benchmark paper. This roadmap turns that
foundation into a multi-paper research program. Pick based on:

- **Time horizon** (12 months → Codex + W2; 24 months → add W1 or P2;
  36 months → all four directions).
- **CV positioning** (engineering thesis → Codex + F; methodology thesis →
  Codex + W; ML-science thesis → Codex + M; clinical thesis → Codex + P).
- **Risk appetite** (low → Codex only; medium → Codex + W; high → add M
  or D).

The single highest-leverage additional task right now is W2 (active labeling),
because it unblocks the project's current human-gated bottleneck AND yields an
independent methodology paper.
