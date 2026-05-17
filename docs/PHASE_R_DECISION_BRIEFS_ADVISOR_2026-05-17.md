# Phase R decision briefs — advisor recommendations (independent review)

Date: 2026-05-17
Companion to: `docs/PHASE_R_DECISION_BRIEFS_2026-05-17.md`

**Status.** This is *one input* to the four Gate A policy decisions — not the
decision. The briefs remain the decision frame; Oussama's recorded sign-off (in
`PLAYBOOK.md` §5 or an ADR) is the artefact that closes the policy items. An
independent advisor reviewed the four briefs; recommendations below, each noting
whether it confirms or diverges from the Phase R audit's position.

## Brief 1 — MSG long-horizon framing — DIVERGES from the audit

**Recommendation: (b) keep SPH60/SOP1440 as a coverage-limited demonstration,
denominator stated inline — and add option (c): also run a shorter horizon.**

The audit's "either is defensible" is too soft. Option (b) is *required*
regardless: presenting n=54 as support for a clinical claim is dishonest about
statistical power. The genuine open decision is whether the paper *also* runs a
coverage-bounded shorter horizon as a powered comparison.

At SOP1440 (24 h) only 54/40 events are coverable. At a shorter SOP — e.g.
SOP240 (4 h) — the coverable count rises substantially because most Empatica
segments comfortably exceed 4 h. **Recommended Option (c):** report both — 24 h
as the clinically-motivated, honestly small-n result, and a shorter horizon as
the well-powered comparison number. More publishable than picking one. Add (c)
to the brief.

## Brief 2 — H1 cluster metric unit — confirms the audit

**Recommendation: cluster-level primary, seizure-level as a secondary table.**

Operational addition: `cluster_gap_minutes` (240) is itself a policy choice, not
a discovery — a different gap (60 / 120 / 480) shifts the cluster count and thus
the headline metric. **Pre-register the gap value in the Phase C protocol; do
not tune it.**

## Brief 3 — Event-denominator standardization — confirms the audit

**Recommendation: report both, coverable-matched primary.**

Operational addition: lock the coverability calculation to a *single label-time
function* — the post-C2 `is_excluded` definition with right-censoring applied —
**not** a per-baseline calculation. If each baseline computed its own coverable
set, sensitivity-on-coverable would be a moving denominator and cross-baseline
comparison would be illusory.

## Brief 4 — Postictal anchor — confirms the audit

**Recommendation: anchor postictal exclusion to onset + a fixed clinical offset.**

Two operational additions:
1. The offset value needs a **clinical-neurophysiology citation**, not just a
   chosen number. Do not reuse `--postictal-exclusion-minutes 240` (present in
   the commands for unrelated reasons). Oussama + advisor must name a source and
   a number together.
2. Specify the policy for an imputed-`seizure_end` event that *also* falls in
   the postictal exclusion zone of a real-end event: state whether such an
   event's postictal zone is computed at all, or whether imputed-end events are
   excluded from postictal-zone generation entirely.

## What Oussama must do to close the policy half of Gate A

- Confirm or override each recommendation above.
- Brief 1: decide whether to also run a shorter horizon (advisor: yes).
- Brief 2: name the `cluster_gap_minutes` value and pre-register it.
- Brief 4: name the postictal offset value and its clinical source.
- Record the four decisions in `PLAYBOOK.md` §5 or an ADR.

After sign-off, the policy half of Gate A closes. The remaining Gate A blocker
is then the manual label audit (Phase B) — genuinely Oussama's alone.
