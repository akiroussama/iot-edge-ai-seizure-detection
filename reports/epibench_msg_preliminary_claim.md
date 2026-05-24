# EpiBench Claim Eligibility Report

Run: `msg_cycle_preserving_random_preliminary`  
EpiBench version: `v1.0-draft`  
Requested claim: `E2-PD`  
Final claim: `E1`  
Epi-Score: `50.024`

## Badges

`EpiBench-Dataset-T3` `EpiBench-Run-Complete` `EpiBench-Failure-Transparent` `EpiBench-Claim-E1` `EpiBench-Leakage-Checked`

## Claim Ceilings

- dataset_tier: `E1`
- split_policy: `E2-PD`
- label_audit: `E1`
- leakage_audit: `E4`
- threshold_policy: `E4`
- failure_status: `E1`
- hardware_evidence: `E4`
- track_consistency: `E4`

## Score Axes

- performance: 0.650
- clinical_safety: 0.700
- robustness: 0.350
- stability: 0.450
- latency: 0.500
- calibration: 0.550

Floor penalty applied: `True`

## Dataset Tier Evaluation

- Declared tier: `T2`
- Effective tier: `T3`
- MTS mean: `1.143`
- MTS item floor: `0`
- Missing core MTS items: `synchronization, missingness`
- Downgraded: `True`

## Blocking Reasons

- Blocking sentinel present: LABEL_UNAUDITED.
- Declared dataset tier exceeded effective MTS-derived tier; certification used effective tier.

## Forbidden Phrases

- None

## Certification Boundary

EpiBench-certified means scientifically certified under EpiBench evidence rules. It does not mean
clinically approved, clinically safe, regulatory approved, or ready for deployment as a medical
device.
