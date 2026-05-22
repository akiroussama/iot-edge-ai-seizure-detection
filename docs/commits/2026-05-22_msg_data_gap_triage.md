# Commit Trace - MSG Data-Gap Triage

Date: 2026-05-22

Branch: `codex/msg-data-gap-triage`

Base: `origin/main@43cb4b0`

## Intent

Add a reproducible MSG source-data and horizon-feasibility triage layer before
Gate B/C. The output should identify blockers and review actions without
creating any citable benchmark or clinical performance claim.

## Files

- `src/reports/msg_gap_triage.py`
- `scripts/build_msg_gap_triage.py`
- `tests/test_msg_gap_triage.py`
- `docs/research/2026-05-22_msg_data_gap_triage.md`
- `docs/commits/2026-05-22_msg_data_gap_triage.md`

## Guardrails

- Claim status: `msg_gap_triage_pre_gate_c_not_citable`.
- No sensitivity, FAR/day, TIW, Brier, BSS, or clinical utility output.
- Unmatched events remain explicit source-data blockers.
- Zero-recording patients are marked `p0_blocker`.
- Long-horizon right-censoring and event-coverability failures are feasibility
  warnings, not model-performance findings.

## Validation Log

Executed before final commit:

```bash
uv run --extra dev ruff check src/reports/msg_gap_triage.py scripts/build_msg_gap_triage.py tests/test_msg_gap_triage.py
uv run --extra dev pytest tests/test_msg_gap_triage.py tests/test_event_coverage.py tests/test_horizon_viability.py
uv run --extra dev ruff check .
uv run --extra dev --extra torch pytest
git diff --check
```

Result:

- Targeted Ruff: passed.
- Targeted pytest: 10 passed.
- Full Ruff: passed.
- Full pytest: 297 passed.
- `git diff --check`: passed.
