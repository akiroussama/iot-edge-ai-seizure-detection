# Commit Trace - SeizeIT2 Cohort Readiness Guardrail

Date: 2026-05-22

Branch: `codex/seizeit2-cohort-readiness`

Base: `origin/main@246a765`

## Intent

Add a full-cohort claim guardrail for SeizeIT2 so a small local smoke test,
partial subject set, missing official split manifest, or count mismatch cannot
be described as full-cohort benchmark evidence.

## Files

- `src/reports/seizeit2_cohort_readiness.py`
- `scripts/build_seizeit2_cohort_readiness.py`
- `tests/test_seizeit2_cohort_readiness.py`
- `docs/research/2026-05-22_seizeit2_cohort_readiness.md`
- `docs/commits/2026-05-22_seizeit2_cohort_readiness.md`

## Guardrails

- Claim status: `seizeit2_cohort_readiness_pre_gate_c_not_citable`.
- Gate B and Gate C are hard blockers for citable cohort claims.
- Missing or mismatched expected counts are blockers by default.
- Required splits, tasks, modalities, and ready track rows are explicit checks.
- The report does not train, score, or upgrade any benchmark result.

## Validation Log

Executed before final commit:

```bash
uv run --extra dev ruff check src/reports/seizeit2_cohort_readiness.py scripts/build_seizeit2_cohort_readiness.py tests/test_seizeit2_cohort_readiness.py
uv run --extra dev pytest tests/test_seizeit2_cohort_readiness.py tests/test_seizeit2_benchmark_track.py
uv run --extra dev ruff check .
uv run --extra dev --extra torch pytest
git diff --check
```

Result:

- Targeted Ruff: passed.
- Targeted pytest: 10 passed.
- Full Ruff: passed.
- Full pytest: 300 passed.
- `git diff --check`: passed.
