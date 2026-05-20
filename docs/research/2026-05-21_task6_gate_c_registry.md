# Task 6 - Gate C Freeze Registry Scaffold

Date: 2026-05-21
Branch: `codex/gate-c-freeze-registry`
Base: `origin/main@3320e6d`
Status: engineering-only, pre-Gate-C-safe.

## Plan

Task 6 implements the machinery required before any future benchmark row can
be treated as citable:

- artifact registry schema;
- checksum, byte-size, row-count, event-count, and split-count verification;
- split manifest;
- CLI to create a registry;
- CLI to verify a registry;
- leaderboard guardrail that refuses citable or frozen rows without a clean
  frozen registry.

This PR does not freeze a real dataset and does not claim Gate C has passed.
The human audit and final artifact decision remain outside this engineering
change.

## Plan Validation

This task follows directly from the fused scoring document:

- Task 5 is merged and makes calibration/BSS reportable.
- Task 8 is the highest-value future task, but it requires citable frozen
  artifacts.
- Gate C is therefore the required bridge between exploratory infrastructure
  and publishable results.

The implementation is valid if synthetic tests can create and verify a
registry, detect file tampering, and prove that a `citable_after_gate_c`
leaderboard row cannot be emitted without a verified frozen registry.

## Attack

Implementation choices:

- `src/artifacts/registry.py` is pure logic: no hidden global state and no
  real-data assumptions.
- Artifact records store `sha256`, byte size, table row count, event count for
  event tables, positive-window count for label tables, and split counts when a
  split column is present.
- Registry status is explicit:
  - `gate_c_status`: `not_started`, `partial`, `passed`, `failed`;
  - `freeze_status`: `engineering_scaffold`, `pending_human_audit`, `frozen`,
    `failed`.
- `gate_c_status=passed` requires `freeze_status=frozen`.
- The leaderboard runner now requires `--artifact-registry` when a row is
  citable or frozen.
- If a registry is provided, it is verified before the row is returned.

## Result

Implemented files:

- `src/artifacts/__init__.py`
- `src/artifacts/registry.py`
- `schemas/gate_c_registry.schema.json`
- `scripts/make_gate_c_registry.py`
- `scripts/verify_gate_c_registry.py`
- `scripts/make_leaderboard_row.py`
- `tests/test_gate_c_registry.py`
- `docs/research/2026-05-21_task6_gate_c_registry.md`

Example registry creation:

```bash
uv run --extra dev python scripts/make_gate_c_registry.py \
  --out artifacts/registry/example.json \
  --registry-id example \
  --dataset synthetic \
  --dataset-version v1 \
  --source-uri tests \
  --generation-command "pytest" \
  --artifact labels=labels:path/to/labels.csv \
  --artifact events=events:path/to/events.csv \
  --split-policy synthetic \
  --split-ref tests/split_manifest.json \
  --split-id train \
  --split-id val \
  --split-id test
```

Example verification:

```bash
uv run --extra dev python scripts/verify_gate_c_registry.py \
  --registry artifacts/registry/example.json
```

For citable rows:

```bash
uv run --extra dev python scripts/make_leaderboard_row.py \
  ... \
  --result-status gate_c_frozen_citable \
  --citation-status citable_after_gate_c \
  --gate-c-status passed \
  --split-frozen-status frozen_git_tag \
  --artifact-registry artifacts/registry/example.json
```

## Audit

What this prevents:

- citable leaderboard rows without frozen artifact evidence;
- silently changed local files after a result is reported;
- split manifests that exist only as prose;
- registry entries whose row counts no longer match disk.

What this does not do:

- it does not upload to Zenodo;
- it does not tag a release;
- it does not mark real MSG or SeizeIT2 artifacts as frozen;
- it does not bypass the human label-audit gate.

## Commands

```bash
python -m json.tool schemas/gate_c_registry.schema.json >/dev/null
uv run --extra dev ruff check src/artifacts/__init__.py \
  src/artifacts/registry.py scripts/make_gate_c_registry.py \
  scripts/verify_gate_c_registry.py scripts/make_leaderboard_row.py \
  tests/test_gate_c_registry.py tests/test_leaderboard_runner.py
uv run --extra dev pytest tests/test_gate_c_registry.py \
  tests/test_leaderboard_runner.py tests/test_leaderboard_schema.py
git diff --check
```

Validation result:

- JSON schema parse: pass.
- Targeted ruff: pass.
- Targeted pytest: `12 passed`.
- Full suite: `uv run --extra dev --extra torch pytest` -> `165 passed`.

## Conclusion

Task 6 makes Gate C enforceable in code. Future benchmark rows can still be
exploratory without a registry, but any row claiming citable frozen status now
must point to a registry whose artifacts, split manifest, checksums, counts,
and Gate C status verify cleanly.
