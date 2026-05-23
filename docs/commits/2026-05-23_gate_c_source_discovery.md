# 2026-05-23 Gate C Source Discovery

## Scope

Added a scanner for source tables required by Gate C input materialization and
executed it against local `data` and `reports`.

## Files

- `src/artifacts/gate_c_source_discovery.py`
- `scripts/discover_gate_c_sources.py`
- `tests/test_gate_c_source_discovery.py`
- `reports/gate_c_source_discovery_2026-05-23/gate_c_source_discovery.json`
- `reports/gate_c_source_discovery_2026-05-23/gate_c_source_candidates.csv`
- `reports/gate_c_source_discovery_2026-05-23/gate_c_source_discovery.md`
- `docs/research/2026-05-23_gate_c_source_discovery.md`

## Local Result

- `scan_status`: `blocked_missing_gate_c_sources`
- `files_scanned`: `70`
- `readable_tables`: `70`
- `recordings_ready`: `0`
- `events_ready`: `0`

## Scientific Guardrail

The scan prevents a false next step. The project cannot materialize Gate C
inputs until real source `recordings` and `events` tables exist locally.

## Validation

- `uv run ruff check src/artifacts/gate_c_source_discovery.py scripts/discover_gate_c_sources.py tests/test_gate_c_source_discovery.py`
- `uv run pytest tests/test_gate_c_source_discovery.py -q`
- `uv run python scripts/discover_gate_c_sources.py --root data --root reports --out-dir reports/gate_c_source_discovery_2026-05-23`
- `uv run ruff check .`
- `uv run pytest tests/test_gate_c_source_discovery.py tests/test_gate_c_materialize_inputs.py tests/test_gate_c_input_discovery.py tests/test_gate_c_freeze_package.py tests/test_gate_c_dry_run.py tests/test_gate_c_registry.py -q`
- `uv run pytest -q`
