#!/usr/bin/env bash
set -euo pipefail

mkdir -p "${BSEBENCH_HOME}" "${BSEBENCH_REPOS_DIR}" "${BSEBENCH_BUNDLES_DIR}" "${BSEBENCH_WORK_DIR}"

exec "$@"
