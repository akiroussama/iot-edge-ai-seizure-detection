# SOTA Citation Integrity Audit

Date: 2026-05-18
Scope: `docs/SOTA_REVIEW_2026.md`
Method: each listed external source was resolved in a browser, then checked for title/topic/content
match against the sentence or paragraph using it. A resolving URL alone was not treated as sufficient.

## Verdict

No phantom or misattributed citation was found. The work-order suspect,
`arXiv:2604.18297`, resolves and matches the circadian wearable single-patient
case-study claim.

## Source Checks

| # | Source | Resolution method | Verdict |
|---|---|---|---|
| 1 | SeizeIT2 dataset paper, `https://www.nature.com/articles/s41597-025-05580-x` | Opened Nature/Scientific Data article; title, abstract, dataset size, modalities, hospital setting, and OpenNeuro/BIDS description matched the SOTA use. | VERIFIED |
| 2 | My Seizure Gauge Long-term Wearable Data, `https://zenodo.org/records/17380899` | Opened Zenodo record; title, dataset DOI `10.5281/zenodo.17380899`, 11 participants, wrist HR/steps, EEG-confirmed seizures, and 337-day average matched the SOTA use. | VERIFIED |
| 3 | Nasseri et al., `https://doi.org/10.1111/epi.18466` | DOI and article metadata verified through Monash (`https://research.monash.edu/en/publications/forecasting-epileptic-seizures-with-wearable-devices-a-hybrid-sho/`) and Mayo (`https://mayoclinic.elsevierpure.com/en/publications/forecasting-epileptic-seizures-with-wearable-devices-a-hybrid-sho/`) institutional records after DOI lookup; title, Epilepsia 2025 citation, 11 participants, HR/steps, EEG-confirmed seizures, and short/long horizon forecasting matched the SOTA use. | VERIFIED |
| 4 | Costa et al., `https://www.nature.com/articles/s41598-024-56019-z` | Opened Nature/Scientific Reports article; title, abstract, EPILEPSIAE EEG cohort, and prediction-vs-forecasting framing matched the SOTA use. | VERIFIED |
| 5 | Carmo et al., `https://link.springer.com/article/10.1007/s00415-024-12655-z` | Opened Springer/Journal of Neurology article; title, systematic-review/meta-analysis scope, AUC/BSS figures, and standardization concerns matched the SOTA use. | VERIFIED |
| 6 | Yang et al., `https://www.sciencedirect.com/science/article/pii/S1388245724002761` | Opened ScienceDirect article page; title, Clinical Neurophysiology 2024 citation, ultra-long-term EEG/RNS/NeuroVista/UNEEG scope, and multi-day forecasting claims matched SOTA context. | VERIFIED |
| 7 | Mirro et al., `https://www.frontiersin.org/journals/neurology/articles/10.3389/fneur.2024.1425490/full` | Opened Frontiers review; title, unseen-data validation, sensitivity/false-positive/deficiency-time evaluation, non-EEG/wearable discussion, and leakage cautions matched the SOTA use. | VERIFIED |
| 8 | PaPaGei repository, `https://github.com/Nokia-Bell-Labs/papagei-foundation-model` | Opened public GitHub repository; README title, PPG scope, public model, and >57,000 hours / 20 million PPG segments matched the foundation-model context. | VERIFIED |
| 9 | ICLR 2024 wearable biosignals foundation-model poster, `https://iclr.cc/virtual/2024/poster/17787` | Opened ICLR poster page; title, authors, AHMS PPG/ECG wearable data, self-supervised training, and 141k-participant / 3-year scale matched the SOTA use. | VERIFIED |
| 10 | Circadian Phase Locking of Epilepsy Seizures in Wearable Data, `https://arxiv.org/abs/2604.18297` | Opened arXiv page; arXiv ID, title, 2026 submission, wearable IBI, seizure diary, single-patient design, and circadian phase-locking analysis matched the SOTA use. | VERIFIED |
| 11 | ECG-Based Detection of Epileptic Seizures in Real-World Wearable Settings, `https://www.mdpi.com/1424-8220/25/24/7687` | Opened MDPI/Sensors article; title, SeizeIT2 ECG detection benchmark, sensitivity/FAR/HMS metrics, and detection-not-forecasting framing matched the SOTA use. | VERIFIED |
| 12 | SeizureFormer PSB 2026 abstract, `https://psb.stanford.edu/psb-online/proceedings/psb26/abstracts/2026_p85.html` | Opened PSB abstract page; title, RNS-derived IEA/LE biomarkers, 1-14 day long-horizon forecasting, five-patient scope, and transformer model matched the SOTA use. | VERIFIED |

## Notes

- `arXiv:2604.18297` was not replaced because it resolves and supports the
  attached claim.
- The MDPI SeizeIT2 ECG paper reports 886 annotated seizures and then 856
  usable ECG-linked seizures after exclusions; the Scientific Data dataset
  descriptor reports 883 focal seizures. The SOTA review does not use the MDPI
  paper for the canonical SeizeIT2 count, so no citation correction was needed.
- This audit did not make any clinical label verdicts, Gate A policy choices,
  split-freeze actions, Zenodo uploads, or baseline-performance claims.

Verified-By: browser resolution of publisher/arXiv/Zenodo/GitHub/ICLR/PSB pages plus title-and-claim matching
