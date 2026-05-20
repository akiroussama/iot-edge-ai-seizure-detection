from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.labeling.sph_sop import label_forecast_windows
from src.utils.io import read_table, write_table


def main() -> None:
    parser = argparse.ArgumentParser(description="Create SPH/SOP forecasting labels.")
    parser.add_argument("--windows", required=True)
    parser.add_argument("--events", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--sph-minutes", type=float, default=5)
    parser.add_argument("--sop-minutes", type=float, default=30)
    parser.add_argument("--postictal-exclusion-minutes", type=float, default=60)
    parser.add_argument(
        "--postictal-anchor",
        choices=["seizure_end", "seizure_start"],
        default="seizure_end",
        help="Anchor postictal exclusion to measured seizure_end or onset-only seizure_start.",
    )
    parser.add_argument("--include-ictal", action="store_true")
    parser.add_argument(
        "--allow-missing-recording-end",
        action="store_true",
        help="Legacy/debug only. Real-data labels should include recording_end for right-censoring.",
    )
    parser.add_argument(
        "--allow-imputed-seizure-end-postictal",
        action="store_true",
        help="Allow postictal exclusion from imputed seizure_end values. Prefer --postictal-anchor seizure_start for onset-only annotations.",
    )
    args = parser.parse_args()

    windows = read_table(args.windows)
    events = read_table(args.events)
    if (
        args.postictal_exclusion_minutes > 0
        and args.postictal_anchor == "seizure_end"
        and not args.allow_imputed_seizure_end_postictal
        and "seizure_end_imputed" in events.columns
        and events["seizure_end_imputed"].fillna(False).astype(bool).any()
    ):
        raise ValueError(
            "events contain imputed seizure_end values. Use --postictal-anchor seizure_start for onset-only "
            "annotations, or pass --allow-imputed-seizure-end-postictal after documenting why seizure_end "
            "anchoring is acceptable."
        )
    labeled = label_forecast_windows(
        windows,
        events,
        sph_minutes=args.sph_minutes,
        sop_minutes=args.sop_minutes,
        postictal_exclusion_minutes=args.postictal_exclusion_minutes,
        ictal_exclusion=not args.include_ictal,
        require_recording_end=not args.allow_missing_recording_end,
        postictal_anchor=args.postictal_anchor,
    )
    write_table(labeled, args.output)
    print(f"wrote {args.output} with {len(labeled)} windows")


if __name__ == "__main__":
    main()
