# F2 Federated Benchmark Protocol

Date: 2026-05-22

Branch: `codex/federated-benchmark-protocol`

Base: `origin/main@d9bcc5c`

## Objective

Add a protocol for future MSG, SeizeIT2, and clinical-site participation
without sharing raw patient data. The first implementation aggregates
site-level leaderboard rows only; it does not federate model parameters yet.

## Implementation Plan

- Add a federated site-result validator that rejects raw patient/window columns.
- Add weighted site-level aggregation over leaderboard metrics.
- Report site heterogeneity through per-metric site ranges.
- Require clean Gate C site rows before any citable federated summary.
- Add CLI, YAML contract, tests, and Markdown output.

## Scientific Guardrails

- No raw patient windows in federated inputs.
- No pooled mean without heterogeneity reporting.
- No citable federated summary unless all site rows are Gate C passed,
  leakage-clean, and frozen.
- This is a benchmark protocol, not a claim of privacy-preserving training.

## Validation Log

Targeted validation:

```bash
uv run --extra dev ruff check src/reports/federated_benchmark.py src/reports/__init__.py scripts/make_federated_benchmark_report.py tests/test_federated_benchmark.py
uv run --extra dev pytest tests/test_federated_benchmark.py
uv run --extra dev pytest tests/test_federated_benchmark.py tests/test_leaderboard_runner.py tests/test_paper_artifact_package.py tests/test_external_sota_reproduction.py
```

Full validation:

```bash
uv run --extra dev ruff check .
uv run --extra dev --extra torch pytest
```

Result:

- Targeted Ruff: passed.
- New tests: 5 passed.
- Neighbor tests: 18 passed.
- Full Ruff: passed.
- Full pytest: 283 passed.

## Result

F2 now has an executable federated benchmark protocol. Sites can submit
leaderboard-compatible metric rows without sharing raw windows, while the report
keeps site heterogeneity visible and blocks citable summaries until every site
row is Gate C passed, leakage-clean, and frozen.
