# Clinical Language Checklist

The reviewer should mark each statement as `allowed`, `soften`, or `blocked`.

## Block Unless Prospective Clinical Evidence Exists

- The model is clinically approved.
- The model is ready for deployment.
- The system is clinically safe.
- EpiBench certification means medical-device certification.
- The detector generalizes to real-world home monitoring.

## Block Unless External Or Multisite Evidence Exists

- The result is generalizable.
- The model is state of the art.
- The detector works across patients.
- The model is robust to seizure-type diversity.

## Block Unless Hardware Evidence Exists

- The model is real-time.
- The model is edge-ready.
- The detector is suitable for on-device IoT deployment.
- The alarm latency is clinically actionable.

## Preferred Bounded Wording

- Scientifically certified under EpiBench v1.0 for the declared evidence package.
- Claim-limited to the declared dataset, sensor, split, label audit, and failure policy.
- Retrospective evidence, not prospective clinical evidence.
- External validation remains required for E3 or higher claims.
