from __future__ import annotations

import subprocess
import sys

import pandas as pd

from src.reports.paper_artifact_package import (
    PaperArtifactPackageConfig,
    build_claim_traceability,
    build_paper_artifact_package,
    collect_artifact_inventory,
)
from src.utils.io import read_table, write_table


def _write_minimal_package_root(root) -> None:
    paths = [
        "schemas/leaderboard_entry.schema.json",
        "schemas/gate_c_registry.schema.json",
        "scripts/make_leaderboard_row.py",
        "scripts/make_gate_c_registry.py",
        "scripts/make_calibration_report.py",
        "scripts/make_forecastability_atlas.py",
        "scripts/make_clinical_utility_report.py",
        "scripts/run_external_sota_reproduction.py",
        "docs/commits/2026-05-22_t10_external_sota_reproduction.md",
        "configs/reproduction/external_sota_reproduction.yaml",
    ]
    for rel_path in paths:
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"artifact: {rel_path}\n", encoding="utf-8")


def test_collect_artifact_inventory_hashes_matching_files(tmp_path) -> None:
    _write_minimal_package_root(tmp_path)

    inventory = collect_artifact_inventory(
        root=tmp_path,
        config=PaperArtifactPackageConfig(tracked_only=False),
    )

    assert "scripts/make_leaderboard_row.py" in set(inventory["artifact_path"])
    assert inventory["sha256"].str.len().min() == 64
    assert set(inventory["artifact_role"]) >= {"schema", "cli_or_pipeline", "commit_evidence"}


def test_claim_traceability_flags_missing_artifacts_and_gate_c_violations() -> None:
    inventory = pd.DataFrame(
        {
            "artifact_path": ["scripts/make_leaderboard_row.py"],
            "artifact_role": ["cli_or_pipeline"],
            "bytes": [1],
            "sha256": ["a" * 64],
        }
    )
    claims = pd.DataFrame(
        {
            "claim_id": ["ok", "missing", "gate"],
            "claim_text": ["ok", "missing", "gate"],
            "artifact_path": [
                "scripts/make_leaderboard_row.py",
                "missing.md",
                "scripts/make_leaderboard_row.py",
            ],
            "source_uri": ["", "", ""],
            "citation_status": [
                "method_claim_only",
                "method_claim_only",
                "citable_after_gate_c",
            ],
            "gate_c_status": ["not_started", "not_started", "not_started"],
        }
    )

    trace = build_claim_traceability(claims, inventory)

    assert bool(trace.loc[trace["claim_id"].eq("ok"), "claim_ready"].iloc[0]) is True
    assert "missing committed artifact" in trace.loc[
        trace["claim_id"].eq("missing"), "traceability_issue"
    ].iloc[0]
    assert "citable claim before Gate C passed" in trace.loc[
        trace["claim_id"].eq("gate"), "traceability_issue"
    ].iloc[0]


def test_build_paper_artifact_package_cli_writes_outputs(tmp_path) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    _write_minimal_package_root(root)
    out_dir = tmp_path / "out"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/build_paper_artifact_package.py",
            "--root",
            str(root),
            "--out-dir",
            str(out_dir),
            "--all-files",
        ],
        check=True,
        text=True,
        capture_output=True,
    )

    assert '"package_status": "pre_gate_c_reproducibility_package"' in result.stdout
    manifest = (out_dir / "paper_artifact_manifest.json").read_text(encoding="utf-8")
    claims = read_table(out_dir / "paper_claim_traceability.csv")
    checklist = read_table(out_dir / "paper_reproducibility_checklist.csv")
    assert "not citable" in (out_dir / "paper_artifact_package.md").read_text(encoding="utf-8")
    assert '"artifact_count"' in manifest
    assert claims["claim_ready"].all()
    assert "blocked_until_gate_c" in set(checklist["status"])


def test_build_paper_artifact_package_rejects_citable_before_gate_c(tmp_path) -> None:
    out_dir = tmp_path / "out"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/build_paper_artifact_package.py",
            "--out-dir",
            str(out_dir),
            "--citation-status",
            "citable_after_gate_c",
            "--gate-c-status",
            "not_started",
        ],
        check=False,
        text=True,
        capture_output=True,
    )

    assert result.returncode != 0
    assert "gate-c-status passed" in result.stderr


def test_build_paper_artifact_package_marks_unverified_source_uri_not_ready(tmp_path) -> None:
    _write_minimal_package_root(tmp_path)
    claims = pd.DataFrame(
        {
            "claim_id": ["source_only"],
            "claim_text": ["external source only claim"],
            "artifact_path": [""],
            "source_uri": ["https://example.org/source"],
            "citation_status": ["method_claim_only"],
            "gate_c_status": ["not_started"],
        }
    )
    claims_path = tmp_path / "claims.csv"
    write_table(claims, claims_path)

    package = build_paper_artifact_package(
        root=tmp_path,
        config=PaperArtifactPackageConfig(tracked_only=False),
        claims=read_table(claims_path),
    )

    assert bool(package.claims.loc[0, "claim_ready"]) is False
    assert "not primary-source verified" in package.claims.loc[0, "traceability_issue"]
    assert package.manifest["ready_claim_count"] == 0


def test_build_paper_artifact_package_accepts_verified_source_only_claim(tmp_path) -> None:
    _write_minimal_package_root(tmp_path)
    claims = pd.DataFrame(
        {
            "claim_id": ["source_only"],
            "claim_text": ["external source only claim"],
            "artifact_path": [""],
            "source_uri": ["https://example.org/source"],
            "source_verification_status": ["primary_source_verified"],
            "citation_status": ["method_claim_only"],
            "gate_c_status": ["not_started"],
        }
    )

    package = build_paper_artifact_package(
        root=tmp_path,
        config=PaperArtifactPackageConfig(tracked_only=False),
        claims=claims,
    )

    assert bool(package.claims.loc[0, "claim_ready"]) is True
    assert package.manifest["ready_claim_count"] == 1
