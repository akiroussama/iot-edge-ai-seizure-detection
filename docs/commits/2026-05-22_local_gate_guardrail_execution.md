# Commit Trace - Local Gate Guardrail Execution

Date: 2026-05-22

Branch: `codex/run-gate-guards-local`

Base: `origin/main@82b3d0a`

## Intent

Execute the MSG and SeizeIT2 guardrails against the real local artifacts
available in the clean repository checkout, then materialize a Gate B/Gate C
checklist with evidence, owners, and exit criteria.

## Files

Code:

- `src/reports/gate_bc_checklist.py`
- `scripts/run_local_gate_guardrails.py`
- `tests/test_gate_bc_checklist.py`

Docs:

- `docs/research/2026-05-22_local_gate_guardrail_execution.md`
- `docs/commits/2026-05-22_local_gate_guardrail_execution.md`

Generated audit outputs:

- `reports/local_gate_guardrails_2026-05-22/`

## Execution Log

Command:

```bash
uv run --extra dev python scripts/run_local_gate_guardrails.py \
  --out-dir reports/local_gate_guardrails_2026-05-22 \
  --gate-b-status not_started \
  --gate-c-status not_started
```

Output:

```json
{
  "out_dir": "reports/local_gate_guardrails_2026-05-22",
  "msg_p0_patients": 3,
  "msg_unmatched_events": 258,
  "seizeit2_blockers": 20,
  "checklist_actions": 8,
  "claim_status": "gate_bc_action_checklist_pre_gate_c_not_citable"
}
```

## Key Outputs

- MSG P0 patients: `1942`, `1219`, `1675`.
- MSG unmatched events: `258`.
- SeizeIT2 local artifact status: blocked local `sub-125` subset, not a
  full-cohort result.
- Combined checklist actions: `8`.
- P0 actions: `3`.
- Gate C action: freeze blocked until Gate B checklist items are closed.

## Guardrails

- No model scoring or training.
- No citable result.
- No Gate C pass.
- Local Markdown reports are converted to structured CSV only because raw local
  CSV/parquet inputs are not present in the clean checkout.
- All generated artifacts carry pre-Gate-C claim status.

## Validation Log

Executed before final commit:

```bash
uv run --extra dev ruff check src/reports/gate_bc_checklist.py scripts/run_local_gate_guardrails.py tests/test_gate_bc_checklist.py
uv run --extra dev pytest tests/test_gate_bc_checklist.py tests/test_msg_gap_triage.py tests/test_seizeit2_cohort_readiness.py
uv run --extra dev ruff check .
uv run --extra dev --extra torch pytest
git diff --check
```

Result:

- Targeted Ruff: passed.
- Targeted pytest: 9 passed.
- Full Ruff: passed.
- Full pytest: 302 passed.
- `git diff --check`: passed.
