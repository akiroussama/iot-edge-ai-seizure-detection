# GB-004 Denominator Policy

Reviewer: O. Akir
Review date: 2026-05-23
Decision: RESOLVED

## Scope

This evidence closes the MSG denominator-integrity action for Gate B. It is a
scope and reporting policy, not a new benchmark result.

## Decision

We adopt a matched-event / prediction-coverable denominator policy for all
citable MSG forecasting rows. Source-event counts remain reported as audit
metadata, but benchmark denominators use only events with sufficient wearable
coverage and valid prediction windows.

All leaderboard rows must expose:

- `source_events`
- `matched_events`
- `prediction_coverable_events`
- `excluded_events`
- `exclusion_reason`

## Rationale

The guardrail rerun found source/matching gaps in MSG. Treating all source
events as forecastable would inflate denominator certainty and weaken the
scientific claim. The adopted policy separates source-data audit coverage from
citable benchmark denominators. This makes the benchmark conservative and
reviewer-defensible.

## Consequence

Rows that cannot declare the source, matched, and prediction-coverable
denominators remain non-citable for the main benchmark table until regenerated
with the required denominator fields.
