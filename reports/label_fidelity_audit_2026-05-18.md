# Label-fidelity audit — automated parser check (Phase B)

Date: 2026-05-18
Script: `scripts/audit_label_fidelity.py`
Datasets: MSG (8 patients) + SeizeIT2 (125 subjects), full processed set.

## Status — PASS (parser fidelity only)

The repo parsers reproduced the raw seizure annotations into
`data/processed/{msg,seizeit2}/events.parquet` with no dropped, added, or
mis-assigned seizures, at the granularity each arm checks.

This is an automated *parser-fidelity* check. It is **not** the Phase B
manual clinical label audit (Owner: Oussama — not delegable) and it does not
close Gate B. It is a precondition for that audit: it confirms the human
review sheets describe faithfully-parsed data rather than a parser artefact.

## What was checked

The audit re-reads the RAW annotation files independently of the parser and
compares the result against `events.parquet`:

| dataset | raw source | comparison | granularity |
|---|---|---|---|
| MSG | onset `.txt` inside the patient `.zip` archives | `(patient_id, unix_second)` set equality | onset-level |
| SeizeIT2 | `*events.tsv` (BIDS) | seizure-row count, overall and per patient | count-level |

## Result (run on the project's Hetzner data-processing server)

```
=== MSG parser fidelity (events.parquet vs raw onsets) ===
  raw onsets: 768  |  events.parquet onsets: 768
  OK: events.parquet onset set is identical to the raw source onset set

=== SeizeIT2 parser fidelity (events.parquet vs raw *events.tsv) ===
  raw *events.tsv seizures: 883  |  events.parquet: 883
  OK: raw seizure counts match events.parquet, overall and per patient

no mismatches: events.parquet is faithful to the raw source annotations
EXIT=0
```

The MSG check is set equality, not just a count match: it would catch a
swap (one onset dropped and a different one introduced) that equal counts
would hide. The SeizeIT2 check is a per-patient count match across all 125
subjects.

## Limits — what this audit does NOT establish

1. **Not a clinical audit.** It checks raw→parquet fidelity, not whether the
   raw annotations are themselves clinically correct. A human spot-check of
   the review sheets (`reports/{msg,seizeit2}_label_audit_review_sheet.csv`)
   is still required and remains Oussama's.
2. **SeizeIT2 is count-level, not onset-level.** A same-count timestamp shift
   would not be caught by the SeizeIT2 arm. Timestamp-ordering sanity
   (`seizure_end >= seizure_start`, recording/window bounds) is covered
   separately by `scripts/verify_processed_data.py`. An onset-level SeizeIT2
   check is a candidate follow-up; it needs the parser's `recording_start`
   reconstruction to convert BIDS-relative onsets to absolute time.
3. **MSG covers the `.txt` path only.** `parse_msg_events` prefers a
   `seizure_times.csv` source if one exists; the audit detects that case and
   refuses (flagging it) rather than reporting a false OK. No such CSV is
   present in the current MSG raw tree, so the `.txt` path is the one the
   parser actually used.

## Verification trail

- The script was reviewed twice by an independent code-reviewer agent before
  it was run. The first pass found 6 correctness bugs: a timezone-incorrect
  Unix-second reconstruction, a false-OK blind spot on the MSG CSV branch,
  and 4 parser-discovery divergences (extracted-`.txt` files, patient-id
  extraction, the SeizeIT2 glob pattern, the SeizeIT2 `sub-` fallback). All 6
  were fixed; the second pass confirmed each fix and found no new issue.
- Run: `uv run python scripts/audit_label_fidelity.py`, exit 0.
- The advisor tool was unavailable during this work; the code-reviewer agent
  served as the independent-review substitute.

## Gate status — unchanged

Phase B (manual label audit), the four Gate A policy sign-offs, the Phase C
freeze (`git tag`), the Zenodo pre-registration, and Phase D baselines all
remain blocked. This audit removes one risk — a silently-corrupting parser —
from the path into Phase B; it does not advance the gate.
