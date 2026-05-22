# General Coherence Review Fixes

Date: 2026-05-22

Branch: `codex/coherence-review-fixes`

Base: `origin/main@d7a61f7`

## Objective

Fix the highest-risk findings from the general coherence review:

1. clinical utility must not select policies whose FAR/day or Time-in-Warning
   metrics are missing;
2. leaderboard rows must fail closed when standardized probabilistic prediction
   columns are absent;
3. paper claim traceability must separate source URI presence from
   primary-source verification;
4. top-level docs must reflect the current roadmap state rather than stale
   May 15 wording.

## Changes

### Clinical utility fail-closed burden metrics

`src/reports/clinical_utility.py` now keeps missing FAR/day and TIW values as
missing instead of silently replacing them with zero. Rows with missing
sensitivity, FAR/day, or TIW become `ineligible`, and utility scores with
missing required components remain missing. This prevents a high-sensitivity
row with unknown alarm burden from being selected as the best policy.

Regression test:

- `tests/test_clinical_utility.py::test_clinical_utility_does_not_select_missing_burden_metrics`

### Leaderboard prediction contract

`scripts/make_leaderboard_row.py` now validates the standardized prediction
contract after filtering:

- `patient_id`
- `window_start`
- `window_end`
- `risk_score`
- `alarm`
- `forecast_label`
- `is_excluded`
- `recording_id` when events are recording-scoped

Required metric computation now raises an explicit `ValueError` instead of
returning silent `None` values for failed Brier/ECE/FAR/TIW computation.
Reference prediction tables used for BSS must also align by identity columns
and match `forecast_label` / `is_excluded`.

Regression tests:

- `tests/test_leaderboard_runner.py::test_leaderboard_row_requires_probabilistic_prediction_contract`
- `tests/test_leaderboard_runner.py::test_leaderboard_row_rejects_reference_row_mismatch`

### Paper claim traceability

`src/reports/paper_artifact_package.py` now treats source-only claims as ready
only when `source_verification_status` is `verified` or
`primary_source_verified`. A `source_uri` by itself remains traceable, but not
ready for paper use.

Regression tests:

- `tests/test_paper_artifact_package.py::test_build_paper_artifact_package_marks_unverified_source_uri_not_ready`
- `tests/test_paper_artifact_package.py::test_build_paper_artifact_package_accepts_verified_source_only_claim`

### Roadmap coherence

Updated:

- `README.md`: removed stale hard-coded Phase R3 `99 tests` wording.
- `PLAYBOOK.md`: revision 3 current-state refresh, Gate B/C still blocking
  citable claims, SeizureFormer clarified as contextual implant-derived SOTA
  rather than a direct HR/steps wearable comparator.
- `docs/PUBLICATION_PROPOSAL.md`: refreshed current readiness to 2026-05-22.
- `docs/ROADMAP_HIGH_LEVEL.md`: replaced the stale `tibia performance` wording
  with an explicit TinyML/edge performance guardrail.

## Validation

Commands run:

```bash
uv run --extra dev ruff check .
uv run --extra dev pytest tests/test_clinical_utility.py \
  tests/test_leaderboard_runner.py \
  tests/test_paper_artifact_package.py \
  tests/test_gate_c_registry.py \
  tests/test_external_sota_reproduction.py \
  tests/test_forecastability_atlas.py
uv run --extra dev --extra torch pytest
```

Results:

- Ruff: passed.
- Targeted/neighbor pytest: 32 passed.
- Full pytest: 287 passed.

## Residual Risk

This patch fixes fail-closed behavior and doc coherence. It does not make any
real-data number citable. Gate B human label audit and Gate C frozen artifacts
remain required before benchmark or clinical claims.
