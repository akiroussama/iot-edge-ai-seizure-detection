# Commit Trace: Gate B Real Decision Intake

Date: 2026-05-23

## Scope

Add a real-decision intake/preflight step before applying reviewer-supplied Gate
B decisions to the closeout ledger.

## Files Changed

- `src/reports/gate_b_decision_intake.py`
- `scripts/run_gate_b_real_decision_intake.py`
- `tests/test_gate_b_decision_intake.py`
- `reports/gate_b_real_decision_intake_2026-05-23/*`
- `docs/research/2026-05-23_gate_b_real_decision_intake.md`
- `docs/commits/2026-05-23_gate_b_real_decision_intake.md`

## Commands

```bash
git fetch --prune origin
git switch -c codex/gate-b-real-decision-intake origin/main
uv run ruff check src/reports/gate_b_decision_intake.py scripts/run_gate_b_real_decision_intake.py tests/test_gate_b_decision_intake.py
uv run pytest tests/test_gate_b_decision_intake.py -q
uv run python scripts/run_gate_b_real_decision_intake.py \
  --closeout-ledger reports/gate_b_closeout_2026-05-22/gate_b_closeout_ledger.csv \
  --required-decisions reports/gate_b_real_closeout_2026-05-22/gate_b_real_closeout_required_decisions_template.csv \
  --decisions reports/gate_b_real_closeout_2026-05-22/gate_b_real_closeout_required_decisions_template.csv \
  --out-dir reports/gate_b_real_decision_intake_2026-05-23 \
  --run-id gate_b_real_decision_intake_2026-05-23 \
  --source-uri reports/gate_b_real_closeout_2026-05-22/gate_b_real_closeout_required_decisions_template.csv
```

## Result

```json
{
  "intake_status": "blocked_invalid_or_incomplete_decisions",
  "gate_b_next_status": "blocked_by_real_decision_intake",
  "required_rows": 5,
  "accepted_rows": 0,
  "issue_rows": 5,
  "claim_status": "gate_b_real_decision_intake_not_citable_pre_gate_c"
}
```

## Audit Notes

- This commit does not close Gate B.
- Blank decision rows are explicitly blocked.
- Simulation markers are rejected in the real-decision path.
- Valid intake is a prerequisite to applying decisions and rerunning Gate B
  validation.
