# Gate C Dry-Run Diagnostics

**Status:** `blocked`

This is a dry-run diagnostic. It is not a Gate C pass and it does not make any
benchmark number citable.

## Registry

- Registry id: `gate_c_prefreeze_2026-05-23`
- Dataset: `epitwin_open`
- Gate B status: `passed`
- Gate C status: `partial`
- Freeze status: `pending_human_audit`
- DOI / preregistration URI: `missing`
- Structural verification: `True`
- Citable readiness: `False`

## Blockers

- registry.gate_c_status is not 'passed'
- registry.freeze_status is not 'frozen'
- doi_or_prereg_uri is required for Gate C
- missing required artifact roles: ['events', 'labels', 'splits']

## Warnings

- none

## Artifact Summary

| name | role | path | row_count | event_count | positive_windows |
| --- | --- | --- | --- | --- | --- |
| gate_b_validation_summary | metadata | reports/gate_b_final_human_closeout_2026-05-23/validation/gate_b_validation_summary.csv | 1 |  |  |

## Next Actions

1. Keep the committed Gate B validation report as the upstream prerequisite.
2. Materialize and register the required Gate C artifact roles: events, labels, splits.
3. Pre-register or DOI the frozen protocol before producing citable rows.
4. Set gate_c_status='passed' and freeze_status='frozen' only after the required artifacts and DOI/preregistration pass verification.
