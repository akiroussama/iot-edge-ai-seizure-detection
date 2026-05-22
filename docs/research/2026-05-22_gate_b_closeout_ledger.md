# Gate B Closeout Ledger

Date: 2026-05-22

Branch: `codex/gate-b-closeout-ledger`

Base: `origin/main@8ad790f`

## Objective

Convert the generated Gate B/C action checklist into a human-reviewable
closeout ledger. The previous guardrail run identified the blockers. This task
creates the formal instrument for closing them with evidence, reviewer identity,
decision date, and rerun artifacts.

This task does not close Gate B. It keeps all human decision columns blank.

## Implementation

- Added `src/reports/gate_b_closeout.py`.
- Added CLI `scripts/build_gate_b_closeout_ledger.py`.
- Added tests in `tests/test_gate_b_closeout.py`.
- Generated `reports/gate_b_closeout_2026-05-22/`.

## Execution

```bash
uv run --extra dev python scripts/build_gate_b_closeout_ledger.py \
  --action-checklist reports/local_gate_guardrails_2026-05-22/gate_bc_action_checklist.csv \
  --out-dir reports/gate_b_closeout_2026-05-22 \
  --run-id gate_b_closeout_2026-05-22
```

Output:

```json
{
  "out_dir": "reports/gate_b_closeout_2026-05-22",
  "gate_b_status": "blocked_pending_human_closeout",
  "ledger_rows": 8,
  "open_rows": 8,
  "claim_status": "gate_b_closeout_ledger_pending_human_review_not_citable"
}
```

## Generated Artifacts

- `reports/gate_b_closeout_2026-05-22/gate_b_closeout_ledger.csv`
- `reports/gate_b_closeout_2026-05-22/gate_b_closeout_ledger.json`
- `reports/gate_b_closeout_2026-05-22/gate_b_closeout_ledger.md`
- `reports/gate_b_closeout_2026-05-22/gate_b_closeout_summary.csv`
- `reports/gate_b_closeout_2026-05-22/gate_b_closeout_manifest.json`

## Ledger State

- Ledger rows: 8.
- Closed rows: 0.
- Open rows: 8.
- P0 open rows: 3.
- Gate B status: `blocked_pending_human_closeout`.

P0 rows:

- `GB-001`: MSG source-data coverage for patients `1942`, `1219`, `1675`.
- `GB-002`: SeizeIT2 full-cohort evidence.
- `GB-003`: Gate C freeze prerequisite.

## Human Decision Columns

The ledger requires these columns to be filled by a human reviewer:

- `human_decision`
- `reviewer_name`
- `review_date`
- `evidence_uri`
- `evidence_hash`
- `resolution_notes`
- `rerun_required`
- `rerun_artifact_uri`

Allowed `human_decision` values:

- `RESOLVED`
- `APPROVED_EXCLUSION`
- `DEFERRED`
- `NEEDS_SOURCE_REVIEW`
- `BLOCKED`

Rows with `BLOCKED` or `NEEDS_SOURCE_REVIEW` keep Gate B blocked. Rows marked
`RESOLVED`, `APPROVED_EXCLUSION`, or `DEFERRED` still require reviewer, date,
and evidence URI before the ledger can advance to a Gate B validation rerun.

## Guardrails

- This is not a Gate B pass.
- This is not clinical evidence.
- This does not freeze splits or artifacts.
- Blank human decision fields deliberately keep Gate B blocked.
- Claim status is `gate_b_closeout_ledger_pending_human_review_not_citable`.

## Validation

Targeted validation:

```bash
uv run --extra dev ruff check src/reports/gate_b_closeout.py scripts/build_gate_b_closeout_ledger.py tests/test_gate_b_closeout.py
uv run --extra dev pytest tests/test_gate_b_closeout.py tests/test_gate_bc_checklist.py
```

Full validation:

```bash
uv run --extra dev ruff check .
uv run --extra dev --extra torch pytest
git diff --check
```

Result:

- Targeted Ruff: passed.
- Targeted pytest: 5 passed.
- Full Ruff: passed.
- Full pytest: 305 passed.
- `git diff --check`: passed.

## Next Step

A reviewer can now fill `gate_b_closeout_ledger.csv`. After human review, the
ledger should be re-summarized, guardrails rerun, and only then should Gate C
dry-run be attempted again.
