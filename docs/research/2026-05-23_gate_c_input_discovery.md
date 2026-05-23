# Gate C Input Discovery

Date: 2026-05-23

## Objective

After adding the Gate C freeze package harness, scan the local repository
artifacts to determine whether any existing table can serve as the frozen
`events`, `labels`, or `splits` input required for a citable Gate C freeze.

## Added Tool

The new CLI is:

```bash
python scripts/discover_gate_c_inputs.py \
  --root data \
  --root reports \
  --out-dir reports/gate_c_input_discovery_2026-05-23
```

It scans local `.csv`, `.tsv`, and `.parquet` tables, then classifies each file
against the minimum Gate C role contracts:

- `events`: patient/recording ids plus seizure start/end timestamps.
- `labels`: patient/recording/window ids, split, forecast label, exclusion flag,
  valid timestamps, no duplicate windows, and at least one positive valid
  forecast window.
- `splits`: split column plus a usable alignment key.

## Local Scan Result

The scanner was run against `data` and `reports`.

```text
scan_status: blocked_missing_gate_c_inputs
files_scanned: 69
readable_tables: 69
events_ready: 0
labels_ready: 0
splits_ready: 0
missing_roles: events, labels, splits
```

Outputs:

- `reports/gate_c_input_discovery_2026-05-23/gate_c_input_discovery.json`
- `reports/gate_c_input_discovery_2026-05-23/gate_c_input_candidates.csv`
- `reports/gate_c_input_discovery_2026-05-23/gate_c_input_discovery.md`

## Interpretation

The current Gate C blocker is now independently confirmed as missing real frozen
benchmark inputs. The local reports contain audit and guardrail tables, but none
of the scanned files satisfy the citable Gate C contracts for `events`,
`labels`, or `splits`.

This is an important anti-hallucination control: we cannot promote Gate C by
renaming guardrail reports into benchmark artifacts.

## Next Required Work

The next scientific block must materialize the real frozen benchmark tables from
the source-data pipeline:

1. `events`: seizure event table with patient/recording ids and start/end times.
2. `labels`: labeled forecast windows with split, label, and exclusion columns.
3. `splits`: frozen split assignment artifact aligned to labels.

Once those exist, run:

```bash
python scripts/build_gate_c_freeze_package.py ...
```

Only that package can move Gate C from `blocked_missing_gate_c_inputs` to a
registry-backed citable freeze.
