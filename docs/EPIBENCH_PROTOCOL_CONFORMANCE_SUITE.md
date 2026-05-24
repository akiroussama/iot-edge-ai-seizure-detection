# EpiBench Protocol Conformance Suite

## Purpose

The conformance suite is the protocol equivalent of a scientific unit test. It proves that EpiBench v1.0-draft does not merely describe claim gates in prose: the reference implementation must reproduce expected verdicts on canonical positive and negative cases.

This is a BSEBench-like requirement. A standard that cannot test its own rules is not yet a standard.

## Executable Suite

Normative suite:

```text
configs/epibench/conformance_suite_v1.yaml
```

Run:

```powershell
python scripts\epibench.py run-conformance-suite configs\epibench\conformance_suite_v1.yaml
```

The command certifies each declared result bundle and compares the generated claim against the expected claim.

## Current Cases

| Case | Scientific purpose | Expected claim |
| --- | --- | --- |
| `clean_loso_t1_reaches_e2_pi` | A clean T1-like LOSO package can support bounded patient-independent evidence | `E2-PI` |
| `patient_dependent_requested_e2_pi_downgrades_to_e2_pd` | Patient-dependent evidence cannot become patient-independent by wording | `E2-PD` |
| `leakage_high_metric_downgrades_to_e1` | Excellent naive metrics cannot rescue leakage or threshold misuse | `E1` |
| `preliminary_msg_is_claim_limited_to_e1` | Real preliminary wearable forecasting evidence remains claim-limited when labels and core MTS are incomplete | `E1` |
| `preliminary_seizeit2_single_subject_is_e1` | A single-subject local check cannot support an operational claim | `E1` |

## Dataset Tier Fail-Closed Rule

Dataset tier is no longer trusted solely because an author declares it.

EpiBench computes an effective tier from MTS evidence:

- missing core MTS items are scored as zero;
- MTS mean and item floor must both satisfy the tier threshold;
- if declared tier is higher than effective tier, the effective tier controls claims and badges;
- DSI can describe domain stress, but it cannot raise the tier.

This matters because a dataset may be useful but not yet claim-grade. For example, the preliminary MSG package declares `T2`, but the effective tier is `T3` because core MTS evidence such as synchronization and missingness are incomplete. The claim remains `E1` because label evidence and failure sentinels also block stronger interpretation.

## Acceptance Criteria

The conformance suite must pass before:

- tagging an EpiBench release candidate;
- submitting a paper using EpiBench claims;
- accepting external result bundles as EpiBench-certified;
- changing YAML thresholds, claim gates, or failure consequences.

## Expansion Rules

Every new normative rule must add at least one conformance case:

- one positive case where the claim is allowed;
- one negative case where the claim is blocked or lowered.

Examples:

- `E3` external validation allowed;
- `E3` blocked without external validation;
- `E4` prospective evidence allowed;
- `E4` blocked without prospective protocol;
- real-time wording allowed with hardware evidence;
- real-time wording forbidden without hardware evidence.

## Release Blocker

If the conformance suite fails, EpiBench cannot be released as a standard. The failure must be resolved either by fixing the implementation or by changing the normative expectation with documented rationale.
