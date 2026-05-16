from __future__ import annotations

import pandas as pd

from scripts.make_dataset_report import (
    _baseline_table,
    _event_denominator_table,
    _event_annotation_table,
    _events_coverable_by_predictions,
    _metric_event_units,
    _prediction_metadata_table,
    _requires_bias_acknowledgement,
)


def test_events_coverable_by_predictions_uses_selected_horizon() -> None:
    base = pd.Timestamp("2026-01-01 00:00:00")
    preds = pd.DataFrame(
        {
            "patient_id": ["p1", "p1"],
            "recording_id": ["r1", "r1"],
            "window_start": [base, base + pd.Timedelta(hours=10)],
            "window_end": [base + pd.Timedelta(hours=1), base + pd.Timedelta(hours=11)],
            "risk_score": [0.1, 0.9],
            "alarm": [False, True],
            "is_excluded": [False, False],
        }
    )
    events = pd.DataFrame(
        {
            "patient_id": ["p1", "p1"],
            "recording_id": ["r1", "r1"],
            "seizure_start": [base + pd.Timedelta(hours=3), base + pd.Timedelta(days=2)],
            "seizure_end": [base + pd.Timedelta(hours=3, minutes=1), base + pd.Timedelta(days=2, minutes=1)],
        }
    )

    covered = _events_coverable_by_predictions(preds, events, sph_minutes=60, sop_minutes=180)

    assert len(covered) == 1
    assert covered.loc[0, "seizure_start"] == base + pd.Timedelta(hours=3)


def test_prediction_metadata_table_reports_fit_and_threshold_scope() -> None:
    predictions = pd.DataFrame(
        {
            "split": ["test", "test"],
            "alarm": [True, False],
            "is_excluded": [False, True],
            "score_fit_split": ["train", "train"],
            "threshold_source_split": ["val", "val"],
            "alarm_threshold": [0.4, 0.4],
        }
    )

    metadata = _prediction_metadata_table(predictions)

    assert metadata.loc[0, "prediction_rows"] == 2
    assert metadata.loc[0, "valid_prediction_rows"] == 1
    assert metadata.loc[0, "alarms"] == 1
    assert metadata.loc[0, "score_fit_split"] == "train"
    assert metadata.loc[0, "threshold_source_split"] == "val"


def test_event_denominator_table_makes_matched_subset_explicit() -> None:
    events_all = pd.DataFrame({"event_id": [1, 2, 3]})
    events_after_filter = pd.DataFrame({"event_id": [1, 2]})
    events_after_coverage = pd.DataFrame({"event_id": [1]})

    denominator = _event_denominator_table(
        events_all,
        events_after_filter,
        events_after_coverage,
        events_after_coverage,
        event_filter="recording_match_status=matched",
        prediction_filter="split=test",
        restricted_to_prediction_coverage=True,
        event_unit="seizure",
        cluster_gap_minutes=240,
    )

    assert _requires_bias_acknowledgement("recording_match_status=matched")
    assert denominator.loc[0, "events_source_total"] == 3
    assert denominator.loc[0, "events_after_filter"] == 2
    assert denominator.loc[0, "events_used_for_metrics"] == 1
    assert denominator.loc[0, "metric_units_used_for_metrics"] == 1
    assert "wearable recording intervals" in denominator.loc[0, "denominator_warning"]
    assert denominator.loc[0, "cluster_policy"] == "seizure_level_metrics_clusters_not_collapsed"


def test_metric_event_units_can_collapse_clusters_for_reports() -> None:
    base = pd.Timestamp("2026-01-01 00:00:00")
    events = pd.DataFrame(
        {
            "patient_id": ["p1", "p1", "p1"],
            "recording_id": ["r1", "r1", "r1"],
            "seizure_start": [
                base,
                base + pd.Timedelta(minutes=60),
                base + pd.Timedelta(hours=8),
            ],
            "seizure_end": [
                base + pd.Timedelta(minutes=1),
                base + pd.Timedelta(minutes=61),
                base + pd.Timedelta(hours=8, minutes=1),
            ],
        }
    )

    units = _metric_event_units(events, event_unit="cluster", cluster_gap_minutes=240)

    assert len(units) == 2
    assert units["event_unit"].tolist() == ["cluster", "cluster"]
    assert units["cluster_size"].tolist() == [2, 1]


def test_event_annotation_table_reports_imputed_seizure_ends() -> None:
    events = pd.DataFrame(
        {
            "seizure_end_imputed": [True, False, True],
            "imputed_duration_seconds": [60.0, float("nan"), 60.0],
        }
    )

    annotation = _event_annotation_table(events)

    assert annotation.loc[0, "seizure_end_imputed_events"] == 2
    assert annotation.loc[0, "seizure_end_imputed_fraction"] == 2 / 3
    assert annotation.loc[0, "imputed_duration_seconds_values"] == "60.0"


def test_baseline_table_renders_sensitivity_with_inline_denominator() -> None:
    """Phase R audit C4: the baseline table's sensitivity cell must carry its
    event denominator inline, so a reader cannot copy a bare rate and lose the
    event count. Fails if sensitivity is rendered as a bare number.
    """
    base = pd.Timestamp("2026-01-01 00:00:00")
    predictions = pd.DataFrame(
        {
            "patient_id": ["p1"] * 3,
            "recording_id": ["r1"] * 3,
            "window_start": [base + pd.Timedelta(minutes=i) for i in range(3)],
            "window_end": [base + pd.Timedelta(minutes=i + 1) for i in range(3)],
            "risk_score": [0.9, 0.2, 0.1],
            "alarm": [True, False, False],
            "forecast_label": [True, False, False],
            "is_excluded": [False, False, False],
        }
    )
    events = pd.DataFrame(
        {
            "patient_id": ["p1"],
            "recording_id": ["r1"],
            "seizure_start": [base + pd.Timedelta(minutes=8)],
            "seizure_end": [base + pd.Timedelta(minutes=9)],
        }
    )

    table = _baseline_table(predictions, events, 5, 30, "rule_x")
    sensitivity_cell = str(table.loc[0, "sensitivity"])

    assert "events)" in sensitivity_cell
    assert "/" in sensitivity_cell


def test_any_event_filter_requires_bias_acknowledgement() -> None:
    """Phase R audit C4: any event filter selects a non-random subset and must
    require acknowledgement, not only recording_match_status=matched.

    Fails if the guard exact-matches a single filter string.
    """
    assert _requires_bias_acknowledgement("recording_match_status=matched")
    assert _requires_bias_acknowledgement("patient_id=p1")
    assert _requires_bias_acknowledgement("seizure_type=focal")
    assert not _requires_bias_acknowledgement(None)
