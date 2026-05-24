from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

import yaml


def main() -> int:
    parser = argparse.ArgumentParser(description="Install the seven BSEBench repositories in editable mode.")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--repos-dir", default="/opt/bsebench/repos")
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    repos_dir = Path(args.repos_dir)
    data = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
    repos = data.get("repositories", [])
    if len(repos) != 7:
        raise SystemExit(f"Expected exactly 7 repositories, found {len(repos)} in {manifest_path}")

    repos_dir.mkdir(parents=True, exist_ok=True)
    for repo in repos:
        name = repo["name"]
        url = repo.get("url")
        ref = repo.get("ref")
        local_path = repo.get("local_path")
        target = repos_dir / name
        if local_path:
            target = Path(local_path)
        elif url:
            if not target.exists():
                subprocess.run(["git", "clone", url, str(target)], check=True)
            if ref:
                subprocess.run(["git", "-C", str(target), "fetch", "--all", "--tags"], check=True)
                subprocess.run(["git", "-C", str(target), "checkout", ref], check=True)
        else:
            raise SystemExit(f"Repository {name} has neither url nor local_path")
        pyproject = target / "pyproject.toml"
        setup_py = target / "setup.py"
        if not pyproject.exists() and not setup_py.exists():
            raise SystemExit(f"Repository {name} is not installable in editable mode: {target}")
        subprocess.run(["python", "-m", "pip", "install", "-e", str(target)], check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
