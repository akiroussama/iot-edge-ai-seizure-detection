# CHB-MIT Waveform Micro EpiBench Package Report

Date: 2026-05-24
Package: `examples/epibench/chbmit_waveform_micro_d/`
Track: `D` seizure detection
Model: 5-second robust line-length threshold baseline

## Result

- final claim: `E1`;
- Epi-Score: `3.079`;
- test events: `2`;
- event sensitivity: `0.0`;
- false alarms per 24h: `311.480865`;
- event F1: `0.0`;
- median latency seconds: `None`;
- p95 latency seconds: `None`.

## Scientific Interpretation

This is the first CHB-MIT EpiBench package in this repository that reads EDF waveform samples and
derives predictions from signal features. It is deliberately a micro-subset smoke result, not a full
CHB-MIT benchmark and not submission-grade evidence by itself.

## Boundary

The result demonstrates that EpiBench can certify a waveform-derived patient-independent EEG
baseline. It does not demonstrate clinical usefulness, real-time operation, on-device viability,
regulatory approval, or generalization beyond the selected CHB-MIT subset.
