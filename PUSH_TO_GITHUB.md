# Push EpiTwin-Open v0.1 to GitHub

Target repository:

```bash
https://github.com/akiroussama/iot-edge-ai-seizure-detection.git
```

Branch:

```bash
feature/epibench-forecast-v0.1
```

## Option A — from the repo folder

```bash
cd epitwin-open
git remote set-url origin https://github.com/akiroussama/iot-edge-ai-seizure-detection.git
git checkout feature/epibench-forecast-v0.1
git push -u origin feature/epibench-forecast-v0.1
```

Then open a Pull Request from:

```text
feature/epibench-forecast-v0.1 -> main
```

## Option B — from the Git bundle

```bash
git clone epitwin-open-target-feature.bundle epitwin-open
cd epitwin-open
git checkout feature/epibench-forecast-v0.1
git remote add origin https://github.com/akiroussama/iot-edge-ai-seizure-detection.git
git push -u origin feature/epibench-forecast-v0.1
```

## Verify locally before push

```bash
python -m pytest -q
python scripts/make_report.py --output-dir reports/demo
```
