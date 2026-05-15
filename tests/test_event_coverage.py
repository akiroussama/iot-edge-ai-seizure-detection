from __future__ import annotations

import pandas as pd
import pytest

from src.reports.event_coverage import event_cluster_summary, event_coverage_markdown, event_coverage_summary


def test_event_coverage_summary_counts_matched_unmatched_unknown() -> None:
    events = pd.DataFrame(
        {
            "patient_id": ["p1", "p1", "p1", "p2"],
            "recording_match_status": ["matched", "unmatched", "other", "matched"],
            "seizure_start": pd.to_datetime(
                [
                    "2026-01-01 00:00:00",
                    "2026-01-02 00:00:00",
                    "2026-01-03 00:00:00",
                    "2026-01-04 00:00:00",
                ]
            ),
        }
    )
    recordings = pd.DataFrame(
        {
            "patient_id": ["p1", "p1", "p2"],
            "recording_id": ["r1", "r2", "r3"],
            "recording_start": pd.to_datetime(
                ["2026-01-01 00:00:00", "2026-01-02 00:00:00", "2026-01-04 00:00:00"]
            ),
            "recording_end": pd.to_datetime(
                ["2026-01-01 01:00:00", "2026-01-02 02:00:00", "2026-01-04 03:00:00"]
            ),
        }
    )

    summary = event_coverage_summary(events, recordings)
    p1 = summary.loc[summary["patient_id"].eq("p1")].iloc[0]

    assert p1["events_total"] == 3
    assert p1["events_matched"] == 1
    assert p1["events_unmatched"] == 1
    assert p1["events_unknown"] == 1
    assert p1["recordings"] == 2
    assert p1["recording_hours"] == 3.0
    assert p1["manual_review_priority"] == "high"


def test_event_cluster_summary_flags_large_clusters() -> None:
    base = pd.Timestamp("2026-01-01 00:00:00")
    events = pd.DataFrame(
        {
            "patient_id": ["p1", "p1", "p1", "p1", "p1"],
            "seizure_start": [
                base,
                base + pd.Timedelta(minutes=60),
                base + pd.Timedelta(minutes=120),
                base + pd.Timedelta(minutes=180),
                base + pd.Timedelta(hours=12),
            ],
        }
    )

    summary = event_cluster_summary(events, cluster_gap_minutes=240)
    row = summary.iloc[0]

    assert row["clusters"] == 2
    assert row["clustered_events"] == 4
    assert row["max_cluster_size"] == 4
    assert row["manual_review_priority"] == "high"


def test_event_coverage_markdown_contains_disclaimer() -> None:
    coverage = pd.DataFrame({"patient_id": ["p1"], "events_total": [1]})
    clusters = pd.DataFrame({"patient_id": ["p1"], "clusters": [1]})

    text = event_coverage_markdown(coverage, clusters, title="Coverage")

    assert "# Coverage" in text
    assert "not a clinical result" in text
    assert "Manual review" in text


def test_event_coverage_requires_minimal_schema() -> None:
    with pytest.raises(ValueError, match="seizure_start"):
        event_coverage_summary(pd.DataFrame({"patient_id": ["p1"]}))
