# 2026-05-23 Gate C Freeze Harness

## Scope

Added an executable harness that turns real frozen Gate C artifacts into a
registry-backed citable package, while failing closed when required evidence is
missing.

## Files

- `src/artifacts/gate_c_freeze_package.py`
- `scripts/build_gate_c_freeze_package.py`
- `tests/test_gate_c_freeze_package.py`
- `docs/research/2026-05-23_gate_c_freeze_harness.md`

## Scientific Result

This does not claim a real Gate C freeze. It adds the missing deterministic
path to create one once the true frozen `events`, `labels`, and `splits`
artifacts are available.

## Guardrails

- Requires DOI or preregistration URI.
- Requires `events`, `labels`, and `splits` roles.
- Requires non-empty clinical events.
- Requires labeled windows with valid split, timestamp, boolean, and duplicate
  checks.
- Requires splits to align with labels.
- Requires Gate B status to remain `passed` through the Gate C dry-run.
- Writes a frozen registry only when dry-run diagnostics have zero blockers.

## Validation

- `uv run ruff check src/artifacts/gate_c_freeze_package.py scripts/build_gate_c_freeze_package.py tests/test_gate_c_freeze_package.py`
- `uv run pytest tests/test_gate_c_freeze_package.py -q`
- `uv run ruff check .`
- `uv run pytest tests/test_gate_c_freeze_package.py tests/test_gate_c_dry_run.py tests/test_gate_c_registry.py -q`
- `uv run pytest -q`
