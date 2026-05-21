#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.models.supervised_ladder import (  # noqa: E402
    LADDER_MODEL_SPECS,
    SupervisedLadderConfig,
    derive_model_seed,
    table_records,
    train_supervised_ladder,
)
from src.utils.io import read_table, write_table  # noqa: E402


def _parse_reference(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("--reference-predictions must be formatted as NAME=PATH")
    name, path = value.split("=", maxsplit=1)
    name = name.strip()
    if not name:
        raise argparse.ArgumentTypeError("reference name cannot be empty")
    return name, Path(path)


def _parse_feature_cols(value: str | None) -> tuple[str, ...]:
    if not value:
        return ()
    return tuple(item.strip() for item in value.split(",") if item.strip())


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Train controlled supervised ladder rungs and emit standardized predictions."
    )
    parser.add_argument("--features", required=True)
    parser.add_argument(
        "--reference-predictions",
        required=True,
        type=_parse_reference,
        help="Required null/reference comparator, formatted as NAME=PATH.",
    )
    parser.add_argument("--out-dir", required=True)
    parser.add_argument(
        "--model",
        action="append",
        choices=sorted(LADDER_MODEL_SPECS),
        default=None,
        help="Model rung to run. Repeatable. Defaults to logistic_regression.",
    )
    parser.add_argument("--feature-cols", default=None, help="Comma-separated feature columns.")
    parser.add_argument("--split-col", default="split")
    parser.add_argument("--train-split", default="train")
    parser.add_argument("--val-split", default="val")
    parser.add_argument("--target-col", default="forecast_label")
    parser.add_argument("--target-tiw", type=float, default=0.1)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--learning-rate", type=float, default=0.05)
    parser.add_argument("--weight-decay", type=float, default=1e-4)
    parser.add_argument("--hidden-dim", type=int, default=32)
    parser.add_argument("--batch-size", type=int, default=256)
    parser.add_argument("--n-estimators", type=int, default=25)
    parser.add_argument("--sequence-length", type=int, default=8)
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    reference_name, reference_path = args.reference_predictions
    models = args.model or ["logistic_regression"]
    if len(set(models)) != len(models):
        parser.error("--model values must be unique")
    feature_cols = _parse_feature_cols(args.feature_cols)
    features = read_table(args.features)
    reference = read_table(reference_path)
    configs = [
        SupervisedLadderConfig(
            model_name=model,
            split_col=args.split_col,
            train_split=args.train_split,
            val_split=args.val_split,
            target_col=args.target_col,
            target_tiw=args.target_tiw,
            seed=args.seed if len(models) == 1 else derive_model_seed(args.seed, model, index),
            feature_cols=feature_cols,
            epochs=args.epochs,
            learning_rate=args.learning_rate,
            weight_decay=args.weight_decay,
            hidden_dim=args.hidden_dim,
            batch_size=args.batch_size,
            n_estimators=args.n_estimators,
            sequence_length=args.sequence_length,
        )
        for index, model in enumerate(models)
    ]
    predictions, manifest = train_supervised_ladder(
        features,
        reference_predictions=reference,
        reference_name=reference_name,
        configs=configs,
    )
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for model_name, table in predictions.items():
        write_table(table, out_dir / f"{model_name}_predictions.csv")
    write_table(manifest, out_dir / "supervised_ladder_manifest.csv")
    (out_dir / "supervised_ladder_manifest.json").write_text(
        json.dumps(table_records(manifest), indent=2),
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "out_dir": str(out_dir),
                "models": models,
                "reference_name": reference_name,
                "rows": int(len(features)),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
