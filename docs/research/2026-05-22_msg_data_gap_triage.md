# MSG Data-Gap Triage

Date: 2026-05-22

Branch: `codex/msg-data-gap-triage`

Base: `origin/main@43cb4b0`

## Objective

Turn the current MSG feasibility blockers into a reproducible triage artifact.
The project already knows that some seizure onsets are unmatched to parsed
wearable segments, some patients have zero parsed recordings, and long-horizon
labels are heavily right-censored. This task makes those gaps machine-readable
so Gate B/C cannot advance by narrative alone.

This task does not train a model, does not produce benchmark numbers, and does
not make any clinical result citable.

## Implementation

- Added `src/reports/msg_gap_triage.py`.
- Added CLI `scripts/build_msg_gap_triage.py`.
- Added behavior tests in `tests/test_msg_gap_triage.py`.

The report consumes already auditable tables:

- event coverage summary from `scripts/summarize_event_coverage.py`;
- optional seizure-cluster summary from the same script;
- optional horizon viability table from `scripts/summarize_horizon_viability.py`.

It writes:

- `msg_gap_patient_triage.csv`;
- `msg_gap_horizon_triage.csv`;
- `msg_gap_summary.csv`;
- `msg_gap_triage_manifest.csv`;
- `msg_gap_triage_report.json`;
- `msg_gap_triage_report.md`.

## Patient Triage Logic

Patients are assigned to explicit review states:

- `p0_blocker`: zero parsed recordings or zero matched events despite annotated
  seizures. These patients are not evaluable without source-data review.
- `p1_source_review_required`: some events are matched, but unmatched events
  remain. These can only be used with explicit matched-event denominators.
- `p1_timeline_review_required`: cluster or matched-fraction concerns require
  timeline/postictal review.
- `p2_routine`: no source-data blocker detected by the supplied summaries.

The default thresholds are conservative:

- matched fraction below `0.8` is flagged;
- cluster size above `3` events is flagged.

## Horizon Triage Logic

Each SPH/SOP candidate is assigned to:

- `not_main_table_ready` when valid-window fraction, event-coverable fraction,
  or right-censored unknown burden fails the configured feasibility thresholds;
- `source_review_required` when only unmatched source events remain;
- `candidate_after_gate_b_c` when the supplied tables do not reveal blockers.

Default feasibility thresholds:

- minimum valid-window fraction: `0.5`;
- minimum event-coverable fraction: `0.5`;
- maximum right-censored unknown fraction: `0.25`.

## Scientific Guardrails

- The claim status is always `msg_gap_triage_pre_gate_c_not_citable`.
- The Markdown report explicitly states that no sensitivity, false-alarm rate,
  Brier score, BSS, or clinical utility is reported.
- Unmatched seizure events are never silently promoted into denominators.
- Long-horizon feasibility warnings are kept separate from model performance.
- The manifest hashes input and output tables for traceability.

## Example

```bash
uv run --extra dev python scripts/build_msg_gap_triage.py \
  --coverage-csv reports/msg_event_coverage.csv \
  --clusters-csv reports/msg_event_clusters.csv \
  --viability-csv reports/msg_horizon_viability.csv \
  --out-dir reports/msg_gap_triage_2026-05-22
```

## Validation

Targeted validation:

```bash
uv run --extra dev ruff check src/reports/msg_gap_triage.py scripts/build_msg_gap_triage.py tests/test_msg_gap_triage.py
uv run --extra dev pytest tests/test_msg_gap_triage.py tests/test_event_coverage.py tests/test_horizon_viability.py
```

Full validation:

```bash
uv run --extra dev ruff check .
uv run --extra dev --extra torch pytest
git diff --check
```

Result:

- Targeted Ruff: passed.
- Targeted pytest: 10 passed.
- Full Ruff: passed.
- Full pytest: 297 passed.
- `git diff --check`: passed.

## Remaining Limits

- The task classifies gaps; it does not recover missing source files.
- Real MSG source-data correction still needs a human audit log before Gate B.
- Gate C still requires frozen splits, artifact registry verification, DOI or
  preregistration evidence, and rerun benchmark rows after any data correction.
