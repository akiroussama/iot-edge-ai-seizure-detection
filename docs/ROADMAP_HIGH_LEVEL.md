# EpiTwin-Open high-level roadmap

## Scientific thesis

Move from reactive seizure detection to proactive, calibrated, patient-aware seizure-risk estimation. The core contribution is not another backbone; it is a forecastability-aware framework that measures what is observable from public wearables under clinical alarm budgets.

## Paper 1 — EpiBench-Forecast / EpiTwin-Open

Goal: a leakage-safe public benchmark and first calibrated risk model.

Deliverables:
- SeizeIT2 and My Seizure Gauge canonical tables.
- SPH/SOP labels.
- Ictal/postictal exclusion.
- Patient-wise, temporal, and center-wise splits.
- Metrics: event sensitivity, FAR/day, Time-in-Warning, lead time, Brier, ECE.
- Baselines: random rate-matched, HR/ECG rules, ACC/EMG energy, TCN-small.
- First EpiTwin-SSL ablation.

Forbidden claims:
- No TinyML/edge performance claim without RAM, latency, and energy evidence.
- No >90% / <0.1 FAR/day hero claim.
- No “all focal seizures are predictable”.

## Paper 2 — Predictive-coding foundation model

Goal: multimodal SSL foundation model for latent seizure-susceptibility state.

Core experiments:
- Masked multimodal modeling.
- Future latent prediction.
- Cross-modal predictive coding.
- Hazard/survival head.
- Mamba-2, TCN, Transformer, CfC/LTC, hybrid ablations.

## Paper 3 — Edge observable student

Goal: compress the observable latent to ECG+ACC or HR+steps.

Core experiments:
- Observable-latent distillation.
- Uncertainty/abstention.
- Quantization-aware training.
- Tiny GRU/TCN/SSM/CfC/SNN-gate comparisons.
- RAM/Flash/latency/energy proxy.

## Paper 4 — Prospective IoT validation

Goal: cross-placement adaptation and real wearable validation.

Requires:
- Wrist/tibia IMU.
- ECG patch or PPG/EDA.
- Clinical reference/annotation.
- IRB/ethics.
- Prospective patient-specific calibration.
