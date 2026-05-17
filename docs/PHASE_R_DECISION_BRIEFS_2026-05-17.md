# Phase R policy decision briefs

Date: 2026-05-17
For: Oussama + advisor
Source: `docs/CLAUDE_PHASE_R_AUDIT_2026-05-15.md` §4 ("Policy decisions") and §6.
Status: each of the four is a Gate A blocker. Gate A does not pass until all
four are decided and the decision recorded (in `PLAYBOOK.md` §5 or an ADR).

These four items are **not code** — the Phase R code punch list is closed
(`docs/CLAUDE_PHASE_R_REREVIEW_2026-05-17.md`). They are scientific framing
choices that change what the benchmark paper claims. Each brief states the
decision, the options, the audit's position, and who signs off.

---

## Brief 1 — MSG long-horizon framing

**Decision.** How is the MSG SPH60 / SOP1440 (24 h) task presented in the paper?

**Why it is open.** A 24 h SOP against Empatica segments mostly far shorter than
24 h means most windows' horizons run off the recording end. Post-reconciliation
the full coverable MSG set is 510 events across 8 patients (2026-05-17 run); the
temporal-test split carries 54 seizure-level / 40 cluster-level matched-coverable
events (`docs/CODEX_PHASE_R3_CLUSTER_AND_POSTICTAL_POLICY_2026-05-16.md`). Any
sensitivity sits on a small denominator with a wide confidence interval.

**Options.**
- (a) Redesign the horizon — a shorter SOP, or a coverage-bounded horizon that
  labels only windows whose full SPH+SOP fits inside the recording.
- (b) Keep SPH60/SOP1440 and present it explicitly as a *coverage-limited
  demonstration*, denominator stated inline, not a benchmark results table.

**Audit position.** Both are defensible; (b) is the honest negative finding a
benchmark paper should elevate, not bury in a footnote.

**Sign-off:** Oussama + advisor. Record in `PLAYBOOK.md` §5 Phase C.

---

## Brief 2 — H1 seizure-cluster metric unit

**Decision.** For MSG long-horizon, are event metrics computed seizure-level or
cluster-level?

**Why it is open.** Patient 1942 has clusters up to 20 seizures within a 240-min
gap. For a 24 h warning, 20 near-identical seizures inside one cluster is one
risk episode; counting them individually distorts both sensitivity and FAR. The
code already supports both units (`event_unit`, `cluster_gap_minutes`); the
policy choice is which is primary.

**Options.** seizure-level primary / cluster-level primary / both reported.

**Audit recommendation.** For long-horizon MSG, **cluster-level primary**, with
seizure-level as a secondary table. Explicit advisor sign-off required before it
is locked.

**Sign-off:** Oussama + advisor.

---

## Brief 3 — Event-denominator standardization

**Decision.** Which event denominator is the headline metric — all events,
coverable-matched events, or both?

**Why it is open.** Phase R made the denominator *visible* per report but did not
*standardize* which is primary. A reader can still compare sensitivities computed
on different denominators across reports.

**Audit recommendation.** Report **both, always labelled**, and make the
**coverable-matched** set the primary number — it is the only denominator every
baseline can actually forecast against. Never present a bare sensitivity without
its denominator (inline `0.85 (n/N events)` rendering is now enforced in code,
audit C4).

**Sign-off:** Oussama + advisor; then standardize across the report suite.

---

## Brief 4 — Postictal-exclusion anchor for onset-only datasets

**Decision.** For onset-only datasets (MSG), is the postictal exclusion window
anchored to the imputed `seizure_end` or to `onset + a fixed clinical offset`?

**Why it is open.** MSG seizure annotations are onset-only; `seizure_end` is
imputed at a flat 60 s. Anchoring an exclusion zone to an imputed value
propagates the imputation artefact into the labels.

**Audit recommendation.** Anchor postictal exclusion to **onset + an explicit
fixed clinical offset**, not to the imputed end. Define and document the offset.
`label_windows.py` already exposes `--postictal-anchor seizure_start`; the policy
is to make that the standard for onset-only data and to fix the offset value.

**Sign-off:** Oussama + advisor; record the chosen offset.

---

## Gate A status

Code punch list: closed (`CLAUDE_PHASE_R_REREVIEW_2026-05-17.md`). These four
decisions plus the manual label audit (Phase B) are the remaining Gate A
blockers. Gate A unblocks Phase C (freeze the benchmark + pre-register).
