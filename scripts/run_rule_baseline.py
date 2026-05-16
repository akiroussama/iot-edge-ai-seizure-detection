#!/usr/bin/env python
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import numpy as np
import pandas as pd

from src.baselines.simple_rules import acc_energy_score, ecg_tachycardia_score, generic_zscore_anomaly, normalize_score
from src.calibration.thresholding import apply_patient_thresholds, patient_specific_quantile_thresholds, quantile_threshold
from src.utils.io import read_table, write_table

DEFAULT_ID_COLUMNS = {
    "patient_id",
    "recording_id",
    "window_start",
    "window_end",
    "forecast_label",
    "is_ictal",
    "is_postictal",
    "is_excluded",
    "alarm",
    "risk_score",
    "split",
    "feature_recordings_processed",
    "time_to_next_seizure_seconds",
    "time_since_last_seizure_seconds",
}


def _generic_feature_columns(df: pd.DataFrame) -> list[str]:
    return [
        col
        for col in df.columns
        if col not in DEFAULT_ID_COLUMNS and pd.api.types.is_numeric_dtype(df[col])
    ]


def _split_mask(df: pd.DataFrame, split_name: str | None) -> pd.Series | None:
    if split_name is None:
        return None
    if "split" not in df.columns:
        raise ValueError(f"split {split_name!r} requested but features table has no split column")
    return df["split"].astype(str).eq(split_name)


def _default_existing_split(df: pd.DataFrame, requested: str | None, default: str) -> str | None:
    if requested is not None:
        return requested
    if "split" not in df.columns:
        return None
    values = set(df["split"].dropna().astype(str))
    return default if default in values else None


def main() -> None:
    parser = argparse.ArgumentParser(description="Run transparent feature-rule baselines.")
    parser.add_argument("--features", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument(
        "--rule",
        choices=["hr_tachycardia", "acc_energy", "generic_zscore"],
        default="generic_zscore",
    )
    parser.add_argument("--feature-cols", nargs="*", default=None)
    parser.add_argument("--target-tiw", type=float, default=0.1)
    parser.add_argument("--patient-specific-threshold", action="store_true")
    parser.add_argument(
        "--score-fit-split",
        default=None,
        help="Split used to fit robust feature statistics and score normalization. Defaults to train when available.",
    )
    parser.add_argument(
        "--threshold-split",
        default=None,
        help="Split used to select alarm threshold. Defaults to val when available.",
    )
    parser.add_argument(
        "--reference-scope",
        choices=["patient", "population"],
        default="patient",
        help="Reference for robust feature statistics. 'population' pools all "
        "fit-split rows so held-out patients stay scorable on patient-wise splits.",
    )
    args = parser.parse_args()

    features = read_table(args.features)
    score_fit_split = _default_existing_split(features, args.score_fit_split, "train")
    threshold_split = _default_existing_split(features, args.threshold_split, "val")
    score_reference_mask = _split_mask(features, score_fit_split)
    if args.rule == "hr_tachycardia":
        raw_score = ecg_tachycardia_score(
            features,
            hr_col="hr_mean",
            reference_mask=score_reference_mask,
            reference_scope=args.reference_scope,
        )
    elif args.rule == "acc_energy":
        raw_score = acc_energy_score(
            features,
            energy_col="acc_energy",
            reference_mask=score_reference_mask,
            reference_scope=args.reference_scope,
        )
    else:
        raw_score = generic_zscore_anomaly(
            features,
            args.feature_cols or _generic_feature_columns(features),
            reference_mask=score_reference_mask,
            reference_scope=args.reference_scope,
        )

    raw_score = pd.to_numeric(raw_score, errors="coerce")
    preds = features.copy()
    preds["risk_score"] = normalize_score(raw_score, reference_mask=score_reference_mask).fillna(0.0).astype(float)
    preds["score_fit_split"] = score_fit_split or "all"
    preds["threshold_source_split"] = threshold_split or "all"
    preds["reference_scope"] = args.reference_scope
    valid_mask = ~preds.get("is_excluded", pd.Series(False, index=preds.index)).fillna(False).astype(bool)
    evidence_mask = raw_score.notna() & np.isfinite(raw_score.astype(float))
    threshold_mask = _split_mask(preds, threshold_split)
    if threshold_mask is None:
        threshold_mask = pd.Series(True, index=preds.index)
    if args.patient_specific_threshold:
        calibration_rows = preds.loc[valid_mask & evidence_mask & threshold_mask]
        if calibration_rows.empty:
            raise ValueError(
                f"threshold split {threshold_split or 'all'} has no valid evidence rows; "
                "refusing silent no-alarm fallback"
            )
        else:
            thresholds = patient_specific_quantile_thresholds(calibration_rows, args.target_tiw)
            preds = apply_patient_thresholds(preds, thresholds)
    else:
        if not (valid_mask & evidence_mask & threshold_mask).any():
            raise ValueError(
                f"threshold split {threshold_split or 'all'} has no valid evidence rows; "
                "refusing silent no-alarm fallback"
            )
        threshold = quantile_threshold(preds.loc[valid_mask & evidence_mask & threshold_mask, "risk_score"], args.target_tiw)
        preds["alarm_threshold"] = threshold
        preds["alarm"] = preds["risk_score"].astype(float) >= threshold
    preds.loc[~valid_mask | ~evidence_mask, "alarm"] = False
    write_table(preds, args.out)
    print(
        {
            "out": args.out,
            "rule": args.rule,
            "rows": len(preds),
            "alarms": int(preds["alarm"].sum()),
            "target_tiw": args.target_tiw,
            "score_fit_split": score_fit_split or "all",
            "threshold_source_split": threshold_split or "all",
            "reference_scope": args.reference_scope,
        }
    )


if __name__ == "__main__":
    main()
