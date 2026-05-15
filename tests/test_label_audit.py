from __future__ import annotations

import pandas as pd

from src.datasets.seizeit2_loader import make_synthetic_seizeit2_tables
from src.labeling.sph_sop import label_forecast_windows
from src.reports.label_audit import build_label_audit_review_sheet, build_label_audit_table


def test_build_label_audit_table_contains_seizure_context_states() -> None:
    _, windows, events = make_synthetic_seizeit2_tables()
    labels = label_forecast_windows(windows, events, 5, 30, postictal_exclusion_minutes=5)

    audit = build_label_audit_table(labels, events, minutes_before=40, minutes_after=10)

    assert not audit.empty
    assert {"forecast_positive", "ictal_excluded", "postictal_excluded"}.issubset(
        set(audit["audit_state"])
    )
    assert "is_right_censored" in audit.columns
    assert audit["minutes_to_seizure"].min() < 0
    assert audit["minutes_to_seizure"].max() > 0


def test_build_label_audit_review_sheet_creates_one_row_per_event() -> None:
    _, windows, events = make_synthetic_seizeit2_tables()
    labels = label_forecast_windows(windows, events, 5, 30, postictal_exclusion_minutes=5)
    audit = build_label_audit_table(labels, events, minutes_before=40, minutes_after=10)

    sheet = build_label_audit_review_sheet(audit, max_events=1)

    assert len(sheet) == 1
    assert sheet.loc[0, "timeline_rows"] > 0
    assert sheet.loc[0, "forecast_positive_rows"] > 0
    assert sheet.loc[0, "ictal_excluded_rows"] > 0
    assert sheet.loc[0, "postictal_excluded_rows"] > 0
    assert bool(sheet.loc[0, "right_censoring_field_present"]) is True
    assert sheet.loc[0, "decision"] == ""


def test_build_label_audit_review_sheet_flags_unexcluded_ictal_rows() -> None:
    _, windows, events = make_synthetic_seizeit2_tables()
    labels = label_forecast_windows(windows, events, 5, 30, postictal_exclusion_minutes=5)
    audit = build_label_audit_table(labels, events, minutes_before=40, minutes_after=10)
    ictal_idx = audit.index[audit["is_ictal"]].tolist()[0]
    audit.loc[ictal_idx, "is_excluded"] = False

    sheet = build_label_audit_review_sheet(audit, max_events=1)

    assert sheet.loc[0, "unexpected_ictal_not_excluded_rows"] == 1


def test_build_label_audit_review_sheet_spreads_events_across_patients() -> None:
    audit = pd.DataFrame(
        [
            {
                "event_index": idx,
                "patient_id": patient,
                "recording_id": f"{patient}_rec",
                "seizure_start": f"2024-01-0{idx + 1} 00:00:00",
                "seizure_end": f"2024-01-0{idx + 1} 00:01:00",
                "minutes_to_seizure": 10,
                "forecast_label": False,
                "is_ictal": False,
                "is_postictal": False,
                "is_right_censored": False,
                "is_excluded": False,
            }
            for idx, patient in enumerate(["p1", "p1", "p1", "p2", "p2", "p3"])
        ]
    )

    sheet = build_label_audit_review_sheet(audit, max_events=3)

    assert sheet["patient_id"].tolist() == ["p1", "p2", "p3"]
