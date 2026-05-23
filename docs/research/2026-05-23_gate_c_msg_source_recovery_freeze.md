# MSG Gate C Source Recovery And Freeze

Date: 2026-05-23

## Scope

This run recovers the real My Seizure Gauge source tables required by Gate C:
`recordings` and `events`. It then materializes frozen Gate C
`events/labels/splits` artifacts for the MSG SPH60/SOP1440 track.

This is a structural data/split freeze. It does not create model performance
numbers and it does not compare against SOTA.

## Source Recovery

Source dataset: My Seizure Gauge Long-term Wearable Data, Zenodo record
`17380899`, DOI `10.5281/zenodo.17380899`.

Raw files recovered under local ignored storage `data/raw/msg`:

- `Mayo_1904.zip`
- `Mayo_1869.zip`
- `Mayo_1965.zip`
- `SeizureTimesOnly.zip`
- `Mayo_1110.zip`
- `Mayo_1927.zip`
- `Mayo_1876.zip`
- `Mayo_2002.zip`
- `Mayo_1988.zip`

The recovery command reported all nine files as present with expected byte
counts. Raw ZIPs remain outside Git.

## Generated Source Tables

Canonical source tables were generated under ignored local storage
`data/processed/msg`, then small CSV copies were committed under
`reports/gate_c_source_recovery_2026-05-23/artifacts`.

Source table counts:

- `recordings`: 2,068 rows, 8 recording patients.
- `events`: 768 rows, 11 event patients.
- `recording_match_status=matched`: 510 events.
- `recording_match_status=unmatched`: 258 events.
- Recording time span: 2020-01-01 00:30:00 to 2021-04-19 00:12:04.

Unmatched source events are intentionally retained in the frozen `events`
artifact. They must not be silently interpreted as prediction-coverable events
in downstream metrics.

## Gate C Materialization

Materialization configuration:

- Window duration: 1 hour.
- Stride: 1 hour.
- SPH: 60 minutes.
- SOP: 1,440 minutes.
- Postictal exclusion: 240 minutes.
- Postictal anchor: `seizure_start`.
- Ictal windows excluded.
- Split strategy: `temporal_recording_elapsed_time`.

Materialized frozen artifacts:

- `reports/gate_c_msg_freeze_2026-05-23/artifacts/events.csv`
- `reports/gate_c_msg_freeze_2026-05-23/artifacts/labels.csv`
- `reports/gate_c_msg_freeze_2026-05-23/artifacts/splits.csv`

Materialization counts:

- Events rows: 768.
- Labels rows: 49,577.
- Splits rows: 49,577.
- Valid non-excluded label rows: 7,920.
- Positive valid forecast windows: 3,326.
- Split counts: train 33,853; val 5,415; test 10,309.

Leakage audit summary:

- Patient overlap across splits: true, allowed for the temporal within-patient
  design used here.
- Recording overlap across splits: false.
- Duplicate window intervals: false.
- Duplicate recording time ranges: false.
- Postictal positive labels not excluded: false.
- Temporal ordering/overlap leakage: false.
- Feature normalization leakage: not applicable because no model features or
  predictions are part of this freeze.

## Gate C Freeze Status

Freeze package:

- Registry: `reports/gate_c_msg_freeze_2026-05-23/gate_c_registry.json`
- Manifest: `reports/gate_c_msg_freeze_2026-05-23/gate_c_freeze_manifest.json`
- Dry-run diagnostics: `reports/gate_c_msg_freeze_2026-05-23/gate_c_dry_run.json`
- Artifact summary: `reports/gate_c_msg_freeze_2026-05-23/gate_c_artifact_summary.csv`

Gate C diagnostics:

- Readiness status: `ready_for_gate_c_review`.
- Structural verification: true.
- Citable readiness flag: true.
- Blockers: none.

Important caveat: the DOI recorded in this freeze package is the MSG source
dataset DOI, not a newly minted benchmark preregistration DOI. The package is
therefore a local registry-backed freeze of artifacts derived from a public
source dataset. Paper text must not imply that a new public benchmark DOI was
minted unless that later happens.

## Exact Commands

```bash
git fetch --prune origin
uv run python scripts/download_msg_zenodo.py --out-dir data/raw/msg --verify-existing
uv run python scripts/prepare_msg.py --raw-dir data/raw/msg --processed-dir data/processed/msg --inspect-only
uv run python scripts/prepare_msg.py --raw-dir data/raw/msg --processed-dir data/processed/msg --duplicate-recording-policy drop_exact
uv run python scripts/discover_gate_c_sources.py --root data/processed/msg --out-dir reports/gate_c_source_recovery_2026-05-23/source_discovery
uv run python scripts/materialize_gate_c_inputs.py --recordings data/processed/msg/recordings.parquet --events data/processed/msg/events.parquet --out-dir data/processed/msg/gate_c_inputs_sph60_sop1440 --window-duration 1h --stride 1h --sph-minutes 60 --sop-minutes 1440 --postictal-exclusion-minutes 240 --postictal-anchor seizure_start --strategy temporal --temporal-unit recording --temporal-basis elapsed_time
uv run python scripts/discover_gate_c_inputs.py --root data/processed/msg/gate_c_inputs_sph60_sop1440 --out-dir reports/gate_c_source_recovery_2026-05-23/input_discovery
uv run python scripts/build_gate_c_freeze_package.py --events reports/gate_c_msg_freeze_2026-05-23/artifacts/events.csv --labels reports/gate_c_msg_freeze_2026-05-23/artifacts/labels.csv --splits reports/gate_c_msg_freeze_2026-05-23/artifacts/splits.csv --out-dir reports/gate_c_msg_freeze_2026-05-23 --registry-id msg_gate_c_sph60_sop1440_2026-05-23 --dataset msg --dataset-version zenodo_17380899_local_2026-05-23 --source-uri reports/gate_c_msg_freeze_2026-05-23/artifacts/gate_c_input_materialization_manifest.json --split-policy temporal_recording_elapsed_time --split-ref reports/gate_c_msg_freeze_2026-05-23/artifacts/gate_c_input_materialization_manifest.json --split-id train --split-id val --split-id test --horizon-name SPH60_SOP1440 --sph-minutes 60 --sop-minutes 1440 --doi-or-prereg-uri doi:10.5281/zenodo.17380899
```

## Scientific Guardrails

- Do not cite these artifacts as a model result.
- Do not collapse source events, matched events, and prediction-coverable events
  into one denominator.
- Report unmatched MSG events explicitly when discussing coverage.
- Treat SPH60/SOP1440 as the frozen track represented by this package; other
  horizons require separate freeze artifacts.
