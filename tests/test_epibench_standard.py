from __future__ import annotations

from pathlib import Path

import pytest

from src.epibench.certification import certify_result_bundle, evaluate_dataset_tier
from src.epibench.cli import run_conformance_suite
from src.epibench.inter_reviewer import build_inter_reviewer_report
from src.epibench.scoring import compute_epi_score
from src.epibench.spec import load_spec
from src.epibench.submission_readiness import assess_submission_readiness
from src.epibench.szcore_bridge import import_szcore_metrics_as_result_bundle, map_szcore_metrics_to_result_bundle
from src.epibench.validation import SchemaValidationError, validate_artifact
from scripts.epibench_build_coverage_audit import build_coverage_audit
from scripts.epibench_build_evidence_panels import build_evidence_panels


REPO_ROOT = Path(__file__).resolve().parents[1]
PILOT = REPO_ROOT / "examples" / "epibench" / "pilot_t1_eeg"
LEAKAGE = REPO_ROOT / "examples" / "epibench" / "failure_leakage"
PATIENT_DEPENDENT = REPO_ROOT / "examples" / "epibench" / "patient_dependent_demo"
EARLY_WARNING_VALID = REPO_ROOT / "examples" / "epibench" / "early_warning_valid_w"
EARLY_WARNING_FAILURE = REPO_ROOT / "examples" / "epibench" / "early_warning_post_event_failure_w"
FAR_EXPLOSION = REPO_ROOT / "examples" / "epibench" / "far_explosion_failure_d"
MSG_PRELIMINARY = REPO_ROOT / "examples" / "epibench" / "msg_preliminary_f"
MSG_GATE_C_FROZEN = REPO_ROOT / "examples" / "epibench" / "msg_gate_c_frozen_f"
CHBMIT_E2PI = REPO_ROOT / "examples" / "epibench" / "chbmit_patient_independent_d"
SEIZEIT2_PRELIMINARY = REPO_ROOT / "examples" / "epibench" / "seizeit2_preliminary_f"


def test_epibench_example_artifacts_validate() -> None:
    assert validate_artifact("dataset-card", PILOT / "dataset_card.yaml")["dataset_id"] == "pilot_t1_eeg"
    assert validate_artifact("split", PILOT / "split_manifest.yaml")["split_policy"] == "leave_one_subject_out"
    assert validate_artifact("failure-trace", PILOT / "failure_trace.yaml")["run_id"] == "pilot_t1_eeg_edge_cnn_demo"
    assert validate_artifact("result-bundle", PILOT / "result_bundle.yaml")["requested_claim"] == "E2-PI"
    assert validate_artifact("sota-registry", REPO_ROOT / "configs" / "epibench" / "sota_registry_v1.yaml")


def test_epibench_clean_example_certifies_e2_pi() -> None:
    report = certify_result_bundle(PILOT / "result_bundle.yaml")

    assert report["final_claim"] == "E2-PI"
    assert "EpiBench-Claim-E2-PI" in report["badges"]
    assert "EpiBench-Leakage-Checked" in report["badges"]
    assert report["blocking_reasons"] == []


def test_epibench_leakage_example_downgrades_despite_high_score() -> None:
    clean = certify_result_bundle(PILOT / "result_bundle.yaml")
    leakage = certify_result_bundle(LEAKAGE / "result_bundle.yaml")

    assert leakage["score"]["epi_score"] > clean["score"]["epi_score"]
    assert leakage["final_claim"] == "E1"
    assert "EpiBench-Claim-E1" in leakage["badges"]
    assert any("PATIENT_LEAKAGE" in reason for reason in leakage["blocking_reasons"])
    assert "EpiBench-Leakage-Checked" not in leakage["badges"]


def test_epibench_patient_dependent_split_cannot_receive_e2_pi() -> None:
    report = certify_result_bundle(PATIENT_DEPENDENT / "result_bundle.yaml")

    assert report["requested_claim"] == "E2-PI"
    assert report["final_claim"] == "E2-PD"
    assert "EpiBench-Claim-E2-PD" in report["badges"]


def test_epibench_preliminary_real_packages_are_claim_limited_to_e1() -> None:
    msg = certify_result_bundle(MSG_PRELIMINARY / "result_bundle.yaml")
    seizeit2 = certify_result_bundle(SEIZEIT2_PRELIMINARY / "result_bundle.yaml")

    assert msg["final_claim"] == "E1"
    assert "EpiBench-Dataset-T3" in msg["badges"]
    assert any("LABEL_UNAUDITED" in reason for reason in msg["blocking_reasons"])
    assert seizeit2["final_claim"] == "E1"
    assert "EpiBench-Dataset-T3" in seizeit2["badges"]


def test_epibench_msg_gate_c_frozen_package_reaches_e2_pd_not_e2_pi() -> None:
    report = certify_result_bundle(MSG_GATE_C_FROZEN / "result_bundle.yaml")

    assert report["final_claim"] == "E2-PD"
    assert report["ceilings"]["split_policy"] == "E2-PD"
    assert report["dataset_tier_evaluation"]["effective_tier"] == "T2"
    assert "EpiBench-Dataset-T2" in report["badges"]
    assert "EpiBench-Leakage-Checked" in report["badges"]
    assert report["blocking_reasons"] == []


def test_epibench_chbmit_patient_independent_null_baseline_reaches_e2_pi_but_low_score() -> None:
    report = certify_result_bundle(CHBMIT_E2PI / "result_bundle.yaml")

    assert report["final_claim"] == "E2-PI"
    assert report["dataset_tier_evaluation"]["effective_tier"] == "T1"
    assert report["score"]["epi_score"] < 5
    assert report["score"]["floor_penalty_applied"] is True
    assert "EpiBench-Claim-E2-PI" in report["badges"]
    assert "real-time" in report["forbidden_phrases"]


def test_epibench_early_warning_track_distinguishes_warning_from_post_event_detection() -> None:
    valid = certify_result_bundle(EARLY_WARNING_VALID / "result_bundle.yaml")
    failure = certify_result_bundle(EARLY_WARNING_FAILURE / "result_bundle.yaml")

    assert valid["final_claim"] == "E2-PI"
    assert valid["ceilings"]["failure_status"] == "E4"
    assert failure["score"]["epi_score"] > valid["score"]["epi_score"]
    assert failure["final_claim"] == "E1"
    assert failure["ceilings"]["failure_status"] == "E1"
    assert any("post-event alarms" in reason for reason in failure["blocking_reasons"])


def test_epibench_far_explosion_blocks_high_sensitivity_detection_claim() -> None:
    report = certify_result_bundle(FAR_EXPLOSION / "result_bundle.yaml")

    assert report["final_claim"] == "E1"
    assert report["ceilings"]["failure_status"] == "E1"
    assert any("False alarm burden" in reason for reason in report["blocking_reasons"])


def test_epibench_loso_split_cannot_receive_e3_without_external_validation(tmp_path: Path) -> None:
    import yaml

    original = validate_artifact("result-bundle", PILOT / "result_bundle.yaml")
    original["requested_claim"] = "E3"
    original["dataset_card_path"] = str(PILOT / "dataset_card.yaml")
    original["split_manifest_path"] = str(PILOT / "split_manifest.yaml")
    original["failure_trace_path"] = str(PILOT / "failure_trace.yaml")
    bundle_path = tmp_path / "result_bundle.yaml"
    bundle_path.write_text(yaml.safe_dump(original, sort_keys=False), encoding="utf-8")

    report = certify_result_bundle(bundle_path)

    assert report["final_claim"] == "E2-PI"


def test_epibench_dataset_tier_is_computed_fail_closed() -> None:
    spec = load_spec()
    pilot = validate_artifact("dataset-card", PILOT / "dataset_card.yaml")
    msg = validate_artifact("dataset-card", MSG_PRELIMINARY / "dataset_card.yaml")

    assert evaluate_dataset_tier(pilot, spec)["effective_tier"] == "T1"
    msg_eval = evaluate_dataset_tier(msg, spec)
    assert msg_eval["declared_tier"] == "T2"
    assert msg_eval["effective_tier"] == "T3"
    assert msg_eval["downgraded"] is True
    assert "synchronization" in msg_eval["missing_core_mts_items"]


def test_epibench_conformance_suite_passes() -> None:
    result = run_conformance_suite(REPO_ROOT / "configs" / "epibench" / "conformance_suite_v1.yaml")

    assert result["status"] == "passed"
    assert all(case["passed"] for case in result["cases"])


def test_epibench_inter_reviewer_report_passes_for_demo_reviews() -> None:
    report = build_inter_reviewer_report(REPO_ROOT / "examples" / "epibench" / "inter_reviewer_reviews.yaml")

    assert report["status"] == "passed"
    assert report["dataset_count"] == 2
    assert all(dataset["claim_ceiling_agreement"] for dataset in report["datasets"])


def test_epibench_submission_readiness_gate_fails_preliminary_packages() -> None:
    report = assess_submission_readiness(
        [
            MSG_GATE_C_FROZEN / "result_bundle.yaml",
            MSG_PRELIMINARY / "result_bundle.yaml",
            SEIZEIT2_PRELIMINARY / "result_bundle.yaml",
        ],
        REPO_ROOT / "configs" / "epibench" / "submission_readiness_gate_v1.yaml",
    )

    assert report["status"] == "failed"
    assert report["submission_grade_count"] == 1
    assert report["operational_package_count"] == 0
    assert any("operational package" in blocker for blocker in report["blockers"])


def test_epibench_submission_readiness_gate_passes_with_chbmit_and_msg_gate_c() -> None:
    report = assess_submission_readiness(
        [
            CHBMIT_E2PI / "result_bundle.yaml",
            MSG_GATE_C_FROZEN / "result_bundle.yaml",
        ],
        REPO_ROOT / "configs" / "epibench" / "submission_readiness_gate_v1.yaml",
    )

    assert report["status"] == "passed"
    assert report["submission_grade_count"] == 2
    assert report["operational_package_count"] == 1


def test_epibench_builds_evidence_panels_that_expose_claim_gating(tmp_path: Path) -> None:
    result = build_evidence_panels(
        bundle_paths=[
            PILOT / "result_bundle.yaml",
            LEAKAGE / "result_bundle.yaml",
            CHBMIT_E2PI / "result_bundle.yaml",
            MSG_GATE_C_FROZEN / "result_bundle.yaml",
            FAR_EXPLOSION / "result_bundle.yaml",
        ],
        out_dir=tmp_path,
    )

    assert result["bundle_count"] == 5
    readme = (tmp_path / "README.md").read_text(encoding="utf-8")
    rank_comparison = (tmp_path / "rank_comparison.csv").read_text(encoding="utf-8")
    waterfall = (tmp_path / "claim_gate_waterfall.csv").read_text(encoding="utf-8")
    failure_matrix = (tmp_path / "failure_matrix.csv").read_text(encoding="utf-8")
    sensitivity = (tmp_path / "sensitivity_only_leaderboard.csv").read_text(encoding="utf-8")

    assert "high_or_mid_score_claim_limited_by_evidence_gate" in rank_comparison
    assert "claim_structure_valid_but_performance_poor" in rank_comparison
    assert "Bundle count: `5`" in readme
    assert "chbmit_always_negative_patient_independent" in rank_comparison
    assert "PATIENT_LEAKAGE" in failure_matrix
    assert "failure_status" in waterfall
    assert "ranking_mode" in sensitivity
    assert "far_explosion_high_sensitivity_demo" in sensitivity


def test_epibench_builds_coverage_audit_with_explicit_gaps(tmp_path: Path) -> None:
    result = build_coverage_audit(
        bundle_paths=[
            CHBMIT_E2PI / "result_bundle.yaml",
            MSG_GATE_C_FROZEN / "result_bundle.yaml",
            SEIZEIT2_PRELIMINARY / "result_bundle.yaml",
        ],
        out_dir=tmp_path,
    )

    assert result["bundle_count"] == 3
    assert result["dataset_count"] == 3
    readme = (tmp_path / "README.md").read_text(encoding="utf-8")
    dataset_matrix = (tmp_path / "dataset_evidence_matrix.csv").read_text(encoding="utf-8")
    gaps = (tmp_path / "coverage_gaps.csv").read_text(encoding="utf-8")

    assert "Covered tracks: `D, F`" in readme
    assert "chbmit_patient_independent_d" in dataset_matrix
    assert "independent_mts_dsi_review" in gaps
    assert "track,W,major" in gaps


def test_epibench_maps_szcore_style_event_metrics(tmp_path: Path) -> None:
    mapped_path = tmp_path / "mapped_result_bundle.yaml"

    bundle = map_szcore_metrics_to_result_bundle(
        REPO_ROOT / "examples" / "epibench" / "szcore_bridge_demo" / "szcore_event_metrics.yaml",
        PILOT / "result_bundle.yaml",
        mapped_path,
    )
    report = certify_result_bundle(mapped_path)

    assert bundle["metrics"]["event_sensitivity"] == 0.81
    assert bundle["metrics"]["false_alarms_per_24h"] == 1.25
    assert bundle["metrics"]["external_event_scoring_relationship"] == "MAP"
    assert report["final_claim"] == "E2-PI"


def test_epibench_imports_szcore_metrics_without_base_bundle(tmp_path: Path) -> None:
    imported_path = tmp_path / "imported_result_bundle.yaml"

    bundle = import_szcore_metrics_as_result_bundle(
        szcore_metrics_path=REPO_ROOT / "examples" / "epibench" / "szcore_bridge_demo" / "szcore_event_metrics.yaml",
        dataset_card_path=PILOT / "dataset_card.yaml",
        split_manifest_path=PILOT / "split_manifest.yaml",
        failure_trace_path=REPO_ROOT / "examples" / "epibench" / "szcore_bridge_demo" / "import_failure_trace.yaml",
        output_path=imported_path,
        run_id="szcore_import_demo",
        requested_claim="E2-PI",
        model_name="szcore_import_model",
        model_family="external_event_scorer",
        commit_sha="external-commit-sha",
        subscores={
            "performance": 0.76,
            "clinical_safety": 0.72,
            "robustness": 0.70,
            "stability": 0.68,
            "latency": 0.75,
        },
    )
    report = certify_result_bundle(imported_path)

    assert bundle["run_id"] == "szcore_import_demo"
    assert bundle["metrics"]["event_sensitivity"] == 0.81
    assert report["final_claim"] == "E2-PI"


def test_epibench_geometric_score_applies_floor_penalty() -> None:
    spec = load_spec()
    bundle = validate_artifact("result-bundle", PILOT / "result_bundle.yaml")
    bundle["score_inputs"]["subscores"]["robustness"] = 0.10

    score = compute_epi_score(bundle, spec)

    assert score["floor_penalty_applied"] is True
    assert score["epi_score"] < 60


def test_epibench_schema_rejects_missing_required_field(tmp_path: Path) -> None:
    invalid = tmp_path / "dataset_card.yaml"
    invalid.write_text("schema_version: epibench.dataset_card.v1\n", encoding="utf-8")

    with pytest.raises(SchemaValidationError, match="missing required property"):
        validate_artifact("dataset-card", invalid)
