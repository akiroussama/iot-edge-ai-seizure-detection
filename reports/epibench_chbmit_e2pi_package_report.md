# CHB-MIT EpiBench E2-PI Package Report

Date: 2026-05-24  
Package: `examples/epibench/chbmit_patient_independent_d/`  
Track: `D` seizure detection  
Dataset: CHB-MIT Scalp EEG Database v1.0.0, PhysioNet DOI `10.13026/C2K01R`

## Result

The CHB-MIT package now provides the first real patient-independent EpiBench `E2-PI` evidence package in this repository.

Certification output:

- final claim: `E2-PI`;
- effective dataset tier: `T1`;
- Epi-Score: `3.186`;
- floor penalty: `true`;
- badges: `EpiBench-Dataset-T1`, `EpiBench-Run-Complete`, `EpiBench-Failure-Transparent`, `EpiBench-Claim-E2-PI`, `EpiBench-Leakage-Checked`;
- forbidden phrases: `real-time`, `on-device`, `edge-ready`;
- blockers: none.

## What This Proves

This proves that EpiBench can wrap a real public EEG seizure dataset into a patient-independent, auditable claim-gated result bundle.

It does not prove that the model is useful. The model is intentionally `always_negative`, so the result is a null-baseline control:

- event sensitivity: `0.0`;
- false alarms per 24h: `0.0`;
- event F1: `0.0`;
- test events: `106`;
- test monitoring hours: `155.306`.

The correct interpretation is:

> The experimental evidence structure can support an `E2-PI` patient-independent performance statement, but the measured baseline performance is scientifically poor and has no clinical utility.

## Why This Is Still Valuable

This package closes a methodological gap that reviewers would otherwise attack:

- it uses a real public EEG dataset;
- it uses official PhysioNet provenance;
- it uses onset and offset annotations;
- it explicitly separates train, validation, and test subjects;
- it keeps `chb01` and `chb21` in the same split because PhysioNet documents that they are the same subject;
- it produces machine-validated Dataset Card, Split Manifest, Failure Trace, Result Bundle, and Claim Report.

## Why This Is Not Enough For A Top Q1 Paper

The package is not a waveform-based EEG detector. It downloads metadata and official summary annotations, not the 42.6 GB EDF signal archive.

For a strong Q1 submission, this package should be followed by a signal-using CHB-MIT or TUSZ baseline:

- EDF subset or full archive materialization;
- native event scoring from generated predictions;
- simple EEG energy or line-length threshold baseline;
- logistic/linear baseline;
- per-patient sensitivity and false alarms/day distribution;
- worst-patient analysis;
- comparison against always-negative and rate-matched random baselines.

## Current Scientific Boundary

`EpiBench-Claim-E2-PI` in this report means:

> Patient-independent retrospective performance has been measured under EpiBench v1.0-draft evidence rules.

It does not mean:

- clinically useful;
- deployment ready;
- real-time;
- on-device;
- regulatory approved;
- state of the art.
