# End-to-end execution map

This is the “without stopping” map. Some stages are executable immediately; others wait for datasets, A100 access, or clinical validation.

## Executable here

- Build benchmark scaffold.
- Validate SPH/SOP labels on synthetic data.
- Validate clinical metrics.
- Validate calibration and alarm controller.
- Validate EpiTwin-SSL model forward pass.
- Validate edge student and distillation loss.
- Generate synthetic report.
- Package repository.

## Requires local public datasets

- Real SeizeIT2 parsing.
- Real My Seizure Gauge parsing.
- Real SPH/SOP label distribution.
- Real random baseline.
- Real TCN/SSL experiments.

## Requires A100

- Full EpiTwin-SSL pretraining.
- Long ablation sweeps.
- Large foundation model experiments.

## Requires human scientific decision

- Choice of horizons.
- Manual audit of labels around seizures.
- Freeze of splits.
- Claim audit before paper submission.

## Requires new data collection

- Tibia/wrist claims.
- Prospective IoT validation.
- Closed-loop intervention claims.
