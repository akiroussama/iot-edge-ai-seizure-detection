# EpiBench Phase 1 Adjudication Examples

Date: 2026-05-24  
Status: illustrative adjudication set for Phase 1 validation  
Companion spec: `docs/EPIBENCH_SPEC_V1.md`

## Purpose

This document tests whether the Phase 1 evidence model produces stable and conservative verdicts.

The examples are deliberately schematic. They are not official certifications of CHB-MIT, TUSZ, SeizeIT2, MSG, or any other real dataset. Real certification requires a completed Evidence Card, source checks, label audit, split manifest, result bundle, and failure trace.

Each example follows the same structure:

- evidence summary;
- MTS/DSI reasoning;
- dataset tier;
- track;
- split;
- label audit;
- failures;
- requested claim;
- granted claim;
- forbidden claims;
- reason log.

## Claim ordering used in examples

```text
E0 < E1 < E2-PD < E2-PI < E3 < E4
```

E2-PD and E2-PI answer different scientific questions. E2-PD is not "bad"; it is patient-dependent. It cannot support new-patient generalization.

---

# Example A - High-quality hospital EEG, narrow domain

## Evidence summary

Archetype:

- public or institutional EEG dataset;
- raw EEG available;
- expert annotations available;
- onset and offset present;
- pediatric or single-center hospital cohort;
- adequate interictal duration;
- no home/ambulatory context;
- patient-independent split available;
- no external validation in this run.

## MTS reasoning

Expected pattern:

- strong source/version;
- clear raw signal provenance;
- good sensor metadata;
- strong onset/offset evidence;
- label uncertainty partly bounded;
- split manifest available;
- missingness and artifacts documented enough for a narrow claim.

Illustrative MTS:

```text
MTS_scaled: 84
MTS blockers: none
MTS tier candidate: T1
```

## DSI reasoning

Expected pattern:

- limited age domain;
- limited site/context domain;
- hospital-only;
- no real home wearable stress;
- possible seizure-type imbalance;
- no external dataset in this run.

Illustrative DSI:

```text
DSI_scaled: 38
DSI band: low
Domain limits:
- hospital-only
- no home deployment evidence
- no external generalization evidence
```

## Adjudication

| Field | Verdict |
| --- | --- |
| Dataset tier | T1 |
| Track | D: Detection |
| Split | patient-independent |
| Label audit | passed or pass-with-caveats |
| Failure status | transparent, no leakage |
| Requested claim | E3 |
| Granted claim | E2-PI |
| Forbidden claims | E3, E4, home deployment, real-time if hardware absent |

## Reason log

E2-PI is allowed because the dataset is T1 candidate, labels are auditable, the split is patient-independent, and failures are transparent.

E3 is blocked because there is no external dataset, leave-site-out validation, or multisite generalization evidence. Low DSI reinforces that the result is narrow, not external.

## Scientific interpretation

Allowed:

> Under EpiBench Track D, this run supports a patient-independent narrow detection claim on this hospital EEG dataset and sensor configuration.

Forbidden:

> The model generalizes to home seizure detection.

---

# Example B - Wearable multimodal dataset with useful but incomplete evidence

## Evidence summary

Archetype:

- wearable multimodal data;
- patients with focal epilepsy;
- modalities may include wearable EEG, ECG, EMG, ACC/GYR;
- source is public or controlled-access;
- annotations available but onset/offset certainty varies;
- context may be hospital/EMU or partially ambulatory;
- patient-independent split possible;
- hardware target not measured in this run.

## MTS reasoning

Illustrative MTS:

```text
MTS_scaled: 72
MTS blockers: none for E2-PD/E2-PI, T1 blocked by label uncertainty and/or incomplete device calibration
MTS tier candidate: T2
```

The dataset is useful, but not all metrological dimensions support a strong claim:

- label uncertainty may not be fully bounded;
- wearable placement may be documented but not fully stress-tested;
- missingness and artifacts may require stronger audit;
- calibration may rely on device specification rather than per-recording calibration.

## DSI reasoning

Illustrative DSI:

```text
DSI_scaled: 66
DSI band: medium
Domain limits:
- wearable stress partially represented
- not sufficient for broad home deployment unless home context is documented
- external validation absent
```

## Adjudication

| Field | Verdict |
| --- | --- |
| Dataset tier | T2 |
| Track | D or W, depending on declared task |
| Split | patient-independent |
| Label audit | required before E2-PD/E2-PI |
| Failure status | must include device missingness and prediction failures |
| Requested claim | E2-PI |
| Granted claim | E2-PI if audit passes; otherwise E1 |
| Forbidden claims | E3, E4, real-time/edge measured if no hardware report |

## Reason log

E2-PI is possible only after label audit, split compliance, FAR/day, latency definition, and failure trace are complete.

E3 is blocked because there is no external validation. Edge/real-time claims are blocked if hardware evidence is absent.

## Scientific interpretation

Allowed:

> The result supports a narrow patient-independent wearable detection claim under the declared dataset, sensor stack, and audit status.

Forbidden:

> The model is ready for real-world wearable deployment.

---

# Example C - Proxy-label exploratory dataset

## Evidence summary

Archetype:

- public or scraped physiological data;
- seizure labels derived from diary/proxy/self-report or weak metadata;
- raw-to-label mapping incomplete;
- onset/offset absent or unreliable;
- no neurologist review;
- model reports very high accuracy.

## MTS reasoning

Illustrative MTS:

```text
MTS_scaled: 44
MTS blockers:
- labels unauditable
- onset absent or proxy-only
- raw-to-canonical trace incomplete
MTS tier candidate: T3
```

## DSI reasoning

The dataset may have broad real-world variability. This does not rescue the evidence.

Illustrative DSI:

```text
DSI_scaled: 78
DSI band: high
Domain limits:
- broad but weak evidence
```

## Adjudication

| Field | Verdict |
| --- | --- |
| Dataset tier | T3 |
| Track | cannot support Track D/W E2-PD/E2-PI or higher without auditable events |
| Split | irrelevant for E2-PD/E2-PI or higher until label issue resolved |
| Label audit | failed |
| Failure status | must be reported if run exists |
| Requested claim | E2-PD/E2-PI or E3 |
| Granted claim | E1 maximum |
| Forbidden claims | E2-PD, E2-PI, E3, E4, low false positives, clinical utility |

## Reason log

High DSI does not compensate for low MTS. The dataset may be useful for software plumbing, exploratory modeling, or hypothesis generation, but not for operational seizure detection claims.

## Scientific interpretation

Allowed:

> This dataset supports E1 structural validation or exploratory analysis only.

Forbidden:

> The model detects seizures with clinically meaningful accuracy.

---

# Example D - Strong patient-dependent result

## Evidence summary

Archetype:

- T1 or T2 dataset;
- labels audited;
- threshold and calibration selected within patient;
- test split is temporal within the same patient;
- no patient-independent evaluation.

## Adjudication

| Field | Verdict |
| --- | --- |
| Dataset tier | T1/T2 |
| Track | D or F |
| Split | patient-dependent temporal |
| Label audit | passed |
| Failure status | transparent |
| Requested claim | E2-PI or E3 |
| Granted claim | E2-PD maximum |
| Forbidden claims | E2-PI, E3, new-patient generalization |

## Reason log

The result may be scientifically useful for personalization. It does not test new-patient generalization.

## Scientific interpretation

Allowed:

> This run supports a patient-dependent claim under the declared sensor and patient-specific calibration protocol.

Forbidden:

> The model generalizes to unseen patients.

---

# Example E - Leakage failure despite strong metrics

## Evidence summary

Archetype:

- T1 candidate dataset;
- strong reported sensitivity and FAR/day;
- later audit detects patient overlap, temporal overlap, normalization leakage, or threshold selection on test data.

## Adjudication

| Field | Verdict |
| --- | --- |
| Dataset tier | may remain T1 |
| Track | any |
| Split | noncompliant |
| Label audit | may pass |
| Failure status | critical leakage |
| Requested claim | E2-PD/E2-PI or E3 |
| Granted claim | E1 maximum |
| Forbidden claims | E2-PD, E2-PI, E3, E4, SOTA |

## Reason log

Leakage invalidates the performance claim. Dataset quality does not rescue a noncompliant run.

## Scientific interpretation

Allowed:

> The run demonstrates a failure mode and should be reported as a leakage failure trace.

Forbidden:

> The leaked metrics show model superiority.

---

# Example F - Real-time claim without hardware evidence

## Evidence summary

Archetype:

- valid Track D detection run;
- event metrics are complete;
- model authors claim real-time or edge readiness;
- no target hardware latency, memory, or energy report.

## Adjudication

| Field | Verdict |
| --- | --- |
| Dataset tier | T1/T2 possible |
| Track | D, but not E |
| Split | according to manifest |
| Label audit | according to audit |
| Failure status | hardware evidence missing |
| Requested claim | E2-PI + real-time edge |
| Granted claim | non-edge claim only, e.g. E2-PI if other gates pass |
| Forbidden claims | real-time, Edge-Measured, Streaming-Feasible |

## Reason log

Hardware evidence is not required for all scientific claims, but it is required for edge and real-time claims.

## Scientific interpretation

Allowed:

> This run may support a non-edge detection claim under EpiBench Track D.

Forbidden:

> This model is real-time on IoT hardware.

---

# Inter-reviewer reproducibility exercise

## Procedure

1. Provide reviewers with one Evidence Card and one result summary.
2. Reviewers independently assign MTS item scores.
3. Reviewers independently assign DSI item scores.
4. Reviewers determine dataset tier.
5. Reviewers determine granted claim and forbidden claims.
6. Differences are adjudicated.

## Pass thresholds

| Output | Pass threshold |
| --- | --- |
| MTS_scaled | reviewer difference <= 5 points |
| DSI_scaled | reviewer difference <= 8 points |
| dataset tier | exact agreement |
| granted claim | exact agreement |
| blocking reasons | same critical blockers |

## Adjudication log template

```text
Example ID:
Reviewer A MTS:
Reviewer B MTS:
Difference:
Reviewer A DSI:
Reviewer B DSI:
Difference:
Tier A:
Tier B:
Claim A:
Claim B:
Disagreement:
Resolution:
Spec change needed: yes/no
```

## Closeout rule

If reviewers cannot reach exact agreement on dataset tier and granted claim after reading the spec, Phase 1 is not ready for Phase 2 encoding.
