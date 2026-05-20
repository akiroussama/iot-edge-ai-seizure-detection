from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import pandas as pd

ColumnKind = Literal["string", "datetime", "numeric", "boolean"]


@dataclass(frozen=True)
class ColumnSpec:
    name: str
    kind: ColumnKind | None = None
    required: bool = True
    nullable: bool = False


@dataclass(frozen=True)
class TableSchema:
    name: str
    columns: tuple[ColumnSpec, ...]

    @property
    def required_columns(self) -> set[str]:
        return {col.name for col in self.columns if col.required}


def _validate_kind(series: pd.Series, kind: ColumnKind, table_name: str, column_name: str) -> None:
    values = series.dropna()
    if values.empty:
        return
    if kind == "datetime":
        converted = pd.to_datetime(values, errors="coerce")
        if converted.isna().any():
            raise ValueError(f"{table_name}.{column_name} contains non-datetime values")
    elif kind == "numeric":
        converted = pd.to_numeric(values, errors="coerce")
        if converted.isna().any():
            raise ValueError(f"{table_name}.{column_name} contains non-numeric values")
    elif kind == "boolean":
        if not pd.api.types.is_bool_dtype(values):
            valid = values.isin([True, False, 0, 1])
            if not valid.all():
                raise ValueError(f"{table_name}.{column_name} contains non-boolean values")
    elif kind == "string":
        if values.astype(str).str.len().eq(0).any():
            raise ValueError(f"{table_name}.{column_name} contains empty string identifiers")


def validate_table_schema(df: pd.DataFrame, schema: TableSchema, allow_empty: bool = False) -> None:
    """Validate required columns, nullability, and lightweight dtype constraints."""
    missing = schema.required_columns - set(df.columns)
    if missing:
        raise ValueError(f"{schema.name} missing required columns: {sorted(missing)}")
    if df.empty and not allow_empty:
        raise ValueError(f"{schema.name} is empty")
    for spec in schema.columns:
        if spec.name not in df.columns:
            continue
        if not spec.nullable and df[spec.name].isna().any():
            raise ValueError(f"{schema.name}.{spec.name} contains null values")
        if spec.kind and not df.empty:
            _validate_kind(df[spec.name], spec.kind, schema.name, spec.name)


def validate_time_order(
    df: pd.DataFrame,
    start_col: str,
    end_col: str,
    table_name: str,
    allow_equal: bool = False,
) -> None:
    """Validate start/end interval ordering for clinical event or window tables."""
    if start_col not in df.columns or end_col not in df.columns:
        raise ValueError(f"{table_name} must contain {start_col} and {end_col}")
    start = pd.to_datetime(df[start_col], errors="coerce")
    end = pd.to_datetime(df[end_col], errors="coerce")
    bad_time = start.isna() | end.isna()
    if bad_time.any():
        raise ValueError(f"{table_name} has invalid timestamps in {start_col}/{end_col}")
    bad_order = end < start if allow_equal else end <= start
    if bad_order.any():
        raise ValueError(f"{table_name} contains non-positive intervals")


def validate_no_null_ids(df: pd.DataFrame, id_columns: tuple[str, ...], table_name: str) -> None:
    for col in id_columns:
        if col not in df.columns:
            raise ValueError(f"{table_name} missing identifier column: {col}")
        if df[col].isna().any() or df[col].astype(str).str.len().eq(0).any():
            raise ValueError(f"{table_name}.{col} contains null or empty identifiers")
