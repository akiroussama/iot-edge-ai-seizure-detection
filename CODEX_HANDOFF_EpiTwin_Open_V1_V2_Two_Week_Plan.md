# Codex Handoff — EpiTwin-Open v1.0 / v2.0 Two-Week Execution Plan

Copy-paste this entire file into Codex as the next handoff prompt.

---

## Role

You are Codex acting as a senior biomedical ML research engineer, software architect, reproducibility lead, and strict methodological reviewer.

You are continuing the EpiTwin-Open project after the v0.1 scaffold was verified and improved.

The user wants a two-week, high-intensity implementation push to turn the current scaffold into:

- **EpiTwin-Open v1.0**: real-dataset-ready benchmark infrastructure.
- **EpiTwin-Open v2.0**: first research-grade baseline/model package ready for A100 experiments and paper v0 results.

You must work as if this is a serious PhD research codebase headed toward IEEE TBME / JBHI / npj Digital Medicine.

Do not overclaim. Do not invent results. Do not fake real dataset outputs. If real data are not mounted, build robust parsers, mocks, dry-runs, tests, and clear instructions.

---

## Current Known Status from Previous Codex Run

A previous Codex pass reported:

```text
EpiTwin-Open is now a stronger v0.1 benchmark scaffold.
42 tests passing.

Verified commands:
uv sync --extra dev --extra torch
uv run python -m pytest -q
uv run ruff check .
./RUN_THIS_FIRST.sh
uv run python scripts/run_synthetic_demo.py
uv run python scripts/make_report.py --synthetic --out-dir reports
uv run python -u scripts/train_epitwin_ssl.py --epochs 1 --batch-size 1 --time-steps 4 --hidden-dim 4 --backbone gru
```

Important improvements already made:
- alarm metrics now sum monitoring time per patient/recording instead of merging simultaneous patients into one clock;
- temporal split purging for overlapping boundary windows;
- leakage audit is strategy-aware;
- duplicate-window and postictal-contamination checks;
- fixed window generation;
- mock-tested SeizeIT2 BIDS-like event parsing;
- MSG seizure/ZIP manifest helpers;
- removed hidden tabulate dependency;
- RUN_THIS_FIRST.sh uses uv run python when available;
- reliability table and sensitivity-at-fixed-Time-in-Warning utilities;
- edge-case tests for SPH/SOP, recording scope, no-event patients, multiple seizures, postictal overlap, random baseline behavior, windowing, mock parsers;
- docs/DATASET_INTEGRATION_PLAN.md and docs/CODEX_REVIEW_PROMPT.md added.

Remaining risks from previous pass:
- no real SeizeIT2 or My Seizure Gauge raw data mounted;
- SeizeIT2 support parses supported BIDS-like event metadata only; waveform decoding still needs real dataset-specific work;
- MSG support parses seizure times and ZIP manifests; HR/steps stream extraction is next;
- feature normalization leakage cannot be fully machine-checked until feature-generation metadata records fit splits;
- synthetic demo is software verification only, not clinical evidence;
- A100 training is not cleared yet.

Do not trust this blindly. Verify again before modifying.

---

## Project Scientific Vision

The project is not “just another deep learning classifier”.

The core research thesis is:

> Wearable seizure forecasting must be evaluated as calibrated, patient-specific risk estimation under observability and alarm-burden constraints, not as naive preictal/interictal window classification.

The project must distinguish:

1. **Detection**  
   “Is a seizure happening now?”

2. **Early warning**  
   “Is there a near-immediate signal shortly before clinical manifestation?”

3. **Short-horizon forecasting**  
   “Is a seizure likely in the next 5–30 minutes?”

4. **Long-horizon forecasting**  
   “Is the patient at elevated risk in the next hour/day?”

5. **Modality-limited forecasting**  
   “What remains observable when bte-EEG or full multimodal sensing is removed?”

6. **Forecastability / observability estimation**  
   “Is this event/risk state actually observable from the available wearable modalities?”

The first publication must be honest:

Allowed claims:
- We provide a leakage-safe public benchmark framework.
- We define detection, early warning, short-horizon forecasting, and long-horizon forecasting separately.
- We evaluate using event-level sensitivity, FAR/day, Time-in-Warning, lead time, Brier score, ECE, and calibration.
- We quantify modality-limited forecastability.
- We avoid forcing edge sensors to hallucinate EEG-only information.

Forbidden claims for v1.0/v2.0:
- “We predict all focal seizures.”
- “The tibia sensor works.”
- “Closed-loop VNS is ready.”
- “Less than 1 mW is proven.”
- “90% sensitivity at 0.1 FAR/day” unless real data prove it.
- “Liquid/Mamba/SNN is biologically superior” without controlled ablations.

---

## Datasets

### Primary Dataset 1 — SeizeIT2

Use for:
- multimodal wearable focal epilepsy;
- bte-EEG, ECG, EMG, ACC/GYR;
- detection, early warning, short-horizon forecasting;
- full-vs-edge observability analysis.

Important:
SeizeIT2 is detection-oriented. Treat true preictal forecasting claims cautiously.

### Primary Dataset 2 — My Seizure Gauge Long-term Wearable Data

Use for:
- longitudinal HR/steps;
- hourly/daily risk forecasting;
- patient-specific temporal evaluation;
- rhythm/cycle baselines.

### Optional Later

- CHB-MIT
- TUH/TUSZ

Do not make them core v1.0/v2.0 unless the main datasets are already integrated.

---

# Version Definitions

## EpiTwin-Open v1.0 — “Real-Dataset-Ready Benchmark”

v1.0 is complete when the repo can process real or mock-real SeizeIT2 and MSG-like layouts into standardized parquet artifacts and produce a benchmark report.

v1.0 deliverables:

1. Clean repository, reproducible environment, tests passing.
2. Real-data-ready dataset integration layer.
3. Standardized artifacts:
   - `metadata.parquet`
   - `events.parquet`
   - `windows.parquet`
   - `forecast_labels.parquet`
   - `modality_availability.parquet`
   - `features.parquet` for simple features if feasible
4. SPH/SOP label generation validated by tests.
5. Ictal/postictal exclusion validated.
6. Patient-wise, temporal, and center-wise split logic.
7. Leakage audit report.
8. Synthetic + mock-dataset demos.
9. Simple baselines:
   - random rate-matched
   - cycle-only
   - HR/tachycardia rule
   - ACC energy
   - generic anomaly score
10. Report generation:
   - dataset summary
   - label distribution
   - baseline results
   - leakage audit
   - human audit checklist
11. Clear instructions for the user to mount real datasets and run parsing.
12. No A100 required.

v1.0 is not required to produce high model scores.

## EpiTwin-Open v2.0 — “First Research-Grade Baselines + A100-Ready Model Package”

v2.0 is complete when the repo can run first real or mock-real baseline experiments, create paper-style result tables, and launch controlled A100 experiments only after data/label checks pass.

v2.0 deliverables:

1. v1.0 complete.
2. Feature extraction layer:
   - HR/ECG-derived features if available;
   - ACC/GYR features;
   - EMG energy/burst features;
   - simple EEG spectral features if feasible;
   - robust missing-modality handling.
3. Baseline experiment runner:
   - config-driven;
   - split-aware;
   - outputs predictions parquet;
   - evaluates clinical metrics.
4. TCN-small / GRU-small supervised baselines.
5. EpiTwin-SSL v0.2:
   - masked modeling;
   - future latent prediction;
   - cross-modal placeholder;
   - hazard/risk head;
   - uncertainty head;
   - supports missing modalities.
6. A100 run configs:
   - small supervised baseline;
   - SSL smoke;
   - SSL base;
   - ablation templates.
7. Calibration/alarm controller:
   - fixed threshold;
   - target FAR/day threshold;
   - target Time-in-Warning threshold;
   - patient-specific threshold option.
8. Observable-latent student v0.1:
   - full teacher modalities vs edge modalities;
   - no blind hallucination of EEG-only information;
   - uncertainty output.
9. Paper v0 assets:
   - Table 1 dataset summary;
   - Table 2 baseline metrics;
   - Figure 1 task timeline;
   - Figure 2 pipeline overview;
   - Figure 3 FAR/TIW tradeoff placeholder or real result if data available;
   - Methods skeleton.
10. Human intervention checklist:
   - label audit;
   - split audit;
   - A100 clearance;
   - paper claim clearance.

v2.0 is not a final paper. It is the first research-grade package that makes paper writing realistic.

---

# Two-Week Execution Roadmap

Assume 14 calendar days of continuous implementation/review work. If real data are not available, complete all dry-run/mocked pathways and leave exact commands for the user.

## Day 0 — Verification and Baseline Freeze

Goal:
Verify current package, freeze v0.1 status, and prepare v1.0/v2.0 tracking.

Tasks:
1. Inspect repository tree.
2. Read:
   - README.md
   - PROJECT_STATUS.md
   - MANIFEST.md
   - docs/DATASET_INTEGRATION_PLAN.md
   - docs/ROADMAP_HIGH_LEVEL.md if present
3. Run:
   ```bash
   uv sync --extra dev --extra torch
   uv run python -m pytest -q
   uv run ruff check .
   ./RUN_THIS_FIRST.sh
   uv run python scripts/run_synthetic_demo.py
   uv run python scripts/make_report.py --synthetic --out-dir reports
   uv run python -u scripts/train_epitwin_ssl.py --epochs 1 --batch-size 1 --time-steps 4 --hidden-dim 4 --backbone gru
   ```
4. Create or update:
   - `docs/V1_V2_TWO_WEEK_PLAN.md`
   - `docs/VERSION_ACCEPTANCE_CRITERIA.md`
   - `reports/v0_1_verification.md`
5. If git is available:
   - create branch `feature/v1-v2-two-week-roadmap`
   - commit verification docs after tests pass.

Acceptance criteria:
- All current tests pass or failures are documented and fixed.
- v0.1 status is clearly documented.
- No new model work begins before verification.

---

## Day 1 — Repository Hardening and CLI Standardization

Goal:
Make the repo easy to run, reproduce, and demo.

Tasks:
1. Ensure `pyproject.toml` has correct dependencies and optional extras:
   - dev
   - torch
   - docs optional if needed
2. Ensure commands work via `uv run`.
3. Ensure Makefile targets map to direct commands:
   - `test`
   - `lint`
   - `demo`
   - `report`
   - `smoke-train`
   - `all-checks`
4. If make is unavailable, document direct equivalents.
5. Ensure `RUN_THIS_FIRST.sh` is robust:
   - detects uv;
   - falls back cleanly;
   - prints what it is doing;
   - fails fast on errors.
6. Add `.gitignore` or verify it prevents committing:
   - raw data
   - processed large parquet
   - model checkpoints
   - wandb/mlruns
   - caches
7. Add `configs/default.yaml` or equivalent if config system exists.
8. Create `docs/COMMANDS.md`.

Acceptance criteria:
- New user can run one command to verify demo.
- No hidden dependency.
- No raw data paths hardcoded.

---

## Day 2 — Dataset Integration Layer v1

Goal:
Standardize dataset outputs independent of raw format.

Tasks:
1. Create/verify schema definitions:
   - metadata schema
   - events schema
   - windows schema
   - modality availability schema
   - features schema
   - predictions schema
2. Implement schema validation helpers:
   - required columns;
   - dtype checks;
   - timestamp checks;
   - no null patient IDs;
   - seizure_start < seizure_end.
3. Add `src/datasets/schemas.py`.
4. Add `src/utils/validation.py`.
5. Add tests for schema validation.
6. Ensure `prepare_seizeit2.py` and `prepare_msg.py` can run in:
   - real mode;
   - dry-run mode;
   - mock mode.
7. Mock mode should generate tiny deterministic dataset artifacts.

Acceptance criteria:
- Mock SeizeIT2 and mock MSG produce standardized parquet artifacts.
- Schema tests pass.
- Real mode fails with clear instructions if raw path missing.

---

## Day 3 — SeizeIT2 Parser v1

Goal:
Make SeizeIT2 integration as real-data-ready as possible without faking.

Tasks:
1. Inspect expected BIDS/OpenNeuro-like layout assumptions.
2. Implement robust discovery:
   - subject folders;
   - session folders;
   - recording files;
   - events TSV/CSV;
   - sidecar JSON if present.
3. Parse seizure events from supported event files.
4. Extract:
   - patient_id;
   - recording_id;
   - center_id if inferable;
   - seizure_start;
   - seizure_end;
   - optional seizure_type;
   - source file path.
5. Build modality availability manifest:
   - bte-EEG;
   - ECG;
   - EMG;
   - ACC;
   - GYR;
   - sampling rate if sidecar contains it;
   - channel count if inferable.
6. Do not decode all waveforms yet unless straightforward.
7. Add dry-run report:
   - files discovered;
   - subjects discovered;
   - event files discovered;
   - modalities discovered.
8. Add tests using miniature BIDS-like mock folder.

Acceptance criteria:
- `prepare_seizeit2.py --mock` creates standardized parquets.
- `prepare_seizeit2.py --raw-dir <missing>` gives clear error.
- Parser does not silently invent missing metadata.
- Tests pass.

---

## Day 4 — My Seizure Gauge Parser v1

Goal:
Support MSG HR/steps/seizure event integration.

Tasks:
1. Implement robust discovery of ZIPs or extracted folders.
2. Create manifest of:
   - participant_id;
   - files;
   - HR streams;
   - steps streams;
   - seizure annotation files;
   - date/time coverage if inferable.
3. Parse seizure times into standardized events.
4. Parse HR/steps streams if feasible:
   - timestamp;
   - patient_id;
   - value;
   - source file;
   - signal type.
5. If formats vary, implement adapters and document supported formats.
6. Add hourly window generator for MSG:
   - hourly risk;
   - daily risk optional.
7. Add mock tests using tiny fake HR/steps CSVs and seizure file.

Acceptance criteria:
- `prepare_msg.py --mock` creates standardized parquets.
- HR/steps stream mock extraction works.
- Hourly windows can be generated.
- Tests pass.

---

## Day 5 — Windowing + Labeling Production Pass

Goal:
Make window generation and SPH/SOP labeling robust enough for real datasets.

Tasks:
1. Verify no windows cross recording boundaries.
2. Add patient/recording grouping.
3. Add support for numeric seconds and datetimes.
4. Add recording coverage checks.
5. Add multi-seizure cluster handling.
6. Add postictal overlap tests.
7. Add boundary tests:
   - seizure exactly at SPH lower boundary should be positive;
   - seizure exactly at SOP upper boundary should be negative if interval is half-open;
   - seizure before SPH should be negative for forecasting task;
   - seizure inside current window should be ictal/excluded.
8. Add `scripts/label_windows.py` if not present.
9. Add `scripts/audit_labels.py`:
   - prints windows around seizure onsets;
   - exports CSV for manual audit;
   - generates a simple timeline table.

Acceptance criteria:
- Labeling has exhaustive synthetic tests.
- Human can inspect 5–10 seizures via exported timeline CSV.
- No ambiguity in interval conventions.

---

## Day 6 — Metrics Production Pass

Goal:
Make metrics reviewer-proof.

Tasks:
1. Review event-level sensitivity.
2. Review false alarm association logic.
3. Review Time-in-Warning logic per patient/recording.
4. Review lead time logic.
5. Add tests for:
   - simultaneous patients;
   - overlapping alarms;
   - adjacent alarms;
   - excluded windows;
   - alarm duration from irregular windows;
   - seizure with multiple alarms;
   - alarm after seizure should not count as forecast.
6. Add reliability table outputs.
7. Add threshold sweep:
   - thresholds 0..1;
   - FAR/day;
   - TIW;
   - sensitivity;
   - Brier;
   - ECE.
8. Add `scripts/sweep_thresholds.py`.

Acceptance criteria:
- Metrics survive synthetic edge cases.
- Reports distinguish window-level and event-level metrics.
- False alarm logic is documented.

---

## Day 7 — v1.0 Release Candidate

Goal:
Finalize v1.0.

Tasks:
1. Run all checks:
   ```bash
   uv run python -m pytest -q
   uv run ruff check .
   ./RUN_THIS_FIRST.sh
   uv run python scripts/run_synthetic_demo.py
   uv run python scripts/make_report.py --synthetic --out-dir reports/v1_0_demo
   ```
2. Create:
   - `PROJECT_STATUS.md` updated to v1.0-rc;
   - `reports/v1_0_release_candidate.md`;
   - `docs/REAL_DATA_QUICKSTART.md`;
   - `docs/HUMAN_LABEL_AUDIT_PROTOCOL.md`.
3. Ensure professor demo can be run without real datasets.
4. Ensure real dataset next commands are clear.

v1.0 acceptance criteria:
- all tests pass;
- mock SeizeIT2 pipeline works;
- mock MSG pipeline works;
- synthetic demo works;
- report generation works;
- label audit export exists;
- leakage audit exists;
- baselines can run on mock/synthetic artifacts;
- clear disclaimer: synthetic/mock only unless real data were mounted.

---

# Week 2 — v2.0

## Day 8 — Feature Extraction Layer

Goal:
Create simple, robust features before advanced deep models.

Tasks:
1. Add `src/features/`.
2. Implement feature extractors:
   - HR/ECG:
     - mean HR;
     - HR z-score;
     - HR slope;
     - HR variability if RR available;
   - ACC/GYR:
     - magnitude mean/std;
     - jerk energy;
     - stillness ratio;
     - activity level;
   - EMG:
     - RMS;
     - burst proxy;
     - energy;
   - EEG if feasible:
     - bandpower;
     - spectral entropy;
     - simple artifact flags.
3. Feature extraction must:
   - be per split safe;
   - not fit normalization on test data;
   - record normalization metadata;
   - handle missing modalities.
4. Add `scripts/extract_features.py`.
5. Add tests on synthetic/mock signals.

Acceptance criteria:
- Feature parquet generated for mock data.
- Missing modalities fail gracefully.
- Normalization metadata exists or feature extraction avoids fitted normalization.

---

## Day 9 — Baseline Experiment Runner

Goal:
Run real benchmark-style baselines with config-driven CLI.

Tasks:
1. Create/verify `scripts/run_experiment.py`.
2. Support configs:
   - dataset;
   - horizon;
   - split strategy;
   - model/baseline;
   - threshold strategy.
3. Implement baselines:
   - random rate-matched;
   - cycle-only;
   - HR rule;
   - ACC rule;
   - EMG rule;
   - logistic regression on features;
   - gradient boosting optional if sklearn available.
4. Output:
   - predictions.parquet;
   - metrics.json;
   - threshold_sweep.csv;
   - config.yaml copy;
   - run_summary.md.
5. Add test with synthetic data.

Acceptance criteria:
- One command runs a full synthetic experiment and produces report artifacts.
- Outputs are deterministic under seed.
- Metrics are event-level and clinical.

---

## Day 10 — Supervised Deep Baselines

Goal:
Add modest deep baselines, not final model.

Tasks:
1. Ensure TCN-small works on feature sequences or raw-lite tensors.
2. Add GRU-small baseline.
3. Add config:
   - `configs/experiments/tcn_small_sph5_sop30.yaml`
   - `configs/experiments/gru_small_sph5_sop30.yaml`
4. Add training script:
   - early stopping;
   - deterministic seed;
   - patient-wise split;
   - save predictions;
   - save metrics;
   - save training curve CSV.
5. Keep CPU smoke tests tiny.
6. Add A100-ready config but do not require A100.

Acceptance criteria:
- CPU smoke training passes.
- No leakage through normalization.
- Outputs predictions in same format as baselines.

---

## Day 11 — EpiTwin-SSL v0.2

Goal:
Improve foundation-model scaffold while keeping it testable.

Tasks:
1. Verify model modules:
   - modality encoders;
   - fusion;
   - backbone;
   - reconstruction head;
   - future prediction head;
   - hazard/risk head;
   - uncertainty head.
2. Add losses:
   - masked reconstruction;
   - future latent prediction;
   - cross-modal prediction placeholder or implementation;
   - supervised hazard/risk loss;
   - uncertainty regularization if available.
3. Add missing-modality tests.
4. Add modality dropout tests.
5. Add causal masking tests if sequence model supports it.
6. Add config:
   - `configs/experiments/epitwin_ssl_smoke.yaml`
   - `configs/experiments/epitwin_ssl_a100_small.yaml`

Acceptance criteria:
- SSL smoke training passes on CPU.
- Model supports missing modalities.
- A100 small config exists but is not run unless user approves.

---

## Day 12 — Calibration + Alarm Controller

Goal:
Turn risk scores into clinically constrained alarms.

Tasks:
1. Implement/verify alarm controllers:
   - fixed threshold;
   - target FAR/day;
   - target Time-in-Warning;
   - patient-specific threshold;
   - uncertainty-gated threshold.
2. Add threshold selection on validation split only.
3. Add tests:
   - threshold fitted only on validation;
   - test labels not used in threshold fitting;
   - target TIW approximately matched;
   - target FAR selection robust to no-event patient.
4. Add reporting:
   - sensitivity vs FAR curve;
   - sensitivity vs TIW curve;
   - threshold table.

Acceptance criteria:
- No threshold leakage.
- Alarm controller outputs clinical metrics.
- Report includes tradeoff, not just one threshold.

---

## Day 13 — Observable Student + Neuro-Symbolic Soft Constraints

Goal:
Prepare the distinctive research contribution.

Tasks:
1. Implement/verify observable edge student:
   - teacher full modalities;
   - student edge modalities;
   - latent distillation;
   - uncertainty output;
   - optional abstention.
2. Add mode:
   - full modality;
   - no-EEG;
   - ECG+ACC;
   - HR+steps.
3. Implement/verify soft constraints:
   - poor signal quality → higher uncertainty;
   - tachycardia + low motion + good ECG → autonomic arousal;
   - high ACC + walking pattern → lower seizure specificity;
   - recent seizure → postictal, not preictal;
   - insufficient modalities → abstain / high uncertainty.
4. Add ablation flags:
   - no symbolic;
   - no uncertainty;
   - no student;
   - full model only.
5. Add tests on synthetic data.

Acceptance criteria:
- Student does not blindly imitate full teacher labels.
- Distillation target can be latent/shared representation.
- Uncertainty/abstention path exists.

---

## Day 14 — v2.0 Release Candidate and Handoff

Goal:
Finalize v2.0 package.

Tasks:
1. Run all checks:
   ```bash
   uv run python -m pytest -q
   uv run ruff check .
   ./RUN_THIS_FIRST.sh
   uv run python scripts/run_synthetic_demo.py
   uv run python scripts/make_report.py --synthetic --out-dir reports/v2_0_demo
   uv run python -u scripts/train_epitwin_ssl.py --epochs 1 --batch-size 1 --time-steps 4 --hidden-dim 4 --backbone gru
   ```
2. Run synthetic baseline experiment:
   ```bash
   uv run python scripts/run_experiment.py --config configs/experiments/synthetic_random.yaml
   uv run python scripts/run_experiment.py --config configs/experiments/synthetic_tcn_small.yaml
   ```
   If exact config names differ, create them.
3. Create:
   - `PROJECT_STATUS.md` updated to v2.0-rc;
   - `reports/v2_0_release_candidate.md`;
   - `docs/A100_LAUNCH_CHECKLIST.md`;
   - `docs/PAPER1_RESULTS_TEMPLATE.md`;
   - `docs/NEXT_30_DAYS_PLAN.md`.
4. Package handoff:
   - file tree summary;
   - commands;
   - known limitations;
   - what needs user intervention;
   - what can run next.

v2.0 acceptance criteria:
- tests pass;
- ruff passes;
- v1.0 functionality preserved;
- synthetic full benchmark works;
- feature extraction works on mock/synthetic data;
- baseline experiment runner works;
- EpiTwin-SSL smoke works;
- A100 configs exist;
- no real-data clinical claims unless real data were mounted and processed.

---

# Mandatory Tests to Add or Verify

## Labeling Tests

1. seizure at SPH lower boundary → positive.
2. seizure at SOP upper boundary → negative if half-open interval.
3. seizure before SPH → negative.
4. seizure inside current window → ictal/excluded.
5. postictal overlap → excluded.
6. multiple seizures → nearest next/last computed correctly.
7. patient with no seizures → no positives, time_to_next null/inf.
8. separate recordings → no cross-recording event leakage.

## Metrics Tests

1. simultaneous patients do not collapse monitored time.
2. excluded windows do not count.
3. multiple alarms for one event count once for sensitivity.
4. false alarm counted correctly when no following seizure.
5. alarm after seizure is not a forecast.
6. irregular window durations handled.
7. lead time from first associated alarm.
8. threshold sweep monotonic sanity checks.

## Split Tests

1. patient-wise split no shared patient.
2. temporal split no overlapping windows at boundary.
3. purge works.
4. center-wise placeholder behavior clear.
5. leakage audit catches duplicate windows.
6. leakage audit catches postictal contamination if labels wrong.

## Dataset Parser Tests

1. mock SeizeIT2 BIDS-like tree.
2. missing event file.
3. malformed event times.
4. missing modality.
5. mock MSG HR/steps CSV.
6. mock MSG seizure annotation.
7. ZIP manifest detection.
8. dry-run mode.

## Model Tests

1. forward pass tiny batch.
2. missing modality.
3. modality dropout.
4. finite loss.
5. causal shape.
6. CPU smoke training.
7. prediction output schema.

---

# Files to Create or Update

Create/update these docs:

```text
docs/V1_V2_TWO_WEEK_PLAN.md
docs/VERSION_ACCEPTANCE_CRITERIA.md
docs/COMMANDS.md
docs/REAL_DATA_QUICKSTART.md
docs/HUMAN_LABEL_AUDIT_PROTOCOL.md
docs/A100_LAUNCH_CHECKLIST.md
docs/PAPER1_RESULTS_TEMPLATE.md
docs/NEXT_30_DAYS_PLAN.md
reports/v0_1_verification.md
reports/v1_0_release_candidate.md
reports/v2_0_release_candidate.md
```

Create/update scripts:

```text
scripts/prepare_seizeit2.py
scripts/prepare_msg.py
scripts/make_windows.py
scripts/label_windows.py
scripts/audit_labels.py
scripts/extract_features.py
scripts/run_baseline.py
scripts/run_experiment.py
scripts/evaluate_predictions.py
scripts/sweep_thresholds.py
scripts/make_report.py
scripts/run_synthetic_demo.py
scripts/train_epitwin_ssl.py
```

Create/update modules:

```text
src/datasets/
src/preprocessing/
src/features/
src/labeling/
src/metrics/
src/calibration/
src/splits/
src/baselines/
src/models/
src/ssl/
src/forecasting/
src/distillation/
src/symbolic/
src/reports/
src/utils/
```

---

# Reporting Requirements

At the end of each work block, produce a concise status:

```text
Status:
What changed:

Passing commands:
- ...

Files modified:
- ...

Methodological risks:
- ...

Blocked on:
- ...

Next recommended action:
- ...
```

At the end of the full two-week implementation, produce:

```text
v1.0 status: pass / partial / fail
v2.0 status: pass / partial / fail

Professor demo readiness: yes/no
Real dataset integration readiness: yes/no
A100 training readiness: yes/no
Paper writing readiness: yes/no

Do not start A100 unless:
- real labels validated
- real splits validated
- random baseline run
- leakage audit clean
- human manually inspected seizure timelines
```

---

# Non-Negotiable Rules

1. Do not fake results.
2. Do not make clinical claims from synthetic data.
3. Do not train huge models before benchmark correctness.
4. Do not use accuracy as primary metric.
5. Do not allow random window split by default.
6. Do not count excluded windows in metrics unless explicitly configured.
7. Do not fit normalization or thresholds on test data.
8. Do not silently drop patients/events.
9. Do not commit raw data or model checkpoints.
10. Do not claim tibia/IoT hardware validation in v1.0/v2.0.

---

# Final Codex Objective

By the end of this handoff, the repo should be ready for:

1. **Professor demo**
   - methodology demo;
   - synthetic/mock results;
   - clear roadmap;
   - no overclaiming.

2. **Real dataset integration**
   - SeizeIT2 and MSG parser pathways;
   - standardized artifacts;
   - label audit workflow.

3. **First baseline experiments**
   - random/cycle/HR/ACC/EMG/logistic/TCN/GRU as applicable;
   - clinical metrics;
   - report outputs.

4. **A100 preparation**
   - config files;
   - launch checklist;
   - smoke-tested model;
   - not launched until human validation.

5. **Paper 1 preparation**
   - methods structure;
   - dataset summary template;
   - baseline results template;
   - figure/table plan;
   - risk/limitations section.

Remember:
The first major win is not a high model score.
The first major win is a benchmark and pipeline that a hostile biomedical ML reviewer cannot easily destroy.
