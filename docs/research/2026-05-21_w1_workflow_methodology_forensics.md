# W1 AI-Assisted Workflow Methodology Forensics

Date: 2026-05-21

Branch: `codex/workflow-methodology-forensics`

Base: `origin/main@0d867c6`

## Objective

Turn the project workflow itself into auditable methodology evidence. The goal
is not to narrate that human+AI collaboration was useful, but to extract
reproducible tables from repository evidence: commits, PR-style squash
subjects, changed artifact classes, research notes, validation mentions, and
guardrail mentions.

This task uses only git history and checked-in repository documents. It does
not claim access to private chat transcripts; those can be integrated later as
a separate evidence source if exported.

## Implementation

- Added `src/reports/workflow_forensics.py`.
- Added CLI `scripts/make_workflow_forensics_report.py`.
- Exported workflow-forensics helpers from `src/reports/__init__.py`.
- Added config contract `configs/report/workflow_forensics.yaml`.
- Added synthetic git-repository tests in `tests/test_workflow_forensics.py`.

The CLI writes:

- `workflow_commits.csv`
- `workflow_task_docs.csv`
- `workflow_artifact_summary.csv`
- `workflow_validation_summary.csv`
- `workflow_forensics_manifest.csv`
- `workflow_forensics_report.json`
- `workflow_forensics_report.md`

## Real Repository Dry Run

Command:

```bash
uv run --extra dev python scripts/make_workflow_forensics_report.py \
  --repo-root . \
  --out-dir /tmp/epitwin-w1-workflow-report \
  --max-commits 80 \
  --doc-globs 'docs/research/*.md,docs/*.md'
```

Observed descriptive counts on `origin/main@0d867c6`:

- Commit rows scanned: 80.
- Workflow-iteration commits: 25.
- Repository document rows scanned: 57.
- Docs with validation sections: 21.
- Docs with remaining-limit sections: 14.
- Docs mentioning Gate C: 27.
- Docs mentioning not-citable status: 8.
- Docs mentioning leakage: 35.
- Total validation-pattern mentions: 624.
- Total guardrail-pattern mentions: 315.

Artifact-class coverage across the 80 scanned commits:

- `src`: 31 commits.
- `scripts`: 34 commits.
- `tests`: 38 commits.
- `docs`: 45 commits.
- `docs/research`: 25 commits.
- `configs`: 4 commits.
- `schemas`: 5 commits.

## Scientific Guardrails

- The report is descriptive methodology evidence, not a clinical benchmark.
- Counts are extracted from repository artifacts only.
- Validation mentions are treated as audit markers, not as proof of scientific
  correctness.
- Guardrail mentions are treated as process evidence, not as proof that all
  possible leakage or citation risks are eliminated.
- Clinical benchmark claims still require Gate C frozen artifacts and
  independent review.

## Validation

Executed targeted validation:

```bash
uv run --extra dev ruff check src/reports/workflow_forensics.py src/reports/__init__.py scripts/make_workflow_forensics_report.py tests/test_workflow_forensics.py
uv run --extra dev pytest tests/test_workflow_forensics.py
```

Additional real-repo smoke run:

```bash
uv run --extra dev python scripts/make_workflow_forensics_report.py --repo-root . --out-dir /tmp/epitwin-w1-workflow-report --max-commits 80 --doc-globs 'docs/research/*.md,docs/*.md'
```

Result:

- Targeted Ruff: passed.
- Targeted pytest: 4 passed.
- Real-repo smoke run: passed.

## Remaining Limits

- Chat transcripts are not included in this implementation.
- The current extraction is intentionally conservative and text-pattern based.
- Future paper work should triangulate this evidence with PR review threads,
  reviewer comments, failed runs, and exported conversation logs when available.
- This creates the dataset for a workflow-methodology paper section; it is not
  the paper itself.
