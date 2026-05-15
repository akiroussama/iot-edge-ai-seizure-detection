from __future__ import annotations

import subprocess
import sys
from io import BytesIO
from zipfile import ZipFile

import pandas as pd

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
