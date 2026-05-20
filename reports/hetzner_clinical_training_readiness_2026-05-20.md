# Hetzner clinical-training readiness check

Date: 2026-05-20
Host: `ubuntu-32gb-fsn1-1`
Code commit checked: `831fee6`
Working tree used: `/root/epitwin-hetzner-stage-20260520`

## Summary

The Hetzner CPU training path is operational, but the run cannot honestly be
promoted to a clinical result yet. The blocking issue is not compute. The
blocking issue is Gate B: the human label-audit review sheets are present but
unfilled.

This check deliberately fails closed. A real clinical result requires:

1. Human-reviewed label audit sheets with all required decision columns filled.
2. Passing `scripts/check_label_audit_review.py` outputs for MSG and SeizeIT2.
3. Frozen splits and leakage audit after any label/parser corrections.
4. A real data-driven trainer. The current `scripts/train_epitwin_ssl.py`
   trains EpiTwin-SSL on synthetic tensors only; it is an infrastructure smoke
   trainer, not a real-data trainer.

## Evidence collected on Hetzner

Review sheets found in `/root/iot-edge-ai-seizure-detection/reports`:

- `msg_label_audit_review_sheet.csv`: 10 rows.
- `seizeit2_label_audit_review_sheet.csv`: 10 rows.
- Full sheets also exist:
  - `msg_label_audit_review_sheet_full.csv`: 510 rows.
  - `seizeit2_label_audit_review_sheet_full.csv`: 883 rows.

Validation commands run:

```bash
cd /root/epitwin-hetzner-stage-20260520

uv run python scripts/check_label_audit_review.py \
  --review-sheet /root/iot-edge-ai-seizure-detection/reports/msg_label_audit_review_sheet.csv \
  --out outputs/clinical_readiness_msg_review_check_20260520.csv \
  --min-events 5

uv run python scripts/check_label_audit_review.py \
  --review-sheet /root/iot-edge-ai-seizure-detection/reports/seizeit2_label_audit_review_sheet.csv \
  --out outputs/clinical_readiness_seizeit2_review_check_20260520.csv \
  --min-events 5
```

Both checks failed for the same reason: all human decision columns are blank.

Missing fields in each 10-row sheet:

| Field | MSG missing | SeizeIT2 missing |
|---|---:|---:|
| `source_onset_verified` | 10 | 10 |
| `source_recording_verified` | 10 | 10 |
| `sph_sop_labels_pass` | 10 | 10 |
| `ictal_exclusion_pass` | 10 | 10 |
| `postictal_exclusion_pass` | 10 | 10 |
| `right_censoring_pass` | 10 | 10 |
| `decision` | 10 | 10 |

Automatic anomaly checks did not find non-zero ictal/postictal exclusion
anomaly counts in those sampled sheets, but that is not a substitute for the
human source/timeline review.

## What must be filled by Oussama

Fill these columns in both sampled review sheets:

- `reviewer`
- `source_onset_verified`
- `source_recording_verified`
- `sph_sop_labels_pass`
- `ictal_exclusion_pass`
- `postictal_exclusion_pass`
- `right_censoring_pass`
- `decision`
- `notes` as needed

Allowed decision values are enforced by code:

- `PASS`
- `FAIL`
- `NEEDS_SOURCE_REVIEW`

For Gate B to pass, every blocking review field must be `PASS`.

## Re-check commands after manual fill

```bash
cd /root/epitwin-hetzner-stage-20260520

uv run python scripts/check_label_audit_review.py \
  --review-sheet /root/iot-edge-ai-seizure-detection/reports/msg_label_audit_review_sheet.csv \
  --out outputs/clinical_readiness_msg_review_check_20260520.csv \
  --min-events 5

uv run python scripts/check_label_audit_review.py \
  --review-sheet /root/iot-edge-ai-seizure-detection/reports/seizeit2_label_audit_review_sheet.csv \
  --out outputs/clinical_readiness_seizeit2_review_check_20260520.csv \
  --min-events 5
```

Only after these pass should the project proceed to split freeze, leakage
audit, and real-data model training.

## Current training status

Already completed on Hetzner:

- Stage A full check at `831fee6`: pytest, ruff, synthetic demo, synthetic
  EpiTwin-SSL smoke training, CPU throughput benchmark.
- CPU proxy training:
  `uv run --extra torch python scripts/train_epitwin_ssl.py --epochs 200 --batch-size 64 --time-steps 128 --hidden-dim 128 --backbone tcn`
  completed with exit 0.

Those runs are infrastructure evidence only. They are not clinical results
because they use synthetic tensors and bypass no human label-audit gate.

