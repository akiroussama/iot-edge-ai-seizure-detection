from __future__ import annotations

import pandas as pd

from src.calibration.thresholding import apply_patient_thresholds, patient_specific_quantile_thresholds, quantile_threshold
from src.calibration.conformal_risk import calibrate_threshold_by_empirical_risk


def test_quantile_threshold() -> None:
    th = quantile_threshold([0.1, 0.2, 0.9, 1.0], warning_fraction=0.5)
    assert 0.2 <= th <= 0.9


def test_patient_specific_thresholds() -> None:
    df = pd.DataFrame({"patient_id": ["a", "a", "b", "b"], "risk_score": [0.1, 0.9, 0.2, 0.8]})
    thresholds = patient_specific_quantile_thresholds(df, 0.5)
    out = apply_patient_thresholds(df, thresholds)
    assert out["alarm"].sum() >= 2


def test_apply_patient_thresholds_refuses_missing_patient_threshold() -> None:
    df = pd.DataFrame({"patient_id": ["a", "b"], "risk_score": [0.1, 0.9]})

    try:
        apply_patient_thresholds(df, {"a": 0.5})
    except ValueError as exc:
        assert "missing patient-specific thresholds" in str(exc)
    else:
        raise AssertionError("expected missing patient threshold to fail")


def test_empirical_risk_threshold() -> None:
    df = pd.DataFrame({"risk_score": [0.1, 0.2, 0.8, 0.9], "false_alarm_loss": [0, 0, 1, 1]})
    res = calibrate_threshold_by_empirical_risk(df, target_risk=0.5, thresholds=[0.0, 0.5, 0.85])
    assert res.n == 4
