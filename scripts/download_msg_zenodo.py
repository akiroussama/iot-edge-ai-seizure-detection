from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.request import urlopen

ZENODO_RECORD_ID = "17380899"
ZENODO_API_URL = f"https://zenodo.org/api/records/{ZENODO_RECORD_ID}"


def _fetch_record(api_url: str) -> dict:
    with urlopen(api_url, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def _selected_files(record: dict, include: list[str] | None) -> list[dict]:
    files = list(record.get("files", []))
    if not include:
        return files
    selected = []
    for file_info in files:
        key = file_info.get("key", "")
        if any(pattern in key for pattern in include):
            selected.append(file_info)
    return selected


def _md5(path: Path) -> str:
    digest = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _checksum_matches(path: Path, checksum: str | None) -> bool:
    if not checksum:
        return True
    algorithm, _, expected = checksum.partition(":")
    if algorithm.lower() != "md5" or not expected:
        return True
    return _md5(path) == expected


def _download_with_curl(url: str, destination: Path) -> None:
    if shutil.which("curl") is None:
        raise RuntimeError("curl is required for resumable downloads")
    destination.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "curl",
            "--fail",
            "--location",
            "--continue-at",
            "-",
            "--output",
            str(destination),
            url,
        ],
        check=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Download My Seizure Gauge files from Zenodo.")
    parser.add_argument("--out-dir", default="data/raw/msg")
    parser.add_argument("--api-url", default=ZENODO_API_URL)
    parser.add_argument(
        "--include",
        action="append",
        help="Substring filter for file keys. Repeat to download a subset, e.g. --include SeizureTimesOnly.zip.",
    )
    parser.add_argument("--verify-existing", action="store_true")
    args = parser.parse_args()

    record = _fetch_record(args.api_url)
    out_dir = Path(args.out_dir)
    files = _selected_files(record, args.include)
    if not files:
        raise SystemExit("No Zenodo files matched the requested filters")

    print(
        {
            "record": record.get("id"),
            "title": record.get("metadata", {}).get("title"),
            "files": [file_info.get("key") for file_info in files],
            "out_dir": str(out_dir),
        }
    )
    for file_info in files:
        key = file_info["key"]
        destination = out_dir / key
        size = int(file_info.get("size") or 0)
        checksum = file_info.get("checksum")
        if destination.exists() and destination.stat().st_size == size:
            if args.verify_existing and not _checksum_matches(destination, checksum):
                raise SystemExit(f"Checksum mismatch for existing file: {destination}")
            print({"status": "present", "file": key, "bytes": size})
            continue
        url = file_info.get("links", {}).get("self") or file_info.get("links", {}).get("download")
        if not url:
            raise SystemExit(f"Zenodo file has no download URL: {key}")
        print({"status": "downloading", "file": key, "bytes": size})
        _download_with_curl(url, destination)
        if destination.stat().st_size != size:
            raise SystemExit(
                f"Download size mismatch for {destination}: expected {size}, got {destination.stat().st_size}"
            )
        if args.verify_existing and not _checksum_matches(destination, checksum):
            raise SystemExit(f"Checksum mismatch after download: {destination}")
        print({"status": "complete", "file": key, "bytes": destination.stat().st_size})


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
