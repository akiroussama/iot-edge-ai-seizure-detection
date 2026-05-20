# Claude Code prompts

## Prompt 1 — connect SeizeIT2 parser

Implement the real SeizeIT2 parser using the official dataset structure. Produce canonical parquet tables:

- metadata.parquet
- events.parquet
- windows.parquet
- modality_availability.parquet

Do not train models. Add tests with a small fixture. Validate time zones and event onset/end parsing.

## Prompt 2 — connect My Seizure Gauge parser

Implement MSG parser for HR/steps and seizure events. Produce hourly and daily forecasting windows. Add rolling-origin split.

## Prompt 3 — strict leakage review

Review the repository for:
- feature leakage;
- label leakage;
- patient contamination;
- postictal contamination;
- event-level metric bugs.

Return patches and tests only.

## Prompt 4 — EpiTwin-SSL training

Implement a real trainer for EpiTwinSSL with:
- modality dropout;
- masked reconstruction;
- future latent prediction;
- hazard head;
- validation metrics;
- checkpointing;
- config-driven runs.
