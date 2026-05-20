# Step 1 - SOTA Leaderboard And Contribution Gap Plan

Date: 2026-05-20
Branch: `codex/sota-leaderboard-step1` retargeted onto
`origin/feature/epibench-forecast-v0.1@307c55d`
Scope: turn the current project into a reproducible SOTA comparison program.

## Plan

This step does not train a new model. It defines the first research layer that
will let us turn the repository from a course replication into a publishable
benchmark contribution.

1. Establish the current baseline position from repository evidence.
2. Map the relevant SOTA families for wearable seizure detection and seizure
   forecasting.
3. Identify where the current work is weak, non-comparable, or under-claimed.
4. Convert those gaps into an experiment backlog with acceptance criteria.
5. Stop after a documented commit so Claude can validate and merge before the
   next implementation step.

## Plan Validation

The plan is valid if the branch contains only auditable research artifacts and
no risky pipeline changes:

- It is created from `origin/feature/epibench-forecast-v0.1`, because that is
  the active branch containing the latest forecasting work.
- It records source URLs and the exact claims imported from each source.
- It separates detection, forecasting, and edge-deployment claims.
- It treats the MSG HR forecasting result as the active feature-branch baseline,
  not as a result already merged into `main`.
- It ends with a concrete experiment queue that can be executed one item at a
  time after Claude validation.

## Attack

The literature scan focused on public, reproducible, and clinically relevant
references:

- SeizeIT2 dataset and official benchmark framing.
- ECG and EEG wearable seizure detection on SeizeIT2.
- Long-term wearable seizure forecasting with Empatica/smartwatch signals.
- Forecasting reviews that define current methodological expectations.
- SzCORE as the strongest nearby benchmark standard for seizure-detection
  evaluation.

The important distinction is:

- `main` currently supports an edge seizure-detection story on SeizeIT2 LOSO.
- `feature/epibench-forecast-v0.1` adds a leakage-aware forecasting benchmark
  direction with an MSG HR patient-wise result.
- A major contribution requires unifying those into one evaluated benchmark:
  detection, forecasting, calibration, false alarms, leakage, and edge cost.

## SOTA Map

| Family | What It Represents | Relevant Evidence | How We Compare |
| --- | --- | --- | --- |
| SeizeIT2 official wearable benchmark | Public multimodal wearable seizure-detection dataset with suggested split and baseline methods | 125 patients, 883 focal seizures, about 11,600 hours, BIDS/OpenNeuro, SVM and ChronoNet baselines | Our `main` uses SeizeIT2 but only a 6-patient FBTC LOSO edge subset, so it is not yet comparable to full SeizeIT2 baselines |
| SeizeIT2 ECG anomaly/detection benchmark | ECG-only detection on the full open SeizeIT2 setting, including Matrix Profile, MADRID, and TimeVQVAE-AD | Shows sensitivity/FAR trade-off remains the central issue for ECG wearable detection | Our current edge pipeline should add ECG-specific reproduction or clearly state it is a tiny edge subset |
| Long-term Empatica LSTM forecasting | Ambulatory wearable forecasting with ACC/BVP/EDA/TEMP/HR and iEEG labels | Uses one-hour preictal epochs with a 15-minute setback and lead seizures separated by at least 4 hours | Our MSG HR result is simpler and more auditable, but currently lacks ACC/BVP/EDA and comparable preictal epoch protocol |
| Wearable cycle-based forecasting | Patient-specific forecasting using HR, sleep, steps, circadian and multiday cycles | Hourly models above chance in 11/11 retrospective subjects; held-out hourly AUC mean 0.68 in 8 subjects | Our cycle baseline is only hour-of-day; we need circadian and multiday HR-cycle features |
| Forecasting reviews/meta-analysis | Field-level benchmark expectations | Reviews emphasize probabilistic forecasts, AUC/Brier/BSS, null models, and patient-specific evaluation | Our reports include Brier/ECE but need Brier Skill Score and constrained chance/null forecasts |
| SzCORE-style benchmark standardization | Evaluation framework for clinical seizure detection | Recommends standardized data, validation, sample/event scoring, sensitivity, precision, F1, false alarms/day, and avoiding accuracy as a clinical headline | We should adapt the spirit to wearable forecasting: event-level metrics, FAR/day, TIW, calibration, and public runner scripts |

## Current Baseline Position

### Baseline A - `main`

`main` documents a SeizeIT2 edge-detection replication:

- Dataset/task: SeizeIT2 subset, focal-to-bilateral tonic-clonic seizure window
  detection.
- Validation: Leave-One-Subject-Out on 6 patients.
- Key finding: the reference Random Forest collapses in LOSO; MLP TinyML is
  much smaller and slightly better, but still far from clinical sensitivity.
- Reported table: MLP TinyML pooled recall `8.7%`, RF LOSO pooled recall `3.3%`.
- Contribution type: critical replication and edge feasibility.

This is publishable only as a negative/replication/edge critique unless expanded
to full public benchmarks.

### Baseline B - Active Forecasting Artifact (pre-Gate-C exploratory)

The active forecasting branch `feature/epibench-forecast-v0.1` records
exploratory pre-freeze MSG patient-wise forecasting numbers, introduced by the
result report and carried forward to the current target head. **Per
`PLAYBOOK.md` section 10 rule 1, these numbers cannot be cited as a benchmark
result until Gate C (frozen splits + Zenodo DOI) passes.**

- Dataset/task: MSG HR Empatica features, SPH 60 minutes / SOP 1440 minutes.
- Split: patient-wise test.
- Model: HR tabular MLP.
- Pre-freeze exploratory result: `27/31` coverable events, sensitivity
  `0.871`, FAR `2.006/day`, TIW `0.1253`.
- Boundary: sampled human label attestation; not a final clinical efficacy
  claim; SeizeIT2 forecasting excluded until duplicate recording-range issues
  are resolved. **Not citable until Gate C closes** (see
  `reports/msg_patientwise_clinical_baseline_2026-05-20.md`).

This is a stronger research direction, but it must be reproduced under a
standard leaderboard schema, frozen at Gate C, and compared against SOTA
baselines before being claimed as a major contribution.

## Gaps To Close

1. Detection and forecasting are mixed in narrative, but they are different
   clinical tasks.
2. `main` SeizeIT2 is a small edge subset, not a full SeizeIT2 benchmark.
3. MSG forecasting result is active on the feature branch but not yet represented
   in a unified leaderboard.
4. No constrained null model or Brier Skill Score is used to prove
   better-than-chance forecasting.
5. Cycle modeling is currently weak: hour-of-day only, no multiday HR cycles.
6. No SOTA reproduction runner exists for Matrix Profile, MADRID,
   TimeVQVAE-AD, ChronoNet, or LSTM forecasting.
7. No single leaderboard schema tracks dataset, split, horizon, denominator,
   FAR/day, TIW, calibration, edge cost, and leakage status.
8. Accuracy is still visible in the `main` story, but clinical evaluation should
   prioritize sensitivity, false alarms, precision/F1, TIW, and calibration.

## Result

The contribution should be framed as:

> A leakage-aware, clinically audited, edge-aware wearable seizure benchmark that
> starts from a negative SeizeIT2 edge replication and grows into a reproducible
> forecasting leaderboard with patient-wise metrics, false-alarm accounting,
> calibration, null models, and edge deployment cost.

This is more publishable than a single model result because benchmark
standardization is a visible gap in the field.

## Experiment Backlog

The next commits should execute the backlog in `2026-05-20_step1_experiment_backlog.csv`.

Priority order:

1. Preserve the MSG forecasting baseline as the feature-branch anchor and build
   the first leaderboard row around its evidence files and commands. (The
   current baseline numbers remain pre-Gate-C exploratory until Gate C — frozen
   splits + Zenodo DOI — closes; the leaderboard row becomes citable then.)
2. Add a leaderboard schema and CLI that accepts any prediction table and emits
   event-level metrics, calibration, Brier Skill Score, FAR/day, TIW, and edge
   cost metadata.
3. Add constrained null models: rate-matched random, cycle-preserving random,
   patient-specific seizure-rate prior.
4. Add multiday HR-cycle features and compare them against the current HR MLP.
5. Reproduce at least one external SOTA family on our standard runner:
   Matrix Profile/MADRID for ECG detection or LSTM/cycle forecasting for
   wearable forecast.

## Audit Of Result

What is strong:

- The path to publication is now explicit.
- The SOTA comparison avoids false equivalence between detection and forecasting.
- The next step is implementable without changing the entire repository.

What remains weak:

- The SOTA table is a research map, not measured reproduction yet.
- Some papers use private datasets, so not every reported number can be fairly
  reproduced.
- `main` and the forecasting branch still need consolidation before the paper
  narrative is coherent.

## Conclusion

Step 1 produces the research scaffold for a major contribution. The next
mergeable engineering step should be a leaderboard schema and evaluation runner
on top of `feature/epibench-forecast-v0.1`, then a later integration decision
can move the consolidated branch into `main`.
