# EpiBench Coverage Audit

Generated from Dataset Evidence Cards, Split Manifests, Failure Traces, and Claim Reports.

## Purpose

This audit measures protocol coverage. It does not score models. It answers whether the current
artifact set exercises enough tracks, claims, tiers, split policies, failure sentinels, and MTS/DSI
rubrics to support a serious methods paper.

## Generated Files

- `dataset_evidence_matrix.csv`: one row per unique Dataset Evidence Card.
- `rubric_item_coverage.csv`: MTS/DSI item coverage and score distribution.
- `protocol_use_case_coverage.csv`: coverage by track, claim, tier, split, label audit, and sentinel.
- `coverage_gaps.csv`: explicit gaps to close before a stronger Q1 submission.

## Summary

- Result bundles audited: `15`.
- Unique Dataset Evidence Cards audited: `14`.
- Covered tracks: `D, E, F, W`.
- Covered final claims: `E1, E2-PD, E2-PI, E3, E4`.
- Total coverage gaps: `4`.
- Major coverage gaps: `4`.

## Boundary

Coverage is not clinical validity. This report only shows which parts of EpiBench v1.0-draft are
currently exercised by the repository artefacts.
