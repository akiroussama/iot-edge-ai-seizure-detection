from __future__ import annotations

import math
from typing import Any


def compute_epi_score(result_bundle: dict[str, Any], spec: dict[str, Any]) -> dict[str, Any]:
    """Compute the preregistered geometric Epi-Score from declared axis subscores.

    This reference implementation intentionally separates score calculation from claim
    certification. A strong score cannot rescue leakage, label uncertainty, or split failure.
    """
    axis_spec = spec["score"]["axes"]
    provided = result_bundle.get("score_inputs", {}).get("subscores", {})
    if not isinstance(provided, dict):
        raise ValueError("result_bundle.score_inputs.subscores must be a mapping")

    missing_required = [
        axis for axis, meta in axis_spec.items() if meta.get("required", False) and axis not in provided
    ]
    if missing_required:
        raise ValueError(f"Missing required Epi-Score axes: {missing_required}")

    selected: dict[str, float] = {}
    selected_weights: dict[str, float] = {}
    for axis, value in provided.items():
        if axis not in axis_spec:
            raise ValueError(f"Unknown Epi-Score axis: {axis}")
        score = float(value)
        if score < 0 or score > 1:
            raise ValueError(f"Epi-Score axis {axis} must be in [0, 1], got {score}")
        selected[axis] = score
        selected_weights[axis] = float(axis_spec[axis]["weight"])

    total_weight = sum(selected_weights.values())
    if total_weight <= 0:
        raise ValueError("No Epi-Score axes selected")
    normalized_weights = {axis: weight / total_weight for axis, weight in selected_weights.items()}

    geometric = 1.0
    for axis, score in selected.items():
        geometric *= max(score, 1e-12) ** normalized_weights[axis]

    min_axis = min(selected.values())
    floor = float(spec["score"]["floor"])
    penalty_lambda = float(spec["score"]["lambda"])
    penalty = math.exp(-penalty_lambda * max(0.0, floor - min_axis))
    epi_score = 100.0 * geometric * penalty
    return {
        "epi_score": round(epi_score, 3),
        "axis_scores": selected,
        "normalized_weights": normalized_weights,
        "minimum_axis_score": min_axis,
        "floor": floor,
        "floor_penalty_applied": min_axis < floor,
    }
