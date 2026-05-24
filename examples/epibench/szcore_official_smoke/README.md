# Official SzCORE Smoke Fixture

This directory contains a minimal executable compatibility fixture for the official `szcore-evaluation`
package. It exists to close the scientific gap where an EpiBench event-scoring bridge could be misread
as a reimplementation of SzCORE.

The fixture is deliberately tiny: one reference TSV and one hypothesis TSV in the BIDS-like layout
accepted by `szcore-evaluation==0.0.7`. The generated JSON is raw official-package output. EpiBench then
maps only the `event_results` fields into an EpiBench Result Bundle and records the relationship as `MAP`.

Run from this directory:

```powershell
$env:UV_PROJECT_ENVIRONMENT='.uv-szcore'
uv run --with szcore-evaluation==0.0.7 --with epilepsy2bids==0.0.7 --with timescoring==0.0.7 --python 3.12 python -m szcore_evaluation reference hypothesis szcore_evaluation_result.json
```

Boundary:

- This is not a seizure detection experiment.
- This is not a clinical or algorithmic result.
- This is a contract test proving that EpiBench can consume the official SzCORE JSON shape without
  replacing SzCORE event scoring.
