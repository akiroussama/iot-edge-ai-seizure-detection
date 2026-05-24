# EpiBench Reviewer Attack Defense Matrix

## Purpose

This document anticipates major reviewer objections for a high-selectivity Q1 submission and defines the evidence required to neutralize each objection.

## Attack Matrix

| Reviewer attack | Severity | Current defense | Missing evidence | Required fix |
| --- | --- | --- | --- | --- |
| This is not a clinical validation study | High | Explicit certification boundary | Stronger wording in abstract/cover letter | State that EpiBench certifies evidence packages, not clinical safety |
| This is just another benchmark | High | Claim gates and failure traces | Stronger comparison to existing benchmarks | Add table: metric benchmark vs evidence certification |
| You reinvent SzCORE | High | SOTA registry says MAP and executable import exists | Replace demo export with official tool output | Add real Track D compatibility example from official output |
| MTS/DSI are subjective | High | Rubrics exist and inter-reviewer report generator exists | True independent clinical review missing | Run real two-reviewer card scoring |
| Demonstration examples are synthetic | High | Labeled as protocol demos | Real datasets missing | Add TUSZ/CHB-MIT and SeizeIT2 packages |
| Epi-Score weights are arbitrary | Medium | YAML preregistration | Sensitivity analysis missing | Add weight perturbation supplement |
| Claims may be misused as clinical approval | High | Strong anti-overclaim language | Badge wording may still be risky | Use "scientific claim eligibility" consistently |
| Patient-dependent claim is still ambiguous | Medium | E2-PD/E2-PI split | More examples needed | Add one E2-PD test case |
| Edge readiness not proven | Medium | Hardware gate exists | Real hardware result missing | Measure hardware or avoid edge demonstration claim |
| Too much software, not enough science | High | Epistemic thesis strong | Manuscript must lead with evidence problem | Rewrite introduction around scientific validity |
| No external validation | High | E3 gated | Real E3 example missing | Either add external example or state E3 is supported by framework only |
| Dataset tiering may penalize useful small datasets | Medium | T2/T3 allow exploratory use | Discussion missing nuance | Add section on exploratory science without overclaim |
| Failure sentinels are too punitive | Medium | Fail-closed principle | Calibration of consequences missing | Add rationale table for each sentinel |
| The framework is epilepsy-specific but cites generic AI guidelines | Medium | Epi-specific label/failure rules | Need explicit mapping | Add guideline-to-EpiBench mapping table |

## Killer Reviewer Questions

### Question 1

Why should the community adopt EpiBench instead of simply reporting SzCORE metrics plus TRIPOD+AI?

Answer:

SzCORE-style outputs and TRIPOD+AI reporting are necessary but not sufficient. They do not by themselves produce deterministic claim ceilings that integrate dataset evidence, label uncertainty, split validity, failure traces, alarm burden, and edge viability. EpiBench should consume compatible scoring outputs and wrap them in evidence and claim governance.

Required evidence:

- one example where SzCORE-compatible metrics are mapped into EpiBench;
- one example where metrics alone and claim-gated interpretation diverge.

### Question 2

How do you prevent EpiBench certification from being misread as medical certification?

Answer:

The certification boundary is explicit in the specification, YAML, reports, and manuscript. Certification refers only to scientific evidence-package validity under EpiBench v1.0. It excludes clinical approval, device safety, regulatory clearance, and deployment readiness.

Required evidence:

- every generated report contains the boundary statement;
- cover letter emphasizes non-regulatory scope;
- no badge uses "clinical certified."

### Question 3

How reproducible are MTS and DSI?

Answer:

They are rubric-based and fail-closed. However, reproducibility must be empirically measured. The submission should include two independent reviewers scoring at least two dataset cards, reporting agreement and adjudicated changes.

Required evidence:

- agreement table;
- revised rubric items after disagreement.

### Question 4

Why use a multi-axis Epi-Score at all if claims are gate-based?

Answer:

The Epi-Score summarizes model behavior after structural validity is established. It is not the proof. It supports comparison among eligible runs while preserving axis-level transparency. Claim gates remain dominant.

Required evidence:

- show high-score invalid model downgraded;
- show axis breakdown in every report.

### Question 5

Can EpiBench handle weak but scientifically useful datasets?

Answer:

Yes. Weak datasets are not discarded; they are assigned lower claim ceilings. They can support exploratory science, software validation, or hypothesis generation without being used for operational claims.

Required evidence:

- T3 example and language for E1-only outputs.

## Cover Letter Defense Points

The cover letter should state:

- the manuscript is about scientific evidence assurance for seizure AI;
- the framework is compatible with existing scoring and reporting standards;
- the reference implementation is public and versioned;
- the paper includes a negative worked example where naive metrics are insufficient;
- the authors do not claim clinical deployment readiness.

## Pre-Submission External Review

Before submitting:

- one epileptologist or clinical neurophysiologist reviews clinical wording;
- one benchmark/reproducibility expert reviews standard mechanics;
- one engineer runs the CLI from a clean checkout.

No submission should proceed if any of the three reviewers finds an unresolved overclaim.
