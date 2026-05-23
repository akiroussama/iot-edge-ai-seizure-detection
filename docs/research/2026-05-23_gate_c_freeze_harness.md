# Gate C Freeze Package Harness

Date: 2026-05-23

## Objective

Convert the Gate C dry-run blockers into an executable freeze pathway without
fabricating benchmark artifacts.

The previous Gate C dry-run proved that Gate B is passed, but the repository
does not yet contain frozen citable `events`, `labels`, and `splits` artifacts.
This harness defines the exact executable contract for turning those real
inputs into a citable Gate C package once they exist.

## Added Harness

The new CLI is:

```bash
python scripts/build_gate_c_freeze_package.py \
  --events <frozen-events.csv|parquet|tsv> \
  --labels <frozen-labels.csv|parquet|tsv> \
  --splits <frozen-splits.csv|parquet|tsv> \
  --out-dir reports/gate_c_freeze_<date> \
  --registry-id <registry-id> \
  --dataset <dataset> \
  --dataset-version <version> \
  --source-uri <source-uri> \
  --generation-command "<exact command>" \
  --split-policy <policy> \
  --split-ref <split-manifest-ref> \
  --split-id train \
  --split-id val \
  --split-id test \
  --horizon-name <horizon> \
  --sph-minutes <minutes> \
  --sop-minutes <minutes> \
  --doi-or-prereg-uri <doi-or-prereg-uri>
```

## Validation Contract

The package fails before writing a citable freeze if any required condition is
missing.

Required `events` contract:

- `patient_id`
- `recording_id`
- `seizure_start`
- `seizure_end`
- non-empty table
- valid timestamp order

Required `labels` contract:

- `patient_id`
- `recording_id`
- `window_start`
- `window_end`
- `split`
- `forecast_label`
- `is_excluded`
- non-empty table
- no duplicate patient/recording/window rows
- at least one non-excluded window
- at least one positive non-excluded forecast window
- split ids exactly match the declared frozen split ids

Required `splits` contract:

- `split`
- at least one alignment key shared with labels:
  - `patient_id`, or
  - `patient_id + recording_id`, or
  - `patient_id + recording_id + window_start + window_end`
- no duplicate alignment keys
- split ids exactly match the declared frozen split ids
- split assignments agree with the labels table

Required registry contract:

- `gate_c_status='passed'`
- `freeze_status='frozen'`
- DOI or preregistration URI present
- required roles present: `events`, `labels`, `splits`
- Gate C dry-run returns `citable_ready=true`

## Outputs

When the contract is satisfied, the harness writes:

- `gate_c_registry.json`
- `gate_c_dry_run.json`
- `gate_c_dry_run.md`
- `gate_c_artifact_summary.csv`
- `gate_c_freeze_manifest.json`

## Current Repository State

No real citable Gate C freeze was produced in this block because the real
frozen `events`, `labels`, and `splits` artifacts are still absent from the
repository. The contribution here is the executable guardrail that prevents a
premature freeze and turns the next real-data step into a deterministic command.

## Validation

Synthetic tests prove the happy path and failure paths:

- valid synthetic artifacts produce `citable_ready=true`
- missing label contract is rejected
- split mismatch is rejected
- CLI writes the expected citable package outputs

This keeps the paper posture strict: no citable benchmark claim until real
frozen artifacts satisfy the same contract.
