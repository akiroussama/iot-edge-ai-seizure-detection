# Final Delivery Brief

Date: 2026-05-23

Project: EpiTwin-Open / wearable seizure-risk forecasting benchmark

## Scope Decision

We stop feature improvement work here and move to delivery.

The project should now be presented as a frozen, reproducible benchmark and
publication proposal, not as an open-ended engineering backlog. Future model
improvements can be listed as follow-up work, but they should not expand the
current delivery scope.

## Delivered State

Main branch status:

- Delivery branch base: `origin/main`.
- Gate C MSG freeze is committed.
- Gate C frozen null benchmark is committed and merged through PR #54.
- Current frozen benchmark package:
  `reports/gate_c_frozen_benchmark_2026-05-23/`.

Core frozen input registry:

- `reports/gate_c_msg_freeze_2026-05-23/gate_c_registry.json`

Core frozen outputs:

- `reports/gate_c_frozen_benchmark_2026-05-23/frozen_benchmark_manifest.json`
- `reports/gate_c_frozen_benchmark_2026-05-23/frozen_benchmark_audit.md`
- `reports/gate_c_frozen_benchmark_2026-05-23/leaderboard_rows_with_ci.csv`
- `reports/gate_c_frozen_benchmark_2026-05-23/forecastability_atlas.csv`
- `reports/gate_c_frozen_benchmark_2026-05-23/forecastability_atlas.md`

## What Was Built

The delivered project contains:

1. A leakage-safe benchmark scaffold for wearable seizure-risk forecasting.
2. Gate B and Gate C audit traces for data readiness, human decisions, and
   freeze prerequisites.
3. A committed Gate C registry for MSG SPH60/SOP1440 frozen artifacts.
4. A frozen-only rerun harness that refuses live `data/*` inputs and reruns
   from committed freeze artifacts only.
5. A unified leaderboard schema with explicit denominator, split, horizon,
   FAR/day, Time-in-Warning, Brier score, Brier Skill Score, calibration,
   leakage status, and edge-cost fields.
6. Null baseline infrastructure:
   `split_prevalence_prior`, `rate_matched_random`, `patient_prior`, and
   `cycle_preserving_random`.
7. Calibration and Brier Skill Score reporting with bootstrap confidence
   intervals.
8. Forecastability Atlas output that separates above-null, null-overlap, and
   non-ready findings.
9. Anti-hallucination and coherence review documents that explicitly separate
   software checks, frozen null results, and non-claimable clinical/SOTA claims.

## First Frozen MSG Null Results

Frozen benchmark configuration:

- Dataset: MSG.
- Horizon: SPH60/SOP1440.
- Window: 1 hour.
- Stride: 1 hour.
- Fit split: train.
- Threshold split: validation.
- Evaluation split: test.
- Target Time-in-Warning: 0.10.
- Event filter: `recording_match_status=matched`.
- Event denominator: prediction-coverable matched test events.

Counts:

- Source events: 768.
- Matched events after event filter: 510.
- Test prediction-coverable matched events used for metrics: 54.
- Valid test prediction windows: 1,418.
- Positive test windows: 373.

| Null model | Sensitivity | FAR/day | TIW | Brier | BSS vs climatology | BSS CI |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| split_prevalence_prior | 0.648 | 1.557 | 0.099 | 0.239 | 0.000 | [0.000, 0.000] |
| rate_matched_random | 0.463 | 1.472 | 0.096 | 0.239 | 0.000 | [0.000, 0.000] |
| patient_prior | 0.056 | 0.085 | 0.038 | 0.128 | 0.466 | [-0.420, 0.771] |
| cycle_preserving_random | 0.741 | 0.592 | 0.097 | 0.222 | 0.070 | [0.034, 0.089] |

Interpretation:

- The cycle-preserving null baseline is above climatology on the frozen MSG
  split, with a patient-bootstrap BSS interval above zero.
- The patient-prior baseline has a strong point estimate but its bootstrap
  interval crosses zero, so it must remain a null-overlap finding.
- These are null baselines, not trained clinical models.
- The main scientific lock is that future learned wearable models must beat
  the cycle-preserving null, not only the split-prevalence prior.

## Defensible Contribution

The defensible contribution is:

> EpiTwin-Open provides a frozen, auditable, leakage-aware benchmark framework
> for calibrated wearable seizure-risk forecasting on public data, with explicit
> denominator accounting, clinical alarm-burden metrics, null baselines,
> calibration reporting, and forecastability classification.

This is a stronger and safer claim than:

> We built the first wearable seizure prediction model.

That claim should not be used.

## SOTA Position

The current SOTA makes the benchmark contribution necessary but also constrains
our claims.

Key external anchors:

- My Seizure Gauge is a public long-term wearable dataset with 11 epilepsy
  participants, wrist-worn heart-rate and step-count data, EEG-confirmed
  seizures, and average recording duration of 337 days.
  Source: https://zenodo.org/records/17380899
- Nasseri et al., Epilepsia 2025, report ultra-long-term non-invasive wearable
  seizure forecasting using heart rate and step count, with hybrid machine
  learning and cycle-based models at short and long horizons.
  Source: https://pubmed.ncbi.nlm.nih.gov/40411751/
- Carmo et al., Journal of Neurology 2024, report a systematic review and
  meta-analysis of seizure forecasting algorithms, highlighting strong
  heterogeneity and the importance of Brier/BSS-style probabilistic evaluation.
  Source: https://link.springer.com/article/10.1007/s00415-024-12655-z
- SeizeIT2 is a public multimodal wearable focal epilepsy dataset, primarily
  framed for seizure detection and observability rather than long-term
  forecasting.
  Source: https://pmc.ncbi.nlm.nih.gov/articles/PMC12264188/
- A Frontiers in Neurology 2024 review emphasizes unseen validation, leakage
  control, data deficiency, and the fact that seizure prediction/forecasting is
  not yet broadly clinically deployable.
  Source: https://www.frontiersin.org/articles/10.3389/fneur.2024.1425490

Positioning:

- We are not claiming to surpass Nasseri et al. as a clinical wearable
  forecasting system.
- We are claiming an open benchmark and audit framework that makes comparisons,
  negative results, calibration, denominator choice, and null baselines
  reproducible.
- This is publishable if the manuscript is framed as a benchmark/methodology
  contribution rather than as a clinical deployment claim.

## Claims Allowed

Allowed:

- We implemented a frozen, registry-backed benchmark rerun harness.
- We report first frozen MSG null-baseline results.
- We expose that cycle-preserving temporal structure beats climatology on the
  frozen MSG test split.
- We provide leaderboard, calibration, and forecastability artifacts.
- We define a reproducible evaluation protocol for future wearable seizure-risk
  models.

Not allowed:

- Claiming clinical readiness.
- Claiming SOTA model performance.
- Claiming all MSG seizures are represented in the metric denominator.
- Claiming the patient-prior result is robust, because its CI crosses zero.
- Claiming novelty as the first wearable seizure forecasting system.

## Paper Proposal

Working title:

**EpiTwin-Open: A Frozen, Leakage-Aware Benchmark for Calibrated Wearable
Seizure-Risk Forecasting**

Alternative title:

**Forecastability-Aware Evaluation of Wearable Seizure-Risk Models on Public
Longitudinal Data**

Paper type:

- Benchmark / methods / data-resource paper.

Core thesis:

Wearable seizure forecasting should be evaluated as calibrated risk estimation
under leakage, denominator, alarm-burden, and observability constraints, not as
a naive preictal/interictal classifier.

Proposed contributions:

1. Open benchmark protocol for wearable seizure-risk forecasting.
2. Frozen registry-backed evaluation package for MSG.
3. Unified leaderboard schema with clinically meaningful metrics.
4. Null-baseline family, including cycle-preserving temporal structure.
5. Forecastability Atlas that prevents overclaiming when a horizon or model is
   not above null.
6. Explicit audit trail for data readiness, human decisions, leakage, and
   citable/non-citable status.

Main paper table:

- Dataset/split/freeze summary.
- Frozen null baseline leaderboard.
- Calibration/BSS confidence intervals.
- Forecastability Atlas summary.
- Claim-status table separating citable, exploratory, and blocked outputs.

Main figures:

- Pipeline from raw public data to frozen registry and leaderboard.
- Forecasting timeline with SPH/SOP, censoring, and postictal exclusion.
- Sensitivity vs FAR/day and Time-in-Warning.
- Forecastability Atlas visualization.

## Why It Can Be Accepted

The paper can be accepted if it is submitted as a rigorous benchmark/methods
contribution because:

- The field has an acknowledged reproducibility and heterogeneity problem.
- Current reviews emphasize calibration, BSS, horizon clarity, and unseen-data
  validation.
- Existing strong wearable forecasting work increases the need for open
  comparison infrastructure.
- Our frozen harness, denominator accounting, null baselines, and audit trail
  directly answer likely reviewer concerns about leakage and overclaiming.
- The negative/underpowered findings are preserved instead of hidden, which is
  scientifically credible.

The paper is weaker if framed as:

- a new clinical model;
- a SOTA neural architecture paper;
- a deployment-ready seizure alarm system.

## Journal Strategy

Recommended first target:

1. **IEEE Journal of Biomedical and Health Informatics (Q1, strong fit)**
   - Best fit for benchmark infrastructure, biomedical AI evaluation,
     calibration, reproducibility, and health-informatics framing.
   - IEEE title list reports JBHI as Q1 in JIF quartile.
   - Source: https://open.ieee.org/wp-content/uploads/IEEE-Title-List-May-2024.pdf

Strong alternative:

2. **Scientific Data (Q1-style data/resource venue, strong benchmark fit)**
   - Best fit if the manuscript emphasizes frozen artifacts, dataset
     descriptors, reusable benchmark package, and machine-readable metadata.
   - Nature lists 2024 Journal Impact Factor 6.9.
   - Source: https://www.nature.com/sdata/journal-impact

High-risk stretch:

3. **npj Digital Medicine (Q1, very selective)**
   - Possible only if the clinical digital-medicine message is made broad and
     the manuscript demonstrates clear translational value.
   - Nature lists 2024 Journal Impact Factor 15.1.
   - Source: https://www.nature.com/npjdigitalmed/journal-impact

Specialist epilepsy target:

4. **Epilepsia (Q1 specialist, high clinical credibility)**
   - Strong if the manuscript includes epileptologist co-authorship and a clear
     clinical interpretation.
   - Risk: a benchmark/software framing may be seen as too engineering-heavy.
   - ILAE describes Epilepsia as the leading journal for epilepsy research.
   - Source: https://www.ilae.org/journals/epilepsia

Fallback / safer route:

5. **Epilepsia Open or IEEE Access**
   - Better if the Q1 route is rejected or if the paper is positioned as a
     transparent open benchmark and negative-results resource.
   - Epilepsia Open is a serious ILAE open-access venue, but less prestigious
     than Epilepsia/JBHI/npj Digital Medicine.

Recommendation:

- Submit first to IEEE JBHI if the paper is framed as biomedical AI evaluation.
- Submit first to Scientific Data if the artifact/data-resource story is the
  strongest and the manuscript prioritizes reusable benchmark package over
  algorithmic novelty.
- Keep npj Digital Medicine as an ambitious stretch only if Mme Manel wants a
  high-risk/high-reward submission.

## Delivery Package

Documents to send to Mme Manel:

- This delivery brief.
- `docs/delivery/2026-05-23_publication_strategy_and_sota.md`
- `docs/delivery/2026-05-23_email_to_mme_manel.md`
- `docs/PUBLICATION_PROPOSAL.md`
- `docs/SOTA_REVIEW_2026.md`
- `docs/research/2026-05-23_gate_c_frozen_null_benchmark.md`
- `reports/gate_c_frozen_benchmark_2026-05-23/frozen_benchmark_audit.md`

Recommended immediate action:

- Send the email draft to Mme Manel.
- Ask her to validate the framing and choose the first target journal.
- Start manuscript writing from the benchmark/methods angle.
- Do not add new experiments before the first manuscript skeleton is reviewed.
