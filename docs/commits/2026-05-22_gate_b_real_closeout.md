# Commit Trace: Gate B Real Closeout

Date: 2026-05-22

## Scope

Build a real Gate B closeout path that separates reviewer simulation data from
actual Gate B evidence.

## Files Changed

- `src/reports/gate_b_closeout.py`
- `scripts/build_gate_b_real_closeout_package.py`
- `tests/test_gate_b_closeout.py`
- `reports/gate_b_real_closeout_2026-05-22/*`
- `docs/research/2026-05-22_gate_b_real_closeout.md`
- `docs/commits/2026-05-22_gate_b_real_closeout.md`

## Commands

```bash
git fetch --prune origin
git switch -c codex/gate-b-real-closeout origin/main
uv run pytest tests/test_gate_b_closeout.py -q
uv run python scripts/build_gate_b_real_closeout_package.py \
  --ledger reports/gate_b_closeout_2026-05-22/gate_b_closeout_ledger.csv \
  --simulation-decisions reports/gate_b_closeout_simulation_2026-05-22/gate_b_closeout_decisions_simulated_remaining_2026-05-22.csv \
  --out-dir reports/gate_b_real_closeout_2026-05-22 \
  --run-id gate_b_real_closeout_2026-05-22 \
  --source-uri reports/gate_b_closeout_2026-05-22/gate_b_closeout_ledger.csv
```

## Result

```json
{
  "gate_b_real_closeout_status": "blocked_pending_real_evidence",
  "ledger_rows": 8,
  "real_closed_rows": 3,
  "real_open_rows": 5,
  "simulation_available_open_rows": 5,
  "claim_status": "gate_b_real_closeout_pending_validation_not_citable"
}
```

## Audit Notes

- Simulation decisions are not copied into the real decision template.
- Applying simulated decisions as real closeout now raises an error.
- Gate B remains blocked until real human evidence exists for `GB-004` through
  `GB-008`.
