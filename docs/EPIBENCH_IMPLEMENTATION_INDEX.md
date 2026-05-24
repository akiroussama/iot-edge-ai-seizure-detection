# EpiBench Implementation Index

This index lists the current v1.0-draft artefacts created from phase 1 through phase 7.

## Normative Core

- `docs/EPIBENCH_SPEC_V1.md`
- `configs/epibench/epibench_v1.yaml`
- `schemas/epibench/dataset_evidence_card.schema.json`
- `schemas/epibench/split_manifest.schema.json`
- `schemas/epibench/failure_trace.schema.json`
- `schemas/epibench/result_bundle.schema.json`
- `schemas/epibench/claim_eligibility.schema.json`
- `schemas/epibench/sota_registry.schema.json`

## SOTA Alignment

- `configs/epibench/sota_registry_v1.yaml`
- `configs/epibench/conformance_suite_v1.yaml`
- `configs/epibench/submission_readiness_gate_v1.yaml`
- `docs/SOTA_REVIEW_2026.md`
- `docs/SOTA_CITATION_AUDIT_2026-05-18.md`

## Reference Implementation

- `src/epibench/spec.py`
- `src/epibench/validation.py`
- `src/epibench/scoring.py`
- `src/epibench/szcore_bridge.py`
- `src/epibench/submission_readiness.py`
- `src/epibench/inter_reviewer.py`
- `src/epibench/certification.py`
- `src/epibench/cli.py`
- `scripts/epibench.py`
- `scripts/epibench_build_msg_gate_c_package.py`
- `scripts/epibench_build_chbmit_package.py`
- `scripts/epibench_build_chbmit_waveform_micro_package.py`
- `scripts/epibench_build_evidence_panels.py`
- `scripts/epibench_build_coverage_audit.py`
- `scripts/epibench_build_reviewer_packet.py`
- `scripts/epibench_build_weight_sensitivity.py`
- `scripts/epibench_build_real_evidence_progression.py`
- `scripts/epibench_overclaim_audit.py`

## Worked Examples

- `examples/epibench/pilot_t1_eeg/result_bundle.yaml`
- `examples/epibench/patient_dependent_demo/result_bundle.yaml`
- `examples/epibench/failure_leakage/result_bundle.yaml`
- `examples/epibench/msg_preliminary_f/result_bundle.yaml`
- `examples/epibench/msg_gate_c_frozen_f/result_bundle.yaml`
- `examples/epibench/chbmit_patient_independent_d/result_bundle.yaml`
- `examples/epibench/chbmit_waveform_micro_d/dataset_card.yaml`
- `examples/epibench/chbmit_waveform_micro_d/split_manifest.yaml`
- `examples/epibench/chbmit_waveform_micro_d/failure_trace.yaml`
- `examples/epibench/chbmit_waveform_micro_d/result_bundle.yaml`
- `examples/epibench/early_warning_valid_w/result_bundle.yaml`
- `examples/epibench/early_warning_post_event_failure_w/result_bundle.yaml`
- `examples/epibench/far_explosion_failure_d/result_bundle.yaml`
- `examples/epibench/seizeit2_preliminary_f/result_bundle.yaml`
- `examples/epibench/szcore_bridge_demo/result_bundle.yaml`
- `examples/epibench/szcore_bridge_demo/imported_result_bundle.yaml`
- `examples/epibench/inter_reviewer_reviews.yaml`
- `reports/epibench_pilot_claim.json`
- `reports/epibench_pilot_claim.md`
- `reports/epibench_patient_dependent_claim.json`
- `reports/epibench_patient_dependent_claim.md`
- `reports/epibench_leakage_claim.json`
- `reports/epibench_leakage_claim.md`
- `reports/epibench_msg_preliminary_claim.json`
- `reports/epibench_msg_preliminary_claim.md`
- `reports/epibench_msg_gate_c_frozen_claim.json`
- `reports/epibench_msg_gate_c_frozen_claim.md`
- `reports/epibench_chbmit_patient_independent_claim.json`
- `reports/epibench_chbmit_patient_independent_claim.md`
- `reports/chbmit_patient_independent_null_metrics.json`
- `reports/epibench_chbmit_e2pi_package_report.md`
- `reports/chbmit_waveform_micro_metrics.json`
- `reports/epibench_chbmit_waveform_micro_claim.json`
- `reports/epibench_chbmit_waveform_micro_claim.md`
- `reports/epibench_chbmit_waveform_micro_report.md`
- `reports/epibench_early_warning_valid_claim.json`
- `reports/epibench_early_warning_valid_claim.md`
- `reports/epibench_early_warning_post_event_failure_claim.json`
- `reports/epibench_early_warning_post_event_failure_claim.md`
- `reports/epibench_far_explosion_claim.json`
- `reports/epibench_far_explosion_claim.md`
- `reports/epibench_evidence_panels/README.md`
- `reports/epibench_evidence_panels/bundle_summary.csv`
- `reports/epibench_evidence_panels/naive_score_leaderboard.csv`
- `reports/epibench_evidence_panels/sensitivity_only_leaderboard.csv`
- `reports/epibench_evidence_panels/claim_gated_leaderboard.csv`
- `reports/epibench_evidence_panels/rank_comparison.csv`
- `reports/epibench_evidence_panels/claim_gate_waterfall.csv`
- `reports/epibench_evidence_panels/failure_matrix.csv`
- `reports/epibench_evidence_panels/score_axis_matrix.csv`
- `reports/epibench_coverage_audit/README.md`
- `reports/epibench_coverage_audit/dataset_evidence_matrix.csv`
- `reports/epibench_coverage_audit/rubric_item_coverage.csv`
- `reports/epibench_coverage_audit/protocol_use_case_coverage.csv`
- `reports/epibench_coverage_audit/coverage_gaps.csv`
- `reports/epibench_overclaim_audit/README.md`
- `reports/epibench_overclaim_audit/overclaim_findings.csv`
- `reports/epibench_reviewer_packet/README.md`
- `reports/epibench_reviewer_packet/reviewer_attack_matrix.csv`
- `reports/epibench_reviewer_packet/pre_submission_action_register.csv`
- `reports/epibench_reviewer_packet/evidence_index.csv`
- `reports/epibench_weight_sensitivity/README.md`
- `reports/epibench_weight_sensitivity/weight_sensitivity_scores.csv`
- `reports/epibench_weight_sensitivity/weight_sensitivity_rank_stability.csv`
- `reports/epibench_weight_sensitivity/weight_sensitivity_summary.csv`
- `reports/epibench_real_evidence_progression/README.md`
- `reports/epibench_real_evidence_progression/real_package_matrix.csv`
- `reports/epibench_real_evidence_progression/next_step_register.csv`
- `reports/epibench_seizeit2_preliminary_claim.json`
- `reports/epibench_seizeit2_preliminary_claim.md`
- `reports/epibench_szcore_bridge_claim.json`
- `reports/epibench_szcore_bridge_claim.md`
- `reports/epibench_szcore_import_claim.json`
- `reports/epibench_szcore_import_claim.md`
- `reports/epibench_submission_readiness_report.json`
- `reports/epibench_submission_readiness_result.json`
- `reports/epibench_real_evidence_gap_report.md`
- `reports/epibench_local_data_inventory_2026-05-24.md`
- `reports/epibench_inter_reviewer_report.json`
- `reports/epibench_conformance_result.json`

## Phase Documents

- `docs/EPIBENCH_PHASE1_DETAILED_PLAN.md`
- `docs/EPIBENCH_PHASE1_ADJUDICATION_EXAMPLES.md`
- `docs/EPIBENCH_PHASE1_REVIEW_CHECKLIST.md`
- `docs/EPIBENCH_PHASE2_SINGLE_SOURCE_OF_TRUTH.md`
- `docs/EPIBENCH_PHASE3_CERTIFICATION_STANDARD.md`
- `docs/EPIBENCH_PHASE4_REFERENCE_IMPLEMENTATION.md`
- `docs/EPIBENCH_PHASE5_PILOT_EVIDENCE_PACKAGES.md`
- `docs/EPIBENCH_PHASE6_Q1_PAPER_STRATEGY.md`
- `docs/EPIBENCH_PHASE7_GOVERNANCE_ADOPTION.md`
- `docs/EPIBENCH_PROTOCOL_CONFORMANCE_SUITE.md`
- `docs/EPIBENCH_CERTIFICATION_SOP.md`
- `docs/EPIBENCH_Q1_REJECTION_AVOIDANCE_FEATURES.md`

## Adoption And Release

- `.github/ISSUE_TEMPLATE/epibench_dataset_proposal.md`
- `.github/ISSUE_TEMPLATE/epibench_result_bundle_submission.md`
- `docs/EPIBENCH_VERSIONING_POLICY.md`
- `docs/EPIBENCH_RELEASE_CHECKLIST.md`
- `CHANGELOG.md`

## Smoke Commands

```powershell
python scripts\epibench.py validate-sota-registry configs\epibench\sota_registry_v1.yaml
python scripts\epibench.py run-conformance-suite configs\epibench\conformance_suite_v1.yaml
python scripts\epibench.py inter-reviewer-report examples\epibench\inter_reviewer_reviews.yaml --out reports\epibench_inter_reviewer_report.json
python scripts\epibench.py certify examples\epibench\pilot_t1_eeg\result_bundle.yaml --out reports\epibench_pilot_claim.json --report reports\epibench_pilot_claim.md
python scripts\epibench.py certify examples\epibench\patient_dependent_demo\result_bundle.yaml --out reports\epibench_patient_dependent_claim.json --report reports\epibench_patient_dependent_claim.md
python scripts\epibench.py certify examples\epibench\failure_leakage\result_bundle.yaml --out reports\epibench_leakage_claim.json --report reports\epibench_leakage_claim.md
python scripts\epibench_build_msg_gate_c_package.py
python scripts\epibench.py certify examples\epibench\msg_gate_c_frozen_f\result_bundle.yaml --out reports\epibench_msg_gate_c_frozen_claim.json --report reports\epibench_msg_gate_c_frozen_claim.md
python scripts\epibench_build_chbmit_package.py
python scripts\epibench.py certify examples\epibench\chbmit_patient_independent_d\result_bundle.yaml --out reports\epibench_chbmit_patient_independent_claim.json --report reports\epibench_chbmit_patient_independent_claim.md
python scripts\epibench_build_chbmit_waveform_micro_package.py
python scripts\epibench.py certify examples\epibench\chbmit_waveform_micro_d\result_bundle.yaml --out reports\epibench_chbmit_waveform_micro_claim.json --report reports\epibench_chbmit_waveform_micro_claim.md
python scripts\epibench.py certify examples\epibench\early_warning_valid_w\result_bundle.yaml --out reports\epibench_early_warning_valid_claim.json --report reports\epibench_early_warning_valid_claim.md
python scripts\epibench.py certify examples\epibench\early_warning_post_event_failure_w\result_bundle.yaml --out reports\epibench_early_warning_post_event_failure_claim.json --report reports\epibench_early_warning_post_event_failure_claim.md
python scripts\epibench.py certify examples\epibench\far_explosion_failure_d\result_bundle.yaml --out reports\epibench_far_explosion_claim.json --report reports\epibench_far_explosion_claim.md
python scripts\epibench_build_evidence_panels.py
python scripts\epibench_build_coverage_audit.py
python scripts\epibench_build_weight_sensitivity.py
python scripts\epibench_build_real_evidence_progression.py
python scripts\epibench_overclaim_audit.py
python scripts\epibench_build_reviewer_packet.py
python scripts\epibench.py certify examples\epibench\msg_preliminary_f\result_bundle.yaml --out reports\epibench_msg_preliminary_claim.json --report reports\epibench_msg_preliminary_claim.md
python scripts\epibench.py certify examples\epibench\seizeit2_preliminary_f\result_bundle.yaml --out reports\epibench_seizeit2_preliminary_claim.json --report reports\epibench_seizeit2_preliminary_claim.md
```

## Scientific Reading Order

1. `docs/EPIBENCH_SPEC_V1.md`
2. `docs/EPIBENCH_PHASE2_SINGLE_SOURCE_OF_TRUTH.md`
3. `docs/EPIBENCH_PHASE3_CERTIFICATION_STANDARD.md`
4. `docs/EPIBENCH_PHASE5_PILOT_EVIDENCE_PACKAGES.md`
5. `docs/EPIBENCH_PHASE6_Q1_PAPER_STRATEGY.md`
6. `docs/EPIBENCH_PHASE7_GOVERNANCE_ADOPTION.md`
