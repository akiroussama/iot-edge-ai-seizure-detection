# EpiBench Local Data Inventory

Date: 2026-05-24  
Purpose: identify which local assets can currently support submission-grade EpiBench evidence packages.

## Inventory Result

| Asset | Local evidence | Usable now? | Maximum defensible role |
| --- | --- | --- | --- |
| MSG raw + processed Gate C | raw ZIPs, processed tables, Gate C frozen registry, null benchmark manifest | yes | Track `F` forecasting package, `E2-PD` ceiling |
| CHB-MIT official metadata | PhysioNet RECORDS, RECORDS-WITH-SEIZURES, SUBJECT-INFO, chbXX summaries | yes | Track `D` metadata/null-baseline package, `E2-PI` evidence structure |
| SeizeIT2 local reports | readiness reports and single-subject audit artefacts only | no | preliminary negative/readiness example, `E1` |
| CHB-MIT EDF waveforms | no local full EDF archive found | no | future Track `D` signal-derived EEG detection package |
| TUSZ/TUH | no local raw or processed data found | no | future Track `D` EEG detection package |

## Consequence

The local evidence set now contains two real EpiBench packages: MSG Gate C forecasting (`E2-PD`) and CHB-MIT metadata-based EEG detection (`E2-PI`). The CHB-MIT package is structurally patient-independent but remains a null-baseline metadata package, not a waveform detector.

## Evidence Checked

Local data directory contains:

- `data/raw/msg/*.zip`;
- `data/processed/msg/*.parquet`;
- `data/processed/msg/gate_c_inputs_sph60_sop1440/*.csv`;
- CHB-MIT metadata files under `data/raw/chbmit_metadata/`;
- no local full CHB-MIT EDF waveform archive or TUSZ/TUH files.

Local reports contain:

- MSG Gate C frozen benchmark manifest and audit artefacts;
- SeizeIT2 readiness and guardrail reports indicating the locally available subset is insufficient for submission-grade evidence;
- no EEG detection evidence package.

## Decision

Do not present the CHB-MIT metadata package as a useful EEG detector. It is a real `E2-PI` evidence-structure package and a null-baseline control. A stronger Q1 package requires raw or processed EEG waveforms, frozen patient-independent splits, signal-derived predictions, event-level metrics, and a failure trace.

The next implementation milestone is therefore CHB-MIT EDF subset/full materialization for a simple signal baseline, or TUSZ acquisition for a higher-prestige but heavier external benchmark.
