# IoT Edge AI for Epileptic Seizure Detection (SeizeIT2)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/release/python-3130/)

This repository contains the engineering replication and Edge AI optimization project for the **IoT Devices** course (École Doctorale SUPCOM). It evaluates the feasibility of embedding seizure detection models on low-power microcontrollers (ESP32) using real-world patient data.

## Project Context

We reproduce and critically analyze the workflow described in:
> **Raman, A., & Velmurugan, N. (2025).** *An Intelligent Internet of Medical Things-Based Wearable Device for Monitoring of Neurological Disorders*. Engineering Proceedings, 106(1), 13. [DOI: 10.3390/engproc2025106013](https://doi.org/10.3390/engproc2025106013)

### Key Contributions (Group 2)
1. **Critical Audit**: Identified 4 major internal contradictions in the reference paper (sensor naming inconsistency, FPR discrepancy between Abstract and Results, unquantified domain shift, and RF performance claims).
2. **Real-World Replication**: Tested the proposed pipeline on the **SeizeIT2** dataset (KU Leuven, 2024) using a rigorous **Leave-One-Subject-Out (LOSO)** protocol on 6 patients with focal-to-bilateral tonic-clonic seizures.
3. **Edge AI Optimization**: Proposed a **MLP TinyML INT8** model that fits within the 520 KB SRAM of an ESP32, achieving a **56x memory reduction** compared to the reference Random Forest.

## Results Summary

| Model | Regime | Recall | RAM (ESP32 INT8) | Latency |
|---|---|---|---|---|
| **Random Forest** | Intra-patient | ~50% | 357 KB (69%) | -- |
| **Random Forest** | **LOSO (Real)** | **8.9%** | 357 KB (69%) | -- |
| **MLP TinyML** | **LOSO (Real)** | **7.5%** | **6.4 KB (1.2%)** | **19.3 µs** |

**Conclusion**: While Random Forest shows better intra-patient performance, it fails to generalize in a cross-subject deployment (LOSO). The MLP TinyML model provides a viable path for true on-device inference with minimal memory footprint.

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
- **Supervisor**: Mme Rim Ben Romdhane.

## License
Distributed under the **MIT License**. See `LICENSE` for more information.
