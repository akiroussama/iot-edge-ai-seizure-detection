# Human Label Audit Protocol

This protocol is mandatory before A100 training or paper claims on real data.

## Goal

Confirm that event times, SPH/SOP labels, ictal exclusions, and postictal exclusions are correct around real seizure onsets.

## Generate the review sheet (per dataset)

The review sheet is one row per seizure and is the file the reviewer fills.
Generate it per dataset from the processed `windows` and `events` tables —
`docs/COMMANDS.md` covers `prepare_seizeit2.py` / `prepare_msg.py` and
`make_windows.py`. Regenerate labels with current code first: a label file
produced before the Phase R P0 fix is stale.

Real windows carry `recording_end`, so `label_windows.py` right-censors
unobserved horizons by default — do not pass `--allow-missing-recording-end`
for real data.

### SeizeIT2

```bash
uv run python scripts/label_windows.py \
  --windows data/processed/seizeit2/windows.parquet \
  --events data/processed/seizeit2/events.parquet \
  --output data/processed/seizeit2/forecast_labels.parquet \
  --sph-minutes 5 \
  --sop-minutes 30 \
  --postictal-exclusion-minutes 60

uv run python scripts/audit_labels.py \
  --labels data/processed/seizeit2/forecast_labels.parquet \
  --events data/processed/seizeit2/events.parquet \
  --out reports/seizeit2_label_audit.csv \
  --minutes-before 60 \
  --minutes-after 60

uv run python scripts/make_label_audit_review_sheet.py \
  --audit reports/seizeit2_label_audit.csv \
  --out reports/seizeit2_label_audit_review_sheet.csv \
  --max-events 10
```

### My Seizure Gauge (MSG)

MSG annotations are onset-only, so `seizure_end` is imputed. Anchor postictal
exclusion to the onset with `--postictal-anchor seizure_start`;
`label_windows.py` fails closed on imputed `seizure_end` otherwise. The MSG
long-horizon is SPH 60 / SOP 1440 on hourly windows.

```bash
uv run python scripts/label_windows.py \
  --windows data/processed/msg/windows_1h.parquet \
  --events data/processed/msg/events.parquet \
  --output data/processed/msg/labels_sph60_sop1440.parquet \
  --sph-minutes 60 \
  --sop-minutes 1440 \
  --postictal-exclusion-minutes 240 \
  --postictal-anchor seizure_start

# --minutes-before spans the full SPH+SOP horizon (60 + 1440) so the timeline
# shows every positive window around each onset.
uv run python scripts/audit_labels.py \
  --labels data/processed/msg/labels_sph60_sop1440.parquet \
  --events data/processed/msg/events.parquet \
  --out reports/msg_label_audit.csv \
  --minutes-before 1500 \
  --minutes-after 60

uv run python scripts/make_label_audit_review_sheet.py \
  --audit reports/msg_label_audit.csv \
  --out reports/msg_label_audit_review_sheet.csv \
  --max-events 10
```

`--max-events` defaults to round-robin patient selection (`--selection-strategy
patient_spread`) so the first audit is not limited to one patient. Use
`--selection-strategy first` only to check a specific sorted event sequence.

### Mock dry run

A synthetic end-to-end check of the pipeline only — it cannot validate real
seizure timelines.

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

After filling each dataset's sheet, run the blocking gate once per dataset
(SeizeIT2 shown; repeat with the `msg_` paths for My Seizure Gauge):

```bash
uv run python scripts/check_label_audit_review.py \
  --review-sheet reports/seizeit2_label_audit_review_sheet.csv \
  --out reports/seizeit2_label_audit_review_check.csv \
  --min-events 5
```

The command must exit successfully before A100 training or paper-result reporting.
An incomplete sheet is expected to fail; that is the intended behavior.

## Failure Conditions

Stop the experiment if any of these appear:

- event timestamps are shifted relative to source annotations;
- a seizure appears in the wrong recording;
- ictal or postictal windows are used as valid training/evaluation windows;
- positive windows are outside the SPH/SOP interval;
- parser silently drops a patient or seizure.

Document every failed audit and fix the parser or annotation mapping before training.
