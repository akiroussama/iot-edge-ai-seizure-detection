from __future__ import annotations

import json
import subprocess
import sys

import pandas as pd
import pytest

from src.reports.longitudinal_deep_dive import (
    LongitudinalDeepDiveConfig,
    build_longitudinal_deep_dive_report,
    patient_selection_table,
)
from src.utils.io import read_table, write_table


def _predictions() -> pd.DataFrame:
    base = pd.Timestamp("2026-01-01 00:00:00")
    rows = []
    for patient, count in [("p_short", 8), ("p_long", 24)]:
        for idx in range(count):
            start = base + pd.Timedelta(hours=idx)
            risk = (idx % 12) / 11
            rows.append(
                {
                    "patient_id": patient,
                    "recording_id": f"{patient}_r1",
                    "window_start": start,
                    "window_end": start + pd.Timedelta(hours=1),
                    "risk_score": risk,
                    "alarm": risk >= 0.6,
                    "forecast_label": idx in {4, 12, 20},
                    "is_excluded": idx == 2 and patient == "p_short",
                    "failure_category": "missed_forecast_positive"
                    if idx in {4, 12, 20} and risk < 0.6
                    else "true_negative",
                    "is_observable": idx % 5 != 0,
                }
            )
    return pd.DataFrame(rows)


def test_patient_selection_prefers_long_informative_patient() -> None:
    prepared = _predictions()
    prepared["window_start"] = pd.to_datetime(prepared["window_start"])

    selection = patient_selection_table(prepared, config=LongitudinalDeepDiveConfig())

    assert selection.loc[0, "patient_id"] == "p_long"
    assert selection.loc[0, "positive_rows"] == 3
    assert selection.loc[0, "duration_hours"] > selection.loc[1, "duration_hours"]


def test_longitudinal_report_builds_timeline_segments_and_events() -> None:
    report = build_longitudinal_deep_dive_report(
        _predictions(),
        config=LongitudinalDeepDiveConfig(segments=4, event_neighborhood_rows=2),
        report_name="toy_n1",
    )

    assert report.metadata["selected_patient_id"] == "p_long"
    assert len(report.timeline) == 24
    assert len(report.segment_summary) == 4
    assert set(report.event_neighborhoods["event_number"]) == {1, 2, 3}
    assert "risk_delta_from_previous" in report.timeline.columns
    assert report.manifest.loc[0, "analysis_status"] == "descriptive_single_patient_not_generalizable"


def test_longitudinal_report_accepts_requested_patient() -> None:
    report = build_longitudinal_deep_dive_report(
        _predictions(),
        config=LongitudinalDeepDiveConfig(patient_id="p_short", segments=2),
    )

    assert report.metadata["selected_patient_id"] == "p_short"
    assert len(report.timeline) == 8


def test_longitudinal_report_rejects_missing_patient() -> None:
    with pytest.raises(ValueError, match="not found"):
        build_longitudinal_deep_dive_report(
            _predictions(),
            config=LongitudinalDeepDiveConfig(patient_id="missing"),
        )


def test_make_longitudinal_deep_dive_cli_writes_outputs(tmp_path) -> None:
    predictions_path = tmp_path / "predictions.csv"
    out_dir = tmp_path / "n1"
    write_table(_predictions(), predictions_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/make_longitudinal_deep_dive.py",
            "--predictions",
            str(predictions_path),
            "--out-dir",
            str(out_dir),
            "--report-name",
            "toy_n1",
            "--segments",
            "4",
            "--event-neighborhood-rows",
            "2",
        ],
        check=True,
        text=True,
        capture_output=True,
    )

    assert '"report_name": "toy_n1"' in result.stdout
    selection = read_table(out_dir / "n1_patient_selection.csv")
    timeline = read_table(out_dir / "n1_timeline.csv")
    segments = read_table(out_dir / "n1_segment_summary.csv")
    neighborhoods = read_table(out_dir / "n1_event_neighborhoods.csv")
    manifest = read_table(out_dir / "n1_manifest.csv")
    payload = json.loads((out_dir / "n1_report.json").read_text(encoding="utf-8"))
    assert selection.loc[0, "patient_id"] == "p_long"
    assert len(timeline) == 24
    assert len(segments) == 4
    assert set(neighborhoods["event_number"]) == {1, 2, 3}
    assert manifest.loc[0, "report_name"] == "toy_n1"
    assert payload["metadata"]["analysis_status"] == "descriptive_single_patient_not_generalizable"
    assert "not citable" in (out_dir / "n1_report.md").read_text(encoding="utf-8")
