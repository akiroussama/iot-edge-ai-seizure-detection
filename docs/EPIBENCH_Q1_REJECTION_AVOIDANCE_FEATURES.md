# EpiBench Q1 Rejection-Avoidance Features

## Purpose

This document records the three highest-risk reviewer objections and the concrete protocol features implemented to reduce rejection risk. It is not a claim that the paper is submission-ready. It is a traceability map from reviewer risk to executable evidence.

## Feature 1 - Submission-Grade Evidence Package Gate

Reviewer risk:

> The framework is only conceptual or demo-based; it has not been validated on real evidence packages.

Implemented artefacts:

- `configs/epibench/submission_readiness_gate_v1.yaml`
- `src/epibench/submission_readiness.py`
- CLI command: `epibench assess-submission-readiness`
- Report: `reports/epibench_submission_readiness_report.json`

Command:

```powershell
python scripts\epibench.py assess-submission-readiness `
  --bundle examples\epibench\msg_preliminary_f\result_bundle.yaml `
  --bundle examples\epibench\seizeit2_preliminary_f\result_bundle.yaml `
  --out reports\epibench_submission_readiness_report.json
```

Current result:

- status: `failed`;
- submission-grade packages: `0`;
- operational packages at `E2-PI` or higher: `0`.

Scientific interpretation:

The feature is working precisely because it refuses to treat the current MSG and SeizeIT2 preliminary packages as Q1-ready operational evidence. This prevents a likely reviewer rejection for overclaiming.

Remaining work:

- upgrade or add one EEG detection package, preferably TUSZ or CHB-MIT;
- upgrade SeizeIT2 to a multi-patient package;
- obtain label audit and split audit sufficient for at least one `E2-PI` package.

## Feature 2 - SzCORE-Compatible Import

Reviewer risk:

> EpiBench reinvents existing seizure event scoring instead of reusing it.

Implemented artefacts:

- `src/epibench/szcore_bridge.py`
- CLI command: `epibench map-szcore`
- CLI command: `epibench import-szcore`
- Demo input: `examples/epibench/szcore_bridge_demo/szcore_event_metrics.yaml`
- Imported bundle: `examples/epibench/szcore_bridge_demo/imported_result_bundle.yaml`
- Claim report: `reports/epibench_szcore_import_claim.json`

Command:

```powershell
python scripts\epibench.py import-szcore `
  --metrics examples\epibench\szcore_bridge_demo\szcore_event_metrics.yaml `
  --dataset-card examples\epibench\pilot_t1_eeg\dataset_card.yaml `
  --split-manifest examples\epibench\pilot_t1_eeg\split_manifest.yaml `
  --failure-trace examples\epibench\szcore_bridge_demo\import_failure_trace.yaml `
  --run-id szcore_import_demo `
  --requested-claim E2-PI `
  --model-name szcore_import_demo_model `
  --model-family external_event_scorer `
  --commit-sha external-commit-sha `
  --subscore performance=0.76 `
  --subscore clinical_safety=0.72 `
  --subscore robustness=0.70 `
  --subscore stability=0.68 `
  --subscore latency=0.75 `
  --out examples\epibench\szcore_bridge_demo\imported_result_bundle.yaml
```

Scientific interpretation:

EpiBench does not replace SzCORE-style event scoring. It maps compatible event metrics into an evidence bundle, then adds dataset tiering, split validation, failure preservation, claim gates, and anti-overclaim language.

Remaining work:

- replace the demo SzCORE-style YAML with a real output from the official scoring tool or an explicitly documented compatible export.

## Feature 3 - Inter-Reviewer Agreement Report For MTS/DSI

Reviewer risk:

> MTS and DSI are subjective rubrics that may not reproduce across reviewers.

Implemented artefacts:

- `src/epibench/inter_reviewer.py`
- CLI command: `epibench inter-reviewer-report`
- Review file: `examples/epibench/inter_reviewer_reviews.yaml`
- Report: `reports/epibench_inter_reviewer_report.json`

Command:

```powershell
python scripts\epibench.py inter-reviewer-report `
  examples\epibench\inter_reviewer_reviews.yaml `
  --out reports\epibench_inter_reviewer_report.json
```

Current result:

- status: `passed`;
- two datasets reviewed;
- claim ceiling agreement reached for both;
- no MTS/DSI item differs by more than one point.

Scientific interpretation:

This is a protocol demonstration, not a substitute for a real independent clinical review. It proves that the agreement calculation is executable and that a submission can include a reviewer-agreement table.

Remaining work:

- replace the proxy review with true independent reviewers, including a neurologist or clinical neurophysiologist.

## Bottom Line

The protocol is now better protected against three high-probability Q1 rejection paths:

1. demo-only evidence;
2. reinvention of event scoring;
3. subjective Evidence Cards.

The current evidence still does not justify submission to a top Q1 venue. The standard now has the mechanisms required to tell us that honestly.
