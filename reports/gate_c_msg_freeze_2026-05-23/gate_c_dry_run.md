# Gate C Dry-Run Diagnostics

**Status:** `ready_for_gate_c_review`

This is a dry-run diagnostic. It is not a Gate C pass and it does not make any
benchmark number citable.

## Registry

- Registry id: `msg_gate_c_sph60_sop1440_2026-05-23`
- Dataset: `msg`
- Gate B status: `passed`
- Gate C status: `passed`
- Freeze status: `frozen`
- DOI / preregistration URI: `doi:10.5281/zenodo.17380899`
- Structural verification: `True`
- Citable readiness: `True`

## Blockers

- none

## Warnings

- none

## Artifact Summary

| name | role | path | row_count | event_count | positive_windows |
| --- | --- | --- | --- | --- | --- |
| events | events | reports/gate_c_msg_freeze_2026-05-23/artifacts/events.csv | 768.0 | 768.0 |  |
| labels | labels | reports/gate_c_msg_freeze_2026-05-23/artifacts/labels.csv | 49577.0 |  | 3326.0 |
| splits | splits | reports/gate_c_msg_freeze_2026-05-23/artifacts/splits.csv | 49577.0 |  |  |
| source_discovery | metadata | reports/gate_c_source_recovery_2026-05-23/source_discovery/gate_c_source_discovery.json |  |  |  |
| input_discovery | metadata | reports/gate_c_source_recovery_2026-05-23/input_discovery/gate_c_input_discovery.json |  |  |  |
| materialization_manifest | metadata | reports/gate_c_msg_freeze_2026-05-23/artifacts/gate_c_input_materialization_manifest.json |  |  |  |
| leakage_audit | metadata | reports/gate_c_msg_freeze_2026-05-23/artifacts/leakage_audit.txt |  |  |  |

## Next Actions

1. Keep the committed Gate B validation report as the upstream prerequisite.
2. Proceed to Gate C review using only the frozen registry-backed artifacts.
