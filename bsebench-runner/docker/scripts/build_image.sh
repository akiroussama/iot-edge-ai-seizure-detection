#!/usr/bin/env bash
set -euo pipefail

IMAGE_NAME="${1:-bsebench-runner:external-repro}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/../../.." && pwd)"

docker build -f "${ROOT_DIR}/bsebench-runner/docker/Dockerfile" -t "${IMAGE_NAME}" "${ROOT_DIR}"
