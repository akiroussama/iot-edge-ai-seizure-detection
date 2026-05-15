from __future__ import annotations

import subprocess
import sys
from io import BytesIO
from zipfile import ZipFile

import pandas as pd

from src.baselines.simple_rules import ecg_tachycardia_score, generic_zscore_anomaly, normalize_score
from src.features.msg_empatica import extract_msg_empatica_window_features
from src.features.window_features import extract_window_features, make_feature_matrix
from src.utils.io import read_table, write_table


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


def test_extract_msg_empatica_features_from_nested_zip(tmp_path) -> None:
    nested_buffer = BytesIO()
    with ZipFile(nested_buffer, "w") as nested:
        nested.writestr("HR.csv", "0.0\n1.0\n60\n62\n64\n66\n")
        nested.writestr("ACC.csv", "0.0,0.0,0.0\n1.0,1.0,1.0\n3,4,0\n0,0,12\n")
    with ZipFile(tmp_path / "Mayo_1869.zip", "w") as outer:
        outer.writestr("Mayo_1869/0_A000.zip", nested_buffer.getvalue())

    windows = pd.DataFrame(
        {
            "patient_id": ["1869"],
            "recording_id": ["1869_0_A000"],
            "window_start": [pd.Timestamp("1970-01-01 00:00:00")],
            "window_end": [pd.Timestamp("1970-01-01 00:00:02")],
        }
    )

    features = extract_msg_empatica_window_features(tmp_path, windows, modalities=["hr", "acc"])

    assert features.loc[0, "hr_mean"] == 61
    assert features.loc[0, "acc_mean"] == 8.5
    assert features.loc[0, "feature_recordings_processed"] == 1


def test_run_rule_baseline_preserves_exclusions(tmp_path) -> None:
    features = pd.DataFrame(
        {
            "patient_id": ["p1", "p1", "p1", "p1"],
            "recording_id": ["r1", "r1", "r1", "r1"],
            "window_start": pd.date_range("2026-01-01", periods=4, freq="1h"),
            "window_end": pd.date_range("2026-01-01 01:00", periods=4, freq="1h"),
            "forecast_label": [False, False, True, False],
            "is_excluded": [False, True, False, False],
            "hr_mean": [60.0, 200.0, 90.0, float("nan")],
        }
    )
    features_path = tmp_path / "features.parquet"
    out_path = tmp_path / "predictions.parquet"
    write_table(features, features_path)

    subprocess.run(
        [
            sys.executable,
            "scripts/run_rule_baseline.py",
            "--features",
            str(features_path),
            "--out",
            str(out_path),
            "--rule",
            "hr_tachycardia",
            "--target-tiw",
            "1.0",
        ],
        check=True,
    )

    preds = read_table(out_path)
    assert preds["alarm"].tolist() == [True, False, True, False]


def test_normalize_score_uses_reference_rows_only() -> None:
    score = pd.Series([0.0, 1.0, 100.0, float("nan")])
    reference_mask = pd.Series([True, True, False, True])

    normalized = normalize_score(score, reference_mask=reference_mask)

    assert normalized.tolist() == [0.5, 1.0, 1.0, 0.0]


def test_run_rule_baseline_defaults_to_train_fit_and_val_threshold(tmp_path) -> None:
    features = pd.DataFrame(
        {
            "patient_id": ["p1", "p1", "p1", "p1"],
            "recording_id": ["r1", "r1", "r2", "r3"],
            "window_start": pd.date_range("2026-01-01", periods=4, freq="1h"),
            "window_end": pd.date_range("2026-01-01 01:00", periods=4, freq="1h"),
            "forecast_label": [False, False, False, True],
            "is_excluded": [False, False, False, False],
            "split": ["train", "train", "val", "test"],
            "hr_mean": [60.0, 62.0, 70.0, 200.0],
        }
    )
    features_path = tmp_path / "features_split.parquet"
    out_path = tmp_path / "predictions_split.parquet"
    write_table(features, features_path)

    subprocess.run(
        [
            sys.executable,
            "scripts/run_rule_baseline.py",
            "--features",
            str(features_path),
            "--out",
            str(out_path),
            "--rule",
            "hr_tachycardia",
            "--target-tiw",
            "1.0",
        ],
        check=True,
    )

    preds = read_table(out_path)
    assert set(preds["score_fit_split"]) == {"train"}
    assert set(preds["threshold_source_split"]) == {"val"}


def test_rule_baseline_fails_on_patient_without_reference_rows() -> None:
    features = pd.DataFrame(
        {
            "patient_id": ["train_patient", "heldout_patient"],
            "hr_mean": [60.0, 90.0],
        }
    )
    reference_mask = pd.Series([True, False])

    try:
        ecg_tachycardia_score(features, reference_mask=reference_mask)
    except ValueError as exc:
        assert "empty reference rows" in str(exc)
    else:
        raise AssertionError("expected empty patient reference to fail")


def test_normalize_score_fails_on_empty_reference_rows() -> None:
    score = pd.Series([0.1, 0.2])
    reference_mask = pd.Series([False, False])

    try:
        normalize_score(score, reference_mask=reference_mask)
    except ValueError as exc:
        assert "empty reference rows" in str(exc)
    else:
        raise AssertionError("expected empty normalization reference to fail")


def test_rule_scores_fail_on_missing_requested_features() -> None:
    features = pd.DataFrame({"patient_id": ["p1"], "other_feature": [1.0]})

    try:
        ecg_tachycardia_score(features)
    except ValueError as exc:
        assert "hr_mean" in str(exc)
    else:
        raise AssertionError("expected missing HR feature to fail")

    try:
        generic_zscore_anomaly(features, ["missing_feature"])
    except ValueError as exc:
        assert "missing_feature" in str(exc)
    else:
        raise AssertionError("expected missing generic feature to fail")
