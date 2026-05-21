from __future__ import annotations

import subprocess
import sys

import pandas as pd
import pytest

from src.reports.external_sota_reproduction import (
    ExternalPredictionColumns,
    ExternalSOTAReference,
    build_external_sota_manifest,
    standardize_external_predictions,
    validate_external_sota_reference,
)
from src.utils.io import read_table, write_table


def _external_predictions(base: pd.Timestamp) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "subject": ["p1", "p1", "p1", "p1"],
            "recording": ["r1", "r1", "r1", "r1"],
            "start": [
                base,
                base + pd.Timedelta(hours=1),
                base + pd.Timedelta(hours=2),
                base + pd.Timedelta(hours=8),
            ],
            "end": [
                base + pd.Timedelta(hours=1),
                base + pd.Timedelta(hours=2),
                base + pd.Timedelta(hours=3),
                base + pd.Timedelta(hours=9),
            ],
            "external_probability": [1.2, 0.4, 0.1, 0.8],
            "target": [True, True, False, False],
            "excluded": [False, False, False, False],
            "fold": ["test", "test", "test", "test"],
        }
    )


def _events(base: pd.Timestamp) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "patient_id": ["p1"],
            "recording_id": ["r1"],
            "seizure_start": [base + pd.Timedelta(hours=2, minutes=30)],
            "seizure_end": [base + pd.Timedelta(hours=2, minutes=31)],
        }
    )


def _reference() -> ExternalSOTAReference:
    return ExternalSOTAReference(
        source_name="Synthetic external cycle forecast",
        source_citation="Synthetic source for unit testing, not a paper claim.",
        source_url="https://example.org/synthetic-sota",
        source_doi=None,
        reproduction_family="cycle_ml_wearable_forecast",
        reproduction_status="adapter_smoke_test_not_sota_claim",
        mismatch_notes="Synthetic adapter check; no external superiority claim.",
    )


def test_standardize_external_predictions_maps_columns_and_thresholds_alarm() -> None:
    base = pd.Timestamp("2026-01-01 00:00:00")
    standardized = standardize_external_predictions(
        _external_predictions(base),
        columns=ExternalPredictionColumns(
            patient_col="subject",
            recording_col="recording",
            window_start_col="start",
            window_end_col="end",
            risk_col="external_probability",
            alarm_col=None,
            label_col="target",
            excluded_col="excluded",
            split_col="fold",
        ),
        alarm_threshold=0.5,
    )

    assert standardized["patient_id"].tolist() == ["p1", "p1", "p1", "p1"]
    assert standardized["risk_score"].tolist()[0] == 1.0
    assert standardized["external_sota_risk_was_clipped"].tolist()[0] is True
    assert standardized["alarm"].tolist() == [True, False, False, True]
    assert standardized["split"].tolist() == ["test", "test", "test", "test"]


def test_external_reference_requires_real_source_and_mismatch_notes() -> None:
    with pytest.raises(ValueError, match="source_url or source_doi"):
        validate_external_sota_reference(
            ExternalSOTAReference(
                source_name="bad",
                source_citation="bad",
                source_url=None,
                source_doi=None,
                reproduction_family="bad",
                reproduction_status="external_reported_not_recomputed",
                mismatch_notes="not recomputed",
            )
        )


def test_build_external_sota_manifest_keeps_non_citable_status_visible() -> None:
    base = pd.Timestamp("2026-01-01 00:00:00")
    standardized = standardize_external_predictions(
        _external_predictions(base),
        columns=ExternalPredictionColumns(
            patient_col="subject",
            recording_col="recording",
            window_start_col="start",
            window_end_col="end",
            risk_col="external_probability",
            alarm_col=None,
            label_col="target",
            excluded_col="excluded",
            split_col="fold",
        ),
        alarm_threshold=0.5,
    )
    manifest = build_external_sota_manifest(
        reference=_reference(),
        standardized_predictions=standardized,
        leaderboard_row={
            "result_id": "synthetic_external",
            "result_status": "external_sota_context",
            "citation_status": "not_citable_pre_gate_c",
            "dataset": "synthetic",
            "task_type": "forecasting",
            "model_name": "synthetic_external",
            "split_name": "test",
            "horizon_name": "SPH30_SOP120",
            "sensitivity": 1.0,
            "false_alarm_rate_per_day": 0.0,
            "time_in_warning": 0.5,
            "brier_score": 0.1,
            "brier_skill_score": None,
            "auroc": 1.0,
            "auprc": 1.0,
        },
    )

    row = manifest.iloc[0]
    assert row["leaderboard_citation_status"] == "not_citable_pre_gate_c"
    assert row["risk_clipped_rows"] == 1
    assert row["sota_claim_status"] == "not_a_sota_claim_until_gate_c_and_faithful_reproduction"


def test_external_sota_reproduction_cli_writes_leaderboard_and_manifest(tmp_path) -> None:
    base = pd.Timestamp("2026-01-01 00:00:00")
    predictions_path = tmp_path / "external_predictions.csv"
    events_path = tmp_path / "events.csv"
    out_dir = tmp_path / "sota"
    write_table(_external_predictions(base), predictions_path)
    write_table(_events(base), events_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_external_sota_reproduction.py",
            "--predictions",
            str(predictions_path),
            "--events",
            str(events_path),
            "--out-dir",
            str(out_dir),
            "--result-id",
            "synthetic_external_sota_adapter",
            "--dataset",
            "synthetic",
            "--model-name",
            "synthetic_external_cycle_ml",
            "--source-name",
            "Synthetic external cycle forecast",
            "--source-citation",
            "Synthetic source for unit testing, not a paper claim.",
            "--source-url",
            "https://example.org/synthetic-sota",
            "--reproduction-family",
            "cycle_ml_wearable_forecast",
            "--reproduction-status",
            "adapter_smoke_test_not_sota_claim",
            "--mismatch-notes",
            "Synthetic adapter check; no external superiority claim.",
            "--patient-col",
            "subject",
            "--recording-col",
            "recording",
            "--window-start-col",
            "start",
            "--window-end-col",
            "end",
            "--risk-col",
            "external_probability",
            "--no-alarm-col",
            "--alarm-threshold",
            "0.5",
            "--label-col",
            "target",
            "--excluded-col",
            "excluded",
            "--split-col",
            "fold",
            "--task-type",
            "forecasting",
            "--split-policy",
            "synthetic",
            "--split-name",
            "test",
            "--prediction-filter",
            "split=test",
            "--restrict-events-to-prediction-coverage",
            "--sph-minutes",
            "30",
            "--sop-minutes",
            "120",
            "--window-seconds",
            "3600",
            "--stride-seconds",
            "3600",
            "--label-audit-status",
            "not_applicable",
            "--gate-b-status",
            "not_applicable_external",
            "--gate-c-status",
            "not_started",
            "--repo-commit",
            "unit-test",
            "--evidence-uri",
            "tests/test_external_sota_reproduction.py",
        ],
        check=True,
        text=True,
        capture_output=True,
    )

    assert '"result_id": "synthetic_external_sota_adapter"' in result.stdout
    leaderboard = read_table(out_dir / "external_sota_leaderboard_row.csv")
    manifest = read_table(out_dir / "external_sota_manifest.csv")
    standardized = read_table(out_dir / "external_sota_predictions.csv")
    assert leaderboard.loc[0, "result_status"] == "external_sota_context"
    assert leaderboard.loc[0, "citation_status"] == "not_citable_pre_gate_c"
    assert manifest.loc[0, "reproduction_status"] == "adapter_smoke_test_not_sota_claim"
    assert standardized["risk_score"].max() == 1.0
    assert "not citable" in (out_dir / "external_sota_report.md").read_text(encoding="utf-8")
