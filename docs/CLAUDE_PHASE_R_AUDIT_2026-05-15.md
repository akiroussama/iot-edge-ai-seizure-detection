# Claude Code Audit — Phase R Remediation

Date: 2026-05-15
Reviewer role: strict biomedical ML methods reviewer + senior software architect
Branch: `feature/epibench-forecast-v0.1`
Audited: Phase R commits `df64c9b` → `f45c3aa`, handoff `73d07dc`
Handoff reviewed: `docs/CODEX_TO_CLAUDE_PHASE_R_REVIEW_2026-05-15.md`
Prior review: `docs/CLAUDE_REVIEW_2026-05-15.md` (the C1–C4 / H1–H5 findings)
Mode: read-only audit. One finding (C1 bypass) was verified by running the CLI.

## Verdict

Phase R closes the **advertised surface** of the findings but not their
**substance**. The CLI entry points are now safe-by-default; the library
functions underneath them are not.

Tally of the 9 findings (4 Critical, 5 High):

| Finding | Phase R status |
|---|---|
| C1 threshold tuning on test | Partially closed — CLI guarded, **library untouched, confirmed bypass** |
| C2 right-censoring | Partially closed — **new active defect introduced** (over-exclusion) |
| C3 silent rule degeneracy | Partially closed — empty-reference path closed, **two gaps remain** |
| C4 MSG denominator | Substantially closed for visibility — policy still open |
| H1 seizure clusters | Deferred by design (policy decision) |
| H2 leakage-audit false assurance | Closed (one residual limitation) |
| H3 reset/duplicate timestamps | Partially closed — detection added, **not enforced** |
| H4 count-based temporal split | Closed for count-vs-time; **shares H3 corrupted-input gap** |
| H5 imputed MSG durations | Closed |

**M2 is not closeable.** The remaining work is real but small: every open item
is a well-scoped change of a few lines plus a test — none is an architectural
rewrite. The closure checklist is in section 9.

## 0. Meta-finding — read this first

> Phase R hardened the CLIs and left the library defaults unsafe. This is the
> exact "safety is opt-in" pattern the original review flagged, reproduced one
> layer up.

Concretely:

- `src/metrics/sweep.py` — **unchanged**. `threshold_sweep_table`,
  `sensitivity_at_fixed_far`, `select_threshold_under_constraints` are still
  split-agnostic. Only the CLI `scripts/sweep_thresholds.py` was guarded.
- `src/labeling/sph_sop.py` — `label_forecast_windows(..., require_recording_end=False)`.
  The unsafe value is the default; only the CLI passes `True`.
- `src/baselines/simple_rules.py` — `ecg_tachycardia_score` and siblings still
  `return pd.Series(0.0, ...)` when the feature column is absent.

When Phase G adds deep-model code, it will `import` these library functions
directly — not the CLIs — and silently re-create C1 and C2. Every Phase R fix
must be pushed **down into the library function**, with the CLI inheriting the
safe behaviour rather than being the only place it exists.

## 1. BLOCKER — Phase R MSG reports are computed under an active bug

C2 introduced an over-exclusion defect (detailed in section 3). Because of it,
**every regenerated MSG report currently on disk has metrics computed on a
corrupted valid-window set**:

```text
reports/msg_full_real_check/dataset_report.md
reports/msg_full_real_check_coverable/dataset_report.md
reports/msg_cycle_hour_recording_test_check/dataset_report.md
reports/msg_hr_tachycardia_recording_splitaware_check/dataset_report.md
```

Until C2 is corrected and these are regenerated, **no Phase R MSG number may be
cited — not even as an "audit signal".** Do not ship the current reports.

## 2. Scientific finding — MSG SPH60/SOP1440 is not a viable task as configured

This is the most important *outcome* of Phase R and it is not a code defect.

After right-censoring, MSG SPH60/SOP1440 collapses to:

```text
total windows:        49,596
valid windows:         4,854   (was ~47,713 pre-censoring)
positive windows:        260   (was 3,325 pre-censoring)
coverable matched events: 78
test-split coverable:     13
```

A 24-hour SOP against Empatica segments that are mostly far shorter than 24 h
means almost every window's horizon runs off the end of its recording. The
reported HR-tachycardia test sensitivity of 0.846 is **11/13 events**. Its
Wilson 95% CI is approximately **[0.58, 0.96]** — a 38-point-wide interval. A
number on n=13 is a methodology illustration, not a result.

Action (decision, Oussama + advisor): either
(a) redesign the MSG horizon — a shorter SOP, or a coverage-bounded horizon that
   only labels windows whose full horizon fits inside the recording; or
(b) accept explicitly that MSG long-horizon forecasting is a *coverage-limited
   demonstration*, not a benchmark results table, and say so in the paper.

This is exactly the kind of honest negative finding a benchmark paper should
surface — but it must be elevated, not buried in a report footnote.

## 3. Per-finding audit

### C1 — Threshold tuning on test — PARTIALLY CLOSED, confirmed bypass

What Codex did: `scripts/sweep_thresholds.py` now refuses a sweep when the
table has a `split` column and no `--sweep-filter`, and refuses
`--sweep-filter split=test` unless `--allow-test-sweep`.

Gap 1 — the library is untouched. `src/metrics/sweep.py` still exposes
`threshold_sweep_table` / `sensitivity_at_fixed_far` /
`select_threshold_under_constraints` with no split concept. Any non-CLI caller
(Phase G model code) bypasses every guard. The original review's C1 fix —
"make the sweep *functions* require `fit_split`/`eval_split` and raise when they
are equal" — was not done.

Gap 2 — confirmed CLI bypass. `_validate_sweep_scope` only checks that
`--sweep-filter` is *non-None*; `_split_value` returns `None` for any filter
whose column is not literally `split`. So a non-`split=` filter passes the
guard. Verified by running the CLI:

```text
$ python scripts/sweep_thresholds.py --predictions <table-with-split-col> \
    --events ... --output ... --sweep-filter score_fit_split=train --steps 3
returncode: 0                         # CLI did NOT refuse
publishable_threshold_tuning: [True]  # leaky sweep marked publishable
```

`score_fit_split` is a constant column that `run_rule_baseline.py` writes into
every prediction table, so `--sweep-filter score_fit_split=train` keeps **all
rows (train+val+test)**, sweeps the full table, and is stamped publishable.

Priority: **P1**. Fix both: (a) in `sweep.py`, add a required
`calibration_split` argument; the function filters to it and raises if it is
`"test"` or if the filtered frame still contains >1 split; (b) in
`sweep_thresholds.py`, require `--sweep-filter` to be a `split=` filter — raise
if `_filter_column(sweep_filter) != "split"`; set `publishable_threshold_tuning`
True only when the filter is `split=val` or `split=train`.
Test to add: a non-`split=` sweep filter on a multi-split table must fail.

### C2 — Right-censoring — PARTIALLY CLOSED, NEW DEFECT — P0

What Codex did: `generate_fixed_windows` carries `recording_end` into windows;
`label_forecast_windows` computes `is_right_censored` when
`window_end + SPH + SOP > recording_end` and folds it into `is_excluded`;
`label_windows.py` requires `recording_end` by default.

The direction is correct. But:

**DEFECT (active, corrupting numbers now).** `src/labeling/sph_sop.py:128`:

```python
out["is_excluded"] = out["is_postictal"] | out["is_right_censored"] | (out["is_ictal"] if ictal_exclusion else False)
```

A window can be `is_right_censored=True` **and** `forecast_label=True`
simultaneously: a seizure onset falls inside `[t+SPH, t+SPH+SOP)` and is before
`recording_end` (a genuinely observed positive), while the horizon's unobserved
*tail* still runs past `recording_end`. Right-censoring should neutralise only
windows that are **negative and unobservable** — a window with a confirmed
observed positive is informative regardless of its horizon tail. The current
blanket OR **excludes confirmed true positives**, eats real signal, and
inflates the MSG positive-window collapse.

One-line fix:

```python
out["is_excluded"] = (
    out["is_postictal"]
    | (out["is_right_censored"] & ~out["forecast_label"])
    | (out["is_ictal"] if ictal_exclusion else False)
)
```

Diagnostic for Codex — how many positives are currently eaten:

```python
(labels["is_right_censored"] & labels["forecast_label"]).sum()
```

Run it before and after the fix; the delta is the number of true positives
Phase R is currently discarding on MSG.

Gap — library default. `require_recording_end` defaults to `False`; only the
CLI is safe. Flip the default to `True` (meta-finding section 0); keep an
explicit opt-out for synthetic/legacy callers.

Gap — `--allow-missing-recording-end` produces labels indistinguishable from
properly censored labels (`is_right_censored` all-False either way). Stamp the
output with a `right_censoring_applied` boolean column so a downstream report
cannot mistake un-censored labels for censored ones.

Priority: **P0** for the over-exclusion (corrupts current numbers), **P2** for
the two gaps.

### C3 — Silent rule degeneracy — PARTIALLY CLOSED — P1

What Codex did: `robust_zscore` and `normalize_score` raise on an empty
reference; `run_rule_baseline.py` raises when the threshold split has no valid
evidence rows. The empty-reference silent path is genuinely closed.

Gap 1 — missing-column silent path remains. `ecg_tachycardia_score`,
`acc_energy_score`, `generic_zscore_anomaly` still
`return pd.Series(0.0, index=...)` when the feature column is absent
(`simple_rules.py:34-35, 49-50, 64-65`). A features table without `hr_mean`
yields all-zero scores with no error — the same silent degeneracy class C3 was
about. Fix: raise (consistent with the rest of Phase R) when the requested
feature column is absent.

Gap 2 — functionality. Raising on an empty reference means the HR/ACC rule
baselines **cannot run on a patient-wise split at all**: every held-out test
patient has zero train rows → raise. Phase R converted "silent wrong number"
into "cannot run" — correct as a stopgap, but the benchmark now has *no rule
baseline for patient-wise evaluation*, which Paper 1 needs. Fix: add a
`reference_scope` of `patient` or `population`; the `population` mode pools all
train-patient rows into one robust reference and applies it to held-out
patients. Expose `--reference-scope` on `run_rule_baseline.py` and record the
chosen scope in the prediction metadata.

Priority: **P1** (Gap 2 blocks Phase D rule baselines; Gap 1 is a quick raise).

### C4 — MSG denominator — SUBSTANTIALLY CLOSED, policy open — P2

What Codex did: `make_dataset_report.py` requires `--acknowledge-event-filter-bias`
for `recording_match_status=matched`; adds an `Event Denominator` table
(`events_source_total`, `events_after_filter`, `events_used_for_metrics`,
filters, coverage flag, warning) and an `Event Annotation` table for imputed
durations. This genuinely addresses "report the denominator".

Gap 1 — the headline `sensitivity` in the `Baseline` table is still a bare
number; the denominator lives in a separate table. A reader copies `0.85` and
loses the `n=13`. Fix: render sensitivity inline as `0.846 (11/13 events)` in
the baseline table itself.

Gap 2 — `_requires_bias_acknowledgement` is an exact-string match on the single
filter `recording_match_status=matched`. Any other biased event filter (by
patient, centre, seizure type) bypasses the acknowledgement. Fix: maintain a set
of known-biased filter columns, or require acknowledgement for any
`--event-filter` that is not on an explicit allowlist.

Open (policy) — the report suite still permits different denominator policies
per report; Phase R makes the policy *visible* per report but does not
*standardize* it. See section 9 and question 7.

Priority: **P2** for the gaps; the policy is a decision item.

### H1 — Seizure clusters — DEFERRED BY DESIGN

Codex exposed `cluster_policy = seizure_level_metrics_clusters_not_collapsed`
as an explicit placeholder and surfaced patient 1942's max cluster size of 20.
No code defect. This is a decision — see question 8 for my recommendation.

### H2 — Leakage-audit false assurance — CLOSED

`check_fit_scope_metadata` makes the audit report `UNVERIFIED_OR_FAILED` when
fit metadata is absent and flags `test`-scope metadata. This closes the false
"clean" line.

Residual (minor, P2) — the check trusts a self-reported string: `score_fit_split="train"`
is whatever the script wrote, not a verification of the actual fit. And a plain
label/split table with no model fit now always shows `UNVERIFIED_OR_FAILED`,
conflating "N/A — no model fit yet" with "FAIL — metadata missing". Consider a
third state `NOT_APPLICABLE` for tables that legitimately carry no predictions.

### H3 — Reset/duplicate timestamps — PARTIALLY CLOSED — P1

What Codex did: `check_duplicate_recording_time_ranges` detects repeated
`(patient, start, end)` ranges across recording IDs; it correctly catches
patient 2002.

Gap 1 — detection without enforcement. `make_splits.py` writes the split file
(`write_table`, line 72) **before** running `leakage_audit` (line 76). When the
audit flags patient 2002, the corrupted split is already on disk and nothing
stops a consumer from using it. Fix: run `check_duplicate_recording_time_ranges`
*before* splitting; if it fires, either raise, or quarantine the affected
patients (`split="quarantine"`) and refuse to assign them train/val/test.

Gap 2 — `check_temporal_leakage` is not connected to the duplicate-range
result. It still independently prints `Temporal ordering/overlap leakage: False`
next to the duplicate warning, which can still mislead. Fix: when duplicate
ranges are detected for a patient, that patient's temporal-leakage verdict must
be `UNRELIABLE`, not `False`.

Gap 3 — only exact-equal ranges are caught; near-duplicate reset clocks are not.
Acceptable for now given patient 2002 is an exact duplicate, but note it.

Priority: **P1** — a corrupted split must not be silently produced and frozen.

### H4 — Count-based temporal split — CLOSED for count-vs-time — P2 (shared gap)

`split_basis="elapsed_time"` is the new default; `_elapsed_time_cuts` cuts on
the observed time span. The count-vs-time issue is fixed.

Shared gap with H3 — `_elapsed_time_cuts` uses `window_start.min()` /
`window_end.max()`. For a patient with reset/duplicate timestamps (2002) the
span mixes overlapping clocks and the cut is meaningless. The H4 fix is correct
but still runs on corrupted input for H3-affected patients. The H3 enforcement
fix (quarantine before splitting) also closes this.

### H5 — Imputed MSG durations — CLOSED

The `Event Annotation` table exposes `seizure_end_imputed_fraction: 1.0` and
`imputed_duration_seconds: 60`. Imputation is no longer presentable as measured
duration. The postictal-anchor question is a policy decision — see question 11.

## 4. Prioritized action list for Codex

### P0 — corrupts numbers, do first
1. **C2 over-exclusion.** `src/labeling/sph_sop.py:128` — change
   `| out["is_right_censored"] |` to `| (out["is_right_censored"] & ~out["forecast_label"]) |`.
   Run the diagnostic `(labels.is_right_censored & labels.forecast_label).sum()`
   before/after; record the recovered-positive count in the commit body.
   Regenerate all four MSG reports. Add a labeling test: a window that is both
   right-censored and forecast-positive stays non-excluded.

### P1 — reopens a critical finding / persists a corrupted artefact
2. **C1 library.** Add a required `calibration_split` arg to the `sweep.py`
   functions; filter internally; raise on `test` or on a residual multi-split
   frame.
3. **C1 CLI bypass.** In `sweep_thresholds.py`, require `--sweep-filter` to be a
   `split=` filter; gate `publishable_threshold_tuning` on that. Add the
   non-`split=` bypass test.
4. **C3 held-out baseline.** Add `reference_scope=patient|population` to the rule
   baselines and `--reference-scope` to `run_rule_baseline.py`; `population`
   pools train-patient rows. Without this there is no patient-wise rule baseline.
5. **C3 missing column.** Make `ecg_tachycardia_score` / `acc_energy_score` /
   `generic_zscore_anomaly` raise on an absent feature column.
6. **H3 enforcement.** `make_splits.py` must run
   `check_duplicate_recording_time_ranges` before writing; raise or quarantine
   affected patients. Investigate whether patient 2002's duplicate is a parser
   bug or genuine duplicate archives in `src/datasets/msg_loader.py`.

### P2 — robustness and transparency
7. **C2 library default.** Flip `require_recording_end` default to `True`.
8. **C2 stamp.** Add a `right_censoring_applied` column to labeled output.
9. **C4 inline denominator.** Render `sensitivity` as `0.846 (11/13)` in the
   baseline table.
10. **C4 general bias guard.** Require `--acknowledge-event-filter-bias` for any
    non-allowlisted `--event-filter`.
11. **H2 third state.** Distinguish `NOT_APPLICABLE` from `UNVERIFIED_OR_FAILED`.
12. **H3 link.** Mark `check_temporal_leakage` verdict `UNRELIABLE` for patients
    with duplicate recording ranges.

### Policy decisions (Oussama + advisor — not Codex code)
- MSG horizon viability (section 2).
- H1 cluster policy (question 8).
- C4 denominator standardization (question 7).
- Postictal anchor for onset-only datasets (question 11).

## 5. M2 closure checklist

M2 is closed only when every box is ticked:

- [ ] `sweep.py` functions require an explicit calibration split and raise on test/multi-split
- [ ] `sweep_thresholds.py` accepts only a `split=` sweep filter (or explicit `--allow-*` override)
- [ ] C2 over-exclusion fixed; censored confirmed-positives no longer excluded
- [ ] all four MSG reports regenerated after the C2 fix
- [ ] `require_recording_end` library default is `True`
- [ ] rule baselines raise on a missing feature column
- [ ] a population-reference path exists OR "no rule baseline on patient-wise" is a documented decision
- [ ] `make_splits.py` refuses or quarantines patients flagged by `check_duplicate_recording_time_ranges`
- [ ] patient 2002 duplicate ranges investigated (parser bug vs genuine duplicate)
- [ ] H1 cluster policy decided (recommendation in question 8)
- [ ] postictal anchor policy decided for onset-only MSG
- [ ] tests added for: non-`split=` sweep bypass, censored-positive retention, missing-column raise, held-out rule baseline, duplicate-range split refusal
- [ ] manual label audit (Phase B of `PLAYBOOK.md`) complete

## 6. Answers to Codex's 12 questions

1. **Does `sweep_thresholds.py` prevent publishable threshold tuning on test by
   default?** No. `split=test` is refused, but a non-`split=` filter
   (e.g. `score_fit_split=train`) bypasses the guard, sweeps all splits and is
   marked publishable — verified by running the CLI. See C1.
2. **Is `is_right_censored` correctly defined and propagated?** The definition
   is correct; the propagation is not — folding it unconditionally into
   `is_excluded` excludes confirmed positives. See C2 (P0).
3. **Keep `forecast_label=True` on censored rows, or null the labels?** Keep the
   label. A censored window with an observed seizure in its horizon is a
   genuine positive — it must keep `forecast_label=True` *and* must not be
   excluded. Only censored *negatives* are uninformative; null or exclude those.
4. **Is `--allow-missing-recording-end` too permissive?** The flag is
   acceptable, but its output is currently indistinguishable from properly
   censored labels. Stamp the output (`right_censoring_applied=False`) so a
   report cannot silently treat un-censored labels as censored.
5. **Raise vs population fallback for held-out patients?** Raising is the
   correct stopgap (loud beats silent), but it leaves the benchmark with no
   rule baseline on patient-wise splits. Add a pre-registered *population*
   reference fitted on pooled train patients; record per-run which scope was
   used. Do not fall back silently.
6. **Is the matched-subset bias explicit enough?** Adequate for the one
   hardcoded filter; not general. Any other biased event filter bypasses the
   acknowledgement. See C4 Gap 2.
7. **All matched, coverable-matched, or both?** Report **both**, always
   labelled, and make the *coverable-matched* set the primary number because it
   is the only one every baseline can actually forecast. Never present a bare
   sensitivity without its denominator.
8. **Collapse seizure clusters for MSG long-horizon?** Recommended: for
   long-horizon MSG (SOP measured in hours), evaluate **cluster-level** — a
   cluster of 20 seizures within a 240-min gap is, for a 24-h warning, one
   risk episode; counting 20 near-identical events distorts both sensitivity
   and FAR. Keep seizure-level as a secondary table. This needs advisor
   sign-off before it is locked.
9. **Is elapsed-time temporal splitting the right default?** Yes — but only
   after the H3 enforcement fix. On patients with reset/duplicate timestamps the
   elapsed-time cut is computed on a corrupted clock; quarantine those patients
   first.
10. **De-duplicate, exclude, or inspect patient 2002?** Inspect first — the
    duplicate `(1607691981, ...)` ranges with `recording_id ... (1)` suffixes
    look like a parser emitting the same archive twice; confirm in
    `msg_loader.py` before deciding. If it is a parser bug, fix the parser; if
    the archives are genuinely duplicated upstream, exclude pending source
    review. Do not de-duplicate blindly.
11. **Postictal anchored to imputed end or onset-only policy?** For onset-only
    datasets, anchor the postictal exclusion to **onset + a fixed clinical
    offset**, not to the imputed `seizure_end`. The imputed 60-s end is an
    artefact; anchoring an exclusion zone to an artefact propagates the
    artefact. Define the offset explicitly and document it.
12. **What prevents "M2 closed"?** Section 5 — primarily: the C2 over-exclusion
    (P0), the C1 library + bypass (P1), the C3 held-out gap (P1), and the H3
    unenforced split refusal (P1). All are small, scoped fixes; none is a
    rewrite.

## 7. Verdict

Phase R is real progress: H2 and H5 are genuinely closed, the CLIs are much
harder to misuse, and Codex's right-censoring work surfaced a true and
important negative result (section 2). But Phase R turned safe *CLIs* without
making the *library* safe, introduced one active over-exclusion bug, and left
three findings as partially-closed with concrete gaps. M2 cannot be marked
closed. The remaining work is a short, well-scoped punch list — section 4 — and
none of it is architectural.

No A100. No clinical claim. No Phase R MSG number cited until C2 is fixed and
the reports are regenerated.

---

Reviewer note: this audit read the post-Phase-R source on branch
`feature/epibench-forecast-v0.1` and verified the C1 bypass by executing
`scripts/sweep_thresholds.py`. Every other finding cites a file and line range
so it can be checked directly.
