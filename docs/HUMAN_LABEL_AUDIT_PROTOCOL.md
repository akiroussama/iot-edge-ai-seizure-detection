# Human Label Audit Protocol

This protocol is mandatory before A100 training or paper claims on real data.

## Goal

Confirm that event times, SPH/SOP labels, ictal exclusions, and postictal exclusions are correct around real seizure onsets.

## Export Audit Timelines

After generating `forecast_labels.parquet`, export seizure-centered windows:

```bash
uv run python scripts/audit_labels.py \
  --labels data/processed/seizeit2/forecast_labels.parquet \
  --events data/processed/seizeit2/events.parquet \
  --out reports/seizeit2_label_audit.csv \
  --minutes-before 60 \
  --minutes-after 60
```

Then create a one-row-per-event review sheet. This is the file the reviewer should fill:

```bash
uv run python scripts/make_label_audit_review_sheet.py \
  --audit reports/seizeit2_label_audit.csv \
  --out reports/seizeit2_label_audit_review_sheet.csv \
  --max-events 10
```

By default, `--max-events` uses round-robin patient selection (`--selection-strategy
patient_spread`) so the first manual audit is not accidentally limited to one patient.
Use `--selection-strategy first` only when checking a specific sorted event sequence.

Mock dry run:

```bash
uv run python scripts/prepare_seizeit2.py --mock --processed-dir /tmp/epitwin_mock_seizeit2
uv run python scripts/label_windows.py \
  --windows /tmp/epitwin_mock_seizeit2/windows.parquet \
  --events /tmp/epitwin_mock_seizeit2/events.parquet \
  --output /tmp/epitwin_mock_seizeit2/forecast_labels.parquet \
  --sph-minutes 5 \
  --sop-minutes 30 \
  --postictal-exclusion-minutes 60
uv run python scripts/audit_labels.py \
  --labels /tmp/epitwin_mock_seizeit2/forecast_labels.parquet \
  --events /tmp/epitwin_mock_seizeit2/events.parquet \
  --out /tmp/epitwin_mock_seizeit2/label_audit.csv
uv run python scripts/make_label_audit_review_sheet.py \
  --audit /tmp/epitwin_mock_seizeit2/label_audit.csv \
  --out /tmp/epitwin_mock_seizeit2/label_audit_review_sheet.csv
```

## Manual Checks

For at least 5-10 real seizures:

- Verify `seizure_start` and `seizure_end` against the original annotation.
- Verify positive labels satisfy `[window_end + SPH, window_end + SPH + SOP)`.
- Verify seizures exactly at the SPH lower boundary are positive.
- Verify seizures exactly at the SOP upper boundary are negative.
- Verify ictal windows are excluded.
- Verify postictal windows are excluded for the configured duration.
- Verify postictal windows are not used as preictal positives.
- Verify patient and recording IDs match the original source file.
- Verify timestamp timezone assumptions.

Fill these review-sheet columns for every audited event:

- `source_onset_verified`: `PASS`, `FAIL`, or `NEEDS_SOURCE_REVIEW`.
- `source_recording_verified`: `PASS`, `FAIL`, or `NEEDS_SOURCE_REVIEW`.
- `sph_sop_labels_pass`: `PASS`, `FAIL`, or `NEEDS_SOURCE_REVIEW`.
- `ictal_exclusion_pass`: `PASS`, `FAIL`, or `NEEDS_SOURCE_REVIEW`.
- `postictal_exclusion_pass`: `PASS`, `FAIL`, or `NEEDS_SOURCE_REVIEW`.
- `right_censoring_pass`: `PASS`, `FAIL`, or `NEEDS_SOURCE_REVIEW`.
- `decision`: `PASS`, `FAIL`, or `NEEDS_SOURCE_REVIEW`.
- `notes`: exact source-file references and any timestamp or exclusion discrepancy.

The precomputed columns `unexpected_ictal_not_excluded_rows` and
`unexpected_postictal_not_excluded_rows` must be zero before the event can pass.

## Failure Conditions

Stop the experiment if any of these appear:

- event timestamps are shifted relative to source annotations;
- a seizure appears in the wrong recording;
- ictal or postictal windows are used as valid training/evaluation windows;
- positive windows are outside the SPH/SOP interval;
- parser silently drops a patient or seizure.

Document every failed audit and fix the parser or annotation mapping before training.
