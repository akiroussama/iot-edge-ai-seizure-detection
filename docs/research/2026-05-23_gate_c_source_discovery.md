# Gate C Source Discovery

Date: 2026-05-23

## Objective

After adding the Gate C materialization harness, scan local artifacts for the
source tables required to run it: `recordings` and `events`.

This is the upstream counterpart to Gate C input discovery. Input discovery asks
whether frozen `events`, `labels`, and `splits` already exist. Source discovery
asks whether enough raw structured source tables exist to materialize them.

## Added Tool

```bash
python scripts/discover_gate_c_sources.py \
  --root data \
  --root reports \
  --out-dir reports/gate_c_source_discovery_2026-05-23
```

The scanner classifies local `.csv`, `.tsv`, and `.parquet` files against:

- `recordings`: `patient_id`, `recording_id`, `recording_start`,
  `recording_end`
- `events`: `patient_id`, `recording_id`, `seizure_start`, `seizure_end`

## Local Scan Result

```text
scan_status: blocked_missing_gate_c_sources
files_scanned: 70
readable_tables: 70
recordings_ready: 0
events_ready: 0
missing_roles: recordings, events
```

Outputs:

- `reports/gate_c_source_discovery_2026-05-23/gate_c_source_discovery.json`
- `reports/gate_c_source_discovery_2026-05-23/gate_c_source_candidates.csv`
- `reports/gate_c_source_discovery_2026-05-23/gate_c_source_discovery.md`

## Interpretation

The repository currently has neither:

1. source `recordings` sufficient to generate windows, nor
2. source `events` sufficient to label windows.

Therefore the Gate C freeze cannot proceed from local artifacts alone. The next
scientific work is source recovery/materialization from the real dataset
pipeline, not benchmark scoring.

## Next Required Inputs

Recover or generate real source tables with:

1. `recordings.csv`: one row per recording with patient/recording ids and
   recording start/end times.
2. `events.csv`: one row per seizure event with patient/recording ids and
   seizure start/end times.

Then run:

```bash
python scripts/materialize_gate_c_inputs.py \
  --recordings <recordings> \
  --events <events> \
  --out-dir reports/gate_c_inputs_<date>
```

Only after that should `build_gate_c_freeze_package.py` be used.
