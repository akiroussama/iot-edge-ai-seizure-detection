# Local Gate Guardrail Execution

Date: 2026-05-22

Branch: `codex/run-gate-guards-local`

Base: `origin/main@82b3d0a`

## Objective

Execute the newly added MSG and SeizeIT2 guardrails on the real local artifacts
available in the repository, then convert the blockers into an actionable Gate
B/Gate C checklist.

This is an audit execution artifact. It is not a model result, not clinical
evidence, and not citable before Gate C.

## Local Inputs

The clean checkout does not contain raw CSV/parquet source artifacts. It does
contain committed Markdown reports generated from prior local real-data runs.
The runner therefore extracts structured tables from:

- `reports/msg_event_coverage_summary.md`;
- `reports/msg_horizon_viability.md`;
- `reports/seizeit2_sub125_real_check/dataset_report.md`.

The extracted tables are written back under:

- `reports/local_gate_guardrails_2026-05-22/inputs/`.

## Implementation

- Added `src/reports/gate_bc_checklist.py`.
- Added `scripts/run_local_gate_guardrails.py`.
- Added tests in `tests/test_gate_bc_checklist.py`.
- Generated committed guardrail outputs in
  `reports/local_gate_guardrails_2026-05-22/`.

The runner executes:

1. MSG data-gap triage from local coverage/cluster/horizon tables.
2. SeizeIT2 cohort-readiness guardrail from the local `sub-125` dataset report.
3. Combined Gate B/Gate C action checklist.

## Execution Command

```bash
uv run --extra dev python scripts/run_local_gate_guardrails.py \
  --out-dir reports/local_gate_guardrails_2026-05-22 \
  --gate-b-status not_started \
  --gate-c-status not_started
```

Output:

```json
{
  "out_dir": "reports/local_gate_guardrails_2026-05-22",
  "msg_p0_patients": 3,
  "msg_unmatched_events": 258,
  "seizeit2_blockers": 20,
  "checklist_actions": 8,
  "claim_status": "gate_bc_action_checklist_pre_gate_c_not_citable"
}
```

## Main Findings

MSG:

- 11 patients represented in the local MSG coverage report.
- 768 annotated seizure events.
- 510 matched events.
- 258 unmatched events.
- 3 P0 source-data blockers: patients `1942`, `1219`, and `1675`.
- 7 P1 matched-only/source-review patients.
- 5 candidate SPH/SOP horizons are not main-table-ready.
- `SPH5/SOP360` still requires source review before citable use.

SeizeIT2:

- Local available report is `sub-125` only.
- The local report has 1 patient, 85 recordings, 4664 windows, and 2 events.
- Cohort readiness is blocked.
- 20 SeizeIT2 blockers are emitted, including missing Gate B/Gate C pass,
  below-threshold patient/event counts, missing expected published counts,
  missing official split manifest, missing required tasks, missing required
  modality tracks, and missing ready train/val/test track rows.

Checklist:

- 8 total actions.
- 3 P0 actions.
- 3 P1 actions.
- 2 P2 actions.
- 7 Gate B actions.
- 1 Gate C action.

The canonical checklist is:

- `reports/local_gate_guardrails_2026-05-22/gate_bc_action_checklist.md`;
- `reports/local_gate_guardrails_2026-05-22/gate_bc_action_checklist.csv`;
- `reports/local_gate_guardrails_2026-05-22/gate_bc_action_checklist.json`.

## Guardrails

- Claim status remains `gate_bc_action_checklist_pre_gate_c_not_citable`.
- The runner does not train, score, or calibrate a model.
- The runner does not freeze splits or produce a Gate C pass.
- Markdown table extraction is used only because the clean checkout contains
  committed Markdown reports, not raw CSV/parquet inputs.
- SeizeIT2 local `sub-125` is explicitly treated as a local smoke/cohort
  readiness blocker, not a cohort result.

## Validation

Targeted validation:

```bash
uv run --extra dev ruff check src/reports/gate_bc_checklist.py scripts/run_local_gate_guardrails.py tests/test_gate_bc_checklist.py
uv run --extra dev pytest tests/test_gate_bc_checklist.py tests/test_msg_gap_triage.py tests/test_seizeit2_cohort_readiness.py
```

Full validation:

```bash
uv run --extra dev ruff check .
uv run --extra dev --extra torch pytest
git diff --check
```

Result:

- Targeted Ruff: passed.
- Targeted pytest: 9 passed.
- Full Ruff: passed.
- Full pytest: 302 passed.
- `git diff --check`: passed.

## Remaining Work

Gate B should now close the P0/P1 actions in the checklist. Gate C should not
start until the checklist is rerun cleanly and the Gate C dry-run reports
`ready_for_gate_c_review`.
