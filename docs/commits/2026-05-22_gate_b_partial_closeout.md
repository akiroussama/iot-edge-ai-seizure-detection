# Commit Trace - Gate B Partial Closeout

Date: 2026-05-22

Branch: `codex/gate-b-partial-closeout`

Base: `origin/main@1ced2a6`

## Intent

Record human-supplied closeout decisions for `GB-001`, `GB-002`, and `GB-003`
without marking Gate B as passed. The remaining ledger rows must stay open.

## Human-Supplied Decisions

- `GB-001`: `RESOLVED`, reviewer `O. Akir`, date `2026-05-22`.
- `GB-002`: `APPROVED_EXCLUSION`, reviewer `O. Akir`, date `2026-05-22`.
- `GB-003`: `APPROVED_EXCLUSION`, reviewer `O. Akir`, date `2026-05-22`.

Evidence URIs and hashes were supplied by the reviewer in chat. This commit
records them as human-attested evidence; it does not independently verify or
retrieve those external resources.

## Files

Code:

- `src/reports/gate_b_closeout.py`
- `scripts/apply_gate_b_closeout_decisions.py`
- `tests/test_gate_b_closeout.py`

Docs:

- `docs/research/2026-05-22_gate_b_partial_closeout.md`
- `docs/commits/2026-05-22_gate_b_partial_closeout.md`

Updated audit outputs:

- `reports/gate_b_closeout_2026-05-22/gate_b_closeout_decisions_partial_2026-05-22.csv`
- `reports/gate_b_closeout_2026-05-22/gate_b_closeout_ledger.csv`
- `reports/gate_b_closeout_2026-05-22/gate_b_closeout_ledger.json`
- `reports/gate_b_closeout_2026-05-22/gate_b_closeout_ledger.md`
- `reports/gate_b_closeout_2026-05-22/gate_b_closeout_manifest.json`
- `reports/gate_b_closeout_2026-05-22/gate_b_closeout_summary.csv`

## Execution Log

Command:

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

- Gate B remains `blocked_pending_human_closeout`.
- No row beyond `GB-001` to `GB-003` was modified.
- `GB-004` to `GB-008` remain pending.
- Gate C remains blocked until all ledger rows close and guardrails rerun.
- No clinical or benchmark result is introduced.

## Validation Log

Executed before final commit:

```bash
uv run --extra dev ruff check src/reports/gate_b_closeout.py scripts/apply_gate_b_closeout_decisions.py tests/test_gate_b_closeout.py
uv run --extra dev pytest tests/test_gate_b_closeout.py
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
