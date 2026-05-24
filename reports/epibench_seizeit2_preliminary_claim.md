# EpiBench Claim Eligibility Report

Run: `seizeit2_sub125_random_preliminary`  
EpiBench version: `v1.0-draft`  
Requested claim: `E2-PI`  
Final claim: `E1`  
Epi-Score: `6.294`

## Badges

`EpiBench-Dataset-T3` `EpiBench-Run-Complete` `EpiBench-Failure-Transparent` `EpiBench-Claim-E1`

## Claim Ceilings

- dataset_tier: `E1`
- split_policy: `E1`
- label_audit: `E1`
- leakage_audit: `E1`
- threshold_policy: `E4`
- failure_status: `E1`
- hardware_evidence: `E4`
- track_consistency: `E4`

## Score Axes

- performance: 0.300
- clinical_safety: 0.050
- robustness: 0.050
- stability: 0.100
- latency: 0.500
- calibration: 0.300

Floor penalty applied: `True`

## Dataset Tier Evaluation

- Declared tier: `T3`
- Effective tier: `T3`
- MTS mean: `0.857`
- MTS item floor: `0`
- Missing core MTS items: `acquisition_protocol, synchronization`
- Downgraded: `False`

## Blocking Reasons

- Blocking sentinel present: LABEL_UNAUDITED.
- Blocking sentinel present: SPLIT_NONCOMPLIANT.
- Split leakage audit did not pass.

## Forbidden Phrases

- None

## Certification Boundary

EpiBench-certified means scientifically certified under EpiBench evidence rules. It does not mean
clinically approved, clinically safe, regulatory approved, or ready for deployment as a medical
device.
