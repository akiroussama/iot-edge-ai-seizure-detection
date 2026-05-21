from __future__ import annotations

import subprocess
import sys

import pandas as pd

from src.active.audit_selection import (
    build_audit_target_table,
    select_audit_targets,
)
from src.utils.io import read_table, write_table


def _synthetic_audit_inputs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rows = []
    prediction_rows = []
    reference_rows = []
    starts = [
        pd.Timestamp("2026-01-01 01:00:00"),
        pd.Timestamp("2026-01-02 01:00:00"),
        pd.Timestamp("2026-01-03 01:00:00"),
    ]
    patients = ["p1", "p2", "p3"]
    risks = {
        0: [0.05, 0.05, 0.05, 0.05],
        1: [0.49, 0.52, 0.50, 0.51],
        2: [0.90, 0.92, 0.91, 0.93],
    }
    reference_risks = {
        0: [0.05, 0.05, 0.05, 0.05],
        1: [0.04, 0.05, 0.04, 0.05],
        2: [0.85, 0.86, 0.85, 0.86],
    }
    for event_index, seizure_start in enumerate(starts):
        for offset, minutes_to_seizure in enumerate([45, 20, 5, -5]):
            window_end = seizure_start - pd.Timedelta(minutes=minutes_to_seizure)
            window_start = window_end - pd.Timedelta(minutes=5)
            row = {
                "event_index": event_index,
                "patient_id": patients[event_index],
                "recording_id": f"rec_{event_index}",
                "seizure_start": seizure_start,
                "seizure_end": seizure_start + pd.Timedelta(minutes=1),
                "window_start": window_start,
                "window_end": window_end,
                "minutes_to_seizure": minutes_to_seizure,
                "forecast_label": event_index == 1 and offset in {1, 2},
                "is_ictal": minutes_to_seizure < 0,
                "is_postictal": event_index == 1 and minutes_to_seizure < 0,
                "is_right_censored": event_index == 1 and offset == 2,
                "is_excluded": minutes_to_seizure < 0 and event_index != 1,
                "injected_label_issue": event_index == 1,
            }
            rows.append(row)
            prediction_rows.append(
                {
                    "patient_id": row["patient_id"],
                    "recording_id": row["recording_id"],
                    "window_start": window_start,
                    "window_end": window_end,
                    "forecast_label": row["forecast_label"],
                    "is_excluded": row["is_excluded"],
                    "risk_score": risks[event_index][offset],
                    "alarm": event_index == 1 and offset in {1, 2},
                }
            )
            reference_rows.append(
                {
                    "patient_id": row["patient_id"],
                    "recording_id": row["recording_id"],
                    "window_start": window_start,
                    "window_end": window_end,
                    "forecast_label": row["forecast_label"],
                    "is_excluded": row["is_excluded"],
                    "risk_score": reference_risks[event_index][offset],
                    "alarm": False,
                }
            )
    return pd.DataFrame(rows), pd.DataFrame(prediction_rows), pd.DataFrame(reference_rows)


def test_active_selection_catches_injected_label_issue_better_than_random() -> None:
    audit, predictions, reference = _synthetic_audit_inputs()

    candidates = build_audit_target_table(
        audit,
        predictions_df=predictions,
        reference_predictions={"split_prior": reference},
    )
    active = select_audit_targets(candidates, budget=1, selection_strategy="top_score")
    random = select_audit_targets(candidates, budget=1, selection_strategy="random", seed=0)

    assert active.loc[0, "event_index"] == 1
    assert bool(active.loc[0, "active_selection_label_issue_flag"]) is True
    assert bool(random.loc[0, "active_selection_label_issue_flag"]) is False
    assert active.loc[0, "active_audit_score"] > random.loc[0, "active_audit_score"]


def test_patient_spread_selection_limits_single_patient_dominance() -> None:
    targets = pd.DataFrame(
        {
            "event_index": [0, 1, 2, 3],
            "patient_id": ["p1", "p1", "p1", "p2"],
            "recording_id": ["a", "b", "c", "d"],
            "seizure_start": pd.date_range("2026-01-01", periods=4, freq="h"),
            "active_audit_score": [0.99, 0.98, 0.97, 0.50],
        }
    )

    selected = select_audit_targets(targets, budget=2, selection_strategy="patient_spread")

    assert selected["patient_id"].tolist() == ["p1", "p2"]
    assert selected["audit_rank"].tolist() == [1, 2]


def test_prediction_alignment_missing_rows_raises() -> None:
    audit, predictions, _ = _synthetic_audit_inputs()

    incomplete = predictions.iloc[:-1].copy()

    try:
        build_audit_target_table(audit, predictions_df=incomplete)
    except ValueError as exc:
        assert "missing prediction rows" in str(exc)
    else:
        raise AssertionError("expected missing prediction rows to fail closed")


def test_duplicate_prediction_alignment_keys_raise() -> None:
    audit, predictions, _ = _synthetic_audit_inputs()
    duplicated = pd.concat([predictions, predictions.iloc[[0]]], ignore_index=True)

    try:
        build_audit_target_table(audit, predictions_df=duplicated)
    except ValueError as exc:
        assert "duplicate alignment keys" in str(exc)
    else:
        raise AssertionError("expected duplicate prediction keys to fail closed")


def test_select_audit_targets_cli_writes_selected_and_candidates(tmp_path) -> None:
    audit, predictions, reference = _synthetic_audit_inputs()
    audit_path = tmp_path / "audit.csv"
    predictions_path = tmp_path / "predictions.csv"
    reference_path = tmp_path / "reference.csv"
    out_path = tmp_path / "selected.csv"
    candidates_path = tmp_path / "candidates.csv"
    write_table(audit, audit_path)
    write_table(predictions, predictions_path)
    write_table(reference, reference_path)

    subprocess.run(
        [
            sys.executable,
            "scripts/select_audit_targets.py",
            "--audit",
            str(audit_path),
            "--predictions",
            str(predictions_path),
            "--reference-predictions",
            f"split_prior={reference_path}",
            "--budget",
            "2",
            "--selection-strategy",
            "top_score",
            "--out",
            str(out_path),
            "--candidates-out",
            str(candidates_path),
        ],
        check=True,
    )

    selected = read_table(out_path)
    candidates = read_table(candidates_path)
    assert selected["audit_rank"].tolist() == [1, 2]
    assert selected.loc[0, "event_index"] == 1
    assert "selection_reason" in selected.columns
    assert len(candidates) == 3
