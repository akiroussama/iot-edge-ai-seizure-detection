# Gate B Real Closeout

Date: 2026-05-22

## Objective

Turn Gate B closeout from a partial human-attested ledger plus positive
simulation rows into a real, auditable closeout path. The work must not promote
simulation decisions into citable Gate B evidence.

## Inputs

- Real partial ledger:
  `reports/gate_b_closeout_2026-05-22/gate_b_closeout_ledger.csv`
- Positive simulation decisions:
  `reports/gate_b_closeout_simulation_2026-05-22/gate_b_closeout_decisions_simulated_remaining_2026-05-22.csv`

## Implementation

- Added a simulation-marker guardrail to `apply_gate_b_closeout_decisions`.
  Decisions containing simulation markers now fail if the source/status does
  not explicitly declare a simulation context.
- Added a dedicated real closeout package builder:
  `scripts/build_gate_b_real_closeout_package.py`.
- Added a real closeout package model in `src/reports/gate_b_closeout.py`.
  Simulation rows are used only as reviewer-intent hints and are not copied into
  the real human-decision template.

## Generated Artifacts

Output directory:

`reports/gate_b_real_closeout_2026-05-22`

Files:

- `gate_b_real_closeout_readiness.csv`
- `gate_b_real_closeout_required_decisions_template.csv`
- `gate_b_real_closeout_summary.csv`
- `gate_b_real_closeout_manifest.json`
- `gate_b_real_closeout.json`
- `gate_b_real_closeout.md`

## Result

```json
{
  "out_dir": "reports/gate_b_real_closeout_2026-05-22",
  "gate_b_real_closeout_status": "blocked_pending_real_evidence",
  "ledger_rows": 8,
  "real_closed_rows": 3,
  "real_open_rows": 5,
  "simulation_available_open_rows": 5,
  "claim_status": "gate_b_real_closeout_pending_validation_not_citable"
}
```

## Interpretation

Gate B is not closed. The real ledger has 3 closed rows and 5 open rows. The
positive simulation decisions for `GB-004` through `GB-008` are preserved only
as hints; they do not unlock real Gate B, Gate C freeze, or citable benchmark
claims.

The next real input needed is a non-simulated human decision sheet for:

- `GB-004`: MSG denominator integrity.
- `GB-005`: MSG horizon feasibility.
- `GB-006`: SeizeIT2 track completeness.
- `GB-007`: MSG horizon source review.
- `GB-008`: SeizeIT2 negative readiness rows.

## Validation

Targeted tests:

`uv run pytest tests/test_gate_b_closeout.py -q`

Result: 9 passed.
