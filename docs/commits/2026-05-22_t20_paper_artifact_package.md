# T20 Paper Artifact Package

Date: 2026-05-22

Branch: `codex/paper-artifact-package`

Base: `origin/main@e5eb88c`

## Objective

Convert the growing EpiTwin-Open engineering corpus into a paper-facing
artifact package: every claim must link to a committed artifact or source, and
pre-Gate-C benchmark numbers must remain visibly non-citable.

## Implementation Plan

- Add an artifact inventory builder with SHA-256 hashes.
- Add a claim traceability table that flags missing artifacts and citable claims
  before Gate C.
- Add a reproducibility checklist for the current benchmark paper path.
- Add a CLI that writes CSV, JSON, and Markdown package outputs.
- Add tests with a synthetic repo root and explicit Gate C guardrail checks.

## Scientific Guardrails

- No phantom citations.
- No citable benchmark claim before Gate C.
- Method claims are allowed only when linked to committed code/config/schema.
- External SOTA comparisons remain non-citable until row-level recomputation and
  frozen artifacts exist.
- Negative/null-overlapping outcomes are treated as reportable scientific
  results, not failures to hide.

## Validation Log

Targeted validation:

```bash
uv run --extra dev ruff check src/reports/paper_artifact_package.py src/reports/__init__.py scripts/build_paper_artifact_package.py tests/test_paper_artifact_package.py
uv run --extra dev pytest tests/test_paper_artifact_package.py
uv run --extra dev pytest tests/test_paper_artifact_package.py tests/test_external_sota_reproduction.py tests/test_workflow_forensics.py tests/test_leaderboard_runner.py
```

Full validation:

```bash
uv run --extra dev ruff check .
uv run --extra dev --extra torch pytest
```

Result:

- Targeted Ruff: passed.
- New tests: 5 passed.
- Neighbor tests: 17 passed.
- Full Ruff: passed.
- Full pytest: 273 passed.

## Result

Task20 now has an executable paper artifact package builder. It produces an
inventory, claim traceability table, reproducibility checklist, JSON manifest,
and Markdown package while enforcing the key publication guardrail: no citable
benchmark-result bundle before Gate C.
