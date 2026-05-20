from __future__ import annotations

import pandas as pd

from src.reports.audit_packet import build_label_audit_packet


def test_build_label_audit_packet_contains_event_timeline() -> None:
    audit = pd.DataFrame(
        {
            "event_index": [0, 0],
            "patient_id": ["p1", "p1"],
            "recording_id": ["r1", "r1"],
            "seizure_start": [pd.Timestamp("2026-01-01 01:00:00")] * 2,
            "seizure_end": [pd.Timestamp("2026-01-01 01:01:00")] * 2,
            "window_end": [pd.Timestamp("2026-01-01 00:30:00"), pd.Timestamp("2026-01-01 01:00:30")],
            "minutes_to_seizure": [30.0, -0.5],
            "forecast_label": [True, False],
            "is_ictal": [False, True],
            "is_postictal": [False, False],
            "is_excluded": [False, True],
            "audit_state": ["forecast_positive", "ictal_excluded"],
        }
    )

    packet = build_label_audit_packet(audit, max_events=1, title="Mock Audit")

    assert "# Mock Audit" in packet
    assert "Event 0" in packet
    assert "forecast_positive" in packet
    assert "ictal_excluded" in packet
