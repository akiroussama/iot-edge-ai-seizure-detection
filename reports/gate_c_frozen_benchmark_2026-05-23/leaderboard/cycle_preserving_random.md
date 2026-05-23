# Leaderboard Row - msg_gate_c_sph60_sop1440_2026-05-23__cycle_preserving_random__test


## Identity

- Dataset: `msg`
- Task: `forecasting`
- Model: `cycle_preserving_random`
- Split: `test` / `temporal_recording`
- Horizon: `SPH60_SOP1440`

## Denominator

- Source events: `768`
- Events after filter: `510`
- Events used for metrics: `54`
- Valid prediction rows: `1418`
- Observable prediction rows: `None`
- Deficient prediction rows: `None`
- Abstained prediction rows: `None`
- Deficiency time minutes: `None`

## Metrics

- Sensitivity: `0.7407407407407407`
- Forecasted/detected: `40`
- FAR/day: `0.5923836389280677`
- TIW: `0.09732016925246827`
- Brier score: `0.22237042583524766`
- Brier Skill Score: `0.06953434996389507`
- ECE: `0.19091797503053085`

## Gates

- Label audit: `sampled_human_attested`
- Gate B: `passed`
- Gate C: `passed`
- Leakage: `clean`
- Split frozen: `frozen_git_tag`

## Evidence

- Commit: `391bca3a05d0`
- Evidence URI: `reports/gate_c_msg_freeze_2026-05-23/gate_c_registry.json`
- Notes: `Frozen MSG null baseline row; source DOI is not a newly minted benchmark DOI. Event metrics use matched prediction-coverable events.`
