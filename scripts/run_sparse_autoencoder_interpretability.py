#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.interpretability.sparse_autoencoder import (  # noqa: E402
    SparseAutoencoderConfig,
    build_sparse_autoencoder_report,
    sparse_autoencoder_markdown,
    table_records,
)
from src.utils.io import read_table, write_table  # noqa: E402


def _parse_columns(value: str | None) -> tuple[str, ...]:
    if not value:
        return ()
    columns = tuple(column.strip() for column in value.split(",") if column.strip())
    if not columns:
        raise argparse.ArgumentTypeError("column list cannot be empty")
    return columns


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Train a sparse autoencoder on activation tables and emit an "
            "interpretability dictionary plus post-hoc associations."
        )
    )
    parser.add_argument("--activations", required=True)
    parser.add_argument("--predictions", default=None)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--model-name", default="sparse_autoencoder")
    parser.add_argument(
        "--id-cols",
        type=_parse_columns,
        default=("patient_id", "recording_id", "window_start", "window_end"),
    )
    parser.add_argument("--activation-cols", type=_parse_columns, default=())
    parser.add_argument("--n-features", type=int, default=8)
    parser.add_argument("--fit-split", default="train")
    parser.add_argument("--split-col", default="split")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--epochs", type=int, default=250)
    parser.add_argument("--learning-rate", type=float, default=0.01)
    parser.add_argument("--sparsity-l1", type=float, default=0.01)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--activation-epsilon", type=float, default=1e-6)
    parser.add_argument("--title", default="Sparse Autoencoder Interpretability Report")
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    activations = read_table(args.activations)
    predictions = read_table(args.predictions) if args.predictions else None
    fit_split = None if str(args.fit_split).lower() in {"", "none", "all"} else args.fit_split
    config = SparseAutoencoderConfig(
        n_features=args.n_features,
        fit_split=fit_split,
        split_col=args.split_col,
        seed=args.seed,
        epochs=args.epochs,
        learning_rate=args.learning_rate,
        sparsity_l1=args.sparsity_l1,
        batch_size=args.batch_size,
        activation_epsilon=args.activation_epsilon,
        activation_cols=args.activation_cols,
    )
    report = build_sparse_autoencoder_report(
        activations,
        predictions=predictions,
        config=config,
        model_name=args.model_name,
        id_columns=args.id_cols,
    )

    out_dir = Path(args.out_dir)
    write_table(report.scores, out_dir / "sae_feature_scores.csv")
    write_table(report.dictionary, out_dir / "sae_dictionary.csv")
    write_table(report.associations, out_dir / "sae_associations.csv")
    write_table(report.manifest, out_dir / "sae_manifest.csv")
    payload = {
        "metadata": report.metadata,
        "dictionary": table_records(report.dictionary),
        "associations": table_records(report.associations),
    }
    (out_dir / "sae_report.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    (out_dir / "sae_report.md").write_text(
        sparse_autoencoder_markdown(report, title=args.title),
        encoding="utf-8",
    )
    print(json.dumps({"out_dir": str(out_dir), **report.metadata}, indent=2))


if __name__ == "__main__":
    main()
