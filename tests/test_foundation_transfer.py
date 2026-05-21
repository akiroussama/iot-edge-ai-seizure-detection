from __future__ import annotations

import subprocess
import sys

import pandas as pd
import pytest

from src.features.foundation_transfer import (
    FoundationTransferConfig,
    build_foundation_transfer_features,
)
from src.models.supervised_ladder import select_feature_columns
from src.utils.io import read_table, write_table


def _features() -> pd.DataFrame:
    base = pd.Timestamp("2026-01-01")
    return pd.DataFrame(
        {
            "patient_id": ["p1", "p1", "p2"],
            "recording_id": ["r1", "r1", "r2"],
            "window_start": [base, base + pd.Timedelta(hours=1), base],
            "window_end": [
                base + pd.Timedelta(hours=1),
                base + pd.Timedelta(hours=2),
                base + pd.Timedelta(hours=1),
            ],
            "split": ["train", "val", "test"],
            "forecast_label": [False, True, False],
            "is_excluded": [False, False, False],
            "hr_mean": [70.0, 82.0, 75.0],
        }
    )


def _embeddings() -> pd.DataFrame:
    base = pd.Timestamp("2026-01-01")
    return pd.DataFrame(
        {
            "patient_id": ["p1", "p1", "p2"],
            "recording_id": ["r1", "r1", "r2"],
            "window_start": [base, base + pd.Timedelta(hours=1), base],
            "window_end": [
                base + pd.Timedelta(hours=1),
                base + pd.Timedelta(hours=2),
                base + pd.Timedelta(hours=1),
            ],
            "embedding_0": [0.1, 0.2, 0.3],
            "embedding_1": [1.0, 1.1, 1.2],
        }
    )


def _config(**overrides) -> FoundationTransferConfig:
    values = {
        "model_name": "OpenPPG-FM",
        "source_name": "Synthetic open PPG foundation model",
        "source_url": "https://example.org/open-ppg-fm",
        "source_doi": None,
        "license_name": "Apache-2.0",
        "license_allows_research_use": True,
        "modality": "PPG",
    }
    values.update(overrides)
    return FoundationTransferConfig(**values)


def test_foundation_transfer_attaches_embeddings_without_labels() -> None:
    result = build_foundation_transfer_features(_features(), _embeddings(), config=_config())

    assert "fm_openppg_fm_embedding_0" in result.features.columns
    assert result.metadata["matched_rows"] == 3
    assert result.metadata["embedding_column_count"] == 2
    assert result.manifest.loc[0, "citation_status"] == "not_citable_pre_gate_c"
    selected = select_feature_columns(result.features)
    assert "fm_openppg_fm_embedding_0" in selected
    assert "forecast_label" not in selected


def test_foundation_transfer_rejects_label_columns_in_embedding_table() -> None:
    embeddings = _embeddings()
    embeddings["forecast_label"] = [False, True, False]

    with pytest.raises(ValueError, match="forbidden leakage columns"):
        build_foundation_transfer_features(_features(), embeddings, config=_config())


def test_foundation_transfer_requires_license_permission() -> None:
    with pytest.raises(ValueError, match="license must allow"):
        build_foundation_transfer_features(
            _features(),
            _embeddings(),
            config=_config(license_allows_research_use=False),
        )


def test_foundation_transfer_rejects_missing_coverage_by_default() -> None:
    embeddings = _embeddings().iloc[:2].copy()

    with pytest.raises(ValueError, match="missing for 1 feature rows"):
        build_foundation_transfer_features(_features(), embeddings, config=_config())


def test_prepare_foundation_transfer_features_cli_writes_outputs(tmp_path) -> None:
    features_path = tmp_path / "features.csv"
    embeddings_path = tmp_path / "embeddings.csv"
    out_dir = tmp_path / "transfer"
    write_table(_features(), features_path)
    write_table(_embeddings(), embeddings_path)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/prepare_foundation_transfer_features.py",
            "--features",
            str(features_path),
            "--embeddings",
            str(embeddings_path),
            "--out-dir",
            str(out_dir),
            "--model-name",
            "OpenPPG-FM",
            "--source-name",
            "Synthetic open PPG foundation model",
            "--source-url",
            "https://example.org/open-ppg-fm",
            "--license-name",
            "Apache-2.0",
            "--license-allows-research-use",
            "--modality",
            "PPG",
        ],
        check=True,
        text=True,
        capture_output=True,
    )

    assert '"matched_rows": 3' in result.stdout
    features = read_table(out_dir / "foundation_transfer_features.csv")
    manifest = read_table(out_dir / "foundation_transfer_manifest.csv")
    assert "fm_openppg_fm_embedding_1" in features.columns
    assert manifest.loc[0, "analysis_status"] == "frozen_foundation_embedding_transfer_baseline"
    assert "not citable" in (out_dir / "foundation_transfer_report.md").read_text(encoding="utf-8")
