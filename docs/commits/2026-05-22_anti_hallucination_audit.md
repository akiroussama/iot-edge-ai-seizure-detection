# Anti-Hallucination Audit

Date: 2026-05-22

Branch: `codex/anti-hallucination-audit`

Base: `origin/main@fc25214`

## Scope

This audit covers the recent publishability-oriented blocks merged as PRs
`#27` through `#31`, plus the current roadmap/playbook text that governs SOTA
claims.

Audited surfaces:

- `docs/commits/2026-05-22_t10_external_sota_reproduction.md`
- `docs/commits/2026-05-22_t15_foundation_transfer_protocol.md`
- `docs/commits/2026-05-22_t20_paper_artifact_package.md`
- `docs/commits/2026-05-22_f2_federated_benchmark_protocol.md`
- `configs/reproduction/external_sota_reproduction.yaml`
- `configs/model/foundation_transfer.yaml`
- `configs/report/federated_benchmark.yaml`
- `configs/report/paper_artifact_package.yaml`
- `PLAYBOOK.md`

## Method

1. Searched the repository for high-risk language: DOI, SOTA, citable,
   certified, phantom citation, Q1, recommendation, and foundation-model claims.
2. Verified external references against primary or canonical sources.
3. Compared documented guardrails to actual code/test behavior.
4. Patched stale or over-strong wording where the code cannot prove the claim.

## External Source Verification

| Claim area | Local claim | Source checked | Verdict |
|---|---|---|---|
| SeizeIT2 | Scientific Data 12, article 1228, 2025; 125 patients, 883 focal seizures, >11,000 h, official split/baselines | Nature Scientific Data article `10.1038/s41597-025-05580-x` | Supported |
| Stirling wearable forecasting | Frontiers in Neurology 12:704060, 2021; wearable HR/sleep/steps seizure likelihood forecasting | Frontiers article `10.3389/fneur.2021.704060` | Supported |
| MSG dataset | Zenodo dataset `10.5281/zenodo.17380899`; 11 participants, HR/steps, EEG-confirmed seizures, average 337 days | Zenodo record `17380899` | Supported |
| Nasseri hybrid forecasting | Epilepsia 2025 linked article DOI `10.1111/epi.18466` | PubMed canonical record and Zenodo related-work metadata | Supported |
| ICLR wearable biosignal FM | ICLR 2024 paper trains PPG/ECG foundation models from AHMS | ICLR 2024 proceedings page | Supported |
| PaPaGei | Open PPG foundation model, accepted at ICLR 2025, code/models linked | arXiv `2410.20542` and GitHub `nokia-bell-Labs/papagei-foundation-model` | Supported |

Primary source URLs checked:

- https://www.nature.com/articles/s41597-025-05580-x
- https://www.frontiersin.org/articles/10.3389/fneur.2021.704060/full
- https://zenodo.org/records/17380899
- https://pubmed.ncbi.nlm.nih.gov/?term=10.1111%2Fepi.18466
- https://proceedings.iclr.cc/paper_files/paper/2024/hash/0d99a8c048befb6dd6e17d7684adacac-Abstract-Conference.html
- https://github.com/nokia-bell-Labs/papagei-foundation-model

## Findings

### Fixed: stale phantom-citation instruction

`PLAYBOOK.md` and a historical Claude work-order still carried stale wording
from an earlier suspicion that `arXiv:2604.18297` was phantom, while
`docs/SOTA_CITATION_AUDIT_2026-05-18.md` records that the ID resolves and
matches the intended circadian wearable single-patient claim. I updated both
surfaces to mark that concern as superseded and require a fresh primary-source
check before reclassifying it as phantom.

### Fixed: over-strong foundation-transfer wording

The foundation-transfer adapter can reject label, split, alarm, and future-event
columns in the submitted embedding table. It cannot prove that the upstream
encoder was generated without labels. I added this limitation to the config and
commit evidence.

### Fixed: over-strong federated privacy wording

The federated benchmark validator rejects known raw patient/window columns. It
does not certify arbitrary submitted fields as PHI-free. I added an explicit
de-identification limitation to the config and commit evidence.

### Fixed: paper package source-URI limitation

The paper artifact package checks whether claims link to an artifact or source
URI. It does not resolve every URL or verify the source content. I added an
explicit guardrail requiring primary-source audit before manuscript claims.

### Fixed: minor validation wording

The Task10 commit note had a stale sentence implying validation was pending,
despite containing full validation results. I removed that sentence.

## Residual Risk Register

| Risk | Status | Required control before manuscript |
|---|---|---|
| External SOTA rows may be task-incompatible despite valid DOI | Controlled by mismatch notes, still manual | For every included SOTA row, attach a reproduction dossier and task-compatibility note |
| Foundation embeddings may have unknown upstream training leakage | Documented residual risk | Require model card/source audit before using embeddings in citable results |
| Federated site submissions may contain PHI in non-standard columns | Documented residual risk | Enforce site-side de-identification checklist before accepting real site submissions |
| Paper artifact package can record a source URI without verifying it | Documented residual risk | Run source-resolution audit for final manuscript bibliography |
| Pre-Gate-C synthetic tests might be misread as benchmark evidence | Controlled by status fields and Markdown warnings | Keep all pre-Gate-C rows labelled `not_citable_pre_gate_c` |

## Verdict

No fabricated DOI or unsupported recent source was found in the audited recent
blocks. The main hallucination risk was not source fabrication; it was stale or
over-strong wording about what local validators can prove. Those statements were
corrected in this branch.

The repository is stronger after this audit, but the final paper still needs a
dedicated bibliography/source-resolution pass immediately before submission.

## Validation

- `uv run --extra dev ruff check .` -> passed.
- `uv run --extra dev --extra torch pytest` -> 283 passed.
- High-risk phrase rescan -> current playbook/config/report guardrails are
  aligned; remaining flagged terms are deliberate limitations or historical
  audit context, not active instructions.
