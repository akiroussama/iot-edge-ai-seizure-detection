# P1 Test-Time Adaptation

Date: 2026-05-21

Branch: `codex/test-time-adaptation`

Base: `origin/main@8476e8f`

## Objective

Add a leakage-safe test-time adaptation layer for standardized seizure-risk
prediction tables. The first implementation is score-level adaptation:
patient-specific rolling-origin rank blending based only on past unlabeled risk
scores.

This is intentionally narrower than updating a deep network online. It is a
defensible first P1 layer because it is compatible with every prediction table
already produced by the benchmark stack and can be tested for future leakage.

## Implementation

- Added `src/adaptation/test_time.py`.
- Added `src/adaptation/__init__.py`.
- Added CLI `scripts/run_test_time_adaptation.py`.
- Added config contract `configs/model/test_time_adaptation.yaml`.
- Added synthetic tests in `tests/test_test_time_adaptation.py`.

The CLI writes:

- `tta_predictions.csv`
- `tta_summary.csv`
- `tta_manifest.csv`
- `tta_report.json`
- `tta_report.md`

## Method

For each patient, windows are sorted by time. The current risk score is blended
with its empirical rank among that patient's previous risk scores:

```text
adapted_risk = (1 - alpha) * current_risk + alpha * rolling_history_rank
```

The history buffer contains only earlier non-excluded rows from the same
patient. No label, seizure timestamp, or future score is used.

## Scientific Guardrails

- `forecast_label` is never read by the adaptation rule.
- Future windows are never read when adapting an earlier window.
- The tests flip labels and verify identical adapted risks and alarms.
- The tests perturb future scores and verify earlier adapted risks are
  unchanged.
- The original model outputs are preserved as `pre_tta_risk_score` and
  `pre_tta_alarm`.
- The adapted score replaces `risk_score` for downstream runner compatibility.
- Outputs carry `tta_leakage_status =
  rolling_origin_past_unlabeled_scores_only`.
- Reports remain pre-Gate-C and not citable as benchmark results.

## Validation

Executed targeted validation:

```bash
uv run --extra dev ruff check src/adaptation/__init__.py src/adaptation/test_time.py scripts/run_test_time_adaptation.py tests/test_test_time_adaptation.py
uv run --extra dev pytest tests/test_test_time_adaptation.py
uv run --extra dev pytest tests/test_test_time_adaptation.py tests/test_leaderboard_runner.py tests/test_calibration_thresholding.py tests/test_supervised_ladder.py
```

Executed full validation:

```bash
uv run --extra dev ruff check .
uv run --extra dev --extra torch pytest
```

Result:

- Targeted Ruff: passed.
- Targeted pytest: 6 passed.
- Neighbor pytest: 22 passed.
- Full Ruff: passed.
- Full pytest: 240 passed.

## Remaining Limits

- This is score-level TTA, not neural weight adaptation or batch-norm
  adaptation.
- The method can improve personalization only if the model's own score
  distribution carries patient-specific information.
- Citable claims require Gate C frozen artifacts, null-corrected comparison,
  calibration checks, and clinical utility analysis.
- Future work can add activation-level or model-weight TTA behind the same
  no-label/no-future contract.
