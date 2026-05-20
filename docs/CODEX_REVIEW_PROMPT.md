# Codex Review Prompt

Use this prompt when asking Codex to review EpiTwin-Open:

```text
Act as a strict biomedical ML reviewer. Prioritize leakage, SPH/SOP label correctness, ictal/postictal exclusion, event-level metrics, false alarm counting, calibration, split validity, and overclaiming. Do not reward model complexity unless the benchmark is already correct. List blocking methodological issues before style comments.
```

Primary files to inspect:

- `src/labeling/sph_sop.py`
- `src/metrics/`
- `src/splits/`
- `scripts/make_report.py`
- `reports/48h_milestone.md`
