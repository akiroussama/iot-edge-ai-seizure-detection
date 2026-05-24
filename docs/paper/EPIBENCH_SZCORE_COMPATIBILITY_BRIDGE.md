# EpiBench SzCORE Compatibility Bridge

## Purpose

This bridge prevents EpiBench from being interpreted as a replacement for existing seizure event-scoring work. For Track `D`, EpiBench should consume compatible event-scoring outputs whenever available and add evidence, failure, claim, and IoT viability semantics around them.

## Scope

This bridge applies to seizure detection tasks where outputs can be expressed as event detections or alarm episodes with seizure-level matching.

It does not automatically apply to:

- early warning where lead time is the primary endpoint;
- forecasting where SPH/SOP risk horizons and calibration matter;
- embedded viability where runtime, memory, and energy are primary.

## Mapping Table

| External event-scoring concept | EpiBench field | Relationship |
| --- | --- | --- |
| Event sensitivity | `metrics.event_sensitivity` | MAP |
| Precision | `metrics.event_precision` or `metrics.precision` | MAP |
| F1 score | `metrics.event_f1` or `metrics.f1_score` | MAP |
| False positives per day | `metrics.false_alarms_per_24h` | MAP |
| Detection delay | `metrics.detection_latency_seconds_*` | MAP if delay definition matches |
| Event matching rule | `result_bundle.track` + split/report metadata | MAP with explicit compatibility note |
| Per-patient performance | `metrics.per_patient_distribution` or supplemental table | EXTEND if not exported |
| Failure cases | `failure_trace.sentinels` | EXTEND |
| Dataset tier | `dataset_card.tier` | EXTEND |
| Claim ceiling | `claim_eligibility.final_claim` | EXTEND |
| Hardware viability | `result_bundle.hardware` + `EpiBench-Edge-Measured` | EXTEND |

## Compatibility Requirements

A SzCORE-compatible Track D result can be imported into EpiBench only if:

1. the scoring output is tied to a declared dataset and split;
2. event matching rules are recorded;
3. false positives per day are available or derivable;
4. per-patient denominators are preserved or the limitation is declared;
5. predictions that failed or were omitted are accounted for in the failure trace;
6. threshold selection policy is known;
7. label provenance and onset/offset uncertainty are recorded in the Dataset Evidence Card.

## Non-Replacement Language

Allowed:

> EpiBench maps compatible event-scoring outputs into a broader evidence and claim-governance framework.

Forbidden:

> EpiBench replaces SzCORE.

## Required Demonstration Before npj Submission

Before submission, add one small Track D example:

1. produce or import event-level detection metrics using a compatible scoring method;
2. map those metrics into an EpiBench result bundle;
3. certify the bundle;
4. show what EpiBench adds: dataset tier, split claim ceiling, failure trace, badges, and anti-overclaim report.

Current executable demo:

```powershell
python scripts\epibench.py map-szcore --metrics examples\epibench\szcore_bridge_demo\szcore_event_metrics.yaml --base-bundle examples\epibench\pilot_t1_eeg\result_bundle.yaml --out examples\epibench\szcore_bridge_demo\result_bundle.yaml
python scripts\epibench.py certify examples\epibench\szcore_bridge_demo\result_bundle.yaml --out reports\epibench_szcore_bridge_claim.json --report reports\epibench_szcore_bridge_claim.md
```

The demo uses a SzCORE-style export, not the SzCORE package itself. Before publication, this should be replaced by a real output emitted by the official scoring tool or by a documented compatible export.

## Reviewer Defense

If reviewers argue that EpiBench reinvents event scoring, the response is:

EpiBench is not an event scorer. It is a claim-certification layer. It consumes event-scoring outputs where compatible and adds missing evidence constraints: dataset qualification, split validity, label audit, failure preservation, edge viability, and deterministic claim ceilings.
