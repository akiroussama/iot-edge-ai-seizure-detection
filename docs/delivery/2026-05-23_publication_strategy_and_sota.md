# Publication Strategy And SOTA Position

Date: 2026-05-23

## Executive Position

The project is now best positioned as a benchmark/methods contribution:

> EpiTwin-Open is a frozen, auditable, leakage-aware public benchmark for
> calibrated wearable seizure-risk forecasting.

The project should not be positioned as:

> A new SOTA clinical seizure prediction model.

That distinction is essential for reviewer credibility.

## What The SOTA Already Has

### Wearable Long-Term Forecasting Exists

Nasseri et al. published a 2025 Epilepsia paper on wearable seizure forecasting
using heart rate and step count from 11 participants, with EEG-confirmed
seizures and average recording duration of 337 days. The paper proposes hybrid
machine-learning and cycle-based models for short and long horizons.

Source:

- https://pubmed.ncbi.nlm.nih.gov/40411751/

Implication:

- We cannot claim first wearable seizure forecasting.
- We can claim an open frozen benchmark that makes such work easier to compare,
  audit, and reproduce.

### MSG Is A Real Public Longitudinal Wearable Dataset

The My Seizure Gauge Zenodo record describes 11 participants, wrist-worn heart
rate and step count, EEG-confirmed seizures, and average recording duration of
337 days.

Source:

- https://zenodo.org/records/17380899

Implication:

- MSG is the right public dataset for a longitudinal wearable forecasting
  benchmark.
- Denominator accounting must be explicit because the local metric denominator
  is the matched, prediction-coverable frozen test subset, not all annotated
  seizures.

### Seizure Forecasting Evaluation Is Heterogeneous

The 2024 Journal of Neurology systematic review/meta-analysis reports major
heterogeneity in study design, horizons, datasets, and metrics. It emphasizes
probabilistic metrics such as Brier Score and Brier Skill Score, and reports
only modest pooled skill over naive forecasts.

Source:

- https://link.springer.com/article/10.1007/s00415-024-12655-z

Implication:

- A benchmark paper with Brier/BSS, calibration, FAR/day, Time-in-Warning, and
  leakage-safe splits addresses a recognized field gap.

### Detection And Forecasting Must Be Separated

SeizeIT2 is a major public wearable focal epilepsy dataset, but its primary
framing is seizure detection in a monitored/hospital environment, not
longitudinal seizure forecasting.

Source:

- https://pmc.ncbi.nlm.nih.gov/articles/PMC12264188/

Implication:

- SeizeIT2 can support modality observability and detection/early-warning
  analysis.
- MSG is the stronger dataset for long-term HR/steps forecasting claims.

### Clinical Translation Still Requires Caution

The 2024 Frontiers in Neurology review emphasizes unseen validation, leakage
avoidance, false-positive burden, data deficiency, and careful clinical framing.
It also notes that seizure prediction/forecasting remains mainly a research
domain rather than broadly proven clinical practice.

Source:

- https://www.frontiersin.org/articles/10.3389/fneur.2024.1425490

Implication:

- Our conservative claim language is a strength, not a weakness.
- Reviewers will likely punish clinical overclaiming.

## Our Differentiation

EpiTwin-Open differs from a model-only paper by delivering:

- frozen registry-backed evaluation;
- explicit denominator policy;
- event-level metrics;
- FAR/day and Time-in-Warning;
- calibration and Brier Skill Score;
- bootstrap confidence intervals;
- null baselines, including cycle-preserving temporal structure;
- forecastability labels that prevent overclaiming;
- human/audit trace documents;
- a leaderboard schema ready for future models.

## Paper Claim Ladder

### Tier 1: Safe Claims

These are safe now:

- We built and froze a benchmark evaluation package.
- We provide the first frozen null-baseline leaderboard for the local MSG
  Gate C package.
- Cycle-preserving temporal structure beats climatology on this frozen test
  split.
- Future learned models must beat a cycle-preserving null, not only a split
  prevalence prior.

### Tier 2: Conditional Claims

These need supervisor/manuscript review:

- The framework is citable as a benchmark artifact.
- The frozen MSG null results can be included in a paper table.
- The public-data protocol can be proposed as an open baseline for wearable
  seizure-risk forecasting.

### Tier 3: Do Not Claim

Do not claim:

- clinical deployment readiness;
- SOTA model performance;
- superiority to Nasseri et al.;
- first wearable seizure forecasting system;
- full-cohort MSG performance;
- generalized seizure predictability across all patients.

## Target Journal Ranking

| Priority | Journal | Likely level | Fit | Rationale | Risk |
| ---: | --- | --- | --- | --- | --- |
| 1 | IEEE Journal of Biomedical and Health Informatics | Q1 | Very strong | Benchmark, calibration, health AI evaluation, reproducibility | Needs strong biomedical informatics framing |
| 2 | Scientific Data | Q1-style / high-impact data-resource | Very strong | Frozen artifacts, registry, reusable benchmark package | Must emphasize data/resource value over model novelty |
| 3 | Epilepsia | Q1 specialist | Strong if clinically framed | Best epilepsy audience and authority | Needs clinical coauthoring and concise clinical message |
| 4 | npj Digital Medicine | Q1 stretch | Ambitious | Digital medicine, wearable monitoring, clinical translation | High desk-reject risk without major clinical validation |
| 5 | Epilepsia Open | Q2/Q1 depending metric/category | Safe specialist fallback | Transparent epilepsy benchmark, open access | Less prestigious than Epilepsia |
| 6 | IEEE Access | Q2/Q1 depending metric/category | Safe engineering fallback | Broad open engineering route | Less selective and less prestigious |

Notes:

- Quartiles change by year and category. Final Q1/Q2 status should be verified
  in the institution's JCR/Scopus access before submission.
- Journal fit matters more than impact factor alone.

## Recommended Submission Route

Primary recommendation:

1. Prepare for IEEE JBHI first.
2. If the editor pushes toward data-resource framing, adapt to Scientific Data.
3. If Mme Manel wants the epilepsy-clinical audience first, submit to Epilepsia.
4. Keep npj Digital Medicine as a stretch only if the manuscript is rewritten
   around broad digital-medicine impact.

## Why Acceptance Is Plausible

Acceptance is plausible because:

- The field needs reproducible evaluation standards.
- The SOTA review literature explicitly highlights heterogeneity and metric
  inconsistency.
- Existing wearable forecasting work makes open comparison more important.
- The project has frozen artifacts, rerun harnesses, audit reports, and
  citable null baselines.
- The paper can be honest about negative and underpowered findings.

Main risk:

- If reviewers expect a high-performing new model, this manuscript will look
  incomplete.

Mitigation:

- Frame the paper as a benchmark and forecastability framework from the title,
  abstract, introduction, and cover letter.

## Manuscript Skeleton

1. Introduction
   - Clinical need.
   - Difference between prediction and forecasting.
   - Reproducibility and leakage gap.

2. Related Work
   - Wearable forecasting SOTA.
   - Seizure forecasting metrics.
   - Public datasets: MSG and SeizeIT2.

3. Methods
   - Data sources.
   - SPH/SOP labels.
   - Exclusions and right-censoring.
   - Split policy.
   - Frozen registry.
   - Null baselines.
   - Metrics.

4. Results
   - Frozen dataset denominator.
   - Null baseline leaderboard.
   - Calibration/BSS.
   - Forecastability Atlas.

5. Discussion
   - What is forecastable above null.
   - Why cycle baselines matter.
   - Why leakage-safe evaluation changes model claims.
   - Limitations.

6. Reproducibility
   - Repository.
   - Frozen artifacts.
   - Rerun command.
   - Data availability.

7. Conclusion
   - EpiTwin-Open as a benchmark for future wearable seizure-risk models.
