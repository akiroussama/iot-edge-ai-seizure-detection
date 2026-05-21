from __future__ import annotations

import json
import subprocess
import sys

import pandas as pd
import pytest

from src.datasets.seizeit2_loader import make_synthetic_seizeit2_tables
from src.labeling.sph_sop import label_forecast_windows
from src.reports.clinical_audit_workbench import (
    build_clinical_audit_workbench,
    build_timeline_geometry,
    clinical_audit_workbench_html,
)
from src.reports.label_audit import (
    REVIEW_DECISION_COLUMNS,
    build_label_audit_table,
    validate_label_audit_review_sheet,
)
from src.utils.io import read_table, write_table


def _audit_table() -> pd.DataFrame:
    _, windows, events = make_synthetic_seizeit2_tables()
    labels = label_forecast_windows(
        windows,
        events,
        5,
        30,
        postictal_exclusion_minutes=5,
        require_recording_end=False,
    )
    audit = build_label_audit_table(labels, events, minutes_before=40, minutes_after=10)
    audit["risk_score"] = [0.8 if flag else 0.2 for flag in audit["forecast_label"]]
    audit["alarm"] = audit["risk_score"].ge(0.5)
    return audit


def test_timeline_geometry_places_sph_sop_zone_and_windows() -> None:
    audit = _audit_table()

    geometry = build_timeline_geometry(
        audit,
        sph_minutes=5,
        sop_minutes=30,
        postictal_exclusion_minutes=5,
    )

    zone = geometry.loc[geometry["layer"].eq("sph_sop_positive_zone")].iloc[0]
    assert zone["start_minutes"] == pytest.approx(-35.0)
    assert zone["end_minutes"] == pytest.approx(-5.0)
    assert geometry["x_pct"].between(0, 100).all()
    assert geometry["width_pct"].gt(0).all()
    assert {"interval", "window"} == set(geometry["element_type"])


def test_workbench_html_contains_review_sheet_without_autofilling_decisions() -> None:
    report = build_clinical_audit_workbench(
        _audit_table(),
        sph_minutes=5,
        sop_minutes=30,
        postictal_exclusion_minutes=5,
        max_events=1,
        result_status="synthetic_smoke_test_not_citable",
        citation_status="synthetic_not_citable",
    )

    html = clinical_audit_workbench_html(report, title="Mock Clinical Audit")

    assert "Mock Clinical Audit" in html
    assert "source_onset_verified" in html
    assert "not citable" in html
    assert report.review_sheet.loc[0, "decision"] == ""


def test_uncertain_review_decision_is_valid_but_blocks_gate() -> None:
    report = build_clinical_audit_workbench(
        _audit_table(),
        sph_minutes=5,
        sop_minutes=30,
        max_events=1,
    )
    sheet = report.review_sheet.copy()
    for column in REVIEW_DECISION_COLUMNS:
        sheet[column] = "PASS"
    sheet.loc[0, "decision"] = "UNCERTAIN"

    validation = validate_label_audit_review_sheet(sheet, min_events=1)

    assert bool(validation.loc[validation["check"].eq("decision_valid_values"), "passed"].iloc[0])
    assert not bool(validation.loc[validation["check"].eq("decision_all_pass"), "passed"].iloc[0])


def test_citable_workbench_requires_gate_c_passed() -> None:
    with pytest.raises(ValueError, match="gate_c_status='passed'"):
        build_clinical_audit_workbench(
            _audit_table(),
            sph_minutes=5,
            sop_minutes=30,
            citation_status="citable_after_gate_c",
            gate_c_status="not_started",
        )


def test_build_clinical_audit_workbench_cli_writes_outputs(tmp_path) -> None:
    audit_path = tmp_path / "audit.csv"
    out_dir = tmp_path / "workbench"
    write_table(_audit_table(), audit_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/build_clinical_audit_workbench.py",
            "--audit",
            str(audit_path),
            "--out-dir",
            str(out_dir),
            "--title",
            "Synthetic Audit Workbench",
            "--sph-minutes",
            "5",
            "--sop-minutes",
            "30",
            "--postictal-exclusion-minutes",
            "5",
            "--max-events",
            "1",
            "--result-status",
            "synthetic_smoke_test_not_citable",
            "--citation-status",
            "synthetic_not_citable",
        ],
        check=True,
        text=True,
        capture_output=True,
    )

    assert '"events_in_workbench": 1' in result.stdout
    geometry = read_table(out_dir / "timeline_geometry.csv")
    review = read_table(out_dir / "review_sheet.csv")
    summary = read_table(out_dir / "audit_workbench_summary.csv")
    payload = json.loads((out_dir / "audit_workbench_report.json").read_text(encoding="utf-8"))
    html = (out_dir / "audit_workbench.html").read_text(encoding="utf-8")
    assert not geometry.empty
    assert review.loc[0, "decision"] != "PASS"
    assert summary.loc[0, "events_in_workbench"] == 1
    assert payload["metadata"]["citation_status"] == "synthetic_not_citable"
    assert "Synthetic Audit Workbench" in html
    assert "not citable" in (out_dir / "audit_workbench.md").read_text(encoding="utf-8")
