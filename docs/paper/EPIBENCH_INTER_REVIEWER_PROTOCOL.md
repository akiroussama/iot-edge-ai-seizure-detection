# EpiBench Inter-Reviewer Agreement Protocol

## Purpose

MTS and DSI rubrics must not depend on a single author's interpretation. Before submission, EpiBench must show that independent reviewers can reach the same claim ceiling on the same dataset evidence.

## Reviewers

Minimum:

- Reviewer A: technical/reproducibility reviewer.
- Reviewer B: clinical or biomedical signal reviewer.

Preferred:

- add Reviewer C: external benchmark researcher.

## Materials

For each dataset:

- dataset source documentation;
- acquisition protocol if available;
- label documentation;
- raw-to-processed trace;
- proposed Dataset Evidence Card;
- proposed split manifest;
- known limitations.

## Procedure

1. Each reviewer scores MTS items independently.
2. Each reviewer scores DSI items independently.
3. Each reviewer assigns a preliminary dataset tier.
4. Each reviewer assigns maximum possible claim ceiling before seeing model metrics.
5. Disagreements are recorded item by item.
6. The rubric is revised only if disagreement reveals ambiguity, not to improve a dataset's tier.
7. The adjudicated final card is frozen.

## Outputs

For each dataset:

- independent score table;
- disagreement table;
- adjudication note;
- final Dataset Evidence Card;
- claim ceiling before algorithm evaluation.

## Metrics

Report:

- exact agreement on final claim ceiling;
- exact agreement on dataset tier;
- mean absolute difference in MTS item scores;
- mean absolute difference in DSI item scores;
- percentage of rubric items differing by more than one point.

If enough datasets are reviewed, report weighted kappa. If not, use transparent descriptive agreement rather than overclaiming statistical reliability.

## Acceptance Criteria

Before Q1 submission:

- two reviewers must agree on final claim ceiling for at least two datasets;
- no MTS/DSI item may differ by more than one point after rubric clarification;
- unresolved disagreement must be listed as a limitation.

## Manuscript Text

Suggested sentence:

> To evaluate rubric stability, two independent reviewers scored each pilot Dataset Evidence Card before model metrics were considered. Disagreements were adjudicated by revising ambiguous rubric language rather than by altering claim gates post hoc.
