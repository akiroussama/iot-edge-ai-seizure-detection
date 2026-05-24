# EpiBench for auditable evidence in seizure AI

Target journal: npj Digital Medicine  
Article type: Article  
Status: full manuscript draft v0.1  
Date: 2026-05-24  

## Title Page

### Title

EpiBench for auditable evidence in seizure AI

### Short title

Auditable seizure AI evidence

### Authors

To be completed.

Required author expertise before submission:

- epilepsy or clinical neurophysiology;
- biomedical signal processing;
- digital health AI evaluation;
- reproducible software or benchmark engineering;
- IoT or embedded systems.

### Corresponding author

To be completed.

### Keywords

Epilepsy; seizure detection; seizure forecasting; digital medicine; wearable sensing; artificial intelligence; benchmark; reproducibility; clinical AI assurance; IoT.

## Abstract

Machine learning systems for seizure detection, early warning, and forecasting are commonly compared using summary metrics such as accuracy, sensitivity, F1 score, AUROC, or false alarm rate. These metrics are not self-interpreting evidence. Their scientific meaning depends on dataset provenance, sensor modality, label quality, seizure onset and offset uncertainty, patient-dependent versus patient-independent splitting, hospital versus home monitoring, artifact burden, missing data, latency, hardware feasibility, and the handling of model failures. A single leaderboard row can therefore overstate clinical or operational validity, particularly when failures, leakage, or alarm burden are hidden.

We introduce EpiBench, an open evidence and claim-certification framework for seizure AI. EpiBench separates dataset evidence from algorithm behavior through Epilepsy Dataset Evidence Cards, metrological trustworthiness and domain stress rubrics, task-specific tracks for detection, early warning, forecasting, and embedded viability, failure-preserving result bundles, and deterministic claim gates. Instead of asking which model is best, EpiBench asks what a result is allowed to prove. The framework maps existing seizure event-scoring and clinical AI reporting standards where compatible, including ILAE seizure vocabulary, event-based scoring frameworks such as SzCORE, and reporting guidance for prediction and diagnostic AI.

We provide a machine-readable specification, JSON Schemas, a reference command-line implementation, certification badges, release-candidate reproduction artefacts, and worked examples. In a demonstration, a model with superior naive metrics is downgraded to a structural-only claim because leakage and threshold-selection failures are preserved, whereas a lower-scoring but auditable run receives a bounded patient-independent operational claim. EpiBench certification is scientific certification of an evidence package, not clinical approval or regulatory clearance. The framework is intended to make seizure AI results auditable, reproducible, comparable, and resistant to leaderboard-driven overclaim.

## Main

### Introduction

Artificial intelligence for epilepsy monitoring is advancing rapidly across hospital EEG, wearable sensors, multimodal biosignals, and edge computing. The field includes seizure detection, early warning, seizure forecasting, and long-term risk estimation. These tasks differ clinically and mathematically, yet their evaluations are often compressed into a small set of performance metrics.

This compression creates a scientific problem. A reported accuracy of 95 percent may reflect class imbalance rather than useful seizure detection. A high AUROC may coexist with an unacceptable number of false alarms per day. A high sensitivity may be achieved by placing patients in warning for large fractions of monitored time. A patient-dependent split may measure within-patient adaptation rather than generalization to new patients. A hospital EEG dataset may not support a claim about home wearable use. A detector may appear real-time in offline evaluation while exceeding latency or energy budgets on target hardware. A seizure forecasting model may be evaluated as a preictal classifier without clinically meaningful alarm burden constraints.

The central claim of this paper is that scores alone are not evidence. The scientific unit should not be an isolated leaderboard row. It should be an auditable evidence package that records the dataset, labels, split, metrics, failures, latency, hardware constraints, code version, and the maximum claim supported by these elements.

This problem is not unique to epilepsy. In battery state estimation, BSEBench addressed a parallel issue: single metrics such as RMSE can misrepresent algorithmic validity when dataset quality, operating conditions, failures, and claim eligibility are not separated. EpiBench applies the same epistemic principle to seizure AI while respecting the specific clinical, signal-processing, and IoT constraints of epilepsy monitoring.

EpiBench is not proposed as another seizure detector. It is a scientific evidence framework. It does not replace clinical validation, regulatory evaluation, prospective studies, or medical-device approval. Instead, it defines the conditions under which retrospective and benchmark results can make bounded scientific claims.

### Related work and non-reinvention principle

EpiBench is designed to reuse rather than replace existing standards whenever possible.

The International League Against Epilepsy provides seizure-type vocabulary and clinical classification structure. EpiBench adopts ILAE terminology when dataset metadata permit it.

Event-based seizure scoring has been advanced by community efforts such as SzCORE, which provides open evaluation machinery for seizure detection algorithms. EpiBench should map or adopt compatible event-level outputs such as sensitivity, precision, F1 score, and false positives per day, rather than redefining event scoring unnecessarily.

Clinical AI reporting has been strengthened by TRIPOD+AI for prediction models, STARD-AI for diagnostic accuracy studies, DECIDE-AI for early-stage clinical evaluation of AI decision support, SPIRIT-AI and CONSORT-AI for AI trial protocols and reports, and FUTURE-AI for trustworthy and deployable healthcare AI. EpiBench maps these reporting principles into a seizure-specific evidence architecture, with additional attention to seizure labels, alarm burden, failures, and embedded viability.

This non-reinvention rule is encoded in the EpiBench SOTA registry. Every normative rule should be classified as `ADOPT`, `MAP`, `EXTEND`, or `DIVERGE` with respect to existing standards. Divergence requires explicit rationale.

### EpiBench architecture

EpiBench separates four evidence layers:

1. Dataset evidence: what the dataset can support.
2. Protocol validity: whether labels, splits, thresholds, and leakage checks are valid.
3. Algorithm behavior: how the system performs under the declared track.
4. Claim eligibility: what can be scientifically claimed from the evidence package.

This separation prevents a strong metric from compensating for weak evidence. A model with excellent sensitivity and false alarm rate can still be ineligible for an operational claim if patient leakage is detected, if labels are proxy-only, or if the requested claim exceeds the dataset and split design.

#### Tracks

EpiBench defines four primary tracks:

- `D`, seizure detection: detection of ongoing or near-onset seizure events.
- `W`, early warning: alarms before a clinically meaningful deadline.
- `F`, forecasting: risk estimation over a specified future horizon using explicit seizure prediction horizon and seizure occurrence period definitions where applicable.
- `E`, embedded viability: feasibility under declared IoT or edge deployment constraints.

Each result bundle must declare one primary track. The same model may be evaluated on several tracks, but each track produces a separate verdict. This prevents, for example, a detection result from being described as forecasting or an offline algorithm from being described as real-time without hardware evidence.

#### Dataset Evidence Cards

Each dataset is documented through an Epilepsy Dataset Evidence Card. The card records provenance, license, acquisition protocol, sensor modalities, sampling rates, calibration, temporal synchronization, label source, onset and offset availability, label temporal uncertainty, number of patients, number of seizures, interictal duration, missing data, artifacts, raw-to-processed traceability, and known limitations.

Two rubric families separate data quality from domain diversity:

- Metrological Trustworthiness Score, or MTS, captures the trustworthiness of measurements, labels, timing, transformations, and traceability.
- Domain Stress Index, or DSI, captures diversity and stress of the domain, including patient diversity, seizure types, hospital or home setting, artifacts, long-term monitoring, sensor placement, multi-device variation, and external validation.

MTS and DSI are scored with 0 to 3 rubrics. Missing evidence fails closed: it lowers the claim ceiling rather than being inferred favorably.

#### Dataset tiers

EpiBench defines dataset evidence tiers:

- `T1`, strong clinical dataset evidence: traceable source, expert annotations, usable onset and offset or task-appropriate timing evidence, clear split policy, and license clarity.
- `T2`, useful but incomplete evidence: useful labels or sensors but incomplete raw traceability, diversity, timing precision, or documentation.
- `T3`, exploratory inventory or weak evidence: insufficient for operational claims.

Dataset tier is not a claim by itself. A T1 dataset can still support only a narrow claim if it is hospital-only, lacks external validation, or uses a patient-dependent split.

#### Claim ladder

EpiBench defines five scientific claim levels plus a no-claim state:

- `E0`, no scientific claim.
- `E1`, structural protocol validity.
- `E2-PD`, patient-dependent operational claim.
- `E2-PI`, patient-independent narrow operational claim.
- `E3`, external or multisite generalization claim.
- `E4`, prospective clinical-grade evidence claim.

EpiBench-certified does not mean clinically approved. It means that an evidence package has been evaluated under public, versioned, reproducible rules and assigned a bounded claim.

### Epi-Score

The Epi-Score is a multi-axis score intended to summarize algorithm behavior without replacing claim eligibility. The v1.0-draft formula is:

```text
EpiScore = 100 * product(axis_score ^ weight) * exp(-lambda * max(0, floor - min_axis_score))
```

The geometric product prevents excellent behavior on one axis from hiding catastrophic behavior on another. The floor penalty further reduces scores when any axis falls below a preregistered threshold.

The current axes are:

- performance;
- clinical safety;
- robustness;
- stability;
- latency;
- embedded viability;
- calibration.

The score is deliberately subordinate to claim gates. Leakage, split failure, unaudited labels, or missing failure traces can downgrade a claim regardless of the numerical Epi-Score.

### Failure-preserving evaluation

EpiBench treats failures as scientific observations. A run must preserve sentinels for conditions such as:

- missing predictions;
- segment crashes;
- NaN or infinite outputs;
- latency budget exceedance;
- post-event alarms counted as early warning;
- excessive false alarm burden;
- patient leakage;
- temporal leakage;
- split noncompliance;
- unaudited labels;
- device missingness;
- absent hardware measurements.

These sentinels are not merely logged. They mechanically affect claims and badges. For example, patient leakage blocks `E2+`; absent hardware measurement forbids real-time, on-device, or edge-ready wording; post-event alarms block early-warning claims when counted as successes.

### Reference implementation

We implemented EpiBench as a versioned, machine-readable standard. The reference package includes:

- a normative YAML specification;
- JSON Schemas for dataset cards, split manifests, failure traces, result bundles, claim eligibility reports, and SOTA registry;
- a command-line interface for validation, scoring, certification, and report rendering;
- example evidence packages;
- tests confirming that leakage downgrades claims even when naive metrics are strong.

The CLI exposes commands:

```text
epibench validate-dataset-card
epibench validate-split
epibench validate-result-bundle
epibench validate-failure-trace
epibench validate-sota-registry
epibench score
epibench certify
epibench render-report
```

The canonical output is a JSON claim eligibility report. A Markdown report is generated for human review.

### Worked example

We constructed two demonstration result bundles to show the difference between leaderboard interpretation and evidence interpretation. These examples are not intended as clinical performance results. They are protocol demonstrations.

The first bundle represents an auditable patient-independent detection run on a T1-like EEG evidence package. It uses leave-one-subject-out splitting, expert-adjudicated labels, complete failure tracing, and no leakage. It includes demonstration hardware fields only to exercise the schema; these fields are not treated as citable target-device evidence and do not authorize edge-ready or real-time wording. Its Epi-Score is 74.158 and its final claim is `E2-PI`.

The second bundle represents a model with stronger naive metrics: sensitivity 0.99, precision 0.95, F1 0.97, and false alarms per 24 hours of 0.1. Its Epi-Score is 94.727. However, the bundle preserves patient leakage, split noncompliance, and threshold selection on test labels. EpiBench downgrades the final claim to `E1`.

A third bundle requests a patient-independent claim while using a declared patient-dependent split. EpiBench downgrades this request from `E2-PI` to `E2-PD`, preserving the value of patient-specific evaluation while preventing generalization overclaim.

We also drafted real and preliminary evidence packages derived from existing local reports and public resources: a CHB-MIT patient-independent detection package, a CHB-MIT waveform micro-subset threshold baseline, a longitudinal MSG forecasting package, and a SeizeIT2 single-subject local pipeline check. These packages are deliberately heterogeneous in strength. The CHB-MIT packages demonstrate patient-independent EEG packaging but remain limited by scale and baseline simplicity. The MSG and SeizeIT2 packages are intentionally claim-limited where labels, split readiness, or local scope are insufficient. These packages demonstrate that EpiBench can represent weak, partial, and stronger evidence without promoting all real data to an operational claim.

These results illustrate the central point. The higher-scoring model is not necessarily the stronger scientific result, and real data are not automatically strong evidence. The protocol prevents the leaderboard from defining what the evidence cannot support.

### Results

#### Machine-readable validation

All demonstration artefacts were validated against EpiBench v1.0-draft schemas:

- Dataset Evidence Card;
- Split Manifest;
- Failure Trace;
- Result Bundle;
- SOTA Registry.

Invalid artifacts fail explicitly, rather than being interpreted with favorable assumptions.

#### Claim generation

The clean demonstration bundle requested `E2-PI` and received `E2-PI`. Its claim ceilings were:

```text
dataset_tier: E2-PI
split_policy: E2-PI
label_audit: E4
leakage_audit: E4
threshold_policy: E4
failure_status: E4
hardware_evidence: E4
track_consistency: E4
```

The leakage demonstration bundle requested `E3` and received `E1`. Its score was higher than the clean example, but the claim was limited by:

```text
leakage_audit: E1
threshold_policy: E1
failure_status: E1
```

The blocking reasons were:

- patient leakage;
- split noncompliance;
- failed leakage audit;
- threshold selection using test labels.

The patient-dependent demonstration bundle requested `E2-PI` and received `E2-PD`, because patient-dependent evaluation cannot support new-patient operational claims even when leakage checks and thresholds are valid.

Real and preliminary packages span several evidence states. The CHB-MIT patient-independent detection package and the CHB-MIT waveform micro-subset package demonstrate EEG Track D packaging, but the waveform result remains a small baseline smoke test. The MSG forecasting baseline requested `E2-PD` but was limited by label-audit and failure sentinels. The SeizeIT2 local single-subject check requested `E2-PI` but was limited by dataset tier, split policy, label audit, leakage-audit status, and failure sentinels.

#### Badge generation

The clean demonstration bundle received:

```text
EpiBench-Dataset-T1
EpiBench-Run-Complete
EpiBench-Failure-Transparent
EpiBench-Claim-E2-PI
EpiBench-Leakage-Checked
```

The leakage demonstration bundle received:

```text
EpiBench-Dataset-T1
EpiBench-Run-Complete
EpiBench-Failure-Transparent
EpiBench-Claim-E1
```

This badge difference is designed to be visible in manuscripts and repositories. A reader can distinguish a high-score but structurally invalid result from a bounded operational result.

### Discussion

EpiBench addresses a recurring failure in seizure AI evaluation: the tendency to treat model performance metrics as self-contained proof. This tendency is especially risky in epilepsy because the clinical meaning of an alarm depends on event timing, false alarm burden, per-patient reliability, sensor context, and deployment latency.

The framework changes the unit of comparison. A model is not compared by sensitivity alone. A result is compared by its evidence package, including dataset tier, split policy, label audit, failures, metrics, score, and final claim.

This approach has several consequences.

First, EpiBench makes negative evidence publishable. A model that fails on certain patients, crashes on segments, produces late alarms, or exceeds false alarm budgets does not disappear from the table. These failures constrain interpretation.

Second, EpiBench prevents patient-dependent results from being narrated as generalizable. The `E2-PD` and `E2-PI` distinction is deliberately explicit because patient-dependent seizure AI can be clinically and technically useful, but it does not prove new-patient generalization.

Third, EpiBench separates detection, early warning, and forecasting. This is essential because a useful detector, a useful warning system, and a calibrated risk forecaster answer different scientific and clinical questions.

Fourth, EpiBench integrates embedded viability into evidence. A system cannot be called real-time or edge-ready without measured hardware evidence. This is important for IoT seizure monitoring, where latency, memory, energy, connectivity, and wearability are not peripheral details.

Fifth, EpiBench offers a route to community adoption without replacing existing work. It can consume event-scoring outputs from compatible frameworks and place them inside a broader evidence and claim-governance structure.

### Limitations

EpiBench v1.0-draft is a scientific certification framework, not a clinical validation pathway. It does not determine whether a system is safe, effective, regulatory cleared, or ready for medical deployment.

The current reference implementation validates structure and applies claim gates, but it does not yet automatically recompute all possible metric subscores from raw biosignals. Integration with established event-scoring packages should be prioritized to avoid metric fragmentation.

MTS and DSI rubrics reduce subjectivity but do not eliminate it. Inter-reviewer agreement studies are required before claiming that evidence card scoring is stable across institutions.

The demonstration examples show protocol mechanics, not clinical performance. The current release-candidate evidence packages include real-data and public-resource packages, but full-scale EEG detection evidence, external reproduction, and independent clinical review remain required before a high-confidence submission.

The Epi-Score weights are preregistered in the v1.0-draft YAML, but they require sensitivity analyses. A standard should not hide the influence of weights.

EpiBench currently focuses on seizure-related AI. Extension to broader paroxysmal event monitoring would require new domain review.

### Conclusion

EpiBench reframes seizure AI evaluation from leaderboard ranking to auditable evidence certification. It separates dataset evidence from algorithm behavior, preserves failures, distinguishes detection from warning and forecasting, includes embedded viability, and assigns explicit claim ceilings. A high metric no longer defines what a result proves. The protocol defines what the metric is allowed to mean.

## Methods

### Design principles

EpiBench was designed around six principles:

1. Separate dataset evidence from algorithm performance.
2. Evaluate task-specific outputs rather than mixing detection, early warning, and forecasting.
3. Preserve failures as scientific observations.
4. Use multi-axis scoring without letting the aggregate score override claim gates.
5. Generate claims deterministically from versioned rules.
6. Reuse existing scoring and reporting standards where compatible.

### Dataset Evidence Card construction

The Dataset Evidence Card schema records dataset identity, provenance, license, source, sensor modalities, sampling rates, placement, synchronization, calibration, population, seizure counts, monitoring duration, label source, onset and offset availability, label uncertainty, MTS rubric items, DSI rubric items, declared tier, limitations, and raw-to-processed traceability.

Each rubric item uses a 0 to 3 score:

- 0, absent or unauditable evidence;
- 1, weak or partial evidence;
- 2, usable evidence with limitations;
- 3, strong and independently reviewable evidence.

Rubric scores must include evidence text and review status. Missing evidence is not imputed.

### Split Manifest construction

The Split Manifest schema records split identity, dataset, track, split policy, train/validation/test unit counts, leakage checks, normalization scope, and threshold selection policy.

Supported split policies include patient-dependent, temporal within-patient, recording-wise same-patient, patient-independent, leave-one-subject-out, external dataset, leave-one-site-out, prospective multisite, synthetic or demo, and noncompliant or unknown.

### Failure Trace construction

The Failure Trace schema records a run identifier, failure policy, sentinels, severity, count, scope, and evidence. EpiBench requires preservation of failures rather than silent exclusion.

### Result Bundle construction

The Result Bundle schema records run identifier, track, requested claim, artifact paths, model name and family, commit SHA, environment, inputs, outputs, metrics, score inputs, hardware evidence where applicable, reproduction command, and checksums.

### Claim eligibility

Claim eligibility is computed as the minimum of the requested claim and the ceilings imposed by:

- dataset tier;
- split policy;
- label audit status;
- leakage audit;
- threshold selection policy;
- failure status;
- hardware evidence;
- track consistency.

Claim ranks are defined in the normative YAML. Authors cannot manually raise the claim.

### Epi-Score calculation

Axis subscores are provided in the result bundle and must lie in [0,1]. Required axes are defined in the YAML. The reference implementation normalizes the weights of provided axes and applies the geometric formula and floor penalty.

### Software implementation

The reference implementation is written in Python. It uses YAML and JSON artifacts as canonical inputs. A local validator implements the subset of JSON Schema required by EpiBench schemas, minimizing dependencies for the release candidate. The CLI validates artifacts, computes scores, certifies result bundles, and renders reports.

### Demonstration protocol

Two demonstration bundles were created. The clean bundle satisfies the dataset, split, label, leakage, threshold, failure, and hardware requirements for a bounded patient-independent claim. The leakage bundle reports stronger naive metrics but includes leakage and threshold-selection failures. The expected result is a higher Epi-Score but lower claim, demonstrating that claim eligibility is not reducible to model performance.

### Validation tests

Automated tests verify that:

- example artifacts validate against schemas;
- the clean bundle certifies as `E2-PI`;
- a patient-dependent bundle cannot receive `E2-PI`;
- a leave-one-subject-out bundle cannot receive `E3` without external validation;
- the leakage bundle is downgraded to `E1` despite higher score;
- the geometric score applies a floor penalty;
- missing required schema fields are rejected.

## Data availability

This draft uses release-candidate evidence packages to demonstrate protocol behavior and does not report new clinical performance results. Public dataset integrations should be strengthened before submission using appropriate dataset access terms. Candidate next packages include full-scale CHB-MIT or TUSZ for clinical EEG detection, SeizeIT2 for multimodal wearable detection, and longitudinal wearable resources for forecasting where licensing permits.

## Code availability

The reference implementation is contained in the repository under `src/epibench`, with command-line access through `scripts/epibench.py` and the planned `epibench` console script. A public release should archive the code, schemas, normative YAML, example bundles, reports, and tests with a DOI before submission.

## Ethics statement

This methodological draft does not introduce new human-subject data collection. Any future application to clinical datasets must follow the relevant dataset licenses, institutional review policies, de-identification requirements, and ethics approvals. EpiBench certification must not be presented as clinical approval.

## Author contributions

To be completed. Recommended taxonomy:

- conceptualization;
- methodology;
- software;
- validation;
- clinical review;
- writing original draft;
- writing review and editing;
- supervision.

## Competing interests

To be completed.

## References Draft

1. International League Against Epilepsy. Operational Classification of Seizure Types, 2017. https://www.ilae.org/guidelines/definition-and-classification/operational-classification-2017
2. SzCORE: A Seizure Community Open-source Research Evaluation framework for the validation of EEG-based automated seizure detection algorithms. https://arxiv.org/abs/2402.13005
3. SzCORE as a benchmark: report from the seizure detection challenge at the 2025 AI in Epilepsy and Neurological Disorders Conference. https://arxiv.org/abs/2505.18191
4. SeizeIT2: Wearable Dataset Of Patients With Focal Epilepsy. Scientific Data, 2025. https://www.nature.com/articles/s41597-025-05580-x
5. The Temple University Hospital Seizure Detection Corpus. https://pmc.ncbi.nlm.nih.gov/articles/PMC6246677/
6. TRIPOD+AI statement. BMJ, 2024. https://www.bmj.com/content/385/bmj-2023-078378
7. STARD-AI reporting guideline. Nature Medicine, 2025. https://www.nature.com/articles/s41591-025-03953-8
8. DECIDE-AI reporting guideline. Nature Medicine, 2022. https://www.nature.com/articles/s41591-022-01772-9
9. CONSORT-AI extension. Nature Medicine, 2020. https://www.nature.com/articles/s41591-020-1034-x
10. FUTURE-AI guideline. BMJ, 2025. https://www.bmj.com/content/388/bmj-2024-081554
11. FDA Clinical Decision Support Software guidance. https://www.fda.gov/medical-devices/software-medical-device-samd/clinical-decision-support-software-frequently-asked-questions-faqs

## Required Before Submission

This manuscript is not yet submission-ready. The following are blocking:

- Scale the CHB-MIT waveform evidence beyond the micro-subset or add a stronger TUSZ/CHB-MIT signal-derived package.
- Upgrade preliminary MSG and SeizeIT2 packages into submission-grade real evidence packages, or keep them only as negative/readiness examples.
- Complete the independent clinical and methods review packet with signed forms and adjudicated MTS/DSI changes.
- Add a full real EEG output scored by the official SzCORE tool if feasible; the current official smoke fixture closes only the API-contract non-reinvention risk.
- Measure the final model on declared target IoT hardware before any edge-ready, on-device, or real-time wording.
- Mint DOI archive and obtain at least one independent external clean-checkout reproduction run.
- Add complete author list, ethics/data statements, and supplementary material.

The manuscript must not claim universal community adoption, clinical validation, prospective clinical-grade evidence, target-device edge readiness, or regulatory certification unless the corresponding external evidence is added before submission.
