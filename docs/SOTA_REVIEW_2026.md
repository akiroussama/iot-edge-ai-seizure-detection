# SOTA Review Snapshot - Wearable Seizure Forecasting

Date checked: 2026-05-15

This is a working SOTA snapshot for EpiTwin-Open. It is not a systematic review. It records the current evidence base used to frame the first paper and must be refreshed before submission.

## Sources Checked

1. SeizeIT2 dataset paper/preprint  
   https://arxiv.org/abs/2502.01224

2. My Seizure Gauge Long-term Wearable Data  
   https://zenodo.org/records/17380899

3. Forecasting epileptic seizures with wearable devices: hybrid short- and long-horizon pseudo-prospective approach  
   https://seermedical.com/research/forecasting-epileptic-seizures-with-wearable-devices/

4. Comparison between epileptic seizure prediction and forecasting based on machine learning  
   https://www.nature.com/articles/s41598-024-56019-z

5. Seizure forecasting based on AI-supported analysis of multidien and circadian cycles in EEG and non-EEG long-term datasets  
   https://link.springer.com/article/10.1007/s10309-024-00709-1

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

## Current Evidence

SeizeIT2 is a key public wearable focal epilepsy dataset. The arXiv record states that it contains more than 11,000 hours of multimodal wearable data, including behind-the-ear EEG, ECG, EMG, accelerometer, and gyroscope, with 886 focal seizures from 125 patients across five European monitoring centers. The same record states that it is available on OpenNeuro in BIDS format.

My Seizure Gauge is a longitudinal wearable dataset. Zenodo describes 11 participants, heart rate and step count from wrist devices, EEG-confirmed seizures, and an average recording duration of 337 days.

Recent wearable forecasting work has moved beyond short hospital recordings. The Seer/Epilepsia summary reports ultra-long-term non-invasive wearable forecasting using heart rate and step count, with EEG-confirmed seizures and both short- and long-horizon models. This is directly relevant competition and a benchmark for framing.

The 2024 Scientific Reports paper explicitly contrasts seizure prediction and seizure forecasting. It argues that forecasting is probabilistic risk assessment rather than a crisp alarm-only preictal detector, and reports improved forecasting behavior over prediction in an EEG cohort.

Recent reviews emphasize that long-term seizure risk is shaped by circadian and multidien cycles, and that wearable autonomic/movement signals are promising but not yet clinically settled. The Springer review explicitly states that clinical utility remains to be determined for wearable-based forecasts.

The 2024 Frontiers review emphasizes unseen-data validation and clinically relevant evaluation dimensions such as sensitivity, false positives, and data deficiency. It also notes that wearable/non-EEG seizure technologies can suffer false positives from everyday activity and that multimodal sensing can help.

Foundation models for wearable biosignals are active but not seizure-forecasting-specific. PaPaGei and ICLR 2024 wearable biosignal foundation-model work support the direction of self-supervised multimodal biosignal learning, but they do not solve seizure-risk forecasting from public epilepsy wearables.

## Gap Assessment

The strongest defensible gap is not "a new large model predicts seizures." The gap is:

- public, leakage-safe, clinically constrained benchmarking for wearable seizure-risk forecasting;
- explicit separation of detection, early warning, short-horizon forecasting, and long-horizon forecasting;
- calibration and alarm burden reporting;
- modality/observability analysis across full wearable modalities and reduced edge modalities;
- an open pipeline that can compare random, cycle, rule-based, classical ML, and small deep baselines before foundation-model scaling.

## Major-Contribution Test

EpiTwin-Open can be a major contribution if the real-data experiments demonstrate all of the following:

- correct public dataset parsing for SeizeIT2 and My Seizure Gauge;
- leakage-safe labels and splits verified by human timeline audit;
- event-level metrics reported with FAR/day and Time-in-Warning;
- baselines that include random rate-matched and cycle/rhythm models;
- calibrated threshold selection on validation data only;
- observability analysis showing what is and is not forecastable from each modality set;
- transparent negative results when a horizon or modality is not forecastable.

Without real-data validation, it is only a strong benchmark infrastructure proposal, not proven clinical science.

## Claims Allowed Now

- EpiTwin-Open implements a leakage-safe open benchmark scaffold.
- EpiTwin-Open operationalizes SPH/SOP labeling and clinical alarm metrics.
- EpiTwin-Open is designed to test forecastability rather than assume all seizures are predictable.

## Claims Not Allowed Yet

- Any numeric clinical performance claim.
- Any claim that public wearable signals reliably predict all focal seizures.
- Any claim of clinical deployment readiness.
- Any edge/TinyML hardware claim.
- Any claim that one backbone family is biologically superior.
