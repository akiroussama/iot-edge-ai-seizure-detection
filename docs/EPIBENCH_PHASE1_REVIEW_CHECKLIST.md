# EpiBench Phase 1 Review Checklist

Date: 2026-05-24  
Phase: 1 closeout review  
Spec under review: `docs/EPIBENCH_SPEC_V1.md`  
Adjudication examples: `docs/EPIBENCH_PHASE1_ADJUDICATION_EXAMPLES.md`

## Purpose

This checklist decides whether Phase 1 is ready to close and whether EpiBench can move to Phase 2: machine-readable YAML and JSON Schemas.

Phase 1 is not a writing exercise. It is a scientific hardening step. The checklist therefore asks whether the protocol is:

- deterministic enough to encode;
- conservative enough to prevent overclaim;
- auditable enough for independent reviewers;
- clinically humble enough to avoid false deployment language;
- concrete enough to produce result-bundle validation rules.

## Review status values

Use exactly one status per item:

| Status | Meaning |
| --- | --- |
| PASS | acceptable for Phase 2 |
| PASS_WITH_MINOR_REVISIONS | acceptable after non-blocking edits |
| BLOCKED | must be resolved before Phase 2 |
| NOT_APPLICABLE | genuinely not relevant to this item |

Any `BLOCKED` item blocks Phase 1 closeout.

## Required reviewers

| Reviewer role | Required | Responsibility |
| --- | --- | --- |
| Scientific owner | yes | BSEBench-like evidence logic, claim ladder coherence |
| Clinical reviewer or clinical proxy | strongly recommended; required before clinical wording in paper | seizure taxonomy, onset/offset, intended use, clinical humility |
| Reproducibility reviewer | yes | rubrics, split logic, auditability, inter-reviewer reproducibility |
| IoT/embedded reviewer | recommended before Track E | latency, memory, energy, sensor missingness, hardware claims |
| External dry-run reviewer | recommended before Phase 2 closeout | can apply spec without author assistance |

If no clinical reviewer is available, E4-related wording MUST remain explicitly provisional and no clinical-grade claim may be asserted.

## Section S - SOTA alignment and non-reinvention

| ID | Check | Status | Reviewer | Notes |
| --- | --- | --- | --- | --- |
| S1 | Existing event-scoring frameworks, especially SzCORE-style scoring, are reused or mapped where compatible. |  |  |  |
| S2 | EpiBench states clearly that it complements rather than replaces existing event-scoring frameworks. |  |  |  |
| S3 | ILAE seizure classification is used or mapped when seizure-type metadata permit. |  |  |  |
| S4 | TRIPOD+AI, STARD-AI, DECIDE-AI, SPIRIT-AI/CONSORT-AI, and FUTURE-AI are positioned correctly by study stage. |  |  |  |
| S5 | FDA CDS guidance is reflected only as regulatory-boundary caution, not as a claim of regulatory compliance. |  |  |  |
| S6 | Every new EpiBench rule is labeled ADOPT, MAP, EXTEND, or DIVERGE relative to existing SOTA. |  |  |  |
| S7 | Any DIVERGE decision has a written rationale. |  |  |  |
| S8 | Citation integrity has been checked for sources used to justify normative rules. |  |  |  |

## Section A - Normative language

| ID | Check | Status | Reviewer | Notes |
| --- | --- | --- | --- | --- |
| A1 | `MUST`, `MUST NOT`, `SHOULD`, `MAY`, `FAIL-CLOSED`, `CLAIM CEILING`, `SENTINEL`, and `RESULT BUNDLE` are defined. |  |  |  |
| A2 | Certification is defined as scientific certification only. |  |  |  |
| A3 | Forbidden wording includes clinical approval, clinical certification, safe deployment, and unbounded real-time claims. |  |  |  |
| A4 | Missing evidence lowers claims rather than being inferred upward. |  |  |  |
| A5 | The spec avoids marketing language and unsupported prestige claims. |  |  |  |

## Section B - MTS rubrics

| ID | Check | Status | Reviewer | Notes |
| --- | --- | --- | --- | --- |
| B1 | MTS measures metrological trustworthiness, not model performance. |  |  |  |
| B2 | The 0/1/2/3 scoring scale is defined. |  |  |  |
| B3 | All 21 MTS items have score descriptions. |  |  |  |
| B4 | Each MTS item has required evidence. |  |  |  |
| B5 | MTS fail-closed effects are explicit. |  |  |  |
| B6 | MTS calculation is explicit and reproducible. |  |  |  |
| B7 | T1 cannot be obtained when T1-blocking evidence is missing. |  |  |  |
| B8 | Label audit and onset/offset evidence are strong enough for seizure-specific claims. |  |  |  |

## Section C - DSI rubrics

| ID | Check | Status | Reviewer | Notes |
| --- | --- | --- | --- | --- |
| C1 | DSI measures domain stress, not label quality. |  |  |  |
| C2 | The 0/1/2/3 DSI scale is defined. |  |  |  |
| C3 | All 20 DSI items have score descriptions. |  |  |  |
| C4 | DSI cannot compensate for weak MTS. |  |  |  |
| C5 | Low DSI limits external or deployment claims even with high MTS. |  |  |  |
| C6 | Home, cross-device, multisite, and prospective claims require corresponding DSI evidence. |  |  |  |

## Section D - Dataset tiers

| ID | Check | Status | Reviewer | Notes |
| --- | --- | --- | --- | --- |
| D1 | T1/T2/T3 definitions are clear and non-punitive. |  |  |  |
| D2 | T1/T2/T3 are derived from MTS and fail-closed rules. |  |  |  |
| D3 | DSI is correctly separated from dataset tier. |  |  |  |
| D4 | T3 is limited to E1 maximum. |  |  |  |
| D5 | T1 does not imply E3 or E4 by itself. |  |  |  |

## Section E - Track separation

| ID | Check | Status | Reviewer | Notes |
| --- | --- | --- | --- | --- |
| E1 | Tracks D, W, F, and E are defined with distinct scientific questions. |  |  |  |
| E2 | Each track has required definitions and primary metrics. |  |  |  |
| E3 | Detection cannot be silently reinterpreted as forecasting. |  |  |  |
| E4 | Forecasting cannot be silently reinterpreted as detection. |  |  |  |
| E5 | Real-time or edge claims require Track E evidence. |  |  |  |

## Section F - Claim ladder

| ID | Check | Status | Reviewer | Notes |
| --- | --- | --- | --- | --- |
| F1 | Claims E0, E1, E2-PD, E2-PI, E3, and E4 are defined. |  |  |  |
| F2 | E2-PD and E2-PI are separated everywhere. |  |  |  |
| F3 | Patient-dependent results cannot support new-patient generalization. |  |  |  |
| F4 | E3 requires external, multisite, or leave-site-out evidence. |  |  |  |
| F5 | E4 requires prospective intended-use evidence and clinician-adjudicated ground truth. |  |  |  |
| F6 | Public retrospective datasets alone cannot support E4. |  |  |  |

## Section G - Claim ceiling matrix

| ID | Check | Status | Reviewer | Notes |
| --- | --- | --- | --- | --- |
| G1 | Claim ceiling is computed as the minimum of dataset, split, label, failure, validation, hardware, and track ceilings. |  |  |  |
| G2 | Dataset ceiling is explicit. |  |  |  |
| G3 | Split ceiling is explicit. |  |  |  |
| G4 | Label audit ceiling is explicit. |  |  |  |
| G5 | Failure ceiling is explicit. |  |  |  |
| G6 | Hardware ceiling is explicit. |  |  |  |
| G7 | Blocking reasons must be reported. |  |  |  |

## Section H - Failure and sentinel consequences

| ID | Check | Status | Reviewer | Notes |
| --- | --- | --- | --- | --- |
| H1 | Failure traces are mandatory for complete runs. |  |  |  |
| H2 | Leakage sentinels block E2-PD/E2-PI or higher. |  |  |  |
| H3 | Missing failure trace blocks `Run-Complete`. |  |  |  |
| H4 | NaN/Inf outputs have explicit consequences. |  |  |  |
| H5 | FAR explosion blocks low-false-positive interpretations. |  |  |  |
| H6 | Hardware-unmeasured blocks real-time and edge-measured claims. |  |  |  |
| H7 | Survivor-only averages are forbidden without caveat and denominator reporting. |  |  |  |

## Section I - Adjudication examples

| ID | Check | Status | Reviewer | Notes |
| --- | --- | --- | --- | --- |
| I1 | Examples cover high-MTS/low-DSI hospital EEG. |  |  |  |
| I2 | Examples cover wearable multimodal incomplete evidence. |  |  |  |
| I3 | Examples cover proxy-label exploratory evidence. |  |  |  |
| I4 | Examples cover patient-dependent high performance. |  |  |  |
| I5 | Examples cover leakage despite strong metrics. |  |  |  |
| I6 | Examples cover real-time claim without hardware evidence. |  |  |  |
| I7 | Examples demonstrate ranking/claim changes caused by evidence constraints. |  |  |  |

## Section J - Inter-reviewer reproducibility

| ID | Check | Status | Reviewer | Notes |
| --- | --- | --- | --- | --- |
| J1 | Two reviewers can independently score the same Evidence Card. |  |  |  |
| J2 | MTS difference is <= 5 points. |  |  |  |
| J3 | DSI difference is <= 8 points. |  |  |  |
| J4 | Dataset tier matches exactly. |  |  |  |
| J5 | Granted claim matches exactly. |  |  |  |
| J6 | Critical blocking reasons match. |  |  |  |

## Section K - Phase 2 readiness

| ID | Check | Status | Reviewer | Notes |
| --- | --- | --- | --- | --- |
| K1 | Rules are specific enough to encode in YAML. |  |  |  |
| K2 | Fields needed for JSON Schemas are identified. |  |  |  |
| K3 | Claim gates are deterministic enough for unit tests. |  |  |  |
| K4 | Failure sentinels are machine-detectable or reportable. |  |  |  |
| K5 | No Phase 1 rule depends on unbounded author discretion. |  |  |  |

## Required validation scenarios

Before Phase 1 closeout, reviewers must confirm these expected outcomes:

| Scenario | Expected result | Status | Notes |
| --- | --- | --- | --- |
| mock data complete | E1 maximum |  |  |
| T3 real dataset | E1 maximum |  |  |
| T2 patient-dependent clean | E2-PD maximum |  |  |
| T2 patient-independent clean | E2-PI maximum |  |  |
| T1 patient-independent plus external validation | E3 candidate |  |  |
| T1 retrospective only | E4 blocked |  |  |
| leakage failure | E1 maximum |  |  |
| missing failure trace | `Run-Complete` blocked |  |  |
| real-time claim without hardware report | real-time/edge claim blocked |  |  |
| SPH/SOP forecasting without event detection outputs | Track F only; Track D blocked |  |  |

## Phase 1 closeout decision

Use this block at closeout:

```text
Phase 1 status: PASS / PASS_WITH_MINOR_REVISIONS / BLOCKED
Normative vocabulary:
MTS rubrics:
DSI rubrics:
Dataset tiers:
Track separation:
Claim ladder:
Claim ceiling matrix:
Failure consequence matrix:
Adjudication examples:
Anti-overclaim wording:
Phase 2 readiness:
Blocking issues:
Minor revisions:
Decision owner:
Decision date:
```

## Go/no-go rule

Phase 2 may begin only if:

- no item is `BLOCKED`;
- E2-PD/E2-PI separation is accepted;
- MTS/DSI rubrics are accepted;
- claim ceiling logic is accepted;
- leakage and failure-trace consequences are accepted;
- certification wording is accepted as scientific, not clinical.
