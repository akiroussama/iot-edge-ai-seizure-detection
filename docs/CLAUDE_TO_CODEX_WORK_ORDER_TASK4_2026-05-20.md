# Claude Code -> Codex — Task 4 work order (forecast null models)

Date: 2026-05-20
Author: Claude Code (revising Codex's original Task 4 proposal after review).
Base: `origin/main` (Task 2 schema + Task 3 runner already merged).
Scope: constrained null models for forecasting, engineering only, pre-Gate-C
safe.

---

## Why this revised plan

Codex's original Task 4 proposal was sound on architecture and on the
anti-leakage rules; the Claude Code review identified six refinements before
implementation, all related to integrity discipline (Phase R lessons) and
test rigor. This document is the revised plan with those six points applied
and supersedes the original chat proposal as the authoritative spec.

## Objective

Implement constrained, reproducible null forecasting baselines suitable for
direct use as `--reference-predictions` of `scripts/make_leaderboard_row.py`
(Task 3 runner). **No real-data run in this PR. Synthetic tests only.**

## Branch

Create `codex/forecast-null-models` from `origin/main`. Task 4 is
autonomous: it produces null predictions + metadata only; the leaderboard
runner consumes them as a follow-up (a later PR).

## Null Models (4 mandatory)

### 1. `split_prevalence_prior` — climatology baseline (MANDATORY)

Risk = positive fraction on `fit_split`. Constant per window. This is the
canonical climatology baseline for Brier Skill Score; without it BSS is hard
to defend at Q1 review. **Promoted from "optional" in the original proposal.**

### 2. `rate_matched_random`

Random alarms whose alarm rate matches `--target-tiw` on `threshold_split`.
Seed-reproducible. Serves as the minimal random reference.

### 3. `patient_prior`

Per-patient constant risk learned from `fit_split`.

- If a patient is absent from `fit_split` OR has fewer than
  `--patient-min-events` (default `3`, parameterized) → **fallback to
  `split_prevalence_prior` for that patient**.
- The fallback **MUST be marked explicitly** in the output column
  `null_model_variant` (see Output Schema). No silent fallback. Direct
  application of the Phase R C3 lesson ("silent rule degeneracy").

### 4. `cycle_preserving_random`

Preserves hour-of-day structure of alarms from `fit_split`. 24 bins derived
from `window_start.dt.hour`. Bins with zero positives in `fit_split`
contribute zero (tested edge case). Multiday cycles deferred to Task 6 by
scope discipline.

## Architecture

### `src/baselines/forecast_nulls.py`

Pure functions, **no IO**, mirroring the pattern of the existing
`src/baselines/random_rate_matched.py` and `cycle_baseline.py`.

Input DataFrame must contain at minimum:
`patient_id, recording_id, window_start, window_end, forecast_label,
is_excluded, split`.

**Output schema — mandatory contract:** input columns pass through
unchanged, with the following new columns appended:

- `risk_score` (float in [0, 1])
- `alarm` (bool)
- `null_model` (str — name of the executed model)
- `null_model_variant` (str — equals `null_model` by default; for
  `patient_prior` may be `patient_prior` OR `patient_prior_fallback_population`)
- `score_fit_split` (str)
- `threshold_source_split` (str)
- `target_tiw` (float)
- `seed` (int)

The pass-through guarantee matters: the Task 3 runner consumes these rows
and needs the identifier and label columns intact.

### `scripts/run_null_baseline.py`

CLI options:

- `--labels PATH` (input table)
- `--out PATH` (output predictions table)
- `--null-model {split_prevalence_prior,rate_matched_random,patient_prior,cycle_preserving_random}`
- `--fit-split train` (default)
- `--threshold-split val` (default)
- `--target-tiw 0.1` (default)
- `--split-col split` (default)
- `--patient-min-events 3` (default — minimum train events for non-fallback
  `patient_prior`)
- `--cycle-bin hour_of_day` (default)
- `--seed 42` (default)

**Per-model seed derivation.** If a future wrapper invokes multiple null
models with the same `--seed`, each model must use a derived stream — for
example `np.random.default_rng(seed).spawn(n_models)[i]` — documented in
the code. This avoids RNG coupling between models.

### `tests/test_forecast_nulls.py`

Synthetic only. See Tests below.

### `docs/research/2026-05-20_task4_forecast_null_models.md`

Plan / validation / attack / result / audit / conclusion / commands /
Gate-C note.

## Anti-leakage rules (mandatory, tested)

- Fit on `fit_split` only; **never on test**.
- Threshold on `threshold_split` only.
- **Forbidden columns — explicitly ignored if present** (no read, no
  influence on `risk_score`):
  - `time_to_next_seizure_seconds`
  - `time_since_last_seizure_seconds`
  - `is_right_censored`
  - `right_censoring_applied`
- Rows with `is_excluded=True` contribute neither to fit nor to threshold.
- `split` column missing or invalid → **explicit error** (no silent fallback).
- `fit_split` or `threshold_split` empty after `is_excluded` filtering →
  **explicit error**.

## Tests (mandatory)

**Anti-leakage and control:**

- (a) `rate_matched_random` approximately respects `target_tiw` on
  `threshold_split`.
- (b) `patient_prior` fit uses only `fit_split` (mutation: modifying test
  rows leaves the output unchanged).
- (c) `cycle_preserving_random` uses only `fit_split` for the bins.
- (d) Empty `threshold_split` → explicit error.
- (e) Test split never used for fit or threshold (mutation test).
- (f) Identical seed → identical output (strict reproducibility).
- (g) Forbidden column injected into the input → ignored in the output
  (no effect on `risk_score`).

**Fallback marking (Phase R C3 lesson):**

- (h) `patient_prior` on a patient with 0 train events (or below
  `--patient-min-events`) → output rows for that patient carry
  `null_model_variant=patient_prior_fallback_population`.
- (i) The count of `patient_prior` vs `patient_prior_fallback_population`
  variants is correctly reportable from the output.

**Null-model behavior sanity (the models actually behave as nulls):**

- (j) `split_prevalence_prior` produces Brier ≈ `p(1 - p)` where `p` is the
  train positive rate.
- (k) Brier Skill Score of `split_prevalence_prior` against itself ≈ 0.
- (l) `rate_matched_random` Brier is near `p(1 - p)` (random climatology).

These behavior tests catch a model that is structurally sound but does not
do its job. The Task 1-3 review noted that purely structural tests can let
broken-behavior code pass — these add the missing layer.

## Validation commands

```bash
git diff --check
uv run --extra dev pytest tests/test_forecast_nulls.py
uv run --extra dev ruff check src/baselines/forecast_nulls.py \
  scripts/run_null_baseline.py tests/test_forecast_nulls.py
```

## Risk audit

| Risk | Mitigation |
|---|---|
| Too many null models | 4 mandatory including the climatology reference |
| `cycle_preserving_random` too ambitious | Hour-of-day only; multiday deferred to Task 6 |
| Confusion with a clinical result | No real-data run; "engineering only" in the doc; output tagged with `null_model` |
| `patient_prior` silent fallback | `null_model_variant` column + tests (h)/(i) |
| Empty cycle bin | Edge case tested; zero contribution documented |
| RNG coupling across models | Per-model seed derivation specified |
| Coupling to Task 2/3 | Task 4 autonomous; runner consumes via `--reference-predictions` as a later PR |

## Commit / PR

Commit subject: `feat(baselines): add constrained forecast null models`

PR draft to `main`; body must include:

- "No real-data run, synthetic tests only"
- "Pre-Gate-C safe"
- "4 null models: split_prevalence_prior (BSS climatology),
  rate_matched_random, patient_prior (with fallback marker),
  cycle_preserving_random (hour-of-day)"
- "Designed for direct consumption by the leaderboard runner via
  `--reference-predictions`"

## Anti-patterns from prior reviews — DO NOT reproduce

Drawn from the Claude Code honest review of Tasks 1-3:

- **No silent failure.** No `try/except` that swallows an exception and
  returns `None`. If a metric or computation fails, raise or `log.warning`
  explicitly. The Task 3 runner's `_metric_or_none` pattern was flagged for
  exactly this reason; do not import or re-use it here.
- **No silent fallback.** Every fallback (population for `patient_prior`)
  must be marked in the output AND countable in the metadata.
- **Tests not only structural.** Include the behavior-sanity tests
  (h) / (i) / (j) / (k) / (l) that validate what the model does, not just
  that it does not crash.
- **No external citation in this PR** (engineering only). If a paper is
  referenced in the doc, verify the canonical URL/DOI (no personal
  websites) — phantom-citation lesson from PR #2 review.

---

When this work order is followed, the resulting PR should review and merge
cleanly without integrity rework, and the produced predictions should be
directly usable as `--reference-predictions` for the leaderboard runner in
a later PR.
