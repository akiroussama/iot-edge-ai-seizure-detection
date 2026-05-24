# EpiBench v1.0-rc Release Checklist

## Normative Artefacts

- [ ] `docs/EPIBENCH_SPEC_V1.md` reviewed.
- [ ] `configs/epibench/epibench_v1.yaml` validates and matches the spec.
- [ ] JSON Schemas validate example artefacts.
- [ ] SOTA registry validated and citation integrity checked.

## Reference Implementation

- [ ] `validate-dataset-card` passes on public example.
- [ ] `validate-split` passes on public example.
- [ ] `validate-result-bundle` passes on public example.
- [ ] `validate-failure-trace` passes on public example.
- [ ] `certify` generates JSON and Markdown reports.
- [ ] Leakage worked example falls to `E1`.
- [ ] Clean worked example reaches expected claim ceiling.
- [ ] `run-conformance-suite` passes on `configs/epibench/conformance_suite_v1.yaml`.
- [ ] Dataset tier is computed from MTS and cannot be raised by declaration alone.

## Scientific Review

- [ ] Clinical reviewer confirms anti-overclaim language.
- [ ] Reproducibility reviewer runs the CLI from a fresh checkout.
- [ ] SOTA steward confirms no ignored equivalent standard.
- [ ] Independent reviewer adjudicates one dataset card.

## Paper Readiness

- [ ] At least two real evidence packages are prepared.
- [ ] Figures are generated from artefacts, not redrawn manually.
- [ ] Claim eligibility matrix is included in supplement.
- [ ] Negative example is included.
- [ ] Limitations section explicitly separates scientific certification from clinical approval.

## Community Adoption

- [ ] GitHub issue templates are present.
- [ ] Versioning policy is present.
- [ ] Changelog entry exists.
- [ ] DOI archive prepared.
- [ ] Tutorial command works in under 10 minutes.

## Release Decision

Release only if all blocking boxes are complete. Otherwise publish as draft, not as `v1.0-rc`.
