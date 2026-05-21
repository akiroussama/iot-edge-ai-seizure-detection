from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

SEIZEIT2_CORE_MODALITIES = ("ecg", "acc", "bte_eeg")
SEIZEIT2_TRACK_MODALITIES = ("ecg", "acc", "bte_eeg", "multimodal")
VALID_SPLITS = {"train", "val", "test", "holdout"}
DEFAULT_SPLIT_ORDER = ("train", "val", "test", "holdout", "unassigned")


@dataclass(frozen=True)
class SeizeIT2TaskSpec:
    task_name: str
    task_type: str
    leaderboard_task_type: str
    horizon_name: str
    sph_minutes: float | None
    sop_minutes: float | None
    score_level: str
    event_unit: str
    description: str


DEFAULT_SEIZEIT2_TASKS = (
    SeizeIT2TaskSpec(
        task_name="ictal_detection",
        task_type="detection",
        leaderboard_task_type="detection",
        horizon_name="ictal_detection",
        sph_minutes=None,
        sop_minutes=None,
        score_level="sample_and_event",
        event_unit="episode",
        description="Ictal/background detection track; not a long-horizon forecast.",
    ),
    SeizeIT2TaskSpec(
        task_name="short_early_warning",
        task_type="early_warning",
        leaderboard_task_type="forecasting",
        horizon_name="SPH0_SOP5",
        sph_minutes=0.0,
        sop_minutes=5.0,
        score_level="event",
        event_unit="seizure",
        description="Short warning track separated from detection and long-horizon forecasting.",
    ),
    SeizeIT2TaskSpec(
        task_name="long_horizon_forecasting",
        task_type="forecasting",
        leaderboard_task_type="forecasting",
        horizon_name="SPH5_SOP30",
        sph_minutes=5.0,
        sop_minutes=30.0,
        score_level="event",
        event_unit="seizure",
        description="Long-horizon forecasting track; not mixed with MSG forecasting rows.",
    ),
)

TRACK_COLUMNS = [
    "benchmark_family",
    "dataset",
    "split_name",
    "task_name",
    "task_type",
    "leaderboard_task_type",
    "horizon_name",
    "sph_minutes",
    "sop_minutes",
    "score_level",
    "event_unit",
    "modality_track",
    "required_modalities",
    "available_modalities",
    "patients",
    "recordings",
    "events",
    "sample_rows",
    "official_split_status",
    "result_status",
    "citation_status",
    "gate_c_status",
    "track_ready",
    "track_reason",
]


def _require_columns(df: pd.DataFrame, required: set[str], name: str) -> None:
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"{name} missing required columns: {missing}")


def _assert_seizeit2_source(df: pd.DataFrame, name: str) -> None:
    if "source_dataset" not in df.columns or df.empty:
        return
    values = set(df["source_dataset"].dropna().astype(str).str.lower())
    bad = sorted(value for value in values if "seizeit2" not in value)
    if bad:
        raise ValueError(f"{name} contains non-SeizeIT2 source_dataset values: {bad[:5]}")


def apply_official_seizeit2_splits(
    df: pd.DataFrame,
    split_manifest: pd.DataFrame,
    *,
    match_columns: tuple[str, ...] = ("patient_id", "recording_id"),
    split_col: str = "split",
) -> pd.DataFrame:
    """Attach official split labels and fail closed on ambiguous manifests."""
    _require_columns(df, set(match_columns), "df")
    _require_columns(split_manifest, {*match_columns, split_col}, "split_manifest")
    duplicated = split_manifest.duplicated(list(match_columns), keep=False)
    if duplicated.any():
        examples = split_manifest.loc[duplicated, list(match_columns)].head(3).to_dict("records")
        raise ValueError(f"split_manifest contains duplicate keys, examples={examples}")
    splits = set(split_manifest[split_col].dropna().astype(str))
    invalid = sorted(splits - VALID_SPLITS)
    if invalid:
        raise ValueError(f"split_manifest contains invalid split labels: {invalid}")

    payload = split_manifest[list(match_columns) + [split_col]].copy()
    out = df.drop(columns=[split_col], errors="ignore").merge(
        payload,
        on=list(match_columns),
        how="left",
        validate="many_to_one",
        indicator=True,
    )
    missing = out["_merge"].ne("both")
    if missing.any():
        examples = out.loc[missing, list(match_columns)].head(3).to_dict("records")
        raise ValueError(
            "official split manifest does not cover all rows: "
            f"missing_rows={int(missing.sum())}, examples={examples}"
        )
    return out.drop(columns=["_merge"])


def _eligible_recordings_for_modality(
    recordings: pd.DataFrame,
    availability: pd.DataFrame,
    modality_track: str,
) -> tuple[pd.DataFrame, str, str]:
    available = availability.loc[availability["available"].fillna(False).astype(bool)].copy()
    grouped = (
        available.groupby(["patient_id", "recording_id"])["modality"]
        .apply(lambda values: sorted(set(values.astype(str))))
        .reset_index(name="available_modalities")
    )
    streams = recordings[["patient_id", "recording_id", "split"]].drop_duplicates().merge(
        grouped,
        on=["patient_id", "recording_id"],
        how="left",
    )
    streams["available_modalities"] = streams["available_modalities"].apply(
        lambda value: value if isinstance(value, list) else []
    )
    if modality_track == "multimodal":
        mask = streams["available_modalities"].apply(
            lambda values: len(set(values).intersection(SEIZEIT2_CORE_MODALITIES)) >= 2
        )
        required = ">=2 of ecg,acc,bte_eeg"
    else:
        mask = streams["available_modalities"].apply(lambda values: modality_track in values)
        required = modality_track
    eligible = streams.loc[mask].copy()
    available_text = (
        ",".join(sorted({modality for values in eligible["available_modalities"] for modality in values}))
        if not eligible.empty
        else ""
    )
    return eligible, required, available_text


def _count_events_for_streams(events: pd.DataFrame, streams: pd.DataFrame) -> int:
    if events.empty or streams.empty:
        return 0
    keys = streams[["patient_id", "recording_id"]].drop_duplicates()
    matched = events.merge(keys, on=["patient_id", "recording_id"], how="inner")
    return int(len(matched))


def _count_windows_for_streams(windows: pd.DataFrame | None, streams: pd.DataFrame) -> int | None:
    if windows is None:
        return None
    if windows.empty or streams.empty:
        return 0
    keys = streams[["patient_id", "recording_id"]].drop_duplicates()
    matched = windows.merge(keys, on=["patient_id", "recording_id"], how="inner")
    return int(len(matched))


def _split_values(recordings: pd.DataFrame) -> list[str]:
    values = recordings["split"].fillna("unassigned").astype(str).unique().tolist()
    ordered = [split for split in DEFAULT_SPLIT_ORDER if split in values]
    ordered.extend(sorted(split for split in values if split not in ordered))
    return ordered


def build_seizeit2_full_track_matrix(
    recordings_df: pd.DataFrame,
    events_df: pd.DataFrame,
    modality_availability_df: pd.DataFrame,
    *,
    windows_df: pd.DataFrame | None = None,
    official_splits_df: pd.DataFrame | None = None,
    split_match_columns: tuple[str, ...] = ("patient_id", "recording_id"),
    tasks: tuple[SeizeIT2TaskSpec, ...] = DEFAULT_SEIZEIT2_TASKS,
    modality_tracks: tuple[str, ...] = SEIZEIT2_TRACK_MODALITIES,
    result_status: str = "pre_gate_c_exploratory_not_citable",
    citation_status: str = "not_citable_pre_gate_c",
    gate_c_status: str = "not_started",
) -> pd.DataFrame:
    """Build a SeizeIT2 benchmark-track matrix without computing model results."""
    _require_columns(recordings_df, {"patient_id", "recording_id"}, "recordings_df")
    _require_columns(events_df, {"patient_id", "recording_id"}, "events_df")
    _require_columns(
        modality_availability_df,
        {"patient_id", "recording_id", "modality", "available"},
        "modality_availability_df",
    )
    if windows_df is not None:
        _require_columns(windows_df, {"patient_id", "recording_id"}, "windows_df")
        _assert_seizeit2_source(windows_df, "windows_df")
    _assert_seizeit2_source(recordings_df, "recordings_df")
    _assert_seizeit2_source(events_df, "events_df")
    _assert_seizeit2_source(modality_availability_df, "modality_availability_df")
    if citation_status == "citable_after_gate_c" and gate_c_status != "passed":
        raise ValueError("citable SeizeIT2 benchmark tracks require gate_c_status='passed'")

    recordings = recordings_df.copy()
    if official_splits_df is not None:
        recordings = apply_official_seizeit2_splits(
            recordings,
            official_splits_df,
            match_columns=split_match_columns,
        )
        official_split_status = "official_manifest_applied"
    else:
        if "split" not in recordings.columns:
            recordings["split"] = "unassigned"
            official_split_status = "missing_official_manifest"
        else:
            official_split_status = "preexisting_split_column_unverified"

    rows: list[dict[str, Any]] = []
    for split_name in _split_values(recordings):
        split_recordings = recordings.loc[recordings["split"].fillna("unassigned").astype(str).eq(split_name)]
        for modality_track in modality_tracks:
            eligible, required, available_text = _eligible_recordings_for_modality(
                split_recordings,
                modality_availability_df,
                modality_track,
            )
            patients = int(eligible["patient_id"].nunique()) if not eligible.empty else 0
            recording_count = int(eligible["recording_id"].nunique()) if not eligible.empty else 0
            event_count = _count_events_for_streams(events_df, eligible)
            sample_rows = _count_windows_for_streams(windows_df, eligible)
            ready = (
                official_split_status == "official_manifest_applied"
                and recording_count > 0
                and event_count > 0
            )
            reason = "track has official split, recordings, and events" if ready else "not ready: "
            if not ready:
                missing = []
                if official_split_status != "official_manifest_applied":
                    missing.append(official_split_status)
                if recording_count == 0:
                    missing.append("no eligible recordings for modality")
                if event_count == 0:
                    missing.append("no seizure events in eligible recordings")
                reason += "; ".join(missing)
            for task in tasks:
                rows.append(
                    {
                        "benchmark_family": "seizeit2_full_track",
                        "dataset": "seizeit2",
                        "split_name": split_name,
                        "task_name": task.task_name,
                        "task_type": task.task_type,
                        "leaderboard_task_type": task.leaderboard_task_type,
                        "horizon_name": task.horizon_name,
                        "sph_minutes": task.sph_minutes,
                        "sop_minutes": task.sop_minutes,
                        "score_level": task.score_level,
                        "event_unit": task.event_unit,
                        "modality_track": modality_track,
                        "required_modalities": required,
                        "available_modalities": available_text,
                        "patients": patients,
                        "recordings": recording_count,
                        "events": event_count,
                        "sample_rows": sample_rows,
                        "official_split_status": official_split_status,
                        "result_status": result_status,
                        "citation_status": citation_status,
                        "gate_c_status": gate_c_status,
                        "track_ready": bool(ready),
                        "track_reason": reason,
                    }
                )
    return pd.DataFrame(rows, columns=TRACK_COLUMNS)


def seizeit2_count_summary(
    recordings_df: pd.DataFrame,
    events_df: pd.DataFrame,
    modality_availability_df: pd.DataFrame,
    *,
    windows_df: pd.DataFrame | None = None,
    expected_counts: dict[str, int] | None = None,
) -> pd.DataFrame:
    """Summarize discovered counts and optionally compare to published expectations."""
    summary = {
        "patients": int(recordings_df["patient_id"].nunique()) if "patient_id" in recordings_df else 0,
        "recordings": int(recordings_df["recording_id"].nunique()) if "recording_id" in recordings_df else 0,
        "events": int(len(events_df)),
        "modality_rows": int(len(modality_availability_df)),
        "windows": int(len(windows_df)) if windows_df is not None else None,
    }
    rows = []
    for metric, observed in summary.items():
        expected = expected_counts.get(metric) if expected_counts else None
        if expected is None:
            status = "expected_count_not_provided"
        elif int(observed or 0) == int(expected):
            status = "matches_expected_count"
        else:
            status = "count_mismatch_document_filter_or_parser"
        rows.append(
            {
                "metric": metric,
                "observed": observed,
                "expected": expected,
                "count_status": status,
            }
        )
    return pd.DataFrame(rows)


def seizeit2_full_track_markdown(
    track_df: pd.DataFrame,
    count_summary: pd.DataFrame,
    *,
    title: str = "SeizeIT2 Full-Benchmark Track",
) -> str:
    def cell(value: object) -> str:
        if pd.isna(value):
            return ""
        if isinstance(value, float):
            if value.is_integer():
                return str(int(value))
            return f"{value:.3f}"
        return str(value)

    def table(df: pd.DataFrame) -> str:
        if df.empty:
            return "_No rows._"
        headers = [str(column) for column in df.columns]
        lines = [
            "| " + " | ".join(headers) + " |",
            "| " + " | ".join(["---"] * len(headers)) + " |",
        ]
        for _, row in df.iterrows():
            lines.append("| " + " | ".join(cell(row[column]) for column in df.columns) + " |")
        return "\n".join(lines)

    visible = [
        "split_name",
        "task_name",
        "task_type",
        "modality_track",
        "score_level",
        "events",
        "sample_rows",
        "track_ready",
        "track_reason",
    ]
    view = track_df[[column for column in visible if column in track_df.columns]]
    return "\n".join(
        [
            f"# {title}",
            "",
            "This is a benchmark-track readiness report, not a model result.",
            "It separates SeizeIT2 detection, short early-warning, and long-horizon forecasting.",
            "It must not be mixed with MSG long-horizon forecasting rows.",
            "",
            "## Count Summary",
            "",
            table(count_summary),
            "",
            "## Track Matrix",
            "",
            table(view),
            "",
            "Interpretation:",
            "",
            "- `track_ready` means the track has official split rows, eligible recordings, and events.",
            "- Citable model scores still require Gate C and completed label audit.",
            "- Missing modality tracks are explicit negative readiness findings, not hidden exclusions.",
        ]
    )
