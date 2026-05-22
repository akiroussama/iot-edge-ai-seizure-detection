# EpiTwin-Open - General Status And Roadmap

Date: 2026-05-22
Base: `origin/main@4475545`
Purpose: one human-readable synthesis of the project status, what has been
done since the beginning, and what should be done next to turn the work into a
major publishable contribution.

## 1. Executive Status

The project is now a strong research infrastructure, not yet a certified
clinical result.

The core scientific direction is coherent and defensible:

> wearable seizure forecasting should be evaluated as calibrated,
> patient-specific risk estimation under observability and alarm-burden
> constraints, not as naive preictal/interictal window classification.

The current repository contains a broad, tested scaffold for public wearable
seizure-risk forecasting: dataset parsers, SPH/SOP labels, leakage-aware
splits, clinical metrics, null models, calibration, conformal intervals,
leaderboard schemas, Gate C registry checks, audit tooling, clinical utility,
forecastability analysis, SOTA-comparison scaffolds, robustness reports,
workflow forensics, and paper artifact packaging.

The main limitation is equally clear: real-data benchmark numbers are still
not citable. Gate B, the manual label/timeline audit, is not fully closed, and
Gate C, the frozen/pre-registered benchmark, has not passed. A100/model
training should remain blocked until those gates are green.

## 2. What We Have Built Since The Beginning

### 2.1 Core Benchmark Scaffold

The first layer established the basic EpiTwin-Open package:

- canonical windowing and feature utilities;
- SPH/SOP forecasting labels;
- ictal/postictal exclusion;
- right-censoring for windows whose forecast horizon exceeds recording end;
- event-level metrics, FAR/hour, FAR/day, Time-in-Warning, lead time, Brier,
  ECE;
- patient-wise, temporal, center-wise, and recording-wise split utilities;
- leakage-audit utilities;
- synthetic demo reports;
- CPU-testable EpiTwin-SSL smoke model;
- hazard/risk head, uncertainty head, edge observable student, and symbolic
  constraints.

This made the repo more than a model prototype: it became a benchmark engine
with explicit clinical evaluation semantics.

### 2.2 Public Dataset Integration

The repository now supports real-data pathways for the two main public dataset
families:

- SeizeIT2: BIDS-style event annotations are supported; a local `sub-125`
  import produced real pipeline-check labels. The current state is a scaffold
  and partial/local validation, not a full cohort result.
- My Seizure Gauge: Zenodo `Mayo_*.zip` nested Empatica manifests, patient
  onset text files, recording intervals, event-to-segment matching, duplicate
  segment resolution, and partial-download handling are supported.

Current MSG factual status from `PROJECT_STATUS.md`:

- 2068 wearable segments parsed in the current local cleaned pass;
- 768 seizure onsets in the parsed source path;
- 510 onsets matched to downloaded wearable segments;
- 49,577 one-hour HR windows in the regenerated local feature table;
- 54 seizure-level matched/coverable temporal-test events, or 40 first-event
  clusters under the 240-minute cluster-gap audit policy;
- 258 seizure onsets remain unmatched to downloaded wearable segments.

These are strong audit artifacts, but not final scientific denominators until
the manual audit and freeze are complete.

### 2.3 Phase R Hardening

The strict methods review and Phase R audit identified the project-specific
failure modes:

- thresholding or normalization leakage;
- unsafe defaults hidden in library functions;
- over-exclusion through right-censoring/postictal edge cases;
- split and denominator ambiguity;
- citable-looking numbers produced before the benchmark was frozen;
- claims outrunning proof.

Those issues led to code and policy hardening:

- split-aware normalization and threshold selection;
- train/validation/test fit-scope metadata;
- fail-closed label and report paths;
- explicit matched/coverable denominators;
- source of truth moved from chat claims to committed evidence docs;
- Gate A policy decisions recorded;
- Gate B and Gate C retained as hard blockers.

The important nuance: the code/policy guardrails are represented in the repo,
but M2/Gate closure is still not declared because the manual label audit is a
human blocker.

### 2.4 Publishability Infrastructure

From the Task 2-20 line and complementary research blocks, main now contains
engineering scaffolds for almost every paper component:

- Task 2: unified leaderboard schema;
- Task 3: leaderboard row runner;
- Task 4: constrained forecast null models;
- Task 5: calibration/Brier Skill Score reports;
- Task 6: Gate C registry guardrails;
- W2/T7: active audit selection and clinical timeline audit workbench;
- P2: conformal/personal risk intervals;
- T8: forecastability atlas;
- T9: multiday cycle features;
- T10: external SOTA reproduction bridge;
- T11: SeizeIT2 full-track scaffold;
- T12: observability/missingness layer;
- T13: patient-adaptive priors;
- T14: supervised model ladder runner;
- T16: edge-aware ablation report;
- T17: statistical robustness layer;
- T18: clinical utility analysis;
- T19: failure taxonomy;
- W1: AI-assisted workflow forensics;
- M1: sparse autoencoder interpretability reports;
- M3: counterfactual probing;
- P3/N1: longitudinal deep-dive report;
- T15: foundation-transfer protocol;
- F2: federated benchmark protocol;
- T20: paper artifact package;
- anti-hallucination audit and claims-surface hardening.

The key point is that many tasks are "implemented as infrastructure", not
"scientifically completed as citable results". Most are pre-Gate-C safe
because they explicitly mark outputs as non-citable unless frozen artifacts are
provided.

## 3. Current Done / Ongoing / To Do

### Done

- The repo has a coherent scientific thesis and operating playbook.
- The package has a broad, testable benchmark scaffold.
- Real MSG and SeizeIT2 pathways exist at pipeline-check level.
- Leaderboard, calibration, nulls, conformal, clinical utility, atlas,
  observability, robustness, external-SOTA, and paper-package infrastructure
  exist.
- Anti-hallucination and claims-surface guardrails were added.
- The SOTA boundary is corrected: EpiTwin-Open is not framed as the first
  wearable seizure-forecasting system; Nasseri 2025 is the direct wearable
  forecasting boundary, and SeizureFormer 2026 is contextual implant-derived
  long-horizon work, not a direct HR/steps comparator.

### Ongoing / Blocked

- Gate B is not closed: manual seizure timeline/source audit remains the
  central bottleneck.
- Gate C is not passed: frozen splits, leakage-clean registry, and
  pre-registration/DOI are not done.
- A100 training is not cleared.
- Current real-data numbers are pipeline checks only.
- SeizeIT2 full-cohort validation remains incomplete.
- MSG event matching remains incomplete for 258 onsets.
- The 24-hour MSG SOP is coverage-limited and may require a shorter horizon,
  a stricter coverage subset, or a different continuity model.

### To Do

The next phase should stop adding attractive side features and convert the
infrastructure into a certified benchmark.

Immediate priority:

1. Close Gate B with a real, committed manual audit.
2. Dry-run and then pass Gate C with frozen splits and registry artifacts.
3. Rerun transparent baselines only on frozen artifacts.
4. Produce citable leaderboard rows with denominators, calibration, FAR/day,
   TIW, BSS, leakage status, and audit status.
5. Only then run supervised/deep models and A100 experiments.

## 4. What This Means For Publication

The project is not yet publishable as a final clinical/model-result paper.

It is already publishable in spirit as a strong benchmark/methodology
direction, but the hard Q1 version requires certification:

- Gate B: source/timeline audit has to prove the labels are reliable.
- Gate C: frozen benchmark artifacts have to make runs reproducible and
  pre-registered.
- Baselines: transparent null/rule/cycle baselines must run on the frozen
  benchmark.
- Comparisons: direct and contextual SOTA comparisons must be separated by
  modality, task, horizon, split, and data type.
- Claims: every result must carry its denominator, coverage fraction, leakage
  status, audit status, and citation status.

If those are done, the defensible Q1 contribution is not "we built a model that
predicts all seizures". The stronger contribution is:

> an open, leakage-safe, calibrated, forecastability-aware benchmark and
> evaluation framework for public wearable seizure-risk forecasting, with
> transparent baselines, uncertainty, observability limits, alarm-burden
> constraints, and reproducibility artifacts.

That contribution can remain valuable even if the final EpiTwin-SSL model does
not beat transparent baselines, because a negative or limited result is itself
important if the benchmark and evaluation are credible.

## 5. Main Gaps And Risks

### Risk 1 - Manual Audit Bottleneck

The biggest scientific risk is not model architecture. It is label reliability.
If Gate B is weak, every downstream table becomes fragile.

Mitigation:

- use the active audit selector to prioritize the highest-yield cases;
- audit 5-10 seizure timelines per dataset at minimum;
- record source onset, recording alignment, SPH/SOP label correctness,
  ictal/postictal exclusion, and right-censoring decisions;
- commit the audit log and rerun affected artifacts.

### Risk 2 - Frozen Benchmark Not Yet Real

Without Gate C, all numbers remain exploratory.

Mitigation:

- run a Gate C dry-run registry now;
- hash splits, labels, prediction inputs, and source manifests;
- enforce citable rows only through the registry;
- pre-register the frozen protocol before final results.

### Risk 3 - MSG Coverage Constraints

MSG has strong longitudinal value, but the public wearable files create
coverage and right-censoring constraints.

Mitigation:

- treat SPH60/SOP1440 as coverage-limited unless proven otherwise;
- include SOP 240 min or another well-powered horizon;
- report seizure-level and cluster-level denominators;
- analyze unmatched-onset reasons explicitly.

### Risk 4 - Overclaiming SOTA

The field already has non-invasive wearable seizure forecasting and implant-
derived long-horizon forecasting work.

Mitigation:

- compare only when task, modality, horizon, split, and dataset type are
  compatible;
- use SeizureFormer as contextual long-horizon forecasting, not direct HR/steps
  competition;
- use Nasseri 2025 as the direct wearable SOTA boundary.

### Risk 5 - Too Many Pre-Gate Artifacts

The project now has many reports. The danger is mistaking infrastructure volume
for certified evidence.

Mitigation:

- keep all pre-Gate outputs marked non-citable;
- focus next work on Gate B/C and frozen reruns;
- avoid new model-side complexity until the benchmark is certified.

## 6. Best Next Work Blocks

### Block A - Gate B Audit Acceleration

Goal: make the manual audit feasible and evidence-rich.

Concrete work:

- run active audit target selection for MSG and SeizeIT2;
- generate a compact clinician review packet for the top-K cases;
- add summary tables of why each case was selected;
- produce a final `reports/human_label_audit_YYYY-MM-DD.md` template that can
  be filled and committed.

Expected output:

- a shorter, prioritized audit queue;
- clear evidence for each selected event;
- faster path to Gate B.

### Block B - Gate C Dry-Run Freeze

Goal: prove the registry can freeze artifacts before the final human approval.

Concrete work:

- create a non-citable dry-run registry for current MSG/SeizeIT2 artifacts;
- verify row counts, event counts, hashes, split refs, leakage statuses;
- make failures explicit rather than silently passing;
- document exactly what blocks a real Gate C freeze.

Expected output:

- `reports/gate_c_dry_run_YYYY-MM-DD.md`;
- machine-readable registry diagnostics;
- a punch list from exploratory to frozen.

### Block C - SeizeIT2 Full-Cohort Validation

Goal: convert SeizeIT2 from partial local track to a real cohort benchmark path.

Concrete work:

- verify available subjects and annotations;
- run parser/label/window/metric checks across all available subjects;
- separate detection, early warning, and short-horizon forecasting tasks;
- generate cohort-level denominators without claiming final performance.

Expected output:

- full-track data-quality table;
- cohort coverage report;
- clear task split between detection and forecasting.

### Block D - MSG Data-Gap Triage

Goal: explain the 258 unmatched MSG onsets and decide whether they are excluded,
recoverable, or outside wearable coverage.

Concrete work:

- classify unmatched events by patient, source file, missing segment, time-zone
  or interval mismatch, duplicate handling, and wearable non-coverage;
- produce patient-level recoverability status;
- decide whether final benchmark uses matched-only, coverage subset, or a
  different horizon.

Expected output:

- denominator defensibility;
- reduced reviewer attack surface;
- more honest forecastability analysis.

### Block E - Frozen Transparent Baseline Rerun

Goal: once Gate B/C pass, produce the first truly citable benchmark table.

Concrete work:

- rerun random rate-matched, cycle, HR/ECG, ACC/EMG, and patient-adaptive nulls;
- emit leaderboard rows only through the frozen registry;
- report confidence intervals, denominators, BSS, calibration, FAR/day, TIW.

Expected output:

- Table 3 baseline results;
- primary benchmark evidence.

### Block F - Supervised/Deep Model Ladder And A100

Goal: evaluate whether model learning adds value beyond transparent baselines.

Concrete work:

- run TCN/GRU supervised ladder on frozen splits;
- then run EpiTwin-SSL/A100 only from committed configs;
- preserve fit-scope metadata and leakage audits;
- accept a negative result if transparent baselines win.

Expected output:

- model contribution or honest negative finding;
- no uncitable GPU results.

## 7. Suggested Roadmap

### Next 48 Hours

1. Produce Gate B audit-acceleration package.
2. Produce Gate C dry-run freeze diagnostics.
3. Produce MSG unmatched-onset triage table.
4. Keep all outputs explicitly non-citable.

### Next Week

1. Complete human audit logs for SeizeIT2 and MSG.
2. Apply any parser/label corrections found by the audit.
3. Regenerate labels, windows, splits, and audit reports.
4. Prepare the real Gate C registry and split freeze.

### Next 2-3 Weeks

1. Pre-register the frozen protocol.
2. Rerun transparent baselines on frozen artifacts.
3. Produce citable leaderboard rows.
4. Generate forecastability atlas and clinical utility reports from frozen
   outputs.
5. Run statistical robustness and SOTA-positioning matrix.

### Next 1-2 Months

1. Run supervised ladder and EpiTwin-SSL/A100 experiments.
2. Complete observability/edge ablation.
3. Complete hostile-reviewer audit and paper artifact package.
4. Draft the manuscript from certified artifacts only.

## 8. Recommendation

The best immediate move is not another model. It is to convert the existing
infrastructure into a certified benchmark.

Priority order:

1. Gate B audit acceleration.
2. Gate C dry-run freeze.
3. MSG data-gap triage.
4. SeizeIT2 full-cohort validation.
5. Frozen transparent baseline rerun.
6. Forecastability atlas and clinical utility on frozen outputs.
7. Supervised/deep model ladder.
8. A100 EpiTwin-SSL.
9. Phase G certification.
10. Manuscript.

This keeps the project aligned with the Q1 goal: rigorous, reproducible,
auditable, and scientifically honest.

## 9. Bottom Line For The Professor

In one paragraph:

EpiTwin-Open has evolved from a seizure-detection prototype into a rigorous
open benchmark framework for calibrated wearable seizure-risk forecasting. The
contribution is not just a neural network: it is a full evaluation stack with
SPH/SOP labels, ictal/postictal exclusion, right-censoring, leakage-aware
splits, event-level metrics, alarm-burden constraints, calibration/Brier Skill
Score, conformal uncertainty, active clinical audit tooling, forecastability
and observability analysis, SOTA-positioning scaffolds, and reproducibility
guardrails. The work is not yet a final publishable clinical-result paper
because manual label audit and benchmark freeze are still required, but the
infrastructure and scientific framing are strong enough to become a Q1-level
benchmark/methodology contribution if Gate B, Gate C, frozen baselines, and
certified comparisons are completed.

## 10. Current Command Evidence

This synthesis was prepared from:

- `PROJECT_STATUS.md`
- `PLAYBOOK.md`
- `docs/ROADMAP_HIGH_LEVEL.md`
- `docs/PUBLICATION_PROPOSAL.md`
- `docs/research/2026-05-20_consolidated_task_scoring.md`
- `docs/research/2026-05-20_fused_task_scoring_codex_challenge.md`
- recent merged history through `origin/main@4475545`

No new benchmark number is introduced by this document.
