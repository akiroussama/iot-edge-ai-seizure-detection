# 2026-05-23 Gate C Input Materialization

## Scope

Added an executable materialization harness that turns source `recordings` and
`events` tables into Gate C `events`, `labels`, and `splits` artifacts.

## Files

- `src/artifacts/gate_c_materialize_inputs.py`
- `scripts/materialize_gate_c_inputs.py`
- `tests/test_gate_c_materialize_inputs.py`
- `docs/research/2026-05-23_gate_c_input_materialization.md`

## Result

The harness can now:

- validate source recordings and seizure events
- generate fixed windows
- create SPH/SOP labels
- apply leakage-aware splits
- write `events`, `labels`, `splits`, `leakage_audit.txt`, and a manifest
- validate the outputs against the Gate C freeze package contract
- provide the next `build_gate_c_freeze_package.py` command

## Scientific Guardrail

The harness does not make citable claims. Its manifest uses
`not_citable_until_gate_c_freeze_package`, and citable promotion still requires
the separate Gate C freeze package plus DOI/preregistration.

## Validation

- `uv run ruff check src/artifacts/gate_c_materialize_inputs.py scripts/materialize_gate_c_inputs.py tests/test_gate_c_materialize_inputs.py`
- `uv run pytest tests/test_gate_c_materialize_inputs.py -q`
- `uv run ruff check .`
- `uv run pytest tests/test_gate_c_materialize_inputs.py tests/test_gate_c_freeze_package.py tests/test_gate_c_input_discovery.py tests/test_gate_c_dry_run.py tests/test_gate_c_registry.py -q`
- `uv run pytest -q`
