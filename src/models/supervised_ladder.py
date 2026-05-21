from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
from typing import Any

import numpy as np
import pandas as pd

from src.calibration.thresholding import quantile_threshold
from src.utils.time import ensure_datetime


LEAKAGE_OR_ID_COLUMNS = {
    "patient_id",
    "recording_id",
    "window_start",
    "window_end",
    "recording_start",
    "recording_end",
    "center_id",
    "source_dataset",
    "forecast_label",
    "is_ictal",
    "is_postictal",
    "is_excluded",
    "is_right_censored",
    "right_censoring_applied",
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
    "population_prior_rate",
}


STANDARD_OUTPUT_COLUMNS = [
    "risk_score",
    "alarm",
    "alarm_threshold",
    "supervised_model_name",
    "supervised_model_family",
    "supervised_ladder_rung",
    "score_fit_split",
    "threshold_source_split",
    "target_tiw",
    "feature_columns",
    "feature_set_hash",
    "training_artifact_hash",
    "comparator_reference_name",
    "comparator_reference_hash",
    "seed",
    "supervised_valid_evidence",
    "supervised_prediction_status",
]


LADDER_MODEL_SPECS = {
    "logistic_regression": {
        "family": "linear",
        "rung": "tabular_linear",
        "input_kind": "tabular_features",
        "requires_torch": False,
    },
    "gradient_stumps": {
        "family": "tree_ensemble",
        "rung": "tabular_stump_boosting",
        "input_kind": "tabular_features",
        "requires_torch": False,
    },
    "mlp": {
        "family": "neural_tabular",
        "rung": "tabular_mlp",
        "input_kind": "tabular_features",
        "requires_torch": True,
    },
    "tcn": {
        "family": "temporal_neural",
        "rung": "window_sequence_tcn",
        "input_kind": "patient_ordered_window_sequence",
        "requires_torch": True,
    },
    "gru": {
        "family": "temporal_neural",
        "rung": "window_sequence_gru",
        "input_kind": "patient_ordered_window_sequence",
        "requires_torch": True,
    },
}


@dataclass(frozen=True)
class SupervisedLadderConfig:
    model_name: str = "logistic_regression"
    split_col: str = "split"
    train_split: str = "train"
    val_split: str = "val"
    target_col: str = "forecast_label"
    target_tiw: float = 0.1
    seed: int = 42
    feature_cols: tuple[str, ...] = ()
    epochs: int = 100
    learning_rate: float = 0.05
    weight_decay: float = 1e-4
    hidden_dim: int = 32
    batch_size: int = 256
    n_estimators: int = 25
    sequence_length: int = 8


def _require_columns(df: pd.DataFrame, required: set[str], name: str) -> None:
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"{name} missing required columns: {missing}")


def _valid_mask(df: pd.DataFrame) -> pd.Series:
    return ~df.get("is_excluded", pd.Series(False, index=df.index)).fillna(False).astype(bool)


def select_feature_columns(df: pd.DataFrame, requested: tuple[str, ...] = ()) -> list[str]:
    if requested:
        missing = [column for column in requested if column not in df.columns]
        if missing:
            raise ValueError(f"requested feature columns are missing: {missing}")
        return list(requested)
    return [
        column
        for column in df.columns
        if column not in LEAKAGE_OR_ID_COLUMNS and pd.api.types.is_numeric_dtype(df[column])
    ]


def valid_evidence_mask(df: pd.DataFrame, feature_cols: list[str]) -> pd.Series:
    if not feature_cols:
        raise ValueError("at least one feature column is required")
    valid = _valid_mask(df)
    evidence = df[feature_cols].apply(pd.to_numeric, errors="coerce").notna().any(axis=1)
    return valid & evidence


def fit_preprocessor(train_df: pd.DataFrame, feature_cols: list[str]) -> dict[str, np.ndarray]:
    values = train_df[feature_cols].apply(pd.to_numeric, errors="coerce")
    medians = values.median(axis=0).fillna(0.0).to_numpy(dtype=np.float64)
    filled = values.fillna(dict(zip(feature_cols, medians, strict=True)))
    means = filled.mean(axis=0).to_numpy(dtype=np.float64)
    scales = filled.std(axis=0).replace(0.0, 1.0).fillna(1.0).to_numpy(dtype=np.float64)
    return {"medians": medians, "means": means, "scales": scales}


def transform_features(
    df: pd.DataFrame,
    feature_cols: list[str],
    preprocessor: dict[str, np.ndarray],
) -> np.ndarray:
    values = df[feature_cols].apply(pd.to_numeric, errors="coerce")
    values = values.fillna(dict(zip(feature_cols, preprocessor["medians"], strict=True)))
    return ((values.to_numpy(dtype=np.float64) - preprocessor["means"]) / preprocessor["scales"]).astype(
        np.float64
    )


def _sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(x, -50, 50)))


def derive_model_seed(base_seed: int, model_name: str, index: int = 0) -> int:
    payload = f"{int(base_seed)}:{model_name}:{int(index)}".encode("utf-8")
    return int.from_bytes(sha256(payload).digest()[:4], byteorder="big", signed=False)


def _fit_logistic(
    x: np.ndarray,
    y: np.ndarray,
    *,
    config: SupervisedLadderConfig,
) -> dict[str, Any]:
    rng = np.random.default_rng(config.seed)
    weights = rng.normal(0.0, 0.01, size=x.shape[1])
    bias = float(np.log((y.mean() + 1e-3) / (1.0 - y.mean() + 1e-3)))
    for _ in range(config.epochs):
        pred = _sigmoid(x @ weights + bias)
        error = pred - y
        grad_w = (x.T @ error) / len(x) + config.weight_decay * weights
        grad_b = float(error.mean())
        weights -= config.learning_rate * grad_w
        bias -= config.learning_rate * grad_b
    return {"weights": weights, "bias": bias}


def _predict_logistic(x: np.ndarray, model: dict[str, Any]) -> np.ndarray:
    return _sigmoid(x @ model["weights"] + float(model["bias"]))


def _fit_gradient_stumps(
    x: np.ndarray,
    y: np.ndarray,
    *,
    config: SupervisedLadderConfig,
) -> dict[str, Any]:
    prior = float(np.clip(y.mean(), 1e-3, 1.0 - 1e-3))
    base_logit = float(np.log(prior / (1.0 - prior)))
    logits = np.full(len(y), base_logit, dtype=float)
    stumps: list[dict[str, float | int]] = []
    for _ in range(config.n_estimators):
        residual = y - _sigmoid(logits)
        best: dict[str, float | int] | None = None
        best_loss = np.inf
        for feature_idx in range(x.shape[1]):
            values = x[:, feature_idx]
            thresholds = np.unique(np.quantile(values, [0.25, 0.5, 0.75]))
            for threshold in thresholds:
                left = values <= threshold
                right = ~left
                if not left.any() or not right.any():
                    continue
                left_value = float(residual[left].mean())
                right_value = float(residual[right].mean())
                update = np.where(left, left_value, right_value)
                loss = float(np.mean((residual - update) ** 2))
                if loss < best_loss:
                    best_loss = loss
                    best = {
                        "feature_idx": int(feature_idx),
                        "threshold": float(threshold),
                        "left_value": left_value,
                        "right_value": right_value,
                    }
        if best is None:
            break
        feature_idx = int(best["feature_idx"])
        update = np.where(
            x[:, feature_idx] <= float(best["threshold"]),
            float(best["left_value"]),
            float(best["right_value"]),
        )
        logits += config.learning_rate * update
        stumps.append(best)
    return {"base_logit": base_logit, "learning_rate": float(config.learning_rate), "stumps": stumps}


def _predict_gradient_stumps(x: np.ndarray, model: dict[str, Any]) -> np.ndarray:
    logits = np.full(x.shape[0], float(model["base_logit"]), dtype=float)
    for stump in model["stumps"]:
        feature_idx = int(stump["feature_idx"])
        update = np.where(
            x[:, feature_idx] <= float(stump["threshold"]),
            float(stump["left_value"]),
            float(stump["right_value"]),
        )
        logits += float(model["learning_rate"]) * update
    return _sigmoid(logits)


def _fit_predict_torch(
    train_x: np.ndarray,
    train_y: np.ndarray,
    predict_x: np.ndarray,
    *,
    config: SupervisedLadderConfig,
) -> tuple[np.ndarray, dict[str, Any]]:
    try:
        import torch
        from torch import nn
    except Exception as exc:  # pragma: no cover - depends on optional dependency
        raise RuntimeError(f"{config.model_name} requires the torch extra") from exc

    torch.manual_seed(config.seed)
    torch.set_num_threads(1)
    x_train = torch.tensor(train_x, dtype=torch.float32)
    y_train = torch.tensor(train_y, dtype=torch.float32)
    x_all = torch.tensor(predict_x, dtype=torch.float32)
    model = nn.Sequential(
        nn.Linear(train_x.shape[1], config.hidden_dim),
        nn.GELU(),
        nn.Linear(config.hidden_dim, 1),
    )
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=config.learning_rate,
        weight_decay=config.weight_decay,
    )
    criterion = nn.BCEWithLogitsLoss()
    batch_size = max(1, int(config.batch_size))
    generator = torch.Generator()
    generator.manual_seed(config.seed)
    for _ in range(config.epochs):
        order = torch.randperm(len(x_train), generator=generator)
        for start in range(0, len(order), batch_size):
            batch = order[start : start + batch_size]
            optimizer.zero_grad(set_to_none=True)
            loss = criterion(model(x_train[batch]).squeeze(-1), y_train[batch])
            loss.backward()
            optimizer.step()
    with torch.no_grad():
        risk = torch.sigmoid(model(x_all).squeeze(-1)).cpu().numpy()
    params = {key: value.detach().cpu().numpy().round(8).tolist() for key, value in model.state_dict().items()}
    return risk.astype(float), {"torch_state": params}


def _fit_model(
    train_x: np.ndarray,
    train_y: np.ndarray,
    predict_x: np.ndarray,
    *,
    config: SupervisedLadderConfig,
) -> tuple[np.ndarray, dict[str, Any]]:
    if config.model_name == "logistic_regression":
        model = _fit_logistic(train_x, train_y, config=config)
        return _predict_logistic(predict_x, model), model
    if config.model_name == "gradient_stumps":
        model = _fit_gradient_stumps(train_x, train_y, config=config)
        return _predict_gradient_stumps(predict_x, model), model
    if config.model_name in {"mlp", "tcn", "gru"}:
        # The first supervised ladder consumes window-feature tables. TCN/GRU
        # rungs are registered here and use the same deterministic tabular
        # interface until sequence tensors are available through Gate C.
        return _fit_predict_torch(train_x, train_y, predict_x, config=config)
    raise ValueError(f"unknown supervised ladder model: {config.model_name}")


def _jsonable(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return value.round(10).tolist()
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, dict):
        return {str(key): _jsonable(val) for key, val in value.items()}
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    return value


def _stable_hash(payload: Any) -> str:
    import json

    data = json.dumps(_jsonable(payload), sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256(data).hexdigest()


def _dataframe_hash(df: pd.DataFrame) -> str:
    normalized = df.copy()
    for column in normalized.columns:
        if column.endswith("_start") or column.endswith("_end"):
            normalized[column] = ensure_datetime(normalized[column]).astype(str)
    csv = normalized.to_csv(index=False).encode("utf-8")
    return sha256(csv).hexdigest()


def _align_reference_features(
    features: pd.DataFrame,
    reference_predictions: pd.DataFrame,
    *,
    id_columns: tuple[str, ...],
    reference_name: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    _require_columns(features, {"forecast_label", "is_excluded", *id_columns}, "features")
    _require_columns(
        reference_predictions,
        {"risk_score", "forecast_label", "is_excluded", *id_columns},
        reference_name,
    )
    feature_dupes = features.duplicated(list(id_columns), keep=False)
    reference_dupes = reference_predictions.duplicated(list(id_columns), keep=False)
    if feature_dupes.any():
        examples = features.loc[feature_dupes, list(id_columns)].head(3).to_dict(orient="records")
        raise ValueError(f"features contains duplicate alignment keys, examples={examples}")
    if reference_dupes.any():
        examples = reference_predictions.loc[reference_dupes, list(id_columns)].head(3).to_dict(
            orient="records"
        )
        raise ValueError(f"{reference_name} contains duplicate alignment keys, examples={examples}")

    model = features.set_index(list(id_columns), drop=False)
    reference = reference_predictions.set_index(list(id_columns), drop=False)
    missing = set(model.index) - set(reference.index)
    extra = set(reference.index) - set(model.index)
    if missing or extra:
        raise ValueError(
            f"{reference_name} row mismatch: missing_reference_rows={len(missing)}, "
            f"extra_reference_rows={len(extra)}"
        )
    reference = reference.loc[model.index]
    for column in ("forecast_label", "is_excluded"):
        model_values = model[column].fillna(False).astype(bool)
        reference_values = reference[column].fillna(False).astype(bool)
        if not model_values.equals(reference_values):
            raise ValueError(f"{reference_name} column {column!r} does not match features")
    return model.reset_index(drop=True), reference.reset_index(drop=True)


def _validate_config(config: SupervisedLadderConfig) -> None:
    if config.model_name not in LADDER_MODEL_SPECS:
        raise ValueError(f"unknown supervised ladder model: {config.model_name}")
    if not 0 <= config.target_tiw <= 1:
        raise ValueError("target_tiw must be in [0, 1]")
    if config.epochs <= 0:
        raise ValueError("epochs must be positive")
    if config.learning_rate <= 0:
        raise ValueError("learning_rate must be positive")


def train_supervised_ladder_model(
    features: pd.DataFrame,
    *,
    reference_predictions: pd.DataFrame,
    reference_name: str,
    config: SupervisedLadderConfig | None = None,
    id_columns: tuple[str, ...] = ("patient_id", "recording_id", "window_start", "window_end"),
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Fit one supervised ladder rung and return standardized predictions plus log."""
    cfg = config or SupervisedLadderConfig()
    _validate_config(cfg)
    _require_columns(features, {cfg.target_col, cfg.split_col, *id_columns}, "features")
    if reference_predictions is None or reference_name == "":
        raise ValueError("supervised ladder runs require a named null/reference comparator")
    aligned_features, aligned_reference = _align_reference_features(
        features,
        reference_predictions,
        id_columns=id_columns,
        reference_name=reference_name,
    )
    feature_cols = select_feature_columns(aligned_features, cfg.feature_cols)
    evidence = valid_evidence_mask(aligned_features, feature_cols)
    train_mask = evidence & aligned_features[cfg.split_col].astype(str).eq(cfg.train_split)
    val_mask = evidence & aligned_features[cfg.split_col].astype(str).eq(cfg.val_split)
    if not train_mask.any():
        raise ValueError(f"train split {cfg.train_split!r} has no valid feature rows")
    if not val_mask.any():
        raise ValueError(f"validation split {cfg.val_split!r} has no valid feature rows")

    train_df = aligned_features.loc[train_mask].copy()
    preprocessor = fit_preprocessor(train_df, feature_cols)
    train_x = transform_features(train_df, feature_cols, preprocessor)
    train_y = train_df[cfg.target_col].astype(float).to_numpy(dtype=float)
    predict_x = transform_features(aligned_features.loc[evidence], feature_cols, preprocessor)
    risk = pd.Series(0.0, index=aligned_features.index, dtype=float)
    risk_values, model_payload = _fit_model(train_x, train_y, predict_x, config=cfg)
    risk.loc[evidence] = np.clip(risk_values, 0.0, 1.0)

    val_scores = risk.loc[val_mask]
    threshold = quantile_threshold(val_scores, cfg.target_tiw)
    alarm = risk.ge(threshold) & evidence
    spec = LADDER_MODEL_SPECS[cfg.model_name]
    feature_set_hash = _stable_hash({"feature_cols": feature_cols})
    comparator_hash = _dataframe_hash(aligned_reference)
    training_artifact_hash = _stable_hash(
        {
            "config": asdict(cfg),
            "feature_cols": feature_cols,
            "preprocessor": preprocessor,
            "model": model_payload,
            "threshold": threshold,
            "comparator_reference_hash": comparator_hash,
        }
    )

    predictions = aligned_features.copy()
    predictions["risk_score"] = risk
    predictions["alarm"] = alarm.fillna(False).astype(bool)
    predictions.loc[~_valid_mask(predictions), "alarm"] = False
    predictions["alarm_threshold"] = float(threshold)
    predictions["supervised_model_name"] = cfg.model_name
    predictions["supervised_model_family"] = spec["family"]
    predictions["supervised_ladder_rung"] = spec["rung"]
    predictions["score_fit_split"] = cfg.train_split
    predictions["threshold_source_split"] = cfg.val_split
    predictions["target_tiw"] = float(cfg.target_tiw)
    predictions["feature_columns"] = ",".join(feature_cols)
    predictions["feature_set_hash"] = feature_set_hash
    predictions["training_artifact_hash"] = training_artifact_hash
    predictions["comparator_reference_name"] = reference_name
    predictions["comparator_reference_hash"] = comparator_hash
    predictions["seed"] = int(cfg.seed)
    predictions["supervised_valid_evidence"] = evidence.astype(bool)
    prediction_status = pd.Series("scored", index=predictions.index, dtype=object)
    prediction_status.loc[~_valid_mask(predictions)] = "excluded_by_label"
    prediction_status.loc[_valid_mask(predictions) & ~evidence] = "no_feature_evidence"
    predictions["supervised_prediction_status"] = prediction_status

    log = {
        "model_name": cfg.model_name,
        "model_family": spec["family"],
        "ladder_rung": spec["rung"],
        "config": asdict(cfg),
        "feature_columns": feature_cols,
        "feature_set_hash": feature_set_hash,
        "training_artifact_hash": training_artifact_hash,
        "seed": int(cfg.seed),
        "comparator_reference_name": reference_name,
        "comparator_reference_hash": comparator_hash,
        "rows": int(len(predictions)),
        "valid_evidence_rows": int(evidence.sum()),
        "no_feature_evidence_rows": int((_valid_mask(aligned_features) & ~evidence).sum()),
        "train_rows": int(train_mask.sum()),
        "val_rows": int(val_mask.sum()),
        "train_positives": int(train_y.sum()),
        "alarm_threshold": float(threshold),
        "result_status": "predictions_only_requires_null_corrected_reporting",
    }
    return predictions, log


def train_supervised_ladder(
    features: pd.DataFrame,
    *,
    reference_predictions: pd.DataFrame,
    reference_name: str,
    configs: list[SupervisedLadderConfig],
    id_columns: tuple[str, ...] = ("patient_id", "recording_id", "window_start", "window_end"),
) -> tuple[dict[str, pd.DataFrame], pd.DataFrame]:
    predictions: dict[str, pd.DataFrame] = {}
    logs = []
    for config in configs:
        preds, log = train_supervised_ladder_model(
            features,
            reference_predictions=reference_predictions,
            reference_name=reference_name,
            config=config,
            id_columns=id_columns,
        )
        predictions[config.model_name] = preds
        logs.append(log)
    return predictions, pd.DataFrame(logs)


def table_records(df: pd.DataFrame) -> list[dict[str, Any]]:
    records = []
    for record in df.to_dict(orient="records"):
        clean = {}
        for key, value in record.items():
            if isinstance(value, float) and (np.isnan(value) or np.isinf(value)):
                clean[key] = None
            elif value is pd.NA or value is pd.NaT:
                clean[key] = None
            elif isinstance(value, pd.Timestamp):
                clean[key] = value.isoformat()
            elif isinstance(value, np.integer):
                clean[key] = int(value)
            elif isinstance(value, np.floating):
                clean[key] = float(value)
            else:
                clean[key] = value
        records.append(clean)
    return records
