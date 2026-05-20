#!/usr/bin/env bash
set -euo pipefail

if command -v uv >/dev/null 2>&1; then
  PYTHON=(uv run python)
else
  PYTHON=(python)
fi

run_step() {
  echo
  echo "==> $*"
  "$@"
}

echo "EpiTwin-Open first-run verification"
echo "Python command: ${PYTHON[*]}"
echo "Scope: synthetic/mock software checks only; no clinical claims."

run_step "${PYTHON[@]}" -m pytest -q
run_step "${PYTHON[@]}" -m ruff check .
run_step "${PYTHON[@]}" scripts/run_synthetic_demo.py
run_step "${PYTHON[@]}" scripts/make_report.py --synthetic --out-dir reports
run_step "${PYTHON[@]}" -u scripts/train_epitwin_ssl.py --epochs 1 --batch-size 1 --time-steps 4 --hidden-dim 4 --backbone gru

echo
echo "EpiTwin-Open first-run verification complete."
