from __future__ import annotations

import pandas as pd


def ensure_datetime(series: pd.Series) -> pd.Series:
    """Return a timezone-naive pandas datetime series.

    Clinical recordings often mix strings, pandas timestamps, or numpy datetimes. This helper
    normalizes those inputs while preserving relative timing.
    """
    out = pd.to_datetime(series, errors="coerce")
    if getattr(out.dt, "tz", None) is not None:
        out = out.dt.tz_convert(None)
    return out


def seconds(delta: pd.Series) -> pd.Series:
    """Convert a pandas timedelta series to seconds."""
    return delta.dt.total_seconds()
