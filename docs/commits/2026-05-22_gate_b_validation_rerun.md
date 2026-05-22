# Commit Trace: Gate B Validation Rerun Harness

Date: 2026-05-22

## Scope

Add a Gate B validation rerun harness that checks real closeout rows against a
fresh local guardrail rerun.

## Files Changed

- `src/reports/gate_b_validation.py`
- `scripts/run_gate_b_validation_rerun.py`
- `tests/test_gate_b_validation.py`
- `reports/gate_b_validation_rerun_2026-05-22/*`
- `docs/research/2026-05-22_gate_b_validation_rerun.md`
- `docs/commits/2026-05-22_gate_b_validation_rerun.md`

## Commands

```bash
git fetch --prune origin
git switch -c codex/gate-b-validation-rerun origin/main
uv run ruff check src/reports/gate_b_validation.py scripts/run_gate_b_validation_rerun.py tests/test_gate_b_validation.py
uv run pytest tests/test_gate_b_validation.py -q
uv run python scripts/run_local_gate_guardrails.py \
  --out-dir reports/gate_b_validation_rerun_2026-05-22/guardrails \
  --gate-b-status partial \
  --gate-c-status not_started
uv run python scripts/run_gate_b_validation_rerun.py \
  --closeout-ledger reports/gate_b_closeout_2026-05-22/gate_b_closeout_ledger.csv \
  --closeout-summary reports/gate_b_real_closeout_2026-05-22/gate_b_real_closeout_summary.csv \
  --guardrails-dir reports/gate_b_validation_rerun_2026-05-22/guardrails \
  --out-dir reports/gate_b_validation_rerun_2026-05-22 \
  --run-id gate_b_validation_rerun_2026-05-22 \
  --source-uri reports/gate_b_validation_rerun_2026-05-22/guardrails
```

## Result

```json
{
  "gate_b_validation_status": "blocked_pending_real_closeout",
  "gate_b_passed": false,
  "gate_b_open_actions": 5,
  "gate_b_p0_open_actions": 0,
  "claim_status": "gate_b_validation_rerun_not_citable_pre_gate_c"
}
```

## Audit Notes

- The harness rejects simulation markers in the real validation path.
- Gate B remains blocked until `GB-004` through `GB-008` are closed with real
  evidence.
- Passing this harness will only unlock Gate C dry-run; it will not by itself
  make benchmark rows citable.
