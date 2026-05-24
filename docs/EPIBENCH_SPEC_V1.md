# EpiBench Spec v1.0-draft

Status: v1.0-draft normative specification with executable release-candidate artefacts  
Date: 2026-05-24  
Purpose: define the evidence, track, dataset-tier, failure, and claim model encoded in YAML, JSON Schemas, and the `epibench` reference CLI.  
Scope: seizure detection, early warning, forecasting, and embedded viability for epilepsy-related AI systems.  

## 1. Normative status

This document is the normative specification for EpiBench v1.0-draft.

It defines:

- the evidence model;
- the MTS and DSI rubrics;
- the dataset tiers;
- the tracks;
- the claim ladder;
- the claim ceiling rules;
- the failure consequence rules;
- the minimum review and validation requirements before release candidate publication.

The executable release-candidate artefacts are:

- `configs/epibench/epibench_v1.yaml`;
- `schemas/epibench/*.schema.json`;
- `configs/epibench/sota_registry_v1.yaml`;
- `src/epibench/*`;
- `scripts/epibench.py`.

If prose and machine-readable artefacts diverge, the release process must block until the inconsistency is resolved. No author may choose the higher-claim interpretation manually.

## 2. Certification boundary

EpiBench certification is scientific certification of an evidence package. It is not clinical approval, regulatory approval, safety certification, or medical-device certification.

Allowed wording:

- "scientifically certified under EpiBench v1.0";
- "eligible for EpiBench Claim E2-PI under the declared track";
- "result bundle passed EpiBench evidence checks";
- "claim limited to this dataset, track, sensor stack, split, and failure profile".

Forbidden wording:

- "clinically certified";
- "clinically approved";
- "safe for clinical deployment";
- "detects epilepsy";
- "generalizable" without E3 evidence;
- "real-time" without hardware or streaming latency evidence;
- "low false positives" without false alarms per 24h and patient-level distribution.

## 3. Normative language

EpiBench uses the following language:

| Term | Meaning |
| --- | --- |
| MUST | mandatory for certification |
| MUST NOT | prohibited for certification |
| SHOULD | strongly recommended; deviations must be justified |
| MAY | optional |
| FAIL-CLOSED | missing or invalid evidence lowers or blocks a claim |
| CLAIM CEILING | maximum claim allowed by the weakest evidence component |
| TRACK | task family with its own outputs, metrics, and claim semantics |
| SENTINEL | named failure condition that must be preserved in the result bundle |
| RESULT BUNDLE | complete auditable package for one evaluated run |

EpiBench follows a conservative rule:

> When evidence is missing, contradictory, or unauditable, the claim is lowered rather than inferred upward.

## 4. Evidence architecture

EpiBench separates four evidence layers:

1. Dataset evidence: what the dataset can prove.
2. Protocol validity: whether labels, splits, thresholds, and leakage checks are valid.
3. Algorithm behavior: what the model does under the declared track.
4. Claim eligibility: what the evidence package is allowed to claim.

A leaderboard row MUST NOT be interpreted without its evidence card, split manifest, failure trace, and claim eligibility report.

## 5. SOTA alignment and non-reinvention rule

EpiBench MUST NOT reinvent existing validated evaluation or reporting machinery without a documented gap.

Before adding a new metric, checklist item, claim rule, or reporting field, the spec MUST classify the relationship to existing work as one of:

| Relationship | Meaning |
| --- | --- |
| ADOPT | EpiBench directly uses the existing rule or metric |
| MAP | EpiBench accepts the existing output and maps it into an EpiBench field |
| EXTEND | EpiBench adds evidence or claim semantics not covered by the existing work |
| DIVERGE | EpiBench deliberately differs, with a written rationale |

### 5.1 Existing work to reuse or map

| Source | EpiBench position |
| --- | --- |
| ILAE seizure classification | ADOPT for seizure-type vocabulary whenever dataset metadata permit |
| SzCORE / event-based seizure scoring | ADOPT or MAP for event-based seizure detection metrics where compatible |
| TUSZ / Temple EEG evaluation tooling | MAP as important EEG detection benchmark context and scoring precedent |
| CHB-MIT, TUSZ, SeizeIT2, MSG | MAP as pilot datasets/evidence-card targets, not as automatic claim evidence |
| TRIPOD+AI | ADOPT reporting principles for model development/validation transparency |
| STARD-AI | ADOPT reporting principles when the task is diagnostic/detection accuracy |
| DECIDE-AI | MAP for early-stage clinical evaluation language if live/clinical workflow studies are later attempted |
| SPIRIT-AI / CONSORT-AI | MAP for prospective trial protocol/reporting requirements; not required for retrospective benchmark-only claims |
| FUTURE-AI | MAP for trustworthy/deployable AI principles: fairness, universality, traceability, usability, robustness, explainability |
| FDA Clinical Decision Support guidance | MAP for regulatory humility around signal analysis and time-critical alert claims |

### 5.2 What EpiBench adds

EpiBench is justified only where it adds a missing evidence layer:

- dataset evidence cards for seizure AI;
- MTS/DSI separation;
- claim ceilings and E0/E1/E2-PD/E2-PI/E3/E4 eligibility;
- failure-preserving result interpretation;
- IoT/embedded viability gates;
- result bundles with checksums, traces, and reproducibility commands;
- anti-overclaim rules linking data quality, split type, failures, external validation, and hardware evidence.

EpiBench MUST NOT claim to replace event-scoring frameworks. It should be positioned as an evidence and claim-governance layer that can consume event-scoring outputs.

### 5.3 SOTA registry requirement

Every EpiBench release candidate MUST include a SOTA registry with:

- source title;
- URL or DOI;
- publication year;
- category: dataset, scoring framework, reporting guideline, regulatory guidance, model baseline, or clinical standard;
- relationship: ADOPT, MAP, EXTEND, or DIVERGE;
- exact EpiBench field or rule affected;
- citation integrity status;
- date verified.

If citation integrity is not verified, the source MUST NOT be used to justify a normative rule.

## 6. Tracks

Every result bundle MUST declare exactly one primary track. A model MAY be evaluated on multiple tracks, but each track requires a separate verdict.

| Track | Name | Scientific question | Primary unit | Primary outputs |
| --- | --- | --- | --- | --- |
| D | Detection | Does the system detect an ongoing or near-onset seizure event? | seizure event | event detections, alarm episodes, latency |
| W | Early warning | Does the system raise a useful alarm before a clinically defined deadline? | warning episode | alarm episodes, lead time, warning burden |
| F | Forecasting | Does the system estimate future seizure risk over a prespecified horizon? | time window / risk interval | calibrated risk, SPH/SOP labels, warning policy |
| E | Embedded viability | Can the system run under declared IoT constraints? | deployment profile | latency, RAM, CPU, energy, storage, connectivity |

### 6.1 Track D: Detection

Required definitions:

- seizure event source;
- event matching rule;
- detection deadline;
- alarm refractory period;
- latency definition;
- false alarm episode definition.

Primary metrics:

- event-based sensitivity;
- false alarms per 24h;
- detection latency median and p95;
- event precision and event F1;
- missed seizure count;
- per-patient distribution;
- failure rate.

Forbidden interpretations:

- A Track D result MUST NOT be called early warning unless useful lead time is defined and positive.
- A Track D result MUST NOT be called forecasting unless SPH/SOP or another prospective risk horizon is declared.

### 6.2 Track W: Early warning

Required definitions:

- clinically useful warning window;
- minimum useful lead time;
- maximum tolerated warning burden;
- alarm refractory period;
- event matching rule.

Primary metrics:

- useful warning sensitivity;
- false warnings per 24h;
- useful lead time median and p95;
- time-in-warning;
- missed useful warning count;
- per-patient distribution.

Forbidden interpretations:

- A warning after onset MUST NOT count as successful early warning.
- A high sensitivity result MUST NOT be considered useful if warning burden exceeds the preregistered budget.

### 6.3 Track F: Forecasting

Required definitions:

- SPH;
- SOP;
- right-censoring policy;
- ictal exclusion;
- postictal exclusion;
- alarm policy;
- calibration policy.

Primary metrics:

- event sensitivity under alarm budget;
- false alarms per 24h;
- time-in-warning;
- lead time or warning horizon coverage;
- Brier score;
- expected calibration error;
- right-censoring rate;
- missing/failure rate.

Forbidden interpretations:

- A Track F result MUST NOT be presented as seizure onset detection unless event detection outputs are evaluated separately.
- A preictal/interictal classifier MUST NOT be accepted without SPH/SOP, censoring, and postictal policy.

### 6.4 Track E: Embedded viability

Required definitions:

- hardware target or profiling environment;
- streaming causality;
- window size and stride;
- memory budget;
- latency budget;
- energy proxy or measured energy;
- connectivity dependency.

Primary metrics:

- p50/p95 inference time;
- end-to-end streaming latency;
- RAM;
- CPU;
- storage;
- battery or energy proxy;
- missing modality behavior;
- cloud dependency.

Forbidden interpretations:

- A system MUST NOT claim real-time or edge viability from desktop-only inference unless labelled as a proxy profile.
- `Edge-Measured` requires target hardware measurement.

## 7. MTS: Metrological Trustworthiness Score

MTS measures dataset measurement trustworthiness. It does not measure model performance or domain breadth.

Each item is scored 0 to 3:

| Score | Meaning |
| --- | --- |
| 0 | absent, contradictory, unauditable, or not documented |
| 1 | present but weak, inferred, incomplete, or not reproducible |
| 2 | documented and usable, but limited for strong claims |
| 3 | complete, traceable, versioned, auditable, and fit for the declared claim |

MTS is computed as:

```text
MTS_raw = sum(item_scores)
MTS_max = 3 * number_of_items
MTS_scaled = 100 * MTS_raw / MTS_max
```

Fail-closed rules override the numeric score.

### 7.1 MTS rubric

| ID | Item | 0 | 1 | 2 | 3 | Evidence required | Fail-closed effect |
| --- | --- | --- | --- | --- | --- | --- | --- |
| MTS-01 | Official source and stable version | no source or unverifiable copy | source named but version unclear | stable source and version partly documented | official or archival source, stable version, citation/DOI or release ID | source URL, DOI/release, access date | no public source blocks public certification |
| MTS-02 | License and access terms | absent or contradictory | informal or unclear terms | documented but restrictive/ambiguous for redistribution | clear license/access terms compatible with audit | license file, dataset terms | unclear license blocks public result bundle release |
| MTS-03 | Raw signal traceability | processed-only and no provenance | partial provenance or inferred pipeline | raw or processed with documented transform gaps | raw available or full raw-to-canonical trace with checksums | raw manifest, transform log, checksums | no traceability blocks T1 |
| MTS-04 | Checksums and provenance | none | partial checksums | checksums for major files only | complete checksums for raw and processed artifacts | checksum manifests | missing checksums blocks reproducibility badge |
| MTS-05 | Acquisition protocol | absent | high-level description only | protocol documented with missing details | acquisition protocol complete, including context and devices | protocol paper, data dictionary | absent protocol blocks T1 |
| MTS-06 | Sensor modality and placement | unknown | modality known, placement unclear | modality and placement mostly documented | modality, placement, channel/device mapping fully documented | sensor metadata | unknown sensor blocks track-specific claims |
| MTS-07 | Sampling rate and resolution | unknown | nominal but not per-channel | documented with some uncertainty | per-channel/device sampling rate and resolution documented | headers, metadata | unknown sampling blocks latency-sensitive claims |
| MTS-08 | Time synchronization | unknown | assumed but not documented | documented with uncertainty | synchronization method and uncertainty documented | clock/sync metadata | unknown sync blocks multimodal timing claims |
| MTS-09 | Calibration or device specification | absent | device named only | device spec known but calibration absent | calibration or validated device specification available | calibration/spec sheet | absent calibration blocks strong metrological claim |
| MTS-10 | Annotator qualification | unknown | non-expert or automatic only | expert or clinical review documented but not adjudicated | neurologist/expert adjudicated or video-EEG confirmed | annotation protocol | unknown annotator blocks E2-PD/E2-PI or higher |
| MTS-11 | Onset availability | absent | proxy or imputed onset | onset available but uncertainty not bounded | onset source traceable and uncertainty bounded | annotation file, audit sheet | absent onset blocks Track D/W E2-PD/E2-PI or higher |
| MTS-12 | Offset availability | absent | imputed or proxy offset | offset available but uncertainty not bounded | offset source traceable and uncertainty bounded | annotation file, audit sheet | absent offset limits duration and postictal claims |
| MTS-13 | Label temporal uncertainty | absent | acknowledged but unquantified | approximate uncertainty stated | uncertainty bounded and used in interpretation | annotation guide | absent uncertainty blocks T1 |
| MTS-14 | Seizure taxonomy | absent | broad labels only | seizure type labels available but not standardized | taxonomy mapped to recognized clinical classification | label dictionary | absent taxonomy blocks seizure-type claims |
| MTS-15 | Patient count | undocumented or <=1 | small, not enough for split | enough for narrow split but limited | adequate for declared split and subgroup reporting | cohort table | insufficient count blocks E2-PI/E3 |
| MTS-16 | Seizure count | undocumented or extremely low | low count, unstable metrics | usable for narrow claims | adequate count for declared event metrics and subgroup caveats | event table | insufficient count blocks strong performance claims |
| MTS-17 | Interictal duration | absent or too short | short, FAR unstable | usable but limited | sufficient for FAR/24h estimation and distribution | recording duration table | insufficient interictal blocks low-FAR claims |
| MTS-18 | Missing data quantification | absent | anecdotal | quantified globally | quantified by patient, modality, time and split | missingness report | unquantified missingness blocks T1 |
| MTS-19 | Artifact quantification | absent | anecdotal | quantified globally | quantified by patient, modality, context and split | artifact report | unquantified artifacts block strong robustness claims |
| MTS-20 | Split manifest availability | absent | described but not machine-readable | machine-readable but incomplete metadata | complete manifest with patient/time/recording/site fields | split manifest | absent split manifest blocks E2-PD/E2-PI or higher |
| MTS-21 | Reproducible canonical transform | absent | manual or partially scripted | scripted with gaps | fully scripted, versioned, logged, checksum-verified | transform command/log | non-reproducible transform blocks T1 |

### 7.2 MTS tier candidates

| Candidate | Numeric rule | Additional rule |
| --- | --- | --- |
| T1 candidate | MTS >= 80 | no T1-blocking fail-closed |
| T2 candidate | 60 <= MTS < 80 | no certification-blocking failure |
| T3 candidate | MTS < 60 | exploratory or inventory only |

MTS tier candidate is not final until fail-closed conditions are applied.

## 8. DSI: Domain Stress Index

DSI measures domain breadth and stress. It does not measure label quality.

Each item is scored 0 to 3:

| Score | Meaning |
| --- | --- |
| 0 | dimension absent or undocumented |
| 1 | dimension marginal, imbalanced, or not stratifiable |
| 2 | dimension present and analyzable but limited |
| 3 | dimension substantially covered, stratifiable, and relevant to the claim |

DSI is computed as:

```text
DSI_raw = sum(item_scores)
DSI_max = 3 * number_of_items
DSI_scaled = 100 * DSI_raw / DSI_max
```

DSI cannot compensate for weak MTS.

### 8.1 DSI rubric

| ID | Item | 0 | 1 | 2 | 3 | Evidence required | Claim effect |
| --- | --- | --- | --- | --- | --- | --- | --- |
| DSI-01 | Patient diversity | undocumented or single profile | limited diversity, not stratifiable | multiple profiles, limited strata | broad and stratifiable cohort | cohort metadata | low score limits external claims |
| DSI-02 | Age coverage | absent | narrow age band | multiple age bands, uneven | clinically meaningful age strata | age metadata | age-general claim requires >=2 |
| DSI-03 | Sex coverage | absent | one sex dominant, not stratifiable | both sexes present, limited balance | stratifiable sex distribution | sex metadata | sex-general claim requires >=2 |
| DSI-04 | Epilepsy phenotype/syndrome | absent | broad epilepsy label only | phenotype partly available | phenotype/syndrome stratifiable | clinical metadata | phenotype claims require >=2 |
| DSI-05 | Seizure type diversity | absent | one dominant type | several types, limited counts | seizure types stratifiable | event labels | broad seizure-type claim requires >=2 |
| DSI-06 | Convulsive/non-convulsive coverage | absent | convulsive only or unclear | both partly present | both stratifiable | event taxonomy | non-convulsive claim requires evidence |
| DSI-07 | Nocturnal/diurnal coverage | absent | one context only | both present, limited | both stratifiable | timestamps/context | night/day claim requires >=2 |
| DSI-08 | Sleep/wake coverage | absent | inferred only | documented partly | documented and stratifiable | sleep/wake metadata | sleep/wake claim requires >=2 |
| DSI-09 | Hospital/home context | absent | one context only | partial ambulatory or context mix | hospital and home/ambulatory stratifiable | acquisition context | home claim requires >=2 |
| DSI-10 | Motion and daily activity | absent | minimal or artificial | some real movement | real activity variability quantified | ACC/context/artifact data | wearable claim requires >=2 |
| DSI-11 | Artifact stress | absent | anecdotal | quantified globally | quantified by modality/split/context | artifact report | robustness claim requires >=2 |
| DSI-12 | Multisensor coverage | single modality only | multiple channels same modality | multimodal but incomplete | multimodal synchronized and stratifiable | sensor metadata | multimodal claim requires >=2 |
| DSI-13 | Cross-device coverage | absent | device variation anecdotal | multiple devices, limited metadata | device variation documented and stratifiable | device IDs | cross-device claim requires >=2 |
| DSI-14 | Multisite coverage | absent | site unknown or single site | multiple sites, limited site split | multi-site with site-aware split | site metadata | E3 multisite requires >=2 |
| DSI-15 | Long-term monitoring | absent/short | short recordings only | moderate duration | long-duration monitoring supports FAR/risk | duration report | long-term claim requires >=2 |
| DSI-16 | Medication/context metadata | absent | partial unstructured | structured but incomplete | structured and stratifiable | clinical metadata | medication-context claims require >=2 |
| DSI-17 | Patient-independent split feasibility | impossible | possible but weak counts | feasible with caveats | feasible and statistically meaningful | split manifest | E2-PI requires >=2 |
| DSI-18 | External validation feasibility | absent | candidate external only | external available with mismatch | external/site validation feasible and declared | external manifest | E3 requires >=2 |
| DSI-19 | Prospective setting feasibility | absent | hypothetical only | protocol-like evidence but retrospective | prospective protocol/evidence available | study protocol | E4 requires >=2 plus prospective evidence |
| DSI-20 | Real wearable placement variability | absent | fixed lab placement | some placement variability | real-world placement/adherence documented | wearable metadata | deployment claim requires >=2 |

### 8.2 DSI bands

| Band | Rule | Interpretation |
| --- | --- | --- |
| Low | DSI < 40 | narrow domain stress |
| Medium | 40 <= DSI < 70 | partial domain stress |
| High | DSI >= 70 | broad domain stress |

High DSI never upgrades a weak MTS. Low DSI can limit E3 even when MTS is high.

## 9. Dataset tiers

Dataset tier is derived from MTS and fail-closed conditions. DSI constrains externality and generalization, but it does not directly certify metrological quality.

| Tier | Definition | Default claim ceiling before split/validation/failure gates |
| --- | --- | --- |
| T1 | strong clinical evidence dataset | E2-PI possible; E3 possible only with external/site evidence |
| T2 | useful but incomplete dataset | E2-PD or E2-PI possible under narrow scope |
| T3 | exploratory or inventory dataset | E1 maximum |

### 9.1 Tier rules

| Condition | Tier effect |
| --- | --- |
| MTS >= 80 and no T1 blocker | T1 candidate |
| 60 <= MTS < 80 and no certification blocker | T2 candidate |
| MTS < 60 | T3 candidate |
| labels unauditable | T3 or claim max E1 |
| raw-to-canonical not traceable | T1 prohibited |
| split manifest absent | E2-PD/E2-PI or higher prohibited |
| license unclear | public certification prohibited until resolved |

## 10. Claim ladder

Claims are evidence eligibility levels. They are not model rankings.

| Claim | Definition | Required minimum evidence | Forbidden interpretation |
| --- | --- | --- | --- |
| E0 | no scientific claim | incomplete/mock/synthetic-only or failed evidence | any real-world performance claim |
| E1 | structural protocol validity | reproducible pipeline logic, labels/splits tested structurally, failures preserved | clinical or operational performance |
| E2-PD | patient-dependent narrow operational claim | T1/T2, audited labels, patient-dependent split, FAR/day, latency definition, no leakage, failure trace | generalization to new patients |
| E2-PI | patient-independent narrow operational claim | T1/T2, audited labels, patient-independent split, FAR/day, latency definition, no leakage, failure trace | external or multisite generalization |
| E3 | external/multisite generalization research claim | E2-PI plus external dataset/site or leave-site-out validation, subgroup/failure report | clinical readiness |
| E4 | prospective clinical-grade evidence | prospective intended-use protocol, clinician-adjudicated ground truth, risk analysis, independent validation | regulatory approval unless separately obtained |

E2-PD and E2-PI MUST remain separate in all reports.

## 11. Claim ceiling model

Claim ceiling is computed conservatively:

```text
claim_ceiling = min(
  dataset_ceiling,
  split_ceiling,
  label_audit_ceiling,
  failure_ceiling,
  validation_ceiling,
  hardware_ceiling,
  track_ceiling
)
```

The minimum is taken over ordered claims:

```text
E0 < E1 < E2-PD < E2-PI < E3 < E4
```

Because E2-PD and E2-PI answer different questions, E2-PD is not automatically "less scientific"; however, for claim ceiling ordering it cannot support new-patient generalization.

### 11.1 Dataset ceiling

| Dataset evidence | Maximum claim |
| --- | --- |
| mock/synthetic only | E1 |
| T3 | E1 |
| T2 | E2-PD or E2-PI depending on split |
| T1 | E2-PD or E2-PI; E3 only with external/site validation |
| prospective clinical-grade evidence | E4 candidate, subject to all other gates |

### 11.2 Split ceiling

| Split evidence | Maximum claim |
| --- | --- |
| no split manifest | E1 |
| patient-dependent only | E2-PD |
| patient-independent | E2-PI |
| leave-one-subject-out | E2-PI, or E3 only if declared external/site condition is met |
| leave-site-out | E3 candidate |
| external dataset | E3 candidate |
| prospective intended-use validation | E4 candidate |

### 11.3 Label audit ceiling

| Label evidence | Maximum claim |
| --- | --- |
| labels missing or proxy-only | E1 |
| labels present but unaudited | E1 |
| onset missing for Track D/W | E1 |
| SPH/SOP labels unaudited for Track F | E1 |
| audited labels with caveats | E2-PD or E2-PI candidate, depending on split |
| clinician-adjudicated prospective labels | E4 candidate |

### 11.4 Failure ceiling

| Failure status | Maximum claim |
| --- | --- |
| no failure trace | E1 and no `Run-Complete` |
| patient leakage | E1 |
| temporal leakage | E1 |
| split noncompliance | E1 |
| unhandled NaN/Inf outputs | E1 or run invalid, depending on scope |
| missing predictions without sentinel | E1 |
| transparent non-critical failures | E2-PD/E2-PI/E3 possible with penalties and caveats |

### 11.5 Hardware ceiling

| Hardware evidence | Maximum hardware/edge claim |
| --- | --- |
| no runtime report | no latency or real-time claim |
| desktop-only profile | proxy performance only |
| controlled device profile | `Edge-Profiled` candidate |
| target hardware measurement | `Edge-Measured` candidate |
| causal streaming end-to-end measurement | `Streaming-Feasible` candidate |

Hardware ceiling applies only to edge/real-time claims. It does not automatically lower non-edge scientific claims unless latency is part of the clinical claim.

## 12. Failure and sentinel consequence matrix

Failure traces are scientific observations. They MUST NOT be deleted, silently imputed, or hidden behind survivor-only averages.

| Sentinel | Detection condition | Severity | Score impact | Claim impact | Required report |
| --- | --- | --- | --- | --- | --- |
| `PREDICTION_MISSING` | required prediction absent for patient/recording/window | major | failure-rate and stability penalty | may lower E2-PD/E2-PI or higher if above threshold; unreported missingness max E1 | affected units, denominator, reason |
| `SEGMENT_CRASH` | inference crashes on segment | major | robustness/stability penalty | E2-PD/E2-PI or higher only if transparent and bounded | stack/log, affected segment count |
| `NAN_OR_INF_OUTPUT` | non-finite model output | critical if unhandled | invalidates affected output; penalty | unhandled NaN/Inf max E1 | affected outputs, handling policy |
| `LATENCY_BUDGET_EXCEEDED` | runtime or detection delay exceeds preregistered budget | major/critical | latency penalty | blocks real-time/edge claim | latency distribution |
| `POST_EVENT_ALARM` | alarm occurs after useful detection/warning window | major | performance/safety penalty | blocks useful early-warning claim | event/alarm timing |
| `FAR_EXPLOSION` | FAR exceeds preregistered maximum | major | safety penalty | blocks low-FAR claim; may block E2-PD/E2-PI or higher if extreme | FAR distribution |
| `PATIENT_LEAKAGE` | patient identity crosses train/test boundary improperly | critical | certified score invalid | max E1 | leakage mechanism |
| `TEMPORAL_LEAKAGE` | future data, overlap, normalization, or threshold leakage | critical | certified score invalid | max E1 | leakage mechanism |
| `SPLIT_NONCOMPLIANT` | run does not use frozen split | critical | certified score invalid | max E1 | expected vs actual split |
| `LABEL_UNAUDITED` | label provenance/timing not cleared | critical | score not claimable beyond structure | max E1 | label audit status |
| `DEVICE_MISSINGNESS` | required modality unavailable/dropout | major | observability/stability penalty | claim limited to observed modality regime | missingness table |
| `HARDWARE_UNMEASURED` | edge/real-time claim without hardware evidence | critical for edge claim | edge score not certified | blocks real-time/edge claim | hardware evidence status |

## 13. Worked adjudication rules

Every Phase 1 adjudication example MUST include:

- Evidence Card summary;
- MTS score and blockers;
- DSI score and domain limits;
- dataset tier;
- declared track;
- split type;
- label audit status;
- failure status;
- requested claim;
- granted claim;
- forbidden claims;
- reason log.

Minimum example set:

1. High-MTS hospital EEG, low DSI, patient-independent: T1 candidate, E2-PI max, E3 blocked by low external evidence.
2. Wearable multimodal dataset with useful but incomplete labels: T2, E2-PI possible under narrow scope if split and audit pass.
3. Proxy-label exploratory dataset: T3, E1 max despite any high classifier metric.
4. Patient-dependent high performance: E2-PD max, E2-PI/E3 blocked.
5. Leakage failure: E1 max even if all metrics are strong.
6. Hardware claim without hardware report: non-edge claim may stand, real-time/edge claim blocked.

## 14. Phase 1 validation tests

### 14.1 Inter-reviewer reproducibility

Two reviewers independently score the same Evidence Card.

Pass criteria:

- MTS difference <= 5 points;
- DSI difference <= 8 points;
- same dataset tier;
- same claim ceiling.

### 14.2 Fail-closed label test

Scenario: high numeric MTS but unauditable labels.

Expected:

- T1 blocked;
- E2-PD/E2-PI or higher blocked;
- reason log includes `LABEL_UNAUDITED`.

### 14.3 Patient-dependent ambiguity test

Scenario: strong patient-dependent result, no patient-independent split.

Expected:

- E2-PD possible;
- E2-PI blocked;
- E3 blocked;
- generalization wording forbidden.

### 14.4 External validation test

Scenario: T1 dataset, patient-independent split, no external validation.

Expected:

- E2-PI maximum;
- E3 blocked.

### 14.5 Hardware claim test

Scenario: real-time claim requested, no hardware report.

Expected:

- real-time claim blocked;
- `Edge-Measured` blocked;
- hardware evidence warning emitted.

### 14.6 Track separation test

Scenario: SPH/SOP risk output only, no event detection output.

Expected:

- Track F may be evaluated;
- Track D claim blocked.

### 14.7 SOTA non-reinvention test

Scenario: an EpiBench rule introduces a metric or report field already covered by an existing source such as SzCORE, TRIPOD+AI, STARD-AI, or DECIDE-AI.

Expected:

- the rule is marked ADOPT, MAP, EXTEND, or DIVERGE;
- divergence has a written rationale;
- citation integrity is verified;
- no new metric is introduced solely for novelty.

## 15. Phase 1 closeout

Phase 1 can close only with the following status table:

| Gate | Required status |
| --- | --- |
| Normative vocabulary | PASS |
| MTS rubrics | PASS |
| DSI rubrics | PASS |
| Dataset tiers | PASS |
| Track separation | PASS |
| Claim ladder | PASS |
| Claim ceiling matrix | PASS |
| Failure consequence matrix | PASS |
| Adjudication examples | PASS |
| Review checklist | PASS |
| Anti-overclaim wording | PASS |
| SOTA alignment | PASS |
| Ready for Phase 2 encoding | YES |

If any gate is `BLOCKED`, Phase 2 MUST NOT begin.

## 16. Fields to encode in Phase 2

The following fields MUST be represented in Phase 2 schemas or YAML:

- `epibench_version`;
- `track_id`;
- `dataset_id`;
- `dataset_tier`;
- `mts_items`;
- `mts_scaled`;
- `mts_fail_closed_flags`;
- `dsi_items`;
- `dsi_scaled`;
- `domain_limit_flags`;
- `split_type`;
- `label_audit_status`;
- `external_validation_status`;
- `prospective_evidence_status`;
- `hardware_evidence_status`;
- `failure_trace_status`;
- `sentinels`;
- `requested_claim`;
- `granted_claim`;
- `forbidden_claims`;
- `claim_blocking_reasons`.
- `sota_registry_entries`;
- `sota_relationship`;
- `sota_citation_integrity_status`.

## 17. Final Phase 1 statement

When Phase 1 is complete, EpiBench has a normative evidence model:

> Dataset quality, domain stress, task track, split type, label audit, failures, hardware evidence, and validation setting jointly determine the maximum scientific claim. A model score can rank behavior inside that allowed evidence boundary, but it cannot expand the boundary.
