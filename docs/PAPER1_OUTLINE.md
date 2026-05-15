# Paper 1 outline

Working title:

**EpiTwin-Open: Forecastability-Aware Multimodal Benchmarking for Calibrated Wearable Seizure-Risk Forecasting**

## Abstract claim

We do not claim all seizures are predictable. We build a public framework that measures what is forecastable from wearable biosignals under clinically meaningful alarm budgets.

## Figures

1. Detection vs early warning vs forecasting vs long-horizon risk.
2. SPH/SOP labeling and exclusion timeline.
3. EpiTwin-Open architecture.
4. Dataset feasibility table.
5. Sensitivity vs FAR/day and Time-in-Warning.
6. Calibration curves.
7. Observability map: full modality vs edge modality.

## Tables

1. Dataset summary.
2. Baseline metrics.
3. Ablations.
4. Subgroup analysis by patient/seizure/modalities.
5. Edge modality projection.

## Reviewer attack surface

- Leakage.
- Window-level vs event-level metrics.
- Postictal contamination.
- Claims exceeding dataset capability.
- Overfitting to patient identity.

## Defensive design

- Patient-wise and temporal splits.
- Random rate-matched baseline.
- Time-in-Warning.
- Calibration.
- Uncertainty/abstention.
