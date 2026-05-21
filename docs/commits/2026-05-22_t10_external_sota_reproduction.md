# T10 External SOTA Reproduction Bridge

Date: 2026-05-22

Branch: `codex/reproduce-first-sota`

Base: `origin/main@1fee975`

## Objective

Create the first reproducible bridge between external SOTA-family claims and
the EpiTwin leaderboard runner. The purpose is not to claim a new SOTA number;
it is to make future SOTA comparison falsifiable, schema-compatible, and honest
about modality, split, label, and horizon mismatch.

## Primary Sources Checked

- SeizeIT2 official wearable focal-epilepsy dataset and detection baselines:
  Bhagubai et al., Scientific Data 12, 1228 (2025),
  DOI `10.1038/s41597-025-05580-x`.
- Wearable seizure likelihood forecasting with HR/sleep/steps:
  Stirling et al., Frontiers in Neurology 12:704060 (2021),
  DOI `10.3389/fneur.2021.704060`.
- MSG long-term wearable forecasting dataset and hybrid short/long-horizon
  context: Zenodo `10.5281/zenodo.17380899`, linked article
  DOI `10.1111/epi.18466`.

## Implementation Plan

- Add a strict external prediction normalizer that maps arbitrary external
  score columns to the EpiTwin prediction contract.
- Add a runner that calls `scripts/make_leaderboard_row.py` logic directly, so
  a reproduced external family produces the same leaderboard schema as internal
  models.
- Add a manifest and Markdown dossier that keep source citation, DOI/URL,
  reproduction status, original metric summary, and mismatch notes visible.
- Add a YAML contract with pinned candidate source families and mismatch risks.
- Add synthetic tests proving adapter output is non-citable and does not hide
  clipped risks or mismatch status.

## Scientific Guardrails

- External reported metrics remain context unless row-level predictions are
  recomputed under the EpiTwin runner.
- Detection, early-warning, and forecasting tasks must remain separate.
- A citable comparison requires Gate C frozen artifacts.
- Any mismatch with the source paper must be explicit in `mismatch_notes`.
- Synthetic adapter tests are not SOTA claims.

## Validation Log

Targeted validation:

```bash
uv run --extra dev ruff check src/reports/external_sota_reproduction.py src/reports/__init__.py scripts/run_external_sota_reproduction.py tests/test_external_sota_reproduction.py
uv run --extra dev pytest tests/test_external_sota_reproduction.py
uv run --extra dev pytest tests/test_external_sota_reproduction.py tests/test_leaderboard_runner.py tests/test_seizeit2_benchmark_track.py
```

Result:

- Targeted Ruff: passed.
- New tests: 4 passed.
- Neighbor tests: 15 passed.

Full validation pending below.

Full validation:

```bash
uv run --extra dev ruff check .
uv run --extra dev --extra torch pytest
```

Result:

- Full Ruff: passed.
- Full pytest: 268 passed.

## Result

Task10 now has a strict external-SOTA reproduction bridge. Future external
families can only enter the leaderboard through row-level predictions scored by
the existing EpiTwin runner, with source provenance and mismatch notes logged in
the reproduction dossier.
