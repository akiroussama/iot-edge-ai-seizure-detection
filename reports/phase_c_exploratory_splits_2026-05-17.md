# Phase C — exploratory split run (provisional, pre-audit)

Date: 2026-05-17

**Status: EXPLORATORY.** These splits were generated on label tables that have
NOT passed the Phase B manual label audit. They are re-runnable and carry no
scientific commitment. The Phase C freeze (`git tag`), the Zenodo
pre-registration, and all Phase D baselines remain gated behind the manual
audit and a formal split-policy sign-off in `PLAYBOOK.md` §5. This note is a
record of exploratory work, not a policy decision.

## What was run

`scripts/make_splits.py`, two strategies x two datasets, default fractions
train 0.70 / val 0.10 / test 0.20 (repo defaults — **provisional**; the real
Phase C policy may change them, regenerating the splits).

| dataset | strategy | result |
|---|---|---|
| MSG | temporal (recording-unit, elapsed-time) | OK — train 33853 / val 5415 / test 10309 |
| MSG | patient-wise | OK — train 29778 / val 4538 / test 15261 |
| SeizeIT2 | temporal (recording-unit, elapsed-time) | **REFUSED** — see finding |
| SeizeIT2 | patient-wise | OK — train 945366 / val 136064 / test 303773 |

## Leakage audits (the `.txt` outputs are gitignored — key lines)

- **MSG temporal-recording**: Patient overlap True (by design for a temporal
  split), Recording overlap False, Duplicate recording ranges False, Temporal
  ordering/overlap leakage False. CLEAN.
- **MSG patient-wise**: Patient-wise leakage False, Duplicate recording ranges
  False. CLEAN.
- **SeizeIT2 patient-wise**: Patient-wise leakage False; Duplicate recording
  time ranges **True**. For a patient-wise split this is informational, not
  leakage (every recording of a patient lands in one split) — but it is the
  cause of the temporal refusal below.

## Finding — SeizeIT2 cannot take a prospective-temporal split as-is

`temporal_split_per_patient` refused the SeizeIT2 temporal split (the H3
duplicate-range guard, working as designed). Cause: the OpenNeuro `ds005873`
release is de-identified with **every recording's timestamps anchored to a
fixed epoch (`2000-01-01 00:00:00`)**. Recordings of equal duration therefore
carry identical `[start, end]` ranges (sub-009, sub-022, sub-066, sub-069, …),
and cross-recording temporal order is not recoverable from the timestamps.

Implication: with the current tooling SeizeIT2 supports a **patient-wise**
split (cross-patient generalization) but **not** a prospective-temporal split.
MSG (real Unix timestamps) supports both.

Open methods question for the real Phase C + advisor: the BIDS run index
(`run-02`, `run-04`, …) does encode session order, so a run-index-ordered
temporal split is a candidate. Whether that is a valid prospective proxy is a
methods decision, not a code fix. Until decided, the SeizeIT2 arm of the
benchmark is cross-patient generalization only.

## Gate status — unchanged

The manual label audit is not done. Phase D baselines, the `git tag` freeze
and the Zenodo pre-registration remain blocked. These exploratory splits do
not advance the gate; they are a re-runnable input for the real Phase C.
