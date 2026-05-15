# SOTA Review Snapshot - Wearable Seizure Forecasting

Date checked: 2026-05-15

This is a working SOTA snapshot for EpiTwin-Open. It is not a systematic review. It records the current evidence base used to frame the first paper and must be refreshed before submission.

## Sources Checked

1. SeizeIT2 dataset paper  
   https://www.nature.com/articles/s41597-025-05580-x

2. My Seizure Gauge Long-term Wearable Data  
   https://zenodo.org/records/17380899

3. Forecasting epileptic seizures with wearable devices: A hybrid short- and long-horizon pseudo-prospective approach  
   https://doi.org/10.1111/epi.18466

4. Comparison between epileptic seizure prediction and forecasting based on machine learning  
   https://www.nature.com/articles/s41598-024-56019-z

5. Automated algorithms for seizure forecast: a systematic review and meta-analysis  
   https://link.springer.com/article/10.1007/s00415-024-12655-z

6. Seizure forecasting with ultra long-term EEG signals  
   https://www.sciencedirect.com/science/article/pii/S1388245724002761

7. The present and future of seizure detection, prediction, and forecasting with machine learning  
   https://www.frontiersin.org/journals/neurology/articles/10.3389/fneur.2024.1425490/full

8. PaPaGei: Open Foundation Models for Optical Physiological Signals  
   https://github.com/Nokia-Bell-Labs/papagei-foundation-model

9. Large-scale Training of Foundation Models for Wearable Biosignals  
   https://iclr.cc/virtual/2024/poster/17787

10. Circadian Phase Locking of Epilepsy Seizures in Wearable Data  
    https://arxiv.org/abs/2604.18297

11. ECG-Based Detection of Epileptic Seizures in Real-World Wearable Settings: Insights from the
    SeizeIT2 Dataset  
    https://www.mdpi.com/1424-8220/25/24/7687

12. SeizureFormer: A Multi-Scale Transformer for Seizure Risk Forecasting from RNS-Derived
    Biomarkers  
    https://psb.stanford.edu/psb-online/proceedings/psb26/abstracts/2026_p85.html

## Current Evidence

SeizeIT2 is a key public wearable focal epilepsy dataset. The Scientific Data article describes it
as the first and largest public phase 3 clinical study containing multimodal wearable bte-EEG, ECG,
EMG, ACC, and GYR data from focal epilepsy patients. The paper is explicit that the main objective
is automated focal seizure detection in continuous wearable data and that the hospital recording
environment does not fully mimic daily life. This supports using SeizeIT2 for multimodal observability,
detection/early-warning baselines, and short-horizon exploration, but not for overclaiming long-term
forecasting.

My Seizure Gauge is a longitudinal wearable dataset. Zenodo describes 11 participants, wrist-worn
heart-rate and step-count data, EEG-confirmed seizures, and an average recording duration of 337
days. The local full-download parser currently finds 768 seizure onsets and 510 onsets matched to
downloaded wearable segments; this count is a local parser artifact requiring manual audit, not a
published dataset statistic.

Recent wearable forecasting work has moved beyond short hospital recordings. Nasseri et al.
(Epilepsia 2025, DOI 10.1111/epi.18466) report ultra-long-term non-invasive wearable forecasting
using heart rate and step count with EEG-confirmed seizures, including hybrid short-horizon and
long-horizon systems. This is direct competition. EpiTwin-Open therefore should not claim novelty as
"first wearable seizure forecasting"; the defensible novelty is open, leakage-safe, reproducible
benchmarking and forecastability/observability analysis on public data.

The 2024 Scientific Reports paper explicitly contrasts seizure prediction and seizure forecasting. It argues that forecasting is probabilistic risk assessment rather than a crisp alarm-only preictal detector, and reports improved forecasting behavior over prediction in an EEG cohort.

The 2024 Journal of Neurology systematic review/meta-analysis reports severe heterogeneity in
datasets, horizons, train/test strategies, and metrics. It reports an overall AUC around 0.71 and Brier
Skill Score around 0.13 across eligible studies, while emphasizing probabilistic metrics, explicit
forecast horizons, and pseudo-prospective evaluation. This strongly supports EpiTwin-Open's focus on
calibration, Brier/ECE, Time-in-Warning, FAR/day, and leakage audits.

The 2024 Frontiers review emphasizes unseen-data validation and clinically relevant evaluation dimensions such as sensitivity, false positives, and data deficiency. It also notes that wearable/non-EEG seizure technologies can suffer false positives from everyday activity and that multimodal sensing can help.

Foundation models for wearable biosignals are active but not seizure-forecasting-specific. ICLR 2024
wearable biosignal foundation-model work used large-scale Apple Heart and Movement Study PPG/ECG
data. PaPaGei reports an open PPG foundation model trained on more than 57,000 hours of public PPG
data. These support the long-term foundation-model direction but do not remove the need for
epilepsy-specific leakage-safe forecasting benchmarks.

Recent SeizeIT2 follow-up work includes ECG-based seizure detection benchmarking on the public
dataset. This reinforces the detection/forecasting separation: SeizeIT2 is already useful for
wearable seizure detection baselines, while EpiTwin-Open must justify any forecasting experiments
with explicit SPH/SOP horizons, postictal exclusions, and alarm burden metrics.

SeizureFormer (PSB 2026) reports long-horizon seizure risk forecasting from RNS-derived biomarkers,
not non-invasive public wearable HR/steps data. It is important SOTA for seizure forecasting models
and long-horizon risk framing, but it does not replace the need for open wearable benchmark
infrastructure because its inputs are implant-derived biomarkers from a small patient set.

The 2026 circadian phase-locking arXiv preprint uses single-patient wearable IBI and seizure diary
data to test whether seizure onsets align with physiological circadian phase. It supports including
cycle/phase baselines and interpretable rhythm features, while also emphasizing that single-patient
wearable findings need multi-patient validation.

## Gap Assessment

The strongest defensible gap is not "a new large model predicts seizures." The gap is:

- public, leakage-safe, clinically constrained benchmarking for wearable seizure-risk forecasting;
- explicit separation of detection, early warning, short-horizon forecasting, and long-horizon forecasting;
- calibration and alarm burden reporting;
- modality/observability analysis across full wearable modalities and reduced edge modalities;
- open reproduction of public-data baselines, including negative/weak baselines, before foundation-model scaling.

## Major-Contribution Test

EpiTwin-Open can be a major contribution if the real-data experiments demonstrate all of the following:

- correct public dataset parsing for SeizeIT2 and My Seizure Gauge;
- leakage-safe labels and splits verified by human timeline audit;
- event-level metrics reported with FAR/day and Time-in-Warning;
- baselines that include random rate-matched and cycle/rhythm models;
- calibrated threshold selection on validation data only;
- fit/normalization metadata showing that test windows were not used to compute feature statistics;
- observability analysis showing what is and is not forecastable from each modality set;
- transparent negative results when a horizon or modality is not forecastable.

Without real-data validation, it is only a strong benchmark infrastructure proposal, not proven clinical science.

## Claims Allowed Now

- EpiTwin-Open implements a leakage-safe open benchmark scaffold.
- EpiTwin-Open operationalizes SPH/SOP labeling and clinical alarm metrics.
- EpiTwin-Open is designed to test forecastability rather than assume all seizures are predictable.
- EpiTwin-Open has produced local public-data pipeline checks for SeizeIT2 and MSG that are ready
  for manual audit.

## Claims Not Allowed Yet

- Any numeric clinical performance claim.
- Any claim that public wearable signals reliably predict all focal seizures.
- Any claim that EpiTwin-Open is the first wearable seizure-forecasting system.
- Any claim of clinical deployment readiness.
- Any edge/TinyML hardware claim.
- Any claim that one backbone family is biologically superior.
