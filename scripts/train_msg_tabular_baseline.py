#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import math
import random
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import numpy as np
import pandas as pd

from src.calibration.thresholding import quantile_threshold
from src.utils.io import read_table, write_table

LEAKAGE_OR_ID_COLUMNS = {
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
    "score_fit_split",
    "threshold_source_split",
    "alarm_threshold",
    "patient_threshold",
}


def _select_feature_columns(df: pd.DataFrame, requested: list[str] | None) -> list[str]:
    if requested:
        missing = [col for col in requested if col not in df.columns]
        if missing:
            raise ValueError(f"requested feature columns are missing: {missing}")
        return requested
    return [
        col
        for col in df.columns
        if col not in LEAKAGE_OR_ID_COLUMNS and pd.api.types.is_numeric_dtype(df[col])
    ]


def _split_mask(df: pd.DataFrame, split_col: str, split_name: str) -> pd.Series:
    if split_col not in df.columns:
        raise ValueError(f"features table must contain split column {split_col!r}")
    return df[split_col].astype(str).eq(split_name)


def _valid_evidence_mask(df: pd.DataFrame, feature_cols: list[str]) -> pd.Series:
    valid = ~df.get("is_excluded", pd.Series(False, index=df.index)).fillna(False).astype(bool)
    evidence = df[feature_cols].apply(pd.to_numeric, errors="coerce").notna().any(axis=1)
    return valid & evidence


def _fit_preprocessor(train_df: pd.DataFrame, feature_cols: list[str]) -> dict[str, np.ndarray]:
    values = train_df[feature_cols].apply(pd.to_numeric, errors="coerce")
    medians = values.median(axis=0).fillna(0.0).to_numpy(dtype=np.float32)
    filled = values.fillna(dict(zip(feature_cols, medians, strict=True)))
    means = filled.mean(axis=0).to_numpy(dtype=np.float32)
    scales = filled.std(axis=0).replace(0.0, 1.0).fillna(1.0).to_numpy(dtype=np.float32)
    return {"medians": medians, "means": means, "scales": scales}


def _transform(df: pd.DataFrame, feature_cols: list[str], preprocessor: dict[str, np.ndarray]) -> np.ndarray:
    values = df[feature_cols].apply(pd.to_numeric, errors="coerce")
    medians = preprocessor["medians"]
    values = values.fillna(dict(zip(feature_cols, medians, strict=True))).to_numpy(dtype=np.float32)
    return (values - preprocessor["means"]) / preprocessor["scales"]


def _make_model(torch: Any, input_dim: int, hidden_dim: int, dropout: float) -> Any:
    return torch.nn.Sequential(
        torch.nn.Linear(input_dim, hidden_dim),
        torch.nn.GELU(),
        torch.nn.Dropout(dropout),
        torch.nn.Linear(hidden_dim, hidden_dim),
        torch.nn.GELU(),
        torch.nn.Linear(hidden_dim, 1),
    )


def _set_seed(torch: Any, seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def _batches(torch: Any, x: Any, y: Any, batch_size: int, seed: int):
    order = torch.randperm(len(x), generator=torch.Generator().manual_seed(seed))
    for start in range(0, len(x), batch_size):
        idx = order[start : start + batch_size]
        yield x[idx], y[idx]


def main() -> None:
    parser = argparse.ArgumentParser(description="Train a CPU tabular MSG forecasting baseline.")
    parser.add_argument("--features", required=True)
    parser.add_argument("--out", required=True, help="Predictions table path.")
    parser.add_argument("--model-out", default=None)
    parser.add_argument("--metrics-out", default=None)
    parser.add_argument("--feature-cols", nargs="*", default=None)
    parser.add_argument("--split-col", default="split")
    parser.add_argument("--train-split", default="train")
    parser.add_argument("--val-split", default="val")
    parser.add_argument("--target-col", default="forecast_label")
    parser.add_argument("--target-tiw", type=float, default=0.1)
    parser.add_argument("--epochs", type=int, default=200)
    parser.add_argument("--batch-size", type=int, default=512)
    parser.add_argument("--hidden-dim", type=int, default=32)
    parser.add_argument("--dropout", type=float, default=0.1)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--weight-decay", type=float, default=1e-4)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    try:
        import torch
    except Exception as exc:  # pragma: no cover - depends on optional extra
        raise SystemExit("Install or run with the torch extra to train this baseline.") from exc

    _set_seed(torch, args.seed)
    features = read_table(args.features)
    if args.target_col not in features.columns:
        raise ValueError(f"features table must contain target column {args.target_col!r}")
    feature_cols = _select_feature_columns(features, args.feature_cols)
    if not feature_cols:
        raise ValueError("no numeric, non-leakage feature columns found")

    valid_evidence = _valid_evidence_mask(features, feature_cols)
    train_mask = valid_evidence & _split_mask(features, args.split_col, args.train_split)
    val_mask = valid_evidence & _split_mask(features, args.split_col, args.val_split)
    if not train_mask.any():
        raise ValueError(f"train split {args.train_split!r} has no valid feature rows")
    if not val_mask.any():
        raise ValueError(f"validation split {args.val_split!r} has no valid feature rows")

    train_df = features.loc[train_mask].copy()
    preprocessor = _fit_preprocessor(train_df, feature_cols)
    x_train = torch.tensor(_transform(train_df, feature_cols, preprocessor), dtype=torch.float32)
    y_train = torch.tensor(train_df[args.target_col].astype(float).to_numpy(), dtype=torch.float32)
    val_df = features.loc[val_mask].copy()
    x_val = torch.tensor(_transform(val_df, feature_cols, preprocessor), dtype=torch.float32)
    y_val = torch.tensor(val_df[args.target_col].astype(float).to_numpy(), dtype=torch.float32)

    positives = float(y_train.sum().item())
    negatives = float(len(y_train) - positives)
    pos_weight = torch.tensor([negatives / max(positives, 1.0)], dtype=torch.float32)
    model = _make_model(torch, x_train.shape[1], args.hidden_dim, args.dropout)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    criterion = torch.nn.BCEWithLogitsLoss(pos_weight=pos_weight)

    best_state = None
    best_val_loss = math.inf
    for epoch in range(args.epochs):
        model.train()
        for xb, yb in _batches(torch, x_train, y_train, args.batch_size, args.seed + epoch):
            optimizer.zero_grad(set_to_none=True)
            logits = model(xb).squeeze(-1)
            loss = criterion(logits, yb)
            loss.backward()
            optimizer.step()
        model.eval()
        with torch.no_grad():
            val_loss = float(criterion(model(x_val).squeeze(-1), y_val).item())
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_state = {key: value.detach().cpu().clone() for key, value in model.state_dict().items()}

    if best_state is not None:
        model.load_state_dict(best_state)

    all_evidence = _valid_evidence_mask(features, feature_cols)
    preds = features.copy()
    preds["risk_score"] = 0.0
    preds["alarm"] = False
    if all_evidence.any():
        x_all = torch.tensor(_transform(preds.loc[all_evidence], feature_cols, preprocessor), dtype=torch.float32)
        model.eval()
        with torch.no_grad():
            risk = torch.sigmoid(model(x_all).squeeze(-1)).cpu().numpy()
        preds.loc[all_evidence, "risk_score"] = risk.astype(float)

    threshold_rows = preds.loc[val_mask & all_evidence]
    if threshold_rows.empty:
        raise ValueError(f"validation split {args.val_split!r} has no threshold rows")
    threshold = quantile_threshold(threshold_rows["risk_score"], args.target_tiw)
    preds["alarm_threshold"] = threshold
    preds["alarm"] = preds["risk_score"].astype(float) >= threshold
    preds.loc[~all_evidence, "alarm"] = False
    preds["score_fit_split"] = args.train_split
    preds["threshold_source_split"] = args.val_split
    preds["model_name"] = "msg_tabular_mlp"
    write_table(preds, args.out)

    metadata: dict[str, Any] = {
        "features": args.features,
        "out": args.out,
        "feature_cols": feature_cols,
        "rows": int(len(preds)),
        "valid_evidence_rows": int(all_evidence.sum()),
        "train_rows": int(train_mask.sum()),
        "val_rows": int(val_mask.sum()),
        "train_positives": int(y_train.sum().item()),
        "val_positives": int(y_val.sum().item()),
        "target_tiw": args.target_tiw,
        "alarm_threshold": float(threshold),
        "best_val_loss": best_val_loss,
        "epochs": args.epochs,
        "batch_size": args.batch_size,
        "hidden_dim": args.hidden_dim,
        "seed": args.seed,
    }
    if args.metrics_out:
        Path(args.metrics_out).write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    if args.model_out:
        torch.save(
            {
                "model_state_dict": model.state_dict(),
                "metadata": metadata,
                "preprocessor": preprocessor,
            },
            args.model_out,
        )
    print(metadata)


if __name__ == "__main__":
    main()
