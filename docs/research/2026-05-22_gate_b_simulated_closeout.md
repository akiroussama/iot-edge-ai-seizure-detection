# Gate B Simulated Closeout

Date: 2026-05-22

Branch: `codex/gate-b-simulated-closeout`

Base: `origin/main@ca8d69e`

## Objective

Apply the reviewer-provided positive simulation decisions for `GB-004` through
`GB-008` in a separate simulation artifact, without upgrading the real Gate B
ledger to a pass.

The reviewer explicitly described these rows as simulation data. Therefore this
run treats them as a workflow rehearsal, not real Gate B evidence.

## Implementation

- Added `decision_evidence_status` to Gate B closeout summaries, manifests, and
  Markdown.
- Added `--decision-evidence-status` to:
  - `scripts/build_gate_b_closeout_ledger.py`;
  - `scripts/apply_gate_b_closeout_decisions.py`.
- Added tests proving simulated closeout cannot advance the real Gate B status.
- Added simulation decisions:
  `reports/gate_b_closeout_simulation_2026-05-22/gate_b_closeout_decisions_simulated_remaining_2026-05-22.csv`.
- Generated simulation outputs under
  `reports/gate_b_closeout_simulation_2026-05-22/`.

The real partial ledger in `reports/gate_b_closeout_2026-05-22/` was regenerated
only to include `decision_evidence_status=human_attested_not_independently_verified`.
Its status remains `blocked_pending_human_closeout`.

## Simulation Execution

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

## Simulation Result

- Simulation ledger rows: 8.
- Simulation closed rows: 8.
- Simulation open rows: 0.
- Simulation P0 open rows: 0.
- Simulation status: `simulation_complete_not_gate_b_evidence`.

This status is intentionally not `ready_for_gate_b_validation_rerun`.

## Real Ledger State

The real ledger remains:

- Closed rows: 3.
- Open rows: 5.
- P0 open rows: 0.
- Gate B status: `blocked_pending_human_closeout`.
- Decision evidence status: `human_attested_not_independently_verified`.

## Guardrails

- Simulation decisions are not real evidence.
- The simulation folder is not a Gate B pass.
- The real ledger remains blocked.
- Gate C remains blocked until real evidence closes all rows, guardrails rerun,
  and Gate C dry-run is clean.
- No clinical result or benchmark claim is introduced.

## Validation

Targeted validation:

```bash
uv run --extra dev ruff check src/reports/gate_b_closeout.py scripts/apply_gate_b_closeout_decisions.py scripts/build_gate_b_closeout_ledger.py tests/test_gate_b_closeout.py
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
- Targeted pytest: 6 passed.
- Full Ruff: passed.
- Full pytest: 308 passed.
- `git diff --check`: passed.
