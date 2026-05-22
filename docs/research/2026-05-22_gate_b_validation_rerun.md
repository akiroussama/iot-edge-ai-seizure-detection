# Gate B Validation Rerun Harness

Date: 2026-05-22

## Objective

Build the validation harness that checks real Gate B closeout decisions against
a fresh local guardrail rerun. The harness must not make benchmark rows citable
and must not promote simulated decisions into real evidence.

## Inputs

- Real closeout ledger:
  `reports/gate_b_closeout_2026-05-22/gate_b_closeout_ledger.csv`
- Real closeout summary:
  `reports/gate_b_real_closeout_2026-05-22/gate_b_real_closeout_summary.csv`
- Fresh local guardrail rerun:
  `reports/gate_b_validation_rerun_2026-05-22/guardrails`

## Implementation

- Added `src/reports/gate_b_validation.py`.
- Added `scripts/run_gate_b_validation_rerun.py`.
- Added `tests/test_gate_b_validation.py`.
- Generated `reports/gate_b_validation_rerun_2026-05-22/`.

The harness joins the current guardrail action checklist to the closeout ledger
by action key:

`gate`, `priority`, `domain`, `blocker_source`, `action`

It emits a validation matrix where each current guardrail action is:

- `closed_by_real_attestation`
- `pending_real_closeout`
- `needs_source_review`
- `invalid_real_closeout`
- `missing_closeout_row`

Simulation markers in a real closeout ledger force
`blocked_simulation_marker_detected`.

## Commands

```bash
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
  "out_dir": "reports/gate_b_validation_rerun_2026-05-22",
  "gate_b_validation_status": "blocked_pending_real_closeout",
  "gate_b_passed": false,
  "gate_b_open_actions": 5,
  "gate_b_p0_open_actions": 0,
  "claim_status": "gate_b_validation_rerun_not_citable_pre_gate_c"
}
```

The rerun guardrails still surface:

- MSG P0 patients: 3.
- MSG unmatched events: 258.
- MSG not-main horizons: 5.
- MSG source-review horizons: 1.
- SeizeIT2 readiness status: `blocked`.
- SeizeIT2 blockers: 20.

The validation matrix shows:

- `GB-001`: closed by real attestation.
- `GB-002`: closed by real attestation.
- `GB-004` to `GB-008`: pending real closeout.

`GB-003` is a Gate C freeze prerequisite row, so it is not counted as an open
Gate B action.

## Interpretation

Gate B is not passed. The current blocker is now precise: five non-P0 Gate B
actions need real closeout decisions. The prior positive simulation rows remain
non-promoted and non-citable.

Once the real closeout ledger has closed `GB-004` through `GB-008`, this harness
can be rerun. If it passes, the next status becomes `ready_for_gate_c_dry_run`,
not a citable benchmark pass.

## Validation

Targeted validation:

```bash
uv run ruff check src/reports/gate_b_validation.py scripts/run_gate_b_validation_rerun.py tests/test_gate_b_validation.py
uv run pytest tests/test_gate_b_validation.py -q
```

Result: 5 passed.
