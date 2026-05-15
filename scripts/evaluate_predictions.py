from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import argparse
import json

from src.metrics import (
    brier_score,
    event_level_sensitivity,
    expected_calibration_error,
    false_alarm_rate_per_day,
    false_alarm_rate_per_hour,
    median_lead_time,
    time_in_warning,
)
from src.utils.io import read_table


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--predictions", required=True)
    parser.add_argument("--events", required=True)
    parser.add_argument("--sph-minutes", type=float, required=True)
    parser.add_argument("--sop-minutes", type=float, required=True)
    args = parser.parse_args()
    preds = read_table(args.predictions)
    events = read_table(args.events)
    sens = event_level_sensitivity(preds, events, args.sph_minutes, args.sop_minutes)
    result = {
        **sens,
        "far_per_hour": false_alarm_rate_per_hour(preds, events, args.sph_minutes, args.sop_minutes),
        "far_per_day": false_alarm_rate_per_day(preds, events, args.sph_minutes, args.sop_minutes),
        "time_in_warning": time_in_warning(preds),
        "median_lead_time_seconds": median_lead_time(preds, events, args.sph_minutes, args.sop_minutes),
        "brier_score": brier_score(preds),
        "ece": expected_calibration_error(preds),
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
