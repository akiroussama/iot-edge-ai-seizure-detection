# IoT Edge AI for Epileptic Seizure Detection (SeizeIT2)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/release/python-3130/)

This repository contains the engineering replication and Edge AI optimization project for the **IoT Devices** course (École Doctorale SUP'COM). It evaluates the feasibility of embedding seizure detection models on low-power microcontrollers (ESP32) using real-world patient data.

## Portfolio — single source of truth

The interactive portfolio bundles the presentation, the LOSO results, the Edge
AI dashboard, the AI-transparency trace and the reproduction guide in one place.

- **Streamlit app** (recommended) : `streamlit run streamlit_app.py`
- **Run from your browser, no install** : [Open in Google Colab](https://colab.research.google.com/github/akiroussama/iot-edge-ai-seizure-detection/blob/main/notebooks/launch_streamlit_colab.ipynb)
- **Static landing page** : [`docs/index.html`](docs/index.html) (deployable on GitHub Pages from `/docs`)
- **Reproduction guide** : [`docs/REPRODUCTION.md`](docs/REPRODUCTION.md)
- **AI transparency trace** : [`presentation/trace_ia.md`](presentation/trace_ia.md)
- **Project workflow infographic** : [`assets/project_workflow_infographic.svg`](assets/project_workflow_infographic.svg)

## Project Context

We reproduce and critically analyze the workflow described in:
> **Raman, A., & Velmurugan, N. (2025).** *An Intelligent Internet of Medical Things-Based Wearable Device for Monitoring of Neurological Disorders*. Engineering Proceedings, 106(1), 13. [DOI: 10.3390/engproc2025106013](https://doi.org/10.3390/engproc2025106013)

### Key Contributions (Group 2)
1. **Critical Audit**: Identified 4 major internal contradictions in the reference paper (sensor naming inconsistency, FPR discrepancy between Abstract and Results, unquantified domain shift, and RF performance claims).
2. **Real-World Replication**: Tested the proposed pipeline on the **SeizeIT2** dataset (KU Leuven, 2024) using a rigorous **Leave-One-Subject-Out (LOSO)** protocol on 6 patients with focal-to-bilateral tonic-clonic seizures.
3. **Edge AI Optimization**: Proposed a **MLP TinyML INT8** model that fits within the 520 KB SRAM of an ESP32, achieving a **56x memory reduction** compared to the reference Random Forest.

## Results Summary

Recall reported as **pooled (micro)** = ΣTP / (ΣTP + ΣFN) across 6 LOSO folds (n=893 seizure windows). This is the standard `Recall = TP / (TP + FN)` definition with TP and FN summed across folds before division (equivalently, ΣTP / ΣN_positives since N_positives = TP + FN by definition). It answers the clinical question "out of all real seizure windows, how many did the system detect?". Pooled aggregation is preferred over the macro per-subject mean because the latter overweights folds with few positives in this strongly imbalanced clinical setting.

| Model | Regime | Recall (pooled) | TP / N_pos | Accuracy (pooled) | RAM (ESP32 INT8) | Latency |
|---|---|---|---|---|---|---|
| **Random Forest** | Intra-patient | ~50 % (macro) | -- | 99.8 % | 357 KB (69 %) | 18.5 µs |
| Random Forest | **LOSO (real)** | **3.3 %** | 29 / 893 | 97.4 % * | 357 KB (69 %) | 18.5 µs |
| **MLP TinyML** | **LOSO (real)** | **8.7 %** | 78 / 893 | 91.6 % | **6.4 KB (1.2 %)** | **19.3 µs** |
| Decision Tree | LOSO (real) | 11.0 % | 98 / 893 | 94.5 % | -- | -- |
| SVM RBF | LOSO (real) | 6.5 % | 58 / 893 | 96.2 % | -- | -- |

\* RF pooled accuracy (97.4 %) ≈ trivial dummy baseline (1 − prevalence = 1 − 893/33925 = 97.37 %). The RF degenerates to "predict all negative" on cross-subject data.

**Conclusion**: Random Forest's intra-patient performance does not transfer to cross-subject (LOSO) deployment, where it collapses to the dummy classifier baseline. The MLP TinyML model — 56× smaller in memory — actually achieves higher pooled recall (8.7 % vs 3.3 %) than the RF, while remaining far below clinically acceptable sensitivity. Both confirm that the reference paper's 100 % recall claim is an artefact of its 30-sample simulated dataset and does not generalize.

## Repository Structure

- `src/`: Python source code for preprocessing, training, and cost estimation.
- `results/`: Reproduced results, CSV tables, and high-resolution figures.
- `article/`: Extracted text of the reference paper for transparency.
- `presentation/`: Final HTML presentation and AI transparency trace.
- `docs/REPRODUCTION.md`: Step-by-step guide to run the pipeline.

## Setup & Reproduction

```bash
# Clone and enter
git clone https://github.com/akiroussama/iot-edge-ai-seizure-detection.git
cd iot-edge-ai-seizure-detection

# Environment setup
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt

# Run the full pipeline
python src/pipeline_multirun.py
python src/train_multirun.py
python src/train_mlp.py
python src/estimate_esp32_cost.py
```

## Authors
- **Group 2 (SUPCOM 2026)**: Rihab HMAIED, Hamdi BENALI, Khaoula JRIDI, Mohamed Amine LAAGAB, Oussama AKIR.
- **Supervisor**: Mme Manel BEN ROMDHANE.

## License
Distributed under the **MIT License**. See `LICENSE` for more information.
