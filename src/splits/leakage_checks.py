from __future__ import annotations

import pandas as pd

from src.utils.time import ensure_datetime


def check_patient_leakage(df: pd.DataFrame, split_col: str = "split") -> dict[str, object]:
    """Detect patients appearing in more than one split."""
    issues = []
    for patient, g in df.groupby("patient_id"):
        splits = sorted(set(g[split_col].dropna()))
        if len(splits) > 1:
            issues.append({"patient_id": patient, "splits": splits})
    return {"has_leakage": bool(issues), "issues": issues}


def check_recording_overlap(df: pd.DataFrame, split_col: str = "split") -> dict[str, object]:
    """Detect recordings appearing in more than one split."""
    if not {"patient_id", "recording_id", split_col}.issubset(df.columns):
        return {"has_leakage": False, "issues": []}
    issues = []
    for (patient, recording), g in df.groupby(["patient_id", "recording_id"]):
        splits = sorted(set(g[split_col].dropna()))
        if len(splits) > 1:
            issues.append({"patient_id": patient, "recording_id": recording, "splits": splits})
    return {"has_leakage": bool(issues), "issues": issues}


def check_duplicate_windows(df: pd.DataFrame) -> dict[str, object]:
    """Detect duplicate patient/recording/window intervals."""
    cols = [c for c in ["patient_id", "recording_id", "window_start", "window_end"] if c in df.columns]
    if len(cols) < 3:
        return {"has_leakage": False, "issues": []}
    duplicates = df.loc[df.duplicated(cols, keep=False), cols]
    issues = duplicates.drop_duplicates().head(10).to_dict("records")
    return {"has_leakage": bool(issues), "issues": issues}


def check_postictal_label_contamination(df: pd.DataFrame) -> dict[str, object]:
    """Flag postictal positive labels that were not excluded."""
    required = {"forecast_label", "is_postictal", "is_excluded"}
    if not required.issubset(df.columns):
        return {"has_leakage": False, "issues": []}
    bad = df.loc[df["forecast_label"].astype(bool) & df["is_postictal"].astype(bool) & ~df["is_excluded"].astype(bool)]
    cols = [c for c in ["patient_id", "recording_id", "window_start", "window_end"] if c in bad.columns]
    return {"has_leakage": not bad.empty, "issues": bad[cols].head(10).to_dict("records")}


def check_temporal_leakage(
    df: pd.DataFrame,
    split_col: str = "split",
    split_order: tuple[str, ...] = ("train", "val", "test"),
) -> dict[str, object]:
    """Check pseudo-prospective ordering and split-boundary overlap per patient."""
    if "window_start" not in df.columns:
        raise ValueError("df must contain window_start")
    out = df.copy()
    out["window_start"] = ensure_datetime(out["window_start"])
    out["window_end"] = ensure_datetime(out["window_end"])
    issues = []
    for patient, g in out.groupby("patient_id"):
        for earlier_pos, earlier in enumerate(split_order[:-1]):
            later_candidates = split_order[earlier_pos + 1 :]
            earlier_rows = g.loc[g[split_col].eq(earlier)]
            if earlier_rows.empty:
                continue
            for later in later_candidates:
                later_rows = g.loc[g[split_col].eq(later)]
                if later_rows.empty:
                    continue
                earlier_end = earlier_rows["window_end"].max()
                later_start = later_rows["window_start"].min()
                if later_start < earlier_end:
                    issues.append(
                        {
                            "patient_id": patient,
                            "earlier_split": earlier,
                            "later_split": later,
                            "earlier_end_max": earlier_end,
                            "later_start_min": later_start,
                        }
                    )
    return {"has_leakage": bool(issues), "issues": issues}


def leakage_audit(df: pd.DataFrame, split_col: str = "split", split_strategy: str = "auto") -> str:
    lines = ["EpiTwin-Open leakage audit", "===========================", ""]
    if "patient_id" in df.columns and split_col in df.columns:
        patient = check_patient_leakage(df, split_col)
        if split_strategy == "patient_wise":
            lines.append(f"Patient-wise leakage: {patient['has_leakage']}")
        else:
            lines.append(
                "Patient overlap across splits: "
                f"{patient['has_leakage']} "
                f"(allowed only for temporal/within-patient analyses; strategy={split_strategy})"
            )
        if patient["issues"]:
            lines.append(str(patient["issues"][:10]))
        recording = check_recording_overlap(df, split_col)
        lines.append(
            "Recording overlap across splits: "
            f"{recording['has_leakage']} "
            f"(allowed only for temporal/within-recording analyses; strategy={split_strategy})"
        )
        if recording["issues"]:
            lines.append(str(recording["issues"][:10]))
    duplicates = check_duplicate_windows(df)
    lines.append(f"Duplicate window intervals: {duplicates['has_leakage']}")
    if duplicates["issues"]:
        lines.append(str(duplicates["issues"][:10]))
    postictal = check_postictal_label_contamination(df)
    lines.append(f"Postictal positive labels not excluded: {postictal['has_leakage']}")
    if postictal["issues"]:
        lines.append(str(postictal["issues"][:10]))
    if split_strategy in {"temporal", "auto"} and {"window_start", "window_end", split_col}.issubset(df.columns):
        temporal = check_temporal_leakage(df, split_col)
        lines.append(f"Temporal ordering/overlap leakage: {temporal['has_leakage']}")
        if temporal["issues"]:
            lines.append(str(temporal["issues"][:10]))
    elif {"window_start", "window_end", split_col}.issubset(df.columns):
        lines.append(
            "Temporal ordering/overlap leakage: not evaluated "
            f"(strategy={split_strategy}; use temporal splits for prospective claims)"
        )
    lines.append("Feature normalization leakage: not machine-checkable without fit metadata")
    lines.append("Future-information feature leakage: requires manual feature audit")
    return "\n".join(lines)
