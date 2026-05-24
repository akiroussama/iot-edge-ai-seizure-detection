# EpiBench Claim Eligibility Report

Run: `early_warning_post_event_failure_demo`  
EpiBench version: `v1.0-draft`  
Requested claim: `E2-PI`  
Final claim: `E1`  
Epi-Score: `81.860`

## Badges

`EpiBench-Dataset-T1` `EpiBench-Run-Complete` `EpiBench-Failure-Transparent` `EpiBench-Claim-E1` `EpiBench-Leakage-Checked`

## Claim Ceilings

- dataset_tier: `E2-PI`
- split_policy: `E2-PI`
- label_audit: `E4`
- leakage_audit: `E4`
- threshold_policy: `E4`
- failure_status: `E1`
- hardware_evidence: `E4`
- track_consistency: `E4`

## Score Axes

- performance: 0.880
- clinical_safety: 0.820
- robustness: 0.780
- stability: 0.760
- latency: 0.840
- calibration: 0.720

Floor penalty applied: `False`

## Dataset Tier Evaluation

- Declared tier: `T1`
- Effective tier: `T1`
- MTS mean: `2.833`
- MTS item floor: `2`
- Missing core MTS items: `None`
- Downgraded: `False`

## Blocking Reasons

- Early-warning track contains post-event alarms counted as success.

## Forbidden Phrases

- None

## Certification Boundary

EpiBench-certified means scientifically certified under EpiBench evidence rules. It does not mean
clinically approved, clinically safe, regulatory approved, or ready for deployment as a medical
device.
