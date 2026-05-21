from __future__ import annotations

import json
import subprocess
import sys

import pandas as pd
import pytest

from src.models.supervised_ladder import (
    LADDER_MODEL_SPECS,
    STANDARD_OUTPUT_COLUMNS,
    SupervisedLadderConfig,
    derive_model_seed,
    select_feature_columns,
    train_supervised_ladder,
    train_supervised_ladder_model,
)
from src.utils.io import read_table, write_table


def _features() -> pd.DataFrame:
    base = pd.Timestamp("2026-01-01 00:00:00")
    rows = []
    specs = [
        ("train", "p1", [0.9, 0.8, 0.7, 0.1, 0.2, 0.3]),
        ("train", "p2", [0.85, 0.75, 0.65, 0.15, 0.25, 0.35]),
        ("val", "p1", [0.95, 0.05, 0.7, 0.3]),
        ("val", "p2", [0.9, 0.1, 0.8, 0.2]),
        ("test", "p1", [0.92, 0.12, 0.72, 0.32]),
        ("test", "p2", [0.88, 0.18, 0.68, 0.28]),
    ]
    cursor = 0
    for split, patient, values in specs:
        for value in values:
            start = base + pd.Timedelta(hours=cursor)
            rows.append(
                {
                    "patient_id": patient,
                    "recording_id": f"{patient}_{split}",
                    "split": split,
                    "window_start": start,
                    "window_end": start + pd.Timedelta(hours=1),
                    "hr_mean": 60.0 + 40.0 * value,
                    "acc_energy": value,
                    "time_to_next_seizure_seconds": 10.0 if value > 0.5 else 1000.0,
                    "forecast_label": value > 0.5,
                    "is_excluded": False,
                }
            )
            cursor += 1
    return pd.DataFrame(rows)


def _reference(features: pd.DataFrame) -> pd.DataFrame:
    reference = features[
        ["patient_id", "recording_id", "window_start", "window_end", "forecast_label", "is_excluded"]
    ].copy()
    reference["risk_score"] = 0.5
    reference["alarm"] = False
    return reference


def test_ladder_specs_include_expected_rungs() -> None:
    assert {"logistic_regression", "gradient_stumps", "mlp", "tcn", "gru"}.issubset(
        LADDER_MODEL_SPECS
    )
    assert LADDER_MODEL_SPECS["logistic_regression"]["requires_torch"] is False
    assert LADDER_MODEL_SPECS["tcn"]["input_kind"] == "patient_ordered_window_sequence"


def test_model_seed_derivation_is_stable_and_model_specific() -> None:
    logistic_seed = derive_model_seed(42, "logistic_regression", 0)
    stumps_seed = derive_model_seed(42, "gradient_stumps", 1)

    assert logistic_seed == derive_model_seed(42, "logistic_regression", 0)
    assert logistic_seed != stumps_seed


def test_feature_selection_excludes_leakage_columns() -> None:
    cols = select_feature_columns(_features())

    assert "hr_mean" in cols
    assert "acc_energy" in cols
    assert "time_to_next_seizure_seconds" not in cols
    assert "forecast_label" not in cols


def test_supervised_ladder_emits_standardized_predictions_and_manifest() -> None:
    features = _features()
    predictions, manifest = train_supervised_ladder(
        features,
        reference_predictions=_reference(features),
        reference_name="constant_prior",
        configs=[
            SupervisedLadderConfig(
                model_name="logistic_regression",
                epochs=40,
                learning_rate=0.1,
                target_tiw=0.5,
                seed=7,
            ),
            SupervisedLadderConfig(
                model_name="gradient_stumps",
                n_estimators=5,
                learning_rate=0.3,
                target_tiw=0.5,
                seed=7,
            ),
        ],
    )

    assert set(predictions) == {"logistic_regression", "gradient_stumps"}
    assert set(manifest["model_name"]) == {"logistic_regression", "gradient_stumps"}
    for model_name, table in predictions.items():
        assert set(STANDARD_OUTPUT_COLUMNS).issubset(table.columns)
        assert table["supervised_model_name"].eq(model_name).all()
        assert table["comparator_reference_name"].eq("constant_prior").all()
        assert table["risk_score"].between(0, 1).all()
        assert table["training_artifact_hash"].str.len().eq(64).all()
        assert table["supervised_prediction_status"].eq("scored").all()


def test_no_feature_evidence_rows_are_explicitly_marked() -> None:
    features = _features()
    no_evidence_idx = features.index[features["split"].eq("test")][0]
    features.loc[no_evidence_idx, ["hr_mean", "acc_energy"]] = pd.NA

    predictions, log = train_supervised_ladder_model(
        features,
        reference_predictions=_reference(features),
        reference_name="constant_prior",
        config=SupervisedLadderConfig(epochs=10, target_tiw=0.5),
    )

    assert bool(predictions.loc[no_evidence_idx, "supervised_valid_evidence"]) is False
    assert predictions.loc[no_evidence_idx, "supervised_prediction_status"] == "no_feature_evidence"
    assert bool(predictions.loc[no_evidence_idx, "alarm"]) is False
    assert log["no_feature_evidence_rows"] == 1


def test_supervised_ladder_requires_reference_comparator() -> None:
    with pytest.raises(ValueError, match="require a named null/reference comparator"):
        train_supervised_ladder_model(
            _features(),
            reference_predictions=_reference(_features()),
            reference_name="",
            config=SupervisedLadderConfig(epochs=5),
        )


def test_test_labels_do_not_change_predictions_when_reference_matches() -> None:
    features = _features()
    mutated = features.copy()
    test_mask = mutated["split"].eq("test")
    mutated.loc[test_mask, "forecast_label"] = ~mutated.loc[test_mask, "forecast_label"].astype(bool)
    config = SupervisedLadderConfig(
        model_name="logistic_regression",
        epochs=30,
        learning_rate=0.1,
        target_tiw=0.5,
        seed=11,
    )

    base_preds, _ = train_supervised_ladder_model(
        features,
        reference_predictions=_reference(features),
        reference_name="constant_prior",
        config=config,
    )
    mutated_preds, _ = train_supervised_ladder_model(
        mutated,
        reference_predictions=_reference(mutated),
        reference_name="constant_prior",
        config=config,
    )

    pd.testing.assert_series_equal(base_preds["risk_score"], mutated_preds["risk_score"])
    pd.testing.assert_series_equal(base_preds["alarm"], mutated_preds["alarm"])


def test_run_supervised_model_ladder_cli_writes_outputs(tmp_path) -> None:
    features = _features()
    features_path = tmp_path / "features.csv"
    reference_path = tmp_path / "reference.csv"
    out_dir = tmp_path / "ladder"
    write_table(features, features_path)
    write_table(_reference(features), reference_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_supervised_model_ladder.py",
            "--features",
            str(features_path),
            "--reference-predictions",
            f"constant_prior={reference_path}",
            "--out-dir",
            str(out_dir),
            "--model",
            "logistic_regression",
            "--model",
            "gradient_stumps",
            "--epochs",
            "20",
            "--learning-rate",
            "0.1",
            "--target-tiw",
            "0.5",
        ],
        check=True,
        text=True,
        capture_output=True,
    )

    assert '"reference_name": "constant_prior"' in result.stdout
    logistic = read_table(out_dir / "logistic_regression_predictions.csv")
    stumps = read_table(out_dir / "gradient_stumps_predictions.csv")
    manifest = read_table(out_dir / "supervised_ladder_manifest.csv")
    payload = json.loads((out_dir / "supervised_ladder_manifest.json").read_text(encoding="utf-8"))
    assert logistic["risk_score"].between(0, 1).all()
    assert stumps["risk_score"].between(0, 1).all()
    assert set(manifest["model_name"]) == {"logistic_regression", "gradient_stumps"}
    assert manifest["seed"].nunique() == 2
    assert len(payload) == 2
