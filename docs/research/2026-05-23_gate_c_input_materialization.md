# Gate C Input Materialization Harness

Date: 2026-05-23

## Objective

Close the gap between source clinical tables and the Gate C freeze package by
adding one deterministic command that materializes the required frozen inputs:
`events`, `labels`, and `splits`.

The previous input-discovery scan found no role-ready Gate C inputs in local
`data` or `reports`. This block does not fabricate those inputs. It creates the
pipeline step that will produce them from real source `recordings` and `events`
tables as soon as those source tables are available.

## Added CLI

```bash
python scripts/materialize_gate_c_inputs.py \
  --recordings <recordings.csv|parquet|tsv> \
  --events <events.csv|parquet|tsv> \
  --out-dir reports/gate_c_inputs_<date> \
  --window-duration 2min \
  --stride 30s \
  --sph-minutes 5 \
  --sop-minutes 30
```

The command writes:

- `events.csv`
- `labels.csv`
- `splits.csv`
- `leakage_audit.txt`
- `gate_c_input_materialization_manifest.json`

## Pipeline

1. Validate `recordings` with `patient_id`, `recording_id`,
   `recording_start`, and `recording_end`.
2. Validate `events` with `patient_id`, `recording_id`, `seizure_start`, and
   `seizure_end`.
3. Generate deterministic fixed windows.
4. Label windows with SPH/SOP forecasting labels.
5. Apply leakage-aware splits.
6. Emit the Gate C `events`, `labels`, and `splits` artifacts.
7. Validate those outputs against the Gate C freeze package contract.
8. Write a leakage audit and a manifest containing the next freeze-package
   command.

## Scientific Guardrail

The materialization output remains non-citable until it is passed into:

```bash
python scripts/build_gate_c_freeze_package.py ...
```

Only the freeze package can promote the artifacts to a registry-backed citable
Gate C state, and only when a DOI or preregistration URI is provided.

## Validation

Synthetic tests cover:

- materialization of freeze-ready `events`, `labels`, and `splits`
- direct chaining from materialized inputs into `build_gate_c_freeze_package`
- rejection when source events produce no positive valid forecast windows
- CLI output and manifest writing

This gives the project a reproducible path from real source tables to a citable
Gate C freeze without weakening the anti-hallucination guardrails.
