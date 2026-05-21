# M1 Sparse Autoencoder Interpretability

Date: 2026-05-21

Branch: `codex/sparse-autoencoder-interpretability`

Base: `origin/main@5f1f7a3`

## Objective

Add the first mechanistic-interpretability layer for EpiTwin-Open: a sparse
autoencoder (SAE) report that consumes hidden activation tables and produces a
dictionary of sparse features, per-window SAE activations, and post-hoc clinical
associations.

This task does not train on real frozen model activations and does not claim
that any discovered SAE feature is clinically valid. It provides the auditable
infrastructure needed to run that analysis after Gate C artifacts and trained
models exist.

## Implementation

- Added `src/interpretability/sparse_autoencoder.py`.
- Added `src/interpretability/__init__.py`.
- Added CLI `scripts/run_sparse_autoencoder_interpretability.py`.
- Added config contract `configs/model/sparse_autoencoder.yaml`.
- Added synthetic tests in `tests/test_sparse_autoencoder_interpretability.py`.

The CLI writes:

- `sae_feature_scores.csv`
- `sae_dictionary.csv`
- `sae_associations.csv`
- `sae_manifest.csv`
- `sae_report.json`
- `sae_report.md`

## Scientific Guardrails

- SAE training uses activation columns only.
- Default activation-column selection excludes IDs, labels, prediction outputs,
  split metadata, and explicit temporal leakage columns.
- Labels and risks are used only after training for post-hoc association
  tables.
- Associations are explicitly marked `post_hoc_not_causal`.
- The fit split controls which rows train the SAE.
- Optional prediction tables must align exactly with activation rows.
- If labels exist in both activation and prediction tables, mismatches raise.
- Training artifacts include activation-table, activation-column, and training
  hashes.
- Label-flip regression tests verify that unsupervised SAE scores, dictionary,
  and artifact hash do not change when held-out labels change.

## Validation

Executed targeted validation:

```bash
uv run --extra dev ruff check src/interpretability/__init__.py src/interpretability/sparse_autoencoder.py scripts/run_sparse_autoencoder_interpretability.py tests/test_sparse_autoencoder_interpretability.py
uv run --extra dev pytest tests/test_sparse_autoencoder_interpretability.py
uv run --extra dev --extra torch pytest tests/test_sparse_autoencoder_interpretability.py tests/test_supervised_ladder.py tests/test_models.py
```

Executed full validation:

```bash
uv run --extra dev ruff check .
uv run --extra dev --extra torch pytest
```

Result:

- Targeted Ruff: passed.
- Targeted pytest: 5 passed.
- Neighbor pytest with Torch: 17 passed.
- Full Ruff: passed.
- Full pytest: 234 passed.

## Remaining Limits

- The SAE implementation is intentionally small and deterministic; large-scale
  interpretability runs may later need a Torch implementation with monitoring.
- No real activation table is analyzed in this task.
- SAE features are not automatically clinical concepts. They require Gate C
  frozen artifacts, trained encoders, clinician review, ablation, and
  robustness checks before paper claims.
- Post-hoc associations are not causal explanations.
