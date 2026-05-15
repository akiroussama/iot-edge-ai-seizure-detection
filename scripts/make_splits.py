from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.splits.leakage_checks import leakage_audit
from src.splits.patient_split import patient_wise_split
from src.splits.recording_split import recording_wise_split
from src.splits.temporal_split import temporal_split_per_patient
from src.utils.io import read_table, write_table


def main() -> None:
    parser = argparse.ArgumentParser(description="Create leakage-aware benchmark splits.")
    parser.add_argument("--labels", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--audit-out", required=True)
    parser.add_argument(
        "--strategy",
        choices=["temporal", "patient_wise", "recording_wise"],
        default="temporal",
    )
    parser.add_argument("--train-fraction", type=float, default=0.7)
    parser.add_argument("--val-fraction", type=float, default=0.1)
    parser.add_argument("--test-fraction", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--no-purge-overlap", action="store_true")
    parser.add_argument(
        "--temporal-unit",
        choices=["window", "recording"],
        default="window",
        help="When strategy=temporal, split individual windows or whole recordings.",
    )
    args = parser.parse_args()

    labels = read_table(args.labels)
    if args.strategy == "temporal":
        split = temporal_split_per_patient(
            labels,
            train_fraction=args.train_fraction,
            val_fraction=args.val_fraction,
            purge_overlap=not args.no_purge_overlap,
            split_unit=args.temporal_unit,
        )
    elif args.strategy == "patient_wise":
        split = patient_wise_split(
            labels,
            test_fraction=args.test_fraction,
            val_fraction=args.val_fraction,
            seed=args.seed,
        )
    else:
        split = recording_wise_split(
            labels,
            test_fraction=args.test_fraction,
            val_fraction=args.val_fraction,
            seed=args.seed,
        )

    write_table(split, args.out)
    audit_strategy = args.strategy if args.strategy != "temporal" else f"temporal_{args.temporal_unit}"
    audit = leakage_audit(split, split_strategy=audit_strategy)
    Path(args.audit_out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.audit_out).write_text(audit, encoding="utf-8")
    print({"out": args.out, "audit_out": args.audit_out, "split_counts": split["split"].value_counts().to_dict()})


if __name__ == "__main__":
    main()
