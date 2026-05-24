# EpiBench Claim Eligibility Report

Run: `leakage_high_metric_demo`  
EpiBench version: `v1.0-draft`  
Requested claim: `E3`  
Final claim: `E1`  
Epi-Score: `94.727`

## Badges

`EpiBench-Dataset-T1` `EpiBench-Run-Complete` `EpiBench-Failure-Transparent` `EpiBench-Claim-E1`

## Claim Ceilings

- dataset_tier: `E2-PI`
- split_policy: `E2-PI`
- label_audit: `E4`
- leakage_audit: `E1`
- threshold_policy: `E1`
- failure_status: `E1`
- hardware_evidence: `E4`
- track_consistency: `E4`

## Score Axes

- performance: 0.980
- clinical_safety: 0.950
- robustness: 0.920
- stability: 0.900
- latency: 0.950

Floor penalty applied: `False`

## Dataset Tier Evaluation

- Declared tier: `T1`
- Effective tier: `T1`
- MTS mean: `2.833`
- MTS item floor: `2`
- Missing core MTS items: `None`
- Downgraded: `False`

## Blocking Reasons

- Blocking sentinel present: PATIENT_LEAKAGE.
- Blocking sentinel present: SPLIT_NONCOMPLIANT.
- Split leakage audit did not pass.
- Threshold selection uses test labels.

## Forbidden Phrases

- None

## Certification Boundary

EpiBench-certified means scientifically certified under EpiBench evidence rules. It does not mean
clinically approved, clinically safe, regulatory approved, or ready for deployment as a medical
device.
