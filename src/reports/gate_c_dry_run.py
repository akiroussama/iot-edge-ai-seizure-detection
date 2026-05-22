from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from src.artifacts.registry import verify_gate_c_registry

DEFAULT_REQUIRED_GATE_C_ROLES = ("events", "labels", "splits")


@dataclass(frozen=True)
class GateCDryRunReport:
    diagnostics: dict[str, Any]
    artifact_summary: pd.DataFrame
    markdown: str


def _artifact_roles(registry: dict[str, Any]) -> set[str]:
    return {
        str(artifact.get("role"))
        for artifact in registry.get("artifacts", [])
        if isinstance(artifact, dict) and artifact.get("role") is not None
    }


def _artifact_summary(registry: dict[str, Any]) -> pd.DataFrame:
    rows = []
    for artifact in registry.get("artifacts", []):
        if not isinstance(artifact, dict):
            continue
        rows.append(
            {
                "name": artifact.get("name"),
                "role": artifact.get("role"),
                "path": artifact.get("path"),
                "bytes": artifact.get("bytes"),
                "row_count": artifact.get("row_count"),
                "event_count": artifact.get("event_count"),
                "positive_windows": artifact.get("positive_windows"),
                "split_counts": artifact.get("split_counts"),
            }
        )
    return pd.DataFrame(rows)


def _split_manifest_warnings(split_manifest: dict[str, Any]) -> list[str]:
    warnings: list[str] = []
    if not split_manifest.get("horizon_name"):
        warnings.append("split_manifest.horizon_name is missing")
    if split_manifest.get("sph_minutes") is None:
        warnings.append("split_manifest.sph_minutes is missing")
    if split_manifest.get("sop_minutes") is None:
        warnings.append("split_manifest.sop_minutes is missing")
    return warnings


def _markdown_list(items: list[str]) -> str:
    if not items:
        return "- none"
    return "\n".join(f"- {item}" for item in items)


def _artifact_table_markdown(artifact_summary: pd.DataFrame) -> str:
    if artifact_summary.empty:
        return "_No artifact records._"
    columns = [
        column
        for column in ("name", "role", "path", "row_count", "event_count", "positive_windows")
        if column in artifact_summary.columns
    ]
    rows = artifact_summary[columns].copy()
    header = "| " + " | ".join(columns) + " |"
    divider = "| " + " | ".join("---" for _ in columns) + " |"
    body = []
    for _, row in rows.iterrows():
        values = []
        for column in columns:
            value = row[column]
            if isinstance(value, float) and pd.isna(value):
                value = ""
            values.append("" if value is None else str(value).replace("|", "\\|"))
        body.append("| " + " | ".join(values) + " |")
    return "\n".join([header, divider, *body])


def gate_c_dry_run_markdown(
    *,
    diagnostics: dict[str, Any],
    artifact_summary: pd.DataFrame,
) -> str:
    return f"""# Gate C Dry-Run Diagnostics

**Status:** `{diagnostics["readiness_status"]}`

This is a dry-run diagnostic. It is not a Gate C pass and it does not make any
benchmark number citable.

## Registry

- Registry id: `{diagnostics.get("registry_id")}`
- Dataset: `{diagnostics.get("dataset")}`
- Gate B status: `{diagnostics["gate_b_status"]}`
- Gate C status: `{diagnostics["gate_c_status"]}`
- Freeze status: `{diagnostics["freeze_status"]}`
- DOI / preregistration URI: `{diagnostics.get("doi_or_prereg_uri") or "missing"}`
- Structural verification: `{diagnostics["structural_ok"]}`
- Citable readiness: `{diagnostics["citable_ready"]}`

## Blockers

{_markdown_list(diagnostics["blockers"])}

## Warnings

{_markdown_list(diagnostics["warnings"])}

## Artifact Summary

{_artifact_table_markdown(artifact_summary)}

## Next Actions

1. Complete Gate B human label audit and commit the passing validation report.
2. Fix any structural registry errors listed above.
3. Register all required artifact roles and rerun the dry-run report.
4. Freeze splits/artifacts only after audit corrections are applied.
5. Pre-register or DOI the frozen protocol before producing citable rows.
"""


def build_gate_c_dry_run_report(
    registry: dict[str, Any],
    *,
    root: str | Path | None = None,
    gate_b_status: str = "not_started",
    required_roles: tuple[str, ...] = DEFAULT_REQUIRED_GATE_C_ROLES,
    require_prereg: bool = True,
    split_col: str = "split",
) -> GateCDryRunReport:
    structural = verify_gate_c_registry(
        registry,
        root=root,
        require_frozen=False,
        split_col=split_col,
    )
    frozen = verify_gate_c_registry(
        registry,
        root=root,
        require_frozen=True,
        split_col=split_col,
    )
    blockers = list(structural["errors"])
    warnings: list[str] = []
    if gate_b_status != "passed":
        blockers.append(f"gate_b_status is {gate_b_status!r}, expected 'passed'")
    if registry.get("gate_c_status") != "passed":
        blockers.append("registry.gate_c_status is not 'passed'")
    if registry.get("freeze_status") != "frozen":
        blockers.append("registry.freeze_status is not 'frozen'")
    if require_prereg and not registry.get("doi_or_prereg_uri"):
        blockers.append("doi_or_prereg_uri is required for Gate C")

    roles = _artifact_roles(registry)
    missing_roles = sorted(set(required_roles) - roles)
    if missing_roles:
        blockers.append(f"missing required artifact roles: {missing_roles}")

    split_manifest = registry.get("split_manifest", {})
    if isinstance(split_manifest, dict):
        warnings.extend(_split_manifest_warnings(split_manifest))
    else:
        blockers.append("registry.split_manifest must be an object")

    artifact_summary = _artifact_summary(registry)
    citable_ready = bool(
        structural["ok"]
        and frozen["ok"]
        and gate_b_status == "passed"
        and not missing_roles
        and (bool(registry.get("doi_or_prereg_uri")) or not require_prereg)
    )
    diagnostics = {
        "readiness_status": "ready_for_gate_c_review" if citable_ready else "blocked",
        "citable_ready": citable_ready,
        "structural_ok": bool(structural["ok"]),
        "frozen_verification_ok": bool(frozen["ok"]),
        "registry_id": registry.get("registry_id"),
        "dataset": registry.get("dataset"),
        "gate_b_status": gate_b_status,
        "gate_c_status": registry.get("gate_c_status"),
        "freeze_status": registry.get("freeze_status"),
        "doi_or_prereg_uri": registry.get("doi_or_prereg_uri"),
        "artifact_count": int(len(registry.get("artifacts", []))),
        "required_roles": list(required_roles),
        "present_roles": sorted(roles),
        "missing_roles": missing_roles,
        "blockers": blockers,
        "warnings": warnings,
        "structural_errors": structural["errors"],
        "frozen_errors": frozen["errors"],
    }
    markdown = gate_c_dry_run_markdown(
        diagnostics=diagnostics,
        artifact_summary=artifact_summary,
    )
    return GateCDryRunReport(
        diagnostics=diagnostics,
        artifact_summary=artifact_summary,
        markdown=markdown,
    )
