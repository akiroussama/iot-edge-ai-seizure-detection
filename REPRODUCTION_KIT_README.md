# BSEBench External Reproduction Kit

## Scientific Purpose

This kit is designed for an external battery laboratory that wants to reproduce a frozen BSEBench result bundle without learning the internal project structure.

The goal is not to make the result look good. The goal is to answer a narrow scientific question:

> Given a frozen BSEBench bundle, can an independent lab reproduce the exact artefacts, hashes, metrics, logs, and reports that support the published claim?

If the answer is no, the kit must report the divergence explicitly.

## What This Kit Provides

- An auditable Docker recipe based on `python:3.12-slim`.
- A config-driven installer for the seven BSEBench repositories in editable mode.
- A one-command reproduction interface:

```bash
bsebench reproduce --bundle bundle_calce_a123_lfp_dst_v1.0
```

- Bit-exact comparison between reproduced outputs and the frozen reference manifest.
- Divergence reports listing missing, unexpected, or changed files.
- A cross-platform CI smoke workflow.

## Certification Boundary

This kit does not certify that an estimator is clinically, industrially, or commercially valid.

It certifies only that a BSEBench result bundle can be externally reproduced under a declared software and data environment.

## Ten-Minute External Lab Workflow

### Step 0 - Check the runner itself

The kit includes a self-contained smoke bundle that proves the fingerprint and bit-exact comparison logic:

```bash
python bsebench-runner/runner/bsebench.py reproduce \
  --bundle smoke_bit_exact_v1 \
  --bundles-dir bsebench-runner/bundles \
  --work-dir reproduction-work
```

Expected status:

```text
bit_exact
```

### Step 1 - Obtain the frozen bundle

Request the frozen bundle directory from the BSEBench authors or download it from the release archive.

The bundle must contain:

- `reproduction.yaml`;
- `reference_manifest.json`;
- frozen inputs or resolvable input references;
- expected outputs or checksums;
- environment metadata;
- claim report.

### Step 2 - Build the image

```bash
bash bsebench-runner/docker/scripts/build_image.sh bsebench-runner:external-repro
```

Before publication-grade use, fill `bsebench-runner/repositories.example.yaml` with the exact seven repository URLs and commit SHAs, then install them inside the image with:

```bash
python /opt/bsebench-runner/docker/scripts/install_editable_repos.py \
  --manifest /path/to/repositories.yaml \
  --repos-dir /opt/bsebench/repos
```

### Step 3 - Reproduce the bundle

```bash
docker run --rm \
  -v "$PWD/bsebench-runner/bundles:/opt/bsebench/bundles:ro" \
  -v "$PWD/reproduction-work:/opt/bsebench/work" \
  bsebench-runner:external-repro \
  bsebench reproduce --bundle bundle_calce_a123_lfp_dst_v1.0
```

### Step 4 - Interpret the report

The runner prints and writes a JSON report:

```json
{
  "status": "bit_exact",
  "comparison": {
    "missing_files": [],
    "unexpected_files": [],
    "changed_files": []
  }
}
```

If status is `diverged`, the result is still scientifically useful. It tells us exactly where the external reproduction differs.

## How To Evaluate Your Own Estimator

To evaluate an estimator under BSEBench:

1. Implement the estimator as a reproducible command.
2. Freeze the dataset, split, preprocessing, and tuning policy.
3. Run the estimator inside the BSEBench environment.
4. Preserve failures and logs.
5. Generate the BSEBench result bundle.
6. Run `bsebench fingerprint` on the output directory.
7. Ask a second environment or lab to run `bsebench reproduce`.

Do not compare only a final RMSE. A BSEBench result must include dataset evidence, estimator behavior, failures, runtime, environment, and claim eligibility.

## Current Limitation In This Repository

This workspace does not contain the seven real BSEBench repositories or the frozen CALCE reference bundle. Therefore the current kit is an auditable runner scaffold and must be connected to the real BSEBench repositories before it can close JES reproduction lock #4.
