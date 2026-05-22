# Claims Surface Sweep

Date: 2026-05-22
Branch: `codex/claims-surface-sweep`
Base: `origin/main` at `be7ed94`

## Objective

Continue the post-review hardening by sweeping the public claims surface for
stale status text and wording that could support an over-claim before Gate B
and Gate C.

## Findings

1. `docs/ROADMAP_HIGH_LEVEL.md` still contained `Wrist/tibia IMU`. Historical
   review docs already treated `tibia` as a suspicious typo, so the roadmap
   should not keep it as a forward requirement.
2. `PROJECT_STATUS.md` still described Phase R as if remediation had merely
   started and did not mention the May 20-22 publishability scaffolds. That made
   the top-level status weaker and less coherent than `PLAYBOOK.md`.
3. `PLAYBOOK.md` still phrased an old hardware-claim typo as an unresolved fix
   rather than a non-regression guardrail.

## Changes

- Replaced the roadmap requirement with `Documented wrist or limb IMU placement`.
- Refreshed `PROJECT_STATUS.md` on 2026-05-22.
- Reframed Phase R as code/policy guardrails represented in the repo, with M2
  still blocked by the human label audit.
- Added the May 20-22 scaffolds to status while explicitly keeping them
  non-citable until Gate B and Gate C pass.
- Updated the playbook claim-cleanup item so old hardware-claim typos are
  treated as non-regression checks, not open operational-doc fixes.

## Validation

Commands run from a clean worktree based on `origin/main`:

```bash
rg -n "\\b(first|novel|SOTA|state[- ]of[- ]the[- ]art|published|publishable|citable|certified|validated|passed|PASS|no leakage|leakage-safe|Q1|A100|Gate [ABCDEFH]|Gate C)\\b" README.md PLAYBOOK.md PROJECT_STATUS.md docs reports scripts src tests configs schemas --glob '!docs/commits/**' --glob '!docs/research/**'
rg -n "tibia|tibial|TinyML|edge performance|99 tests|May 15|2026-05-15|not citable|pre[- ]Gate|Gate C passed|Gate B passed|full human audited|verifiably SOTA|first wearable|first.*forecast" README.md PLAYBOOK.md PROJECT_STATUS.md docs reports scripts src tests configs schemas --glob '!docs/commits/**' --glob '!docs/research/**'
rg -n "tibia|tibial" README.md PLAYBOOK.md PROJECT_STATUS.md docs/ROADMAP_HIGH_LEVEL.md docs/HUMAN_INTERVENTION_CHECKPOINTS.md docs/PUBLICATION_PROPOSAL.md docs/SOTA_REVIEW_2026.md
rg -n "Phase R audit remediation has started|99 tests|Gate C passed|Gate B passed|full human audited|first wearable seizure-forecasting system" README.md PLAYBOOK.md PROJECT_STATUS.md docs/ROADMAP_HIGH_LEVEL.md docs/PUBLICATION_PROPOSAL.md docs/SOTA_REVIEW_2026.md
uv run --extra dev ruff check .
uv run --extra dev pytest tests/test_workflow_forensics.py
git diff --check
```

Ruff result: all checks passed.
Targeted workflow-forensics test: 4 passed.

## Residual Risk

Historical review/audit files still contain old dates, old test counts, and the
original `tibia` note by design. They are archival evidence, not current status.
