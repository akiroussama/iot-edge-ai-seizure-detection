# EpiBench Figure And Table Blueprint

## Main Figures

### Figure 1 - EpiBench Evidence Architecture

Panels:

- A: dataset evidence card;
- B: split and label audit;
- C: model output and failures;
- D: Epi-Score;
- E: claim gate.

Message:

> A leaderboard row is not the result; the evidence package is the result.

### Figure 2 - Task Separation Timeline

Panels:

- detection after or near onset;
- early warning before a useful deadline;
- forecasting with SPH/SOP;
- embedded viability path.

Message:

> Detection, early warning, and forecasting are different scientific questions.

### Figure 3 - Dataset Evidence Card

Panels:

- MTS rubric;
- DSI rubric;
- tier assignment;
- claim ceiling.

Message:

> Data quality and domain stress are measured separately.

### Figure 4 - Claim Gate Waterfall

Show requested claim reduced by:

- dataset tier;
- split;
- label audit;
- leakage;
- failures;
- hardware.

Message:

> Claim is determined by the weakest evidence component.

### Figure 5 - Naive Versus EpiBench Ranking

Panels:

- naive leaderboard by sensitivity/F1;
- Epi-Score leaderboard;
- claim-gated leaderboard.

Message:

> Better naive metrics can correspond to weaker scientific evidence.

### Figure 6 - Failure Heatmap

Rows:

- models or runs.

Columns:

- failure sentinels.

Message:

> Failures remain visible and interpretable.

## Main Tables

### Table 1 - Relationship To Existing Standards

Columns:

- standard or dataset;
- role;
- ADOPT/MAP/EXTEND/DIVERGE;
- EpiBench field affected.

### Table 2 - Claim Eligibility Matrix

Rows:

- dataset tier;
- split type;
- label audit;
- failure state;
- external validation.

Columns:

- maximum claim.

### Table 3 - Pilot Evidence Packages

Columns:

- dataset;
- track;
- sensor;
- labels;
- split;
- MTS;
- DSI;
- claim ceiling.

### Table 4 - Worked Example Results

Columns:

- model;
- sensitivity;
- precision;
- FAR/24h;
- latency;
- Epi-Score;
- failures;
- final claim.

## Supplementary Figures

- JSON Schema dependency graph.
- CLI workflow.
- Epi-Score weight sensitivity.
- Inter-reviewer MTS/DSI agreement.
- Per-patient performance distribution.

## Rule

Every figure in the paper should be generated from an artefact or have a clear trace to a validated artefact. Avoid hand-drawn claims that cannot be reproduced.
