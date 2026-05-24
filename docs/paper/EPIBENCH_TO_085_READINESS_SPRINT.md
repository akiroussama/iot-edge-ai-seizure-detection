# EpiBench Sprint To >0.85 Q1 Readiness

## Objective

Raise the internal submission readiness score from `0.697` to `>0.85` before submitting to a highly selective Q1 venue such as npj Digital Medicine.

This is not an acceptance guarantee. It is a no-obvious-major-flaw threshold.

## Current Blocking Gaps

| Gap | Current state | Required state | Readiness gain |
| --- | --- | --- | --- |
| Real evidence packages | CHB-MIT metadata null baseline at E2-PI plus MSG Gate C at E2-PD; SeizeIT2 remains E1 | waveform-derived EEG package plus wearable package | +0.08 |
| Clinical credibility | no confirmed clinician review | neurologist or clinical neurophysiologist review logged | +0.05 |
| MTS/DSI reproducibility | rubric exists | two-reviewer agreement on two cards | +0.04 |
| SzCORE compatibility | mapping document exists | one executable mapping example | +0.03 |
| DOI/release | local artefacts | v1.0-rc archived and citable | +0.02 |
| Figure generation | blueprint exists | manuscript figures generated from artefacts | +0.02 |

Projected readiness if completed: `0.87-0.89`.

## Sprint A - Submission-Grade Evidence Package 1

Dataset:

- TUSZ preferred; CHB-MIT acceptable if TUSZ cannot be completed quickly.

Track:

- `D`, detection.

Definition of done:

- Dataset Evidence Card validates.
- Split manifest validates.
- Failure trace validates.
- Result bundle validates.
- Claim report generated.
- Baselines include always negative, rate-matched random, simple EEG energy threshold, and one small model.
- Event metrics map to EpiBench fields.
- Patient-independent or LOSO split supports at least `E2-PI` if label audit permits.
- Per-patient distribution and worst-patient table are generated.

Blocking rule:

- No main-paper operational claim if label timing or split leakage cannot be audited.

## Sprint B - Submission-Grade Evidence Package 2

Dataset:

- SeizeIT2 full or sufficiently documented subset.

Track:

- `D` for wearable detection first.
- `F` only if forecasting labels are scientifically justified.

Definition of done:

- At least multiple patients, not single-subject local check.
- Missing modality report included.
- Motion/artifact stress documented.
- Patient-independent split.
- Baselines include wearable thresholds and rate-matched random.
- Claim report generated.

Blocking rule:

- No home IoT generalization if evidence remains hospital-only.

## Sprint C - Inter-Reviewer Evidence Card Study

Inputs:

- EEG evidence card.
- Wearable evidence card.

Reviewers:

- one technical reviewer;
- one clinical or biomedical signal reviewer.

Definition of done:

- independent MTS/DSI scores recorded;
- final dataset tier agreement recorded;
- final claim ceiling agreement recorded;
- disagreements resolved by rubric clarification.

Main-paper output:

- one paragraph in Methods;
- one supplementary agreement table.

## Sprint D - SzCORE Bridge Demonstration

Definition of done:

- event scoring output generated or imported for Track D;
- sensitivity, precision, F1, and false positives/day mapped to EpiBench metrics;
- EpiBench adds failure trace and claim report;
- manuscript includes "not a replacement" language.

Acceptance value:

- neutralizes a high-severity reviewer attack.

## Sprint E - Figure Package

Generate reproducible figures:

1. Evidence architecture.
2. Track timeline.
3. MTS/DSI evidence heatmap.
4. Claim gate waterfall.
5. Naive versus claim-gated leaderboard.
6. Failure heatmap.
7. Per-patient distribution.

Definition of done:

- each figure has a data source;
- no figure depends on manual spreadsheet editing;
- figure captions include claim limitations.

## Sprint F - Release Candidate

Definition of done:

- `v1.0-rc1` tag;
- changelog;
- Zenodo DOI or equivalent archive;
- schemas, YAML, examples, reports included;
- smoke test commands documented;
- clean checkout reproduction verified.

## Sprint G - Clinical Language Lock

Reviewer:

- epileptologist or clinical neurophysiologist.

Review targets:

- abstract;
- introduction;
- claim ladder;
- false alarm wording;
- certification boundary;
- limitations.

Definition of done:

- signed-off language note or documented review summary;
- all "clinical certification" ambiguity removed;
- no deployment claim remains without prospective evidence.

## Go Criteria

Submit to npj Digital Medicine only if:

- readiness score exceeds `0.85`;
- all high-severity reviewer attacks have a concrete artefact response;
- two real evidence packages are complete;
- clinical review is complete;
- SOTA bridge is demonstrated;
- release candidate is archived.

## No-Go Criteria

Do not submit if:

- only demonstration bundles are available;
- MTS/DSI remain single-reviewer;
- SeizeIT2 remains single-subject;
- claims rely on unreviewed labels;
- the CLI cannot reproduce claim reports from a fresh checkout;
- the cover letter implies clinical approval.
