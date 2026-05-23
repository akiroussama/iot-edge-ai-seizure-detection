from __future__ import annotations

import json
import subprocess
import sys

import pandas as pd
import pytest

from src.artifacts.gate_c_freeze_package import build_gate_c_freeze_package
from src.artifacts.gate_c_materialize_inputs import (
    GateCMaterializationConfig,
    materialize_gate_c_inputs,
    write_gate_c_materialization,
)
from src.utils.io import read_table, write_table


def _recordings() -> pd.DataFrame:
    rows = []
    for idx, patient in enumerate(("p1", "p2", "p3")):
        start = pd.Timestamp("2026-01-01 00:00:00") + pd.Timedelta(days=idx)
        rows.append(
            {
                "patient_id": patient,
                "recording_id": f"{patient}_r1",
                "recording_start": start,
                "recording_end": start + pd.Timedelta(hours=12),
            }
        )
    return pd.DataFrame(rows)


def _events() -> pd.DataFrame:
    rows = []
    for idx, patient in enumerate(("p1", "p2", "p3")):
        start = pd.Timestamp("2026-01-01 00:00:00") + pd.Timedelta(days=idx, hours=6)
        rows.append(
            {
                "patient_id": patient,
                "recording_id": f"{patient}_r1",
                "seizure_start": start,
                "seizure_end": start + pd.Timedelta(minutes=1),
            }
        )
    return pd.DataFrame(rows)


def _write_sources(tmp_path, *, events: pd.DataFrame | None = None) -> tuple[str, str]:
    recordings_path = tmp_path / "recordings.csv"
    events_path = tmp_path / "events_source.csv"
    write_table(_recordings(), recordings_path)
    write_table(_events() if events is None else events, events_path)
    return str(recordings_path), str(events_path)


def _cfg() -> GateCMaterializationConfig:
    return GateCMaterializationConfig(
        window_duration="1h",
        stride="1h",
        sph_minutes=60.0,
        sop_minutes=120.0,
        postictal_exclusion_minutes=60.0,
        strategy="temporal",
        train_fraction=0.7,
        val_fraction=0.1,
        temporal_basis="elapsed_time",
        temporal_unit="window",
    )


def test_gate_c_materialization_writes_freeze_ready_inputs(tmp_path) -> None:
    recordings_path, events_path = _write_sources(tmp_path)
    materialization = materialize_gate_c_inputs(
        recordings_path=recordings_path,
        events_path=events_path,
        cfg=_cfg(),
    )
    written = write_gate_c_materialization(
        materialization,
        out_dir=tmp_path / "gate_c_inputs",
        recordings_path=recordings_path,
        events_path=events_path,
        cfg=_cfg(),
    )

    assert written.manifest["materialization_status"] == "gate_c_inputs_materialized"
    assert written.manifest["claim_status"] == "not_citable_until_gate_c_freeze_package"
    assert written.manifest["events_rows"] == 3
    assert written.manifest["positive_valid_windows"] > 0
    assert set(written.manifest["split_ids"]) >= {"train", "val", "test"}
    assert read_table(written.output_paths["labels"])["forecast_label"].any()
    assert "EpiTwin-Open leakage audit" in open(written.output_paths["leakage_audit"], encoding="utf-8").read()


def test_materialized_inputs_can_feed_gate_c_freeze_package(tmp_path) -> None:
    recordings_path, events_path = _write_sources(tmp_path)
    materialization = write_gate_c_materialization(
        materialize_gate_c_inputs(
            recordings_path=recordings_path,
            events_path=events_path,
            cfg=_cfg(),
        ),
        out_dir=tmp_path / "gate_c_inputs",
        recordings_path=recordings_path,
        events_path=events_path,
        cfg=_cfg(),
    )

    package = build_gate_c_freeze_package(
        events_path=materialization.output_paths["events"],
        labels_path=materialization.output_paths["labels"],
        splits_path=materialization.output_paths["splits"],
        registry_id="synthetic_materialized_gate_c",
        dataset="synthetic",
        dataset_version="v1",
        source_uri=materialization.output_paths["manifest"],
        generation_command="pytest tests/test_gate_c_materialize_inputs.py",
        split_policy=materialization.manifest["split_strategy"],
        split_ref=materialization.output_paths["manifest"],
        split_ids=tuple(materialization.manifest["split_ids"]),
        horizon_name=materialization.manifest["horizon_name"],
        sph_minutes=materialization.manifest["sph_minutes"],
        sop_minutes=materialization.manifest["sop_minutes"],
        doi_or_prereg_uri="doi:10.0000/synthetic-materialized-gate-c",
    )

    assert package.dry_run_diagnostics["citable_ready"] is True
    assert package.dry_run_diagnostics["blockers"] == []


def test_gate_c_materialization_rejects_no_positive_windows(tmp_path) -> None:
    future_events = _events()
    future_events["seizure_start"] = future_events["seizure_start"] + pd.Timedelta(days=30)
    future_events["seizure_end"] = future_events["seizure_end"] + pd.Timedelta(days=30)
    recordings_path, events_path = _write_sources(tmp_path, events=future_events)

    with pytest.raises(ValueError, match="labels contains no positive valid forecast windows"):
        materialize_gate_c_inputs(
            recordings_path=recordings_path,
            events_path=events_path,
            cfg=_cfg(),
        )


def test_gate_c_materialization_cli_writes_manifest(tmp_path) -> None:
    recordings_path, events_path = _write_sources(tmp_path)
    out_dir = tmp_path / "cli_inputs"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/materialize_gate_c_inputs.py",
            "--recordings",
            recordings_path,
            "--events",
            events_path,
            "--out-dir",
            str(out_dir),
            "--window-duration",
            "1h",
            "--stride",
            "1h",
            "--sph-minutes",
            "60",
            "--sop-minutes",
            "120",
            "--postictal-exclusion-minutes",
            "60",
        ],
        check=True,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)
    manifest = json.loads((out_dir / "gate_c_input_materialization_manifest.json").read_text(encoding="utf-8"))
    assert payload["materialization_status"] == "gate_c_inputs_materialized"
    assert manifest["positive_valid_windows"] > 0
    assert (out_dir / "events.csv").exists()
    assert (out_dir / "labels.csv").exists()
    assert (out_dir / "splits.csv").exists()
