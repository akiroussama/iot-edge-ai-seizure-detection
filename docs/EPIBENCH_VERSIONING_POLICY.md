# EpiBench Versioning Policy

## Principle

Every EpiBench result bundle must declare the EpiBench version used for validation and certification. A leaderboard row without versioned protocol context is not scientifically interpretable.

## Version Format

EpiBench uses:

```text
vMAJOR.MINOR.PATCH
```

Release candidates use:

```text
vMAJOR.MINOR-rcN
```

## Major Version

Increment `MAJOR` when a change can alter a published verdict:

- claim gate changed;
- Epi-Score weights changed;
- dataset tier thresholds changed;
- failure sentinel consequence changed;
- required artifact fields changed in a non-compatible way.

Major changes require:

- migration note;
- explicit rationale;
- regression certification on public examples;
- changelog entry;
- public review window.

## Minor Version

Increment `MINOR` when a change adds compatible capability:

- optional schema field;
- new non-blocking sentinel;
- new report renderer;
- new dataset evidence package;
- SOTA registry update that does not alter existing verdicts.

## Patch Version

Increment `PATCH` for:

- typos;
- documentation clarifications;
- bug fixes that do not change certification output;
- compatibility fixes.

## Verdict Stability

Published EpiBench claims are only comparable under the same major version. If two results use different major versions, the paper must state that their claim reports are not directly equivalent.

## Citation Rule

Papers must cite:

- EpiBench version;
- commit SHA;
- DOI if available;
- normative YAML path;
- schema version;
- claim report hash if available.
