from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SPEC_PATH = REPO_ROOT / "configs" / "epibench" / "epibench_v1.yaml"
DEFAULT_SCHEMA_ROOT = REPO_ROOT / "schemas" / "epibench"


@lru_cache(maxsize=4)
def load_spec(path: str | Path = DEFAULT_SPEC_PATH) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise ValueError(f"EpiBench spec is not a mapping: {path}")
    return data


def claim_ranks(spec: dict[str, Any]) -> dict[str, int]:
    return {claim: int(meta["rank"]) for claim, meta in spec["claims"].items()}


def min_claim(claims: list[str], spec: dict[str, Any]) -> str:
    ranks = claim_ranks(spec)
    known = [claim for claim in claims if claim in ranks]
    if not known:
        return "E0"
    return min(known, key=lambda claim: ranks[claim])


def claim_at_or_above(claim: str, floor: str, spec: dict[str, Any]) -> bool:
    ranks = claim_ranks(spec)
    return ranks.get(claim, -1) >= ranks.get(floor, 999)
