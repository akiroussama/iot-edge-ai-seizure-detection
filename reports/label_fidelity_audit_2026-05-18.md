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
| SeizeIT2 onset extension | `*events.tsv` (BIDS) + processed `recordings.parquet` | `(patient_id, recording_id, event_source_file, onset)` multiset and `seizure_start - recording_start == raw onset` | onset-level |

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

## Codex remediation candidate — SeizeIT2 onset-level extension

`scripts/audit_label_fidelity.py` now keeps the existing SeizeIT2 count check
and adds an onset-level arm. The added comparison is deliberately
parser-internal-free: it does not import `_parse_recording_start`; it compares
the raw BIDS `onset` value with `events.parquet.seizure_start -
recordings.parquet.recording_start`, keyed by patient, recording/run, source
`*events.tsv`, and onset. Missing raw roots, missing processed parquet,
missing onset columns, missing source-file keys, and missing/ambiguous
recording starts are flagged as audit findings rather than passing silently.

Local verification in this checkout:

```
uv run --extra dev ruff check scripts/audit_label_fidelity.py tests/test_label_fidelity_audit.py
All checks passed!

uv run --extra dev pytest tests/test_label_fidelity_audit.py
5 passed

uv run --extra dev python scripts/audit_label_fidelity.py
EXIT=1
MISMATCH: MSG missing data/processed/msg/events.parquet
MISMATCH: SeizeIT2 missing data/processed/seizeit2/events.parquet
```

The only mounted raw SeizeIT2 BIDS tree found locally was the sibling
`/mnt/c/doctorat/iot/epitwin-open/datasets` subset (`sub-125`, 85 event TSVs).
The onset extension passes on that mounted subset:

```
uv run --extra dev python scripts/audit_label_fidelity.py \
  --dataset seizeit2 \
  --repo-root /mnt/c/doctorat/iot/epitwin-open \
  --seizeit2-raw-root /mnt/c/doctorat/iot/epitwin-open/datasets

raw *events.tsv seizures: 2  |  events.parquet: 2
OK: raw seizure counts match events.parquet, overall and per patient
raw onset keys: 2  |  events.parquet onset keys: 2
OK: raw onset multiset matches events.parquet patient/recording/source/onset keys
OK: seizure_start - recording_start matches every raw SeizeIT2 onset
EXIT=0
```

The full 125-subject / 883-seizure onset-level run remains pending in this
workspace because the full raw and processed `data/` tree is not mounted here.
This is therefore a remediation candidate, not a closed full-data finding.

## Limits — what this audit does NOT establish

1. **Not a clinical audit.** It checks raw→parquet fidelity, not whether the
   raw annotations are themselves clinically correct. A human spot-check of
   the review sheets (`reports/{msg,seizeit2}_label_audit_review_sheet.csv`)
   is still required and remains Oussama's.
2. **The full SeizeIT2 onset run is still pending.** The script now contains
   an onset-level SeizeIT2 check and falsification tests for a count-preserving
   timestamp shift, but this checkout did not have the full 125-subject raw
   and processed data tree mounted. Claude Code's dated full-data re-review is
   still required before this limitation can be removed.
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
