# Leaderboard Row - msg_gate_c_sph60_sop1440_2026-05-23__patient_prior__test


## Identity

- Dataset: `msg`
- Task: `forecasting`
- Model: `patient_prior`
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

- Sensitivity: `0.05555555555555555`
- Forecasted/detected: `3`
- FAR/day: `0.0846262341325811`
- TIW: `0.0380818053596615`
- Brier score: `0.1276733800426928`
- Brier Skill Score: `0.4657756574080335`
- ECE: `0.13101441631256677`

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
