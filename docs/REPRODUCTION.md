# Reproduction Guide - Seizure Detection Edge AI

This guide explains how to reproduce the results of the Group 2 project, from raw data acquisition to Edge AI cost estimation.

## 1. Prerequisites

- **Python 3.13** (recommended)
- **Git**
- ~2GB of disk space for the SeizeIT2 subset

## 2. Dataset Acquisition

The project uses the **SeizeIT2** dataset (OpenNeuro `ds005873`). Due to licensing and privacy, raw data is not included in this repository.

1. Download the following subjects from [OpenNeuro ds005873](https://openneuro.org/datasets/ds005873):
   - `sub-001`
   - `sub-032`
   - `sub-085`
   - `sub-096`
   - `sub-124`
   - `sub-125`
2. Extract the data into a `data/` folder at the root of the repository.
3. Ensure you have both `eeg.edf` and `mov.edf` for the selected runs.

## 3. Installation

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install pipeline dependencies (mne, scipy, scikit-learn, matplotlib + the demo)
pip install --upgrade pip
pip install -r requirements-pipeline.txt
```

> Note: `requirements.txt` at the repo root contains only the lightweight
> dependencies needed by `streamlit_app.py` (the interactive demo). It is
> kept minimal so Streamlit Cloud can deploy it without compiling scientific
> libraries from source. Use `requirements-pipeline.txt` for the full
> reproduction stack.

## 4. Execution Pipeline

The reproduction follows a strictly ordered pipeline:

### Step 1: Data Indexing & Loading
Verify that the data is correctly placed and accessible.
```bash
python src/load_data.py
```

### Step 2: Preprocessing & Feature Engineering
Filters the signals (Butterworth 0.5-12Hz for EEG, 0.1-10Hz for MOV) and extracts the 10 statistical features (Variance, Skewness, Higuchi Fractal Dimension, Spectral Entropy, etc.).
```bash
python src/preprocess.py
```

### Step 3: Global Feature Matrix (Multirun)
Consolidates all patients into a single feature matrix for Leave-One-Subject-Out (LOSO) cross-validation.
```bash
python src/pipeline_multirun.py
```

### Step 4: Model Training & Evaluation
Trains the reference models (DT, SVM, RF) and the proposed TinyML MLP.
```bash
python src/train_multirun.py
python src/train_mlp.py
```

### Step 5: Edge AI Cost Estimation
Calculates the analytical estimates for ESP32 deployment (RAM, Latency, Energy).
```bash
python src/estimate_esp32_cost.py
```

### Step 6: Figure Generation
Regenerates the ROC curves and the Performance vs. RAM tradeoff plots.
```bash
python src/make_figures.py
```

## 5. Interpreting Results

Results are saved in the `results/` directory:
- `multirun_loso_summary.json`: Detailed metrics for classical models.
- `mlp_loso_summary.json`: Detailed metrics for the TinyML model.
- `esp32_cost_estimate.json`: The 4-axis Edge AI metrics (Accuracy, RAM, Latency, Energy).

## 6. Common Issues

- **Memory Error**: Ensure you are using the 64-bit version of Python.
- **Missing EDF**: Check if the file naming matches the expected BIDS format in `src/load_data.py`.
- **MNE Version**: Using a version older than 1.6 might cause issues with `mov.edf` parsing.
