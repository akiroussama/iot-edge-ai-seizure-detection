# EpiBench Submission Readiness Matrix

Status: active risk-control document  
Primary target: npj Digital Medicine  
Secondary targets: IEEE Journal of Biomedical and Health Informatics, IEEE Transactions on Biomedical Engineering, Epilepsia or Epilepsia Open  

## Non-Negotiable Statement

No rigorous team can guarantee an acceptance probability above 80 percent at a selective Q1 journal. The defensible target is not "guaranteed acceptance"; it is "no obvious desk-reject reason and no unaddressed major reviewer attack." This matrix measures readiness against that standard.

## Current Readiness Summary

| Domain | Current status | Risk | Required action |
| --- | --- | --- | --- |
| Conceptual novelty | Strong | Medium | Phrase as evidence infrastructure, not benchmark-only |
| SOTA alignment | Good v1 registry exists | Medium | Add more direct SzCORE compatibility proof |
| Reference implementation | Working draft | Medium | Package as installable CLI and archive DOI |
| Worked example | Strong pedagogical demo plus one frozen real package | Medium | Add patient-independent real dataset packages |
| Clinical credibility | Insufficient | High | Add neurologist review or co-author |
| Dataset evidence | CHB-MIT metadata `E2-PI` null baseline plus MSG Gate C `E2-PD` forecasting package | Medium | Upgrade CHB-MIT to waveform-derived baseline and complete SeizeIT2 |
| MTS/DSI reproducibility | Rubrics exist | High | Run inter-reviewer agreement |
| Claim gates | Strong | Low | E2-PD and E3-block tests added; add E4 prospective-block test later |
| Hardware/IoT evidence | Demo only | Medium | Add actual edge benchmark or remove edge claims |
| Paper draft | Created | Medium | Convert from Markdown to journal manuscript format |

## Readiness Score

This score is an internal editorial tool, not a scientific result.

| Gate | Weight | Current score | Weighted |
| --- | ---: | ---: | ---: |
| Novelty and framing | 0.15 | 0.85 | 0.128 |
| SOTA reuse/non-reinvention | 0.15 | 0.75 | 0.113 |
| Clinical relevance and safety language | 0.15 | 0.55 | 0.083 |
| Real evidence packages | 0.20 | 0.70 | 0.140 |
| Reproducible implementation | 0.15 | 0.75 | 0.113 |
| Statistical and reviewer robustness | 0.10 | 0.50 | 0.050 |
| Community adoption package | 0.10 | 0.70 | 0.070 |
| **Total** | **1.00** |  | **0.697** |

Interpretation:

- `<0.60`: draft not ready for Q1.
- `0.60-0.75`: promising, but likely major revision or rejection if submitted now.
- `0.75-0.85`: plausible Q1 submission if clinical and SOTA gaps are closed.
- `>0.85`: no obvious avoidable rejection reason remains.

Current estimate: `0.697`. The paper is stronger after adding a generated CHB-MIT patient-independent package certified as `E2-PI` and a generated MSG Gate C package certified as `E2-PD`. It is still not ready for the most selective target because the `E2-PI` package is an always-negative metadata baseline, not a signal-derived detector, and no clinical reviewer has signed off the claim language.

Updated protocol note:

- `assess-submission-readiness` now passes the structural minimum when run on CHB-MIT plus MSG Gate C.
- This pass must not be interpreted as clinical readiness; it only means the package set satisfies the current evidence-structure gate.

## Highest Priority Upgrades

### Upgrade 1 - Real Evidence Packages

Minimum:

- TUSZ or CHB-MIT for EEG detection.
- SeizeIT2 for wearable multimodal detection.

Each must include:

- dataset card;
- MTS/DSI;
- split manifest;
- label audit note;
- baseline suite;
- result bundle;
- claim report;
- figure panels.

Acceptance impact: very high.

### Upgrade 2 - Inter-Reviewer Agreement

Run two independent reviewers on:

- one EEG dataset card;
- one wearable dataset card.

Report:

- exact agreement on claim ceiling;
- weighted kappa or simpler agreement table for MTS/DSI items;
- disagreements and rubric revisions.

Acceptance impact: high, because it directly addresses subjectivity.

### Upgrade 3 - SzCORE Compatibility Demonstration

For Track D:

- take a compatible event-level output;
- map sensitivity, precision, F1, false positives/day into EpiBench;
- show that EpiBench adds claims/failures without replacing event scoring.

Acceptance impact: high, because it prevents "you reinvented the wheel" rejection.

### Upgrade 4 - Clinical Reviewer Lock

Before submission:

- neurologist reviews anti-overclaim language;
- neurologist reviews claim ladder;
- neurologist reviews dataset label categories;
- statements about utility and alarm burden are edited conservatively.

Acceptance impact: very high for npj Digital Medicine and Epilepsia.

### Upgrade 5 - Real Edge Measurement Or Remove Edge Badge From Main Claim

Either:

- measure latency/RAM/energy on a declared target;

or:

- move embedded viability to framework capability and avoid claiming demonstrated edge readiness.

Acceptance impact: medium to high.

## Desk-Reject Risk Checklist

| Risk | Present now? | Fix |
| --- | --- | --- |
| Manuscript sounds like a software project | Partly | Emphasize clinical AI evidence and reproducibility |
| No real dataset result | Yes | Add real evidence packages |
| Claims too broad | Controlled | Keep anti-overclaim language |
| Not aligned with journal scope | Low for npj | Connect digital/mobile health and AI implementation |
| Ignores existing seizure scoring | Partly | Add SzCORE compatibility example |
| No clinician | Yes | Add clinical reviewer/co-author |
| Tool not reproducible | Mostly fixed | DOI release and install instructions |
| Too many acronyms | Medium | Add glossary and simplify main narrative |

## Target Journal Fit

### npj Digital Medicine

Fit:

- strong if framed as digital medicine AI assurance and mobile/wearable evidence infrastructure;
- requires excellent clinical framing and data/code availability.

Main weakness:

- demonstration-only evidence is insufficient.

### IEEE JBHI

Fit:

- strong for benchmark infrastructure and health informatics;
- more tolerant of technical implementation detail.

Main weakness:

- novelty must be above software packaging.

### IEEE TBME

Fit:

- possible if signal-processing and embedded evaluation are strengthened.

Main weakness:

- current paper is evidence-methodology heavy, less engineering-method focused.

### Epilepsia

Fit:

- strong only if clinical evidence and neurologist co-authorship are added.

Main weakness:

- software/protocol framing may need stronger clinical outcome relevance.

## Acceptance Probability Control

Do not state a numerical acceptance probability in the paper or cover letter. Internally, the path toward a high-confidence submission is:

1. Close all high-risk items in this matrix.
2. Obtain one external pre-submission review from a clinician.
3. Obtain one external pre-submission review from a benchmark/methods researcher.
4. Freeze v1.0-rc with DOI.
5. Submit only after the readiness score exceeds 0.85.

## Go No-Go Rule

Do not submit to npj Digital Medicine until:

- at least two real evidence packages are complete;
- one seizure scoring compatibility demonstration exists;
- clinical review is complete;
- inter-reviewer agreement is measured;
- code archive DOI exists;
- all result reports reproduce from a fresh checkout.
