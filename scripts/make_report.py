from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import argparse
from pathlib import Path

import pandas as pd

from src.baselines.random_rate_matched import generate_random_rate_matched_alarms
from src.datasets.seizeit2_loader import make_synthetic_seizeit2_tables
from src.labeling.sph_sop import label_forecast_windows
from src.metrics import (
    brier_score,
    event_level_sensitivity,
    expected_calibration_error,
    false_alarm_rate_per_day,
    false_alarm_rate_per_hour,
    median_lead_time,
    time_in_warning,
)
from src.reports.summary_tables import dataset_summary, label_distribution
from src.splits.leakage_checks import leakage_audit
from src.splits.temporal_split import temporal_split_per_patient
from src.utils.io import write_table


def _markdown_table(df: pd.DataFrame) -> str:
    """Render a small dataframe as GitHub-flavored markdown without optional tabulate."""
    if df.empty:
        return "_No rows._"
    headers = [str(c) for c in df.columns]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for _, row in df.iterrows():
        values = [str(row[col]) for col in df.columns]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--synthetic", action="store_true")
    parser.add_argument("--out-dir", default="reports")
    parser.add_argument("--sph-minutes", type=float, default=5)
    parser.add_argument("--sop-minutes", type=float, default=30)
    args = parser.parse_args()
    if not args.synthetic:
        raise SystemExit("v0.1 report supports --synthetic. Dataset-specific reports come next.")

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    metadata, windows, events = make_synthetic_seizeit2_tables()
    labeled = label_forecast_windows(windows, events, args.sph_minutes, args.sop_minutes, postictal_exclusion_minutes=5)
    split = temporal_split_per_patient(labeled)
    preds = generate_random_rate_matched_alarms(split, 0.1, seed=42)

    write_table(dataset_summary(windows, events), out_dir / "dataset_summary.csv")
    write_table(label_distribution(labeled), out_dir / "label_distribution.csv")

    sens = event_level_sensitivity(preds, events, args.sph_minutes, args.sop_minutes)
    baseline = pd.DataFrame(
        [
            {
                "baseline": "random_rate_matched",
                "horizon": f"SPH {args.sph_minutes:g} / SOP {args.sop_minutes:g}",
                "sensitivity": sens["sensitivity"],
                "n_events": sens["n_events"],
                "far_per_hour": false_alarm_rate_per_hour(preds, events, args.sph_minutes, args.sop_minutes),
                "far_per_day": false_alarm_rate_per_day(preds, events, args.sph_minutes, args.sop_minutes),
                "time_in_warning": time_in_warning(preds),
                "median_lead_time_seconds": median_lead_time(preds, events, args.sph_minutes, args.sop_minutes),
                "brier_score": brier_score(preds),
                "ece": expected_calibration_error(preds),
            }
        ]
    )
    write_table(baseline, out_dir / "baseline_results.csv")
    (out_dir / "leakage_audit.txt").write_text(
        leakage_audit(split, split_strategy="temporal"),
        encoding="utf-8",
    )
    md = f"""# EpiTwin-Open 48h milestone

## Scope

This v0.1 milestone implements leakage-safe SPH/SOP labeling, clinical metrics, temporal splitting, random rate-matched sanity baseline, and report generation.

## Synthetic-only disclaimer

The table below is generated from a toy synthetic fixture. It is useful for software verification only and is not clinical evidence.

## Task definitions

- Detection: is a seizure happening now?
- Early warning: is there a near-immediate warning signal before clinical manifestation?
- Short-horizon forecasting: is a seizure likely in the next minutes under SPH/SOP?
- Long-horizon forecasting: is risk elevated over an hour/day scale?

## SPH/SOP

For a window ending at `t`, the positive forecasting interval is `[t + SPH, t + SPH + SOP)`.

## Metrics

- Event sensitivity: fraction of seizure events with at least one valid alarm whose SPH/SOP interval contains the seizure onset.
- FAR/day: false alarm episodes per valid monitored day.
- Time-in-Warning: fraction of valid monitored time covered by alarm windows.
- Lead time: time from first associated alarm window end to seizure onset.
- Brier/ECE: calibration checks on valid, non-excluded windows.

## Synthetic smoke-test result

{_markdown_table(baseline)}

## Requires real data

- SeizeIT2 and My Seizure Gauge raw-file parsing must be verified locally.
- SPH/SOP labels around real seizures must be manually audited.
- Splits must be frozen before model selection.
- No paper claim can use the synthetic result above.

## Next intervention

1. Place real SeizeIT2 and My Seizure Gauge files under `data/raw/`.
2. Run parser inspection and generate canonical events/windows/labels.
3. Manually audit 5-10 seizure timelines before any A100 run.
4. Freeze splits and rerun the leakage audit before reporting scores.
"""
    (out_dir / "48h_milestone.md").write_text(md, encoding="utf-8")
    print(f"wrote report files to {out_dir}")


if __name__ == "__main__":
    main()
