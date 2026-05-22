# Gate B Audit Acceleration Package

Date: 2026-05-22
Branch: `codex/gate-b-audit-acceleration`
Base: `origin/main@b3e951a`

## Objective

Gate B is the main current bottleneck: the project cannot freeze the benchmark,
claim citable real-data numbers, or run A100/deep-model experiments until human
seizure-timeline audits are complete and committed. The existing active audit
selector ranks events, but it did not yet produce a complete human-facing audit
package.

This block adds a Gate B package builder that converts an audit timeline plus
optional model/reference predictions into:

- a selected human review sheet;
- the full scored candidate table;
- a JSON manifest;
- a Markdown instruction packet with validation command and guardrails.

## Implementation

Added:

- `src/reports/gate_b_audit_package.py`
- `scripts/build_gate_b_audit_package.py`
- `tests/test_gate_b_audit_package.py`

The package builder wraps the existing active audit selection logic and keeps
review decisions blank. It does not infer clinical correctness and it does not
turn active-selection output into a Gate B pass.

Default output filenames:

- `gate_b_audit_review_sheet.csv`
- `gate_b_audit_candidates.csv`
- `gate_b_audit_manifest.json`
- `gate_b_audit_package.md`

The generated Markdown instructs the reviewer to fill:

- `source_onset_verified`
- `source_recording_verified`
- `sph_sop_labels_pass`
- `ictal_exclusion_pass`
- `postictal_exclusion_pass`
- `right_censoring_pass`
- `decision`

Then run:

```bash
python scripts/check_label_audit_review.py --review-sheet gate_b_audit_review_sheet.csv --out gate_b_audit_validation.csv --min-events 5
```

## Guardrails

- `package_status` is `pending_human_review_not_gate_b_pass`.
- `result_status` is `audit_prioritization_not_citable`.
- `gate_b_status` is `not_passed_pending_human_review`.
- `gate_c_status` is `blocked_until_gate_b_and_freeze`.
- The package is explicitly not a benchmark result and not citable as model
  performance.
- Minimum event-budget coverage is recorded but does not replace the blocking
  review-sheet validation.

## Example

```bash
python scripts/build_gate_b_audit_package.py \
  --audit reports/msg_full_label_audit.csv \
  --dataset msg \
  --budget 10 \
  --selection-strategy patient_spread \
  --out-dir reports/gate_b_msg_audit_package_2026-05-22
```

With aligned predictions and null/reference rows:

```bash
python scripts/build_gate_b_audit_package.py \
  --audit reports/msg_full_label_audit.csv \
  --predictions reports/model_predictions.csv \
  --reference-predictions split_prior=reports/split_prior_predictions.csv \
  --dataset msg \
  --budget 10 \
  --selection-strategy patient_spread \
  --out-dir reports/gate_b_msg_audit_package_2026-05-22
```

## Validation

```bash
uv run --extra dev ruff check src/reports/gate_b_audit_package.py scripts/build_gate_b_audit_package.py tests/test_gate_b_audit_package.py src/reports/__init__.py
uv run --extra dev pytest tests/test_gate_b_audit_package.py tests/test_active_audit_selection.py tests/test_label_audit.py
uv run --extra dev ruff check .
uv run --extra dev --extra torch pytest
git diff --check
```

Results:

- Ruff: passed.
- Targeted pytest: 15 passed.
- Full pytest: 290 passed.
- Diff whitespace check: passed.

## Residual Risk

This package reduces audit friction; it does not close Gate B. Gate B still
requires a human to verify source annotations and timeline labels, commit the
completed review sheet/log, and rerun affected artifacts after any correction.
