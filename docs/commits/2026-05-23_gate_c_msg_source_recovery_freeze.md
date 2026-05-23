# Gate C MSG Source Recovery Freeze

Date: 2026-05-23

## What Changed

- Downloaded and verified the full MSG Zenodo source set locally under
  ignored storage `data/raw/msg`.
- Generated real canonical MSG `recordings` and `events` source tables.
- Materialized MSG Gate C `events/labels/splits` artifacts for SPH60/SOP1440.
- Built a registry-backed Gate C freeze package with committed artifact copies
  under `reports/gate_c_msg_freeze_2026-05-23`.
- Added source recovery artifacts under
  `reports/gate_c_source_recovery_2026-05-23/artifacts`.

## Key Counts

- Source recordings: 2,068 rows.
- Source events: 768 rows.
- Matched source events: 510.
- Unmatched source events: 258.
- Frozen labels: 49,577 rows.
- Valid non-excluded labels: 7,920 rows.
- Positive valid forecast windows: 3,326.
- Split counts: train 33,853; val 5,415; test 10,309.

## Validation

Commands executed:

```bash
git fetch --prune origin
uv run python scripts/download_msg_zenodo.py --out-dir data/raw/msg --verify-existing
uv run python scripts/prepare_msg.py --raw-dir data/raw/msg --processed-dir data/processed/msg --inspect-only
uv run python scripts/prepare_msg.py --raw-dir data/raw/msg --processed-dir data/processed/msg --duplicate-recording-policy drop_exact
uv run python scripts/discover_gate_c_sources.py --root data/processed/msg --out-dir reports/gate_c_source_recovery_2026-05-23/source_discovery
uv run python scripts/materialize_gate_c_inputs.py --recordings data/processed/msg/recordings.parquet --events data/processed/msg/events.parquet --out-dir data/processed/msg/gate_c_inputs_sph60_sop1440 --window-duration 1h --stride 1h --sph-minutes 60 --sop-minutes 1440 --postictal-exclusion-minutes 240 --postictal-anchor seizure_start --strategy temporal --temporal-unit recording --temporal-basis elapsed_time
uv run python scripts/discover_gate_c_inputs.py --root data/processed/msg/gate_c_inputs_sph60_sop1440 --out-dir reports/gate_c_source_recovery_2026-05-23/input_discovery
python -m json.tool reports/gate_c_msg_freeze_2026-05-23/gate_c_registry.json
python -m json.tool reports/gate_c_msg_freeze_2026-05-23/gate_c_freeze_manifest.json
```

Gate C freeze package status:

- `readiness_status`: `ready_for_gate_c_review`.
- `citable_ready`: true.
- Blockers: none.
- Artifact count: 7.

## Caveat

The DOI used by the freeze package is the MSG source dataset DOI
`10.5281/zenodo.17380899`. No new benchmark DOI or preregistration DOI was
minted in this run.
