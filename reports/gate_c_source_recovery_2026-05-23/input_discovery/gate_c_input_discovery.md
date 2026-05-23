# Gate C Input Discovery

**Status:** `gate_c_inputs_available`

This report scans local table artifacts for files that satisfy the minimum
Gate C role contracts. It does not freeze artifacts and it does not make any
benchmark row citable.

## Summary

- Files scanned: `3`
- Readable tables: `3`
- Missing roles: `none`

## Role-Ready Counts

- events: 1
- labels: 1
- splits: 2

## Candidate Files

| path | candidate_roles | row_count |
| --- | --- | --- |
| data/processed/msg/gate_c_inputs_sph60_sop1440/events.csv | events | 768 |
| data/processed/msg/gate_c_inputs_sph60_sop1440/labels.csv | labels,splits | 49577 |
| data/processed/msg/gate_c_inputs_sph60_sop1440/splits.csv | splits | 49577 |

## Next Action

If any required role is missing, materialize the real frozen `events`, `labels`,
and `splits` artifacts before running `scripts/build_gate_c_freeze_package.py`.
