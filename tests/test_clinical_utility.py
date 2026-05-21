from __future__ import annotations

import subprocess
import sys

import pandas as pd

from src.reports.clinical_utility import (
    ClinicalUtilityAssumptions,
    ClinicalUtilityConstraints,
    apply_refractory_alarm_policy,
    clinical_utility_markdown,
    clinical_utility_table,
)
from src.utils.io import read_table, write_table


def _sweep_table() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "threshold": [0.2, 0.5, 0.8],
            "sensitivity": [0.95, 0.80, 0.40],
            "far_per_day": [4.0, 0.6, 0.1],
            "time_in_warning": [0.50, 0.12, 0.03],
            "median_lead_time_seconds": [600.0, 1200.0, 1800.0],
            "brier_skill_score": [0.10, 0.20, 0.05],
        }
    )


def test_clinical_utility_selects_best_policy_under_costs() -> None:
    utility = clinical_utility_table(
        _sweep_table(),
        assumptions=ClinicalUtilityAssumptions(
            false_alarm_cost_per_day=0.25,
            warning_time_cost=0.5,
            brier_skill_score_weight=0.2,
        ),
        constraints=ClinicalUtilityConstraints(max_far_per_day=1.0, max_time_in_warning=0.2),
    )

    selected = utility.loc[utility["selected_under_assumptions"]].iloc[0]
    assert selected["threshold"] == 0.5
    assert selected["policy_status"] == "eligible"
    assert utility.loc[utility["threshold"].eq(0.2), "policy_status"].iloc[0] == "ineligible"


def test_clinical_utility_markdown_is_decision_support_not_recommendation() -> None:
    assumptions = ClinicalUtilityAssumptions()
    constraints = ClinicalUtilityConstraints(max_far_per_day=1.0)
    utility = clinical_utility_table(_sweep_table(), assumptions=assumptions, constraints=constraints)

    text = clinical_utility_markdown(
        utility,
        assumptions=assumptions,
        constraints=constraints,
        citation_status="synthetic_not_citable",
        gate_c_status="not_started",
    )

    assert "decision-support analysis" in text
    assert "not citable" in text
    assert "selected_under_assumptions" in text


def test_refractory_alarm_policy_suppresses_close_follow_up_alarms() -> None:
    base = pd.Timestamp("2026-01-01 00:00:00")
    predictions = pd.DataFrame(
        {
            "patient_id": ["p1", "p1", "p1", "p1"],
            "recording_id": ["r1", "r1", "r1", "r1"],
            "window_start": [
                base,
                base + pd.Timedelta(minutes=10),
                base + pd.Timedelta(minutes=70),
                base + pd.Timedelta(minutes=80),
            ],
            "window_end": [
                base + pd.Timedelta(minutes=5),
                base + pd.Timedelta(minutes=15),
                base + pd.Timedelta(minutes=75),
                base + pd.Timedelta(minutes=85),
            ],
            "alarm": [True, True, True, False],
        }
    )

    out = apply_refractory_alarm_policy(predictions, refractory_minutes=30)

    assert out["alarm"].tolist() == [True, False, True, False]
    assert out["alarm_refractory_suppressed"].tolist() == [False, True, False, False]


def test_clinical_utility_cli_writes_outputs(tmp_path) -> None:
    sweep_path = tmp_path / "sweep.csv"
    out_csv = tmp_path / "utility.csv"
    out_md = tmp_path / "utility.md"
    write_table(_sweep_table(), sweep_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/make_clinical_utility_report.py",
            "--sweep",
            str(sweep_path),
            "--out-csv",
            str(out_csv),
            "--out-md",
            str(out_md),
            "--max-far-per-day",
            "1.0",
            "--max-time-in-warning",
            "0.2",
            "--false-alarm-cost-per-day",
            "0.25",
            "--warning-time-cost",
            "0.5",
            "--result-status",
            "synthetic_smoke_test_not_citable",
            "--citation-status",
            "synthetic_not_citable",
        ],
        check=True,
        text=True,
        capture_output=True,
    )

    utility = read_table(out_csv)
    assert '"selected_rows": 1' in result.stdout
    assert utility.loc[utility["selected_under_assumptions"], "threshold"].iloc[0] == 0.5
    assert "not citable" in out_md.read_text(encoding="utf-8")


def test_clinical_utility_cli_requires_gate_c_for_citable(tmp_path) -> None:
    sweep_path = tmp_path / "sweep.csv"
    write_table(_sweep_table(), sweep_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/make_clinical_utility_report.py",
            "--sweep",
            str(sweep_path),
            "--out-csv",
            str(tmp_path / "utility.csv"),
            "--out-md",
            str(tmp_path / "utility.md"),
            "--citation-status",
            "citable_after_gate_c",
            "--gate-c-status",
            "not_started",
        ],
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode != 0
    assert "gate-c-status passed" in result.stderr
