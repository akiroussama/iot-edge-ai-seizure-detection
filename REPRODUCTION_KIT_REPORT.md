# BSEBench Reproduction Kit Report

Date: 2026-05-24  
Status: scaffold complete; real BSEBench repositories not present in this workspace  

## Mission

Prepare a turnkey external reproduction kit for BSEBench so that an outside battery laboratory can reproduce a frozen result bundle with minimal setup.

## Delivered Artefacts

- `bsebench-runner/docker/Dockerfile`
- `bsebench-runner/docker/scripts/entrypoint.sh`
- `bsebench-runner/docker/scripts/install_editable_repos.py`
- `bsebench-runner/docker/scripts/build_image.sh`
- `bsebench-runner/docker/scripts/reproduce_bundle.sh`
- `bsebench-runner/runner/bsebench.py`
- `bsebench-runner/repositories.example.yaml`
- `bsebench-runner/bundles/bundle_calce_a123_lfp_dst_v1.0/reproduction.yaml`
- `bsebench-runner/bundles/smoke_bit_exact_v1/reproduction.yaml`
- `REPRODUCTION_KIT_README.md`
- `outreach/email_template.md`
- `.github/workflows/bsebench_reproduction_kit.yml`

## Implemented Features

### Docker

Base image:

```text
python:3.12-slim
```

Installed tools:

- pytest;
- ruff;
- mypy;
- opentimestamps-client;
- weasyprint;
- scientific Python stack;
- Git and build tools.

### Repository Installation

`install_editable_repos.py` enforces exactly seven repositories and installs each in editable mode. It accepts either:

- `url` plus `ref`; or
- `local_path`.

If a repository is missing or not installable, the script fails.

### One-Command Reproduction

Interface:

```bash
bsebench reproduce --bundle bundle_calce_a123_lfp_dst_v1.0
```

The runner:

1. loads `reproduction.yaml`;
2. executes the frozen commands;
3. fingerprints the output directory;
4. compares against `reference_manifest.json`;
5. writes a reproduction report.

### Bit-Exact Validation

The comparison reports:

- missing files;
- unexpected files;
- changed files;
- reference and actual file counts.

Exit code:

- `0`: bit-exact reproduction;
- `2`: divergence detected;
- nonzero: setup or execution failure.

### Self-Contained Smoke Bundle

The kit includes `smoke_bit_exact_v1`, which writes one deterministic text file and compares it against a frozen SHA256 manifest. This validates the runner logic without requiring BSEBench data.

## Important Limitation

The current workspace does not contain:

- the seven real BSEBench repositories;
- the real CALCE A123 LFP DST frozen bundle;
- the real reference manifest.

Therefore JES reproduction lock #4 is not closed yet. This kit reduces the remaining work to supplying the real repositories, frozen bundle, and reference manifest.

## Local Verification Performed

The Python runner was verified locally:

```text
python bsebench-runner/runner/bsebench.py smoke
python bsebench-runner/runner/bsebench.py validate-bundle --bundle bundle_calce_a123_lfp_dst_v1.0 --bundles-dir bsebench-runner/bundles
python bsebench-runner/runner/bsebench.py reproduce --bundle smoke_bit_exact_v1 --bundles-dir bsebench-runner/bundles --work-dir reports/bsebench_runner_smoke
```

The self-contained smoke bundle reproduced bit-exactly.

Docker CLI is installed locally, but the Docker Desktop Linux engine was not running in this session, so the image build could not be executed here. The Dockerfile and GitHub Actions workflow are included for CI-side validation.

## Next Required Actions

1. Fill `bsebench-runner/repositories.example.yaml` with the actual seven repository URLs and commit SHAs.
2. Replace the placeholder `bundle_calce_a123_lfp_dst_v1.0` recipe with the frozen publication recipe.
3. Generate a real `reference_manifest.json` from the reference bundle.
4. Build the Docker image.
5. Run the kit locally.
6. Run the CI workflow.
7. Send the outreach email to 5-10 labs.

## Scientific Interpretation

This kit supports external reproducibility. It does not validate battery science by itself. A bit-exact reproduction means the bundle is computationally reproducible under the declared environment. Scientific claims still depend on BSEBench dataset evidence, estimator behavior, failures, and claim eligibility.
