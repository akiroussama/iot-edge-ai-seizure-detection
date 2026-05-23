from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from scripts.make_leaderboard_row import build_leaderboard_row, write_outputs
from src.artifacts.registry import load_registry, verify_gate_c_registry
from src.baselines.forecast_nulls import generate_forecast_null, variant_counts
from src.reports.calibration_skill import build_calibration_skill_report, table_records
from src.reports.forecastability_atlas import (
    ForecastabilityThresholds,
    build_forecastability_atlas,
    forecastability_atlas_markdown,
)
from src.utils.io import read_table, write_table

FROZEN_NULL_MODELS = (
    "split_prevalence_prior",
    "rate_matched_random",
    "patient_prior",
    "cycle_preserving_random",
)
REQUIRED_FROZEN_ROLES = ("events", "labels", "splits")


@dataclass(frozen=True)
class GateCFrozenBenchmarkConfig:
    registry_path: str | Path
    out_dir: str | Path
    root: str | Path = "."
    null_models: tuple[str, ...] = FROZEN_NULL_MODELS
    fit_split: str = "train"
    threshold_split: str = "val"
    evaluation_split: str = "test"
    target_tiw: float = 0.1
    seed: int = 42
    patient_min_events: int = 3
    cycle_bin: str = "hour_of_day"
    event_filter: str | None = "recording_match_status=matched"
    restrict_events_to_prediction_coverage: bool = True
    sph_minutes: float = 60.0
    sop_minutes: float = 1440.0
    window_seconds: float = 3600.0
    stride_seconds: float = 3600.0
    n_bins: int = 10
    bootstrap_samples: int = 200
    min_events: int = 5
    min_valid_prediction_rows: int = 100
    min_brier_skill_score: float = 0.0
    max_far_per_day: float | None = None
    label_audit_status: str = "sampled_human_attested"
    doi_or_prereg_uri: str | None = None
    notes: str = (
        "Frozen MSG null baseline row; source DOI is not a newly minted benchmark DOI. "
        "Event metrics use matched prediction-coverable events."
    )


@dataclass(frozen=True)
class GateCFrozenBenchmarkResult:
    manifest: dict[str, Any]
    leaderboard: pd.DataFrame
    leaderboard_with_ci: pd.DataFrame
    calibration_summary: pd.DataFrame
    calibration_skill: pd.DataFrame
    calibration_reliability: pd.DataFrame
    calibration_bootstrap: pd.DataFrame
    atlas: pd.DataFrame
    output_paths: dict[str, str]


def _repo_commit(root: Path) -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short=12", "HEAD"],
            cwd=root,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return None


def _clean_value(value: Any) -> Any:
    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        return value.item()
    return value


def _records(df: pd.DataFrame) -> list[dict[str, Any]]:
    return [{key: _clean_value(value) for key, value in row.items()} for row in df.to_dict("records")]


def _artifact_records_by_role(registry: dict[str, Any]) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    for artifact in registry.get("artifacts", []):
        role = str(artifact.get("role", ""))
        if role in REQUIRED_FROZEN_ROLES and role not in records:
            records[role] = artifact
    missing = sorted(set(REQUIRED_FROZEN_ROLES) - set(records))
    if missing:
        raise ValueError(f"frozen registry missing required artifact roles: {missing}")
    return records


def _relative_to_root(path: Path, root: Path) -> Path:
    try:
        return path.resolve().relative_to(root.resolve())
    except ValueError:
        return path


def _reject_data_artifacts(records: dict[str, dict[str, Any]], root: Path) -> None:
    offenders = []
    for role, artifact in records.items():
        raw_path = Path(str(artifact["path"]))
        rel = raw_path if not raw_path.is_absolute() else _relative_to_root(raw_path, root)
        if rel.parts and rel.parts[0] == "data":
            offenders.append(f"{role}={artifact['path']}")
    if offenders:
        raise ValueError(
            "Gate C frozen benchmark refuses non-frozen data/* inputs: "
            + ", ".join(sorted(offenders))
        )


def _resolve_artifact_paths(
    registry: dict[str, Any],
    *,
    root: Path,
) -> dict[str, Path]:
    records = _artifact_records_by_role(registry)
    _reject_data_artifacts(records, root)
    return {
        role: (Path(record["path"]) if Path(record["path"]).is_absolute() else root / record["path"])
        for role, record in records.items()
    }


def _verify_registry(config: GateCFrozenBenchmarkConfig) -> tuple[dict[str, Any], dict[str, Any], dict[str, Path]]:
    root = Path(config.root)
    registry_path = Path(config.registry_path)
    full_registry_path = registry_path if registry_path.is_absolute() else root / registry_path
    registry = load_registry(full_registry_path)
    artifact_paths = _resolve_artifact_paths(registry, root=root)
    verification = verify_gate_c_registry(registry, root=root, require_frozen=True)
    if not verification["ok"]:
        raise ValueError(f"Gate C registry verification failed: {verification['errors']}")
    return registry, verification, artifact_paths


def _filter_split(df: pd.DataFrame, split: str) -> pd.DataFrame:
    if "split" not in df.columns:
        raise ValueError("prediction table missing split column")
    return df.loc[df["split"].astype(str).eq(split)].reset_index(drop=True)


def _leaderboard_args(
    *,
    config: GateCFrozenBenchmarkConfig,
    registry: dict[str, Any],
    model_name: str,
    reference_name: str,
    registry_path: str,
    split_ref: str | None,
    repo_commit: str | None,
) -> argparse.Namespace:
    split_manifest = registry.get("split_manifest", {})
    doi = config.doi_or_prereg_uri or registry.get("doi_or_prereg_uri")
    return argparse.Namespace(
        result_id=f"{registry['registry_id']}__{model_name}__{config.evaluation_split}",
        result_status="gate_c_frozen_citable",
        citation_status="citable_after_gate_c",
        task_type="forecasting",
        dataset=registry["dataset"],
        cohort="matched_prediction_coverable_test",
        modality="labels_only_null",
        model_name=model_name,
        model_family="forecast_null",
        split_name=config.evaluation_split,
        split_policy="temporal_recording",
        split_ref=split_ref or split_manifest.get("split_ref"),
        horizon_name=split_manifest.get("horizon_name", "SPH60_SOP1440"),
        sph_minutes=float(config.sph_minutes),
        sop_minutes=float(config.sop_minutes),
        window_seconds=float(config.window_seconds),
        stride_seconds=float(config.stride_seconds),
        event_unit="seizure",
        cluster_gap_minutes=None,
        event_filter=config.event_filter,
        prediction_filter=f"split={config.evaluation_split}",
        acknowledge_event_filter_bias=bool(config.event_filter),
        restrict_events_to_prediction_coverage=config.restrict_events_to_prediction_coverage,
        bss_reference=reference_name,
        label_audit_status=config.label_audit_status,
        gate_b_status="passed",
        gate_c_status="passed",
        leakage_status="clean",
        split_frozen_status="frozen_git_tag",
        doi_or_prereg_uri=doi,
        edge_target=None,
        quantization=None,
        model_size_kb=None,
        ram_kb=None,
        flash_kb=None,
        latency_ms=None,
        energy_mj_per_inference=None,
        repo_commit=repo_commit,
        evidence_uri=registry_path,
        notes=config.notes,
        artifact_registry=registry_path,
        artifact_registry_root=str(config.root),
    )


def _write_calibration_report(report, out_dir: Path) -> dict[str, str]:
    paths = {
        "summary": str(out_dir / "calibration_summary.csv"),
        "skill": str(out_dir / "calibration_skill.csv"),
        "reliability": str(out_dir / "calibration_reliability.csv"),
        "bootstrap": str(out_dir / "calibration_bootstrap.csv"),
        "json": str(out_dir / "calibration_report.json"),
        "markdown": str(out_dir / "calibration_report.md"),
    }
    write_table(report.summary, paths["summary"])
    write_table(report.skill, paths["skill"])
    write_table(report.reliability, paths["reliability"])
    write_table(report.bootstrap, paths["bootstrap"])
    payload = {
        "metadata": report.metadata,
        "summary": table_records(report.summary),
        "skill": table_records(report.skill),
        "reliability": table_records(report.reliability),
        "bootstrap": table_records(report.bootstrap),
    }
    Path(paths["json"]).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    Path(paths["markdown"]).write_text(_calibration_markdown(report), encoding="utf-8")
    return paths


def _markdown_table(df: pd.DataFrame, columns: list[str] | None = None, max_rows: int = 20) -> str:
    if df.empty:
        return "_No rows._"
    view = df.loc[:, columns] if columns else df
    view = view.head(max_rows)
    lines = [
        "| " + " | ".join(str(col) for col in view.columns) + " |",
        "| " + " | ".join(["---"] * len(view.columns)) + " |",
    ]
    for _, row in view.iterrows():
        lines.append("| " + " | ".join(str(row[col]) for col in view.columns) + " |")
    if len(df) > max_rows:
        lines.append(f"\nShowing {max_rows} of {len(df)} rows.")
    return "\n".join(lines)


def _calibration_markdown(report) -> str:
    warning = ""
    if report.metadata["citation_status"] != "citable_after_gate_c":
        warning = "\nCitation status: not citable as a benchmark result.\n"
    return f"""# Calibration And Null-Corrected Skill Report
{warning}
## Metadata

- Model: `{report.metadata["model_name"]}`
- References: `{", ".join(report.metadata["reference_names"])}`
- Result status: `{report.metadata["result_status"]}`
- Citation status: `{report.metadata["citation_status"]}`
- Gate C status: `{report.metadata["gate_c_status"]}`
- Bootstrap samples: `{report.metadata["n_bootstrap"]}`

## Summary

{_markdown_table(report.summary)}

## Brier Skill Score

{_markdown_table(report.skill)}

## Bootstrap Confidence Intervals

{_markdown_table(report.bootstrap)}

## Reliability Bins

{_markdown_table(report.reliability)}
"""


def _stamp_model(df: pd.DataFrame, model_name: str) -> pd.DataFrame:
    out = df.copy()
    if "model_name" not in out.columns:
        out.insert(0, "model_name", model_name)
    return out


def _ci_from_bootstrap(bootstrap: pd.DataFrame, reference_name: str) -> tuple[float | None, float | None]:
    if bootstrap.empty:
        return None, None
    rows = bootstrap.loc[
        bootstrap["reference_name"].astype(str).eq(reference_name)
        & bootstrap["scope"].astype(str).eq("patient")
    ]
    if rows.empty:
        rows = bootstrap.loc[bootstrap["reference_name"].astype(str).eq(reference_name)]
    if rows.empty:
        return None, None
    row = rows.iloc[0]
    return _clean_value(row.get("ci_low")), _clean_value(row.get("ci_high"))


def _audit_markdown(
    *,
    registry: dict[str, Any],
    verification: dict[str, Any],
    leaderboard: pd.DataFrame,
    leaderboard_with_ci: pd.DataFrame,
    atlas: pd.DataFrame,
    output_paths: dict[str, str],
    config: GateCFrozenBenchmarkConfig,
) -> str:
    result_cols = [
        "model_name",
        "events_used_for_metrics",
        "valid_prediction_rows",
        "sensitivity",
        "false_alarm_rate_per_day",
        "time_in_warning",
        "brier_score",
        "brier_skill_score",
        "brier_skill_score_ci_low",
        "brier_skill_score_ci_high",
        "expected_calibration_error",
    ]
    atlas_cols = [
        "model_name",
        "forecastability_label",
        "claim_status",
        "paper_table_ready",
        "forecastability_reason",
    ]
    source_total = int(leaderboard["events_source_total"].iloc[0]) if not leaderboard.empty else 0
    events_after_filter = int(leaderboard["events_after_filter"].iloc[0]) if not leaderboard.empty else 0
    events_used = int(leaderboard["events_used_for_metrics"].iloc[0]) if not leaderboard.empty else 0
    return f"""# Gate C Frozen Null Benchmark Audit

## Frozen-Only Guard

- Registry id: `{registry["registry_id"]}`
- Registry verification ok: `{verification["ok"]}`
- Registry artifacts verified: `{verification["artifact_count"]}`
- Required benchmark inputs came from committed freeze artifacts, not `data/*`.
- Output manifest: `{output_paths["manifest"]}`

## Denominator

- Source events: `{source_total}`
- Event filter: `{config.event_filter or "none"}`
- Events after filter: `{events_after_filter}`
- Restricted to prediction coverage: `{config.restrict_events_to_prediction_coverage}`
- Events used for metrics on `{config.evaluation_split}`: `{events_used}`

The filtered denominator is a matched, prediction-coverable subset. It is the
right denominator for comparing frozen forecasts on this split, but it must not
be described as all annotated MSG seizures.

## Frozen Null Results

{_markdown_table(leaderboard_with_ci, result_cols)}

## Forecastability Classification

{_markdown_table(atlas, atlas_cols)}

## Scientific Interpretation

- These rows are null baselines, not trained wearable models.
- `split_prevalence_prior` is the BSS reference; its self-skill should be zero.
- Any positive skill from `patient_prior` or `cycle_preserving_random` is evidence
  that patient/cycle structure in the frozen labels is exploitable, not proof of
  a deployable clinical model.
- A Q1-level claim still requires comparing non-null models against these frozen
  nulls, reporting denominator scope, and preserving negative/underpowered rows.
"""


def run_gate_c_frozen_benchmark(
    config: GateCFrozenBenchmarkConfig,
) -> GateCFrozenBenchmarkResult:
    root = Path(config.root)
    out_dir = Path(config.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    registry, verification, artifact_paths = _verify_registry(config)
    labels = read_table(artifact_paths["labels"])
    events = read_table(artifact_paths["events"])
    repo_commit = _repo_commit(root)
    registry_path = str(config.registry_path)
    split_ref = registry.get("split_manifest", {}).get("split_ref")

    predictions_dir = out_dir / "predictions"
    leaderboard_dir = out_dir / "leaderboard"
    calibration_dir = out_dir / "calibration"
    predictions_by_model: dict[str, pd.DataFrame] = {}
    prediction_paths: dict[str, str] = {}
    variant_by_model: dict[str, dict[str, int]] = {}
    for model in config.null_models:
        predictions = generate_forecast_null(
            labels,
            null_model=model,
            fit_split=config.fit_split,
            threshold_split=config.threshold_split,
            target_tiw=config.target_tiw,
            patient_min_events=config.patient_min_events,
            cycle_bin=config.cycle_bin,
            seed=config.seed,
        )
        path = predictions_dir / f"{model}.parquet"
        write_table(predictions, path)
        predictions_by_model[model] = predictions
        prediction_paths[model] = str(path)
        variant_by_model[model] = variant_counts(predictions)

    if "split_prevalence_prior" not in predictions_by_model:
        raise ValueError("split_prevalence_prior must be included as the BSS reference")
    reference_predictions = predictions_by_model["split_prevalence_prior"]

    leaderboard_rows = []
    leaderboard_ci_rows = []
    calibration_summaries = []
    calibration_skills = []
    calibration_reliability = []
    calibration_bootstrap = []
    calibration_paths: dict[str, dict[str, str]] = {}
    for model, predictions in predictions_by_model.items():
        reference_name = "split_prevalence_prior"
        args = _leaderboard_args(
            config=config,
            registry=registry,
            model_name=model,
            reference_name=reference_name,
            registry_path=registry_path,
            split_ref=split_ref,
            repo_commit=repo_commit,
        )
        row = build_leaderboard_row(
            predictions=predictions,
            events=events,
            reference_predictions=reference_predictions,
            args=args,
        )
        row_csv = leaderboard_dir / f"{model}.csv"
        row_json = leaderboard_dir / f"{model}.json"
        row_md = leaderboard_dir / f"{model}.md"
        write_outputs(row, row_csv, row_json, row_md)

        model_test = _filter_split(predictions, config.evaluation_split)
        reference_test = _filter_split(reference_predictions, config.evaluation_split)
        report = build_calibration_skill_report(
            model_test,
            {reference_name: reference_test},
            model_name=model,
            n_bins=config.n_bins,
            n_bootstrap=config.bootstrap_samples,
            seed=config.seed,
            patient_col="patient_id",
            event_col=None,
            result_status="gate_c_frozen_citable",
            citation_status="citable_after_gate_c",
            gate_c_status="passed",
        )
        calibration_paths[model] = _write_calibration_report(report, calibration_dir / model)
        ci_low, ci_high = _ci_from_bootstrap(report.bootstrap, reference_name)
        row_with_ci = {
            **row,
            "brier_skill_score_ci_low": ci_low,
            "brier_skill_score_ci_high": ci_high,
        }

        leaderboard_rows.append(row)
        leaderboard_ci_rows.append(row_with_ci)
        calibration_summaries.append(_stamp_model(report.summary, model))
        calibration_skills.append(_stamp_model(report.skill, model))
        calibration_reliability.append(_stamp_model(report.reliability, model))
        calibration_bootstrap.append(_stamp_model(report.bootstrap, model))

    leaderboard = pd.DataFrame(leaderboard_rows)
    leaderboard_with_ci = pd.DataFrame(leaderboard_ci_rows)
    summary = pd.concat(calibration_summaries, ignore_index=True)
    skill = pd.concat(calibration_skills, ignore_index=True)
    reliability = pd.concat(calibration_reliability, ignore_index=True)
    bootstrap = pd.concat(calibration_bootstrap, ignore_index=True)
    atlas = build_forecastability_atlas(
        leaderboard_with_ci,
        reliability_df=reliability,
        thresholds=ForecastabilityThresholds(
            min_events=config.min_events,
            min_valid_prediction_rows=config.min_valid_prediction_rows,
            min_brier_skill_score=config.min_brier_skill_score,
            max_false_alarm_rate_per_day=config.max_far_per_day,
        ),
        gate_c_required=True,
    )

    output_paths = {
        "leaderboard": str(out_dir / "leaderboard_rows.csv"),
        "leaderboard_with_ci": str(out_dir / "leaderboard_rows_with_ci.csv"),
        "calibration_summary": str(out_dir / "calibration_summary.csv"),
        "calibration_skill": str(out_dir / "calibration_skill.csv"),
        "calibration_reliability": str(out_dir / "calibration_reliability.csv"),
        "calibration_bootstrap": str(out_dir / "calibration_bootstrap.csv"),
        "forecastability_atlas": str(out_dir / "forecastability_atlas.csv"),
        "forecastability_atlas_md": str(out_dir / "forecastability_atlas.md"),
        "audit": str(out_dir / "frozen_benchmark_audit.md"),
        "manifest": str(out_dir / "frozen_benchmark_manifest.json"),
    }
    write_table(leaderboard, output_paths["leaderboard"])
    write_table(leaderboard_with_ci, output_paths["leaderboard_with_ci"])
    write_table(summary, output_paths["calibration_summary"])
    write_table(skill, output_paths["calibration_skill"])
    write_table(reliability, output_paths["calibration_reliability"])
    write_table(bootstrap, output_paths["calibration_bootstrap"])
    write_table(atlas, output_paths["forecastability_atlas"])
    Path(output_paths["forecastability_atlas_md"]).write_text(
        forecastability_atlas_markdown(atlas, title="Gate C Frozen Forecastability Atlas"),
        encoding="utf-8",
    )
    Path(output_paths["audit"]).write_text(
        _audit_markdown(
            registry=registry,
            verification=verification,
            leaderboard=leaderboard,
            leaderboard_with_ci=leaderboard_with_ci,
            atlas=atlas,
            output_paths=output_paths,
            config=config,
        ),
        encoding="utf-8",
    )
    manifest = {
        "benchmark_status": "gate_c_frozen_null_benchmark_complete",
        "registry_id": registry["registry_id"],
        "registry_path": registry_path,
        "registry_verification": verification,
        "frozen_artifact_paths": {role: str(path) for role, path in artifact_paths.items()},
        "null_models": list(config.null_models),
        "prediction_paths": prediction_paths,
        "null_model_variants": variant_by_model,
        "fit_split": config.fit_split,
        "threshold_split": config.threshold_split,
        "evaluation_split": config.evaluation_split,
        "target_tiw": float(config.target_tiw),
        "event_filter": config.event_filter,
        "restrict_events_to_prediction_coverage": config.restrict_events_to_prediction_coverage,
        "sph_minutes": float(config.sph_minutes),
        "sop_minutes": float(config.sop_minutes),
        "leaderboard_rows": _records(leaderboard_with_ci),
        "forecastability_labels": atlas["forecastability_label"].value_counts().to_dict()
        if not atlas.empty
        else {},
        "calibration_paths": calibration_paths,
        "output_paths": output_paths,
    }
    Path(output_paths["manifest"]).write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return GateCFrozenBenchmarkResult(
        manifest=manifest,
        leaderboard=leaderboard,
        leaderboard_with_ci=leaderboard_with_ci,
        calibration_summary=summary,
        calibration_skill=skill,
        calibration_reliability=reliability,
        calibration_bootstrap=bootstrap,
        atlas=atlas,
        output_paths=output_paths,
    )
