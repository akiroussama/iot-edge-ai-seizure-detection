# Gate B Audit Acceleration

Date: 2026-05-22
Branch: `codex/gate-b-audit-acceleration`
Base: `origin/main@b3e951a`

## Objective

Add a human-facing Gate B audit package builder so active audit selection
becomes directly usable for the manual seizure-timeline review bottleneck.

## Changes

- Added `src/reports/gate_b_audit_package.py`.
- Added `scripts/build_gate_b_audit_package.py`.
- Added `tests/test_gate_b_audit_package.py`.
- Added `docs/research/2026-05-22_gate_b_audit_acceleration_package.md`.

## Guardrails

- The generated package is `pending_human_review_not_gate_b_pass`.
- Outputs are audit prioritization only and not citable benchmark results.
- Review decision columns stay blank and must be filled by a human.
- Gate C remains blocked until Gate B is complete and frozen artifacts are
  registered.

## Validation

```bash
uv run --extra dev ruff check src/reports/gate_b_audit_package.py scripts/build_gate_b_audit_package.py tests/test_gate_b_audit_package.py src/reports/__init__.py
uv run --extra dev pytest tests/test_gate_b_audit_package.py tests/test_active_audit_selection.py tests/test_label_audit.py
uv run --extra dev ruff check .
uv run --extra dev --extra torch pytest
git diff --check
```

Results:

- Ruff: passed.
- Targeted pytest: 15 passed.
- Full pytest: 290 passed.
- Diff whitespace check: passed.
