# T15 Foundation-Model Transfer Protocol

Date: 2026-05-22

Branch: `codex/foundation-transfer-protocol`

Base: `origin/main@242afde`

## Objective

Add a rigorous transfer baseline path for wearable foundation-model embeddings.
The goal is to compare frozen external representations under the EpiTwin
benchmark without claiming that this project trained a foundation model.

## Research Context

- ICLR 2024: "Large-scale Training of Foundation Models for Wearable
  Biosignals" trains PPG/ECG foundation models on large longitudinal wearable
  biosignal data.
- PaPaGei/ICLR 2025 context: open PPG foundation models make transfer baselines
  increasingly relevant for wearable benchmarking.

## Implementation Plan

- Add `src/features/foundation_transfer.py` to attach frozen embeddings to
  existing window-feature rows.
- Add a CLI that writes merged features, manifest JSON/CSV, and a Markdown
  provenance report.
- Reject embedding tables containing labels, alarms, split assignments, or
  future-event timing columns.
- Require source URL/DOI, license name, modality, and explicit license research
  permission before use.
- Keep outputs non-citable before Gate C.

## Scientific Guardrails

- Embedding generation must not read labels.
- License and modality compatibility are mandatory.
- Transfer rows are baselines, not a new foundation model.
- Gate C frozen artifacts are required before citable comparisons.

## Validation Log

Targeted validation:

```bash
uv run --extra dev ruff check src/features/foundation_transfer.py src/features/__init__.py scripts/prepare_foundation_transfer_features.py tests/test_foundation_transfer.py
uv run --extra dev pytest tests/test_foundation_transfer.py
uv run --extra dev --extra torch pytest tests/test_foundation_transfer.py tests/test_supervised_ladder.py tests/test_models.py
```

Full validation:

```bash
uv run --extra dev ruff check .
uv run --extra dev --extra torch pytest
```

Result:

- Targeted Ruff: passed.
- New tests: 5 passed.
- Neighbor tests with Torch: 17 passed.
- Full Ruff: passed.
- Full pytest: 278 passed.

## Result

Task15 now has an executable frozen-embedding transfer protocol. External
wearable foundation embeddings can be attached to EpiTwin feature rows only when
source provenance, license permission, modality, and leakage guardrails are
explicitly satisfied.
