# EpiBench protocol for auditable IoT seizure detection

Date: 2026-05-24  
Scope: seizure detection and alarm generation from EEG, wearable, multimodal, or edge-IoT signals.  
Position: this is a protocol of evidence, not a leaderboard.

Normative note: this document is the readable protocol narrative. The Phase 1
normative evidence model is defined in `docs/EPIBENCH_SPEC_V1.md`, including
MTS/DSI rubrics, track definitions, E2-PD/E2-PI separation, claim ceiling rules,
and failure consequences.

SOTA note: EpiBench is not intended to replace existing seizure-event scoring,
clinical reporting, or healthcare-AI guidance. It should adopt or map existing
frameworks where appropriate, especially event-based seizure scoring, ILAE
seizure taxonomy, and AI reporting guidelines. Its added contribution is the
evidence and claim-governance layer: dataset cards, MTS/DSI, failure
preservation, IoT viability, result bundles, and claim eligibility.

## Scientific problem

The central problem is not "which model has the best accuracy". The central problem is:

> What can a given dataset, label process, split, sensor stack, and inference budget legitimately prove about seizure detection?

Classical metrics can be scientifically misleading in seizure detection:

- Accuracy is almost uninterpretable under massive interictal imbalance. A model can be "accurate" by never alarming.
- AUROC can look strong while the operating point is clinically useless, because clinical use is constrained by false alarms per day, missed seizures, and detection delay.
- Sensitivity alone is dangerous: a model that detects most seizures but alarms hundreds of times per day is not operationally credible.
- Specificity is often inflated because non-seizure samples dominate the denominator.
- Patient-dependent validation may measure personalization or leakage, not generalization to new patients.
- Hospital video-EEG and home wearable data are not interchangeable domains.
- Onset and offset annotations are not exact physical constants; they are clinical judgments with temporal uncertainty.
- Sensor placement, adherence, motion artifacts, battery gaps, and synchronization errors can dominate model behavior.
- "Real-time" is not a property of an algorithm on paper; it requires measured streaming latency on the intended hardware.
- A leaderboard row without failures, abstentions, missing patients, and uncertainty is not a reproducible scientific result.

The EpiBench answer is to separate four layers:

1. Dataset evidence: what the data can support.
2. Protocol validity: whether labels, splits, leakage checks, thresholds, and baselines are valid.
3. Algorithm behavior: how the model performs across detection, safety, robustness, latency, and edge viability.
4. Claim eligibility: what the result is allowed to mean.

## A. Architecture of the protocol

EpiBench should be organized as an auditable pipeline:

1. Dataset Intake
   - raw-source registry, license, checksums, acquisition protocol, sensor list, annotation files, and known limitations.
2. Epilepsy Dataset Evidence Card
   - Metrological Trustworthiness Score, Domain Stress Index, tier T1/T2/T3, and explicit "claim ceiling".
3. Task Definition
   - detection, early warning, or forecasting must be declared before experiments. For detection, define event matching window, alarm refractory period, detection deadline, and latency definition. For forecasting, define SPH/SOP.
4. Split Manifest
   - patient-dependent, patient-independent, leave-one-subject-out, temporal, center/site, home-vs-hospital, and external validation splits where available.
5. Pre-Registered Evaluation Plan
   - metrics, thresholds, alarm budgets, failure policy, hardware target, baselines, exclusion rules, and claim gates fixed before the final run.
6. Model Evaluation
   - predictions, event detections, alarm episodes, patient-level metrics, calibration, runtime, memory, energy proxy, and failure traces.
7. Epi-Score
   - multi-axis model behavior score. It is never a clinical approval score.
8. Claim Eligibility Report
   - maps dataset tier, split strength, failures, external validation, and hardware evidence to E0-E4.
9. Result Bundle
   - immutable run package with code SHA, configs, inputs, outputs, logs, metrics, figures, checksums, and reproduction command.

Short rule:

> The leaderboard is not the result. The result is the evidence package that constrains what the leaderboard row can claim.

## B. Epilepsy Dataset Evidence Card template

Recommended identifier:

```yaml
dataset_id:
version:
source_url:
license:
raw_data_available: true|false
processed_data_available: true|false
checksum_manifest:
population:
  n_patients:
  age_distribution:
  sex_distribution:
  epilepsy_type:
  seizure_types_ilae:
  medications_available:
  comorbidities_available:
recording_context:
  hospital_video_eeg: true|false
  home_ambulatory: true|false
  duration_total_hours:
  duration_interictal_hours:
  seizure_count:
  nocturnal_diurnal:
sensors:
  modalities:
  sampling_rates:
  placement:
  synchronization:
  calibration:
labels:
  annotator_type:
  neurologist_reviewed: true|false
  video_eeg_confirmed: true|false
  onset_available: true|false
  offset_available: true|false
  temporal_uncertainty_seconds:
  seizure_type_available: true|false
  label_adjudication:
quality:
  missing_data:
  artifacts:
  signal_quality_indices:
  device_dropouts:
  clock_drift:
transform:
  raw_to_canonical_steps:
  exclusion_rules:
  postictal_policy:
  split_manifest:
limits:
  known_biases:
  claim_ceiling:
```

### Metrological Trustworthiness Score

MTS measures whether the dataset is a reliable measurement instrument. Each item is scored 0-3, then scaled to 0-100:

- official source and stable version;
- license and access terms clear;
- raw signals available or traceable;
- acquisition protocol documented;
- sensor modality, placement, and sampling rate documented;
- time synchronization documented;
- calibration or device specification documented;
- neurologist or expert annotation;
- onset and offset available;
- temporal uncertainty documented;
- seizure type taxonomy documented, preferably aligned with ILAE classification;
- number of patients and seizures sufficient for the declared split;
- interictal duration adequate for false alarm estimation;
- missingness and artifacts quantified;
- raw-to-processed transform reproducible with checksums.

Suggested MTS tiers:

- MTS >= 80: strong metrological evidence.
- 60 <= MTS < 80: usable but incomplete evidence.
- 40 <= MTS < 60: exploratory evidence.
- MTS < 40: inventory only.

### Domain Stress Index

DSI measures how much domain variability the dataset actually tests. Each item is scored 0-3, then scaled to 0-100:

- patient diversity by age, sex, epilepsy syndrome, and clinical history;
- seizure type diversity, including convulsive and non-convulsive events when relevant;
- nocturnal and diurnal recordings;
- hospital and home contexts;
- motion, sleep/wake, noise, and normal daily activity;
- wearable placement variability;
- multi-device or cross-device recordings;
- long-term monitoring duration;
- medication/context metadata;
- external site or multi-center acquisition;
- patient-independent split possible;
- prospective or external validation possible.

High MTS with low DSI means strong proof in a narrow domain. High DSI with low MTS means broad but weak evidence. Both axes must be reported separately.

## C. Dataset tiers

T1: strong clinical dataset
- Raw or fully traceable signals, stable source, clear license.
- Expert/neurologist annotation, ideally video-EEG confirmed.
- Onset and offset available, seizure type documented, temporal uncertainty bounded.
- Multi-patient, enough interictal duration for false alarms/day, split manifest clean.
- Supports E2-PD or E2-PI depending on split; with external or leave-site-out
  validation, possibly E3.

T2: useful but incomplete dataset
- Good signals and usable labels, but one or more limitations: partial raw access, limited diversity, uncertain onset, weak metadata, small patient count, short interictal duration, or single-center bias.
- Supports E1 or narrow E2-PD/E2-PI, depending on split and label audit.

T3: exploratory or inventory dataset
- Labels are proxy, weak, derived, incomplete, or non-auditable.
- Missing raw traceability, unclear license, insufficient seizure/interictal denominator, or major unquantified artifacts.
- Supports only E0/E1. It must not support clinical or generalization claims.

## D. Claim Eligibility Matrix

Claims are gated by the weakest required evidence, not by the best metric.

| Claim level | Allowed statement | Minimum evidence |
| --- | --- | --- |
| E0 | No scientific claim; software or data plumbing only | Synthetic data, mock data, incomplete labels, or failed audit |
| E1 | Structural validity of the protocol | Reproducible pipeline, label/split logic tested, baselines run, failures preserved |
| E2-PD | Narrow patient-dependent operational claim | T1/T2 dataset, audited labels, validation-only thresholding, no leakage, event metrics, FAR/day, latency definition, patient-dependent split, failure trace |
| E2-PI | Narrow patient-independent operational claim | T1/T2 dataset, audited labels, validation-only thresholding, no leakage, event metrics, FAR/day, latency definition, patient-independent split, failure trace |
| E3 | External/generalizable research claim | T1 evidence, patient-independent split, external dataset/site or leave-site-out validation, subgroup results, failure-rate bound, hardware latency if real-time is claimed |
| E4 | Pre-clinical or clinical-grade claim | Prospective protocol, clinician-adjudicated ground truth, prespecified safety endpoints, risk analysis, device/regulatory pathway review, intended-use population, and independent validation |

Hard gates:

- No E3 from patient-dependent validation alone.
- No E2-PI from patient-dependent validation alone.
- No "real-time" claim without measured target-hardware latency.
- No "low false positives" claim without false alarms per 24h and distribution across patients.
- No "clinical-ready" or "safe" claim from retrospective public data alone.
- Leakage, nonconforming splits, or undisclosed exclusions invalidate the run for E2-PD/E2-PI/E3/E4.

## E. Epi-Score

The Epi-Score summarizes model behavior under a fixed protocol. It must not replace the Claim Eligibility Matrix.

Let each axis score be in [0, 1]:

- `S_perf`: event detection performance.
- `S_safety`: clinical safety burden.
- `S_robust`: inter-patient and cross-domain robustness.
- `S_stability`: variance, worst-case patients, fold stability, missing/failure rate.
- `S_latency`: detection delay and streaming runtime.
- `S_edge`: embedded viability.
- `S_cal`: calibration and uncertainty quality.

Proposed pre-registered weights:

```text
performance          0.20
clinical safety      0.25
robustness           0.15
stability            0.10
latency              0.10
embedded viability   0.10
calibration          0.10
```

Formula:

```text
EpiScore = 100 * product_c(S_c ^ w_c)
           * exp(-lambda * max(0, F_floor - min_c S_c))
```

Default preregistration:

```text
lambda = 2.0
F_floor = 0.35
```

Rationale:

- The geometric product prevents a model with excellent sensitivity but catastrophic false alarms from winning.
- The floor penalty makes the weakest axis visible.
- Safety receives the largest weight because a seizure detector is an alarm system, not a pure classifier.
- Calibration and embedded viability remain explicit because IoT deployment depends on trustable probability and resource feasibility.

### Example axis construction

`S_perf` may combine event sensitivity, event F1, and onset detection delay.  
`S_safety` may combine false negatives, false alarms/24h, alarm duration, and alarm clustering.  
`S_robust` may combine leave-one-subject-out performance, cross-dataset degradation, seizure-type subgroup performance, and artifact stress tests.  
`S_stability` may combine patient-level variance, worst-case patient, fold variance, and missing/failure rate.  
`S_latency` may combine median/p95 detection delay and p95 streaming inference time.  
`S_edge` may combine RAM, CPU, energy proxy, storage, and cloud dependency.  
`S_cal` may combine Brier score, expected calibration error, reliability curves, and abstention behavior.

Every mapping from raw metric to subscore must be fixed before the benchmark run.

## F. Failure and sentinel policy

Failures are scientific observations. They must stay in the denominator and in the report.

Sentinel events:

- `PREDICTION_MISSING`: no prediction for a patient, recording, or required segment.
- `SEGMENT_CRASH`: inference crashes on a segment.
- `NAN_OR_INF_OUTPUT`: non-finite score or probability.
- `LATENCY_BUDGET_EXCEEDED`: runtime or detection delay violates preregistered bound.
- `POST_EVENT_ALARM`: first alarm occurs after the clinically useful detection window or after seizure offset when the task is onset detection.
- `FAR_EXPLOSION`: false alarms exceed a prespecified maximum alarm burden.
- `PATIENT_LEAKAGE`: training information crosses patient boundary.
- `TEMPORAL_LEAKAGE`: future data, overlapping windows, normalization, or thresholding leaks into validation/test.
- `SPLIT_NONCOMPLIANT`: run uses a split different from the frozen manifest.
- `LABEL_UNAUDITED`: label provenance or onset/offset uncertainty not cleared.
- `DEVICE_MISSINGNESS`: sensor dropout prevents a required modality from being observed.
- `HARDWARE_UNMEASURED`: real-time or edge claim attempted without target hardware measurement.

Reporting rules:

- Do not impute missing predictions silently.
- Do not average only over surviving patients without a survivor caveat.
- Report failure counts by patient, seizure type, sensor modality, recording context, and split.
- A model with failures can still be useful, but its claim level and robustness axis must reflect those failures.
- Leakage failures invalidate the affected run rather than merely penalizing it.

## G. Baselines

Baselines are not decorative. They are experimental controls.

Minimum baselines:

- Always negative.
- Random alarms calibrated by prevalence or alarm budget.
- Rate-matched random baseline preserving recording duration.
- Time-of-day or patient-cycle prior when longitudinal data exist.
- Simple motion threshold from ACC/GYR.
- Simple EEG energy, line length, or bandpower threshold.
- Simple HR/ECG tachycardia or autonomic threshold when available.
- Logistic regression or gradient boosting on transparent handcrafted features.
- Patient-specific threshold baseline.
- Small CNN/GRU/TCN streaming baseline with validation-only thresholding.

Interpretation rule:

If a complex model does not beat the relevant simple baseline under event sensitivity, false alarms/day, latency, and failure rate, the result is still valuable, but it is not evidence of model superiority.

## H. Mandatory splits

Every result must declare which split family it belongs to:

- Patient-dependent: allowed for personalization or within-patient adaptation, not generalization.
- Patient-independent: required for new-patient claims.
- Leave-one-subject-out: strong small-cohort stress test.
- Temporal split: required when long-term patient-specific monitoring is evaluated.
- Recording-boundary temporal split: preferred when within-recording cuts could leak preprocessing or artifacts.
- Center/site split: required for multi-site external validity when available.
- External dataset validation: required for E3 generalization.
- Home vs hospital split: required if the claim mentions home deployment.

Threshold selection must occur on validation data only. Feature normalization, artifact filters, calibration, and patient priors must record fit scope.

## I. Metrics adapted to seizure detection

Primary metrics:

- Event-based sensitivity.
- False alarms per 24h, reported as mean, median, p95, and per-patient distribution.
- Detection latency from annotated onset, with median and p95.
- Event-level precision and event F1.
- Time in alarm or time-in-warning.
- Missed seizure count and missed seizure rate.
- Per-patient and worst-case patient performance.
- Missing prediction rate and failure rate.
- Calibration: Brier score, expected calibration error, reliability curve.
- Hardware metrics: p50/p95 inference time, RAM, CPU, energy proxy, connectivity dependency.

Secondary metrics:

- AUROC and AUPRC, reported with class imbalance caveats.
- Window-level metrics only as diagnostics, not as main evidence.
- Subgroup metrics by seizure type, sleep/wake, motion/artifact burden, sensor modality, and site.

Metrics to avoid as primary evidence:

- Accuracy.
- Specificity without event-level alarm burden.
- Mean-only scores with no patient distribution.
- Best-threshold results selected on test data.

## J. Result Bundle

Each run must produce a result bundle:

```text
result_bundle/
  config.yaml
  dataset_evidence_card.yaml
  split_manifest.csv
  claim_eligibility_report.md
  code_manifest.json
  environment.lock
  raw_input_checksums.json
  processed_input_checksums.json
  training_log.jsonl
  inference_log.jsonl
  predictions.parquet
  event_detections.parquet
  alarm_episodes.parquet
  per_patient_metrics.csv
  subgroup_metrics.csv
  calibration_report.md
  latency_report.md
  hardware_report.md
  failure_traces.jsonl
  figures/
  reproduction_command.txt
  interpretation_report.md
```

The interpretation report must state:

- what the run proves;
- what it does not prove;
- which claim level is allowed;
- which failures or dataset limits constrain interpretation;
- whether thresholds, calibration, and normalization were fit without leakage.

## K. Minimal experimental plan

Phase 0: protocol lock
- Freeze task definition, metrics, thresholds, FAR budgets, split rules, baselines, and failure policy.

Phase 1: dataset audit
- Complete Evidence Card, compute MTS/DSI, verify license, raw traceability, missingness, artifacts, annotation provenance, and onset/offset uncertainty.

Phase 2: labels and splits
- Generate canonical events and windows. Run label timeline audit on 5-10 seizures per dataset at minimum. Freeze patient, temporal, and external splits.

Phase 3: sanity baselines
- Always-negative, random/rate-matched, sensor-threshold, and transparent ML baselines.

Phase 4: model ladder
- Small interpretable model, classical ML, compact deep model, streaming IoT model.

Phase 5: evaluation and result bundles
- Produce event metrics, FAR/day, latency, calibration, per-patient distributions, failures, and claim eligibility.

Phase 6: interpretation
- Compare naive ranking to protocol ranking. Highlight overclaim traps. Report negative and weak results explicitly.

## Worked example: naive leaderboard versus EpiBench

Illustrative numbers only:

| Model | Naive view | Sensitivity | FAR/24h | Median latency | Failure rate | EpiBench interpretation |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| A: deep detector | Wins by sensitivity | 0.96 | 200 | 4 s | 3% | Not clinically credible under alarm burden; E2-PD/E2-PI blocked unless the intended use explicitly accepts extreme alarms |
| B: classical ML | Middle | 0.86 | 7 | 12 s | 0% | Useful narrow E2-PD or E2-PI candidate, depending on split, if labels and split are clean |
| C: streaming IoT | Lower sensitivity | 0.78 | 0.8 | 8 s | 1% | More defensible for low-burden alarm use, especially if edge latency is measured |
| D: always negative | High accuracy | 0.00 | 0 | n/a | 0% | Demonstrates why accuracy is not evidence |

Naive conclusion:

> Model A is best.

EpiBench conclusion:

> Model A detects many seizures but creates an unacceptable alarm burden. Model C may support a narrower, more honest claim if the intended use prioritizes low false alarms and timely edge operation. The result is not "C is clinically ready"; it is "C has a more defensible evidence profile under this protocol."

## Figures to produce

1. Raw-to-result evidence pipeline.
2. Dataset Evidence Card dashboard with MTS and DSI.
3. Task timeline: interictal, preictal, ictal, postictal, detection window, alarm refractory period.
4. Split diagram showing patient-dependent, patient-independent, temporal, LOSO, and external validation.
5. Naive leaderboard versus protocol-adjusted interpretation.
6. Sensitivity versus false alarms/24h curve.
7. Detection latency ECDF and p95 latency by patient.
8. Per-patient performance violin/box plots with worst-case patient highlighted.
9. Failure-trace heatmap by patient and model.
10. Edge Pareto plot: sensitivity, FAR/day, latency, RAM/energy proxy.
11. Calibration reliability diagrams.
12. Claim Eligibility Matrix heatmap.

## Scientific risks

- Label uncertainty may dominate model differences.
- Seizure onset may be physiologically gradual but annotated discretely.
- Convulsive seizures may be easier than focal non-motor seizures, creating a false sense of generality.
- Hospital video-EEG data may not represent home wearable deployment.
- Short recordings may underestimate false alarms/day.
- Patient overlap, temporal overlap, normalization leakage, and threshold leakage can inflate results.
- Models may learn device/site artifacts rather than seizure physiology.
- Wearable missingness and adherence may be non-random.
- External datasets may differ in sensor, montage, annotation policy, and patient population.
- Edge claims can be overstated if only desktop inference is measured.
- Public retrospective data cannot establish clinical safety by itself.

## Questions for the clinical or medical supervisor

1. Which seizure types are clinically in scope: generalized tonic-clonic, focal impaired awareness, focal motor, non-motor, nocturnal only, or all?
2. What is the intended use: caregiver alert, clinician review, diary support, emergency alarm, or research-only detection?
3. What detection delay is still useful for the intended use?
4. What false alarm burden is tolerable per patient per day or night?
5. Should repeated seizures in clusters count as separate events or one clinical episode?
6. How should postictal periods be excluded or modeled?
7. What onset definition should be used when EEG onset, clinical onset, and wearable signal onset disagree?
8. What temporal uncertainty should be attached to onset/offset labels?
9. Which annotation source is authoritative when metadata conflict?
10. Which patient subgroups must be reported separately?
11. Is home deployment a target in this thesis, or only a future claim?
12. What is the minimum prospective validation needed before any clinical language is acceptable?
13. What harms should be represented explicitly: missed seizures, alarm fatigue, sleep disruption, caregiver burden, false reassurance, battery failure, connectivity loss?
14. What regulatory boundary should be respected for software that analyzes biosignals and generates time-critical alerts?

## Anti-overclaim rules

Forbidden without the corresponding evidence:

- "Our model detects epilepsy."
- "Clinical-ready."
- "SOTA" without reproduced external comparison under the same protocol.
- "Generalizable" without patient-independent and external validation.
- "Real-time" without target-hardware latency.
- "Low false positives" without false alarms/day and patient-level distribution.
- "Safe" without prospective safety evidence and risk analysis.

Preferred language:

- "This is an E1 structural-validity result."
- "The claim is limited to this dataset, sensor stack, seizure type, and split."
- "False alarms and latency bound the interpretation."
- "The result supports a narrow E2-PD or E2-PI operational claim, not E3 generalization."
- "Failures are reported as part of the evidence, not removed from the denominator."

## Project-specific fit

The current EpiTwin-Open repository already contains many ingredients that map naturally to EpiBench:

- SPH/SOP labels and postictal exclusion for forecasting-style tasks.
- Patient-wise, temporal, recording-wise, and center-wise split utilities.
- Leakage audits.
- Event-level metrics, FAR/day, Time-in-Warning, Brier score, and ECE.
- Random, cycle, HR/ACC, transparent rule, and small deep baselines.
- Label audit sheets, failure taxonomy, clinical utility reports, calibration reports, leaderboard schemas, and paper artifact packages.

The missing scientific step is to explicitly name the evidence architecture and enforce claim eligibility:

> EpiTwin-Open should not be presented as a model-first seizure detector. It should be presented as EpiBench-compatible evidence infrastructure for determining what is actually detectable or forecastable from public wearable seizure datasets under alarm-burden, observability, leakage, and edge constraints.

## Reference anchors

- ILAE operational classification of seizure types, useful for seizure-type taxonomy: https://www.ilae.org/guidelines/definition-and-classification/operational-classification-2017
- CHB-MIT Scalp EEG Database, a common public EEG detection dataset with annotated seizure onsets/offsets: https://physionet.org/content/chbmit/1.0.0/
- TUH EEG resources and TUSZ corpus, including manually annotated seizure events: https://isip.piconepress.com/projects/nedc/html/tuh_eeg/
- SzCORE seizure detection evaluation framework, including event-based metrics and false alarms/day: https://epilepsybenchmarks.com/framework/
- SeizeIT2 wearable focal epilepsy dataset, relevant for multimodal wearable IoT evaluation: https://arxiv.org/abs/2502.01224
- FDA CDS software FAQ, relevant for caution around signal-analysis software and time-critical alerts: https://www.fda.gov/medical-devices/software-medical-device-samd/clinical-decision-support-software-frequently-asked-questions-faqs
