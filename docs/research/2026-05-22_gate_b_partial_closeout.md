# Gate B Partial Closeout

Date: 2026-05-22

Branch: `codex/gate-b-partial-closeout`

Base: `origin/main@1ced2a6`

## Objective

Apply human-supplied closeout decisions for the first three Gate B ledger rows
(`GB-001` to `GB-003`) while keeping the ledger fail-closed until all remaining
rows are reviewed.

The evidence URIs and hashes in this update were supplied by the reviewer in
chat. They are recorded as human-attested evidence and were not independently
retrieved or verified by this run.

## Implementation

- Added `scripts/apply_gate_b_closeout_decisions.py`.
- Extended `src/reports/gate_b_closeout.py` with decision-application logic.
- Extended `tests/test_gate_b_closeout.py`.
- Added `reports/gate_b_closeout_2026-05-22/gate_b_closeout_decisions_partial_2026-05-22.csv`.
- Regenerated `reports/gate_b_closeout_2026-05-22/` outputs.

## Decisions Applied

Closed rows:

- `GB-001`: `RESOLVED` by `O. Akir`, dated `2026-05-22`.
- `GB-002`: `APPROVED_EXCLUSION` by `O. Akir`, dated `2026-05-22`.
- `GB-003`: `APPROVED_EXCLUSION` by `O. Akir`, dated `2026-05-22`.

Still open:

- `GB-004`: MSG denominator integrity.
- `GB-005`: MSG horizon feasibility.
- `GB-006`: SeizeIT2 track completeness.
- `GB-007`: MSG horizon source review.
- `GB-008`: SeizeIT2 negative readiness rows.

## Execution

```bash
uv run --extra dev python scripts/apply_gate_b_closeout_decisions.py \
  --ledger reports/gate_b_closeout_2026-05-22/gate_b_closeout_ledger.csv \
  --decisions reports/gate_b_closeout_2026-05-22/gate_b_closeout_decisions_partial_2026-05-22.csv \
  --out-dir reports/gate_b_closeout_2026-05-22 \
  --run-id gate_b_closeout_2026-05-22 \
  --source-uri reports/gate_b_closeout_2026-05-22/gate_b_closeout_decisions_partial_2026-05-22.csv
```

Output:

```json
{
  "out_dir": "reports/gate_b_closeout_2026-05-22",
  "gate_b_status": "blocked_pending_human_closeout",
  "ledger_rows": 8,
  "open_rows": 5,
  "closed_rows": 3,
  "p0_open_rows": 0,
  "claim_status": "gate_b_closeout_ledger_pending_human_review_not_citable"
}
```

## Guardrails

- Gate B is still not passed.
- The ledger remains `blocked_pending_human_closeout`.
- `GB-004` through `GB-008` still need human decisions.
- Gate C remains blocked until all ledger rows close, guardrails rerun cleanly,
  and Gate C dry-run reports readiness.
- No model result, clinical result, or citable benchmark claim is introduced.

## Validation

Targeted validation:

```bash
uv run --extra dev ruff check src/reports/gate_b_closeout.py scripts/apply_gate_b_closeout_decisions.py tests/test_gate_b_closeout.py
uv run --extra dev pytest tests/test_gate_b_closeout.py
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
- Full pytest: 307 passed.
- `git diff --check`: passed.
