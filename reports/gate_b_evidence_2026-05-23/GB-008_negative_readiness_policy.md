# GB-008 SeizeIT2 Negative Readiness Policy

Reviewer: O. Akir
Review date: 2026-05-23
Decision: RESOLVED

## Scope

This evidence closes the SeizeIT2 negative-readiness action for Gate B.

## Decision

Non-ready SeizeIT2 tracks must be preserved as explicit negative readiness
findings in the appendix/reporting layer. They must not be silently dropped or
converted into positive benchmark coverage.

## Rationale

Negative readiness rows are scientifically useful because they document the
limits of current public/local artifacts. Removing them would hide a material
boundary of reproducibility. Promoting them would overclaim dataset readiness.
The correct treatment is explicit negative evidence.

## Consequence

Final reporting must retain SeizeIT2 non-ready tracks as appendix/readiness
findings with clear non-citable or excluded status. This protects the main
benchmark table while preserving the audit value of the failed readiness checks.
