from __future__ import annotations

import numpy as np
import pandas as pd

from src.utils.time import ensure_datetime


def _valid_predictions(predictions_df: pd.DataFrame) -> pd.DataFrame:
    df = predictions_df.copy()
    if "is_excluded" in df.columns:
        df = df.loc[~df["is_excluded"].fillna(False)]
    if df.empty:
        return df
    df["window_start"] = ensure_datetime(df["window_start"])
    df["window_end"] = ensure_datetime(df["window_end"])
    if "alarm" not in df.columns:
        if "risk_score" not in df.columns:
            raise ValueError("predictions_df must contain either alarm or risk_score")
        df["alarm"] = df["risk_score"] >= 0.5
    df["alarm"] = df["alarm"].astype(bool)
    return df


def _union_duration_seconds(intervals: list[tuple[pd.Timestamp, pd.Timestamp]]) -> float:
    if not intervals:
        return 0.0
    intervals = sorted(intervals, key=lambda x: x[0])
    total = 0.0
    cur_start, cur_end = intervals[0]
    for start, end in intervals[1:]:
        if start <= cur_end:
            cur_end = max(cur_end, end)
        else:
            total += (cur_end - cur_start).total_seconds()
            cur_start, cur_end = start, end
    total += (cur_end - cur_start).total_seconds()
    return float(total)


def _stream_group_columns(df: pd.DataFrame) -> list[str]:
    """Columns that define independent monitoring streams.

    Monitoring time must be summed across patients and recordings. Merging intervals globally
    would collapse simultaneous patients into one clock and inflate alarm-rate metrics.
    """
    cols = []
    if "patient_id" in df.columns:
        cols.append("patient_id")
    if "recording_id" in df.columns:
        cols.append("recording_id")
    return cols


def _sum_union_duration_by_stream(df: pd.DataFrame) -> float:
    if df.empty:
        return 0.0
    group_cols = _stream_group_columns(df)
    if not group_cols:
        intervals = list(zip(df["window_start"], df["window_end"], strict=False))
        return _union_duration_seconds(intervals)

    total = 0.0
    for _, group in df.groupby(group_cols, sort=False):
        intervals = list(zip(group["window_start"], group["window_end"], strict=False))
        total += _union_duration_seconds(intervals)
    return float(total)


def monitored_time_seconds(predictions_df: pd.DataFrame) -> float:
    """Total valid monitored time across independent patient/recording streams.

    Within each stream, overlapping windows are merged so short strides do not inflate
    denominators. Across different patients or recordings, durations are summed.
    """
    df = _valid_predictions(predictions_df)
    return _sum_union_duration_by_stream(df)


def time_in_warning(predictions_df: pd.DataFrame) -> float:
    """Fraction of valid monitored time spent in alarm state.

    Overlapping windows are merged before duration is computed, avoiding over-counting when
    stride is shorter than the window length.
    """
    df = _valid_predictions(predictions_df)
    total = monitored_time_seconds(df)
    if total <= 0:
        return float("nan")
    alarm_df = df.loc[df["alarm"]]
    return _sum_union_duration_by_stream(alarm_df) / total


def _alarm_episodes(df: pd.DataFrame) -> list[pd.DataFrame]:
    """Collapse consecutive alarm windows into episodes per patient.

    The gap threshold is inferred as 1.5x the median stride of all valid windows within a stream,
    not from alarm windows only. Inferring stride from alarm starts would merge sparse alarms across
    long silent gaps and undercount false alarm episodes.
    """
    df = _valid_predictions(df)
    episodes: list[pd.DataFrame] = []
    if df.empty:
        return episodes

    group_cols = _stream_group_columns(df)
    sort_cols = group_cols + ["window_start"] if group_cols else ["window_start"]
    sorted_df = df.sort_values(sort_cols)
    group_iter = sorted_df.groupby(group_cols, sort=False) if group_cols else [(None, sorted_df)]
    for _, stream in group_iter:
        alarms = stream.loc[stream["alarm"]].sort_values("window_start")
        if alarms.empty:
            continue
        stream_starts = stream["window_start"].drop_duplicates().sort_values().reset_index(drop=True)
        if len(stream_starts) > 1:
            stride = stream_starts.diff().dropna().median()
            max_gap = stride * 1.5 if pd.notna(stride) and stride > pd.Timedelta(0) else pd.Timedelta(0)
        else:
            max_gap = pd.Timedelta(0)
        cuts = [0]
        prev_end = alarms.iloc[0]["window_end"]
        for pos in range(1, len(alarms)):
            row = alarms.iloc[pos]
            if row["window_start"] - prev_end > max_gap:
                cuts.append(pos)
            prev_end = max(prev_end, row["window_end"])
        cuts.append(len(alarms))
        for a, b in zip(cuts[:-1], cuts[1:], strict=True):
            episodes.append(alarms.iloc[a:b])
    return episodes


def _episode_associated_with_event(
    episode: pd.DataFrame,
    events_df: pd.DataFrame,
    sph_minutes: float,
    sop_minutes: float,
) -> bool:
    sph = pd.Timedelta(minutes=sph_minutes)
    sop = pd.Timedelta(minutes=sop_minutes)
    patient_events = events_df.loc[events_df["patient_id"].eq(episode.iloc[0]["patient_id"])]
    if "recording_id" in episode.columns and "recording_id" in events_df.columns:
        patient_events = patient_events.loc[patient_events["recording_id"].eq(episode.iloc[0]["recording_id"])]
    if patient_events.empty:
        return False
    starts = ensure_datetime(patient_events["seizure_start"])
    for _, row in episode.iterrows():
        h0 = row["window_end"] + sph
        h1 = row["window_end"] + sph + sop
        if ((starts >= h0) & (starts < h1)).any():
            return True
    return False


def false_alarm_count(
    predictions_df: pd.DataFrame,
    events_df: pd.DataFrame,
    sph_minutes: float,
    sop_minutes: float,
) -> int:
    events = events_df.copy()
    if not events.empty:
        events["seizure_start"] = ensure_datetime(events["seizure_start"])
        events["seizure_end"] = ensure_datetime(events["seizure_end"])
    count = 0
    for episode in _alarm_episodes(predictions_df):
        if not _episode_associated_with_event(episode, events, sph_minutes, sop_minutes):
            count += 1
    return count


def false_alarm_rate_per_hour(
    predictions_df: pd.DataFrame,
    events_df: pd.DataFrame,
    sph_minutes: float,
    sop_minutes: float,
) -> float:
    hours = monitored_time_seconds(predictions_df) / 3600.0
    if hours <= 0:
        return float("nan")
    return false_alarm_count(predictions_df, events_df, sph_minutes, sop_minutes) / hours


def false_alarm_rate_per_day(
    predictions_df: pd.DataFrame,
    events_df: pd.DataFrame,
    sph_minutes: float,
    sop_minutes: float,
) -> float:
    days = monitored_time_seconds(predictions_df) / 86400.0
    if days <= 0:
        return float("nan")
    return false_alarm_count(predictions_df, events_df, sph_minutes, sop_minutes) / days


def median_lead_time(
    predictions_df: pd.DataFrame,
    events_df: pd.DataFrame,
    sph_minutes: float,
    sop_minutes: float,
) -> float:
    """Median seconds between the first valid alarm and seizure onset for forecasted events."""
    from src.metrics.event_metrics import event_forecast_details

    details = event_forecast_details(predictions_df, events_df, sph_minutes, sop_minutes)
    leads = [d["lead_time_seconds"] for d in details if d["forecasted"]]
    if not leads:
        return float("nan")
    return float(np.median(leads))
