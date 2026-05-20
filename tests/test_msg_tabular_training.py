from __future__ import annotations

import numpy as np
import pandas as pd

from scripts.train_msg_tabular_baseline import (
    _fit_preprocessor,
    _select_feature_columns,
    _transform,
    _valid_evidence_mask,
)


def test_msg_tabular_feature_selection_excludes_leakage_columns() -> None:
    df = pd.DataFrame(
        {
            "patient_id": ["p1"],
            "forecast_label": [True],
            "time_to_next_seizure_seconds": [300.0],
            "time_since_last_seizure_seconds": [100.0],
            "feature_recordings_processed": [1],
            "hr_mean": [80.0],
            "acc_energy": [1.5],
        }
    )

    assert _select_feature_columns(df, requested=None) == ["hr_mean", "acc_energy"]


def test_msg_tabular_preprocessor_imputes_and_standardizes_from_train_rows() -> None:
    train = pd.DataFrame({"hr_mean": [70.0, np.nan, 90.0], "acc_energy": [1.0, 1.0, 1.0]})
    preprocessor = _fit_preprocessor(train, ["hr_mean", "acc_energy"])

    transformed = _transform(
        pd.DataFrame({"hr_mean": [np.nan], "acc_energy": [1.0]}),
        ["hr_mean", "acc_energy"],
        preprocessor,
    )

    assert transformed.shape == (1, 2)
    assert np.isfinite(transformed).all()
    assert transformed[0, 1] == 0.0


def test_msg_tabular_valid_evidence_requires_non_excluded_feature_row() -> None:
    df = pd.DataFrame(
        {
            "is_excluded": [False, True, False],
            "hr_mean": [75.0, 80.0, np.nan],
            "acc_energy": [np.nan, 2.0, np.nan],
        }
    )

    assert _valid_evidence_mask(df, ["hr_mean", "acc_energy"]).tolist() == [True, False, False]
