# Gate C Source Discovery

**Status:** `gate_c_sources_available`

This report scans local tables for source artifacts that can feed
`scripts/materialize_gate_c_inputs.py`. It does not materialize labels, freeze
splits, or make any benchmark row citable.

## Summary

- Files scanned: `5`
- Readable tables: `5`
- Missing source roles: `none`

## Source-Ready Counts

- recordings: 1
- events: 1

## Candidate Source Files

| path | candidate_roles | row_count |
| --- | --- | --- |
| data/processed/msg/events.parquet | events | 768 |
| data/processed/msg/recordings.parquet | recordings | 2068 |

## Next Action

If either source role is missing, recover or generate real `recordings` and
`events` tables before running `scripts/materialize_gate_c_inputs.py`.
