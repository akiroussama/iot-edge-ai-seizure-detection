from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
from typing import Any

import numpy as np
import pandas as pd

from src.utils.time import ensure_datetime


DEFAULT_SAE_ID_COLUMNS = ("patient_id", "recording_id", "window_start", "window_end")
DATETIME_ALIGNMENT_COLUMNS = {"window_start", "window_end", "recording_start", "recording_end"}
LEAKAGE_OR_METADATA_COLUMNS = {
    "patient_id",
    "recording_id",
    "window_start",
    "window_end",
    "recording_start",
    "recording_end",
    "source_dataset",
    "center_id",
    "split",
    "forecast_label",
    "is_excluded",
    "is_ictal",
    "is_postictal",
    "is_right_censored",
    "right_censoring_applied",
    "risk_score",
    "alarm",
    "alarm_threshold",
    "event_id",
    "seizure_id",
    "time_to_next_seizure_seconds",
    "time_since_last_seizure_seconds",
}


@dataclass(frozen=True)
class SparseAutoencoderConfig:
    n_features: int = 8
    fit_split: str | None = "train"
    split_col: str = "split"
    seed: int = 42
    epochs: int = 250
    learning_rate: float = 0.01
    sparsity_l1: float = 0.01
    batch_size: int = 128
    activation_epsilon: float = 1e-6
    activation_cols: tuple[str, ...] = ()


@dataclass(frozen=True)
class SparseAutoencoderReport:
    scores: pd.DataFrame
    dictionary: pd.DataFrame
    associations: pd.DataFrame
    manifest: pd.DataFrame
    metadata: dict[str, Any]


def _require_columns(df: pd.DataFrame, required: set[str], name: str) -> None:
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"{name} missing required columns: {missing}")


def _bool_series(df: pd.DataFrame, column: str, default: bool = False) -> pd.Series:
    if column not in df.columns:
        return pd.Series(default, index=df.index, dtype=bool)
    series = df[column]
    if pd.api.types.is_bool_dtype(series):
        return series.fillna(default).astype(bool)
    if pd.api.types.is_numeric_dtype(series):
        return series.fillna(int(default)).astype(bool)
    normalized = series.astype("string").str.strip().str.lower()
    out = pd.Series(default, index=df.index, dtype=bool)
    out[normalized.isin({"true", "1", "yes", "y"})] = True
    out[normalized.isin({"false", "0", "no", "n", "", "nan", "<na>"})] = False
    return out


def _normalize_alignment_columns(
    df: pd.DataFrame,
    id_columns: tuple[str, ...],
    name: str,
) -> pd.DataFrame:
    _require_columns(df, set(id_columns), name)
    out = df.copy()
    for column in id_columns:
        if column in DATETIME_ALIGNMENT_COLUMNS:
            out[column] = ensure_datetime(out[column])
    return out


def select_activation_columns(df: pd.DataFrame, requested: tuple[str, ...] = ()) -> list[str]:
    if requested:
        missing = [column for column in requested if column not in df.columns]
        if missing:
            raise ValueError(f"requested activation columns are missing: {missing}")
        non_numeric = [
            column for column in requested if not pd.api.types.is_numeric_dtype(df[column])
        ]
        if non_numeric:
            raise ValueError(f"requested activation columns are non-numeric: {non_numeric}")
        return list(requested)
    return [
        column
        for column in df.columns
        if column not in LEAKAGE_OR_METADATA_COLUMNS
        and pd.api.types.is_numeric_dtype(df[column])
    ]


def _fit_preprocessor(df: pd.DataFrame, columns: list[str]) -> dict[str, np.ndarray]:
    values = df[columns].apply(pd.to_numeric, errors="coerce")
    medians = values.median(axis=0).fillna(0.0).to_numpy(dtype=np.float64)
    filled = values.fillna(dict(zip(columns, medians, strict=True)))
    means = filled.mean(axis=0).to_numpy(dtype=np.float64)
    scales = filled.std(axis=0).replace(0.0, 1.0).fillna(1.0).to_numpy(dtype=np.float64)
    return {"medians": medians, "means": means, "scales": scales}


def _transform(df: pd.DataFrame, columns: list[str], preprocessor: dict[str, np.ndarray]) -> np.ndarray:
    values = df[columns].apply(pd.to_numeric, errors="coerce")
    values = values.fillna(dict(zip(columns, preprocessor["medians"], strict=True)))
    return ((values.to_numpy(dtype=np.float64) - preprocessor["means"]) / preprocessor["scales"]).astype(
        np.float64
    )


def _init_model(input_dim: int, n_features: int, rng: np.random.Generator) -> dict[str, np.ndarray]:
    scale = 1.0 / np.sqrt(max(input_dim, 1))
    return {
        "encoder_w": rng.normal(0.0, scale, size=(input_dim, n_features)),
        "encoder_b": np.zeros(n_features, dtype=np.float64),
        "decoder_w": rng.normal(0.0, scale, size=(n_features, input_dim)),
        "decoder_b": np.zeros(input_dim, dtype=np.float64),
    }


def _encode(x: np.ndarray, model: dict[str, np.ndarray]) -> tuple[np.ndarray, np.ndarray]:
    pre = x @ model["encoder_w"] + model["encoder_b"]
    return pre, np.maximum(pre, 0.0)


def _forward(x: np.ndarray, model: dict[str, np.ndarray]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    pre, z = _encode(x, model)
    recon = z @ model["decoder_w"] + model["decoder_b"]
    return pre, z, recon


def _loss(
    x: np.ndarray,
    recon: np.ndarray,
    z: np.ndarray,
    sparsity_l1: float,
) -> tuple[float, float, float]:
    mse = float(np.mean((recon - x) ** 2))
    sparse = float(sparsity_l1 * np.mean(np.abs(z)))
    return mse + sparse, mse, sparse


def _adam_step(
    model: dict[str, np.ndarray],
    grads: dict[str, np.ndarray],
    state: dict[str, dict[str, np.ndarray]],
    *,
    t: int,
    learning_rate: float,
) -> None:
    beta1 = 0.9
    beta2 = 0.999
    eps = 1e-8
    for name, grad in grads.items():
        first = state.setdefault("m", {}).setdefault(name, np.zeros_like(grad))
        second = state.setdefault("v", {}).setdefault(name, np.zeros_like(grad))
        first *= beta1
        first += (1.0 - beta1) * grad
        second *= beta2
        second += (1.0 - beta2) * (grad**2)
        first_hat = first / (1.0 - beta1**t)
        second_hat = second / (1.0 - beta2**t)
        model[name] -= learning_rate * first_hat / (np.sqrt(second_hat) + eps)


def _train_sparse_autoencoder(
    train_x: np.ndarray,
    all_x: np.ndarray,
    config: SparseAutoencoderConfig,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict[str, Any]]:
    if train_x.size == 0:
        raise ValueError("no training rows available for sparse autoencoder")
    rng = np.random.default_rng(config.seed)
    model = _init_model(train_x.shape[1], config.n_features, rng)
    initial_pre, initial_z, initial_recon = _forward(train_x, model)
    del initial_pre
    initial_loss, initial_mse, initial_sparse = _loss(
        train_x,
        initial_recon,
        initial_z,
        config.sparsity_l1,
    )
    state: dict[str, dict[str, np.ndarray]] = {}
    t = 0
    batch_size = max(1, int(config.batch_size))
    for _ in range(config.epochs):
        order = rng.permutation(len(train_x))
        for start in range(0, len(order), batch_size):
            idx = order[start : start + batch_size]
            batch = train_x[idx]
            pre, z, recon = _forward(batch, model)
            err = recon - batch
            grad_recon = 2.0 * err / max(err.size, 1)
            grad_decoder_w = z.T @ grad_recon
            grad_decoder_b = grad_recon.sum(axis=0)
            grad_z = grad_recon @ model["decoder_w"].T
            grad_z += config.sparsity_l1 * np.sign(z) / max(z.size, 1)
            grad_pre = grad_z * (pre > 0.0)
            grads = {
                "encoder_w": batch.T @ grad_pre,
                "encoder_b": grad_pre.sum(axis=0),
                "decoder_w": grad_decoder_w,
                "decoder_b": grad_decoder_b,
            }
            t += 1
            _adam_step(model, grads, state, t=t, learning_rate=config.learning_rate)

    final_pre, final_z, final_recon = _forward(train_x, model)
    del final_pre
    final_loss, final_mse, final_sparse = _loss(
        train_x,
        final_recon,
        final_z,
        config.sparsity_l1,
    )
    _, all_z, all_recon = _forward(all_x, model)
    payload = {
        "model": {name: value.round(8).tolist() for name, value in model.items()},
        "initial_loss": initial_loss,
        "initial_mse": initial_mse,
        "initial_sparse_penalty": initial_sparse,
        "final_loss": final_loss,
        "final_mse": final_mse,
        "final_sparse_penalty": final_sparse,
        "baseline_zero_mse": float(np.mean(train_x**2)),
    }
    return all_z, all_recon, model["decoder_w"], payload


def _jsonable(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return value.round(10).tolist()
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(key): _jsonable(val) for key, val in value.items()}
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    return value


def _stable_hash(payload: Any) -> str:
    import json

    encoded = json.dumps(_jsonable(payload), sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )
    return sha256(encoded).hexdigest()


def _dataframe_hash(df: pd.DataFrame) -> str:
    normalized = df.copy()
    for column in normalized.columns:
        if column in DATETIME_ALIGNMENT_COLUMNS:
            normalized[column] = ensure_datetime(normalized[column]).astype(str)
    return sha256(normalized.to_csv(index=False).encode("utf-8")).hexdigest()


def _join_prediction_metadata(
    activations: pd.DataFrame,
    predictions: pd.DataFrame | None,
    *,
    id_columns: tuple[str, ...],
) -> pd.DataFrame:
    base = _normalize_alignment_columns(activations, id_columns, "activations")
    if predictions is None:
        return base
    pred = _normalize_alignment_columns(predictions, id_columns, "predictions")
    base_dupes = base.duplicated(list(id_columns), keep=False)
    pred_dupes = pred.duplicated(list(id_columns), keep=False)
    if base_dupes.any():
        examples = base.loc[base_dupes, list(id_columns)].head(3).to_dict(orient="records")
        raise ValueError(f"activations contains duplicate alignment keys, examples={examples}")
    if pred_dupes.any():
        examples = pred.loc[pred_dupes, list(id_columns)].head(3).to_dict(orient="records")
        raise ValueError(f"predictions contains duplicate alignment keys, examples={examples}")

    base_indexed = base.set_index(list(id_columns), drop=False)
    pred_indexed = pred.set_index(list(id_columns), drop=False)
    missing = set(base_indexed.index) - set(pred_indexed.index)
    extra = set(pred_indexed.index) - set(base_indexed.index)
    if missing or extra:
        raise ValueError(
            "prediction/activation row mismatch: "
            f"missing_prediction_rows={len(missing)}, extra_prediction_rows={len(extra)}"
        )
    pred_indexed = pred_indexed.loc[base_indexed.index]
    for column in ("forecast_label", "is_excluded"):
        if column in base_indexed.columns and column in pred_indexed.columns:
            base_values = base_indexed[column].fillna(False).astype(bool)
            pred_values = pred_indexed[column].fillna(False).astype(bool)
            if not base_values.equals(pred_values):
                raise ValueError(f"predictions column {column!r} does not match activations")

    payload_columns = [
        column
        for column in ("risk_score", "alarm", "forecast_label", "is_excluded", "split")
        if column in pred.columns and column not in base.columns
    ]
    if not payload_columns:
        return base.reset_index(drop=True)
    payload = pd.concat(
        [pred_indexed[list(id_columns)], pred_indexed[payload_columns]],
        axis=1,
    ).reset_index(drop=True)
    return base.merge(payload, on=list(id_columns), how="left", validate="one_to_one")


def _fit_mask(df: pd.DataFrame, config: SparseAutoencoderConfig) -> pd.Series:
    valid = ~_bool_series(df, "is_excluded")
    if config.fit_split is not None and config.split_col in df.columns:
        valid &= df[config.split_col].astype(str).eq(str(config.fit_split))
    return valid


def _validate_config(config: SparseAutoencoderConfig) -> None:
    if config.n_features <= 0:
        raise ValueError("n_features must be positive")
    if config.epochs <= 0:
        raise ValueError("epochs must be positive")
    if config.learning_rate <= 0:
        raise ValueError("learning_rate must be positive")
    if config.sparsity_l1 < 0:
        raise ValueError("sparsity_l1 must be non-negative")
    if config.batch_size <= 0:
        raise ValueError("batch_size must be positive")


def _passthrough_columns(df: pd.DataFrame, id_columns: tuple[str, ...]) -> list[str]:
    wanted = [
        *id_columns,
        "split",
        "forecast_label",
        "is_excluded",
        "risk_score",
        "alarm",
        "event_id",
    ]
    return [column for column in dict.fromkeys(wanted) if column in df.columns]


def _dictionary_table(
    z: np.ndarray,
    decoder_w: np.ndarray,
    activation_columns: list[str],
    *,
    epsilon: float,
) -> pd.DataFrame:
    rows = []
    for feature_idx in range(z.shape[1]):
        weights = decoder_w[feature_idx]
        abs_weights = np.abs(weights)
        top_idx = int(np.argmax(abs_weights))
        denom = float(abs_weights.sum())
        active = z[:, feature_idx] > epsilon
        rows.append(
            {
                "sae_feature": f"sae_feature_{feature_idx:02d}",
                "feature_index": int(feature_idx),
                "mean_activation": float(np.mean(z[:, feature_idx])),
                "max_activation": float(np.max(z[:, feature_idx])),
                "activation_prevalence": float(np.mean(active)),
                "sparsity_fraction": float(1.0 - np.mean(active)),
                "decoder_l2_norm": float(np.linalg.norm(weights)),
                "top_activation_column": activation_columns[top_idx],
                "top_decoder_weight": float(weights[top_idx]),
                "monosemanticity_proxy": float(abs_weights[top_idx] / denom) if denom else 0.0,
            }
        )
    return pd.DataFrame(rows)


def _pearson(x: pd.Series, y: pd.Series) -> float:
    joined = pd.concat(
        [pd.to_numeric(x, errors="coerce"), pd.to_numeric(y, errors="coerce")],
        axis=1,
    ).dropna()
    if len(joined) < 2:
        return float("nan")
    left = joined.iloc[:, 0].to_numpy(dtype=float)
    right = joined.iloc[:, 1].to_numpy(dtype=float)
    if np.std(left) == 0 or np.std(right) == 0:
        return float("nan")
    return float(np.corrcoef(left, right)[0, 1])


def _association_table(
    metadata: pd.DataFrame,
    scores: pd.DataFrame,
    feature_columns: list[str],
    activation_columns: list[str],
    id_columns: tuple[str, ...],
) -> pd.DataFrame:
    analysis = pd.concat([metadata.reset_index(drop=True), scores[feature_columns]], axis=1)
    valid = ~_bool_series(analysis, "is_excluded")
    numeric_metadata = [
        column
        for column in analysis.columns
        if column not in set(feature_columns)
        and column not in set(activation_columns)
        and column not in set(id_columns)
        and column not in LEAKAGE_OR_METADATA_COLUMNS
        and pd.api.types.is_numeric_dtype(analysis[column])
    ]
    rows = []
    for feature in feature_columns:
        label_delta = float("nan")
        positive_mean = float("nan")
        negative_mean = float("nan")
        if "forecast_label" in analysis.columns:
            labels = _bool_series(analysis, "forecast_label")
            positives = analysis.loc[valid & labels, feature]
            negatives = analysis.loc[valid & ~labels, feature]
            if not positives.empty:
                positive_mean = float(positives.mean())
            if not negatives.empty:
                negative_mean = float(negatives.mean())
            if not positives.empty and not negatives.empty:
                label_delta = positive_mean - negative_mean

        risk_corr = (
            _pearson(analysis.loc[valid, feature], analysis.loc[valid, "risk_score"])
            if "risk_score" in analysis.columns
            else float("nan")
        )
        metadata_corrs = {
            column: _pearson(analysis.loc[valid, feature], analysis.loc[valid, column])
            for column in numeric_metadata
        }
        finite_corrs = {
            column: value
            for column, value in metadata_corrs.items()
            if np.isfinite(value)
        }
        if finite_corrs:
            top_column, top_corr = max(finite_corrs.items(), key=lambda item: abs(item[1]))
        else:
            top_column, top_corr = None, float("nan")
        rows.append(
            {
                "sae_feature": feature,
                "label_positive_mean_activation": positive_mean,
                "label_negative_mean_activation": negative_mean,
                "label_mean_activation_delta": label_delta,
                "risk_score_correlation": risk_corr,
                "top_metadata_correlation_column": top_column,
                "top_metadata_correlation": top_corr,
                "association_status": "post_hoc_not_causal",
            }
        )
    return pd.DataFrame(rows)


def build_sparse_autoencoder_report(
    activations: pd.DataFrame,
    *,
    predictions: pd.DataFrame | None = None,
    config: SparseAutoencoderConfig | None = None,
    model_name: str = "sparse_autoencoder",
    id_columns: tuple[str, ...] = DEFAULT_SAE_ID_COLUMNS,
) -> SparseAutoencoderReport:
    cfg = config or SparseAutoencoderConfig()
    _validate_config(cfg)
    metadata = _join_prediction_metadata(activations, predictions, id_columns=id_columns)
    activation_columns = select_activation_columns(metadata, cfg.activation_cols)
    if not activation_columns:
        raise ValueError("at least one numeric activation column is required")
    fit_mask = _fit_mask(metadata, cfg)
    if not fit_mask.any():
        raise ValueError("fit split has no usable activation rows")

    preprocessor = _fit_preprocessor(metadata.loc[fit_mask], activation_columns)
    train_x = _transform(metadata.loc[fit_mask], activation_columns, preprocessor)
    all_x = _transform(metadata, activation_columns, preprocessor)
    z, recon, decoder_w, training_payload = _train_sparse_autoencoder(train_x, all_x, cfg)
    feature_columns = [f"sae_feature_{idx:02d}" for idx in range(z.shape[1])]

    scores = metadata[_passthrough_columns(metadata, id_columns)].copy()
    for idx, feature in enumerate(feature_columns):
        scores[feature] = z[:, idx].astype(float)
    scores["sae_reconstruction_mse"] = np.mean((recon - all_x) ** 2, axis=1)
    dominant_idx = np.argmax(z, axis=1)
    scores["dominant_sae_feature"] = [feature_columns[idx] for idx in dominant_idx]
    scores["dominant_sae_activation"] = z[np.arange(len(z)), dominant_idx]
    scores["sae_fit_split"] = cfg.fit_split if cfg.fit_split is not None else "all_rows"
    scores["sae_model_name"] = model_name

    dictionary = _dictionary_table(
        z,
        decoder_w,
        activation_columns,
        epsilon=cfg.activation_epsilon,
    )
    associations = _association_table(
        metadata,
        scores,
        feature_columns,
        activation_columns,
        id_columns,
    )
    activation_table_hash = _dataframe_hash(metadata[[*id_columns, *activation_columns]])
    training_artifact_hash = _stable_hash(
        {
            "model_name": model_name,
            "config": asdict(cfg),
            "id_columns": list(id_columns),
            "activation_columns": activation_columns,
            "preprocessor": preprocessor,
            "training": training_payload,
            "activation_table_hash": activation_table_hash,
        }
    )
    metadata_payload = {
        "model_name": model_name,
        "id_columns": list(id_columns),
        "activation_columns": activation_columns,
        "n_rows": int(len(metadata)),
        "fit_rows": int(fit_mask.sum()),
        "n_sae_features": int(cfg.n_features),
        "seed": int(cfg.seed),
        "fit_split": cfg.fit_split if cfg.fit_split is not None else "all_rows",
        "split_col": cfg.split_col,
        "activation_table_hash": activation_table_hash,
        "activation_column_hash": _stable_hash({"activation_columns": activation_columns}),
        "training_artifact_hash": training_artifact_hash,
        "initial_reconstruction_mse": float(training_payload["initial_mse"]),
        "final_reconstruction_mse": float(training_payload["final_mse"]),
        "baseline_zero_reconstruction_mse": float(training_payload["baseline_zero_mse"]),
        "result_status": "interpretability_artifact_pre_gate_c_not_citable",
        "association_status": "post_hoc_not_causal",
    }
    manifest = pd.DataFrame([metadata_payload | {"config": asdict(cfg)}])
    return SparseAutoencoderReport(
        scores=scores,
        dictionary=dictionary,
        associations=associations,
        manifest=manifest,
        metadata=metadata_payload,
    )


def _markdown_table(df: pd.DataFrame, max_rows: int = 20) -> str:
    if df.empty:
        return "_No rows._"
    view = df.head(max_rows)
    headers = [str(column) for column in view.columns]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for _, row in view.iterrows():
        lines.append("| " + " | ".join(str(row[column]) for column in view.columns) + " |")
    if len(df) > max_rows:
        lines.append(f"\n_Showing {max_rows} of {len(df)} rows._")
    return "\n".join(lines)


def sparse_autoencoder_markdown(
    report: SparseAutoencoderReport,
    *,
    title: str = "Sparse Autoencoder Interpretability Report",
) -> str:
    return f"""# {title}

**Citation status:** not citable as a benchmark result before Gate C.

## Metadata

- Model: `{report.metadata["model_name"]}`
- Rows: `{report.metadata["n_rows"]}`
- Fit rows: `{report.metadata["fit_rows"]}`
- SAE features: `{report.metadata["n_sae_features"]}`
- Fit split: `{report.metadata["fit_split"]}`
- Result status: `{report.metadata["result_status"]}`
- Association status: `{report.metadata["association_status"]}`
- Training artifact hash: `{report.metadata["training_artifact_hash"]}`

## Dictionary

{_markdown_table(report.dictionary)}

## Post-Hoc Associations

{_markdown_table(report.associations)}
"""


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
