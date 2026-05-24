# EpiBench Independent Clinical Review Packet

Status: ready for external review; not yet completed by independent reviewers.

## Purpose

This packet operationalizes the A05 reviewer lock: MTS, DSI, dataset tier, and claim ceiling must be
auditable by independent reviewers, including at least one clinical or biomedical signal expert. The
current repository contains a deterministic inter-reviewer demo, but that is not sufficient for a Q1
claim of independent clinical review. This packet is the execution kit to obtain that review without
changing the protocol after seeing model results.

## Scientific Boundary

This packet does not certify EpiBench clinically. It does not assert that independent review has already
occurred. It freezes the materials, forms, roles, adjudication procedure, and acceptance criteria needed
to run a real review before manuscript submission.

## Required External Reviewers

Minimum:

- Reviewer C1: board-certified epileptologist, clinical neurophysiologist, neurologist with epilepsy
  monitoring expertise, or equivalent supervised clinical EEG annotation expert.
- Reviewer M1: biomedical signal processing, benchmark methodology, or reproducibility researcher not
  involved in protocol authorship.

Preferred:

- Reviewer B1: external benchmark maintainer or dataset curator.

## Files

- `review_execution_manifest.yaml`: frozen scope, candidate datasets, reviewer roles, independence rules,
  and acceptance criteria.
- `clinical_reviewer_brief.md`: clinical task description and claim-boundary instructions.
- `methods_reviewer_brief.md`: reproducibility/methodology task description.
- `dataset_review_form.csv`: machine-readable form for independent MTS/DSI scoring.
- `adjudication_register_template.csv`: item-level disagreement and resolution register.
- `independence_and_conflict_of_interest_form.md`: required independence declaration.
- `clinical_language_checklist.md`: overclaim screen for manuscript and badges.

## Acceptance Rule

The independent review is complete only when:

1. at least two independent reviewers submit forms without seeing model scores;
2. each dataset has an item-level MTS/DSI table;
3. tier and claim ceiling are assigned before model metrics are inspected;
4. all disagreements greater than one rubric point are adjudicated by rubric clarification, not by
   dataset-specific score tuning;
5. the final adjudication register is committed and linked from the reviewer packet.

Until then, A05 remains a partial defense.
