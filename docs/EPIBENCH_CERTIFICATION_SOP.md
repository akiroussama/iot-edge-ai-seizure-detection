# EpiBench Certification Standard Operating Procedure

## Purpose

This SOP defines how an external group certifies a result under EpiBench. It is written for reproducibility reviewers, not for marketing.

## Certification Boundary

EpiBench certification is scientific certification of a result bundle under a versioned protocol. It is not:

- clinical approval;
- regulatory approval;
- medical-device certification;
- safety certification;
- deployment readiness.

## Required Inputs

Certification requires:

1. Dataset Evidence Card.
2. Split Manifest.
3. Failure Trace.
4. Result Bundle.
5. Normative EpiBench YAML.
6. JSON Schemas.
7. Reference implementation or compatible independent implementation.

Optional but expected for publication:

- SOTA registry entry;
- evidence package README;
- checksums;
- raw-to-processed trace;
- figure generation script;
- reviewer adjudication log.

## Procedure

### Step 1 - Validate Artefact Structure

Run:

```powershell
python scripts\epibench.py validate-dataset-card path\to\dataset_card.yaml
python scripts\epibench.py validate-split path\to\split_manifest.yaml
python scripts\epibench.py validate-failure-trace path\to\failure_trace.yaml
python scripts\epibench.py validate-result-bundle path\to\result_bundle.yaml
```

If any validation fails, certification stops.

### Step 2 - Compute Effective Dataset Tier

The declared tier is not sufficient.

The CLI computes:

- declared tier;
- effective tier;
- MTS mean;
- MTS item floor;
- missing core MTS items;
- downgrade status.

The effective tier controls the claim. A declared `T1` can become effective `T2` or `T3`.

### Step 3 - Apply Claim Gates

The CLI computes ceilings from:

- effective dataset tier;
- split policy;
- label audit;
- leakage audit;
- threshold selection policy;
- failure status;
- hardware evidence;
- track consistency.

The final claim is the lowest supported claim.

### Step 4 - Generate Report

Run:

```powershell
python scripts\epibench.py certify path\to\result_bundle.yaml --out claim_report.json --report claim_report.md
```

The JSON report is canonical. The Markdown report is for human inspection.

### Step 5 - Run Conformance Suite

Before publication or release:

```powershell
python scripts\epibench.py run-conformance-suite configs\epibench\conformance_suite_v1.yaml
```

If the suite fails, do not publish EpiBench-certified claims.

### Step 6 - Human Review

For paper-grade evidence, at least two reviewers should inspect:

- Dataset Evidence Card;
- MTS/DSI scores;
- label audit;
- split policy;
- failure trace;
- anti-overclaim language.

Clinical claims require clinical review, even when EpiBench returns a high scientific claim.

## Output Package

A certified package must include:

- original artefacts;
- claim report JSON;
- rendered claim report Markdown;
- conformance suite result;
- software version;
- commit SHA;
- reproduction command;
- known limitations.

## Rejection Conditions

Certification must fail or downgrade if:

- required artefacts are missing;
- schema validation fails;
- dataset tier is overdeclared;
- split is noncompliant;
- threshold uses test labels;
- leakage is detected;
- labels are unaudited for an operational claim;
- failure trace is absent;
- hardware wording is used without hardware evidence.

## Auditor Checklist

- [ ] Artefacts validate.
- [ ] Effective tier is not higher than evidence supports.
- [ ] Split supports the requested claim.
- [ ] Label audit supports the requested claim.
- [ ] Failure trace is complete.
- [ ] Conformance suite passes.
- [ ] Report includes certification boundary.
- [ ] Manuscript language does not exceed final claim.
