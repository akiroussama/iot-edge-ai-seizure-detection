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
    "time_to_next_seizure_seconds",
    "time_since_last_seizure_seconds",
}


def _generic_feature_columns(df: pd.DataFrame) -> list[str]:
    return [
        col
        for col in df.columns
        if col not in DEFAULT_ID_COLUMNS and pd.api.types.is_numeric_dtype(df[col])
    ]


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
    args = parser.parse_args()

    features = read_table(args.features)
    if args.rule == "hr_tachycardia":
        raw_score = ecg_tachycardia_score(features, hr_col="hr_mean")
    elif args.rule == "acc_energy":
        raw_score = acc_energy_score(features, energy_col="acc_energy")
    else:
        raw_score = generic_zscore_anomaly(features, args.feature_cols or _generic_feature_columns(features))

    raw_score = pd.to_numeric(raw_score, errors="coerce")
    preds = features.copy()
    preds["risk_score"] = normalize_score(raw_score).fillna(0.0).astype(float)
    valid_mask = ~preds.get("is_excluded", pd.Series(False, index=preds.index)).fillna(False).astype(bool)
    evidence_mask = raw_score.notna() & np.isfinite(raw_score.astype(float))
    if args.patient_specific_threshold:
        calibration_rows = preds.loc[valid_mask & evidence_mask]
        if calibration_rows.empty:
            preds["patient_threshold"] = np.nan
            preds["alarm"] = False
        else:
            thresholds = patient_specific_quantile_thresholds(calibration_rows, args.target_tiw)
            preds = apply_patient_thresholds(preds, thresholds)
    else:
        threshold = quantile_threshold(preds.loc[valid_mask & evidence_mask, "risk_score"], args.target_tiw)
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
        }
    )


if __name__ == "__main__":
    main()
