# Q1-Publishable Contribution Roadmap

Date: 2026-05-20
Author: Codex
Status: proposal, not executed
Scope: turn EpiTwin-Open from a rigorous scaffold into a defensible Q1-level
scientific contribution.

## Executive Thesis

The strongest publishable contribution is not "one more seizure model". The
field already has wearable seizure forecasting claims, including ultra-long-term
non-invasive HR/steps forecasting. The defensible Q1 contribution is:

> An open, leakage-safe, clinically constrained wearable seizure-risk benchmark
> that quantifies forecastability, observability, calibration, false-alarm
> burden, edge cost, and null-corrected skill across public wearable datasets.

This makes negative results useful: if a horizon, patient group, or modality is
not forecastable, the benchmark should prove that honestly. That is more
valuable than overfitting a single headline number.

## Evidence Used

- SeizeIT2 is a public multimodal wearable focal-epilepsy dataset with more
  than 11,000 hours, 883 focal seizures, 125 patients, and official benchmark
  framing for wearable seizure detection:
  https://www.nature.com/articles/s41597-025-05580-x
- My Seizure Gauge is a public long-term HR/steps wearable dataset with 11
  participants, EEG-confirmed seizures, and average recording duration of 337
  days:
  https://zenodo.org/records/17380899
- Nasseri et al. report hybrid short- and long-horizon wearable seizure
  forecasting using HR/steps and cycle-based methods, so EpiTwin-Open must not
  claim to be the first wearable seizure forecaster:
  https://seermedical.com/research/forecasting-epileptic-seizures-with-wearable-devices/
- Seizure forecast reviews emphasize probabilistic forecasting, AUC/Brier/BSS,
  and standardized validation:
  https://pmc.ncbi.nlm.nih.gov/articles/PMC11447137/
- SzCORE shows how seizure evaluation can become publishable as an open
  standard, not just a model comparison:
  https://arxiv.org/abs/2402.13005
- Wearable biosignal foundation models are now relevant SOTA context, but they
  should be treated as transfer-learning baselines, not as a substitute for
  clinical benchmark correctness:
  https://proceedings.iclr.cc/paper_files/paper/2024/hash/0d99a8c048befb6dd6e17d7684adacac-Abstract-Conference.html

## Publication Strategy

The target paper should be framed as a benchmark + forecastability study:

1. Public wearable datasets: SeizeIT2 for detection/early-warning and MSG for
   longitudinal HR/steps forecasting.
2. Standardized SPH/SOP labels, censoring rules, postictal exclusion, and
   leakage audits.
3. Event-level metrics, FAR/day, Time-in-Warning, calibration, Brier Skill
   Score, and edge-cost fields.
4. Constrained nulls and cycle baselines before neural models.
5. Patient-level forecastability maps that show where wearable signals help,
   where they do not, and why.

The contribution becomes Q1-plausible when we can say:

> We do not merely report a model score; we release the protocol, artifacts,
> null models, reproducible runners, and failure analysis needed to evaluate
> wearable seizure forecasting honestly.

## Task Backlog

### Task 5 - Calibration, BSS, And Null-Corrected Skill Report

Branch suggestion: `codex/calibration-bss`

Objective: turn Task 4 null models into quantitative reference baselines for
every prediction table.

Deliverables:

- CLI/report that consumes model predictions plus one or more null prediction
  tables.
- Brier, ECE, reliability bins, BSS versus `split_prevalence_prior`,
  `patient_prior`, `rate_matched_random`, and `cycle_preserving_random`.
- Bootstrap confidence intervals by patient and by seizure event.
- Markdown + CSV/JSON outputs compatible with the leaderboard schema.

Acceptance criteria:

- Synthetic tests prove BSS-vs-self is zero.
- A deliberately random model does not look better than its null.
- Missing or mismatched prediction rows raise explicit errors.
- No real-data number is reported before Gate C unless marked
  `pre-Gate-C exploratory, not citable`.

Scientific value:

This is mandatory for Q1. It upgrades the claim from "model has sensitivity" to
"model has null-corrected probabilistic skill under alarm burden".

### Task 6 - Gate C Split Freeze And Artifact Registry

Branch suggestion: `codex/gate-c-freeze-registry`

Objective: make every later result citable by freezing splits, manifests, and
artifact hashes.

Deliverables:

- `artifacts/registry/*.json` with dataset version, source URL, local path,
  checksum, row counts, event counts, split IDs, and generation command.
- Split manifest for each dataset/task/horizon.
- Human-readable Gate C report with freeze decision, exclusions, and known
  limitations.
- Guardrail that refuses benchmark rows when the artifact registry is missing
  or dirty.

Acceptance criteria:

- Re-running the registry check verifies checksums and row/event counts.
- Split files are immutable unless an explicit new registry version is created.
- CI has a synthetic registry test.

Scientific value:

Without this, no result is citable. With it, the paper can claim reproducibility
and avoid the "pre-freeze exploratory" weakness.

### Task 7 - Manual Clinical Timeline Audit Workbench

Branch suggestion: `codex/clinical-timeline-audit`

Objective: make the label audit human-verifiable around seizures and around
negative windows.

Deliverables:

- Static HTML or Streamlit timeline viewer for each audited recording.
- Layers: seizure onset, SPH, SOP, postictal exclusion, censoring, split,
  sensor availability, and model alarm intervals.
- Reviewer sheet with pass/fail/uncertain annotations and notes.
- Aggregated audit report with sampled positives, sampled negatives, and all
  edge cases.

Acceptance criteria:

- At least synthetic timeline tests validate geometry and interval placement.
- A real audit can be performed without editing code.
- Reviewer decisions are stored as data, not prose only.

Scientific value:

This converts "we believe labels are correct" into a traceable clinical
attestation. It is a strong differentiator versus many ML-only seizure papers.

### Task 8 - Forecastability Atlas

Branch suggestion: `codex/forecastability-atlas`

Objective: quantify which patients, horizons, modalities, and temporal regimes
are actually forecastable above null.

Deliverables:

- Per-patient and pooled tables for BSS, event sensitivity, FAR/day, TIW,
  reliability slope, and null-model deltas.
- Horizon grid: short, medium, daily, and long horizon where supported by the
  dataset.
- Modality grid: HR, steps/ACC, EDA/TEMP if available, and multimodal.
- "Unforecastable" label when confidence intervals overlap nulls.

Acceptance criteria:

- Produces a figure/table that can go directly into the paper.
- Uses only frozen Gate C artifacts for citable numbers.
- Negative findings are explicitly represented, not hidden.

Scientific value:

This is likely the core Q1 contribution. It answers a better question than
"which model wins": when is wearable seizure risk observable at all?

### Task 9 - Multiday Cycle And Phase-Locking Features

Branch suggestion: `codex/multiday-cycle-features`

Objective: go beyond hour-of-day and implement clinically interpretable rhythm
features.

Deliverables:

- Circadian phase, weekly phase, and patient-specific multiday cycle features.
- Rolling-origin fit to avoid future leakage.
- Cycle-only model and cycle+HR/steps hybrid model.
- Ablation versus hour-of-day Task 4 null.

Acceptance criteria:

- Feature generation never reads future events.
- Synthetic periodic seizures are recovered.
- Randomized seizure times destroy the apparent cycle skill.

Scientific value:

This directly addresses current wearable forecasting SOTA, where cycles are a
central mechanism. It is also interpretable to clinicians.

### Task 10 - External SOTA Reproduction Under Our Runner

Branch suggestion: `codex/reproduce-first-sota`

Objective: reproduce at least one external family under our metrics, not just
cite it.

Candidate families:

- SeizeIT2 official detection baselines or ECG-only anomaly methods.
- Matrix Profile / MADRID / TimeVQVAE-style ECG anomaly detection.
- MSG-style hybrid cycle + ML forecasting.
- LSTM wearable forecasting protocol from older Empatica literature.

Deliverables:

- One reproduction runner with pinned config and exact source reference.
- Leaderboard row generated by the same schema as our models.
- Failure note if modality/data mismatch prevents faithful reproduction.

Acceptance criteria:

- The reproduced model runs through `scripts/make_leaderboard_row.py`.
- The report separates detection, early warning, and forecasting.
- Any mismatch with the original paper is explicit.

Scientific value:

This is the difference between "we compare narratively to SOTA" and "we put
SOTA through our public benchmark".

### Task 11 - SeizeIT2 Full-Benchmark Track

Branch suggestion: `codex/seizeit2-full-track`

Objective: stop relying on a small edge subset as the SeizeIT2 story.

Deliverables:

- Official SeizeIT2 split support.
- Detection and early-warning tasks separated from long-horizon forecasting.
- ECG-only, ACC-only, bte-EEG-only, and multimodal tracks when data are
  available.
- SzCORE-inspired output fields for event/sample-level scoring.

Acceptance criteria:

- Dataset summary matches published SeizeIT2 counts within documented filters.
- Official split rows are reproducible.
- Full-track results never get mixed with MSG long-horizon forecasting.

Scientific value:

This broadens the paper from a single MSG forecasting study to a public
wearable benchmark suite.

### Task 12 - Observability And Missingness Modeling

Branch suggestion: `codex/observability-missingness`

Objective: make "not observable" a first-class output instead of forcing every
window into a risk prediction.

Deliverables:

- Sensor coverage, dropout, motion artifact, and physiological plausibility
  features.
- `observable_score` or `deficiency_time` output.
- Metrics stratified by observable vs deficient windows.
- Optional abstention policy under a fixed deficiency budget.

Acceptance criteria:

- Missingness cannot improve scores through leakage.
- Bad-quality synthetic windows trigger lower observability.
- Leaderboard rows record deficiency/abstention status.

Scientific value:

This is a strong paper angle: a clinically honest system should know when the
wearable signal cannot support a forecast.

### Task 13 - Patient-Adaptive Hierarchical Baselines

Branch suggestion: `codex/patient-adaptive-baselines`

Objective: model patient specificity without leaking held-out outcomes.

Deliverables:

- Population prior, patient prior, and empirical-Bayes shrinkage baseline.
- Cold-start, warm-start, and rolling-origin evaluation modes.
- Minimum-event thresholds and fallback markers.

Acceptance criteria:

- Below-threshold patients fall back explicitly.
- Synthetic patients with known rates are recovered with shrinkage.
- Cold-start and warm-start rows cannot be confused in the leaderboard.

Scientific value:

Seizure forecasting is patient-specific. A fair benchmark must compare neural
models against strong patient-adaptive non-neural baselines.

### Task 14 - Small Supervised Model Ladder

Branch suggestion: `codex/supervised-model-ladder`

Objective: build a controlled ladder from simple models to temporal neural
models under identical frozen splits.

Deliverables:

- Logistic regression / gradient-boosted tree / MLP / TCN / GRU configs.
- Same features, same splits, same threshold budget, same leaderboard runner.
- Ablation by feature family and horizon.

Acceptance criteria:

- Every model emits standardized predictions.
- No model reports a number without a null-corrected comparator.
- Training logs, config, seed, and artifact hashes are stored.

Scientific value:

This prevents the paper from being dismissed as only tooling. It provides a
measured model ladder while keeping the benchmark as the main contribution.

### Task 15 - Foundation-Model Transfer Baseline

Branch suggestion: `codex/wearable-fm-transfer`

Objective: test whether wearable foundation-model embeddings improve seizure
forecasting under our benchmark.

Deliverables:

- Adapter interface for external PPG/ECG foundation embeddings when modality
  and license allow.
- Linear probe and frozen-encoder baselines.
- Comparison against hand-crafted HR/steps/cycle features.

Acceptance criteria:

- License and modality compatibility documented before use.
- Embeddings are generated without reading labels.
- Results are reported as transfer baselines, not as a new foundation model.

Scientific value:

This connects the work to modern AI without making a fragile claim that we have
trained a foundation model ourselves.

### Task 16 - Edge-Aware Forecasting Ablation

Branch suggestion: `codex/edge-forecast-ablation`

Objective: connect forecast quality to deployability.

Deliverables:

- RAM, flash, latency, parameter count, and estimated energy for each model.
- Quantized tiny models where supported.
- Skill-vs-cost Pareto frontier.

Acceptance criteria:

- Edge-cost estimates are traceable to commands or documented calculators.
- No hardware claim is made without measurement or conservative estimation.
- Paper table separates clinical score from edge cost.

Scientific value:

This preserves the IoT/edge identity of the project and gives a practical
engineering contribution beyond clinical metrics.

### Task 17 - Statistical Significance And Robustness Layer

Branch suggestion: `codex/statistical-robustness`

Objective: make all paper claims statistically defensible.

Deliverables:

- Patient-level bootstrap confidence intervals.
- Event-level bootstrap confidence intervals.
- Permutation tests against nulls.
- Multiple-comparison correction for horizon/modality grids.

Acceptance criteria:

- Synthetic known-effect tests pass.
- Tiny-N warnings appear when intervals are unstable.
- Paper tables include uncertainty, not only point estimates.

Scientific value:

This is a Q1 requirement. Without uncertainty, seizure forecasting claims are
too easy to overstate.

### Task 18 - Clinical Utility And Alarm Policy Analysis

Branch suggestion: `codex/clinical-utility`

Objective: translate scores into clinically meaningful tradeoffs.

Deliverables:

- Sensitivity vs FAR/day vs TIW policy curves.
- Decision-curve or utility-style analysis with configurable costs.
- Alarm episode consolidation and refractory alarm logic.
- Lead-time distribution under each alarm budget.

Acceptance criteria:

- Utility assumptions are configurable and documented.
- Alarm policies are evaluated on frozen splits only.
- No clinical recommendation is made; the output is decision-support analysis.

Scientific value:

This makes the work relevant to clinicians and reviewers who care less about
AUC and more about alarm burden.

### Task 19 - Failure Taxonomy And Error Forensics

Branch suggestion: `codex/failure-taxonomy`

Objective: classify why forecasts fail.

Deliverables:

- False-negative event table with seizure type, patient, horizon, sensor
  availability, preceding activity, circadian phase, and postictal proximity.
- False-alarm episode table with likely artifact/motion/signal-quality tags.
- Representative timeline figures for paper qualitative analysis.

Acceptance criteria:

- Every failure category is data-backed or marked unknown.
- No speculative clinical explanation is stored as fact.
- At least one paper figure can be generated automatically.

Scientific value:

Q1 reviewers value insight. This task turns metrics into mechanisms and
limitations.

### Task 20 - Paper Artifact Package

Branch suggestion: `codex/paper-artifact-package`

Objective: make the paper submission and reproducibility package coherent.

Deliverables:

- Contribution statement.
- Related-work table with verified citations.
- Methods section skeleton linked to exact scripts/configs.
- Reproducibility checklist.
- Dataset cards and model cards.
- Limitations and negative-result statement.

Acceptance criteria:

- Every paper claim links to a committed artifact or source.
- No phantom citation.
- All pre-Gate-C numbers are either removed or explicitly labeled.

Scientific value:

This converts engineering output into a submission-ready scientific narrative.

## Recommended Execution Order

1. Task 5: Calibration/BSS report.
2. Task 6: Gate C split freeze and artifact registry.
3. Task 7: Manual clinical timeline audit workbench.
4. Task 8: Forecastability atlas.
5. Task 9: Multiday cycle features.
6. Task 10: First external SOTA reproduction.
7. Task 11: SeizeIT2 full-benchmark track.
8. Task 12: Observability and missingness.
9. Task 13: Patient-adaptive hierarchical baselines.
10. Task 14: Small supervised model ladder.
11. Task 17: Statistical robustness layer.
12. Task 18: Clinical utility analysis.
13. Task 19: Failure taxonomy.
14. Task 16: Edge-aware ablation.
15. Task 15: Foundation-model transfer baseline.
16. Task 20: Paper artifact package.

Rationale:

- Tasks 5-8 make the benchmark scientifically defensible.
- Tasks 9-14 make the model comparisons meaningful.
- Tasks 17-19 make the claims robust and clinically interpretable.
- Tasks 15-16 add modern AI and IoT/edge relevance without compromising the
  core benchmark.
- Task 20 packages the contribution for submission.

## Minimum Publishable Unit

If time is limited, the minimum Q1-plausible package is:

1. Gate C freeze.
2. Manual label audit.
3. Null-corrected calibration/BSS report.
4. Forecastability atlas.
5. Multiday cycle baseline.
6. One external SOTA reproduction.
7. Statistical confidence intervals.
8. Paper artifact package.

This is enough to claim a real benchmark contribution even if neural models do
not beat all baselines.

## Strongest Paper Title Direction

Working title:

> EpiTwin-Open: A Leakage-Safe Benchmark for Forecastability-Aware Wearable
> Seizure Risk Estimation

Alternative:

> What Is Forecastable From Public Wearable Epilepsy Data? A Null-Corrected,
> Calibration-Aware Benchmark

The second title is scientifically stronger because it promises an answer, not
just a software artifact.

## Stop Rules

- Do not report real-data benchmark numbers before Gate C.
- Do not compare detection and forecasting in the same row.
- Do not use AUC as the main clinical headline.
- Do not hide patients or horizons that are not forecastable.
- Do not claim first wearable seizure forecasting.
- Do not use SOTA papers without verified DOI/URL and task compatibility.
- Do not run large GPU experiments until labels, splits, nulls, and clinical
  audit are stable.

## Conclusion

The project becomes publishable when it stops trying to win by one model score
and instead wins by scientific discipline: public data, frozen artifacts,
audited labels, constrained nulls, calibrated skill, forecastability maps,
SOTA reproduction, statistical uncertainty, and transparent failure analysis.

That is a Q1-grade contribution because it gives the field a way to measure
wearable seizure forecasting honestly.
