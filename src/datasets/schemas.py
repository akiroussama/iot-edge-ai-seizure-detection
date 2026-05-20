from __future__ import annotations

import pandas as pd

from src.utils.validation import ColumnSpec, TableSchema, validate_no_null_ids, validate_table_schema, validate_time_order

METADATA_SCHEMA = TableSchema(
    name="metadata",
    columns=(
        ColumnSpec("patient_id", "string"),
        ColumnSpec("recording_id", "string"),
        ColumnSpec("center_id", "string", required=False, nullable=True),
        ColumnSpec("source_dataset", "string", required=False, nullable=True),
    ),
)

EVENTS_SCHEMA = TableSchema(
    name="events",
    columns=(
        ColumnSpec("patient_id", "string"),
        ColumnSpec("recording_id", "string"),
        ColumnSpec("seizure_start", "datetime"),
        ColumnSpec("seizure_end", "datetime"),
        ColumnSpec("seizure_type", "string", required=False, nullable=True),
        ColumnSpec("center_id", "string", required=False, nullable=True),
        ColumnSpec("source_dataset", "string", required=False, nullable=True),
    ),
)

RECORDINGS_SCHEMA = TableSchema(
    name="recordings",
    columns=(
        ColumnSpec("patient_id", "string"),
        ColumnSpec("recording_id", "string"),
        ColumnSpec("recording_start", "datetime"),
        ColumnSpec("recording_end", "datetime"),
        ColumnSpec("center_id", "string", required=False, nullable=True),
        ColumnSpec("source_dataset", "string", required=False, nullable=True),
    ),
)

WINDOWS_SCHEMA = TableSchema(
    name="windows",
    columns=(
        ColumnSpec("patient_id", "string"),
        ColumnSpec("recording_id", "string"),
        ColumnSpec("window_start", "datetime"),
        ColumnSpec("window_end", "datetime"),
        ColumnSpec("center_id", "string", required=False, nullable=True),
        ColumnSpec("source_dataset", "string", required=False, nullable=True),
        ColumnSpec("modalities_available", "string", required=False, nullable=True),
    ),
)

MODALITY_AVAILABILITY_SCHEMA = TableSchema(
    name="modality_availability",
    columns=(
        ColumnSpec("patient_id", "string"),
        ColumnSpec("recording_id", "string"),
        ColumnSpec("modality", "string"),
        ColumnSpec("available", "boolean"),
        ColumnSpec("sampling_rate", "numeric", required=False, nullable=True),
        ColumnSpec("channel_count", "numeric", required=False, nullable=True),
        ColumnSpec("notes", "string", required=False, nullable=True),
    ),
)

FEATURES_SCHEMA = TableSchema(
    name="features",
    columns=(
        ColumnSpec("patient_id", "string"),
        ColumnSpec("recording_id", "string"),
        ColumnSpec("window_start", "datetime"),
        ColumnSpec("window_end", "datetime"),
    ),
)

PREDICTIONS_SCHEMA = TableSchema(
    name="predictions",
    columns=(
        ColumnSpec("patient_id", "string"),
        ColumnSpec("window_start", "datetime"),
        ColumnSpec("window_end", "datetime"),
        ColumnSpec("risk_score", "numeric"),
        ColumnSpec("alarm", "boolean"),
        ColumnSpec("forecast_label", "boolean", required=False, nullable=True),
        ColumnSpec("is_excluded", "boolean", required=False, nullable=True),
        ColumnSpec("recording_id", "string", required=False, nullable=True),
    ),
)


def validate_metadata(df: pd.DataFrame, allow_empty: bool = False) -> None:
    validate_table_schema(df, METADATA_SCHEMA, allow_empty=allow_empty)
    validate_no_null_ids(df, ("patient_id", "recording_id"), "metadata")


def validate_events(df: pd.DataFrame, allow_empty: bool = True) -> None:
    validate_table_schema(df, EVENTS_SCHEMA, allow_empty=allow_empty)
    if not df.empty:
        validate_no_null_ids(df, ("patient_id", "recording_id"), "events")
        validate_time_order(df, "seizure_start", "seizure_end", "events")


def validate_recordings(df: pd.DataFrame, allow_empty: bool = False) -> None:
    validate_table_schema(df, RECORDINGS_SCHEMA, allow_empty=allow_empty)
    validate_no_null_ids(df, ("patient_id", "recording_id"), "recordings")
    if not df.empty:
        validate_time_order(df, "recording_start", "recording_end", "recordings")


def validate_windows(df: pd.DataFrame, allow_empty: bool = False) -> None:
    validate_table_schema(df, WINDOWS_SCHEMA, allow_empty=allow_empty)
    validate_no_null_ids(df, ("patient_id", "recording_id"), "windows")
    if not df.empty:
        validate_time_order(df, "window_start", "window_end", "windows")


def validate_modality_availability(df: pd.DataFrame, allow_empty: bool = False) -> None:
    validate_table_schema(df, MODALITY_AVAILABILITY_SCHEMA, allow_empty=allow_empty)
    validate_no_null_ids(df, ("patient_id", "recording_id", "modality"), "modality_availability")


def validate_features(df: pd.DataFrame, allow_empty: bool = False) -> None:
    validate_table_schema(df, FEATURES_SCHEMA, allow_empty=allow_empty)
    validate_no_null_ids(df, ("patient_id", "recording_id"), "features")
    if not df.empty:
        validate_time_order(df, "window_start", "window_end", "features")


def validate_predictions(df: pd.DataFrame, allow_empty: bool = False) -> None:
    validate_table_schema(df, PREDICTIONS_SCHEMA, allow_empty=allow_empty)
    validate_no_null_ids(df, ("patient_id",), "predictions")
    if not df.empty:
        validate_time_order(df, "window_start", "window_end", "predictions")
        scores = pd.to_numeric(df["risk_score"], errors="coerce")
        if ((scores < 0) | (scores > 1)).any():
            raise ValueError("predictions.risk_score must be in [0, 1]")
