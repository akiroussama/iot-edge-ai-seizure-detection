# Claude to Codex handoff: Phase R reconciliation landed

**Date:** 2026-05-15
**Author:** Claude Code (Opus 4.7)
**Branch:** `feature/epibench-forecast-v0.1`

## Action required before your next work

The canonical tip of `feature/epibench-forecast-v0.1` moved:

```
a940098  (your last pushed tip)   ->   141fc0c  (current)
```

`git fetch`, then base any new work on **`141fc0c`**. Rebase any
unpushed local commits onto `origin/feature/epibench-forecast-v0.1`;
if you have no unpushed work, reset to it. Do **not** branch or rebase
from `a940098` — that state is superseded and rebuilding on it will
collide again.

## What happened

On 2026-05-15 Claude and Codex independently remediated the same
Phase R audit (findings C1-C4 / H1-H5) on the same branch. Codex
pushed first (Phase R2/R3, tip `a940098`); Claude's parallel audit
work could not push (non-fast-forward) and overlapped Codex's
substantially. Where the two overlapped, Claude's version was a
near-duplicate of yours — that part was dropped, not committed.

## Resolution (Strategy A)

Your pushed branch was kept **canonical**. A reconcile branch was cut
from `a940098`, only Claude's *unique* (non-duplicated) audit work was
re-applied as 7 focused commits, and the result was fast-forwarded
back (no `--force`). Your Phase R2/R3 work — P0 over-exclusion fix,
H1 cluster metrics, onset-only postictal anchor, MSG parser duplicate
policy, label-audit scaffolding, regenerated reports — is fully
preserved and untouched.

## The 7 commits on top of `a940098`

| SHA | Commit | Adds |
|-----|--------|------|
| `a20f61a` | `chore(gitignore)` | ignore `.pytest_tmp` basetemp dir |
| `caf2da2` | `feat(baselines)` | C3 — `reference_scope="population"` keeps held-out patients scorable; `--reference-scope` on `run_rule_baseline.py`; gap-1 `acc_energy_score` mutation coverage |
| `74edfbc` | `fix(labeling)` | C2 — `label_forecast_windows` defaults `require_recording_end=True`; `right_censoring_applied` stamp on labels |
| `85f2a78` | `feat(leakage)` | H2/H3 — `check_fit_scope_metadata` three-state status (`not_applicable` / `unverified_or_failed` / `verified`); temporal verdict `UNRELIABLE` on duplicate recording ranges |
| `2a4786e` | `feat(report)` | C4 — baseline-table `sensitivity` rendered with inline `(n/N events)` denominator; bias-ack guard widened beyond one filter string |
| `cf99ae6` | `docs(playbook)` | revision-2 `PLAYBOOK.md` + `CLAUDE_PHASE_R_AUDIT_2026-05-15.md` |
| `141fc0c` | `fix(msg_loader)` | cross-platform path bug (see below) |

Each commit body carries a `Verified-By:` pytest command.

## Heads-up: `require_recording_end` default flipped

`74edfbc` flips `label_forecast_windows(require_recording_end=...)`
from `False` to `True`. Real-data callers with no `recording_end`
column now **fail loudly** instead of silently treating unobserved
forecast horizons as true negatives. Synthetic or legacy callers must
now pass `require_recording_end=False` explicitly. If any of your
scripts call `label_forecast_windows` on windows without
`recording_end`, update them.

## Pre-existing bug fixed (`141fc0c`)

`msg_loader.py` `inspect_msg_raw_layout` emitted `seizure_txt_files`
with `str(Path.relative_to())` — OS-native separators. On Windows that
produced `\`, failing `test_parse_msg_zenodo_seizure_times_only_txt`.
Fixed with `.as_posix()`. The failure pre-dated the reconciliation and
is invisible on POSIX, which is likely why it shipped. The full suite
is now green on Windows and POSIX: **116 passed / 0 failed**.

## Coordination going forward

Root cause: both agents ran as *implementers* on the same task. Per
`PLAYBOOK.md` section 7 the split is Codex = implement, Claude =
review. In either role: `git fetch` and inspect the other agent's
branch state **before** starting substantial work, and lock scope
against its commits up front — not at push time.
