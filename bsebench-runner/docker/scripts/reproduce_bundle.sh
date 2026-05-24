#!/usr/bin/env bash
set -euo pipefail

BUNDLE_ID="${1:-bundle_calce_a123_lfp_dst_v1.0}"
shift || true

exec bsebench reproduce --bundle "${BUNDLE_ID}" "$@"
