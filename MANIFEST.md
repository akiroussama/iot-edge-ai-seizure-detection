# Package manifest

## Immediate-value files

- `README.md`: project usage and scope.
- `PROJECT_STATUS.md`: current status and next action.
- `docs/ROADMAP_HIGH_LEVEL.md`: roadmap to the thesis end.
- `docs/HUMAN_INTERVENTION_CHECKPOINTS.md`: moments where the user must intervene.
- `docs/HUMAN_LABEL_AUDIT_PROTOCOL.md`: concrete seizure timeline audit workflow.
- `docs/A100_RUNBOOK.md`: when and how to train.
- `docs/PAPER1_OUTLINE.md`: first-paper structure.
- `docs/CLAUDE_CODE_PROMPTS.md`: prompts to continue implementation.
- `docs/CODEX_REVIEW_PROMPTS.md`: prompts for strict code review.
- `docs/CODEX_REVIEW_PROMPT.md`: concise single-review prompt.
- `docs/RISK_REGISTER.md`: scientific risks and mitigations.
- `docs/DATASET_INTEGRATION_PLAN.md`: concrete SeizeIT2/MSG integration commands and checkpoints.
- `docs/SOTA_REVIEW_2026.md`: current literature snapshot and gap analysis.
- `docs/PUBLICATION_PROPOSAL.md`: paper proposal and claim boundaries.
- `docs/REAL_DATA_QUICKSTART.md`: real dataset command sequence.
- `scripts/make_dataset_report.py`: dataset-specific report generator for real-data pipeline checks.
- `scripts/extract_msg_features.py`: MSG nested Empatica HR/ACC window feature extraction.
- `scripts/run_rule_baseline.py`: transparent HR tachycardia, ACC energy, and generic z-score rule baselines.

## Core source modules

- `src/labeling/sph_sop.py`
- `src/metrics/`
- `src/splits/`
- `src/preprocessing/windowing.py`
- `src/baselines/`
- `src/features/window_features.py`
- `src/forecasting/hazard.py`
- `src/forecasting/alarm_controller.py`
- `src/calibration/`
- `src/models/`

## Tests

- Tests cover labels, metrics, calibration, models, hazard, features, leakage, windowing,
  random/rule baselines, schemas, threshold sweeps, label audit export, mock dataset parsers,
  BIDS-score SeizeIT2 events, Zenodo MSG nested ZIP manifests, and MSG Empatica HR/ACC feature extraction.

## Reports

- `reports/synthetic_demo/`: generated synthetic demo outputs.
- `reports/*_real_check/`: local real-data pipeline check reports. These are not paper results until manual audit is complete.
- `reports/msg_hr_tachycardia_check/`: local full-download MSG HR-rule baseline check. This is an audit artifact, not a clinical result.
