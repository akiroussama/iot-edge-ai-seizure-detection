from __future__ import annotations

from src.datasets.seizeit2_loader import make_synthetic_seizeit2_tables
from src.labeling.sph_sop import label_forecast_windows
from src.reports.label_audit import build_label_audit_table


def test_build_label_audit_table_contains_seizure_context_states() -> None:
    _, windows, events = make_synthetic_seizeit2_tables()
    labels = label_forecast_windows(windows, events, 5, 30, postictal_exclusion_minutes=5)

    audit = build_label_audit_table(labels, events, minutes_before=40, minutes_after=10)

    assert not audit.empty
    assert {"forecast_positive", "ictal_excluded", "postictal_excluded"}.issubset(
        set(audit["audit_state"])
    )
    assert audit["minutes_to_seizure"].min() < 0
    assert audit["minutes_to_seizure"].max() > 0
