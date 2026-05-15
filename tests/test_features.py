from __future__ import annotations

import pandas as pd

from src.features.window_features import extract_window_features, make_feature_matrix


def test_extract_window_features_basic() -> None:
    samples = pd.DataFrame(
        {
            "patient_id": ["p1"] * 4,
            "timestamp": pd.date_range("2026-01-01", periods=4, freq="1min"),
            "modality": ["hr", "hr", "hr", "hr"],
            "value": [60, 62, 64, 66],
        }
    )
    windows = pd.DataFrame(
        {
            "patient_id": ["p1"],
            "window_start": [pd.Timestamp("2026-01-01 00:00")],
            "window_end": [pd.Timestamp("2026-01-01 00:03")],
        }
    )
    features = extract_window_features(samples, windows, modalities=["hr"])
    assert features.loc[0, "hr_mean"] == 62
    X, cols = make_feature_matrix(features)
    assert X.shape[0] == 1
    assert "hr_mean" in cols
