# MSG Patient-Wise Real-Data Baseline — exploratory pre-freeze (2026-05-20)

## Scope

**These are exploratory pre-freeze numbers from a real-data MSG run on
Hetzner CPU.** Per `PLAYBOOK.md` §10 rule 1, no benchmark number may be
cited before Gate C (frozen splits + Zenodo pre-registration). These
figures are recorded for development and planning only; they are **not a
citable benchmark result**.

- Code commit: `7568122`
- Host: Hetzner `ubuntu-32gb-fsn1-1`
- Worktree: `/root/epitwin-hetzner-stage-20260520`
- Dataset: MSG only
- Split: patient-wise, `split=test`
- Horizon: SPH 60 minutes / SOP 1440 minutes
- Evaluation denominator: test events coverable by selected prediction horizons
- Gate B status: sampled human attestation by Oussama on 2026-05-20 (form
  met; the audit log has no per-seizure observation notes —
  strengthening recommended before any pre-registration)
- Gate C status: **NOT passed.** Only one of its four conditions is met
  (leakage audit clean); the others — split policy documented, frozen
  splits with `git tag`, Zenodo DOI pre-registration — are pending

SeizeIT2 is intentionally out of scope for this result because its current
patient-wise audit still shows duplicate recording time ranges that need a
separate resolution or documented justification before a strict clean result is
claimed.

## Data And Training

MSG HR features were extracted from the raw Empatica ZIP archives:

```bash
uv run python scripts/extract_msg_features.py \
  --raw-dir /root/iot-edge-ai-seizure-detection/data/raw/msg \
  --windows /root/iot-edge-ai-seizure-detection/data/processed/msg/split_patient.parquet \
  --out outputs/msg_clinical_baselines_20260520/msg_patient_features_hr.parquet \
  --modalities hr
```

Extraction summary:

- rows: 49,577
- processed recordings: 2,055
- populated HR feature rows: 49,543

The trained model was a CPU tabular MLP using only physiological HR summary
features:

- `hr_mean`
- `hr_std`
- `hr_min`
- `hr_max`
- `hr_median`
- `hr_mad`
- `hr_slope`
- `hr_energy`

The training script excludes label, timing-to-seizure, right-censoring, split,
dataset, and identifier metadata from automatic feature selection. Preprocessing
statistics are fit on `train` only; the alarm threshold is selected on `val`.

Training command:

```bash
uv run --extra torch python scripts/train_msg_tabular_baseline.py \
  --features outputs/msg_clinical_baselines_20260520/msg_patient_features_hr.parquet \
  --out outputs/msg_clinical_baselines_20260520/msg_tabular_hr_patient_predictions_clean.parquet \
  --model-out outputs/msg_clinical_baselines_20260520/msg_tabular_hr_patient_model_clean.pt \
  --metrics-out outputs/msg_clinical_baselines_20260520/msg_tabular_hr_patient_train_metadata_clean.json \
  --epochs 300 \
  --batch-size 512 \
  --hidden-dim 32 \
  --target-tiw 0.1 \
  --seed 42
```

Training metadata:

- valid evidence rows: 7,911
- train rows: 4,516
- validation rows: 532
- train positives: 2,712
- validation positives: 361
- validation-selected alarm threshold: 0.5399338901042938
- best validation loss: 0.5287359356880188

Test-set denominator summary:

- test patients: 2
- test recordings: 543
- test windows: 15,261
- valid test prediction rows: 2,872
- coverable test events used for metrics: 31
- test positive windows: 253

## Patient-Wise Test Results (pre-freeze exploratory, not for citation)

| Model | Sensitivity | Events | FAR/day | TIW | Median Lead Time |
| --- | ---: | ---: | ---: | ---: | ---: |
| random rate-matched | 0.613 | 19/31 | 1.889 | 0.0999 | 44,480 s |
| hour-of-day cycle prior | 0.290 | 9/31 | 0.844 | 0.0790 | 62,474 s |
| HR tachycardia rule | 0.645 | 20/31 | 1.964 | 0.1313 | 57,344 s |
| HR generic z-score rule | 0.806 | 25/31 | 2.323 | 0.1442 | 56,569 s |
| MSG HR tabular MLP | 0.871 | 27/31 | 2.006 | 0.1253 | 55,274 s |

The strongest run in this batch is the MSG HR tabular MLP:

- sensitivity: `0.871 (27/31 events)`
- false alarm rate: `2.006/day`
- time in warning: `0.1253`
- median lead time: `55,274 seconds`

## Evidence Files

Primary model artifacts on Hetzner:

- `outputs/msg_clinical_baselines_20260520/msg_patient_features_hr.parquet`
- `outputs/msg_clinical_baselines_20260520/msg_tabular_hr_patient_predictions_clean.parquet`
- `outputs/msg_clinical_baselines_20260520/msg_tabular_hr_patient_model_clean.pt`
- `outputs/msg_clinical_baselines_20260520/msg_tabular_hr_patient_train_metadata_clean.json`
- `outputs/msg_clinical_baselines_20260520/report_patient_tabular_hr_test_clean/baseline_results.csv`
- `outputs/msg_clinical_baselines_20260520/report_patient_tabular_hr_test_clean/prediction_metadata.csv`

Comparison reports on Hetzner:

- `outputs/msg_clinical_baselines_20260520/report_patient_random_test/baseline_results.csv`
- `outputs/msg_clinical_baselines_20260520/report_patient_cycle_test/baseline_results.csv`
- `outputs/msg_clinical_baselines_20260520/report_patient_rule_hr_tachy_test/baseline_results.csv`
- `outputs/msg_clinical_baselines_20260520/report_patient_rule_hr_generic_test/baseline_results.csv`

## Interpretation Boundaries

**These are pre-freeze exploratory numbers — not a benchmark result.** Per
`PLAYBOOK.md` §10 rule 1 ("No reported number before the benchmark is
frozen, Gate C") and §3 consequence 1 ("A model trained on an unfrozen,
unaudited, leaky benchmark yields a number that cannot be cited"), these
figures may not be presented as a "clinical-prototype benchmark result",
as final clinical efficacy, as regulatory evidence, or as a broad
multi-dataset claim. They are useful internally for pipeline development
and SOTA-planning context only.

Current limitations:

- Gate B is sampled human attestation, not a full manual source review of
  every event. The audit log has no per-seizure observation notes — to
  resist a Q1 reviewer's "show me the clinical audit" question,
  strengthen the log with per-seizure notes before Gate C /
  pre-registration.
- The test event denominator is 31 coverable seizures from 2 held-out
  patients.
- The model uses HR summary features only; ACC extraction was stopped
  because it was not needed for this first complete result and was still
  parsing.
- Thresholding targets validation TIW 0.1; test TIW can differ, as seen
  here.
- SeizeIT2 remains excluded from strict clinical claims until its
  duplicate recording-range audit issue is resolved.
- These numbers must not be cited externally (paper, leaderboard,
  abstract) until Gate C closes (frozen splits + Zenodo DOI).
