# EpiBench Real Evidence Gap Report

Date: 2026-05-24  
Scope: local EpiBench v1.0-draft evidence packages and Q1 submission readiness gate.

## Executive Result

The MSG Gate C frozen forecasting package is now a real, generated EpiBench evidence package rather than a preliminary demonstration. It certifies as:

- final claim: `E2-PD`;
- effective dataset tier: `T2`;
- Epi-Score: `58.984`;
- badges: `EpiBench-Dataset-T2`, `EpiBench-Run-Complete`, `EpiBench-Failure-Transparent`, `EpiBench-Claim-E2-PD`, `EpiBench-Leakage-Checked`;
- blocking failures: none.

This is scientifically useful but not sufficient for a highly selective Q1 submission by itself. A CHB-MIT metadata-based patient-independent EEG package has now been added and reaches `E2-PI`, but it is an intentionally poor always-negative null baseline. The repository now has a machine-valid `E2-PI` evidence structure; the next scientific gap is a signal-using EEG baseline with non-trivial detection performance.

## Current Package Status

| Package | Track | Final claim | Effective tier | Submission-grade | Main limitation |
| --- | --- | --- | --- | --- | --- |
| `chbmit_patient_independent_d` | `D` | `E2-PI` | `T1` | yes | metadata-only always-negative null baseline; no clinical utility |
| `msg_gate_c_frozen_f` | `F` | `E2-PD` | `T2` | yes | temporal within-patient forecasting; no patient-independent claim |
| `msg_preliminary_f` | `F` | `E1` | `T3` | no | label audit and missing MTS core evidence |
| `seizeit2_preliminary_f` | `F` | `E1` | `T3` | no | single subject, two events, synthetic/demo split, label audit absent |

## Readiness Gate Outcome

Machine report: `reports/epibench_submission_readiness_result.json`.

Gate result after adding CHB-MIT and MSG Gate C:

- status: `passed`;
- submission-grade packages: `2 / 2`;
- operational packages at `E2-PI` or higher: `1 / 1`.

This pass is a structural gate pass, not a clinical-utility pass. The CHB-MIT result is `E2-PI` because the evaluation is patient-independent, not because the always-negative baseline is useful.

## Why The MSG Package Stops At E2-PD

The limiting ceiling is not the metric value and not a hidden crash. The limiting ceiling is the experimental design:

- dataset tier ceiling: `E2-PI`;
- label audit ceiling: `E2-PI`;
- leakage audit ceiling: `E4`;
- failure status ceiling: `E4`;
- split-policy ceiling: `E2-PD`.

Therefore the final claim is `E2-PD`. This is the intended fail-closed behavior of EpiBench.

## Minimum Next Work For Q1 Submission

### Required Package A: EEG Detection, Patient-Independent

Preferred route:

- TUSZ if access and event scoring are ready;
- CHB-MIT if speed and clean reproducibility matter more than scale.

Definition of done:

- Track `D`;
- patient-independent or leave-one-subject-out split;
- event-based sensitivity, false alarms per 24h, event F1, latency, and per-patient distribution;
- always-negative, rate-matched random, simple EEG energy threshold, and one small model baseline;
- failure trace with leakage, missing prediction, NaN, FAR explosion, and post-event alarm checks;
- claim report at least `E2-PI` if label audit permits.

### Required Package B: Wearable Detection Or Multimodal Detection

Preferred route:

- full SeizeIT2 or a documented multi-subject subset that passes the cohort readiness gate.

Definition of done:

- Track `D` before attempting Track `F`;
- multiple patients and enough events for the readiness gate;
- patient-independent split;
- missing modality and artifact report;
- false alarm burden per 24h;
- no home-IoT generalization if the evidence remains hospital-only.

### Required External Review

Before submission:

- one clinical reviewer must review claim ladder, false alarm wording, label categories, and anti-overclaim language;
- one benchmark/methods reviewer must independently score at least two Dataset Evidence Cards;
- the inter-reviewer report must show agreement on final claim ceiling or document adjudication.

## Submission Boundary

Do not submit to a top Q1 venue while the readiness gate remains failed. The current package set is scientifically stronger than the original draft, but it still supports a methods paper in progress, not a mature community standard paper.

The next decisive milestone is not another narrative section. It is a waveform-based EEG package that keeps the `E2-PI` evidence structure but replaces the null baseline with at least one non-trivial signal-derived baseline.
