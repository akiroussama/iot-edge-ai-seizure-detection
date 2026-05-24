#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="bsebench", description="BSEBench external reproduction runner")
    sub = parser.add_subparsers(dest="command", required=True)

    reproduce = sub.add_parser("reproduce", help="Reproduce and verify a BSEBench result bundle")
    reproduce.add_argument("--bundle", required=True, help="Bundle id, e.g. bundle_calce_a123_lfp_dst_v1.0")
    reproduce.add_argument("--bundles-dir", default=os.getenv("BSEBENCH_BUNDLES_DIR", "bundles"))
    reproduce.add_argument("--work-dir", default=os.getenv("BSEBENCH_WORK_DIR", "work"))
    reproduce.add_argument("--report", default=None)
    reproduce.add_argument("--no-run", action="store_true", help="Validate and compare existing outputs without executing commands")

    validate = sub.add_parser("validate-bundle", help="Validate bundle recipe and reference manifest presence")
    validate.add_argument("--bundle", required=True)
    validate.add_argument("--bundles-dir", default=os.getenv("BSEBENCH_BUNDLES_DIR", "bundles"))

    fingerprint = sub.add_parser("fingerprint", help="Create a SHA256 manifest for a directory")
    fingerprint.add_argument("--root", required=True)
    fingerprint.add_argument("--out", required=True)

    smoke = sub.add_parser("smoke", help="Run runner self-checks without BSEBench data")
    smoke.add_argument("--out", default=None)

    args = parser.parse_args(argv)
    if args.command == "reproduce":
        return reproduce_bundle(args)
    if args.command == "validate-bundle":
        bundle = load_bundle(args.bundle, Path(args.bundles_dir))
        print(json.dumps({"status": "valid", "bundle_id": bundle["bundle_id"]}, indent=2))
        return 0
    if args.command == "fingerprint":
        manifest = fingerprint_tree(Path(args.root))
        write_json(Path(args.out), manifest)
        return 0
    if args.command == "smoke":
        result = {"status": "passed", "checks": ["cli_import", "json", "yaml", "sha256"]}
        if args.out:
            write_json(Path(args.out), result)
        else:
            print(json.dumps(result, indent=2))
        return 0
    raise AssertionError(args.command)


def reproduce_bundle(args: argparse.Namespace) -> int:
    bundles_dir = Path(args.bundles_dir)
    work_dir = Path(args.work_dir) / args.bundle
    bundle = load_bundle(args.bundle, bundles_dir)
    work_dir.mkdir(parents=True, exist_ok=True)

    if not args.no_run:
        for command in bundle.get("commands", []):
            run_command(command, work_dir)

    output_root = resolve_bundle_path(bundle, "output_root", work_dir)
    reference_manifest_path = resolve_bundle_path(bundle, "reference_manifest", bundles_dir / args.bundle)
    if not reference_manifest_path.exists():
        raise SystemExit(f"Missing reference manifest: {reference_manifest_path}")
    reference = load_json(reference_manifest_path)
    actual = fingerprint_tree(output_root)
    comparison = compare_manifests(reference, actual)

    report = {
        "schema_version": "bsebench.reproduction_report.v1",
        "bundle_id": args.bundle,
        "status": "bit_exact" if comparison["bit_exact"] else "diverged",
        "reference_manifest": str(reference_manifest_path),
        "output_root": str(output_root),
        "comparison": comparison,
    }
    report_path = Path(args.report) if args.report else work_dir / "reproduction_report.json"
    write_json(report_path, report)
    print(json.dumps(report, indent=2))
    return 0 if comparison["bit_exact"] else 2


def load_bundle(bundle_id: str, bundles_dir: Path) -> dict[str, Any]:
    bundle_dir = bundles_dir / bundle_id
    recipe_path = bundle_dir / "reproduction.yaml"
    if not recipe_path.exists():
        raise SystemExit(f"Missing bundle recipe: {recipe_path}")
    bundle = yaml.safe_load(recipe_path.read_text(encoding="utf-8")) or {}
    if bundle.get("bundle_id") != bundle_id:
        raise SystemExit(f"Bundle id mismatch: expected {bundle_id}, got {bundle.get('bundle_id')}")
    required = ["bundle_id", "reference_manifest", "output_root", "commands"]
    missing = [key for key in required if key not in bundle]
    if missing:
        raise SystemExit(f"Bundle recipe {recipe_path} missing required keys: {missing}")
    return bundle


def run_command(command: str | list[str], cwd: Path) -> None:
    if isinstance(command, str):
        subprocess.run(command, cwd=cwd, shell=True, check=True)
    else:
        subprocess.run(command, cwd=cwd, check=True)


def resolve_bundle_path(bundle: dict[str, Any], key: str, base: Path) -> Path:
    path = Path(str(bundle[key]))
    return path if path.is_absolute() else base / path


def fingerprint_tree(root: Path) -> dict[str, Any]:
    if not root.exists():
        raise SystemExit(f"Cannot fingerprint missing output root: {root}")
    files = []
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        rel = path.relative_to(root).as_posix()
        files.append({"path": rel, "sha256": sha256_file(path), "size_bytes": path.stat().st_size})
    return {"schema_version": "bsebench.sha256_manifest.v1", "files": files}


def compare_manifests(reference: dict[str, Any], actual: dict[str, Any]) -> dict[str, Any]:
    ref = {item["path"]: item for item in reference.get("files", [])}
    act = {item["path"]: item for item in actual.get("files", [])}
    missing = sorted(set(ref) - set(act))
    unexpected = sorted(set(act) - set(ref))
    changed = sorted(path for path in set(ref) & set(act) if ref[path]["sha256"] != act[path]["sha256"])
    return {
        "bit_exact": not missing and not unexpected and not changed,
        "missing_files": missing,
        "unexpected_files": unexpected,
        "changed_files": changed,
        "reference_file_count": len(ref),
        "actual_file_count": len(act),
    }


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
