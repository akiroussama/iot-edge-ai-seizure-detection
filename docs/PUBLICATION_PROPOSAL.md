# Publication Proposal

Working title:

**EpiTwin-Open: A Leakage-Safe Public Benchmark for Calibrated Wearable Seizure-Risk Forecasting**

Alternative title:

**Forecastability-Aware Evaluation of Wearable Seizure-Risk Models on Public Multimodal and Longitudinal Datasets**

## Target Venue

Primary targets:

- IEEE Journal of Biomedical and Health Informatics
- IEEE Transactions on Biomedical Engineering
- npj Digital Medicine
- Epilepsia Open or Epilepsia as a methods/data benchmark paper

## Core Thesis

Wearable seizure forecasting should be evaluated as calibrated patient-specific risk estimation under alarm-burden and observability constraints, not as a naive preictal/interictal classifier.

The paper will not claim that all seizures are predictable. It will measure what is forecastable from public wearable biosignals under clinically meaningful constraints.

## Scientific Gap

Recent work shows strong momentum in seizure forecasting, long-term seizure cycles, public wearable datasets, and biosignal foundation models. However, the field still lacks an open, reproducible, leakage-safe benchmark that jointly provides:

- SPH/SOP forecasting labels;
- explicit ictal/postictal exclusions;
- patient-wise and temporal split checks;
- event-level sensitivity with FAR/day and Time-in-Warning;
- calibration metrics;
- threshold selection under clinical alarm budgets;
- detection versus early warning versus short/long-horizon forecasting separation;
- full-modality versus edge-modality observability analysis.

This is the contribution EpiTwin-Open is designed to make.

Important SOTA boundary: Nasseri et al. (Epilepsia 2025, DOI 10.1111/epi.18466) already report
ultra-long-term non-invasive wearable seizure forecasting using HR/step data with EEG-confirmed
seizures. EpiTwin-Open must therefore be framed as an open benchmark, audit, and forecastability
framework, not as the first wearable seizure-forecasting system.

## Public Datasets

SeizeIT2:

- Use for multimodal wearable focal epilepsy.
- Use for detection, early warning, short-horizon forecasting exploration, and modality observability.
- Treat as detection-oriented; do not overclaim long-term forecasting from short hospital recordings.

My Seizure Gauge:

- Use for longitudinal HR/steps forecasting.
- Use for hourly/daily risk, circadian/multiday rhythm baselines, and patient-specific temporal evaluation.

## Proposed Contributions

1. **Leakage-safe public benchmark infrastructure**
   - Canonical artifact schemas.
   - Dataset parsers/dry-runs.
   - Windowing and SPH/SOP labels.
   - Leakage audit and human label audit protocol.

2. **Clinically constrained evaluation**
   - Event-level sensitivity.
   - FAR/day and FAR/hour.
   - Time-in-Warning.
   - Lead time.
   - Brier score and ECE.
   - Threshold sweeps under FAR/TIW budgets.
   - Prediction metadata documenting score-fit and threshold-selection splits.

3. **Forecastability-aware baselines**
   - Random rate-matched alarms.
   - Cycle/rhythm baseline.
   - HR/ECG tachycardia rule.
   - ACC/GYR activity rule.
   - EMG energy rule.
   - Generic anomaly score.
   - Small TCN/GRU supervised baselines only after benchmark correctness.

4. **Modality observability analysis**
   - Full wearable modalities versus ECG+ACC/GYR.
   - HR+steps longitudinal wearable setting.
   - Explicit abstention/uncertainty when signal quality or modality coverage is insufficient.

5. **Foundation-model-ready scaffold**
   - Multimodal encoders.
   - Missing modality support.
   - Masked reconstruction and future latent prediction.
   - Hazard/risk and uncertainty heads.
   - A100-ready configs after labels/splits/baselines are validated.

## Experiments

Table 1: Dataset summary

```text
Dataset | Patients | Recordings | Hours/days | Seizures | Modalities | Task
```

Table 2: Label distribution

```text
Dataset | SPH/SOP | Windows | Valid windows | Excluded ictal/postictal | Positive windows
```

Table 3: Baseline results

```text
Model | Dataset | Horizon | Event sensitivity | FAR/day | TIW | Median lead time | Brier | ECE
```

Table 4: Modality observability

```text
Modalities | Dataset | Horizon | Sensitivity @ FAR budget | Sensitivity @ TIW budget | Calibration | Abstention rate
```

Figure 1: Task timeline showing detection, early warning, SPH/SOP forecasting, and postictal exclusion.

Figure 2: Pipeline diagram from raw public datasets to canonical artifacts, labels, splits, baselines, calibration, and reports.

Figure 3: Sensitivity versus FAR/day and sensitivity versus Time-in-Warning.

Figure 4: Modality ablation/observability matrix.

## Validation Criteria

The paper is submission-ready only if:

- real dataset parsing is complete;
- 5-10 seizure timelines per dataset have been manually audited;
- leakage audit is clean;
- random rate-matched baseline has run;
- at least one clinically interpretable baseline table is generated;
- thresholds are selected on validation splits only;
- feature statistics and normalization are fit without validation/test leakage;
- negative/weak results are reported honestly.

## Reviewer Attack Points And Defenses

Attack: Detection is confused with forecasting.  
Defense: Separate tasks and report SPH/SOP definitions in every experiment.

Attack: Window-level accuracy hides class imbalance.  
Defense: Do not use accuracy as a primary metric; report event sensitivity, FAR/day, TIW, lead time, Brier, and ECE.

Attack: Leakage through random windows or normalization.  
Defense: Default patient-wise/temporal splits, purge overlaps, recording-boundary temporal split
option, audit split leakage, and record score-fit/threshold-selection scope.

Attack: Postictal periods contaminate preictal labels.  
Defense: Ictal/postictal exclusions are explicit, tested, and audited.

Attack: Edge sensors hallucinate EEG-only information.  
Defense: Edge student learns observable/shared latent representations and exposes uncertainty/abstention.

Attack: Synthetic/demo results are overstated.  
Defense: Synthetic/mock outputs are labeled as software checks only.

## Current Readiness

As of 2026-05-15:

- Software scaffold: strong.
- Mock SeizeIT2/MSG pathways: working.
- Real SeizeIT2 local integration: single-subject pipeline check produced labels/reports; not a cohort result.
- Real MSG local integration: full Zenodo file list downloaded and parsed; 510 / 768 onsets are matched
  to downloaded wearable segments; labels, random baseline, HR-rule baseline, and split audits exist.
- A split-safe hour-of-day cycle baseline now exists and uses validation-only thresholding, but the
  current unaudited temporal-test check has low event sensitivity.
- A recording-boundary temporal split now exists for MSG and the local audit reports no recording
  overlap or temporal overlap across train/validation/test.
- A split-aware HR tachycardia pipeline check now fits score statistics on train, selects threshold
  on validation, and reports on test only. Its local numbers are audit signals only, not paper
  results, because event matching, seizure timelines, cluster handling, and normalization policy
  are not manually cleared.
- Clinical result claims: not allowed yet.
- A100 training: not cleared.
- Next blocker: manual audit of 5-10 seizure timelines per dataset and correction of any parser/label issues.

## Bottom Line

This can become a major scientific contribution if the real-data audits validate the benchmark and
the final experiments expose meaningful forecastability/observability structure. As of this snapshot,
the contribution is not yet "without doubt" scientifically proven; the defensible claim is a rigorous
open benchmark pipeline with local public-data audit artifacts. The clinical/scientific impact claim
must wait for manual label audit, frozen splits, validation-only thresholding, leakage-checked feature
normalization, and final baseline tables.
