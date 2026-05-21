from __future__ import annotations

import csv
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO_ROOT / "schemas" / "leaderboard_entry.schema.json"
COLUMNS_PATH = REPO_ROOT / "schemas" / "leaderboard_columns.csv"
TEMPLATE_PATH = REPO_ROOT / "schemas" / "leaderboard_template.csv"


def _schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _column_rows() -> list[dict[str, str]]:
    with COLUMNS_PATH.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _template_header() -> list[str]:
    with TEMPLATE_PATH.open(newline="", encoding="utf-8") as handle:
        return next(csv.reader(handle))


def test_leaderboard_schema_required_columns_match_csv_template() -> None:
    schema = _schema()
    required = schema["required"]

    assert required == _template_header()


def test_leaderboard_column_dictionary_matches_schema_properties() -> None:
    schema = _schema()
    columns = [row["column"] for row in _column_rows()]

    assert columns == schema["required"]
    assert set(columns) == set(schema["properties"])
    assert all(row["required"] == "yes" for row in _column_rows())


def test_leaderboard_schema_contains_gate_c_safe_statuses() -> None:
    schema = _schema()

    assert "pre_gate_c_exploratory_not_citable" in schema["properties"]["result_status"]["enum"]
    assert "not_citable_pre_gate_c" in schema["properties"]["citation_status"]["enum"]
    assert "passed" in schema["properties"]["gate_c_status"]["enum"]
    assert "not_frozen" in schema["properties"]["split_frozen_status"]["enum"]


def test_leaderboard_schema_covers_task2_required_dimensions() -> None:
    required_dimensions = {
        "dataset",
        "split_name",
        "split_policy",
        "horizon_name",
        "sph_minutes",
        "sop_minutes",
        "event_unit",
        "events_used_for_metrics",
        "sensitivity",
        "false_alarm_rate_per_day",
        "time_in_warning",
        "observable_prediction_rows",
        "deficient_prediction_rows",
        "abstained_prediction_rows",
        "deficiency_time_minutes",
        "mean_observable_score",
        "brier_score",
        "brier_skill_score",
        "leakage_status",
        "edge_target",
        "ram_kb",
        "latency_ms",
        "energy_mj_per_inference",
    }

    schema = _schema()

    assert required_dimensions.issubset(schema["required"])
