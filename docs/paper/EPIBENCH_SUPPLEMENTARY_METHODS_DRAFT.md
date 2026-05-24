# Supplementary Methods Draft

## S1 Normative Artefact Hierarchy

EpiBench uses four levels of normative authority:

1. Scientific prose specification.
2. Machine-readable YAML standard.
3. JSON Schemas for artefact validation.
4. Reference CLI applying the standard.

The YAML and schemas are intended to prevent post hoc reinterpretation of the protocol.

## S2 Claim Ceiling Computation

The final claim is computed as:

```text
final_claim = min(
  requested_claim,
  dataset_tier_ceiling,
  split_policy_ceiling,
  label_audit_ceiling,
  leakage_audit_ceiling,
  threshold_policy_ceiling,
  failure_status_ceiling,
  hardware_evidence_ceiling,
  track_consistency_ceiling
)
```

The minimum is taken using the ordered ladder:

```text
E0 < E1 < E2-PD < E2-PI < E3 < E4
```

## S3 Failure Sentinel Rationale

| Sentinel | Why it matters | Claim consequence |
| --- | --- | --- |
| `PREDICTION_MISSING` | Missing predictions bias survivor-only metrics | systematic failure lowers claim |
| `SEGMENT_CRASH` | Runtime failure is algorithm behavior | systematic failure lowers claim |
| `NAN_OR_INF_OUTPUT` | Invalid numerical output makes predictions unauditable | blocks operational claim |
| `LATENCY_BUDGET_EXCEEDED` | Late alarms may be clinically useless | blocks real-time wording |
| `POST_EVENT_ALARM` | A warning after onset is not early warning | blocks early-warning success |
| `FAR_EXPLOSION` | Alarm burden can make high sensitivity unusable | may block operational claim |
| `PATIENT_LEAKAGE` | Inflates patient-independent performance | blocks E2+ |
| `TEMPORAL_LEAKAGE` | Inflates temporal generalization | blocks E2+ |
| `SPLIT_NONCOMPLIANT` | Invalidates evaluation design | blocks run completeness |
| `LABEL_UNAUDITED` | Uncertain truth undermines claim | lowers claim |
| `DEVICE_MISSINGNESS` | Wearable missingness affects deployment evidence | must be preserved |
| `HARDWARE_UNMEASURED` | Edge claims require measured hardware evidence | blocks edge/real-time wording |

## S4 Epi-Score Sensitivity Analysis Plan

Before submission, compute Epi-Score under:

- default weights;
- equal weights;
- clinical-safety-heavy weights;
- robustness-heavy weights;
- latency-heavy weights.

Report whether ranking and claim interpretation change. Claims should remain gate-controlled regardless of score weights.

## S5 Baseline Policy

Each dataset must include trivial and simple baselines before complex models:

- always negative;
- rate-matched random;
- threshold rule;
- logistic or linear model;
- small neural baseline if appropriate.

If a complex model fails to beat a trivial baseline under claim-gated evaluation, the result must remain visible.

## S6 Anti-Overclaim Lexicon

Forbidden:

- clinically certified;
- clinically approved;
- ready for clinical deployment;
- detects epilepsy;
- generalized seizure AI;
- real-time without hardware evidence;
- low false positives without false alarms per 24h.

Preferred:

- scientifically certified under EpiBench;
- bounded patient-independent claim;
- retrospective evidence package;
- claim-limited result;
- failure-transparent result.
