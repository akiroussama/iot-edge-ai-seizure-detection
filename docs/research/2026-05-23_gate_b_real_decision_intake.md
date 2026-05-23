# Gate B Real Decision Intake

Date: 2026-05-23

## Objective

Add a strict intake/preflight step for real Gate B decisions. This is the bridge
between the blank real closeout template and the Gate B validation rerun harness.
The intake must reject incomplete rows, invalid SHA-256 hashes, missing rerun
artifacts, unknown decision rows, and simulation markers before any decisions are
applied to the real closeout ledger.

## Inputs

- Current real closeout ledger:
  `reports/gate_b_closeout_2026-05-22/gate_b_closeout_ledger.csv`
- Required real decisions template:
  `reports/gate_b_real_closeout_2026-05-22/gate_b_real_closeout_required_decisions_template.csv`
- Current decision sheet used for this preflight:
  `reports/gate_b_real_closeout_2026-05-22/gate_b_real_closeout_required_decisions_template.csv`

The decision sheet is intentionally still blank. The expected result is a
blocked intake, not a Gate B pass.

## Implementation

- Added `src/reports/gate_b_decision_intake.py`.
- Added `scripts/run_gate_b_real_decision_intake.py`.
- Added `tests/test_gate_b_decision_intake.py`.
- Generated `reports/gate_b_real_decision_intake_2026-05-23/`.

The intake validates:

- all required `ledger_id` rows are present;
- no unknown or duplicate decision rows are supplied;
- `human_decision` is in the allowed vocabulary;
- reviewer, date, evidence URI, evidence hash, resolution notes, and
  `rerun_required` are present;
- `evidence_hash` has format `sha256:<64 hex>`;
- `rerun_required=yes` has a non-empty `rerun_artifact_uri`;
- simulation markers are not present in the real-decision path.

`BLOCKED` and `NEEDS_SOURCE_REVIEW` are valid human decisions, but they keep Gate
B blocked after application.

## Command

```bash
uv run python scripts/run_gate_b_real_decision_intake.py \
  --closeout-ledger reports/gate_b_closeout_2026-05-22/gate_b_closeout_ledger.csv \
  --required-decisions reports/gate_b_real_closeout_2026-05-22/gate_b_real_closeout_required_decisions_template.csv \
  --decisions reports/gate_b_real_closeout_2026-05-22/gate_b_real_closeout_required_decisions_template.csv \
  --out-dir reports/gate_b_real_decision_intake_2026-05-23 \
  --run-id gate_b_real_decision_intake_2026-05-23 \
  --source-uri reports/gate_b_real_closeout_2026-05-22/gate_b_real_closeout_required_decisions_template.csv
```

## Result

```json
{
  "out_dir": "reports/gate_b_real_decision_intake_2026-05-23",
  "intake_status": "blocked_invalid_or_incomplete_decisions",
  "gate_b_next_status": "blocked_by_real_decision_intake",
  "required_rows": 5,
  "accepted_rows": 0,
  "issue_rows": 5,
  "claim_status": "gate_b_real_decision_intake_not_citable_pre_gate_c"
}
```

## Interpretation

Gate B remains blocked. The five required rows `GB-004` through `GB-008` are
present only as blank template rows. The next action is to fill those rows with
real human decisions and evidence, then rerun this intake. If the intake reports
`ready_for_closeout_application`, the decisions can be applied to the closeout
ledger and passed to the Gate B validation rerun harness.

## Validation

Targeted validation:

```bash
uv run ruff check src/reports/gate_b_decision_intake.py scripts/run_gate_b_real_decision_intake.py tests/test_gate_b_decision_intake.py
uv run pytest tests/test_gate_b_decision_intake.py -q
```

Result: 6 passed.
