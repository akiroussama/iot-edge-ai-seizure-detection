# T18 Clinical Utility Analysis

Date: 2026-05-21

Branch: `codex/clinical-utility`

Base: `origin/main@a34e545`

## Objective

Translate model scores and alarm metrics into configurable decision-support
tradeoffs. This complements calibration, conformal intervals, and the
forecastability atlas by showing how sensitivity changes under alarm burden,
warning-time, lead-time, and optional BSS assumptions.

The output is not a clinical recommendation. It is a transparent utility table
that makes the assumptions explicit and easy to challenge.

## Implementation

- Added `src/reports/clinical_utility.py`.
- Exported utility helpers from `src/reports/__init__.py`.
- Added CLI `scripts/make_clinical_utility_report.py`.
- Added synthetic tests in `tests/test_clinical_utility.py`.

The utility score is additive:

```text
benefit * sensitivity
- missed_event_cost * (1 - sensitivity)
- false_alarm_cost_per_day * FAR/day
- warning_time_cost * TIW
+ lead_time_bonus_per_hour * lead_time_hours
+ brier_skill_score_weight * BSS
```

All terms are configurable from the CLI.

## Alarm Policy Logic

The module also adds `apply_refractory_alarm_policy`, which suppresses follow-up
alarms within a configurable refractory period after a kept alarm episode. This
supports alarm-policy analysis without pretending that every high-risk window
should become a distinct clinical interruption.

## Guardrails

- The report says "decision-support analysis", not recommendation.
- The selected row is named `selected_under_assumptions`, because changing
  costs or constraints may change the selected policy.
- Citable report status requires `gate_c_status=passed`.
- Pre-Gate-C outputs remain exploratory and not citable.

## Validation

Executed targeted validation:

```bash
uv run --extra dev ruff check src/reports/clinical_utility.py src/reports/__init__.py scripts/make_clinical_utility_report.py tests/test_clinical_utility.py
uv run --extra dev pytest tests/test_clinical_utility.py tests/test_alarm_controller.py tests/test_threshold_sweep_cli.py
uv run --extra dev ruff check .
uv run --extra dev --extra torch pytest
```

Result:

- Targeted Ruff: passed.
- Targeted pytest: 11 passed.
- Full Ruff: passed.
- Full pytest: 187 passed.

## Remaining Limits

- Utility weights are assumptions, not clinical truth.
- This layer consumes threshold-sweep artifacts; it does not replace clinical
  validation.
- Real-data utility tables before Gate C remain non-citable.
- The refractory policy is a transparent engineering policy, not a validated
  patient-care protocol.
