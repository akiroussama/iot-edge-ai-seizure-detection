from __future__ import annotations

import hashlib
import json
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class PaperArtifactPackageConfig:
    title: str = "EpiTwin-Open Paper Artifact Package"
    package_status: str = "pre_gate_c_reproducibility_package"
    gate_c_status: str = "not_started"
    citation_status: str = "not_citable_pre_gate_c"
    tracked_only: bool = True
    include_globs: tuple[str, ...] = (
        "configs/**/*.yaml",
        "docs/commits/**/*.md",
        "docs/research/**/*.md",
        "docs/research/**/*.csv",
        "schemas/**/*.json",
        "schemas/**/*.csv",
        "scripts/**/*.py",
        "src/**/*.py",
        "tests/**/*.py",
    )


@dataclass(frozen=True)
class PaperArtifactPackage:
    inventory: pd.DataFrame
    claims: pd.DataFrame
    checklist: pd.DataFrame
    manifest: dict[str, Any]


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git_tracked_files(root: Path) -> set[str]:
    try:
        out = subprocess.check_output(
            ["git", "ls-files"],
            cwd=root,
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        return set()
    return {line.strip() for line in out.splitlines() if line.strip()}


def _glob_files(root: Path, patterns: tuple[str, ...]) -> set[str]:
    paths: set[str] = set()
    for pattern in patterns:
        paths.update(
            str(path.relative_to(root))
            for path in root.glob(pattern)
            if path.is_file() and ".venv" not in path.parts
        )
    return paths


def _artifact_role(path: str) -> str:
    if path.startswith("docs/commits/"):
        return "commit_evidence"
    if path.startswith("docs/research/"):
        return "research_trace"
    if path.startswith("schemas/"):
        return "schema"
    if path.startswith("configs/"):
        return "configuration"
    if path.startswith("scripts/"):
        return "cli_or_pipeline"
    if path.startswith("tests/"):
        return "test"
    if path.startswith("src/"):
        return "source_code"
    return "other"


def collect_artifact_inventory(
    *,
    root: str | Path,
    config: PaperArtifactPackageConfig | None = None,
) -> pd.DataFrame:
    cfg = config or PaperArtifactPackageConfig()
    root_path = Path(root)
    candidates = _glob_files(root_path, cfg.include_globs)
    if cfg.tracked_only:
        tracked = _git_tracked_files(root_path)
        candidates = candidates & tracked if tracked else candidates
    rows = []
    for rel_path in sorted(candidates):
        full_path = root_path / rel_path
        rows.append(
            {
                "artifact_path": rel_path,
                "artifact_role": _artifact_role(rel_path),
                "bytes": int(full_path.stat().st_size),
                "sha256": _sha256_file(full_path),
            }
        )
    return pd.DataFrame(rows)


def default_paper_claims(inventory: pd.DataFrame) -> pd.DataFrame:
    available = set(inventory.get("artifact_path", pd.Series(dtype=str)).astype(str))
    candidate_claims = [
        {
            "claim_id": "C01",
            "paper_section": "Contribution",
            "claim_text": "The project defines a unified wearable seizure-risk leaderboard schema.",
            "artifact_path": "schemas/leaderboard_entry.schema.json",
            "source_uri": "",
            "claim_status": "engineering_ready",
            "citation_status": "method_claim_only",
            "gate_c_status": "not_started",
        },
        {
            "claim_id": "C02",
            "paper_section": "Methods",
            "claim_text": "Leaderboard rows are computed from standardized prediction and event tables.",
            "artifact_path": "scripts/make_leaderboard_row.py",
            "source_uri": "",
            "claim_status": "engineering_ready",
            "citation_status": "method_claim_only",
            "gate_c_status": "not_started",
        },
        {
            "claim_id": "C03",
            "paper_section": "Reproducibility",
            "claim_text": "Gate C registries verify artifact hashes, row counts, and split metadata.",
            "artifact_path": "schemas/gate_c_registry.schema.json",
            "source_uri": "",
            "claim_status": "engineering_ready",
            "citation_status": "method_claim_only",
            "gate_c_status": "not_started",
        },
        {
            "claim_id": "C04",
            "paper_section": "Baselines",
            "claim_text": "Constrained null models and calibration reports exist before model claims.",
            "artifact_path": "scripts/make_calibration_report.py",
            "source_uri": "",
            "claim_status": "engineering_ready",
            "citation_status": "method_claim_only",
            "gate_c_status": "not_started",
        },
        {
            "claim_id": "C05",
            "paper_section": "Audit",
            "claim_text": "Active audit target selection supports prioritized human label review.",
            "artifact_path": "scripts/select_audit_targets.py",
            "source_uri": "",
            "claim_status": "engineering_ready",
            "citation_status": "method_claim_only",
            "gate_c_status": "not_started",
        },
        {
            "claim_id": "C06",
            "paper_section": "Uncertainty",
            "claim_text": "Conformal risk intervals can be generated from standardized predictions.",
            "artifact_path": "scripts/run_conformal_calibration.py",
            "source_uri": "",
            "claim_status": "engineering_ready",
            "citation_status": "method_claim_only",
            "gate_c_status": "not_started",
        },
        {
            "claim_id": "C07",
            "paper_section": "Clinical Utility",
            "claim_text": "Clinical utility reports separate decision-support analysis from recommendations.",
            "artifact_path": "scripts/make_clinical_utility_report.py",
            "source_uri": "",
            "claim_status": "engineering_ready",
            "citation_status": "method_claim_only",
            "gate_c_status": "not_started",
        },
        {
            "claim_id": "C08",
            "paper_section": "External Comparison",
            "claim_text": "External SOTA-family predictions must pass through the same leaderboard runner.",
            "artifact_path": "configs/reproduction/external_sota_reproduction.yaml",
            "source_uri": "",
            "claim_status": "engineering_ready",
            "citation_status": "method_claim_only",
            "gate_c_status": "not_started",
        },
        {
            "claim_id": "C09",
            "paper_section": "Results",
            "claim_text": "No citable benchmark number is claimed before Gate C frozen artifacts.",
            "artifact_path": "docs/research/2026-05-21_task6_gate_c_registry.md",
            "source_uri": "",
            "claim_status": "pre_gate_c_guardrail",
            "citation_status": "not_citable_pre_gate_c",
            "gate_c_status": "not_started",
        },
    ]
    return pd.DataFrame(
        [claim for claim in candidate_claims if claim["artifact_path"] in available]
    )


def build_claim_traceability(claims: pd.DataFrame, inventory: pd.DataFrame) -> pd.DataFrame:
    required = {"claim_id", "claim_text", "artifact_path", "citation_status", "gate_c_status"}
    missing = sorted(required - set(claims.columns))
    if missing:
        raise ValueError(f"claims missing required columns: {missing}")
    inventory_paths = set(inventory.get("artifact_path", pd.Series(dtype=str)).astype(str))
    out = claims.copy()
    out["artifact_found"] = out["artifact_path"].astype(str).isin(inventory_paths)
    out["has_source_uri"] = out.get("source_uri", pd.Series("", index=out.index)).fillna("").astype(str).str.len() > 0
    out["citation_safe"] = ~(
        out["citation_status"].eq("citable_after_gate_c") & ~out["gate_c_status"].eq("passed")
    )
    issues = []
    for _, row in out.iterrows():
        row_issues = []
        if not bool(row["artifact_found"]) and not bool(row["has_source_uri"]):
            row_issues.append("missing committed artifact or source URI")
        if not bool(row["citation_safe"]):
            row_issues.append("citable claim before Gate C passed")
        issues.append("; ".join(row_issues) if row_issues else "ok")
    out["traceability_issue"] = issues
    out["claim_ready"] = out["traceability_issue"].eq("ok")
    return out


def build_reproducibility_checklist(
    *,
    inventory: pd.DataFrame,
    claims: pd.DataFrame,
    config: PaperArtifactPackageConfig | None = None,
) -> pd.DataFrame:
    cfg = config or PaperArtifactPackageConfig()
    available = set(inventory.get("artifact_path", pd.Series(dtype=str)).astype(str))
    checks = [
        ("leaderboard_schema", "schemas/leaderboard_entry.schema.json"),
        ("leaderboard_runner", "scripts/make_leaderboard_row.py"),
        ("gate_c_schema", "schemas/gate_c_registry.schema.json"),
        ("gate_c_builder", "scripts/make_gate_c_registry.py"),
        ("calibration_report", "scripts/make_calibration_report.py"),
        ("forecastability_atlas", "scripts/make_forecastability_atlas.py"),
        ("clinical_utility", "scripts/make_clinical_utility_report.py"),
        ("external_sota_bridge", "scripts/run_external_sota_reproduction.py"),
        ("docs_commit_trace", "docs/commits/2026-05-22_t10_external_sota_reproduction.md"),
    ]
    rows = []
    for check_name, path in checks:
        rows.append(
            {
                "check_name": check_name,
                "artifact_path": path,
                "status": "present" if path in available else "missing",
                "gate_c_status": cfg.gate_c_status,
            }
        )
    rows.append(
        {
            "check_name": "all_claims_traceable",
            "artifact_path": "",
            "status": "present" if claims["claim_ready"].all() else "needs_attention",
            "gate_c_status": cfg.gate_c_status,
        }
    )
    rows.append(
        {
            "check_name": "citable_results_allowed",
            "artifact_path": "",
            "status": "allowed" if cfg.gate_c_status == "passed" else "blocked_until_gate_c",
            "gate_c_status": cfg.gate_c_status,
        }
    )
    return pd.DataFrame(rows)


def build_paper_artifact_package(
    *,
    root: str | Path,
    config: PaperArtifactPackageConfig | None = None,
    claims: pd.DataFrame | None = None,
) -> PaperArtifactPackage:
    cfg = config or PaperArtifactPackageConfig()
    inventory = collect_artifact_inventory(root=root, config=cfg)
    claim_seed = claims if claims is not None else default_paper_claims(inventory)
    traceability = build_claim_traceability(claim_seed, inventory)
    checklist = build_reproducibility_checklist(
        inventory=inventory,
        claims=traceability,
        config=cfg,
    )
    manifest = {
        "title": cfg.title,
        "package_status": cfg.package_status,
        "gate_c_status": cfg.gate_c_status,
        "citation_status": cfg.citation_status,
        "artifact_count": int(len(inventory)),
        "claim_count": int(len(traceability)),
        "ready_claim_count": int(traceability["claim_ready"].sum()),
        "check_count": int(len(checklist)),
        "failed_checks": checklist.loc[~checklist["status"].isin({"present", "allowed"}), "check_name"].tolist(),
        "config": asdict(cfg),
    }
    return PaperArtifactPackage(
        inventory=inventory,
        claims=traceability,
        checklist=checklist,
        manifest=manifest,
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


def paper_artifact_package_markdown(package: PaperArtifactPackage) -> str:
    manifest = package.manifest
    warning = ""
    if manifest["citation_status"] != "citable_after_gate_c":
        warning = "\n**Citation status:** package is not citable as a benchmark-result bundle before Gate C.\n"
    return "\n".join(
        [
            f"# {manifest['title']}",
            warning,
            "This package links paper claims to committed artifacts or explicit sources.",
            "",
            "## Manifest",
            "",
            f"- Package status: `{manifest['package_status']}`",
            f"- Gate C status: `{manifest['gate_c_status']}`",
            f"- Artifact count: `{manifest['artifact_count']}`",
            f"- Claim count: `{manifest['claim_count']}`",
            f"- Ready claims: `{manifest['ready_claim_count']}`",
            f"- Failed checks: `{manifest['failed_checks']}`",
            "",
            "## Contribution Statement Draft",
            "",
            "EpiTwin-Open contributes a leakage-aware, reproducible wearable seizure-risk "
            "benchmark scaffold with constrained nulls, calibration, clinical-utility "
            "analysis, audit prioritization, formal uncertainty, and external-SOTA "
            "reproduction hooks. The package explicitly separates methods infrastructure "
            "from citable benchmark results until Gate C frozen artifacts are available.",
            "",
            "## Claim Traceability",
            "",
            _markdown_table(package.claims),
            "",
            "## Reproducibility Checklist",
            "",
            _markdown_table(package.checklist),
            "",
            "## Limitations And Negative-Result Policy",
            "",
            "- Pre-Gate-C exploratory numbers must remain non-citable.",
            "- Missing, unforecastable, or null-overlapping regimes are reportable outcomes.",
            "- External SOTA comparisons require row-level recomputation under this runner.",
            "- Clinical utility tables are decision-support analysis, not recommendations.",
            "",
        ]
    )


def manifest_json(package: PaperArtifactPackage) -> str:
    return json.dumps(package.manifest, indent=2)
