# Gate C Source Discovery

**Status:** `blocked_missing_gate_c_sources`

This report scans local tables for source artifacts that can feed
`scripts/materialize_gate_c_inputs.py`. It does not materialize labels, freeze
splits, or make any benchmark row citable.

## Summary

- Files scanned: `70`
- Readable tables: `70`
- Missing source roles: `recordings, events`

## Source-Ready Counts

- recordings: 0
- events: 0

## Candidate Source Files

_No Gate C source-ready candidate files found._

## Next Action

If either source role is missing, recover or generate real `recordings` and
`events` tables before running `scripts/materialize_gate_c_inputs.py`.
