# Claude Code re-review — Phase R remediation closure

Date: 2026-05-17
Reviewer role: strict biomedical ML methods reviewer + senior software architect
Branch: `feature/epibench-forecast-v0.1`
Re-reviews: `docs/CLAUDE_PHASE_R_AUDIT_2026-05-15.md` against the
post-reconciliation source.
Verification basis: `uv run --extra dev --extra torch python -m pytest -q`
(all tests pass, 0 failures — 118 tests incl. the 2 C1-bypass tests added
during this re-review), `uv run ruff check` (clean), direct source inspection,
the reconciliation commits `a20f61a`..`141fc0c`, and the `fix(sweep)` commit
made during this re-review.

## Context

Between the 2026-05-15 audit and this re-review, Claude and Codex independently
remediated the Phase R findings and collided on the shared branch. The collision
was reconciled (Strategy A — see `docs/CLAUDE_TO_CODEX_RECONCILIATION_2026-05-15.md`):
Codex's pushed Phase R2/R3 work kept as the canonical base, Claude's unique
remediation re-applied as 7 focused commits. This re-review verifies the
**combined** result against the audit's section-5 M2 closure checklist, and
fixed one residual it found (C1 Gap 2 — see below).

## M2 closure checklist — verified status

| # | Item (audit §5) | Status | Verified by |
|---|---|---|---|
| 1 | `sweep.py` requires explicit calibration split, raises on test/multi-split | CLOSED | guard `scope_predictions_for_threshold_sweep` in `sweep.py` raises on no-split-column / no-filter / `split=test` / non-`split=` filter; `tests/test_metric_sweep.py` |
| 2 | `sweep_thresholds.py` accepts only a `split=` sweep filter | CLOSED | CLI delegates to the library guard; `tests/test_threshold_sweep_cli.py` covers the non-`split=` refusal |
| 3 | C2 over-exclusion fixed — censored confirmed-positives not excluded | CLOSED | `sph_sop.py:133-134` (current source): `is_excluded = is_postictal \| (is_right_censored & ~forecast_label) \| ...` |
| 4 | four MSG reports regenerated after the C2 fix | CLOSED | Codex Phase R2 post-P0-fix; legacy reports superseded (`a940098`); reconciliation did not alter labeling math |
| 5 | `require_recording_end` library default is `True` | CLOSED | `sph_sop.py` default flipped; commit `74edfbc` |
| 6 | rule baselines raise on a missing feature column | CLOSED | `simple_rules.py` raises (all 3 score fns); `tests/test_features.py` |
| 7 | population-reference path for patient-wise rule baselines | CLOSED | `reference_scope="population"`; commit `caf2da2`; `tests/test_features.py` |
| 8 | `make_splits.py` refuses/quarantines duplicate-range patients | CLOSED | `temporal_split_per_patient` raises `ValueError` on duplicate ranges by default (`temporal_split.py:47-53`), before `write_table` |
| 9 | patient 2002 duplicate ranges investigated | CLOSED | `msg_loader.resolve_msg_duplicate_recording_ranges` — diagnosed as `(N)`-suffix copy files, resolved by `drop_exact` policy |
| 10 | H1 cluster policy decided | **OPEN — decision** | `PHASE_R_DECISION_BRIEFS_2026-05-17.md` brief 2 |
| 11 | postictal anchor policy for onset-only MSG decided | **OPEN — decision** | brief 4 |
| 12 | tests added (sweep bypass, censored-positive, missing-column, held-out baseline, duplicate-range refusal) | CLOSED | suite green incl. all 5 named mutation tests; the non-`split=` sweep-bypass test added at library + CLI level during this re-review |
| 13 | manual label audit (Phase B) complete | **OPEN — Oussama** | review sheets generated 2026-05-17, not yet filled |

Other Gate A conditions: `pytest -q` — all pass, 0 failures; `ruff check` — clean.

## C1 Gap 2 — found and fixed during this re-review

At the start of this re-review the audit's C1 Gap 2 was still open. The
split-scope guard `scope_predictions_for_threshold_sweep` had been correctly
pushed into `src/metrics/sweep.py` and raised on a missing `split` column, a
missing `sweep_filter`, and `split=test` — but it keyed off `_split_value`,
which silently returns `None` for any non-`split=` filter. So
`--sweep-filter score_fit_split=train` (a constant column `run_rule_baseline.py`
writes into every prediction table) ran the sweep across train+val+test instead
of refusing it. It was correctly stamped `publishable_threshold_tuning=False`,
so the audit's worst harm — a leaky sweep marked *publishable* — was already
gone, but the audit's prescribed `raise` was not implemented.

Fixed in this re-review's `fix(sweep)` commit: `scope_predictions_for_threshold_sweep`
now raises when the sweep-filter column is not `split`. Bypass tests added at
both library (`test_metric_sweep.py`) and CLI (`test_threshold_sweep_cli.py`)
level. The audit's C1 Gap 2 prescription is now fully implemented.

## Verdict

The Phase R **code punch list is fully closed**: 10 of the 13 M2 items CLOSED,
3 OPEN (2 policy decisions + the manual audit). The audit's 2026-05-15
meta-finding — "safe CLIs, unsafe library" — no longer holds: the library
defaults are safe (`require_recording_end=True`, missing-column raises, the
sweep guard lives in the library and now also rejects non-`split=` filters) and
the C2 over-exclusion P0 defect is fixed.

Gate A is **not** yet passed. Remaining, none of them code:

- the **four section-4 policy decisions** (`PHASE_R_DECISION_BRIEFS_2026-05-17.md`);
- the **manual label audit** (Phase B — Oussama; review sheets ready);
- **advisor sign-off** on the four policy decisions.

No A100, no clinical claim, no headline MSG number until Gate A and Gate B close.
