# Gate B Final Human Closeout

Date: 2026-05-23

## Objective

Close Gate B using the reviewer-approved real decisions for `GB-004` through
`GB-008`, without promoting any simulated evidence. This block converts the
previous blank real-decision template into a hash-backed decision sheet, applies
it to the closeout ledger, and reruns Gate B validation.

## Human Decision Source

Reviewer: O. Akir

Decision date: 2026-05-23

Decision rows:

- `GB-004`: `RESOLVED`
- `GB-005`: `RESOLVED`
- `GB-006`: `APPROVED_EXCLUSION`
- `GB-007`: `DEFERRED`
- `GB-008`: `RESOLVED`

## Evidence Files

- `reports/gate_b_evidence_2026-05-23/GB-004_denominator_policy.md`
- `reports/gate_b_evidence_2026-05-23/GB-005_horizon_policy.md`
- `reports/gate_b_evidence_2026-05-23/GB-006_seizeit2_scope_policy.md`
- `reports/gate_b_evidence_2026-05-23/GB-007_sph5_sop360_source_review_policy.md`
- `reports/gate_b_evidence_2026-05-23/GB-008_negative_readiness_policy.md`

The decision CSV records SHA-256 hashes for each evidence file:

`reports/gate_b_final_human_closeout_2026-05-23/gate_b_real_decisions_2026-05-23.csv`

## Commands

```bash
sha256sum reports/gate_b_evidence_2026-05-23/GB-004_denominator_policy.md \
  reports/gate_b_evidence_2026-05-23/GB-005_horizon_policy.md \
  reports/gate_b_evidence_2026-05-23/GB-006_seizeit2_scope_policy.md \
  reports/gate_b_evidence_2026-05-23/GB-007_sph5_sop360_source_review_policy.md \
  reports/gate_b_evidence_2026-05-23/GB-008_negative_readiness_policy.md

uv run python scripts/run_gate_b_real_decision_intake.py \
  --closeout-ledger reports/gate_b_closeout_2026-05-22/gate_b_closeout_ledger.csv \
  --required-decisions reports/gate_b_real_closeout_2026-05-22/gate_b_real_closeout_required_decisions_template.csv \
  --decisions reports/gate_b_final_human_closeout_2026-05-23/gate_b_real_decisions_2026-05-23.csv \
  --out-dir reports/gate_b_final_human_closeout_2026-05-23/intake \
  --run-id gate_b_final_human_decision_intake_2026-05-23 \
  --source-uri reports/gate_b_final_human_closeout_2026-05-23/gate_b_real_decisions_2026-05-23.csv \
  --fail-on-blocked

uv run python scripts/apply_gate_b_closeout_decisions.py \
  --ledger reports/gate_b_closeout_2026-05-22/gate_b_closeout_ledger.csv \
  --decisions reports/gate_b_final_human_closeout_2026-05-23/gate_b_real_decisions_2026-05-23.csv \
  --out-dir reports/gate_b_final_human_closeout_2026-05-23/closeout \
  --run-id gate_b_final_human_closeout_2026-05-23 \
  --source-uri reports/gate_b_final_human_closeout_2026-05-23/gate_b_real_decisions_2026-05-23.csv \
  --decision-evidence-status human_attested_not_independently_verified

uv run python scripts/build_gate_b_real_closeout_package.py \
  --ledger reports/gate_b_final_human_closeout_2026-05-23/closeout/gate_b_closeout_ledger.csv \
  --out-dir reports/gate_b_final_human_closeout_2026-05-23/real_closeout \
  --run-id gate_b_final_real_closeout_package_2026-05-23 \
  --source-uri reports/gate_b_final_human_closeout_2026-05-23/closeout/gate_b_closeout_ledger.csv

uv run python scripts/run_local_gate_guardrails.py \
  --out-dir reports/gate_b_final_human_closeout_2026-05-23/validation_guardrails \
  --gate-b-status passed \
  --gate-c-status not_started

uv run python scripts/run_gate_b_validation_rerun.py \
  --closeout-ledger reports/gate_b_final_human_closeout_2026-05-23/closeout/gate_b_closeout_ledger.csv \
  --closeout-summary reports/gate_b_final_human_closeout_2026-05-23/real_closeout/gate_b_real_closeout_summary.csv \
  --guardrails-dir reports/gate_b_final_human_closeout_2026-05-23/validation_guardrails \
  --out-dir reports/gate_b_final_human_closeout_2026-05-23/validation \
  --run-id gate_b_final_validation_rerun_2026-05-23 \
  --source-uri reports/gate_b_final_human_closeout_2026-05-23/validation_guardrails \
  --fail-on-blocked
```

## Results

### Intake

```json
{
  "intake_status": "ready_for_closeout_application",
  "gate_b_next_status": "ready_to_apply_closeout_and_run_validation",
  "required_rows": 5,
  "accepted_rows": 5,
  "issue_rows": 0,
  "claim_status": "gate_b_real_decision_intake_not_citable_pre_gate_c"
}
```

### Closeout

```json
{
  "gate_b_status": "ready_for_gate_b_validation_rerun",
  "ledger_rows": 8,
  "closed_rows": 8,
  "open_rows": 0,
  "p0_open_rows": 0,
  "claim_status": "gate_b_closeout_ledger_pending_human_review_not_citable"
}
```

### Gate B Validation

```json
{
  "gate_b_validation_status": "passed_ready_for_gate_c_dry_run",
  "gate_b_passed": true,
  "gate_b_open_actions": 0,
  "gate_b_p0_open_actions": 0,
  "claim_status": "gate_b_validation_rerun_not_citable_pre_gate_c"
}
```

## Interpretation

Gate B is now passed for the current local guardrail rerun. This does not make
benchmark rows citable. It only unlocks the next hard blocker: Gate C dry-run
and freeze.

Remaining known constraints:

- MSG still records source/coverage limitations in the guardrail artifacts.
- SeizeIT2 full-cohort claims remain excluded from main benchmark claims.
- SPH5/SOP360 remains non-citable pending source review.
- Gate C is still `not_started`.

## Next Step

Run Gate C dry-run using `gate_b_status=passed`, then freeze only the eligible
splits, horizons, denominators, and exclusions.
