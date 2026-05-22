# Commit Trace - Gate B Simulated Closeout

Date: 2026-05-22

Branch: `codex/gate-b-simulated-closeout`

Base: `origin/main@ca8d69e`

## Intent

Record the reviewer-provided positive simulation decisions for `GB-004` through
`GB-008` without treating them as real Gate B evidence.

## Inputs

The user explicitly introduced these rows as simulation data:

- `GB-004`: `RESOLVED`
- `GB-005`: `RESOLVED`
- `GB-006`: `APPROVED_EXCLUSION`
- `GB-007`: `DEFERRED`
- `GB-008`: `RESOLVED`

## Files

Code:

- `src/reports/gate_b_closeout.py`
- `scripts/build_gate_b_closeout_ledger.py`
- `scripts/apply_gate_b_closeout_decisions.py`
- `tests/test_gate_b_closeout.py`

Docs:

- `docs/research/2026-05-22_gate_b_simulated_closeout.md`
- `docs/commits/2026-05-22_gate_b_simulated_closeout.md`

Generated simulation outputs:

- `reports/gate_b_closeout_simulation_2026-05-22/`

Updated real partial ledger outputs:

- `reports/gate_b_closeout_2026-05-22/`

## Execution Log

Simulation command:

```bash
uv run --extra dev python scripts/apply_gate_b_closeout_decisions.py \
  --ledger reports/gate_b_closeout_2026-05-22/gate_b_closeout_ledger.csv \
  --decisions reports/gate_b_closeout_simulation_2026-05-22/gate_b_closeout_decisions_simulated_remaining_2026-05-22.csv \
  --out-dir reports/gate_b_closeout_simulation_2026-05-22 \
  --run-id gate_b_closeout_simulation_2026-05-22 \
  --source-uri reports/gate_b_closeout_simulation_2026-05-22/gate_b_closeout_decisions_simulated_remaining_2026-05-22.csv \
  --decision-evidence-status simulation_positive_not_real_gate_b_evidence
```

Output:

```json
{
  "out_dir": "reports/gate_b_closeout_simulation_2026-05-22",
  "gate_b_status": "simulation_complete_not_gate_b_evidence",
  "ledger_rows": 8,
  "open_rows": 0,
  "closed_rows": 8,
  "p0_open_rows": 0,
  "claim_status": "gate_b_closeout_ledger_pending_human_review_not_citable"
}
```

Real partial ledger regeneration command:

```bash
uv run --extra dev python scripts/apply_gate_b_closeout_decisions.py \
  --ledger reports/gate_b_closeout_2026-05-22/gate_b_closeout_ledger.csv \
  --decisions reports/gate_b_closeout_2026-05-22/gate_b_closeout_decisions_partial_2026-05-22.csv \
  --out-dir reports/gate_b_closeout_2026-05-22 \
  --run-id gate_b_closeout_2026-05-22 \
  --source-uri reports/gate_b_closeout_2026-05-22/gate_b_closeout_decisions_partial_2026-05-22.csv \
  --decision-evidence-status human_attested_not_independently_verified
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

- Simulation decisions never advance real Gate B status.
- Real Gate B remains `blocked_pending_human_closeout`.
- Gate C remains blocked.
- The simulation artifact is a workflow rehearsal, not evidence.
- No citable benchmark or clinical result is introduced.

## Validation Log

Executed before final commit:

```bash
uv run --extra dev ruff check src/reports/gate_b_closeout.py scripts/apply_gate_b_closeout_decisions.py scripts/build_gate_b_closeout_ledger.py tests/test_gate_b_closeout.py
uv run --extra dev pytest tests/test_gate_b_closeout.py
uv run --extra dev ruff check .
uv run --extra dev --extra torch pytest
git diff --check
```

Result:

- Targeted Ruff: passed.
- Targeted pytest: 6 passed.
- Full Ruff: passed.
- Full pytest: 308 passed.
- `git diff --check`: passed.
