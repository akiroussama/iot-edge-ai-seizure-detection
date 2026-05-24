# EpiBench Real-Evidence Progression

Generated from `reports/epibench_evidence_panels/bundle_summary.csv`.

## Purpose

This panel separates real-data progress from protocol demonstrations. It is intentionally conservative:
real packages are not promoted because they use public data. They are interpreted through their claim,
failure state, split policy, label audit, and denominator strength.

## Summary

- Real or preliminary real-data packages tracked: `4`.
- Claim distribution among these packages: `E1=1, E2-PD=1, E2-PI=2`.
- Strongest real-data claim currently present: `E2-PI`.

## Package Interpretation

- `chbmit_patient_independent_d`: `E2-PI`; T1 patient-independent CHB-MIT structure is certified, but the model is always-negative.
- `chbmit_waveform_micro_d`: `E2-PI`; EDF-derived line-length baseline reaches structural E2-PI after train FAR-budgeted thresholding, but detects no test seizures and scores poorly.
- `msg_gate_c_frozen_f`: `E2-PD`; Frozen MSG forecasting package reaches E2-PD under denominator restrictions.
- `seizeit2_preliminary_f`: `E1`; Wearable package remains E1 because labels/split/acquisition evidence are incomplete.

## Next-Step Register

- `medium` `chbmit_patient_independent_d`: Replace null baseline with waveform-derived detector over a larger patient-independent EDF subset.
- `highest` `chbmit_waveform_micro_d`: Scale to more patients and add robust baselines before requesting operational E2-PI.
- `medium` `msg_gate_c_frozen_f`: Add patient-independent or external forecasting evidence before claiming E2-PI or E3.
- `high` `seizeit2_preliminary_f`: Complete label audit, acquisition provenance, and patient-independent split manifest.

## Boundary

This progression panel is not a claim that EpiBench has solved seizure detection. It shows, with
traceable artefacts, where the current repository has real evidence, where that evidence fails, and
which upgrade would most improve the scientific case.
