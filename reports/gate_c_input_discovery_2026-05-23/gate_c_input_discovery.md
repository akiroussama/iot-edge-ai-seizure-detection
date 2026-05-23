# Gate C Input Discovery

**Status:** `blocked_missing_gate_c_inputs`

This report scans local table artifacts for files that satisfy the minimum
Gate C role contracts. It does not freeze artifacts and it does not make any
benchmark row citable.

## Summary

- Files scanned: `69`
- Readable tables: `69`
- Missing roles: `events, labels, splits`

## Role-Ready Counts

- events: 0
- labels: 0
- splits: 0

## Candidate Files

_No Gate C role-ready candidate files found._

## Next Action

If any required role is missing, materialize the real frozen `events`, `labels`,
and `splits` artifacts before running `scripts/build_gate_c_freeze_package.py`.
