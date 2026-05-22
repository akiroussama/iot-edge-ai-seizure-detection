# Gate C Dry-Run Diagnostics

Date: 2026-05-22
Branch: `codex/gate-c-dry-run-diagnostics`
Base: `origin/main@1bc70e4`

## Objective

Gate C is the bridge between exploratory engineering artifacts and citable
benchmark results. The registry scaffold already verifies hashes and artifact
counts, but the project also needs a dry-run diagnostic that says why a current
registry is or is not ready for a real freeze.

This block adds a non-citable Gate C dry-run report.

## Implementation

Added:

- `src/reports/gate_c_dry_run.py`
- `scripts/make_gate_c_dry_run_report.py`
- `tests/test_gate_c_dry_run.py`

The dry-run report:

- verifies the registry structurally without requiring frozen status;
- separately verifies frozen/citable readiness;
- checks Gate B status;
- checks required artifact roles;
- checks DOI/preregistration presence by default;
- emits blockers, warnings, artifact summary, JSON diagnostics, and Markdown.

## Output

The CLI writes:

- diagnostics JSON;
- Markdown report;
- optional artifact-summary table.

Example:

```bash
python scripts/make_gate_c_dry_run_report.py \
  --registry artifacts/registry/current_msg_gate_c.json \
  --out-json reports/gate_c_dry_run_msg_2026-05-22.json \
  --out-md reports/gate_c_dry_run_msg_2026-05-22.md \
  --artifact-summary-out reports/gate_c_dry_run_msg_artifacts_2026-05-22.csv \
  --gate-b-status partial
```

For a stricter citable-readiness check:

```bash
python scripts/make_gate_c_dry_run_report.py \
  --registry artifacts/registry/current_msg_gate_c.json \
  --out-json reports/gate_c_dry_run_msg_2026-05-22.json \
  --out-md reports/gate_c_dry_run_msg_2026-05-22.md \
  --gate-b-status passed \
  --required-role events \
  --required-role labels \
  --required-role splits \
  --fail-on-blockers
```

## Guardrails

- A dry-run report is not a Gate C pass.
- Structural verification and citable readiness are separate fields.
- Missing Gate B, unfrozen registry status, missing preregistration, or missing
  required artifact roles are blockers.
- The report introduces no benchmark number and does not make any row citable.

## Validation

```bash
uv run --extra dev ruff check src/reports/gate_c_dry_run.py scripts/make_gate_c_dry_run_report.py tests/test_gate_c_dry_run.py
uv run --extra dev pytest tests/test_gate_c_dry_run.py tests/test_gate_c_registry.py
uv run --extra dev ruff check .
uv run --extra dev --extra torch pytest
git diff --check
```

Results:

- Ruff: passed.
- Targeted pytest: 7 passed.
- Full pytest: 293 passed.
- Diff whitespace check: passed.

## Residual Risk

This diagnostic cannot decide that labels are clinically correct. Gate B still
requires a human audit log and passing review-sheet validation. Gate C still
requires an explicit freeze decision and preregistration/DOI before citable
benchmark rows are allowed.
