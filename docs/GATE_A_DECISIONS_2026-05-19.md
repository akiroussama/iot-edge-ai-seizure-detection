# Gate A — policy decisions sign-off

Date: 2026-05-19
Decider: Oussama Akir (PhD candidate, project lead).
Recorded by: Claude Code.
Decision frame: `docs/PHASE_R_DECISION_BRIEFS_2026-05-17.md`.
Independent input: `docs/PHASE_R_DECISION_BRIEFS_ADVISOR_2026-05-17.md`.

This document records Oussama's decision on the four Gate A policy items
from the Phase R audit (`docs/CLAUDE_PHASE_R_AUDIT_2026-05-15.md` §4). The
Phase R code punch list is already closed (`docs/CLAUDE_PHASE_R_REREVIEW_2026-05-17.md`,
`docs/CLAUDE_CODEX_WORKORDER_REREVIEW_2026-05-18.md`). With these four
decisions recorded, the policy half of Gate A is closed; the remaining
Gate A blocker is the Phase B manual label audit (Oussama, not delegable).

Oussama followed the advisor's recommendation on all four items.

## Decision 1 — MSG long-horizon framing (Brief 1)

**Decided.** The MSG SPH 60 min / SOP 1440 min (24 h) task is kept and
presented explicitly as a *coverage-limited demonstration* — denominator
stated inline, not a benchmark results table — AND a shorter, well-powered
horizon is also run as a comparison: **SOP 240 min (4 h)**.

Rationale: at SOP 1440 the temporal-test split carries only 54
seizure-level coverable events — too small a denominator for a headline
clinical claim. At SOP 240 the coverable count rises substantially (most
Empatica segments exceed 4 h), giving a well-powered comparison number.
Reporting both is more honest, and more publishable, than picking one.

Matches the advisor recommendation (brief options b + c).

## Decision 2 — H1 seizure-cluster metric unit (Brief 2)

**Decided.** For MSG long-horizon event metrics the primary unit is
**cluster-level**; seizure-level is reported as a secondary table. The
cluster gap is pre-registered at **`cluster_gap_minutes = 240`** — the
current code value, registered as-is and not to be tuned.

Rationale: for a 24 h warning, a cluster of up to 20 near-identical
seizures (patient 1942) is one risk episode; counting them individually
distorts both sensitivity and false-alarm rate.

Matches the advisor recommendation.

## Decision 3 — Event-denominator standardization (Brief 3)

**Decided.** Both event denominators are reported, always explicitly
labelled; the **coverable-matched** denominator is the headline / primary
number. Coverability is computed by a single label-time function (the
post-C2 `is_excluded` definition with right-censoring applied), not
per baseline.

Rationale: the coverable-matched set is the only denominator every
baseline can actually forecast against, so it is the only basis for a
fair cross-baseline comparison. A single shared coverability function
keeps the denominator fixed across baselines.

Matches the advisor recommendation.

## Decision 4 — Postictal-exclusion anchor (Brief 4)

**Decided.** For onset-only datasets (MSG), the postictal-exclusion
window is anchored to **`onset + a fixed offset of 120 minutes`**, not to
the imputed `seizure_end`.

Offset value and clinical basis: 120 min is anchored to the average time
for the EEG to return to baseline after a seizure in adults — reported as
mean ~120 min (maximum ~420 min) by Abood W, Bandyopadhyay S, "Postictal
Seizure State", StatPearls, NCBI Bookshelf NBK526004 (last updated
2023-07-10). It is consistent with the "T2 (hours)" postictal phase of the
reference review: Pottkämper JCM, Hofmeijer J, van Waarde JA, van Putten
MJAM, "The postictal state — what do we know?", Epilepsia
2020;61(6):1045-1061, DOI 10.1111/epi.16519.

Both sources were independently verified — real and content-matched — on
2026-05-19 by direct fetch of the NCBI pages.

Rationale: MSG `seizure_end` is imputed at a flat 60 s; anchoring an
exclusion window to an imputed value propagates the imputation artefact
into the labels. Anchoring to onset plus a fixed, clinically-justified
offset avoids that. Per the advisor's requirement, the offset value is
named together with a clinical source rather than reused from an
unrelated default.

Matches the advisor recommendation (onset + fixed clinical offset).

Open implementation detail (Phase C, not a blocker for this sign-off):
the advisor's brief-4 operational note asks the Phase C protocol to
specify how the postictal zone interacts with imputed-`seizure_end`
events; this is an implementation detail for `label_windows.py`, recorded
here so it is not lost.

## Gate A status after this sign-off

- Policy half: **closed** — the four decisions above are recorded.
- Remaining Gate A blocker: the **Phase B manual label audit** (Oussama,
  not delegable; `docs/HUMAN_LABEL_AUDIT_PROTOCOL.md`).
- Gate A unblocks Phase C (freeze the benchmark + pre-register). The four
  decisions above are inputs to the Phase C protocol and its
  pre-registration.
