# EpiTwin-Open Playbook

Single operating document. Last updated: 2026-05-15 (revision 2).

## What this is and how to use it

This playbook is the forward operating plan for EpiTwin-Open. Revision 2 changes
the **objective**, records a **scope decision**, and inserts a **certification
phase**. The gated critical-path discipline of revision 1 is carried forward.

It does not repeat work that already exists. Read these first, in order:

1. `PROJECT_STATUS.md` — current factual state of the package.
2. `docs/CLAUDE_REVIEW_2026-05-15.md` — strict methods review; the C/H findings.
3. `docs/CLAUDE_PHASE_R_AUDIT_2026-05-15.md` — audit of the Phase R remediation;
   the open punch list, the P0 blocker, the M2 closure checklist.
4. `docs/PUBLICATION_PROPOSAL.md` and `docs/SOTA_REVIEW_2026.md` — the intended
   paper and its SOTA framing.
5. `CODEX_HANDOFF_EpiTwin_Open_V1_V2_Two_Week_Plan.md` — construction plan and
   the Non-Negotiable Rules. This playbook supersedes its *sequencing*, never
   its scientific vision or its rules.

## 1. Objective — revision 2

> The objective is a **published contribution that is verifiably SOTA**. The
> manuscript is a formality — but only as an *output*: a formality *because*
> every claim was certified before it was written, not because the work is
> nearly done.

Read the next sentence before acting on the one above.

**This is a target, not the current state.** As of 2026-05-15 the Phase R audit
lists one **P0 blocker**, **M2 is not closed**, the benchmark is not frozen, and
no manual label audit has been done. "Verifiably SOTA" is *reached* by passing
the phase gates in section 5 — it is never asserted, never assumed.

What revision 2 changes: revision 1 ended at "write and submit". Revision 2
inserts **Phase G — certification** between the science and the writing. Nothing
is written until the contribution has survived a hostile review in rehearsal;
the manuscript (Phase H) then transcribes a certified result.

## 2. Locked orientation

The scientific orientation does not change:

> Wearable seizure forecasting must be evaluated as calibrated, patient-specific
> risk estimation under observability and alarm-burden constraints — not as
> naive preictal/interictal window classification.

The defensible contribution and its components are in
`docs/PUBLICATION_PROPOSAL.md`; do not restate them elsewhere. Hard SOTA
boundary: Nasseri et al., *Epilepsia* 2025 (DOI 10.1111/epi.18466) already
report non-invasive wearable seizure forecasting — EpiTwin-Open is **not** "the
first wearable seizure-forecasting system" and is never framed that way.
Forbidden claims: `CODEX_HANDOFF_*.md` and
`docs/HUMAN_INTERVENTION_CHECKPOINTS.md`, unchanged.

## 3. Scope — DECISION RECORDED

Revision 1 marked the Paper 1 / Paper 2 split DECISION REQUIRED and recommended a
benchmark-first cut with deep models deferred. **On 2026-05-15 Oussama decided
the full-package scope:** the first contribution is one paper containing the
open benchmark, the transparent baselines, the deep baselines (TCN/GRU),
**EpiTwin-SSL**, A100 training, and the forecastability/observability analysis.

This overrides the methods-review recommendation. Scope is Oussama's call, so
the override stands. It is recorded here with the three consequences the rest of
this playbook is built around:

1. **Sequencing does not change; A100 does not jump the queue.** A model trained
   on an unfrozen, unaudited, leaky benchmark yields a number that cannot be
   cited — methods review C1–C4, `CODEX_HANDOFF` Non-Negotiable Rule 3. Deep
   models and A100 stay **behind Gate C** (benchmark frozen) and Gate B (labels
   audited). Full scope changes *what* the paper contains, not the *order* in
   which it is built.
2. **The SOTA bar is now higher.** A protocol contribution is defended on
   novelty. A model contribution is *also* defended on performance, head-to-head
   with Nasseri 2025 and SeizureFormer 2026. Phase G must clear both.
3. **A negative model result is pre-accepted, now, in writing.** If the certified
   EpiTwin-SSL does not beat the transparent baselines or prior SOTA, the honest
   result — "EpiTwin-SSL does not yet outperform X on this benchmark" — is still
   publishable on the benchmark and protocol. Agreeing this here makes Gate G a
   measurement, not a crisis.

## 4. Where we are now

The scaffold is built and tested (`PROJECT_STATUS.md`). The 2026-05-15 methods
review found 4 Critical + 5 High findings; Phase R remediation closed some and
left a punch list — `docs/CLAUDE_PHASE_R_AUDIT_2026-05-15.md` has the detail,
including a **P0** over-exclusion bug that currently corrupts every MSG report on
disk. Real MSG is parsed (510/768 onsets matched); SeizeIT2 is a single subject.
Do not relitigate findings here — they live in the review and the audit with
file:line anchors.

## 5. Critical path

Each phase ends in a **gate**: a binary, checkable condition. A phase does not
start until the previous gate passes. No exceptions for A100 or paper claims.

### Phase A — Methods hardening
Close the review + audit punch list in the order of
`docs/CLAUDE_PHASE_R_AUDIT_2026-05-15.md` section 4: P0 first (C2 over-exclusion),
then P1 (C1 library + CLI bypass, C3 held-out + missing-column, H3 enforcement),
then P2. Owner: Codex implements remediation candidates; Claude Code closes.
**Gate A** — every code-closable item on the Phase R audit section 4 punch list
(P0, P1, P2) closed per the Definition of Done in section 8; the four section 4
policy items written up as decision briefs for Oussama + advisor; `uv run python
-m pytest -q` green; `uv run ruff check .` clean; a dated Claude Code re-review.
(Milestone M2 in the audit also requires the Phase B label audit; M2 closes
after Gate B and is not itself a gate here.)

### Phase B — Human label audit
Only after Gate A: C2 and H1 change which windows are labelled, so auditing
earlier wastes the audit. Verify 5–10 seizure timelines per dataset against
source annotations from the regenerated audit packets. Owner: Oussama — not
delegable.
**Gate B** — audit log committed (`reports/human_label_audit_<date>.md`); every
correction it surfaces applied and committed; packets regenerated.

### Phase C — Freeze the benchmark and pre-register
Decide and write the split policy; freeze the splits; run the fail-closed
leakage audit; `git tag` the frozen benchmark. Then **pre-register** the frozen
protocol and the planned Phase D–F analyses (Zenodo DOI) — this must precede any
reported run, so Phases D–F are confirmatory, not post-hoc. **DECISION RECORDED
(2026-05-19, `docs/GATE_A_DECISIONS_2026-05-19.md`)** — how to frame the
MSG long-horizon. The pre-remediation figure of
13 coverable test events (docs/CODEX_TO_CLAUDE_PHASE_R_REVIEW_2026-05-15.md)
was an artifact of the P0 over-exclusion bug; after the P0 fix, label
regeneration, and cluster-metric reporting (Codex Phase R2/R3) the
temporal-recording test split carries 54 seizure-level / 40 cluster-level
matched-coverable events — coverage-limited, not a collapse. Both
denominators and their per-baseline forecasted counts are recorded in
docs/CODEX_PHASE_R3_CLUSTER_AND_POSTICTAL_POLICY_2026-05-16.md (HR-tachycardia
46/54 seizure-level, 33/40 cluster-level). Decision: SPH60/SOP1440 is
presented as a coverage-limited demonstration with its matched-event
denominator stated inline, AND SOP 240 min (4 h) is also run as a
well-powered comparison horizon.
**Gate C** — split policy and the MSG-horizon decision both documented; frozen
splits committed and tagged; leakage audit clean with fit-scope metadata
present; the frozen protocol and planned analyses pre-registered with a DOI.
**Gate C unblocks Phase D and A100.**

### Phase D — Transparent baseline tables
Run random rate-matched, cycle, HR rule, ACC rule on the **frozen** splits with
the split-safe runners only.
**Gate D** — baseline tables produced; every metric annotated with its explicit
denominator, coverage fraction, and confidence interval; no number from the
`sweep.py` / `sweep_thresholds.py` path until C1 is closed.

### Phase E — Deep models and A100
TCN/GRU supervised baselines, then EpiTwin-SSL; A100 training per
`docs/A100_RUNBOOK.md`; the observable edge student and neuro-symbolic
constraints. Starts only after Gate D and
`docs/HUMAN_INTERVENTION_CHECKPOINTS.md` checkpoint 4.
**Gate E** — model results on the frozen benchmark; predictions carry fit-scope
metadata; leakage audit clean on model features; every A100 run reproducible
from a committed config.

### Phase F — Forecastability and observability analysis
The novelty: full-modality vs edge-modality observability matrix; matched-vs-
coverage selection-bias analysis; what is and is not observable from each
modality set, baselines and models together.
**Gate F** — observability matrix produced; the paper's central claim is
supported by the analysis or honestly bounded as a negative/limited result.

### Phase G — SOTA validation and certification
The phase that makes Phase H a formality. Four deliverables:
1. **Positioning matrix** — EpiTwin-Open vs Nasseri 2025, SeizureFormer 2026,
   SeizeIT2-ECG 2025, on protocol *and* model performance. Every cited SOTA
   source verified. The earlier `arXiv:2604.18297` phantom-citation concern was
   superseded by `docs/SOTA_CITATION_AUDIT_2026-05-18.md`; do not reclassify it
   as phantom without a fresh primary-source check.
2. **Reproducibility certification** — clean clone → one documented command →
   result tables reproduced to a documented numerical tolerance; a committed
   golden-numbers / golden-SHA non-regression test.
3. **Hostile-reviewer audit** — operationalize the Attack/Defense table of
   `docs/PUBLICATION_PROPOSAL.md`: each attack gets an evidence-anchored rebuttal
   or an honest limitation, in a dated audit document.
4. **Claims-surface clean-up** — confirm every manuscript claim is covered by
   the Phase C pre-registration and the certified artifacts, with no claim
   exceeding the pre-registered scope. Fix the `tibia` typo in
   `docs/HUMAN_INTERVENTION_CHECKPOINTS.md` and `README.md` (review L3).
**Gate G** — all four delivered; **advisor sign-off** that the contribution is
certified SOTA-defensible and reproducible.

### Phase H — Manuscript
Transcribe certified evidence into the table/figure plan of
`docs/PUBLICATION_PROPOSAL.md`. No new result is produced in this phase.
**Gate H** — draft assembled from Gate-G-certified artifacts only; supervisor
sign-off; submitted.

## 6. Decision gates

| Gate | Condition (binary) | Owner | Unblocks |
|---|---|---|---|
| A | Audit §4 punch list (P0/P1/P2) closed per section 8 DoD; policy items written as briefs; tests + ruff green; dated re-review | Codex + Claude Code + advisor | Phase B |
| B | 5–10 timelines/dataset audited; log committed; corrections applied; packets regenerated | Oussama | Phase C |
| C | Split policy + MSG-horizon decision documented; splits frozen + tagged; leakage audit clean; protocol pre-registered (DOI) | Oussama + Codex + advisor | Phase D, A100 |
| D | Transparent baseline tables with denominator + coverage + CI; no leaky-path number | Codex + Claude Code | Phase E |
| E | Model results on frozen benchmark; fit-scope metadata; leakage clean; A100 runs reproducible | Codex + Claude Code | Phase F |
| F | Observability matrix produced; central claim supported or honestly bounded | Oussama + advisor | Phase G |
| G | Positioning matrix + reproducibility + hostile-reviewer audit + claims clean-up; advisor sign-off | Claude Code + advisor | Phase H |
| H | Draft from certified artifacts; supervisor sign-off; submitted | Oussama | — |

## 7. Roles

- **Oussama (human, PhD candidate)** — strategic decisions (the section 3 scope),
  the manual label audit, the MSG-horizon decision, freeze approval, A100
  clearance, all paper claims, submission. The label audit and the claims are
  not delegable.
- **Codex** — implementation: review fixes as remediation candidates, phase
  deliverables, A100 runs.
- **Claude Code** — methods review and verification; closes findings; runs the
  Phase G certification.
- **advisor** — adjudicates the hard methodology calls flagged
  `Advisor-checkpoint` and signs off Gates A, C, F, G.

## 8. How Claude and Codex work — kaizen

The build/review loop works; the Phase R audit showed *how* it leaks. The
corrections, carried into every future phase:

- **"Closed" is a word reserved for Claude Code's dated re-review.** Codex
  produces a **remediation candidate**, never a "closed finding". The same holds
  for "verified", "certified", "SOTA": a claim of status is made only by the
  party that can prove it.
- **Definition of Done** for a finding — all four required:
  1. the fix is in the **library function**, not only the CLI that calls it;
  2. a **named mutation/falsification test** exists that fails if the finding
     reopens;
  3. **before/after diagnostic numbers** are in the commit body;
  4. a **dated Claude Code re-review** signs it closed.
- **Per-finding handoff line**, fixed format:
  `finding: <id> | fix: <file:line> | test: <name> | mutation it kills: <one
  line> | diagnostic: <before -> after>`.
- **Smaller cycles.** Hand off per finding or per small cluster, then review —
  not nine findings then one audit. Batching is how the Phase R P0 reached disk.
- **Keep what works.** Codex's commit trailers — `Verified-By`, `Falsifiability`,
  `Advisor-checkpoint` — stay mandatory; they are the forensic trail.

## 9. Codex — the three mistakes to avoid

From the Phase R audit (`docs/CLAUDE_PHASE_R_AUDIT_2026-05-15.md`). Avoid all
three on every future fix:

1. **Fix the root, not the entry point.** Phase R guarded the CLIs and left the
   library defaults unsafe — the "safety is opt-in" pattern the original review
   flagged, reproduced one layer up. Future model code imports library
   functions, not CLIs. Push every fix down into the library function; test the
   function directly.
2. **A fix must not introduce a new defect.** The C2 remediation created the P0
   over-exclusion because it was never tested against its own new edge case — a
   window both right-censored *and* forecast-positive. Every fix ships with a
   test of its own boundary, plus the before/after diagnostic.
3. **Never declare a finding closed without a test that proves it.** C1 was
   reported closed; a non-`split=` filter bypassed the guard — confirmed by
   running the CLI. Until the mutation test from section 8 exists and passes, it
   is a remediation candidate, not a closed finding.

Root cause of all three: **a claim of done outrunning the proof of done** — the
hallucination pattern in `COMMIT_GUIDELINES.md`. The Definition of Done in
section 8 is the single mechanism that closes all three.

## 10. Hard rules carried forward

From the handoff's Non-Negotiable Rules and the reviews. The three most often
violated under time pressure:

1. **No reported number before the benchmark is frozen (Gate C).** Full scope
   does not relax this — it raises the stakes, because A100 is now on the path.
2. **Never fit thresholds or normalization on test data**, and enforce it in the
   library function, not only the CLI.
3. **No A100 training and no clinical claim before Gates B and C are green.**

## 11. Project-specific anti-patterns

- Training EpiTwin-SSL or launching A100 before Gate C to "get a number" — the
  number cannot be cited; the compute is wasted until the benchmark is clean.
- Reporting a sensitivity without its denominator, coverage fraction, and CI.
- Treating "tests pass" as "the methods are sound" — the methods review exists
  because they are different things.
- "closed" / "certified" used by anyone other than the party that proved it.
- Burying a negative result — the MSG horizon collapse, or a model that does not
  beat its baselines — in a footnote instead of elevating it as a finding.

## 12. Maintaining this playbook

- When a gate passes, mark and date it in section 6.
- When the MSG-horizon decision (Phase C) is made, record it and the date here.
- Keep this file shorter than it wants to be. It is an operating plan, not a
  second copy of the review, the audit, or the publication proposal — link, do
  not duplicate.

### Changelog

| Date | Change |
|---|---|
| 2026-05-15 | Initial playbook (revision 1). Gated path to a benchmark-first Paper 1, deep models deferred to a Paper 2. |
| 2026-05-15 | Revision 2. Objective reframed to a published, verifiably-SOTA contribution with the manuscript as a downstream formality. Scope decision recorded (section 3): Oussama chose the full package — benchmark + deep baselines + EpiTwin-SSL + A100 in one paper. Added Phase G (certification) and Phase H (manuscript); added the Claude/Codex kaizen (section 8) and the three Codex mistakes (section 9) from the Phase R audit. |
| 2026-05-19 | Gate A policy half closed — the four Phase R policy decisions recorded in docs/GATE_A_DECISIONS_2026-05-19.md. MSG horizon: coverage-limited 24 h plus an added SOP 240 min comparison. Cluster metric: cluster-level primary, cluster_gap_minutes 240. Event denominator: both reported, coverable-matched primary. Postictal anchor: onset + 120 min (StatPearls NBK526004, Pottkämper et al. 2020). Remaining Gate A blocker: the Phase B manual label audit. |
