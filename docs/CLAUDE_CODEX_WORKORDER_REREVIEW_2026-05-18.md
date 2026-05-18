# Claude Code closure re-review — Codex work order 2026-05-18

Date: 2026-05-18
Reviewer role: Claude Code (per `PLAYBOOK.md` §7 — verification and closure).
Closes: `docs/CLAUDE_TO_CODEX_WORK_ORDER_2026-05-18.md` (Tasks 1 and 2).
Codex commits re-reviewed: `a0fa264` (Task 1), `acc1ad1` (Task 2).

Verification basis:

- Full-data run of `scripts/audit_label_fidelity.py` on the Hetzner
  data-processing server (MSG + SeizeIT2, all 125 SeizeIT2 subjects /
  883 seizures).
- Independent code-reviewer subagent pass over the SeizeIT2 onset code,
  cross-checked against `src/datasets/seizeit2_loader.py`.
- Independent `WebFetch` of `https://arxiv.org/abs/2604.18297`.
- `uv run --extra dev pytest tests/test_label_fidelity_audit.py` — 5 passed.

## Task 1 — SeizeIT2 onset-level label-fidelity audit

**Codex delivered** (`a0fa264`): an onset-level arm for
`scripts/audit_label_fidelity.py`. It keeps the per-patient count check and
adds a parser-internal-free onset comparison — raw BIDS `onset` against
`event_onset_seconds`, keyed by patient / recording / source file, plus
`seizure_start - recording_start` against `event_onset_seconds` — and
`tests/test_label_fidelity_audit.py` (5 tests). Codex's own report flagged the
full 125-subject run as pending: Codex's checkout lacked the full data.

**Full-data verification — PASS.** Claude Code ran the audit on the Hetzner
server, where the full data lives:

```
=== SeizeIT2 parser fidelity (events.parquet vs raw *events.tsv) ===
  raw *events.tsv seizures: 883  |  events.parquet: 883
  OK: raw seizure counts match events.parquet, overall and per patient
  raw onset keys: 883  |  events.parquet onset keys: 883
  OK: raw onset multiset matches events.parquet patient/recording/source/onset keys
  OK: seizure_start - recording_start matches every raw SeizeIT2 onset
EXIT=0
```

The onset check **genuinely executed**: `883` onset keys on both sides
confirms the real `events.parquet` carries the columns the audit needs
(`recording_id`, `event_source_file`, `event_onset_seconds`) and
`recordings.parquet` carries `recording_start`. The independent subagent
review confirmed these column names match what `parse_bids_like_seizeit2_events`
and `discover_seizeit2_recordings` write, and that `_seizeit2_recording_id`
reproduces the parser's `recording_id` derivation byte-for-byte.

**Verdict:** the SeizeIT2 onset-level fidelity finding is **VERIFIED on the
full 125-subject data**. The "pending" limitation in
`reports/label_fidelity_audit_2026-05-18.md` is lifted.

**Re-review found two robustness defects in the audit script.** Neither
affected the verified run — it ran on Hetzner, the same OS that generated the
parquet, with `recordings.parquet` present — but both must be fixed before the
script is robust. Per `PLAYBOOK.md` §7 these are implementation, so they are
handed to Codex as a remediation candidate:

```
finding: R1 (cross-OS path separator)
fix: scripts/audit_label_fidelity.py:238 — str(tsv.relative_to(raw_root))
     -> tsv.relative_to(raw_root).as_posix(); :323 — normalise the
     event_source_file read from events.parquet (backslash -> forward slash)
test: a Seizeit2OnsetKey built from a backslash-separated event_source_file
      still matches its forward-slash raw counterpart
mutation it kills: running the audit on a different OS than the one that
      generated events.parquet reports ~100% of onsets as missing/extra
diagnostic: Hetzner run unaffected (Linux generated the parquet, Linux ran
      the audit); a Windows audit of the Linux parquet would flood
```

```
finding: R2 (multiset check skipped when recordings.parquet absent)
fix: scripts/audit_label_fidelity.py:286-292 — run the onset-key multiset
     comparison (currently lines 349-361) before / independently of the
     recordings.parquet guard; gate only the seizure_start-recording_start
     offset sub-check on recordings.parquet
test: with recordings.parquet removed, a dropped raw onset is still reported
      by the multiset check rather than silently skipped
mutation it kills: a dropped or added onset goes unreported whenever
     recordings.parquet is missing
diagnostic: recordings.parquet present in the verified run, so the multiset
     check did execute there
```

These are P2 robustness hardening of an already-verified check. The
onset-fidelity result does not depend on them.

## Task 2 — SOTA citation integrity audit

**Codex delivered** (`acc1ad1`): per-citation 2026-05-18 verification status on
all 12 sources in `docs/SOTA_REVIEW_2026.md`, and a new
`docs/SOTA_CITATION_AUDIT_2026-05-18.md` recording each resolution method and
verdict. Codex's verdict on the work-order suspect, `arXiv:2604.18297`: it
resolves and matches its claim; not phantom; not replaced.

**Independent verification — confirmed.** The work order required the disputed
citation be checked independently, not rubber-stamped. Claude Code fetched
`https://arxiv.org/abs/2604.18297` directly:

> Real arXiv paper. "Circadian Phase Locking of Epilepsy Seizures in Wearable
> Data: A Single-Patient Case Study", Ewart-James et al. (University of
> Bristol), submitted 2026-04-20. Subject: whether seizure onsets align with
> circadian rhythm extracted from wearable heart-rate data.

This matches both the title in `SOTA_REVIEW_2026.md` and the claim it is
attached to. **Codex's verdict is correct.** The `PLAYBOOK.md` §G description
of `arXiv:2604.18297` as "the phantom" is **stale**: it was a 2026-05-15
suspicion, already retracted in `SOTA_REVIEW_2026.md` on 2026-05-16 and now
independently re-confirmed as a real, correctly-attributed citation.

The other 11 citations are accepted on Codex's documented per-source
resolution trail in `SOTA_CITATION_AUDIT_2026-05-18.md`. The one citation
independently re-checked here — the only disputed one — confirms Codex's audit
method is sound, not fabricated.

**Verdict:** Task 2 is **CLOSED**.

**Playbook maintenance recommended:** `PLAYBOOK.md` §G Phase-G deliverable 1
still instructs "fix the phantom `arXiv:2604.18297`". That instruction is
obsolete; it should be removed or rewritten ("citation verified real,
2026-05-18") so a future reader does not re-chase a resolved item. This is a
`PLAYBOOK.md` edit and is left to Oussama (§12 — playbook maintenance).

## Status

- Task 2: closed.
- Task 1: the onset-fidelity finding is verified on full data; the audit
  script has two P2 robustness defects (R1, R2) handed back to Codex.
- The EpiTwin critical path is unchanged — still gated on the Gate A policy
  sign-offs and the Phase B manual label audit (Oussama). This closure does
  not move a gate.
