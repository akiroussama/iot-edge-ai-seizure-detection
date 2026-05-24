from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = REPO_ROOT / "reports" / "epibench_release_candidate"
REPRODUCED_DIR = OUT_DIR / "reproduced_claims"

REFERENCE_CLAIMS = [
    (
        "pilot_t1_eeg",
        REPO_ROOT / "examples" / "epibench" / "pilot_t1_eeg" / "result_bundle.yaml",
        REPO_ROOT / "reports" / "epibench_pilot_claim.json",
    ),
    (
        "chbmit_waveform_micro_d",
        REPO_ROOT / "examples" / "epibench" / "chbmit_waveform_micro_d" / "result_bundle.yaml",
        REPO_ROOT / "reports" / "epibench_chbmit_waveform_micro_claim.json",
    ),
    (
        "msg_gate_c_frozen_f",
        REPO_ROOT / "examples" / "epibench" / "msg_gate_c_frozen_f" / "result_bundle.yaml",
        REPO_ROOT / "reports" / "epibench_msg_gate_c_frozen_claim.json",
    ),
    (
        "far_explosion_failure_d",
        REPO_ROOT / "examples" / "epibench" / "far_explosion_failure_d" / "result_bundle.yaml",
        REPO_ROOT / "reports" / "epibench_far_explosion_claim.json",
    ),
]

CHECKSUM_PATHS = [
    REPO_ROOT / "docs" / "EPIBENCH_SPEC_V1.md",
    REPO_ROOT / "configs" / "epibench" / "epibench_v1.yaml",
    REPO_ROOT / "configs" / "epibench" / "conformance_suite_v1.yaml",
    REPO_ROOT / "schemas" / "epibench" / "dataset_evidence_card.schema.json",
    REPO_ROOT / "schemas" / "epibench" / "split_manifest.schema.json",
    REPO_ROOT / "schemas" / "epibench" / "failure_trace.schema.json",
    REPO_ROOT / "schemas" / "epibench" / "result_bundle.schema.json",
    REPO_ROOT / "schemas" / "epibench" / "claim_eligibility.schema.json",
    REPO_ROOT / "src" / "epibench" / "certification.py",
    REPO_ROOT / "src" / "epibench" / "scoring.py",
    REPO_ROOT / "src" / "epibench" / "szcore_bridge.py",
    REPO_ROOT / "scripts" / "epibench.py",
    REPO_ROOT / "scripts" / "epibench_build_q1_hardening_register.py",
    REPO_ROOT / "scripts" / "epibench_build_reviewer_packet.py",
    REPO_ROOT / "scripts" / "epibench_measure_local_hardware.py",
    REPO_ROOT / "scripts" / "epibench_overclaim_audit.py",
    REPO_ROOT / "scripts" / "epibench_reproduce_release_candidate.py",
    REPO_ROOT / "tests" / "test_epibench_standard.py",
    REPO_ROOT / "docs" / "EPIBENCH_IMPLEMENTATION_INDEX.md",
    REPO_ROOT / "docs" / "paper" / "EPIBENCH_NPJ_DIGITAL_MEDICINE_DRAFT.md",
    REPO_ROOT / "reports" / "epibench_reviewer_packet" / "README.md",
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Reproduce the EpiBench v1.0-rc evidence claims.")
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    args = parser.parse_args()

    result = reproduce_release_candidate(out_dir=args.out_dir)
    print(
        "EpiBench release-candidate reproduction "
        f"{result['status']} with {result['matched_count']}/{result['claim_count']} matched claims"
    )
    return 0 if result["status"] == "passed" else 1


def reproduce_release_candidate(*, out_dir: Path = OUT_DIR) -> dict[str, Any]:
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))

    from src.epibench.certification import certify_result_bundle

    out_dir.mkdir(parents=True, exist_ok=True)
    reproduced_dir = out_dir / "reproduced_claims"
    reproduced_dir.mkdir(parents=True, exist_ok=True)

    claim_results = []
    for claim_id, bundle_path, reference_path in REFERENCE_CLAIMS:
        reproduced = certify_result_bundle(bundle_path)
        reproduced_path = reproduced_dir / f"{claim_id}.json"
        _write_json(reproduced_path, reproduced)
        reference = json.loads(reference_path.read_text(encoding="utf-8"))
        matched = _canonical_json(reference) == _canonical_json(reproduced)
        claim_results.append(
            {
                "claim_id": claim_id,
                "bundle_path": _rel(bundle_path),
                "reference_path": _rel(reference_path),
                "reproduced_path": _rel(reproduced_path),
                "matched": matched,
                "reference_sha256": _sha256(reference_path),
                "reproduced_sha256": _sha256(reproduced_path),
                "final_claim": reproduced["final_claim"],
                "epi_score": reproduced["score"]["epi_score"],
            }
        )

    checksums = [
        {
            "path": _rel(path),
            "sha256": _sha256(path) if path.exists() else None,
            "exists": path.exists(),
        }
        for path in CHECKSUM_PATHS
    ]
    result = {
        "schema_version": "epibench.release_candidate_reproduction.v1",
        "release_candidate": "v1.0-rc-local",
        "status": "passed" if all(item["matched"] for item in claim_results) else "failed",
        "generation_base_commit": _git_commit(),
        "git_commit_boundary": (
            "The report cannot embed the final commit that contains itself. "
            "The final archive or Git tag is the authoritative source commit."
        ),
        "claim_count": len(claim_results),
        "matched_count": sum(1 for item in claim_results if item["matched"]),
        "claim_results": claim_results,
        "checksums": checksums,
        "doi_status": "pending_zenodo_deposition",
        "external_reproduction_status": "pending_external_lab_run",
        "one_command": "python scripts/epibench_reproduce_release_candidate.py",
        "boundary": (
            "This package verifies scientific reproducibility of EpiBench artefacts from the checkout. "
            "It is not clinical validation, regulatory clearance, or a DOI minting event."
        ),
    }
    _write_json(out_dir / "reproduction_result.json", result)
    _write_json(out_dir / "release_manifest.json", _release_manifest(result))
    (out_dir / "README.md").write_text(_render_readme(result), encoding="utf-8")
    return result


def _release_manifest(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "epibench.release_manifest.v1",
        "release_candidate": result["release_candidate"],
        "generation_base_commit": result["generation_base_commit"],
        "git_commit_boundary": result["git_commit_boundary"],
        "doi_status": result["doi_status"],
        "external_reproduction_status": result["external_reproduction_status"],
        "one_command_reproduction": result["one_command"],
        "reference_claims": result["claim_results"],
        "checksums": result["checksums"],
        "release_blockers": [
            "Zenodo DOI has not yet been minted.",
            "No independent external laboratory has yet run the one-command reproduction kit.",
            "Target IoT hardware measurement remains required; edge-ready wording remains forbidden.",
            "Independent clinical/methods review packet is prepared but not yet completed.",
        ],
    }


def _render_readme(result: dict[str, Any]) -> str:
    rows = "\n".join(
        "- `{claim_id}`: matched=`{matched}`, final_claim=`{final_claim}`, epi_score=`{epi_score}`".format(**item)
        for item in result["claim_results"]
    )
    return f"""# EpiBench Release Candidate Reproduction Packet

Status: `{result['status']}`

## Purpose

This packet turns the current EpiBench checkout into a reproducible release-candidate artefact. It
checks that reference claim reports can be regenerated from result bundles and that core normative files
have stable checksums.

## One-Command Reproduction

```powershell
python scripts\\epibench_reproduce_release_candidate.py
```

## Claim Reproduction

{rows}

## Release Boundary

- DOI status: `{result['doi_status']}`;
- external reproduction status: `{result['external_reproduction_status']}`;
- generation base commit: `{result['generation_base_commit']}`;
- git commit boundary: {result['git_commit_boundary']}
- boundary: {result['boundary']}

This is a scientific release-candidate packet, not clinical approval and not regulatory certification.
"""


def _canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.resolve().as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
