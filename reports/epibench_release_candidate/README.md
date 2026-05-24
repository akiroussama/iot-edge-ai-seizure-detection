# EpiBench Release Candidate Reproduction Packet

Status: `passed`

## Purpose

This packet turns the current EpiBench checkout into a reproducible release-candidate artefact. It
checks that reference claim reports can be regenerated from result bundles and that core normative files
have stable checksums.

## One-Command Reproduction

```powershell
python scripts\epibench_reproduce_release_candidate.py
```

## Claim Reproduction

- `pilot_t1_eeg`: matched=`True`, final_claim=`E2-PI`, epi_score=`74.158`
- `chbmit_waveform_micro_d`: matched=`True`, final_claim=`E2-PI`, epi_score=`7.529`
- `msg_gate_c_frozen_f`: matched=`True`, final_claim=`E2-PD`, epi_score=`58.984`
- `far_explosion_failure_d`: matched=`True`, final_claim=`E1`, epi_score=`19.629`

## Release Boundary

- DOI status: `pending_zenodo_deposition`;
- external reproduction status: `pending_external_lab_run`;
- generation base commit: `417fd082ac9b03c37c884e7e6526df309ed736fc`;
- git commit boundary: The report cannot embed the final commit that contains itself. The final archive or Git tag is the authoritative source commit.
- boundary: This package verifies scientific reproducibility of EpiBench artefacts from the checkout. It is not clinical validation, regulatory clearance, or a DOI minting event.

This is a scientific release-candidate packet, not clinical approval and not regulatory certification.
