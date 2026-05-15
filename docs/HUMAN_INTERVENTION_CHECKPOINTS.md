# Human intervention checkpoints

You should intervene at these points. Do not let automation skip them.

## Checkpoint 1 — SPH/SOP clinical choice

Recommended initial horizons:
- SeizeIT2: SPH 5 min / SOP 30 min.
- SeizeIT2 secondary: SPH 1 / SOP 5 and SPH 15 / SOP 30.
- My Seizure Gauge: hourly risk.

## Checkpoint 2 — Manual label audit

Inspect at least 5–10 seizures:
- Confirm seizure onset/end.
- Confirm positive windows are inside `[window_end + SPH, window_end + SPH + SOP)`.
- Confirm ictal windows are excluded.
- Confirm postictal windows are excluded.
- Confirm no future information is used in features.

## Checkpoint 3 — Split freeze

Freeze:
- patient-wise split;
- temporal split per patient;
- center-wise split if center metadata is present.

No random window split is allowed as a primary result.

## Checkpoint 4 — A100 launch

Launch A100 training only after:
- tests pass;
- labels are manually audited;
- random baseline exists;
- leakage audit passes;
- clinical metrics are computed.

## Checkpoint 5 — Claim audit before writing

Allowed:
- “forecastability-aware risk estimation”.
- “calibrated alarm budgets”.
- “observable-latent distillation”.

Forbidden:
- “we predict all seizures”.
- “tibia works” without tibia data.
- “closed-loop VNS” without clinical protocol.
