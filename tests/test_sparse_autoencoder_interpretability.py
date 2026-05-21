from __future__ import annotations

import json
import subprocess
import sys

import pandas as pd
import pytest

from src.interpretability.sparse_autoencoder import (
    SparseAutoencoderConfig,
    build_sparse_autoencoder_report,
    select_activation_columns,
)
from src.utils.io import read_table, write_table


ACTIVATION_COLS = ("enc_0", "enc_1", "enc_2", "enc_3")


def _activations() -> pd.DataFrame:
    base = pd.Timestamp("2026-01-01 00:00:00")
    basis = {
        0: (2.0, 0.1, 0.0, 0.2),
        1: (0.1, 2.0, 0.2, 0.0),
        2: (0.0, 0.2, 2.0, 0.1),
    }
    rows = []
    for row_idx in range(72):
        concept = row_idx % 3
        split = "train" if row_idx < 42 else "val" if row_idx < 54 else "test"
        patient = f"p{row_idx % 6}"
        start = base + pd.Timedelta(hours=row_idx)
        values = basis[concept]
        rows.append(
            {
                "patient_id": patient,
                "recording_id": f"{patient}_r1",
                "window_start": start,
                "window_end": start + pd.Timedelta(hours=1),
                "split": split,
                "forecast_label": concept == 0,
                "is_excluded": False,
                "risk_score": 0.8 if concept == 0 else 0.2,
                "alarm": concept == 0,
                "time_to_next_seizure_seconds": 30.0 if concept == 0 else 1000.0,
                "enc_0": values[0] + 0.01 * (row_idx % 5),
                "enc_1": values[1] + 0.01 * (row_idx % 7),
                "enc_2": values[2] + 0.01 * (row_idx % 11),
                "enc_3": values[3] + 0.01 * (row_idx % 13),
            }
        )
    return pd.DataFrame(rows)


def test_activation_selection_excludes_labels_predictions_and_leakage() -> None:
    columns = select_activation_columns(_activations())

    assert set(ACTIVATION_COLS).issubset(columns)
    assert "forecast_label" not in columns
    assert "risk_score" not in columns
    assert "time_to_next_seizure_seconds" not in columns


def test_sparse_autoencoder_report_reconstructs_and_writes_dictionary() -> None:
    report = build_sparse_autoencoder_report(
        _activations(),
        config=SparseAutoencoderConfig(
            n_features=3,
            epochs=120,
            learning_rate=0.03,
            sparsity_l1=0.005,
            activation_cols=ACTIVATION_COLS,
            seed=7,
        ),
        model_name="toy_sae",
    )

    assert len(report.scores) == 72
    assert set(report.dictionary["sae_feature"]) == {
        "sae_feature_00",
        "sae_feature_01",
        "sae_feature_02",
    }
    assert report.metadata["final_reconstruction_mse"] < report.metadata["baseline_zero_reconstruction_mse"]
    assert report.metadata["training_artifact_hash"] == report.manifest.loc[0, "training_artifact_hash"]
    assert report.associations["association_status"].eq("post_hoc_not_causal").all()


def test_label_flip_does_not_change_unsupervised_sae_artifact() -> None:
    activations = _activations()
    mutated = activations.copy()
    test_rows = mutated["split"].eq("test")
    mutated.loc[test_rows, "forecast_label"] = ~mutated.loc[test_rows, "forecast_label"].astype(bool)
    config = SparseAutoencoderConfig(
        n_features=3,
        epochs=80,
        learning_rate=0.03,
        sparsity_l1=0.005,
        activation_cols=ACTIVATION_COLS,
        seed=11,
    )

    base = build_sparse_autoencoder_report(activations, config=config, model_name="toy_sae")
    changed = build_sparse_autoencoder_report(mutated, config=config, model_name="toy_sae")

    pd.testing.assert_frame_equal(
        base.scores.filter(like="sae_feature_"),
        changed.scores.filter(like="sae_feature_"),
    )
    pd.testing.assert_frame_equal(base.dictionary, changed.dictionary)
    assert base.metadata["training_artifact_hash"] == changed.metadata["training_artifact_hash"]


def test_prediction_alignment_rejects_mismatched_labels() -> None:
    activations = _activations()
    predictions = activations[
        ["patient_id", "recording_id", "window_start", "window_end", "forecast_label", "is_excluded"]
    ].copy()
    predictions["risk_score"] = activations["risk_score"]
    predictions.loc[0, "forecast_label"] = not bool(predictions.loc[0, "forecast_label"])

    with pytest.raises(ValueError, match="does not match activations"):
        build_sparse_autoencoder_report(
            activations,
            predictions=predictions,
            config=SparseAutoencoderConfig(
                n_features=3,
                epochs=10,
                activation_cols=ACTIVATION_COLS,
            ),
        )


def test_sparse_autoencoder_cli_writes_outputs(tmp_path) -> None:
    activations = _activations()
    activations_path = tmp_path / "activations.csv"
    out_dir = tmp_path / "sae"
    write_table(activations, activations_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_sparse_autoencoder_interpretability.py",
            "--activations",
            str(activations_path),
            "--out-dir",
            str(out_dir),
            "--model-name",
            "toy_sae",
            "--activation-cols",
            ",".join(ACTIVATION_COLS),
            "--n-features",
            "3",
            "--epochs",
            "80",
            "--learning-rate",
            "0.03",
            "--sparsity-l1",
            "0.005",
        ],
        check=True,
        text=True,
        capture_output=True,
    )

    assert '"model_name": "toy_sae"' in result.stdout
    scores = read_table(out_dir / "sae_feature_scores.csv")
    dictionary = read_table(out_dir / "sae_dictionary.csv")
    associations = read_table(out_dir / "sae_associations.csv")
    manifest = read_table(out_dir / "sae_manifest.csv")
    payload = json.loads((out_dir / "sae_report.json").read_text(encoding="utf-8"))
    assert len(scores) == 72
    assert len(dictionary) == 3
    assert associations["association_status"].eq("post_hoc_not_causal").all()
    assert manifest.loc[0, "model_name"] == "toy_sae"
    assert payload["metadata"]["result_status"] == "interpretability_artifact_pre_gate_c_not_citable"
    assert "not citable" in (out_dir / "sae_report.md").read_text(encoding="utf-8")
