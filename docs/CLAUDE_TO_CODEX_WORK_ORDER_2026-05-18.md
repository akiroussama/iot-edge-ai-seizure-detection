# Claude Code -> Codex — Work order, 2026-05-18

Branch: `feature/epibench-forecast-v0.1`
Author: Claude Code. Recipient: Codex.
Source of truth: `PLAYBOOK.md` — especially §5 (critical path), §7 (roles),
§8 (the kaizen build/review loop), §9 (the three mistakes to avoid).

---

## 1. Read this first — why this work order is short

This work order is deliberately small. That is a finding, not an omission.

- Phase A's **code punch list is fully closed** — verified by
  `docs/CLAUDE_PHASE_R_REREVIEW_2026-05-17.md`: 10 of 13 M2 items CLOSED; the
  3 OPEN are 2 policy decisions and the manual label audit — **none of them
  code**.
- The critical path is now **human-gated**: Gate A needs Oussama's 4 policy
  sign-offs plus advisor; Gate B is the manual label audit (Oussama, "not
  delegable"); Gate C is the irreversible split freeze plus Zenodo
  pre-registration.
- So there is **no large code backlog** to hand you. This file contains the
  **two** genuine, non-redundant, non-gated tasks that exist right now. It is
  not padded to look like more — padding it would be the `CLAUDE.md`
  "throughput is not progress" error and would have you re-do already-closed
  work.
- Do the two tasks **one at a time**, each reviewed before the next starts
  (`PLAYBOOK.md` §8 — "smaller cycles").

## 2. Hard boundary — what no AI agent may do (this includes you)

The items below are not blocked because "Claude could not do them". They
require human clinical expertise, accountable authorship, or an irreversible
public act. You are an AI with the same limits. Producing output for any of
them is **fabrication** — worse than leaving them undone.

- **The Phase B clinical label verdicts.** Do not fill any judgment column in
  `reports/*_label_audit_review_sheet*.csv`. Do not write a clinical
  assessment of any seizure, anywhere — including comments or logs. Owner:
  Oussama, "not delegable" (`PLAYBOOK.md` §7).
- **The 4 Gate A policy decisions** (`docs/PHASE_R_DECISION_BRIEFS_2026-05-17.md`).
  Do not choose an option; do not write a decision into `PLAYBOOK.md` §5.
  Brief 4 needs a real clinical-neurophysiology citation — never invent one.
- **The Phase C freeze and Zenodo pre-registration.** Do not `git tag` a
  frozen benchmark; do not upload anything to Zenodo. Irreversible and
  public — explicit human go only.
- **Phase D baseline runs / Phase E A100 runs.** No reported number before
  Gate C (`PLAYBOOK.md` §10 rule 1). Do not run baselines on the exploratory
  (un-frozen) splits and report the numbers.

If a task seems to require one of these, STOP and flag it. Do not "helpfully"
do it.

## 3. Coordination (dual-agent)

- Branch `feature/epibench-forecast-v0.1`. Claude Code also commits here.
  **`git fetch` and check `origin/feature/epibench-forecast-v0.1` before you
  start and before every push** — Claude and Codex have collided on this
  branch before (`docs/CLAUDE_TO_CODEX_RECONCILIATION_2026-05-15.md`).
- One focused commit per task. Conventional Commits. Keep your `Verified-By`,
  `Falsifiability`, `Advisor-checkpoint` trailers (`PLAYBOOK.md` §8).
- Definition of Done (`PLAYBOOK.md` §8): the fix lives in the **library
  function**, not only a CLI; a **named falsification test** exists that fails
  if the issue reopens; **before/after diagnostic numbers** are in the commit
  body; "closed"/"verified" is reserved for Claude Code's dated re-review —
  you produce a **remediation candidate**, never a "closed" finding.
- The three mistakes to avoid (`PLAYBOOK.md` §9): fix the root, not the entry
  point; a fix must not introduce a new defect (ship a boundary test); never
  declare done without a test that proves it.

## 4. Orient yourself before Task 1

Read, in order: `reports/label_fidelity_audit_2026-05-18.md` (the audit you
are extending — note its stated Limit #2); `scripts/audit_label_fidelity.py`
(the existing script); `src/datasets/seizeit2_loader.py`
(`parse_bids_like_seizeit2_events`, `_parse_recording_start`,
`_is_seizure_event_type`); `reports/phase_c_exploratory_splits_2026-05-17.md`
(the SeizeIT2 de-identification finding).

---

## Task 1 — Onset-level SeizeIT2 label-fidelity audit

**Role (casquette).** Adversarial data-validation engineer. Assume the parser
is wrong until the data proves it right. Your nightmare is a *false OK* — the
audit printing "no mismatch" when one exists.

**Context.** `scripts/audit_label_fidelity.py` (commit `0d7f70f`) checks that
`data/processed/{msg,seizeit2}/events.parquet` faithfully reflects the raw
annotations. It checks **MSG at onset granularity** (timestamp set equality)
but **SeizeIT2 only at count granularity** (seizure-row count per patient).
`reports/label_fidelity_audit_2026-05-18.md` Limit #2 states the consequence:
a count-preserving timestamp shift in SeizeIT2 would pass undetected. The
count-level version needed two code-review passes and 6 bug fixes before it
was correct; onset-level is harder.

**Objective.** Extend the audit so SeizeIT2 is verified at **onset
granularity** — every seizure's onset in `events.parquet` matched against the
raw `*events.tsv` onset, across all 125 subjects / 883 seizures. Extend
`scripts/audit_label_fidelity.py` or add a sibling script; keep the existing
count-level check.

**Errors to avoid.**
- **False OK.** Every comparison must be exercised. If a code path cannot
  verify a row, it must `flag` it — never pass silently. (This is the bug
  class — a false-OK CSV blind spot — that review caught in the count-level
  version.)
- **Badly replicating parser internals.** The parser converts BIDS-relative
  `onset` to absolute time via `_parse_recording_start`. Re-implement it and
  get it subtly wrong -> false mismatches; import it -> you lose audit
  independence. Decide deliberately and document the choice. **Preferred:** a
  parser-internal-free comparison — compare the offset
  `seizure_start - recording_start` already in `events.parquet` against the
  raw `onset` column; it re-derives nothing. First inspect the SeizeIT2
  `events.parquet` schema to confirm `recording_start` and a recording/run
  key are present.
- **Assuming absolute timestamps.** The OpenNeuro `ds005873` release is
  de-identified, every recording epoch-anchored to `2000-01-01`
  (`reports/phase_c_exploratory_splits_2026-05-17.md`). A SeizeIT2 onset is
  meaningful only relative to its own recording.
- **Wrong join key.** Matching a raw `events.tsv` row to its `events.parquet`
  row needs a stable key — patient + recording/run + onset. Get it wrong and
  you compare unrelated rows; the result is then meaningless but green.

**The challenge.** Build a check independent enough to catch a real parser
bug, yet not a re-implementation so faithful that it mirrors any bug the
parser already has. MSG was easy — its onsets are absolute Unix seconds.
SeizeIT2's relative, epoch-anchored timestamps make the same rigor genuinely
harder. That gap is the task.

**Definition of done.** Script extended or added; reviewed by an independent
code-reviewer subagent before it is run (budget for two passes — the
count-level version needed them); `ruff` clean; run on the server where the
data lives (`uv run python ...`); exits non-zero on any mismatch; the result
folded into a dated report. Remediation candidate — Claude Code's dated
re-review closes it.

---

## Task 2 — SOTA citation integrity audit of `docs/SOTA_REVIEW_2026.md`

**Role (casquette).** Bibliography / literature-integrity auditor. Every
citation is guilty until it resolves to a real source whose content matches
the use.

**Context.** `PLAYBOOK.md` Phase G deliverable 1 requires "Every cited SOTA
source verified" and explicitly flags a **phantom `arXiv:2604.18297`** in
`docs/SOTA_REVIEW_2026.md` — confirmed still present at line 37
(`https://arxiv.org/abs/2604.18297`). A phantom citation in the
SOTA-positioning document is the failure class `COMMIT_GUIDELINES.md`
documents (the 4 phantom DOIs incident). The SOTA review feeds the paper's
positioning matrix, so a wrong citation there propagates into the manuscript.

**Objective.** Verify **every** external source cited in
`docs/SOTA_REVIEW_2026.md` resolves to a real publication whose content
matches how the document uses it. Start with `arXiv:2604.18297`. Correct or
explicitly flag each citation that fails.

**Errors to avoid.**
- **Never invent a replacement.** If `arXiv:2604.18297` does not resolve, do
  not substitute a plausible-looking arXiv ID or DOI. Either identify the
  genuinely-intended source from the surrounding text (author, title, venue)
  and cite that, or mark it `[UNVERIFIED — does not resolve, 2026-05-18]` and
  leave it for Oussama. A confidently-wrong citation is worse than a flagged
  one.
- **A resolving ID is not a verified citation.** An ID can resolve to a real
  but *unrelated* paper — exactly what the COMMIT_GUIDELINES phantom-DOI
  incident found (3 of 4 resolved to unrelated work). Read the resolved
  paper; confirm its topic matches the claim the document attaches to it.
- **Do not touch the `tibia` wording.** A 2026-05-18 grep finds no `tibia` in
  `README.md` or `docs/HUMAN_INTERVENTION_CHECKPOINTS.md` — the playbook §G
  typo appears already fixed. The remaining `tibia` occurrences elsewhere are
  intentional forbidden-claim examples. No action there.

**The challenge.** Distinguishing a phantom ID from a real-but-misattributed
one. The first is caught by a 404. The second is caught only by reading the
resolved paper and judging whether it supports the sentence citing it — and
that is the dangerous one.

**Definition of done.** Every citation in `SOTA_REVIEW_2026.md` carries a
verified status; phantom or misattributed ones corrected or explicitly
flagged (never invented); a short audit note (`docs/SOTA_CITATION_AUDIT_<date>.md`)
records each citation checked, its verification method (resolved URL/DOI),
and its verdict; the commit carries a `Verified-By` trailer naming the
resolution method. Remediation candidate — Claude Code closes.

---

## 5. What is deliberately NOT in this work order

Listed so you do not go looking for more and accidentally jump the queue
(`PLAYBOOK.md` §1 — "sequencing does not change"):

- **Phase D baseline runs** — gated behind Gate C (frozen splits). The runners
  already exist (`scripts/run_baseline.py`, `run_rule_baseline.py`,
  `run_cycle_baseline.py`); they are not run, and no number is reported, until
  Gate C passes.
- **Phase E / A100** — behind Gate D and `docs/HUMAN_INTERVENTION_CHECKPOINTS.md`
  checkpoint 4.
- **The 4 Gate A policy decisions and the Phase B label audit** — Oussama's.
  See §2.

When Tasks 1 and 2 are done and reviewed, the honest status is: Codex's
legitimate backlog is empty until a gate moves. Report that — do not invent a
Task 3.
