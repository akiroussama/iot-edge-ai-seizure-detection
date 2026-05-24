# Repository Full Timeline: IoT Edge AI Seizure Detection To EpiBench

Generated: `2026-05-24T18:51:26+02:00`
Workspace: `C:\doctorat\iot\iot-edge-ai-seizure-detection`
Branch at generation: `codex/epibench-evidence-panels`
HEAD at generation: `7133e4b5534f38f9ed1e3f9ddfb415bd70300041`
Commit count included: `173`
First commit: `002dfbe` 2026-05-04T18:10:46+02:00 - feat: initial release - SeizeIT2 LOSO replication of Raman 2025
Latest commit included: `7133e4b` 2026-05-24T18:43:12+02:00 - Harden EpiBench against Q1 reviewer attacks

## Non-Censorship Boundary

This file is intentionally not a marketing history. It records the repository as it is visible from Git metadata: successful features, exploratory work, readiness gates, negative evidence, failed-or-pending proof obligations, and pivots. It does not claim that every intermediate artefact is citable science. When the repository contains demo, simulated, preliminary, or non-citable artefacts, they are treated as part of the history rather than hidden.

Self-reference note: this document is generated from the 173 commits that existed before the document itself was committed. A Git commit cannot stably contain a full ledger entry for its own final SHA because the SHA changes when the file changes. The commit that adds this document is therefore reported in the assistant summary and visible in `git log` after the file is committed.

## Executive Synthesis

The repository began as an IoT/edge AI seizure-detection workspace and gradually became a scientific evidence-governance project. The strongest pivot is methodological: instead of optimizing only a detector, the work now asks what a seizure-AI result is allowed to prove under auditable evidence constraints. That pivot produced EpiBench: a BSEBench-like protocol with dataset cards, machine-readable schemas, claim gates, failure preservation, evidence panels, overclaim audits, release-candidate reproduction, and Q1 reviewer hardening.

## Current Honest State

- Full-scale signal-derived EEG evidence remains required beyond the current micro/provisional packages.
- Independent clinical and methods review forms are prepared but not yet completed by external reviewers.
- Target IoT hardware latency/RAM/energy evidence is not yet available; local CPU timing is not edge evidence.
- Zenodo DOI and independent external clean-checkout reproduction are still pending.
- Prospective clinical evidence is not claimed and remains future E4-level work.

## Commit Distribution By Month

- `2026-05`: `173` commit(s)

## Approximate Topic Distribution

- `data`: `94` commit touch(es)
- `docs`: `138` commit touch(es)
- `epibench`: `71` commit touch(es)
- `gates`: `124` commit touch(es)
- `models`: `64` commit touch(es)
- `other`: `10` commit touch(es)
- `release`: `30` commit touch(es)
- `tests`: `136` commit touch(es)

## Major Pivots

### 1. Scaffold and raw IoT seizure workspace

The earliest commits establish the project skeleton, reporting utilities, validation culture, and the local data-processing substrate. The work is mostly infrastructure rather than publishable science.

### 2. Gate-based data quality discipline

The repository then pivots toward Gate A/B/C style controls: label audits, cohort readiness, source recovery, dry runs, closeout ledgers, and explicit non-citable states. This is the first major scientific pivot: bad or incomplete data are treated as blockers, not annoyances.

### 3. Real-data readiness and negative evidence

SeizeIT2, MSG, CHB-MIT, and local inventory work appear progressively. The pattern is conservative: weak local subsets are preserved as negative readiness findings or E1 evidence rather than inflated into performance claims.

### 4. BSEBench-like EpiBench standardization

The project then shifts from model-first IoT seizure detection to an evidence standard. EpiBench introduces Dataset Evidence Cards, MTS/DSI, claim gates, failure traces, Epi-Score, result bundles, schemas, conformance tests, and reviewer-defense packets.

### 5. Q1 paper hardening

The latest phase attacks the paper as a severe reviewer would: SzCORE non-reinvention, clinical-review dependency, hardware-evidence boundaries, release-candidate reproduction, overclaim audit, and a 10-angle Q1 hardening register.

## Timeline Commands Used

```powershell
git log --reverse --date=iso-strict --pretty=format:'%H%x1f%h%x1f%ad%x1f%an%x1f%s%x1f%b%x1e'
git show --shortstat --format= <commit>
git diff-tree --no-commit-id --name-status -r --root <commit>
```

## Full Commit-By-Commit Ledger

### 001. `002dfbe` - feat: initial release - SeizeIT2 LOSO replication of Raman 2025

- Full SHA: `002dfbeda12d050cac99f4e2da969bc4643f0ad3`
- Date: `2026-05-04T18:10:46+02:00`
- Author: `Akir Oussama`
- Shortstat: 69 files changed, 4807 insertions(+)
- Body: none
- Files changed:
  - `A	.gitignore`
  - `A	LICENSE`
  - `A	README.md`
  - `A	article/Raman_Velmurugan_2025_neurological_iomt.txt`
  - `A	docs/REPRODUCTION.md`
  - `A	git-metadata/HEAD`
  - `A	git-metadata/config`
  - `A	git-metadata/description`
  - `A	git-metadata/info/exclude`
  - `A	git-metadata/objects/02/83c01873c301623fdbba7c90c526243a53bee0`
  - `A	git-metadata/objects/09/11f316fdbc339ee8bd82789a1790321deb8699`
  - `A	git-metadata/objects/20/8994b98031671d635eb21989a137ddcd32073e`
  - `A	git-metadata/objects/25/606e76d36e143be8bde24fdd400b9b3db71737`
  - `A	git-metadata/objects/25/75f9f57b616d2ba7a70a7728fdbb7bf30f42e8`
  - `A	git-metadata/objects/33/96313016b2271a2e92352bb74c6c0bf2ddf9fd`
  - `A	git-metadata/objects/37/19c6d3fc4810c048c0bd7026e2d568feaa0a4f`
  - `A	git-metadata/objects/39/b939ad382902f48692579be4716008b9119548`
  - `A	git-metadata/objects/3c/0d78c831d077cbd7726beeab7d85f65dbc05f6`
  - `A	git-metadata/objects/3e/a5cf0a7465c46be6439670d4990950d208945f`
  - `A	git-metadata/objects/40/0678d15f5b77e3ec6170a15ccbcc4221bb1ed3`
  - `A	git-metadata/objects/56/8686d11629d4506a182a0071da14ff08394785`
  - `A	git-metadata/objects/68/2aa833218f10fa758d693c4462bf14cb1fdd2d`
  - `A	git-metadata/objects/72/9eac5c3ef030616e46184c3da560c098b70d10`
  - `A	git-metadata/objects/75/ba364318d58b0cea2df7d7ea7707950d2b1046`
  - `A	git-metadata/objects/7c/61986c544ee88a260863f6ab3c56de93682b78`
  - `A	git-metadata/objects/7e/5f78afdffb01bd274c0a1624d3910116ae98cb`
  - `A	git-metadata/objects/97/7b391efbf0738de2ee19b58043a31657f90bdf`
  - `A	git-metadata/objects/9d/8ca980e64bb0bb7d57c6c6eb83196cad90d216`
  - `A	git-metadata/objects/9f/84cf25c0bfc08d34bd32ca7d4e6aaec9dce800`
  - `A	git-metadata/objects/a2/13fbb6d710ccb5d8d4ba62f9f5797765ab06c9`
  - `A	git-metadata/objects/a5/ead92e85ff62ec7aa6a894ac59e29fddc38ed0`
  - `A	git-metadata/objects/ab/92a3a61e2d2a302456486197eb00fbc107a42e`
  - `A	git-metadata/objects/b4/5be283baf34f7858d2d2587c6f472100d06445`
  - `A	git-metadata/objects/b9/299ba882009345a8a504a5ec91eeee7ef9f72f`
  - `A	git-metadata/objects/bc/9a274207ac2bbe6bc5429ae331c54edeb3eb16`
  - `A	git-metadata/objects/cb/5abf368442b04df5f2f989e5f9faa5954abcf2`
  - `A	git-metadata/objects/cc/1c28acaec5d40de6dd5bd31fb137101e0a9699`
  - `A	git-metadata/objects/d6/f2734d869f66d47211b5e0714567e0597b7a8c`
  - `A	git-metadata/objects/d8/d178d50a362da52029f194bf3dd07d88a7238f`
  - `A	git-metadata/objects/da/17372170958c7e46e1b078c3a0f832309e1c3d`
  - `A	git-metadata/objects/e1/1438458882f32b2b58682424cf033f589ff92a`
  - `A	git-metadata/objects/e7/df86225149d4d11e88bdff9c0e854d4b5111c6`
  - `A	git-metadata/objects/ea/b87405cec278b2171bcdefb0fbbd18b0871aa4`
  - `A	git-metadata/objects/f4/cde07d8b5ffcff9640b4ce1c91b7920237ad4f`
  - `A	git-metadata/objects/fa/c0e288de2471e0634b2ee7e1e18581de69fd30`
  - `A	git-metadata/refs/heads/main`
  - `A	presentation/presentation.html`
  - `A	presentation/trace_ia.md`
  - `A	requirements.txt`
  - `A	results/baseline_run07.csv`
  - `A	results/baseline_run07_summary.json`
  - `A	results/esp32_cost_estimate.json`
  - `A	results/figures/perf_vs_ram.png`
  - `A	results/figures/roc_loso.png`
  - `A	results/figures/sub-001_run-07_seizure.png`
  - `A	results/mlp_loso.csv`
  - `A	results/mlp_loso_summary.json`
  - `A	results/multirun_loso.csv`
  - `A	results/multirun_loso_summary.json`
  - `A	src/estimate_esp32_cost.py`
  - `A	src/explore_first_seizure.py`
  - `A	src/features.py`
  - `A	src/load_data.py`
  - `A	src/make_figures.py`
  - `A	src/pipeline_multirun.py`
  - `A	src/preprocess.py`
  - `A	src/train_baseline.py`
  - `A	src/train_mlp.py`
  - `A	src/train_multirun.py`

### 002. `4b244fd` - Update supervisor name in README.md

- Full SHA: `4b244fd8ff9e0ed50d3f6309bb5f754a101d17df`
- Date: `2026-05-04T18:12:38+02:00`
- Author: `Akir Oussama`
- Shortstat: 1 file changed, 1 insertion(+), 1 deletion(-)
- Body: none
- Files changed:
  - `M	README.md`

### 003. `533523b` - fix(loso): replace macro recall with pooled aggregation

- Full SHA: `533523bb515f2ede6cfe4c51965b4587ff7ade0c`
- Date: `2026-05-09T12:17:05+02:00`
- Author: `Akir Oussama`
- Shortstat: 7 files changed, 401 insertions(+), 18 deletions(-)
- Body:

```text
Trigger: feedback Mme Manel 2026-05-09 flagging RF recall calculation.

Root cause: train_multirun.py:153-157 aggregated per-fold recalls via
np.mean (macro), the sklearn cross_val_score default. For severely
imbalanced multi-subject clinical detection (893 positives spread
unevenly across 6 LOSO folds: 114, 116, 58, 37, 345, 223) the macro
mean is dominated by sub-085 (39.66 % recall, 58 positives) and
overstates the system's global sensitivity. The right aggregator for
"out of all real seizure windows, how many were detected?" is the
pooled (micro) recall: sum(TP) / sum(N_positives).

Recomputed pooled metrics (compute_pooled_metrics.py, derived from
multirun_loso.csv per-subject TP/FN/FP/TN):

  RF  : recall 3.25 % (29/893), accuracy 97.36 %, FPR 0.09 %
  DT  : recall 10.97 % (98/893), accuracy 94.47 %
  SVM : recall 6.49 % (58/893), accuracy 96.24 %
  MLP : recall 8.73 % (78/893), accuracy 91.59 %

Sanity check that should have flagged this earlier: prevalence
893/33925 = 2.63 %, so the trivial dummy classifier (predict all
negative) yields accuracy 97.37 %. The RF pooled accuracy 97.36 %
matches the dummy baseline to four decimal places — meaning the
RF degenerates to the dummy classifier on cross-subject data. This
also explains the absurdly low FPR (0.09 %): the model almost never
predicts positive.

Effect on narrative: the corrected pooled recall reinforces our
critique of Raman & Velmurugan 2025 rather than weakening it. RF
ranking drops from 2nd to 4th; MLP TinyML moves to 2nd, supporting
the Edge AI conclusion that a 56x-smaller model also detects ~3x
more real seizures than the RF.

Files changed:
- README.md: results table now reports pooled recall + dummy
  baseline footnote
- presentation/presentation.html: slide 15 results table replaced;
  slide 17 comparison "8.9 %" -> "3.25 %"
- presentation/trace_ia.md: new section 5.4 documenting the prof
  feedback episode and 4-fault chain in the AI system
- src/train_multirun.py: aggregate() now also exposes pooled
  metrics + raw confusion-matrix totals in the JSON
- src/compute_pooled_metrics.py: new post-processing script that
  recomputes pooled metrics from existing CSV without re-training
- results/multirun_loso_pooled.json: new pooled-metrics artefact
- VERIFICATION_RECALL_RF.md: forensic verification document with
  per-subject TP/FN table and macro-vs-pooled side-by-side

Refs:
- multirun_loso.csv (per-subject ground-truth, lines 4,7,10,13,16,19 for RF)
- VERIFICATION_RECALL_RF.md (full forensic trail, sections 2-6bis)
- presentation/trace_ia.md section 5.4 (AI accountability narrative)

Verified-By: python src/compute_pooled_metrics.py  (output: RF 0.0325,
DT 0.1097, SVM 0.0649, MLP 0.0873; baseline accuracy 0.9737 = RF
accuracy 0.9736)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```
- Files changed:
  - `M	README.md`
  - `A	VERIFICATION_RECALL_RF.md`
  - `M	presentation/presentation.html`
  - `M	presentation/trace_ia.md`
  - `A	results/multirun_loso_pooled.json`
  - `A	src/compute_pooled_metrics.py`
  - `M	src/train_multirun.py`

### 004. `a031276` - chore(repo): trim to evaluation-ready scope

- Full SHA: `a0312762225f267ad0fedac94d2b3f970c717910`
- Date: `2026-05-10T17:06:15+02:00`
- Author: `Akir Oussama`
- Shortstat: 48 files changed, 122 insertions(+), 264 deletions(-)
- Body:

```text
- Remove tracked git-metadata/ directory (accidental .git copy, 24 obj)
- Remove VERIFICATION_RECALL_RF.md (internal audit document)
- Add git-metadata/ and _gitdir_probe/ to .gitignore as guard
- Fix UTF-8 mojibake across README.md, presentation/presentation.html,
  presentation/trace_ia.md, docs/REPRODUCTION.md, article/*.txt
- Rewrite presentation/trace_ia.md preserving methodological substance
  (anti-hallucination protocol, error log including the macro-vs-pooled
  recall correction triggered by Mme Manel BEN ROMDHANE feedback,
  human/AI decision split, observed limits) using neutral
  assistant-tier terminology
- Update README results discussion to drop the now-removed verification
  file pointer; pooled aggregation justification kept inline

Tracked tree narrowed from 79 to 30 files; repo now contains only the
artefacts directly required for evaluation: source code, reproducible
results, paper extract, reproduction guide, presentation, and the
AI-usage trace required by criterion (b) of the course brief.
```
- Files changed:
  - `M	.gitignore`
  - `M	README.md`
  - `D	VERIFICATION_RECALL_RF.md`
  - `M	article/Raman_Velmurugan_2025_neurological_iomt.txt`
  - `M	docs/REPRODUCTION.md`
  - `D	git-metadata/HEAD`
  - `D	git-metadata/config`
  - `D	git-metadata/description`
  - `D	git-metadata/info/exclude`
  - `D	git-metadata/objects/02/83c01873c301623fdbba7c90c526243a53bee0`
  - `D	git-metadata/objects/09/11f316fdbc339ee8bd82789a1790321deb8699`
  - `D	git-metadata/objects/20/8994b98031671d635eb21989a137ddcd32073e`
  - `D	git-metadata/objects/25/606e76d36e143be8bde24fdd400b9b3db71737`
  - `D	git-metadata/objects/25/75f9f57b616d2ba7a70a7728fdbb7bf30f42e8`
  - `D	git-metadata/objects/33/96313016b2271a2e92352bb74c6c0bf2ddf9fd`
  - `D	git-metadata/objects/37/19c6d3fc4810c048c0bd7026e2d568feaa0a4f`
  - `D	git-metadata/objects/39/b939ad382902f48692579be4716008b9119548`
  - `D	git-metadata/objects/3c/0d78c831d077cbd7726beeab7d85f65dbc05f6`
  - `D	git-metadata/objects/3e/a5cf0a7465c46be6439670d4990950d208945f`
  - `D	git-metadata/objects/40/0678d15f5b77e3ec6170a15ccbcc4221bb1ed3`
  - `D	git-metadata/objects/56/8686d11629d4506a182a0071da14ff08394785`
  - `D	git-metadata/objects/68/2aa833218f10fa758d693c4462bf14cb1fdd2d`
  - `D	git-metadata/objects/72/9eac5c3ef030616e46184c3da560c098b70d10`
  - `D	git-metadata/objects/75/ba364318d58b0cea2df7d7ea7707950d2b1046`
  - `D	git-metadata/objects/7c/61986c544ee88a260863f6ab3c56de93682b78`
  - `D	git-metadata/objects/7e/5f78afdffb01bd274c0a1624d3910116ae98cb`
  - `D	git-metadata/objects/97/7b391efbf0738de2ee19b58043a31657f90bdf`
  - `D	git-metadata/objects/9d/8ca980e64bb0bb7d57c6c6eb83196cad90d216`
  - `D	git-metadata/objects/9f/84cf25c0bfc08d34bd32ca7d4e6aaec9dce800`
  - `D	git-metadata/objects/a2/13fbb6d710ccb5d8d4ba62f9f5797765ab06c9`
  - `D	git-metadata/objects/a5/ead92e85ff62ec7aa6a894ac59e29fddc38ed0`
  - `D	git-metadata/objects/ab/92a3a61e2d2a302456486197eb00fbc107a42e`
  - `D	git-metadata/objects/b4/5be283baf34f7858d2d2587c6f472100d06445`
  - `D	git-metadata/objects/b9/299ba882009345a8a504a5ec91eeee7ef9f72f`
  - `D	git-metadata/objects/bc/9a274207ac2bbe6bc5429ae331c54edeb3eb16`
  - `D	git-metadata/objects/cb/5abf368442b04df5f2f989e5f9faa5954abcf2`
  - `D	git-metadata/objects/cc/1c28acaec5d40de6dd5bd31fb137101e0a9699`
  - `D	git-metadata/objects/d6/f2734d869f66d47211b5e0714567e0597b7a8c`
  - `D	git-metadata/objects/d8/d178d50a362da52029f194bf3dd07d88a7238f`
  - `D	git-metadata/objects/da/17372170958c7e46e1b078c3a0f832309e1c3d`
  - `D	git-metadata/objects/e1/1438458882f32b2b58682424cf033f589ff92a`
  - `D	git-metadata/objects/e7/df86225149d4d11e88bdff9c0e854d4b5111c6`
  - `D	git-metadata/objects/ea/b87405cec278b2171bcdefb0fbbd18b0871aa4`
  - `D	git-metadata/objects/f4/cde07d8b5ffcff9640b4ce1c91b7920237ad4f`
  - `D	git-metadata/objects/fa/c0e288de2471e0634b2ee7e1e18581de69fd30`
  - `D	git-metadata/refs/heads/main`
  - `M	presentation/presentation.html`
  - `M	presentation/trace_ia.md`

### 005. `5b98fab` - feat(demo): add interactive Streamlit demo SeizureGuard Live

- Full SHA: `5b98fabcef4a11868f5e2984bf0cc4c120b8bf7f`
- Date: `2026-05-10T20:26:29+02:00`
- Author: `Akir Oussama`
- Shortstat: 2 files changed, 636 insertions(+)
- Body:

```text
Single-file Streamlit app (streamlit_app.py) with four tabs replaying
the empirical LOSO results stored in results/:

1. Signal & contexte     — synthetic IMU trace with bell-shaped
                            tonic-clonic burst, parametric duration
                            and onset, prevalence reminder vs trivial
                            dummy baseline.
2. Model arena (live)    — animated playback of per-window predictions
                            for the 4 models on a chosen held-out
                            patient. Counts (TP / FP / FN) match the
                            measured values in multirun_loso.csv and
                            mlp_loso.csv ; visualises the LOSO collapse
                            of the Random Forest (recall = 0 on most
                            subjects) and the comparative TinyML MLP
                            performance.
3. ESP32 cost dashboard  — table + filling-bar visualisation of RAM
                            usage on a 520 KB SRAM target, with a
                            live calculator (sliders) showing the
                            RAM / latency / energy of arbitrary
                            RF (n_trees, depth) and MLP architectures.
4. Trade-off explorer    — Pareto scatter (RAM vs AUC) on log-x with
                            the >100 % SRAM region shaded as
                            non-deployable, colour-coded markers, and
                            hover tooltips showing pooled recall.

Plot library: plotly (already installable). No live training, no
extra dataset required: every figure derives from CSV/JSON committed
to results/. Run with:  streamlit run streamlit_app.py
```
- Files changed:
  - `M	requirements.txt`
  - `A	streamlit_app.py`

### 006. `edbb69d` - fix(deploy): split app deps from pipeline deps

- Full SHA: `edbb69d76bdd62ee564e331ca73ff1e048162a1c`
- Date: `2026-05-10T20:35:56+02:00`
- Author: `Akir Oussama`
- Shortstat: 3 files changed, 30 insertions(+), 8 deletions(-)
- Body:

```text
Streamlit Cloud failed to deploy because the previous requirements.txt
pinned scipy==1.12.0 + numpy==1.26.4, which have no pre-built wheels
for Python 3.14 (the cloud runtime). Pip then attempted to compile
scipy from source and aborted because gfortran is not in the sandbox.

Resolution: streamlit_app.py only needs streamlit, plotly, pandas,
and numpy at runtime — all of which have wheels across recent Python
versions. The full reproduction stack (mne, scipy, scikit-learn,
matplotlib) is needed only by the offline pipeline scripts in src/,
which run on the developer's machine where SeizeIT2 .edf files are
already present.

- requirements.txt          : 4 minimal deps for the cloud demo
- requirements-pipeline.txt : full stack with loose pins (>= ranges)
                              so resolvers can pick wheels matching
                              the local Python
- docs/REPRODUCTION.md      : updated install command to point at
                              requirements-pipeline.txt with a note
                              explaining the split
```
- Files changed:
  - `M	docs/REPRODUCTION.md`
  - `A	requirements-pipeline.txt`
  - `M	requirements.txt`

### 007. `dbd62fa` - chore: ignore Streamlit Cloud log dumps in repo root

- Full SHA: `dbd62fa8432862979689bebf83599872f225ff20`
- Date: `2026-05-10T20:36:24+02:00`
- Author: `Akir Oussama`
- Shortstat: 1 file changed, 3 insertions(+)
- Body: none
- Files changed:
  - `M	.gitignore`

### 008. `1d13576` - fix(demo): drop matplotlib dependency from cost dashboard

- Full SHA: `1d1357647ede949fff03f580d8812a5db7ffa6f8`
- Date: `2026-05-10T20:38:36+02:00`
- Author: `Akir Oussama`
- Shortstat: 2 files changed, 18 insertions(+), 5 deletions(-)
- Body:

```text
pandas Styler.background_gradient delegates colormap resolution to
matplotlib. Since matplotlib was intentionally removed from
requirements.txt to keep the cloud deploy lightweight, the cost
dashboard crashed at import time on Streamlit Cloud:

  ImportError: Styler.background_gradient requires matplotlib.

Replace the gradient with a hand-rolled threshold colourer (green / amber
/ red) wired through Styler.map. The visual signal — which models exceed
the 520 KB ESP32 SRAM ceiling — is preserved without pulling in the full
plotting stack.

- streamlit_app.py : tab_cost() now uses a local _color_sram_pct
                     callback instead of background_gradient
- requirements.txt : bump pandas pin to >=2.1 (Styler.map was added
                     there; pre-2.1 installs would need .applymap)
```
- Files changed:
  - `M	requirements.txt`
  - `M	streamlit_app.py`

### 009. `98afd3a` - fix(arena): clamp progress bar to [0, 1] and drop dead code

- Full SHA: `98afd3ac89324b5aab2fcb514f39f177af202261`
- Date: `2026-05-10T20:42:54+02:00`
- Author: `Akir Oussama`
- Shortstat: 1 file changed, 2 insertions(+), 3 deletions(-)
- Body:

```text
Two issues in tab_arena:

1. progress.progress((step + chunk) / n_test) could exceed 1.0 on
   the final iteration when step + chunk overshoots n_test (e.g.
   n_test=23059, chunk=115, last step=23000 -> ratio=1.005).
   Streamlit raises StreamlitAPIException for any value outside
   [0, 1]. Wrap with min(1.0, ...).

2. render_state() previously computed an unused tp_so_far via a
   convoluted np.isin-based subtraction, then re-derived the same
   value through the simpler `fired & pos_mask` pattern just below.
   Drop the unused expression and add an explicit step clamp at the
   top of the function for safety on edge cases (step=n_test).
```
- Files changed:
  - `M	streamlit_app.py`

### 010. `764d72f` - fix(arena): give plotly_chart a unique key per step to dodge dup IDs

- Full SHA: `764d72f72e853fac6b6833c7339c3680b90ccca0`
- Date: `2026-05-10T20:49:35+02:00`
- Author: `Akir Oussama`
- Shortstat: 1 file changed, 1 insertion(+), 1 deletion(-)
- Body:

```text
Recent Streamlit (1.36+) auto-generates element IDs from the call
fingerprint. The animation loop in tab_arena calls bars.plotly_chart
many times in quick succession; the final post-loop render_state(
n_test - 1) often produces the same fingerprint as the last in-loop
iteration, causing StreamlitDuplicateElementId.

Fix: pass key=f"arena_bars_{subj}_{step}". Each render now has a
distinct identity (subject + step), the placeholder still owns the
visible slot, and reruns wipe the registry so no accumulation
across sessions.
```
- Files changed:
  - `M	streamlit_app.py`

### 011. `ba37f7d` - docs(recall): make TP/(TP+FN) form explicit alongside ΣTP/ΣN_positives

- Full SHA: `ba37f7d726b137fa8274b2f494a9eb1f4661bef2`
- Date: `2026-05-10T21:09:26+02:00`
- Author: `Akir Oussama`
- Shortstat: 2 files changed, 5 insertions(+), 2 deletions(-)
- Body:

```text
Clarification triggered by Mme Manel BEN ROMDHANE pre-defense feedback:
"Recall = TP / (TP + FN), j'ai l'impression que votre formule est
fausse !". The formula is correct but the slide notation
"recall pooled = ΣTP / ΣN_positives" did not visibly match the
canonical "Recall = TP / (TP + FN)" form for a quick read, because the
identity N_positives = TP + FN was implicit.

Verification of the actual computation (results/multirun_loso.csv):
- Random Forest : ΣTP = 29, ΣFN = 864, Recall = 29 / (29 + 864) = 29/893 = 0.0325
- MLP TinyML  : ΣTP = 78, ΣFN = 815, Recall = 78 / (78 + 815) = 78/893 = 0.0873

Code path unchanged (src/compute_pooled_metrics.py sums per-fold TP/FN
then divides). Only the documentation notation is rewritten:

- README.md: pooled recall written as ΣTP/(ΣTP+ΣFN), note that this is
  the standard Recall = TP/(TP+FN) with sums across folds, and explicit
  reminder that N_positives = TP + FN by definition.
- presentation/trace_ia.md §5.4: recalcul block now writes both forms
  with the numeric substitution shown step by step (29/(29+864) etc.).
```
- Files changed:
  - `M	README.md`
  - `M	presentation/trace_ia.md`

### 012. `332eb66` - feat(demo): add Paper vs Reality side-by-side tab

- Full SHA: `332eb666d52409e32d79f686632e4242b482195d`
- Date: `2026-05-11T00:01:56+02:00`
- Author: `Akir Oussama`
- Shortstat: 1 file changed, 156 insertions(+), 1 deletion(-)
- Body:

```text
New 5th tab "Paper vs Réalité (démo soutenance)" without touching the
four existing tabs. It is the cinematic kill-shot for the defense.

Concept: same Random Forest, same weights, two protocols. Left grid
shows the Raman 2025 paper test set (30 mimicked-seizure windows on
healthy volunteers, balanced 50% prevalence): all 30 cells turn green
as the animation progresses (100% recall). Right grid shows our
empirical SeizeIT2 LOSO pooled measurement (893 real seizure windows,
prevalence 2.63%): 30 windows sampled deterministically (seed=2026),
the RF catches 1 of them (expected = 30 * 29/893 ≈ 0.97, rounded to 1).
29 red Xs + 1 green tick.

Big counter under each grid (X / 30 = Y %). Speed selector. Banner
below: "MÊME MODÈLE · MÊMES POIDS · ÉCART ≈ 30×". Expander documents
the sampling math for full reproducibility.

Build: pure Streamlit + HTML/CSS grids in st.markdown(
unsafe_allow_html=True), no extra Python dependency. Zero impact on
tabs 1-4 (signal, arena, ESP32 cost, Pareto) — they remain bit-exact.
```
- Files changed:
  - `M	streamlit_app.py`

### 013. `bb09c09` - feat(demo): replace tab 5 with full pipeline wizard A to Z

- Full SHA: `bb09c09f2a5315b2927d906e61afe21e1687e66e`
- Date: `2026-05-11T00:09:31+02:00`
- Author: `Akir Oussama`
- Shortstat: 1 file changed, 552 insertions(+), 2 deletions(-)
- Body:

```text
User feedback on previous tab 5: the abstract X/check grid was not
pertinent, doesn't tell the story of the actual work.

Replace with a guided wizard through the 11 stages of the project:

  1. Problématique     — paper Raman, 4 contradictions, our approach
  2. Dataset SeizeIT2  — OpenNeuro ds005873, BIDS, 125 patients, 6 used
  3. Préprocessing     — Butterworth filter, 256 Hz -> 25 Hz downsample
  4. Fenêtrage         — 2.56 s windows, 50% overlap, label from events.tsv
  5. Features          — 10 stat/spectral features × 8 channels = 80
  6. Modèles           — DT, SVM RBF, RF, MLP TinyML (80->32->16->1)
  7. LOSO              — leave-one-subject-out with table of 6 folds
  8. Métriques         — recall, accuracy, F1, FPR with class-imbalance trap
  9. Résultats         — pooled table + per-subject RF breakdown
 10. Coût ESP32        — analytical cost table FP32/INT8, RF vs MLP
 11. Conclusion        — contributions, limits, perspectives

Navigation: Previous / Selectbox jump / Next, progress bar, session_state
tracks current step. Each step references the relevant src/ file or
results/ artefact so the prof can audit.

Existing tabs 1-4 untouched. Old paper-vs-reality function kept in file
as dormant code (not wired to any tab), can be deleted later.
```
- Files changed:
  - `M	streamlit_app.py`

### 014. `3355f82` - fix(wizard): nav callbacks + add scientific figures per useful step

- Full SHA: `3355f82fd73e8d5fe54d292ae7b4ea7fb9a11274`
- Date: `2026-05-11T00:21:54+02:00`
- Author: `Akir Oussama`
- Shortstat: 1 file changed, 242 insertions(+), 16 deletions(-)
- Body:

```text
Two issues addressed:

1) Navigation bug : "Suivant" / "Précédent" buttons fought the "Aller à"
   selectbox. On click, wizard_step changed via st.rerun() but the
   selectbox's session_state key still held the previous index, and
   silently reverted the step on the next run. Replace inline button
   logic with on_click / on_change callbacks that sync both
   wizard_step and wiz_jump atomically — no more rerun ping-pong.

2) Add 6 plotly figures, one per step where the content benefits
   visually from data viz (text-only steps unchanged) :

   Step 2  : donut de la prévalence (893 / 33 925 = 2,63 %)
   Step 3  : avant/après filtre passe-bas sur signal IMU synthétique
   Step 4  : fenêtrage glissant + chevauchement avec crise annotée
             (montre comment label = 1 dérive du chevauchement)
   Step 7  : matrice LOSO 6×6 heatmap train (vert) / test (rouge)
   Step 8  : bar groupé Accuracy / Recall / F1 par modèle, avec
             ligne dashed du baseline trivial 97,37 % en rouge
   Step 9  : barres recall RF par patient held-out, avec ligne
             pooled 3,25 % et nombres bruts (X/Y) sur chaque barre
   Step 10 : empreinte RAM FP32 vs INT8 par modèle, échelle log,
             ligne dashed du plafond 520 KB SRAM ESP32

Steps 1 / 5 / 6 / 11 restent purement textuels — leur contenu
n'a pas besoin de figure pour être compréhensible. Aucune
dépendance ajoutée : tout en numpy + plotly déjà présents.
```
- Files changed:
  - `M	streamlit_app.py`

### 015. `0d905f8` - feat(streamlit): add project portfolio website and Colab launcher

- Full SHA: `0d905f82dfc62900cb038cebd6faa26dd9f7e222`
- Date: `2026-05-13T19:52:10+02:00`
- Author: `Akir Oussama`
- Shortstat: 9 files changed, 2546 insertions(+), 1406 deletions(-)
- Body: none
- Files changed:
  - `A	.streamlit/config.toml`
  - `A	DEPLOY_STREAMLIT_COLAB.md`
  - `A	assets/presentation_iot_uploaded.pdf`
  - `A	assets/report_iot.pdf`
  - `A	docs/DEPLOYMENT_CHECKLIST.md`
  - `A	docs/index.html`
  - `A	notebooks/launch_streamlit_colab.ipynb`
  - `M	streamlit_app.py`
  - `A	streamlit_demo_live.py`

### 016. `29ff17e` - add portfolio

- Full SHA: `29ff17ef3499b1bbb20cc925447d83231ab455e2`
- Date: `2026-05-13T21:55:23+02:00`
- Author: `Akir Oussama`
- Shortstat: 12 files changed, 1914 insertions(+), 9 deletions(-)
- Body:

```text
single source of truth: the potfolio contain all links and informations
```
- Files changed:
  - `M	README.md`
  - `A	assets/README.md`
  - `A	assets/project_workflow_infographic.svg`
  - `A	assets/screenshots/README.md`
  - `M	docs/DEPLOYMENT_CHECKLIST.md`
  - `A	docs/assets/project_workflow_infographic.svg`
  - `M	docs/index.html`
  - `M	streamlit_app.py`
  - `A	web/README.md`
  - `A	web/assets/project_workflow_infographic.svg`
  - `A	web/index.html`
  - `A	web/vercel.json`

### 017. `c4f2516` - move index to main branch

- Full SHA: `c4f2516c10660da5948742583db56ce59acdd91a`
- Date: `2026-05-13T22:05:06+02:00`
- Author: `Akir Oussama`
- Shortstat: 2 files changed, 53 insertions(+), 6 deletions(-)
- Body: none
- Files changed:
  - `A	vercel.json`
  - `M	web/README.md`

### 018. `e16a0de` - clean repo

- Full SHA: `e16a0de95df9c184f0941f54b4e1073ff4f1356a`
- Date: `2026-05-13T22:22:16+02:00`
- Author: `Akir Oussama`
- Shortstat: 2 files changed, 0 insertions(+), 0 deletions(-)
- Body:

```text
remove pdf
```
- Files changed:
  - `D	assets/presentation_iot_uploaded.pdf`
  - `D	assets/report_iot.pdf`

### 019. `f8baf76` - Update streamlit_app.py

- Full SHA: `f8baf764a28b88893a7852d04238841f121258d9`
- Date: `2026-05-13T22:29:59+02:00`
- Author: `Akir Oussama`
- Shortstat: 1 file changed, 35 insertions(+), 9 deletions(-)
- Body: none
- Files changed:
  - `M	streamlit_app.py`

### 020. `be9cbc2` - google collab to reproduce pipeline

- Full SHA: `be9cbc29009e0023c009f0f7c00e054fbc7e319e`
- Date: `2026-05-13T22:36:44+02:00`
- Author: `Akir Oussama`
- Shortstat: 3 files changed, 555 insertions(+), 6 deletions(-)
- Body: none
- Files changed:
  - `A	notebooks/reproduce_pipeline_colab.ipynb`
  - `M	streamlit_app.py`
  - `M	web/index.html`

### 021. `1c3961b` - fix google collab build issue

- Full SHA: `1c3961ba8fb9ea812ed5634b218dd32c13090aca`
- Date: `2026-05-13T22:40:44+02:00`
- Author: `Akir Oussama`
- Shortstat: 2 files changed, 41 insertions(+), 14 deletions(-)
- Body: none
- Files changed:
  - `M	notebooks/reproduce_pipeline_colab.ipynb`
  - `M	requirements-pipeline.txt`

### 022. `d0c9f05` - update google collab link in the porfoltio

- Full SHA: `d0c9f0523df03943902154af836eed14775469a1`
- Date: `2026-05-13T22:42:23+02:00`
- Author: `Akir Oussama`
- Shortstat: 3 files changed, 16 insertions(+), 9 deletions(-)
- Body: none
- Files changed:
  - `M	docs/index.html`
  - `M	streamlit_app.py`
  - `M	web/index.html`

### 023. `b45ffdf` - update deployment checklist

- Full SHA: `b45ffdf2ff5350de3d5a3c741b952f9b6f79ed09`
- Date: `2026-05-13T22:42:45+02:00`
- Author: `Akir Oussama`
- Shortstat: 3 files changed, 10 insertions(+), 4 deletions(-)
- Body: none
- Files changed:
  - `M	DEPLOY_STREAMLIT_COLAB.md`
  - `M	README.md`
  - `M	docs/DEPLOYMENT_CHECKLIST.md`

### 024. `444596d` - Update README.md

- Full SHA: `444596d0d049b1a3a4dfe0f459ee53db12c5bf89`
- Date: `2026-05-13T22:42:54+02:00`
- Author: `Akir Oussama`
- Shortstat: 1 file changed, 2 insertions(+), 1 deletion(-)
- Body: none
- Files changed:
  - `M	assets/screenshots/README.md`

### 025. `9906494` - Update streamlit_app.py

- Full SHA: `99064942ef3eba442463a80f0555b6720798b205`
- Date: `2026-05-13T22:43:03+02:00`
- Author: `Akir Oussama`
- Shortstat: 1 file changed, 2 insertions(+), 1 deletion(-)
- Body: none
- Files changed:
  - `M	streamlit_app.py`

### 026. `4bb74dc` - Update reproduce_pipeline_colab.ipynb

- Full SHA: `4bb74dc06bc109a39f8ffed7fae1e9d71335b4ed`
- Date: `2026-05-13T22:45:47+02:00`
- Author: `Akir Oussama`
- Shortstat: 1 file changed, 22 insertions(+), 21 deletions(-)
- Body: none
- Files changed:
  - `M	notebooks/reproduce_pipeline_colab.ipynb`

### 027. `e477c74` - force numpy-2-compatible scipy/mne/sklearn minimums

- Full SHA: `e477c74ab9d8f6d4e70622600a63aa63f08479cb`
- Date: `2026-05-13T22:53:32+02:00`
- Author: `Akir Oussama`
- Shortstat: 2 files changed, 22 insertions(+), 17 deletions(-)
- Body: none
- Files changed:
  - `M	notebooks/reproduce_pipeline_colab.ipynb`
  - `M	requirements-pipeline.txt`

### 028. `1c31ee0` - Update reproduce_pipeline_colab.ipynb

- Full SHA: `1c31ee04efcc6e1f4649e7a3729ffee7f7d6c905`
- Date: `2026-05-14T08:06:31+02:00`
- Author: `Akir Oussama`
- Shortstat: 1 file changed, 19 insertions(+), 18 deletions(-)
- Body: none
- Files changed:
  - `M	notebooks/reproduce_pipeline_colab.ipynb`

### 029. `4b4d68e` - fix(colab): use BIDS subject-dir include for OpenNeuro download

- Full SHA: `4b4d68ed1d816734ef8b9d0e30e3b3f64863b3bb`
- Date: `2026-05-14T08:32:28+02:00`
- Author: `Akir Oussama`
- Shortstat: 1 file changed, 24 insertions(+), 19 deletions(-)
- Body:

```text
`sub-001/*events.tsv` did not match the deep BIDS layout
(`sub-001/ses-XX/eeg/...`) and crashed openneuro-py at the manifest
lookup. Switch to two more robust patterns:

- Phase 1 (metadata) : `include=[sub-XXX, ...]` + `exclude=[*.edf]`
  to grab every events.tsv / channels.tsv / json sidecar but skip
  the heavy EDF files.
- Phase 3 (EDF) : reuse the events.tsv paths already on disk to
  construct exact relative paths for `*_eeg.edf` and `*_mov.edf`,
  so no glob ambiguity reaches openneuro-py.

Verified-By: python -m json.tool notebooks/reproduce_pipeline_colab.ipynb
  (valid JSON) + ast.parse on every code cell (clean except the
  expected magic-only first cell).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```
- Files changed:
  - `M	notebooks/reproduce_pipeline_colab.ipynb`

### 030. `cbf59a4` - Build EpiTwin-Open benchmark infrastructure

- Full SHA: `cbf59a4397116eef782f7e8dd0a79e63db76fc70`
- Date: `2026-05-15T13:36:40+02:00`
- Author: `Oussama Akir`
- Shortstat: 172 files changed, 8074 insertions(+), 10350 deletions(-)
- Body:

```text
Replace the prior IoT seizure demo branch contents with the EpiTwin-Open research benchmark package.

Implemented leakage-safe SPH/SOP labeling, postictal/ictal exclusions, fixed window generation, clinical event/alarm/calibration metrics, threshold sweeps, split helpers, leakage checks, random and simple baselines, and CPU-smoke EpiTwin-SSL modules.

Added real-dataset-ready loaders for SeizeIT2 BIDS-score annotations and My Seizure Gauge Zenodo nested Empatica ZIP archives. SeizeIT2 now supports eventType/dateTime/recordingDuration TSVs and modality manifests. MSG now supports SeizureTimesOnly text files, per-patient Mayo ZIP seizure onset files, recording interval discovery from HR/ACC headers, event-to-recording matching, and partial-download-safe inspection/preparation.

Added dataset-specific reporting and audit tooling: label audit exports, synthetic milestone reports, real-data pipeline-check reports, command runbooks, SOTA/publication framing, human intervention checkpoints, A100 policy, and dataset quickstart docs. All real-data reports are explicitly marked as pipeline checks, not clinical evidence.

Validation before commit: uv run python -m pytest -q passed with 56 tests; uv run ruff check . passed; ./RUN_THIS_FIRST.sh passed including synthetic demo, synthetic report, and one-epoch CPU smoke train.

Data governance: raw and processed data directories, local datasets, generated CSV/parquet reports, caches, checkpoints, and model artifacts are ignored so public raw data and generated tables are not committed.
```
- Files changed:
  - `A	.github/workflows/tests.yml`
  - `M	.gitignore`
  - `D	.streamlit/config.toml`
  - `A	CODEX_HANDOFF_EpiTwin_Open_V1_V2_Two_Week_Plan.md`
  - `D	DEPLOY_STREAMLIT_COLAB.md`
  - `D	LICENSE`
  - `A	MANIFEST.md`
  - `A	Makefile`
  - `A	PROJECT_STATUS.md`
  - `A	PUSH_TO_GITHUB.md`
  - `M	README.md`
  - `A	RUN_THIS_FIRST.sh`
  - `D	article/Raman_Velmurugan_2025_neurological_iomt.txt`
  - `D	assets/README.md`
  - `D	assets/project_workflow_infographic.svg`
  - `D	assets/screenshots/README.md`
  - `A	configs/default.yaml`
  - `A	configs/eval/metrics.yaml`
  - `A	configs/experiment/seizeit2_sph5_sop30.yaml`
  - `A	configs/labeling/sph_sop.yaml`
  - `A	configs/model/edge_student.yaml`
  - `A	configs/model/epitwin_ssl.yaml`
  - `A	configs/train/base.yaml`
  - `A	docs/A100_RUNBOOK.md`
  - `A	docs/CLAUDE_CODE_PROMPTS.md`
  - `A	docs/CODEX_REVIEW_PROMPT.md`
  - `A	docs/CODEX_REVIEW_PROMPTS.md`
  - `A	docs/COMMANDS.md`
  - `A	docs/DATASET_INTEGRATION_PLAN.md`
  - `D	docs/DEPLOYMENT_CHECKLIST.md`
  - `A	docs/END_TO_END_EXECUTION_MAP.md`
  - `A	docs/HUMAN_INTERVENTION_CHECKPOINTS.md`
  - `A	docs/HUMAN_LABEL_AUDIT_PROTOCOL.md`
  - `A	docs/PAPER1_OUTLINE.md`
  - `A	docs/PUBLICATION_PROPOSAL.md`
  - `A	docs/REAL_DATA_QUICKSTART.md`
  - `D	docs/REPRODUCTION.md`
  - `A	docs/RISK_REGISTER.md`
  - `A	docs/ROADMAP_HIGH_LEVEL.md`
  - `A	docs/SOTA_REVIEW_2026.md`
  - `A	docs/V1_V2_TWO_WEEK_PLAN.md`
  - `A	docs/VERSION_ACCEPTANCE_CRITERIA.md`
  - `D	docs/assets/project_workflow_infographic.svg`
  - `D	docs/index.html`
  - `D	notebooks/launch_streamlit_colab.ipynb`
  - `D	notebooks/reproduce_pipeline_colab.ipynb`
  - `D	presentation/presentation.html`
  - `D	presentation/trace_ia.md`
  - `A	pyproject.toml`
  - `A	reports/48h_milestone_template.md`
  - `A	reports/msg_partial_real_check/dataset_report.md`
  - `A	reports/seizeit2_sub125_real_check/dataset_report.md`
  - `A	reports/v0_1_verification.md`
  - `A	reports/v1_0_release_candidate.md`
  - `D	requirements-pipeline.txt`
  - `D	requirements.txt`
  - `D	results/baseline_run07.csv`
  - `D	results/baseline_run07_summary.json`
  - `D	results/esp32_cost_estimate.json`
  - `D	results/figures/perf_vs_ram.png`
  - `D	results/figures/roc_loso.png`
  - `D	results/figures/sub-001_run-07_seizure.png`
  - `D	results/mlp_loso.csv`
  - `D	results/mlp_loso_summary.json`
  - `D	results/multirun_loso.csv`
  - `D	results/multirun_loso_pooled.json`
  - `D	results/multirun_loso_summary.json`
  - `A	scripts/audit_labels.py`
  - `A	scripts/evaluate_predictions.py`
  - `A	scripts/inspect_labels.py`
  - `A	scripts/label_windows.py`
  - `A	scripts/make_dataset_report.py`
  - `A	scripts/make_report.py`
  - `A	scripts/make_windows.py`
  - `A	scripts/prepare_msg.py`
  - `A	scripts/prepare_seizeit2.py`
  - `A	scripts/run_baseline.py`
  - `A	scripts/run_synthetic_demo.py`
  - `A	scripts/sweep_thresholds.py`
  - `A	scripts/train_epitwin_ssl.py`
  - `A	src/__init__.py`
  - `A	src/baselines/__init__.py`
  - `A	src/baselines/random_rate_matched.py`
  - `A	src/baselines/simple_rules.py`
  - `A	src/baselines/tcn_small.py`
  - `A	src/calibration/__init__.py`
  - `A	src/calibration/conformal_risk.py`
  - `A	src/calibration/thresholding.py`
  - `D	src/compute_pooled_metrics.py`
  - `D	src/estimate_esp32_cost.py`
  - `D	src/explore_first_seizure.py`
  - `D	src/features.py`
  - `A	src/features/__init__.py`
  - `A	src/features/window_features.py`
  - `A	src/forecasting/__init__.py`
  - `A	src/forecasting/alarm_controller.py`
  - `A	src/forecasting/hazard.py`
  - `A	src/labeling/__init__.py`
  - `A	src/labeling/postictal.py`
  - `A	src/labeling/sph_sop.py`
  - `D	src/load_data.py`
  - `D	src/make_figures.py`
  - `A	src/metrics/__init__.py`
  - `A	src/metrics/alarm_metrics.py`
  - `A	src/metrics/calibration.py`
  - `A	src/metrics/event_metrics.py`
  - `A	src/metrics/sweep.py`
  - `A	src/models/__init__.py`
  - `A	src/models/backbones/__init__.py`
  - `A	src/models/backbones/causal_transformer.py`
  - `A	src/models/backbones/cfc_placeholder.py`
  - `A	src/models/backbones/gru.py`
  - `A	src/models/backbones/mamba_placeholder.py`
  - `A	src/models/backbones/tcn.py`
  - `A	src/models/edge/__init__.py`
  - `A	src/models/edge/edge_student.py`
  - `A	src/models/encoders/__init__.py`
  - `A	src/models/encoders/simple_encoders.py`
  - `A	src/models/epitwin_ssl.py`
  - `A	src/models/fusion/__init__.py`
  - `A	src/models/fusion/multimodal_fusion.py`
  - `A	src/models/heads/__init__.py`
  - `A	src/models/heads/hazard_head.py`
  - `A	src/models/heads/reconstruction_head.py`
  - `A	src/models/heads/uncertainty_head.py`
  - `A	src/models/symbolic_constraints.py`
  - `D	src/pipeline_multirun.py`
  - `D	src/preprocess.py`
  - `A	src/preprocessing/__init__.py`
  - `A	src/preprocessing/windowing.py`
  - `A	src/reports/__init__.py`
  - `A	src/reports/label_audit.py`
  - `A	src/reports/summary_tables.py`
  - `A	src/splits/__init__.py`
  - `A	src/splits/center_split.py`
  - `A	src/splits/leakage_checks.py`
  - `A	src/splits/patient_split.py`
  - `A	src/splits/temporal_split.py`
  - `D	src/train_baseline.py`
  - `D	src/train_mlp.py`
  - `D	src/train_multirun.py`
  - `A	src/utils/__init__.py`
  - `A	src/utils/io.py`
  - `A	src/utils/logging.py`
  - `A	src/utils/time.py`
  - `A	src/utils/validation.py`
  - `D	streamlit_app.py`
  - `D	streamlit_demo_live.py`
  - `A	tests/test_alarm_controller.py`
  - `A	tests/test_alarm_metrics.py`
  - `A	tests/test_calibration.py`
  - `A	tests/test_calibration_thresholding.py`
  - `A	tests/test_dataset_parsers.py`
  - `A	tests/test_event_metrics.py`
  - `A	tests/test_features.py`
  - `A	tests/test_hazard.py`
  - `A	tests/test_label_audit.py`
  - `A	tests/test_labeling_edge_cases.py`
  - `A	tests/test_metric_sweep.py`
  - `A	tests/test_models.py`
  - `A	tests/test_no_temporal_leakage.py`
  - `A	tests/test_postictal_exclusion.py`
  - `A	tests/test_random_baseline.py`
  - `A	tests/test_schemas.py`
  - `A	tests/test_sph_sop_labeling.py`
  - `A	tests/test_windowing.py`
  - `A	uv.lock`
  - `D	vercel.json`
  - `D	web/README.md`
  - `D	web/assets/project_workflow_infographic.svg`
  - `D	web/index.html`
  - `D	web/vercel.json`

### 031. `9b8bf8d` - Add reproducible MSG Zenodo downloader

- Full SHA: `9b8bf8d941d0ecc44369471e5e9f964af74d0647`
- Date: `2026-05-15T13:40:19+02:00`
- Author: `Oussama Akir`
- Shortstat: 3 files changed, 142 insertions(+)
- Body:

```text
Add a versioned downloader for the current My Seizure Gauge Zenodo record. The script reads the Zenodo API, supports resumable curl downloads, optional file filters, expected-size checks, and optional md5 verification.

Document the annotation-only and full-download commands in the real-data quickstart and command reference so the local data acquisition path is reproducible instead of an ad hoc shell session.

Validation before commit: uv run ruff check . passed; uv run python -m pytest -q passed with 56 tests.
```
- Files changed:
  - `M	docs/COMMANDS.md`
  - `M	docs/REAL_DATA_QUICKSTART.md`
  - `A	scripts/download_msg_zenodo.py`

### 032. `70b6626` - Restore dataset modules in pushed package

- Full SHA: `70b6626d53a12333eb2270d4ea2cff47d7bbe8a0`
- Date: `2026-05-15T13:42:38+02:00`
- Author: `Oussama Akir`
- Shortstat: 8 files changed, 1398 insertions(+)
- Body:

```text
Fix the publish staging filter so repository-internal paths named data/datasets are not excluded. The previous rsync excluded root raw-data directories correctly, but also omitted src/datasets and configs/data from the pushed branch.

Adds the missing dataset abstraction, schemas, SeizeIT2 loader, MSG loader, data configs, and the annotation-only ZIP regression test.

Validation in the push clone: uv run --extra dev --extra torch python -m pytest -q passed with 57 tests; uv run --extra dev ruff check . passed.
```
- Files changed:
  - `A	configs/data/msg.yaml`
  - `A	configs/data/seizeit2.yaml`
  - `A	src/datasets/__init__.py`
  - `A	src/datasets/base.py`
  - `A	src/datasets/msg_loader.py`
  - `A	src/datasets/schemas.py`
  - `A	src/datasets/seizeit2_loader.py`
  - `M	tests/test_dataset_parsers.py`

### 033. `12ca0b9` - Add recording-wise split audits for local SeizeIT2 checks

- Full SHA: `12ca0b9161c6d6663a02c60ba3498f703fe74cb3`
- Date: `2026-05-15T13:51:13+02:00`
- Author: `Oussama Akir`
- Shortstat: 9 files changed, 212 insertions(+), 2 deletions(-)
- Body:

```text
Introduce a recording_wise split strategy and CLI support so single-patient, multi-recording smoke checks can avoid sharing a recording across train/val/test. This is specifically for local SeizeIT2-style runs where patient-wise splitting is impossible and absolute recording timestamps can be reset or dummy values.

Update leakage_audit so non-temporal strategies report temporal ordering as not evaluated instead of emitting a misleading prospective-leakage result. Patient overlap remains visible, recording overlap is still machine-checked, and the docs state that recording-wise splits do not support prospective or patient-generalization claims.

Document the new command in REAL_DATA_QUICKSTART and COMMANDS, keep generated local leakage audits ignored, and add regression coverage for recording-disjoint splits. Verified before commit with: uv run --extra dev --extra torch python -m pytest -q; uv run --extra dev ruff check .
```
- Files changed:
  - `M	.gitignore`
  - `M	PROJECT_STATUS.md`
  - `M	docs/COMMANDS.md`
  - `M	docs/REAL_DATA_QUICKSTART.md`
  - `A	scripts/make_splits.py`
  - `M	src/splits/__init__.py`
  - `M	src/splits/leakage_checks.py`
  - `A	src/splits/recording_split.py`
  - `M	tests/test_no_temporal_leakage.py`

### 034. `372efd7` - Use audited labels for random baseline generation

- Full SHA: `372efd79c452a9ea64f2457e88ec4c8f25c11397`
- Date: `2026-05-15T13:57:50+02:00`
- Author: `Oussama Akir`
- Shortstat: 5 files changed, 65 insertions(+), 11 deletions(-)
- Body:

```text
Fix run_baseline so real-data baselines can consume an existing labeled-window table via --labels instead of silently recomputing SPH/SOP labels and exclusion masks from windows/events.

This matters for MSG long-horizon checks because labels were generated with a 240 minute postictal exclusion, while the previous baseline CLI relabeled with its default 60 minute exclusion. That could make prediction masks, Brier/ECE inputs, FAR denominators, and report label distributions inconsistent.

Update the real-data quickstart to pass --labels, add a CLI regression test proving excluded windows remain excluded, and regenerate the tracked local pipeline-check reports. These reports remain audit planning artifacts only, not clinical results.

Verified before commit with: uv run python -m pytest -q; uv run ruff check .; uv run --extra dev --extra torch python -m pytest -q; uv run --extra dev ruff check .
```
- Files changed:
  - `M	docs/REAL_DATA_QUICKSTART.md`
  - `M	reports/msg_partial_real_check/dataset_report.md`
  - `M	reports/seizeit2_sub125_real_check/dataset_report.md`
  - `M	scripts/run_baseline.py`
  - `M	tests/test_random_baseline.py`

### 035. `5167a1a` - Add MSG HR ACC feature and rule baselines

- Full SHA: `5167a1aac128dd236406d20d9c201fb5a4626e6a`
- Date: `2026-05-15T14:05:53+02:00`
- Author: `Oussama Akir`
- Shortstat: 7 files changed, 419 insertions(+)
- Body:

```text
Add a streaming MSG Empatica feature extractor that reads nested Mayo_*.zip archives one recording at a time and produces per-window HR and ACC summary features without materializing all raw samples into one table.

Add extract_msg_features.py and run_rule_baseline.py so the benchmark can run transparent HR tachycardia, ACC energy, and generic z-score baselines before any deep model work. Rule alarms are calibrated only on windows with available feature evidence and excluded windows are forced to alarm=False.

Document the commands in REAL_DATA_QUICKSTART and COMMANDS. Add tests for nested Empatica feature extraction and for rule-baseline exclusion/missing-feature behavior.

Verified before commit with: uv run python -m pytest -q; uv run ruff check .; uv run --extra dev --extra torch python -m pytest -q; uv run --extra dev ruff check .; real smoke extraction on downloaded MSG ZIPs with --max-recordings.
```
- Files changed:
  - `M	docs/COMMANDS.md`
  - `M	docs/REAL_DATA_QUICKSTART.md`
  - `A	scripts/extract_msg_features.py`
  - `A	scripts/run_rule_baseline.py`
  - `M	src/features/__init__.py`
  - `A	src/features/msg_empatica.py`
  - `M	tests/test_features.py`

### 036. `2fc9428` - Document full MSG pipeline check artifacts

- Full SHA: `2fc9428df3d1cc66a8f04e01a1e7a38f21fd86b9`
- Date: `2026-05-15T14:14:51+02:00`
- Author: `Oussama Akir`
- Shortstat: 6 files changed, 129 insertions(+), 9 deletions(-)
- Body:

```text
Record the local full-download MSG pipeline state after all Zenodo Mayo_*.zip files completed: 2070 wearable segments, 768 seizure onsets, and 510 onsets matched to downloaded wearable segments.

Add markdown reports for the full-download random rate-matched baseline and the HR tachycardia rule baseline. The reports explicitly remain pipeline/audit artifacts, not clinical evidence.

Update project status, manifest, human intervention checkpoints, and v1.0 acceptance criteria to reflect that the remaining blockers are manual seizure timeline audit, split freeze, and normalization/feature-fit leakage audit.

Verified before commit with: uv run --extra dev --extra torch python -m pytest -q; uv run --extra dev ruff check .
```
- Files changed:
  - `M	MANIFEST.md`
  - `M	PROJECT_STATUS.md`
  - `M	docs/HUMAN_INTERVENTION_CHECKPOINTS.md`
  - `M	docs/VERSION_ACCEPTANCE_CRITERIA.md`
  - `A	reports/msg_full_real_check/dataset_report.md`
  - `A	reports/msg_hr_tachycardia_check/dataset_report.md`

### 037. `3f9b4b2` - Tighten SOTA framing after current literature check

- Full SHA: `3f9b4b2bdc67e256379b96549f4e60a38da85f97`
- Date: `2026-05-15T14:19:25+02:00`
- Author: `Oussama Akir`
- Shortstat: 2 files changed, 54 insertions(+), 16 deletions(-)
- Body:

```text
Update the SOTA snapshot with verified 2025/2026 context: SeizeIT2 Scientific Data, MSG Zenodo, Nasseri et al. Epilepsia 2025 wearable forecasting, Journal of Neurology 2024 seizure-forecast meta-analysis, ICLR 2024 wearable biosignal foundation models, and PaPaGei.

Clarify that EpiTwin-Open must not claim to be the first wearable seizure-forecasting system. The defensible contribution is an open, leakage-safe, clinically constrained benchmark with forecastability and observability analysis over public data.

Update the publication proposal readiness state to reflect the completed local MSG full-download pipeline check and the remaining blocker: manual seizure timeline audit before frozen splits, A100 training, or paper claims.

Verified before commit with: uv run --extra dev ruff check .
```
- Files changed:
  - `M	docs/PUBLICATION_PROPOSAL.md`
  - `M	docs/SOTA_REVIEW_2026.md`

### 038. `f45f76b` - Add human label audit packets

- Full SHA: `f45f76b595316eb02d133d8f36f2bd81f64eefe9`
- Date: `2026-05-15T14:23:43+02:00`
- Author: `Oussama Akir`
- Shortstat: 7 files changed, 614 insertions(+)
- Body:

```text
Add a Markdown audit-packet generator for seizure-centered label review. The packet groups audit rows by event, shows state counts, and lists each window with minutes-to-seizure, forecast_label, ictal/postictal flags, exclusion status, and audit_state.

Generate local audit packets for SeizeIT2 sub-125 and the full MSG pipeline check so manual review can start from a compact document instead of only long CSV files.

This is explicitly an audit aid, not a clinical result. It is meant to catch parser mistakes, SPH/SOP boundary errors, ictal/postictal exclusion issues, and seizure-cluster edge cases before split freeze or A100 training.

Verified before commit with: uv run python -m pytest -q; uv run ruff check .; uv run --extra dev --extra torch python -m pytest -q; uv run --extra dev ruff check .
```
- Files changed:
  - `M	docs/COMMANDS.md`
  - `M	docs/REAL_DATA_QUICKSTART.md`
  - `A	reports/msg_full_audit_packet.md`
  - `A	reports/seizeit2_sub125_audit_packet.md`
  - `A	scripts/make_audit_packet.py`
  - `A	src/reports/audit_packet.py`
  - `A	tests/test_audit_packet.py`

### 039. `29fd714` - Add Claude review handoff and cycle baseline

- Full SHA: `29fd71486e0b121e36d11827f3202f50b7f1520c`
- Date: `2026-05-15T15:59:31+02:00`
- Author: `Oussama Akir`
- Shortstat: 14 files changed, 1363 insertions(+), 2 deletions(-)
- Body:

```text
Add a detailed Claude Code review handoff documenting the last work session: pushed commits, MSG download and full pipeline checks, SeizeIT2 local status, SOTA boundaries, generated audit artifacts, known risks, and exact review questions.

Add a split-safe hour-of-day cycle baseline for MSG. The baseline fits empirical patient/hour-of-day risk on the train split and selects the alarm threshold on the validation split, avoiding the test-threshold-fitting issue present in simple pipeline checks.

Extend make_dataset_report with prediction filtering and event-denominator restriction so split-level reports can count only events that are actually coverable by selected prediction horizons. Add a local MSG temporal-test cycle report as an audit artifact, not a clinical result.

Verified before commit with: uv run python -m pytest -q; uv run ruff check .; uv run --extra dev --extra torch python -m pytest -q; uv run --extra dev ruff check .
```
- Files changed:
  - `M	MANIFEST.md`
  - `M	PROJECT_STATUS.md`
  - `A	docs/CODEX_TO_CLAUDE_REVIEW_2026-05-15.md`
  - `M	docs/COMMANDS.md`
  - `M	docs/PUBLICATION_PROPOSAL.md`
  - `M	docs/REAL_DATA_QUICKSTART.md`
  - `M	docs/VERSION_ACCEPTANCE_CRITERIA.md`
  - `A	reports/msg_cycle_hour_test_check/dataset_report.md`
  - `M	scripts/make_dataset_report.py`
  - `A	scripts/run_cycle_baseline.py`
  - `M	src/baselines/__init__.py`
  - `A	src/baselines/cycle_baseline.py`
  - `A	tests/test_cycle_baseline.py`
  - `A	tests/test_dataset_report.py`

### 040. `1976b95` - Add MSG event coverage audit summary

- Full SHA: `1976b95768d314794b188761c22bfcfa0d67edd1`
- Date: `2026-05-15T16:09:15+02:00`
- Author: `Oussama Akir`
- Shortstat: 8 files changed, 420 insertions(+), 11 deletions(-)
- Body:

```text
Add a reusable event-coverage report that summarizes matched, unmatched, and unknown seizure onsets per patient, parsed recording hours, and seizure-cluster size before event-level metrics are interpreted.

Generate a local MSG coverage artifact showing 768 total onsets, 510 matched onsets, and patients 1219/1675/1942 with seizure annotations but zero parsed wearable recordings. This is an audit finding, not a clinical result.

Update the Claude review handoff, project status, and command docs so a methods reviewer can focus on denominator validity, unmatched events, and seizure clusters before split freeze or A100 training.

Verified with: uv run --extra dev --extra torch python -m pytest -q; uv run --extra dev ruff check .
```
- Files changed:
  - `M	PROJECT_STATUS.md`
  - `M	docs/CODEX_TO_CLAUDE_REVIEW_2026-05-15.md`
  - `M	docs/COMMANDS.md`
  - `M	docs/REAL_DATA_QUICKSTART.md`
  - `A	reports/msg_event_coverage_summary.md`
  - `A	scripts/summarize_event_coverage.py`
  - `A	src/reports/event_coverage.py`
  - `A	tests/test_event_coverage.py`

### 041. `9bb929c` - Add recording-boundary temporal splits

- Full SHA: `9bb929c98d5b18016f4c71c426aa578156eae091`
- Date: `2026-05-15T16:15:23+02:00`
- Author: `Oussama Akir`
- Shortstat: 10 files changed, 303 insertions(+), 28 deletions(-)
- Body:

```text
Add temporal split support for whole-recording assignment so long wearable segments can stay inside a single train, validation, or test split while preserving per-patient chronological ordering.

Extend leakage audit handling for temporal_recording strategies and add tests that verify recordings remain split-disjoint and temporally ordered.

Generate local MSG audit artifacts for the recording-boundary split and cycle-hour pipeline check. These reports remain audit aids only and do not support clinical or paper claims until timelines, labels, normalization, and split policy are manually reviewed.

Verified with: uv run --extra dev --extra torch python -m pytest -q; uv run --extra dev ruff check .
```
- Files changed:
  - `M	PROJECT_STATUS.md`
  - `M	docs/CODEX_TO_CLAUDE_REVIEW_2026-05-15.md`
  - `M	docs/COMMANDS.md`
  - `M	docs/REAL_DATA_QUICKSTART.md`
  - `A	reports/msg_cycle_hour_recording_test_check/dataset_report.md`
  - `A	reports/msg_temporal_recording_leakage_audit.md`
  - `M	scripts/make_splits.py`
  - `M	src/splits/leakage_checks.py`
  - `M	src/splits/temporal_split.py`
  - `M	tests/test_no_temporal_leakage.py`

### 042. `841dc65` - Make rule baselines split-aware

- Full SHA: `841dc6587fd84b4cda68b6a974455ff268d60c11`
- Date: `2026-05-15T16:28:59+02:00`
- Author: `Oussama Akir`
- Shortstat: 10 files changed, 340 insertions(+), 38 deletions(-)
- Body:

```text
Fit transparent rule baseline feature statistics and score normalization on training rows when a split column is present, and select alarm thresholds on validation rows by default.

Extend dataset reports with prediction metadata so reviewers can see score_fit_split, threshold_source_split, alarm thresholds, selected split rows, and valid prediction counts.

Generate a local MSG HR tachycardia pipeline-check report using recording-boundary temporal splits, train-fitted scores, validation-selected threshold, and test-only evaluation. This report remains unaudited and is not clinical evidence.

Verified with: uv run --extra dev --extra torch python -m pytest -q; uv run --extra dev ruff check .
```
- Files changed:
  - `M	PROJECT_STATUS.md`
  - `M	docs/CODEX_TO_CLAUDE_REVIEW_2026-05-15.md`
  - `M	docs/COMMANDS.md`
  - `M	docs/REAL_DATA_QUICKSTART.md`
  - `A	reports/msg_hr_tachycardia_recording_splitaware_check/dataset_report.md`
  - `M	scripts/make_dataset_report.py`
  - `M	scripts/run_rule_baseline.py`
  - `M	src/baselines/simple_rules.py`
  - `M	tests/test_dataset_report.py`
  - `M	tests/test_features.py`

### 043. `b662aeb` - Refresh publication proposal SOTA boundaries

- Full SHA: `b662aebf00d96035254ee195c58f5e840d34f17a`
- Date: `2026-05-15T16:32:07+02:00`
- Author: `Oussama Akir`
- Shortstat: 2 files changed, 39 insertions(+), 5 deletions(-)
- Body:

```text
Update the SOTA snapshot with 2025 SeizeIT2 ECG detection benchmarking, 2026 RNS-derived SeizureFormer forecasting, and 2026 wearable circadian phase-locking work.

Tighten the publication proposal so the current local MSG split-aware HR results are described as audit signals only, not clinical or paper results.

Keep the contribution claim conditional: EpiTwin-Open is currently a rigorous open benchmark pipeline with public-data audit artifacts; a major scientific contribution still depends on manual label audits, frozen splits, leakage-checked normalization, and final real-data tables.

Verified with: uv run --extra dev --extra torch python -m pytest -q; uv run --extra dev ruff check .
```
- Files changed:
  - `M	docs/PUBLICATION_PROPOSAL.md`
  - `M	docs/SOTA_REVIEW_2026.md`

### 044. `df64c9b` - Remediate critical benchmark audit findings

- Full SHA: `df64c9bd0e6ecb140aa349d0da61ef417fc0e656`
- Date: `2026-05-15T17:53:38+02:00`
- Author: `Oussama Akir`
- Shortstat: 24 files changed, 675 insertions(+), 50 deletions(-)
- Body:

```text
Phase R starts from the Claude methods review and preserves the actionable review in docs/CLAUDE_REVIEW_2026-05-15.md.

C1 closed: threshold sweeps now fail closed. A predictions table with split metadata requires --sweep-filter, split=test sweeps are refused by default, and outputs record sweep scope plus a falsifiability statement. Tests cover the mutant paths: no split filter and test-split sweep both fail.

C2 closed in the real label-generation path: generated windows now carry recording_start/recording_end, label_windows requires recording_end by default, and label_forecast_windows marks horizons beyond recording_end as is_right_censored and excluded.

C3 closed for rule baselines: empty train/reference scopes now raise ValueError instead of silently returning zero scores or no alarms. Tests cover held-out patient references and empty normalization references.

C4/H1 made explicit: dataset reports now require acknowledgement for recording_match_status=matched, write an event denominator table, distinguish source/filter/coverage denominators, and document seizure-level metrics with clusters not collapsed.

MSG right-censoring changed the local SPH60/SOP1440 audit materially: valid windows dropped from 47,713 to 4,854 out of 49,596 because 44,708 windows have horizons extending beyond parsed recording ends. Right-censored reports are regenerated and remain audit artifacts only, not clinical results.

Falsifiability: this remediation is false if scripts/sweep_thresholds.py can tune thresholds on test without explicit override, if label_windows.py accepts real-data windows without recording_end by default, if rule baselines silently produce all-zero scores for empty references, or if MSG matched-subset reports omit source/filter/coverage denominators.

Advisor-checkpoint: Required before M3/M4 or A100. Claude/advisor must review C1-C4 remediation and explicitly mark M2 closed; until then these are plumbing fixes, not publishable results.

Verified with: uv run --extra dev --extra torch python -m pytest -q; uv run --extra dev ruff check .; 83 tests collected/passing.
```
- Files changed:
  - `M	PROJECT_STATUS.md`
  - `M	README.md`
  - `A	docs/CLAUDE_REVIEW_2026-05-15.md`
  - `M	docs/CODEX_TO_CLAUDE_REVIEW_2026-05-15.md`
  - `M	docs/COMMANDS.md`
  - `M	docs/PUBLICATION_PROPOSAL.md`
  - `M	docs/REAL_DATA_QUICKSTART.md`
  - `M	reports/msg_cycle_hour_recording_test_check/dataset_report.md`
  - `M	reports/msg_full_audit_packet.md`
  - `M	reports/msg_full_real_check/dataset_report.md`
  - `A	reports/msg_full_real_check_coverable/dataset_report.md`
  - `M	reports/msg_hr_tachycardia_recording_splitaware_check/dataset_report.md`
  - `M	scripts/label_windows.py`
  - `M	scripts/make_dataset_report.py`
  - `M	scripts/run_rule_baseline.py`
  - `M	scripts/sweep_thresholds.py`
  - `M	src/baselines/simple_rules.py`
  - `M	src/labeling/sph_sop.py`
  - `M	src/preprocessing/windowing.py`
  - `M	tests/test_dataset_report.py`
  - `M	tests/test_features.py`
  - `M	tests/test_labeling_edge_cases.py`
  - `A	tests/test_threshold_sweep_cli.py`
  - `M	tests/test_windowing.py`

### 045. `4345e08` - Make leakage audit adversarial

- Full SHA: `4345e0877de982382f3cfd93f8d1de93e0ff84ff`
- Date: `2026-05-15T17:57:24+02:00`
- Author: `Oussama Akir`
- Shortstat: 4 files changed, 115 insertions(+), 4 deletions(-)
- Body:

```text
Address Phase R high findings H2/H3 by replacing the static normalization-leakage reassurance with an explicit UNVERIFIED_OR_FAILED status when fit-scope metadata is absent or test-scoped.

Add duplicate recording time-range detection so reset or duplicated recording timestamps are surfaced before temporal splits are trusted. The regenerated MSG audit now flags duplicate patient 2002 recording ranges with suffixed recording IDs.

Falsifiability: this gate is false if leakage_audit reports normalization as clean without score_fit_split/threshold_source_split metadata, if score_fit_split=test is not flagged, or if duplicated per-patient recording time ranges are not reported.

Advisor-checkpoint: Advisor must review whether duplicate MSG patient 2002 intervals are true duplicate archives, parser artifacts, or valid repeated files before M2 can be closed.

Verified with: uv run --extra dev --extra torch python -m pytest -q; uv run --extra dev ruff check .; 86 tests collected/passing.
```
- Files changed:
  - `M	PROJECT_STATUS.md`
  - `M	reports/msg_temporal_recording_leakage_audit.md`
  - `M	src/splits/leakage_checks.py`
  - `M	tests/test_no_temporal_leakage.py`

### 046. `8139bde` - Split temporal folds by elapsed time

- Full SHA: `8139bdec30a6587fbc498e5e37f1e840b78ebf03`
- Date: `2026-05-15T18:03:01+02:00`
- Author: `Oussama Akir`
- Shortstat: 9 files changed, 104 insertions(+), 14 deletions(-)
- Body:

```text
Address Phase R H4 by changing temporal split boundaries from row/recording counts to elapsed patient time by default. The legacy count basis remains available only via explicit --temporal-basis count.

Update make_splits.py with --temporal-basis, propagate the basis into audit strategy labels, and add a regression test where dense early windows no longer dominate fold boundaries.

Regenerate MSG right-censored split-aware cycle and HR reports using temporal_recording_elapsed_time. The split now has 33,853 train windows, 5,415 validation windows, and 10,328 test windows.

Falsifiability: this gate is false if temporal splits default to row count, if dense sampling changes temporal fold duration, or if the split audit does not record the temporal basis used.

Advisor-checkpoint: Advisor must confirm elapsed-time temporal splitting is the intended default for MSG before M2 closure; count-based splits are now diagnostic only.

Verified with: uv run --extra dev --extra torch python -m pytest -q; uv run --extra dev ruff check .; 87 tests collected/passing.
```
- Files changed:
  - `M	PROJECT_STATUS.md`
  - `M	docs/COMMANDS.md`
  - `M	docs/REAL_DATA_QUICKSTART.md`
  - `M	reports/msg_cycle_hour_recording_test_check/dataset_report.md`
  - `M	reports/msg_hr_tachycardia_recording_splitaware_check/dataset_report.md`
  - `M	reports/msg_temporal_recording_leakage_audit.md`
  - `M	scripts/make_splits.py`
  - `M	src/splits/temporal_split.py`
  - `M	tests/test_no_temporal_leakage.py`

### 047. `f45c3aa` - Expose imputed MSG seizure durations

- Full SHA: `f45c3aa58f578ae88a6b4fe050bdf937c0777cf0`
- Date: `2026-05-15T18:06:35+02:00`
- Author: `Oussama Akir`
- Shortstat: 7 files changed, 66 insertions(+)
- Body:

```text
Address Phase R H5 by adding an Event Annotation section to dataset reports. MSG onset-only seizure annotations now report how many seizure_end values are imputed and which imputed duration values are present.

Regenerate MSG right-censored reports so they show seizure_end_imputed_events=768 and imputed_duration_seconds_values=60.0. These durations are parser placeholders, not measured clinical seizure durations.

Falsifiability: this gate is false if a report can present MSG seizure_end as measured ground truth when seizure_end_imputed metadata is present.

Advisor-checkpoint: Advisor should confirm whether onset-only MSG events may be used for ictal/postictal exclusion with a 60-second placeholder, or whether postictal exclusion should anchor only to onset for this dataset.

Verified with: uv run --extra dev --extra torch python -m pytest -q; uv run --extra dev ruff check .; 88 tests collected/passing.
```
- Files changed:
  - `M	PROJECT_STATUS.md`
  - `M	reports/msg_cycle_hour_recording_test_check/dataset_report.md`
  - `M	reports/msg_full_real_check/dataset_report.md`
  - `M	reports/msg_full_real_check_coverable/dataset_report.md`
  - `M	reports/msg_hr_tachycardia_recording_splitaware_check/dataset_report.md`
  - `M	scripts/make_dataset_report.py`
  - `M	tests/test_dataset_report.py`

### 048. `73d07dc` - Add Phase R Claude review handoff

- Full SHA: `73d07dc84d4f8bca2ca22db65a034de8279eb08b`
- Date: `2026-05-15T20:41:27+02:00`
- Author: `Oussama Akir`
- Shortstat: 1 file changed, 717 insertions(+)
- Body:

```text
Document the last 24h of Codex Phase R remediation work for Claude Code review, including C1-C4/H1-H5 changes, regenerated MSG audit artifacts, commands, test status, falsifiability checks, and remaining advisor blockers.

The handoff explicitly states that current MSG numbers are audit signals only, that A100 and M3/M4 remain blocked, and that M2 requires advisor review before closure.

Verified with: uv run --extra dev --extra torch python -m pytest -q; uv run --extra dev ruff check .
```
- Files changed:
  - `A	docs/CODEX_TO_CLAUDE_PHASE_R_REVIEW_2026-05-15.md`

### 049. `da6a489` - Close Phase R safety gaps after Claude audit

- Full SHA: `da6a4893c16622b1f9ab7a0535648ba363bb4e23`
- Date: `2026-05-15T23:37:30+02:00`
- Author: `Oussama Akir`
- Shortstat: 26 files changed, 926 insertions(+), 168 deletions(-)
- Body:

```text
Address the second Claude Phase R audit summary with fail-closed fixes in the library and data plumbing rather than only the CLI paths. The audit report commit 17d298b was not present locally or on origin, so this commit targets the explicit P0/C1/C3/H3 findings included in the user-provided summary.

P0 right-censoring: keep is_right_censored as a horizon-boundary flag, but exclude only right-censored unknown negatives. Confirmed positives whose seizure onset is observed inside the SPH/SOP interval now remain valid unless ictal/postictal. Regenerated MSG SPH60/SOP1440 audit reports; valid positives changed from 260 to 3325, proving the previous reports were materially invalid.

C1 threshold tuning: move split-scope enforcement into src.metrics.sweep. threshold_sweep_table and fixed-FAR/TIW sweep helpers now refuse unsplit tables, full split tables, and split=test by default. The CLI delegates to this library guard and records publishable_threshold_tuning metadata.

C3 rule baselines: remove silent zero-score/no-alarm paths for missing rule features and missing patient thresholds. HR/ACC/generic z-score rules now raise on absent requested features; patient-specific thresholding now raises when calibration scores or per-patient thresholds are missing.

H3 duplicate recording ranges: temporal splits now fail closed on exact duplicate recording time ranges. MSG parsing exposes an explicit duplicate policy, defaulting to error with drop_exact only after documenting duplicated files. Added a processed-recording cleanup CLI for local MSG artifacts and regenerated reports after dropping two exact patient-2002 copy segments.

Validation: pytest and ruff pass in both the Git checkout and the Windows working tree. Synthetic demo and one-epoch SSL smoke training pass. A100 remains blocked; regenerated MSG numbers are audit signals only and require manual timeline review before any scientific claim.
```
- Files changed:
  - `A	docs/CODEX_PHASE_R2_REMEDIATION_2026-05-15.md`
  - `M	reports/msg_cycle_hour_recording_test_check/dataset_report.md`
  - `M	reports/msg_event_coverage_summary.md`
  - `M	reports/msg_full_audit_packet.md`
  - `M	reports/msg_full_real_check/dataset_report.md`
  - `M	reports/msg_full_real_check_coverable/dataset_report.md`
  - `M	reports/msg_hr_tachycardia_recording_splitaware_check/dataset_report.md`
  - `A	reports/msg_hr_tachycardia_recording_splitaware_leakage_audit.md`
  - `M	reports/msg_temporal_recording_leakage_audit.md`
  - `A	scripts/clean_msg_recordings.py`
  - `M	scripts/make_splits.py`
  - `M	scripts/prepare_msg.py`
  - `M	scripts/sweep_thresholds.py`
  - `M	src/baselines/simple_rules.py`
  - `M	src/calibration/thresholding.py`
  - `M	src/datasets/msg_loader.py`
  - `M	src/labeling/sph_sop.py`
  - `M	src/metrics/__init__.py`
  - `M	src/metrics/sweep.py`
  - `M	src/splits/temporal_split.py`
  - `M	tests/test_calibration_thresholding.py`
  - `M	tests/test_dataset_parsers.py`
  - `M	tests/test_features.py`
  - `M	tests/test_labeling_edge_cases.py`
  - `M	tests/test_metric_sweep.py`
  - `M	tests/test_no_temporal_leakage.py`

### 050. `180d42d` - Add cluster metrics and onset-only postictal policy

- Full SHA: `180d42dfd85edb3850f73db97a2ab34839ec8b5c`
- Date: `2026-05-16T00:57:42+02:00`
- Author: `Oussama Akir`
- Shortstat: 20 files changed, 667 insertions(+), 36 deletions(-)
- Body:

```text
Convert two remaining Phase R policy gaps into executable benchmark behavior. H1 cluster handling now has a first-event cluster-level metric path, and onset-only MSG annotations no longer silently anchor postictal exclusion to imputed seizure_end values.

Cluster metrics: add assign_event_clusters and collapse_event_clusters, preserve recording scope by default, expose --event-unit cluster in make_dataset_report and evaluate_predictions, and regenerate separate MSG cluster-level HR/cycle audit reports. Cluster reporting keeps seizure-level and cluster-level denominators separate instead of hiding the policy in prose.

Postictal policy: label_forecast_windows accepts postictal_anchor=seizure_end|seizure_start. scripts/label_windows.py now fails when seizure_end_imputed=True is used with seizure_end anchoring unless explicitly overridden. Regenerated MSG labels with --postictal-anchor seizure_start for onset-only annotations.

Current MSG audit signals after this policy: labels have 49,577 windows, 7,920 valid windows, 3,326 valid positives. HR tachycardia test seizure-level denominator is 54 events with 46 forecasted; cluster-level denominator is 40 clusters with 33 forecasted. These remain audit signals only, not clinical claims.

Validation: pytest and ruff pass in both /tmp/epitwin-open-push and /mnt/c/doctorat/iot/epitwin-open; synthetic demo and one-epoch SSL smoke training pass. A100 remains blocked until manual timeline audit and advisor/Claude approval.
```
- Files changed:
  - `A	docs/CODEX_PHASE_R3_CLUSTER_AND_POSTICTAL_POLICY_2026-05-16.md`
  - `M	docs/COMMANDS.md`
  - `M	docs/REAL_DATA_QUICKSTART.md`
  - `A	reports/msg_cycle_hour_cluster_recording_test_check/dataset_report.md`
  - `M	reports/msg_cycle_hour_recording_test_check/dataset_report.md`
  - `M	reports/msg_full_real_check/dataset_report.md`
  - `M	reports/msg_full_real_check_coverable/dataset_report.md`
  - `A	reports/msg_hr_tachycardia_cluster_recording_splitaware_check/dataset_report.md`
  - `M	reports/msg_hr_tachycardia_recording_splitaware_check/dataset_report.md`
  - `M	reports/msg_hr_tachycardia_recording_splitaware_leakage_audit.md`
  - `M	reports/msg_temporal_recording_leakage_audit.md`
  - `M	scripts/evaluate_predictions.py`
  - `M	scripts/label_windows.py`
  - `M	scripts/make_dataset_report.py`
  - `M	src/labeling/sph_sop.py`
  - `M	src/metrics/__init__.py`
  - `M	src/metrics/event_metrics.py`
  - `M	tests/test_dataset_report.py`
  - `M	tests/test_event_metrics.py`
  - `M	tests/test_labeling_edge_cases.py`

### 051. `b1cccf6` - Refresh status docs after Phase R3

- Full SHA: `b1cccf671ba0a9b26aa2f7b92ed8c6e30cbfa119`
- Date: `2026-05-16T01:00:58+02:00`
- Author: `Oussama Akir`
- Shortstat: 10 files changed, 53 insertions(+), 30 deletions(-)
- Body:

```text
Update README, project status, release-candidate report, risk register, SOTA snapshot, and publication proposal after the Phase R2/R3 methodological fixes. Remove stale test counts and stale MSG feasibility numbers, document the current 99-test checkpoint, and mark the old Phase R handoff as superseded where it mentions the invalid 13-event denominator.

Also replace stray edge/hardware wording flagged by the audit, recheck the arXiv 2604.18297 SOTA reference on 2026-05-16, and repair the MSG temporal leakage audit markdown fence.

Validation: uv run --extra dev --extra torch python -m pytest -q; uv run --extra dev ruff check .
```
- Files changed:
  - `M	PROJECT_STATUS.md`
  - `M	README.md`
  - `M	docs/CODEX_TO_CLAUDE_PHASE_R_REVIEW_2026-05-15.md`
  - `M	docs/HUMAN_INTERVENTION_CHECKPOINTS.md`
  - `M	docs/PUBLICATION_PROPOSAL.md`
  - `M	docs/RISK_REGISTER.md`
  - `M	docs/SOTA_REVIEW_2026.md`
  - `M	reports/48h_milestone_template.md`
  - `M	reports/msg_temporal_recording_leakage_audit.md`
  - `M	reports/v1_0_release_candidate.md`

### 052. `edd8879` - Add manual label audit review sheet

- Full SHA: `edd8879b0022f51f6adc1b62e70c910414ef791c`
- Date: `2026-05-16T01:07:35+02:00`
- Author: `Oussama Akir`
- Shortstat: 4 files changed, 310 insertions(+), 1 deletion(-)
- Body:

```text
Add a one-row-per-event review sheet generator for human SPH/SOP label audits. The sheet carries reviewer decision columns, source-verification fields, right-censoring visibility, and precomputed anomaly counts for ictal/postictal rows that are not excluded.

Default event selection now spreads limited audit samples across patients instead of taking only the first sorted events, reducing the risk that the initial manual audit covers a single patient cluster. The label audit timeline also preserves is_right_censored for downstream review.

Validated with: uv run --extra dev --extra torch python -m pytest -q; uv run --extra dev ruff check .
```
- Files changed:
  - `M	docs/HUMAN_LABEL_AUDIT_PROTOCOL.md`
  - `A	scripts/make_label_audit_review_sheet.py`
  - `M	src/reports/label_audit.py`
  - `M	tests/test_label_audit.py`

### 053. `fd31135` - Gate completed label audit reviews

- Full SHA: `fd31135cf6a9b95b0b68eb49467dbd53de035c4d`
- Date: `2026-05-16T01:09:18+02:00`
- Author: `Oussama Akir`
- Shortstat: 4 files changed, 174 insertions(+), 1 deletion(-)
- Body:

```text
Add a blocking review-sheet validator for the mandatory human label audit checkpoint. The validator requires the expected review columns, a minimum event count, explicit PASS values for source/timestamp/SPH-SOP/exclusion/right-censoring checks, and zero precomputed ictal/postictal anomaly counts.

Add a CLI that exits non-zero for incomplete or failing audit sheets, so manual audit status is machine-checkable before A100 training or result reporting. The human audit protocol now documents the gate and states that an incomplete sheet is expected to fail.

Validated with: uv run --extra dev --extra torch python -m pytest -q; uv run --extra dev ruff check .; uv run python scripts/check_label_audit_review.py --review-sheet reports/msg_label_audit_review_sheet.csv --out reports/msg_label_audit_review_check.csv --min-events 5 (expected exit 2 for unfilled MSG sheet).
```
- Files changed:
  - `M	docs/HUMAN_LABEL_AUDIT_PROTOCOL.md`
  - `A	scripts/check_label_audit_review.py`
  - `M	src/reports/label_audit.py`
  - `M	tests/test_label_audit.py`

### 054. `6f31386` - Add horizon viability audit

- Full SHA: `6f313866475abac57c2b69c9d44dcba5ca01da13`
- Date: `2026-05-16T01:13:09+02:00`
- Author: `Oussama Akir`
- Shortstat: 5 files changed, 296 insertions(+)
- Body:

```text
Add a SPH/SOP horizon viability report that recomputes labels over candidate horizons and summarizes valid-window fraction, right-censoring burden, positive-window counts, and event coverability by valid windows.

Document the MSG workflow so SPH60/SOP1440 cannot become a headline task without checking recording coverage first. The committed MSG report shows SOP1440 is coverage-limited: only 7,920/49,577 windows remain valid for SPH60/SOP1440 and 41,178 windows are right-censored unknowns.

Validated with: uv run --extra dev --extra torch python -m pytest -q; uv run --extra dev ruff check .; uv run python scripts/summarize_horizon_viability.py --windows data/processed/msg/windows_1h.parquet --events data/processed/msg/events.parquet --out-csv reports/msg_horizon_viability.csv --out-md reports/msg_horizon_viability.md --sph-minutes 5 60 --sop-minutes 30 360 1440 --postictal-exclusion-minutes 240 --postictal-anchor seizure_start.
```
- Files changed:
  - `M	docs/REAL_DATA_QUICKSTART.md`
  - `A	reports/msg_horizon_viability.md`
  - `A	scripts/summarize_horizon_viability.py`
  - `A	src/reports/horizon_viability.py`
  - `A	tests/test_horizon_viability.py`

### 055. `ffc60d6` - Wire audit gates into runbooks

- Full SHA: `ffc60d605662b3e9810b09b61a20e0f502c61be8`
- Date: `2026-05-16T01:15:17+02:00`
- Author: `Oussama Akir`
- Shortstat: 4 files changed, 84 insertions(+), 10 deletions(-)
- Body:

```text
Add Makefile targets for MSG horizon viability, manual label-audit review-sheet generation, and the blocking completed-review check. Update A100 and human-checkpoint docs so these gates are part of the normal workflow instead of ad hoc commands.

Project status now records the horizon-viability and manual-review gate support, including the current SPH60/SOP1440 right-censoring warning: 7,920 valid windows, 44,689 right-censored windows, and 41,178 right-censored unknown negatives.

Validated with: uv run --extra dev --extra torch python -m pytest -q; uv run --extra dev ruff check .; direct script equivalents for msg-horizon-viability and msg-label-audit-check. The local shell lacks make, so Makefile targets were not executed via make in this environment.
```
- Files changed:
  - `M	Makefile`
  - `M	PROJECT_STATUS.md`
  - `M	docs/A100_RUNBOOK.md`
  - `M	docs/HUMAN_INTERVENTION_CHECKPOINTS.md`

### 056. `b338799` - Fix false alarm episode stride inference

- Full SHA: `b338799f914159d8f9cd3463e292ed1d2d8b85af`
- Date: `2026-05-16T01:19:18+02:00`
- Author: `Oussama Akir`
- Shortstat: 9 files changed, 77 insertions(+), 32 deletions(-)
- Body:

```text
False alarm episodes now infer the stream stride from all valid prediction windows rather than alarm windows only. This prevents sparse alarms separated by silent windows from being merged into a single false-alarm episode and undercounting FAR/day.

Added adversarial tests for separated alarms with intervening non-alarm windows and overlapping warning intervals. Regenerated current MSG random, cycle, and HR rule reports whose FAR/day values are affected by the stricter episode count.

Current affected audit signals after regeneration include random SPH60/SOP1440 FAR/day 1.2061 and split-aware HR tachycardia FAR/day 1.0663. These remain unaudited pipeline checks, not clinical results.

Validated with: uv run --extra dev --extra torch python -m pytest -q; uv run --extra dev ruff check .
```
- Files changed:
  - `M	PROJECT_STATUS.md`
  - `M	reports/msg_cycle_hour_cluster_recording_test_check/dataset_report.md`
  - `M	reports/msg_cycle_hour_recording_test_check/dataset_report.md`
  - `M	reports/msg_full_real_check/dataset_report.md`
  - `M	reports/msg_full_real_check_coverable/dataset_report.md`
  - `M	reports/msg_hr_tachycardia_cluster_recording_splitaware_check/dataset_report.md`
  - `M	reports/msg_hr_tachycardia_recording_splitaware_check/dataset_report.md`
  - `M	src/metrics/alarm_metrics.py`
  - `M	tests/test_alarm_metrics.py`

### 057. `a940098` - Mark legacy MSG reports superseded

- Full SHA: `a9400983f4d2b047fac27d0dc02857847a891d2a`
- Date: `2026-05-16T01:20:17+02:00`
- Author: `Oussama Akir`
- Shortstat: 3 files changed, 16 insertions(+)
- Body:

```text
Add explicit supersession warnings to older MSG report artifacts that predate Phase R right-censoring, recording-wise splits, onset-anchored postictal handling, cluster-denominator reporting, and false-alarm episode fixes.

This avoids stale report tables being mistaken for current pipeline checks. Current reports are the recording-split-aware cycle and HR reports plus the full/coverable random-baseline reports regenerated after the alarm episode correction.
```
- Files changed:
  - `M	reports/msg_cycle_hour_test_check/dataset_report.md`
  - `M	reports/msg_hr_tachycardia_check/dataset_report.md`
  - `M	reports/msg_partial_real_check/dataset_report.md`

### 058. `a20f61a` - chore(gitignore): ignore .pytest_tmp basetemp dir

- Full SHA: `a20f61aa2563e06596395a3f5a71cb9840ff4f39`
- Date: `2026-05-16T22:35:31+02:00`
- Author: `Akir Oussama`
- Shortstat: 1 file changed, 1 insertion(+)
- Body:

```text
The sandbox blocks pytest's default tmp_path location, so the test
suite is run with --basetemp=.pytest_tmp. Ignore that directory so
the workaround never enters a commit.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```
- Files changed:
  - `M	.gitignore`

### 059. `caf2da2` - feat(baselines): add population reference scope

- Full SHA: `caf2da23abc802ac442bd1727501922ef9229f35`
- Date: `2026-05-16T22:35:31+02:00`
- Author: `Akir Oussama`
- Shortstat: 3 files changed, 109 insertions(+), 22 deletions(-)
- Body:

```text
Phase R audit C3. The feature-rule baselines fit robust statistics
per patient, so a held-out patient with no rows in the score-fit
split was unscorable. This re-applies Claude's C3 remediation onto
the Codex Phase R branch after the two parallel audit efforts were
reconciled.

Gap 2: ecg_tachycardia_score, acc_energy_score and
generic_zscore_anomaly gain a reference_scope argument. "patient"
(default) keeps the prior per-patient behaviour; "population" pools
every fit-split reference row into one robust reference, so held-out
patients stay scorable on patient-wise splits. run_rule_baseline.py
exposes it as --reference-scope and records the chosen scope on each
prediction row.

Gap 1 coverage is completed too: the existing missing-column
mutation test exercised ecg_tachycardia_score and
generic_zscore_anomaly but not acc_energy_score; an acc_energy_score
block is added so all three fail-closed raises are covered.

Refs: docs/CLAUDE_PHASE_R_AUDIT_2026-05-15.md (C3)
Verified-By: uv run --extra dev python -m pytest -q tests/test_features.py --basetemp=.pytest_tmp  (9 passed)
Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```
- Files changed:
  - `M	scripts/run_rule_baseline.py`
  - `M	src/baselines/simple_rules.py`
  - `M	tests/test_features.py`

### 060. `74edfbc` - fix(labeling): require recording_end by default

- Full SHA: `74edfbccc56b5e25c7e333617954e3090e8b37d7`
- Date: `2026-05-16T22:35:31+02:00`
- Author: `Akir Oussama`
- Shortstat: 8 files changed, 99 insertions(+), 24 deletions(-)
- Body:

```text
Phase R audit C2. label_forecast_windows defaulted
require_recording_end to False, so a real-data caller that omitted
recording_end would silently turn unobserved future horizons into
true negatives instead of right-censoring them.

The default is now True: a caller with no recording_end fails
loudly, and only synthetic or legacy windows pass
require_recording_end=False explicitly. The seven affected synthetic
test callers are updated accordingly. Labels also carry a new
right_censoring_applied boolean so a downstream report cannot
mistake un-censored labels for censored ones.

Refs: docs/CLAUDE_PHASE_R_AUDIT_2026-05-15.md (C2)
Verified-By: uv run --extra dev python -m pytest -q tests/test_alarm_metrics.py tests/test_calibration.py tests/test_event_metrics.py tests/test_label_audit.py tests/test_labeling_edge_cases.py tests/test_postictal_exclusion.py tests/test_sph_sop_labeling.py --basetemp=.pytest_tmp  (31 passed)
Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```
- Files changed:
  - `M	src/labeling/sph_sop.py`
  - `M	tests/test_alarm_metrics.py`
  - `M	tests/test_calibration.py`
  - `M	tests/test_event_metrics.py`
  - `M	tests/test_label_audit.py`
  - `M	tests/test_labeling_edge_cases.py`
  - `M	tests/test_postictal_exclusion.py`
  - `M	tests/test_sph_sop_labeling.py`

### 061. `85f2a78` - feat(leakage): add three-state fit-scope status

- Full SHA: `85f2a7836db3637d12cc34ab869e5de6acf11c1b`
- Date: `2026-05-16T22:35:32+02:00`
- Author: `Akir Oussama`
- Shortstat: 2 files changed, 83 insertions(+), 9 deletions(-)
- Body:

```text
Phase R audit H2/H3. check_fit_scope_metadata conflated "no
predictions present, nothing to verify" with "predictions present
but fit metadata missing": both returned has_leakage=True, so a
plain label table looked like a leakage failure. It now returns an
explicit status -- not_applicable, unverified_or_failed, or
verified -- and leakage_audit prints the matching line.

H3: leakage_audit no longer prints a bare temporal-leakage verdict
when duplicate recording time ranges are present. It reports
UNRELIABLE, because duplicate ranges make temporal ordering
untrustworthy. Re-applied from Claude's audit branch.

Refs: docs/CLAUDE_PHASE_R_AUDIT_2026-05-15.md (H2, H3)
Verified-By: uv run --extra dev python -m pytest -q tests/test_no_temporal_leakage.py --basetemp=.pytest_tmp  (16 passed)
Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```
- Files changed:
  - `M	src/splits/leakage_checks.py`
  - `M	tests/test_no_temporal_leakage.py`

### 062. `2a4786e` - feat(report): render event denominators inline

- Full SHA: `2a4786e8bbc10e813d4fc49f9ea0e1241b0254c5`
- Date: `2026-05-16T22:35:32+02:00`
- Author: `Akir Oussama`
- Shortstat: 2 files changed, 65 insertions(+), 2 deletions(-)
- Body:

```text
Phase R audit C4. Two reporting gaps let a reader lose the basis of
a headline number.

The baseline table rendered sensitivity as a bare rate; it now
renders it as "0.852 (46/54 events)" so the event denominator
travels with the rate. The sensitivity column is therefore a string
display column -- n_events and n_forecasted stay as separate numeric
columns for any numeric use.

The bias-acknowledgement guard previously exact-matched the single
string recording_match_status=matched, so every other event filter
selected a non-random subset without acknowledgement. It now flags
any event filter whose column is not on an (empty) unbiased
allowlist.

Refs: docs/CLAUDE_PHASE_R_AUDIT_2026-05-15.md (C4)
Verified-By: uv run --extra dev python -m pytest -q tests/test_dataset_report.py --basetemp=.pytest_tmp  (7 passed)
Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```
- Files changed:
  - `M	scripts/make_dataset_report.py`
  - `M	tests/test_dataset_report.py`

### 063. `cf99ae6` - docs(playbook): add revision-2 playbook and audit

- Full SHA: `cf99ae66564336be05b28393205c90aad64c3703`
- Date: `2026-05-16T22:35:32+02:00`
- Author: `Akir Oussama`
- Shortstat: 2 files changed, 736 insertions(+)
- Body:

```text
Adds the revision-2 PLAYBOOK.md and the Phase R audit report the
remediation commits re-apply. The playbook reframes the objective
around a verifiably-SOTA published contribution and encodes the
Phase R findings; the audit report is the C1-C4 / H1-H5 source the
remediation commits reference.

PLAYBOOK section 5 states the MSG long-horizon denominators -- 54
seizure-level / 40 cluster-level coverable test events -- with their
source files cited inline, replacing the pre-remediation 13-event
figure that was a P0 over-exclusion artifact.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```
- Files changed:
  - `A	PLAYBOOK.md`
  - `A	docs/CLAUDE_PHASE_R_AUDIT_2026-05-15.md`

### 064. `141fc0c` - fix(msg_loader): emit POSIX paths in raw layout

- Full SHA: `141fc0cf3b9e884f859165aebc29568d569c976e`
- Date: `2026-05-16T22:35:32+02:00`
- Author: `Akir Oussama`
- Shortstat: 1 file changed, 1 insertion(+), 1 deletion(-)
- Body:

```text
inspect_msg_raw_layout rendered seizure_txt_files with
str(Path.relative_to()), which uses the OS-native separator --
backslashes on Windows, forward slashes on POSIX -- so
test_parse_msg_zenodo_seizure_times_only_txt failed on Windows.

For a public benchmark meant to be reproduced on any OS, the raw
layout must be platform-deterministic; .as_posix() always emits
forward slashes. Stash-tested against origin/feature: the failure
pre-existed this reconciliation and is unrelated to the audit
remediation, so it is fixed in its own commit.

Verified-By: uv run --extra dev python -m pytest -q tests/test_dataset_parsers.py --basetemp=.pytest_tmp  (12 passed)
Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```
- Files changed:
  - `M	src/datasets/msg_loader.py`

### 065. `d687d96` - docs(handoff): record reconciliation tip for Codex

- Full SHA: `d687d96e467aac8330dfa28279cf24c0b0f36a7f`
- Date: `2026-05-16T23:30:08+02:00`
- Author: `Akir Oussama`
- Shortstat: 1 file changed, 79 insertions(+)
- Body:

```text
After the 2026-05-15 Claude/Codex Phase R audit collision was
reconciled (Strategy A), Codex still holds the pre-reconciliation
origin/feature tip a940098 and would re-collide if it rebuilds on it.

Adds docs/CLAUDE_TO_CODEX_RECONCILIATION_2026-05-15.md: the canonical
tip is now 141fc0c, what the 7 reconciliation commits added, the
require_recording_end default flip Codex's scripts may need to
absorb, and the fetch-before-work coordination rule.

Refs: 141fc0c (Phase R reconciliation tip)
Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```
- Files changed:
  - `A	docs/CLAUDE_TO_CODEX_RECONCILIATION_2026-05-15.md`

### 066. `0177bb3` - docs(protocol): add per-dataset label-audit runbook

- Full SHA: `0177bb3565778f80f4848eb24ebb29a97579af71`
- Date: `2026-05-16T23:55:37+02:00`
- Author: `Akir Oussama`
- Shortstat: 1 file changed, 60 insertions(+), 10 deletions(-)
- Body:

```text
The human label audit protocol documented only SeizeIT2 sheet
generation and began mid-pipeline, after forecast_labels.parquet
already existed. Phase B audits both datasets, and MSG needs a
different label command: its onset-only annotations give an imputed
seizure_end, so label_windows.py fails closed unless postictal
exclusion is anchored with --postictal-anchor seizure_start.

Rewrites the section into an explicit per-dataset runbook -
label_windows, audit_labels, make_label_audit_review_sheet for
SeizeIT2 and MSG, plus the per-dataset blocking gate. Commands are
taken from docs/COMMANDS.md and the scripts' arguments; the
five-stage pipeline was verified end-to-end on mock data.

Refs: docs/COMMANDS.md
Verified-By: mock prepare_seizeit2 -> label_windows -> audit_labels -> make_label_audit_review_sheet -> check_label_audit_review ran end-to-end (sheet generated; gate exit 2 on unfilled sheet)
Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```
- Files changed:
  - `M	docs/HUMAN_LABEL_AUDIT_PROTOCOL.md`

### 067. `bffe503` - fix(sweep): refuse non-split sweep filter

- Full SHA: `bffe503e3508cd173b1e4c7f0ad12a4b5b270ce7`
- Date: `2026-05-17T21:48:39+02:00`
- Author: `Akir Oussama`
- Shortstat: 3 files changed, 66 insertions(+)
- Body:

```text
Phase R audit C1 Gap 2. scope_predictions_for_threshold_sweep keyed
the split-scope guard off _split_value, which silently returns None
for any sweep filter whose column is not split. A non-split filter
such as --sweep-filter score_fit_split=train (a constant column
run_rule_baseline.py writes into every prediction table) therefore
ran the threshold sweep across train+val+test rows instead of being
refused. It was stamped publishable_threshold_tuning=False, so the
audit's worst harm was already gone, but the prescribed raise was
not implemented.

The guard now raises when the sweep-filter column is not split.
Non-split-bypass tests added at library level (test_metric_sweep.py)
and CLI level (test_threshold_sweep_cli.py). This closes the last
code item on the Phase R audit M2 punch list.

Refs: docs/CLAUDE_PHASE_R_AUDIT_2026-05-15.md (C1 Gap 2)
Verified-By: uv run --extra dev --extra torch python -m pytest -q --basetemp=.pytest_tmp  (all pass, 0 failures)
Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```
- Files changed:
  - `M	src/metrics/sweep.py`
  - `M	tests/test_metric_sweep.py`
  - `M	tests/test_threshold_sweep_cli.py`

### 068. `43d4404` - docs(gate-a): add Phase R re-review and briefs

- Full SHA: `43d4404df2e4e54a344752c44a4eb2c332070abd`
- Date: `2026-05-17T21:48:39+02:00`
- Author: `Akir Oussama`
- Shortstat: 2 files changed, 179 insertions(+)
- Body:

```text
Adds the two Gate A artefacts PLAYBOOK.md Gate A requires beyond the
code punch list.

CLAUDE_PHASE_R_REREVIEW_2026-05-17.md re-reviews the 2026-05-15 audit
against the post-reconciliation source: 10 of 13 M2 checklist items
verified CLOSED, 3 OPEN (two policy decisions + the manual label
audit). It found and recorded the C1 Gap-2 residual the preceding
fix(sweep) commit closes.

PHASE_R_DECISION_BRIEFS_2026-05-17.md frames the four section-4 policy
decisions (MSG long-horizon framing, H1 cluster metric unit, event
denominator standardization, postictal anchor) for Oussama + advisor
sign-off.

Refs: docs/CLAUDE_PHASE_R_AUDIT_2026-05-15.md
Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```
- Files changed:
  - `A	docs/CLAUDE_PHASE_R_REREVIEW_2026-05-17.md`
  - `A	docs/PHASE_R_DECISION_BRIEFS_2026-05-17.md`

### 069. `bc7077a` - docs(gate-a): add advisor recs on Phase R briefs

- Full SHA: `bc7077aa5cb31a4c58d4fb79f13cc1b0d7141158`
- Date: `2026-05-17T21:51:59+02:00`
- Author: `Akir Oussama`
- Shortstat: 1 file changed, 71 insertions(+)
- Body:

```text
An independent advisor reviewed the four Phase R policy decision
briefs (PHASE_R_DECISION_BRIEFS_2026-05-17.md). It confirms the
audit's position on briefs 2-4 with operational additions, and
diverges on brief 1: the MSG long-horizon framing is not "either
defensible" -- the coverage-limited presentation is required, and the
open decision is whether to also run a shorter, well-powered horizon
(advisor: yes).

Recorded as a separate companion file, not merged into the briefs:
the briefs stay the decision frame, the advisor recommendations are
one input, and Oussama's recorded sign-off is what closes the policy
items.

Refs: docs/PHASE_R_DECISION_BRIEFS_2026-05-17.md
Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```
- Files changed:
  - `A	docs/PHASE_R_DECISION_BRIEFS_ADVISOR_2026-05-17.md`

### 070. `2eb0baa` - chore(scripts): add processed-data integrity check

- Full SHA: `2eb0baa44557e0bca1f4be9df54de4cdc3e63d33`
- Date: `2026-05-17T22:17:09+02:00`
- Author: `Akir Oussama`
- Shortstat: 1 file changed, 77 insertions(+)
- Body:

```text
B4 of the bounded autonomous block (Phase C de-risk). Adds a
read-only verification that loads every processed parquet under
data/processed/{msg,seizeit2} and checks row/col counts, NaN per
column, timestamp-ordering sanity (seizure/recording/window), and
label/exclusion distributions. Exits non-zero on a read failure or
a timestamp-ordering violation; NaN in nullable metadata columns is
reported, not flagged.

Run against the current server-side processed data: exit 0, no
anomalies -- MSG 768 events / 49577 windows / 84% excluded (the
coverage-limited long-horizon reality), SeizeIT2 883 events /
1385203 windows / 125 patients. Phase C's split freeze will not
inherit corrupt processed data.

Verified-By: uv run --extra dev ruff check scripts/verify_processed_data.py (clean); executed against server data/processed/{msg,seizeit2} -- exit 0, 0 anomalies
Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```
- Files changed:
  - `A	scripts/verify_processed_data.py`

### 071. `f198820` - chore(phase-c): record exploratory pre-audit splits

- Full SHA: `f1988209555e14a4a0a1c996f5e9f4e43b94c7e8`
- Date: `2026-05-17T22:34:11+02:00`
- Author: `Akir Oussama`
- Shortstat: 1 file changed, 60 insertions(+)
- Body:

```text
Exploratory Phase C split run on label tables that have NOT passed
the Phase B manual audit. Re-runnable; no scientific commitment; the
freeze, pre-registration and Phase D baselines stay gated.

make_splits.py, 2 strategies x 2 datasets, default fractions
0.70/0.10/0.20 (provisional). MSG temporal + patient-wise: OK, leakage
audits clean. SeizeIT2 patient-wise: OK, clean.

SeizeIT2 temporal split REFUSED by the H3 guard: OpenNeuro ds005873 is
de-identified with every recording anchored to epoch 2000-01-01, so
equal-duration recordings collide on [start,end] and cross-recording
temporal order is unrecoverable. SeizeIT2 supports patient-wise only
with current tooling; MSG supports both. A run-index-ordered temporal
proxy for SeizeIT2 is an open methods question for the real Phase C.

Refs: reports/phase_c_exploratory_splits_2026-05-17.md
Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```
- Files changed:
  - `A	reports/phase_c_exploratory_splits_2026-05-17.md`

### 072. `0d7f70f` - audit(labels): add parser-fidelity check (passes)

- Full SHA: `0d7f70ff3fa8a02b12192c512780dbe1422be18a`
- Date: `2026-05-18T02:49:23+02:00`
- Author: `Akir Oussama`
- Shortstat: 2 files changed, 259 insertions(+)
- Body:

```text
Phase B is a manual clinical label audit of the MSG and SeizeIT2
review sheets. That audit is only meaningful if the tables it reviews
faithfully reflect the raw annotations: a silently-corrupting parser
would invalidate the human review before it starts. This commit adds
an automated parser-fidelity check that rules that risk out.

scripts/audit_label_fidelity.py re-reads the raw annotations
independently of the repo parsers and compares them against
data/processed/{msg,seizeit2}/events.parquet:
- MSG: (patient_id, unix_second) set equality, 768 == 768, identical
  sets (catches a swap, not only a net count change).
- SeizeIT2: seizure-row count per patient across all 125 subjects,
  883 == 883, matched overall and per patient.

The script was reviewed twice by an independent code-reviewer agent
before it was run. The first pass found 6 correctness bugs (a
timezone-incorrect Unix reconstruction; a false-OK blind spot on the
MSG CSV branch; 4 parser-discovery divergences); all 6 were fixed and
the second pass confirmed each fix. The advisor tool was unavailable;
the code-reviewer agent was the independent-review substitute.

This is parser fidelity only, NOT the Phase B clinical audit, which
remains Oussama's. Limits and gate status are in the report.

Refs:
- reports/label_fidelity_audit_2026-05-18.md (full result + limits)
- docs/HUMAN_LABEL_AUDIT_PROTOCOL.md (the Phase B runbook)
- scripts/verify_processed_data.py (sibling schema/ordering check)

Verified-By: uv run python scripts/audit_label_fidelity.py (exit 0,
0 findings, run on the Hetzner data-processing server)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```
- Files changed:
  - `A	reports/label_fidelity_audit_2026-05-18.md`
  - `A	scripts/audit_label_fidelity.py`

### 073. `f9593e6` - docs(handoff): add Codex work order 2026-05-18

- Full SHA: `f9593e6aa4cd29a2a94f8d215da0b063873fe351`
- Date: `2026-05-18T07:17:26+02:00`
- Author: `Akir Oussama`
- Shortstat: 1 file changed, 205 insertions(+)
- Body:

```text
Oussama asked to delegate the remaining EpiTwin work to Codex.
This file is that delegation work order. It is deliberately short:
docs/CLAUDE_PHASE_R_REREVIEW_2026-05-17.md verified the Phase A
code punch list is fully closed (10/13 M2 items; the 3 open are
2 policy decisions + the manual audit, none of them code), so
there is no code backlog to hand over. The order carries the two
genuine, non-redundant, non-gated tasks that actually exist:

- Task 1: extend scripts/audit_label_fidelity.py to verify
  SeizeIT2 at onset granularity (currently count-level only --
  Limit #2 of reports/label_fidelity_audit_2026-05-18.md).
- Task 2: SOTA citation integrity audit of SOTA_REVIEW_2026.md,
  starting with the phantom arXiv:2604.18297 the playbook flags.

Section 2 is a hard boundary: the Phase B clinical verdicts, the
4 Gate A policy decisions, the Phase C freeze / Zenodo, and any
pre-Gate-C baseline run are off-limits to every AI agent. Codex
has the same limits as Claude there; producing output would be
fabrication, not delegation.

Grounded by verification, not assumption: the phantom arXiv was
confirmed still present (SOTA_REVIEW_2026.md:37); the playbook's
`tibia` typo was confirmed already fixed (no occurrence in
README.md or HUMAN_INTERVENTION_CHECKPOINTS.md) and is therefore
NOT a task.

Refs:
- PLAYBOOK.md §5/§7/§8/§9 (critical path, roles, kaizen, mistakes)
- docs/CLAUDE_PHASE_R_REREVIEW_2026-05-17.md (Phase A code closure)
- reports/label_fidelity_audit_2026-05-18.md (Task 1 origin)

Verified-By: grep -in 'tibia' (0 hits in README.md and
HUMAN_INTERVENTION_CHECKPOINTS.md) ; grep -n '2604.18297' (present
at docs/SOTA_REVIEW_2026.md:37)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```
- Files changed:
  - `A	docs/CLAUDE_TO_CODEX_WORK_ORDER_2026-05-18.md`

### 074. `a0fa264` - audit(labels): add SeizeIT2 onset fidelity check

- Full SHA: `a0fa2643d0250ec1f125f880f2f7666ac00fea53`
- Date: `2026-05-18T07:49:52+02:00`
- Author: `Oussama Akir`
- Shortstat: 3 files changed, 455 insertions(+), 30 deletions(-)
- Body:

```text
Extend the parser-fidelity audit with an onset-level SeizeIT2 comparison keyed by patient, recording, source event file, and raw BIDS onset. Keep the existing count-level check, add fail-closed missing-input handling, and add CLI path overrides for mounted data layouts.

Before: SeizeIT2 only checked counts, so a count-preserving timestamp shift could pass. The local default checkout has no data/ tree and now exits 1 with explicit missing-parquet findings instead of an unhandled traceback.

After: the mounted sub-125 subset reports raw seizures 2 / events.parquet 2 and raw onset keys 2 / processed onset keys 2 with exit 0. Full 125-subject / 883-seizure data was not mounted here, so this remains a remediation candidate pending full-data re-review.

Independent-Review: explorer review found one false-OK missing-raw-root path; fixed with a regression test.

Verified-By: uv run --extra dev ruff check scripts/audit_label_fidelity.py tests/test_label_fidelity_audit.py

Verified-By: uv run --extra dev pytest tests/test_label_fidelity_audit.py

Verified-By: uv run --extra dev python scripts/audit_label_fidelity.py --dataset seizeit2 --repo-root /mnt/c/doctorat/iot/epitwin-open --seizeit2-raw-root /mnt/c/doctorat/iot/epitwin-open/datasets

Falsifiability: test_seizeit2_onset_audit_flags_count_preserving_timestamp_shift

Advisor-checkpoint: Full SeizeIT2 125-subject / 883-seizure onset audit still requires the full raw and processed data mount; no Gate B clinical-label verdict or gate closure is made.
```
- Files changed:
  - `M	reports/label_fidelity_audit_2026-05-18.md`
  - `M	scripts/audit_label_fidelity.py`
  - `A	tests/test_label_fidelity_audit.py`

### 075. `acc1ad1` - docs(sota): verify citation integrity

- Full SHA: `acc1ad15031deefce69f6329278a9844153bc4dd`
- Date: `2026-05-18T07:50:03+02:00`
- Author: `Oussama Akir`
- Shortstat: 2 files changed, 68 insertions(+), 14 deletions(-)
- Body:

```text
Mark every external source in docs/SOTA_REVIEW_2026.md with an explicit 2026-05-18 verification status and add a separate citation-integrity audit note recording each resolution method and verdict.

Before: arXiv:2604.18297 was flagged in the work order as a suspected phantom citation, and the SOTA source list did not carry per-citation verification status.

After: all 12 listed sources were resolved and title/topic matched against their attached claims. arXiv:2604.18297 resolves to the circadian wearable single-patient case study and was not replaced.

Verified-By: browser resolution of publisher/arXiv/Zenodo/GitHub/ICLR/PSB pages plus title-and-claim matching on 2026-05-18

Falsifiability: docs/SOTA_CITATION_AUDIT_2026-05-18.md records each checked URL/DOI and verdict; any future unresolved or misattributed source should be marked UNVERIFIED rather than substituted.

Advisor-checkpoint: Citation verification only; no Gate A policy choice, clinical-label verdict, split freeze, Zenodo upload, or baseline-performance claim.
```
- Files changed:
  - `A	docs/SOTA_CITATION_AUDIT_2026-05-18.md`
  - `M	docs/SOTA_REVIEW_2026.md`

### 076. `5f6c704` - docs(closure): close Codex work order Tasks 1-2

- Full SHA: `5f6c70447b66ac099159666fcbd3a417e21c540c`
- Date: `2026-05-18T23:44:50+02:00`
- Author: `Akir Oussama`
- Shortstat: 2 files changed, 145 insertions(+), 8 deletions(-)
- Body:

```text
Claude Code closure re-review of Codex's 2026-05-18 work order
(commits a0fa264 Task 1, acc1ad1 Task 2), per PLAYBOOK.md §8 --
"closed" is reserved for Claude Code's dated re-review.

Task 2 (SOTA citation integrity) is CLOSED. The work order
required the disputed citation be checked independently, not
rubber-stamped: Claude Code fetched arxiv.org/abs/2604.18297
directly and confirmed a real paper ("Circadian Phase Locking
of Epilepsy Seizures in Wearable Data", Ewart-James et al.,
Bristol, submitted 2026-04-20), correctly attributed. Codex's
verdict was right; PLAYBOOK.md §G calling it "the phantom" is
stale and should be updated by Oussama.

Task 1 (SeizeIT2 onset-level fidelity): the onset finding is
VERIFIED on the full 125-subject / 883-seizure data. Codex
could not run it (no full data mounted); Claude Code ran
scripts/audit_label_fidelity.py on the Hetzner server -- raw
onset multiset matches events.parquet (883 == 883) and
seizure_start - recording_start matches every raw onset.

Re-review found two P2 robustness defects in the audit script
(R1 cross-OS path separator; R2 multiset check skipped when
recordings.parquet is absent). Neither affected the verified
run. Per PLAYBOOK.md §7 these are implementation -- handed to
Codex as a remediation candidate with per-finding handoff
lines in the closure doc.

reports/label_fidelity_audit_2026-05-18.md: the two stale
"run pending" statements are corrected to point at this closure.

Refs:
- a0fa264 (Codex Task 1), acc1ad1 (Codex Task 2)
- docs/CLAUDE_TO_CODEX_WORK_ORDER_2026-05-18.md (the work order)
- docs/CLAUDE_CODEX_WORKORDER_REREVIEW_2026-05-18.md (this closure)

Verified-By: uv run python scripts/audit_label_fidelity.py on
the Hetzner server (SeizeIT2 883 onset keys match, exit 0);
WebFetch https://arxiv.org/abs/2604.18297 (real paper);
uv run --extra dev pytest tests/test_label_fidelity_audit.py
(5 passed)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```
- Files changed:
  - `A	docs/CLAUDE_CODEX_WORKORDER_REREVIEW_2026-05-18.md`
  - `M	reports/label_fidelity_audit_2026-05-18.md`

### 077. `a3aa98e` - fix(audit): harden SeizeIT2 onset fidelity checks

- Full SHA: `a3aa98edcc14ca8b52d934d7e0abd0b513b27eef`
- Date: `2026-05-19T00:38:25+02:00`
- Author: `Oussama Akir`
- Shortstat: 2 files changed, 116 insertions(+), 51 deletions(-)
- Body:

```text
Remediation candidate for R1/R2 from docs/CLAUDE_CODEX_WORKORDER_REREVIEW_2026-05-18.md.

R1 before: event_source_file values written with Windows backslashes could fail the raw/parquet onset-key comparison even when the source row was identical. After: raw source paths are emitted with as_posix(), parquet source paths are normalized from backslash to forward slash, and the backslash-source fixture returns zero findings.

R2 before: when recordings.parquet was absent, the onset-key multiset comparison could be skipped together with the seizure_start-recording_start offset check. After: the patient/recording/source/onset multiset runs before the recordings guard; missing recordings only blocks the offset sub-check and still flags dropped or added onsets.

Verified-By: uv run --extra dev pytest tests/test_label_fidelity_audit.py -q (7 passed)

Verified-By: uv run --extra dev ruff check scripts/audit_label_fidelity.py tests/test_label_fidelity_audit.py

Falsifiability: test_seizeit2_onset_audit_accepts_backslash_source_file

Falsifiability: test_seizeit2_onset_audit_checks_multiset_without_recordings

Advisor-checkpoint: Claude Code dated re-review still required to close R1/R2; no clinical label verdicts or gated baseline numbers changed.
```
- Files changed:
  - `M	scripts/audit_label_fidelity.py`
  - `M	tests/test_label_fidelity_audit.py`

### 078. `e053026` - chore(scripts): add EpiTwin-SSL CPU benchmark

- Full SHA: `e053026e5472df3678acae70d25b320041e8d863`
- Date: `2026-05-19T01:17:22+02:00`
- Author: `Akir Oussama`
- Shortstat: 1 file changed, 114 insertions(+)
- Body:

```text
Phase E (deep models) is several gates out, but it is useful now to
know whether EpiTwin-SSL training can run on a PC rather than an
A100. This script answers that empirically: it times the real
EpiTwinSSL forward + backward + optimizer step on synthetic batches
and extrapolates to the 1.385M SeizeIT2 processed windows.

Run on the Hetzner 16-core CPU server (no GPU), torch 2.12+cu130:
- the model is small -- 113k (TCN h64) to 514k (GRU h128) params;
- TCN h128: ~22 min per epoch over 1.385M windows (two runs: 21.4
  and 22.9 min -- the box is shared, timing varies);
- a ~30-epoch SSL pretrain: ~11 h of CPU compute;
- the Stage D ablation sweep (~7 variants): ~3 days of CPU compute.

So the GPU part is feasible without an A100: an overnight job for a
single run on this CPU, a long weekend for the full sweep. The
script measures synthetic-batch compute only -- real training adds
data-loading I/O -- and the epoch counts and model sizes are stated
assumptions, not the (still unpinned) Stage C config.

Refs:
- docs/A100_RUNBOOK.md (the Phase E training procedure)
- scripts/train_epitwin_ssl.py (the synthetic smoke-train it reuses)

Verified-By: uv run --extra dev ruff check (clean); uv run --extra
torch python scripts/bench_epitwin_ssl_cpu.py on the Hetzner server
(3 configs timed, extrapolation printed, exit 0)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```
- Files changed:
  - `A	scripts/bench_epitwin_ssl_cpu.py`

### 079. `b033296` - docs(closure): close R1/R2 audit hardening

- Full SHA: `b0332967c98fb375348ef92f312a3508f49046a8`
- Date: `2026-05-19T01:30:22+02:00`
- Author: `Akir Oussama`
- Shortstat: 1 file changed, 40 insertions(+), 3 deletions(-)
- Body:

```text
Codex delivered the R1/R2 remediation candidate (commit a3aa98e),
the two robustness defects this re-review doc handed back on
2026-05-18. Claude Code closure re-review:

- R1 (cross-OS path separator): raw keys use as_posix(), parquet
  event_source_file normalised backslash to slash. CLOSED.
- R2 (multiset check skipped when recordings.parquet absent): the
  onset-key multiset now runs before the recordings guard; only
  the offset sub-check stays gated. CLOSED.

An independent code-reviewer subagent confirmed both fixes correct
with no new defect, and both new falsification tests discriminating.
With R1/R2 closed, scripts/audit_label_fidelity.py has no open
findings and Codex's 2026-05-18 work order is fully closed.

Refs:
- a3aa98e (Codex R1/R2 remediation candidate)
- docs/CLAUDE_CODEX_WORKORDER_REREVIEW_2026-05-18.md (this closure)

Verified-By: uv run --extra dev pytest
tests/test_label_fidelity_audit.py (7 passed) ; uv run python
scripts/audit_label_fidelity.py on Hetzner (SeizeIT2 883/883 onset
multiset match, MSG 768/768, exit 0)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```
- Files changed:
  - `M	docs/CLAUDE_CODEX_WORKORDER_REREVIEW_2026-05-18.md`

### 080. `f9e123f` - docs(gate-a): record the 4 policy sign-offs

- Full SHA: `f9e123f369fd525933ed2fbf1ab8ed3d3ecd442a`
- Date: `2026-05-19T05:40:54+02:00`
- Author: `Akir Oussama`
- Shortstat: 2 files changed, 109 insertions(+), 6 deletions(-)
- Body:

```text
Oussama signed off the four Gate A policy decisions from the Phase R
audit. Recorded in docs/GATE_A_DECISIONS_2026-05-19.md; PLAYBOOK.md
updated (the section 5 Phase C MSG-horizon item flipped DECISION
REQUIRED -> RECORDED, plus a section 12 changelog entry).

The four decisions, all following the advisor's recommendation:
1. MSG long-horizon: keep SPH60/SOP1440 as a coverage-limited
   demonstration AND also run SOP 240 min (4 h) as a powered
   comparison.
2. H1 cluster metric: cluster-level primary, seizure-level secondary;
   cluster_gap_minutes pre-registered at 240.
3. Event denominator: report both, coverable-matched primary, one
   shared coverability function.
4. Postictal anchor: onset + a fixed 120-minute offset (not the
   imputed seizure_end). 120 min is anchored to the adult EEG
   return-to-baseline time (mean ~120 min) and cited to StatPearls
   NBK526004 and Pottkaemper et al. 2020 (Epilepsia, DOI
   10.1111/epi.16519) -- both verified real by direct fetch.

This closes the policy half of Gate A. The remaining Gate A blocker
is the Phase B manual label audit (Oussama, not delegable).

Refs:
- docs/PHASE_R_DECISION_BRIEFS_2026-05-17.md (the decision frame)
- docs/PHASE_R_DECISION_BRIEFS_ADVISOR_2026-05-17.md (advisor input)
- docs/GATE_A_DECISIONS_2026-05-19.md (this sign-off record)

Verified-By: WebFetch of ncbi.nlm.nih.gov/books/NBK526004 and
pmc.ncbi.nlm.nih.gov/articles/PMC7317965 -- both citations confirmed
real and content-matched (2026-05-19)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```
- Files changed:
  - `M	PLAYBOOK.md`
  - `A	docs/GATE_A_DECISIONS_2026-05-19.md`

### 081. `831fee6` - fix(demo): make synthetic windows right-censoring ready

- Full SHA: `831fee613eab5bf35c1e77ade00506dd1ab08892`
- Date: `2026-05-20T05:00:22+02:00`
- Author: `Oussama Akir`
- Shortstat: 2 files changed, 19 insertions(+)
- Body:

```text
Stage-A Hetzner run exposed that scripts/run_synthetic_demo.py still used make_synthetic_seizeit2_tables() without recording_end, while label_forecast_windows now correctly defaults require_recording_end=True.

Before: uv run python scripts/run_synthetic_demo.py failed with 'windows_df must contain recording_end for right-censoring'.

After: the synthetic helper emits recording_start/recording_end on every window; the demo runs without bypassing the labeler guard.

Verified-By: uv run --extra dev pytest tests/test_sph_sop_labeling.py tests/test_alarm_metrics.py tests/test_event_metrics.py tests/test_calibration.py -q (14 passed)

Verified-By: uv run --extra dev ruff check src/datasets/seizeit2_loader.py tests/test_sph_sop_labeling.py scripts/run_synthetic_demo.py

Verified-By: uv run python scripts/run_synthetic_demo.py

Falsifiability: test_synthetic_seizeit2_tables_are_right_censoring_ready

Advisor-checkpoint: This changes only synthetic/demo fixtures; no clinical label verdicts, split freeze, or model-performance claim.
```
- Files changed:
  - `M	src/datasets/seizeit2_loader.py`
  - `M	tests/test_sph_sop_labeling.py`

### 082. `d506900` - docs(training): record Hetzner clinical readiness gate

- Full SHA: `d5069006bf91b219b8f7fadfec15abb273b61c04`
- Date: `2026-05-20T05:18:22+02:00`
- Author: `Oussama Akir`
- Shortstat: 1 file changed, 121 insertions(+)
- Body:

```text
The Hetzner CPU path can run Stage A and synthetic proxy training, but the sampled MSG and SeizeIT2 human label-audit sheets are still blank in every blocking review column.

Before: a CPU proxy run could be mistaken for a clinical result. After: the readiness report records the exact Gate B failures and the re-check commands that must pass before any real clinical training/result claim.

Verified-By: uv run --extra dev pytest tests/test_sph_sop_labeling.py tests/test_label_audit.py -q (10 passed)

Verified-By: uv run --extra dev ruff check src/datasets/seizeit2_loader.py tests/test_sph_sop_labeling.py

Falsifiability: scripts/check_label_audit_review.py fails MSG and SeizeIT2 sampled sheets until human decision columns are filled

Advisor-checkpoint: This is a fail-closed readiness report; no clinical result, split freeze, or model-performance claim is made.
```
- Files changed:
  - `A	reports/hetzner_clinical_training_readiness_2026-05-20.md`

### 083. `23ec05a` - docs(training): record human-attested Gate B pass

- Full SHA: `23ec05a28b3548e5b6c3b5b29510a7026f3b8f9e`
- Date: `2026-05-20T11:09:21+02:00`
- Author: `Oussama Akir`
- Shortstat: 1 file changed, 36 insertions(+), 1 deletion(-)
- Body:

```text
Verified-By: Hetzner check_label_audit_review.py passed for sampled MSG and SeizeIT2 sheets

Falsifiability: gate_b_msg_review_check_20260520_pass.csv and gate_b_seizeit2_review_check_20260520_pass.csv

Advisor-checkpoint: Human attestation recorded; Codex did not perform clinical review.
```
- Files changed:
  - `M	reports/hetzner_clinical_training_readiness_2026-05-20.md`

### 084. `36433ac` - feat(training): add real MSG tabular CPU baseline

- Full SHA: `36433acdb12ebd3078a4f5795b03558ac4b0fc6d`
- Date: `2026-05-20T11:15:15+02:00`
- Author: `Oussama Akir`
- Shortstat: 2 files changed, 296 insertions(+)
- Body:

```text
Trains on real MSG HR/ACC feature summaries with train-only preprocessing, validation thresholding, and leakage-column exclusion.

Verified-By: uv run pytest tests/test_msg_tabular_training.py

Verified-By: uv run ruff check scripts/train_msg_tabular_baseline.py tests/test_msg_tabular_training.py

Falsifiability: full pytest without torch extra fails during existing torch test collection.
```
- Files changed:
  - `A	scripts/train_msg_tabular_baseline.py`
  - `A	tests/test_msg_tabular_training.py`

### 085. `7568122` - fix(training): exclude censoring metadata from MSG tabular features

- Full SHA: `7568122af89c08db21659cf81838cadf21edf322`
- Date: `2026-05-20T11:25:13+02:00`
- Author: `Oussama Akir`
- Shortstat: 2 files changed, 8 insertions(+)
- Body:

```text
The real-data tabular baseline must not train on right-censoring flags or dataset metadata; it now defaults to physiological feature columns only.

Verified-By: uv run pytest tests/test_msg_tabular_training.py

Verified-By: uv run ruff check scripts/train_msg_tabular_baseline.py tests/test_msg_tabular_training.py
```
- Files changed:
  - `M	scripts/train_msg_tabular_baseline.py`
  - `M	tests/test_msg_tabular_training.py`

### 086. `35be2c1` - docs(results): record MSG patient-wise real-data baseline

- Full SHA: `35be2c149d3e9182ad7c816e6cdfcaf1d219896e`
- Date: `2026-05-20T11:31:44+02:00`
- Author: `Oussama Akir`
- Shortstat: 1 file changed, 142 insertions(+)
- Body:

```text
Records Hetzner CPU HR feature extraction, real MSG tabular training, patient-wise test metrics, comparison baselines, evidence files, and interpretation boundaries.

Verified-By: Hetzner report_patient_tabular_hr_test_clean/baseline_results.csv

Falsifiability: outputs/msg_clinical_baselines_20260520/msg_tabular_hr_patient_train_metadata_clean.json
```
- Files changed:
  - `A	reports/msg_patientwise_clinical_baseline_2026-05-20.md`

### 087. `307c55d` - Create logs-akiroussama-iot-edge-ai-seizure-detection-main-streamlit_app.py-2026-05-10T18_33_37.811Z.txt

- Full SHA: `307c55d32180a6d47c9c21b5572e5eca10c257f9`
- Date: `2026-05-20T12:38:18+02:00`
- Author: `Akir Oussama`
- Shortstat: 1 file changed, 269 insertions(+)
- Body: none
- Files changed:
  - `A	logs-akiroussama-iot-edge-ai-seizure-detection-main-streamlit_app.py-2026-05-10T18_33_37.811Z.txt`

### 088. `6e5c766` - docs(research): define SOTA leaderboard step 1

- Full SHA: `6e5c7666d0f7392bcbce8ab375ddbd0eec91c463`
- Date: `2026-05-20T12:32:09+02:00`
- Author: `Oussama Akir`
- Shortstat: 4 files changed, 319 insertions(+)
- Body:

```text
Add the Step 1 plan, validation criteria, SOTA source matrix, experiment backlog, and execution log for the incremental research program.

Base: origin/feature/epibench-forecast-v0.1@307c55d

Recovery: cherry-picked the original main-based Step 1 commit onto the active feature branch with no merge conflicts, then corrected branch/base metadata.

Verified-By: git diff --check

Verified-By: csv shape validation for SOTA sources and experiment backlog

Falsifiability: docs/research/2026-05-20_step1_sota_sources.csv

Stop-Rule: wait for Claude validation and merge before Step 2.
```
- Files changed:
  - `A	docs/research/2026-05-20_step1_execution_log.md`
  - `A	docs/research/2026-05-20_step1_experiment_backlog.csv`
  - `A	docs/research/2026-05-20_step1_sota_leaderboard_plan.md`
  - `A	docs/research/2026-05-20_step1_sota_sources.csv`

### 089. `9a0264f` - docs(results): re-frame MSG baseline as pre-freeze

- Full SHA: `9a0264fa8d2646668810a282fd1864e3bd5301ae`
- Date: `2026-05-20T13:05:30+02:00`
- Author: `Akir Oussama`
- Shortstat: 1 file changed, 37 insertions(+), 18 deletions(-)
- Body:

```text
reports/msg_patientwise_clinical_baseline_2026-05-20.md previously framed
the 27/31 / FAR 2.006 / TIW 0.1253 run as a "clinical-prototype benchmark
result" and declared "Gate C: MSG patient-wise leakage audit clean", which
is misleading: Gate C has four conditions (split policy documented,
frozen splits with git tag, leakage audit clean, Zenodo DOI
pre-registration) and only the leakage audit is currently green.

Per PLAYBOOK.md section 10 rule 1 ("No reported number before the
benchmark is frozen, Gate C") and section 3 consequence 1, the numbers
must be marked as exploratory and not citable as a benchmark result.

Framing-only changes; no numbers altered.

- Title and lead now state "exploratory pre-freeze" and cite the playbook
  rule explicitly.
- Gate B status: kept Oussama's 2026-05-20 sampled human attestation, and
  noted the audit log has no per-seizure observation notes (strengthening
  recommended before any pre-registration per the Claude Code review).
- Gate C status: corrected to "NOT passed" with the four conditions
  enumerated; only the leakage audit clean is verified.
- Interpretation Boundaries rewritten: "pre-freeze exploratory numbers,
  not a benchmark result"; explicitly cannot be cited externally until
  Gate C closes.
- Patient-Wise Test Results table heading suffixed "pre-freeze
  exploratory, not for citation".

Refs:
- PLAYBOOK.md section 10 rule 1, section 3 consequence 1, sections 5/6
  Gate C definition
- reports/hetzner_clinical_training_readiness_2026-05-20.md (Gate B
  attestation that this doc cross-references)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```
- Files changed:
  - `M	reports/msg_patientwise_clinical_baseline_2026-05-20.md`

### 090. `1cb0030` - docs(research): fix S7 canonical citation + S9 pre-Gate-C labelling

- Full SHA: `1cb00300fce11664fc5cd3bbc9d3905f49926882`
- Date: `2026-05-20T13:10:45+02:00`
- Author: `Akir Oussama`
- Shortstat: 2 files changed, 17 insertions(+), 12 deletions(-)
- Body:

```text
Per Claude Code review of PR #2:

S7 (SzCORE): the original URL pointed to a personal-website summary
(thorirmar.com), not the canonical citation. Replaced with the
Epilepsia DOI (10.1111/epi.18113, Dan et al. June 2025). Title
corrected to the full canonical title; year corrected from 2024 to
2025.

S9 (feature-branch MSG baseline): the row claimed the result as the
"first leaderboard row" without acknowledging that the underlying
numbers are pre-Gate-C. Per PLAYBOOK.md section 10 rule 1 ("No
reported number before the benchmark is frozen"), the row now labels
the result as pre-Gate-C exploratory and states explicitly it is not
a citable leaderboard entry until Gate C closes (frozen splits +
Zenodo DOI). Same qualifier added to the Baseline B subsection of the
plan markdown and to priority 1 of the experiment backlog.

No numbers altered; framing and citation fixes only.

Refs:
- PLAYBOOK.md section 10 rule 1, section 3 consequence 1
- reports/msg_patientwise_clinical_baseline_2026-05-20.md (re-framed)

Verified-By: WebFetch of https://thorirmar.com/publication/2025-epilepsia-szcore/
returned a personal-website summary; canonical Dan et al. 2025
Epilepsia article verified at DOI 10.1111/epi.18113

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```
- Files changed:
  - `M	docs/research/2026-05-20_step1_sota_leaderboard_plan.md`
  - `M	docs/research/2026-05-20_step1_sota_sources.csv`

### 091. `c0c9fb6` - Merge pull request #2 from akiroussama/codex/sota-leaderboard-step1

- Full SHA: `c0c9fb6af675d1d98f5eb3a3506321c6c69f6d28`
- Date: `2026-05-20T12:10:53+01:00`
- Author: `Akir Oussama`
- Shortstat: 4 files changed, 324 insertions(+)
- Body:

```text
[codex] Define SOTA leaderboard step 1 on feature branch
```
- Files changed: none reported

### 092. `729e329` - Merge pull request #1 from akiroussama/feature/epibench-forecast-v0.1

- Full SHA: `729e329b62befc6eea1d2ea5402d639b98a9c782`
- Date: `2026-05-20T12:15:19+01:00`
- Author: `Akir Oussama`
- Shortstat: 246 files changed, 21634 insertions(+), 10350 deletions(-)
- Body:

```text
[codex] Build EpiTwin-Open benchmark infrastructure
```
- Files changed: none reported

### 093. `249cd12` - chore(license): restore LICENSE removed by feature merge

- Full SHA: `249cd12b9fdf82262fc9502d144d95ceef6860a5`
- Date: `2026-05-20T13:18:23+02:00`
- Author: `Akir Oussama`
- Shortstat: 1 file changed, 21 insertions(+)
- Body:

```text
The feature->main merge (PR #1, commit 729e329) brought feature's
file structure to main; the old main's LICENSE file was therefore
absent from the merged HEAD. Restoring it from main's pre-merge
state (4b4d68e). No license terms changed; this is a recovery of
the file the merge removed.

The merge also removed other files from old main that are not on
the feature branch (streamlit_app.py, streamlit_demo_live.py,
notebooks/, web/, presentation/, requirements*.txt, vercel.json,
old results/). They remain recoverable from history
(git checkout 4b4d68e -- <path>) but their relevance to the new
EpiTwin-Open direction is a user decision and is therefore left
out of this recovery commit.

Refs:
- 4b4d68e (pre-merge main)
- 729e329 (PR #1 merge that removed LICENSE)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```
- Files changed:
  - `A	LICENSE`

### 094. `cf171b9` - docs(leaderboard): add unified schema contract

- Full SHA: `cf171b924f681c52a8ca0cad0a743bbd871dd0d4`
- Date: `2026-05-20T12:40:38+01:00`
- Author: `Akir Oussama`
- Shortstat: 1 file changed, 1 insertion(+)
- Body: none
- Files changed:
  - `A	schemas/leaderboard_template.csv`

### 095. `27ac535` - docs(leaderboard): add leaderboard column dictionary

- Full SHA: `27ac535991b1d7f81436233dc29f917ff006bb13`
- Date: `2026-05-20T12:41:05+01:00`
- Author: `Akir Oussama`
- Shortstat: 1 file changed, 58 insertions(+)
- Body: none
- Files changed:
  - `A	schemas/leaderboard_columns.csv`

### 096. `b7bc626` - test(leaderboard): guard schema column consistency

- Full SHA: `b7bc626cdc3d7fcd8358fab073312b6035e02624`
- Date: `2026-05-20T12:41:24+01:00`
- Author: `Akir Oussama`
- Shortstat: 1 file changed, 77 insertions(+)
- Body: none
- Files changed:
  - `A	tests/test_leaderboard_schema.py`

### 097. `b1b1d57` - docs(leaderboard): record task 2 execution trace

- Full SHA: `b1b1d57a027400ae583986c07d776d7124269fb3`
- Date: `2026-05-20T12:42:00+01:00`
- Author: `Akir Oussama`
- Shortstat: 1 file changed, 137 insertions(+)
- Body: none
- Files changed:
  - `A	docs/research/2026-05-20_task2_leaderboard_schema.md`

### 098. `3035e62` - docs(leaderboard): add leaderboard json schema

- Full SHA: `3035e6249bb1b5b1417ada9d60df44c1fa686c35`
- Date: `2026-05-20T12:43:12+01:00`
- Author: `Akir Oussama`
- Shortstat: 1 file changed, 344 insertions(+)
- Body: none
- Files changed:
  - `A	schemas/leaderboard_entry.schema.json`

### 099. `4236d83` - feat(leaderboard): add row generation runner

- Full SHA: `4236d8304720bd2b84726332814647e3e0874c22`
- Date: `2026-05-20T16:18:49+02:00`
- Author: `Oussama Akir`
- Shortstat: 3 files changed, 832 insertions(+)
- Body:

```text
Add a pre-Gate-C-safe CLI that converts predictions and events into leaderboard.v1 CSV, JSON, and Markdown outputs with denominator accounting, core forecast metrics, optional Brier Skill Score, and citation status fields.

Base: origin/codex/leaderboard-schema@3035e62

Verified-By: git diff --check

Verified-By: uv run --extra dev pytest tests/test_leaderboard_runner.py tests/test_leaderboard_schema.py

Verified-By: uv run --extra dev ruff check scripts/make_leaderboard_row.py tests/test_leaderboard_runner.py tests/test_leaderboard_schema.py

Gate-C: synthetic tests only; no new real-data benchmark numbers generated.
```
- Files changed:
  - `A	docs/research/2026-05-20_task3_leaderboard_runner.md`
  - `A	scripts/make_leaderboard_row.py`
  - `A	tests/test_leaderboard_runner.py`

### 100. `e798400` - Merge pull request #3 from akiroussama/codex/leaderboard-schema

- Full SHA: `e79840053a3736ce9f63d6e7caa3b2f64034be06`
- Date: `2026-05-20T15:25:22+01:00`
- Author: `Akir Oussama`
- Shortstat: 5 files changed, 617 insertions(+)
- Body:

```text
[codex] Add unified leaderboard schema
```
- Files changed: none reported

### 101. `6234b5c` - Merge pull request #5 from akiroussama/codex/leaderboard-runner

- Full SHA: `6234b5c5aeafdf78f6c96bc41cbcc1706de64b5d`
- Date: `2026-05-20T15:30:16+01:00`
- Author: `Akir Oussama`
- Shortstat: 3 files changed, 832 insertions(+)
- Body:

```text
[codex] Add leaderboard row generation runner (Task 3, retargeted to main)
```
- Files changed: none reported

### 102. `22f7908` - docs(handoff): Task 4 null models work order

- Full SHA: `22f7908559e1e9f24f4ec437968e0a1fe06cc528`
- Date: `2026-05-20T16:40:36+02:00`
- Author: `Akir Oussama`
- Shortstat: 1 file changed, 225 insertions(+)
- Body:

```text
Revises Codex's original Task 4 proposal after Claude Code review.
Codex's plan was sound on architecture and anti-leakage rules; six
refinements added before implementation, all integrity-discipline
related:

1. split_prevalence_prior promoted from optional to mandatory (BSS
   climatology baseline canonical for Q1 defense).
2. patient_prior fallback marked explicitly via null_model_variant
   output column (Phase R C3 lesson: no silent rule degeneracy).
3. Fallback threshold parameterized: --patient-min-events N (default
   3) with explicit documentation.
4. Output schema explicit: input columns pass through unchanged, new
   columns appended (so the Task 3 runner consumes the rows
   directly).
5. Tests added beyond structural: (h)/(i) fallback marker assertions
   and (j)/(k)/(l) null-model behavior sanity (Brier ~ p(1-p),
   BSS-against-self ~ 0).
6. Per-model seed derivation specified to avoid RNG coupling between
   models when multiple are run in one wrapper.

The doc also reiterates anti-patterns from the Task 1-3 review to
avoid: no silent failure, no silent fallback, behavior-sanity tests
required, no phantom citations.

Refs:
- docs/research/2026-05-20_step1_experiment_backlog.csv (Task 4 row)
- src/baselines/ (existing baseline patterns to mirror)
- scripts/make_leaderboard_row.py (Task 3 runner; consumes outputs)
- docs/CLAUDE_PHASE_R_AUDIT_2026-05-15.md (C3 silent-degeneracy
  lesson)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```
- Files changed:
  - `A	docs/CLAUDE_TO_CODEX_WORK_ORDER_TASK4_2026-05-20.md`

### 103. `9b4c1a3` - feat(baselines): add constrained forecast null models

- Full SHA: `9b4c1a3727c201ff624d681dc4cb67baa00dd0d9`
- Date: `2026-05-20T19:02:11+02:00`
- Author: `Oussama Akir`
- Shortstat: 5 files changed, 959 insertions(+)
- Body:

```text
Base: origin/main@22f7908

Work-Order: docs/CLAUDE_TO_CODEX_WORK_ORDER_TASK4_2026-05-20.md

Implements four engineering-only null forecasting baselines: split_prevalence_prior, rate_matched_random, patient_prior with explicit population fallback markers, and cycle_preserving_random hour-of-day.

No real-data run; synthetic tests only; pre-Gate-C safe.

Verified-By: git diff --check

Verified-By: uv run --extra dev pytest tests/test_forecast_nulls.py (18 passed)

Verified-By: uv run --extra dev ruff check src/baselines/__init__.py src/baselines/forecast_nulls.py scripts/run_null_baseline.py tests/test_forecast_nulls.py

Verified-By: uv run --extra dev --extra torch pytest (154 passed)
```
- Files changed:
  - `A	docs/research/2026-05-20_task4_forecast_null_models.md`
  - `A	scripts/run_null_baseline.py`
  - `M	src/baselines/__init__.py`
  - `A	src/baselines/forecast_nulls.py`
  - `A	tests/test_forecast_nulls.py`

### 104. `7b08904` - Merge pull request #6 from akiroussama/codex/forecast-null-models

- Full SHA: `7b0890463f21c9c94d8793ce7ca41eeae3b93e10`
- Date: `2026-05-20T18:23:12+01:00`
- Author: `Akir Oussama`
- Shortstat: 5 files changed, 959 insertions(+)
- Body:

```text
[codex] Add constrained forecast null models
```
- Files changed: none reported

### 105. `953275d` - Create 2026-05-20_q1_publishable_task_roadmap.md

- Full SHA: `953275d955099067de6d867d730db8c8cfa1d7f4`
- Date: `2026-05-20T19:25:26+02:00`
- Author: `Akir Oussama`
- Shortstat: 1 file changed, 558 insertions(+)
- Body: none
- Files changed:
  - `A	docs/research/2026-05-20_q1_publishable_task_roadmap.md`

### 106. `2f89a16` - docs(research): Claude complementary Q1 research roadmap

- Full SHA: `2f89a163495ee0d8fa92ee23b8153c86911977e4`
- Date: `2026-05-20T19:32:52+02:00`
- Author: `Akir Oussama`
- Shortstat: 1 file changed, 342 insertions(+)
- Body:

```text
Companion to Codex's docs/research/2026-05-20_q1_publishable_task_roadmap.md.
Where Codex's plan converges on a single benchmark-methodology paper, this
doc proposes four complementary paper directions building on the same
infrastructure but addressing different scientific questions.

Directions:
- A. Mechanism (sparse autoencoders, causal discovery, counterfactuals) —
  opens the wearable forecasting black box.
- B. Personalization (test-time adaptation, conformal prediction, N=1
  longitudinal deep dive) — per-patient risk with formal guarantees.
- C. AI-assisted clinical workflow as a contribution itself (W1 documents
  the project's own human+AI cycle as Karpathy-style autoresearch; W2
  active labeling unblocks Phase B and yields a methodology paper; W3
  clinical LLM reasoning interface).
- D. Privacy and federation (diffusion-based synthetic patient data,
  federated benchmark protocol) — scaling without raw-data sharing.

Each direction is anchored in research areas with substantial activity in
the last 12-24 months (some in the last 3 months), explicitly flagged as
DIRECTIONS not phantom citations per the playbook §G rule.

The single highest-leverage additional task right now is W2 (active
labeling): it solves the project's current human-gated bottleneck
(Phase B) AND yields an independent methodology paper.

Refs:
- docs/research/2026-05-20_q1_publishable_task_roadmap.md (Codex's
  roadmap that this doc complements)
- docs/research/2026-05-20_step1_experiment_backlog.csv (Task 1-9 backlog)
- PLAYBOOK.md §G (phantom-citation rule applied to all references here)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```
- Files changed:
  - `A	docs/research/2026-05-20_claude_complementary_research_roadmap.md`

### 107. `b942c78` - docs(research): consolidated scoring of all 27 proposed tasks

- Full SHA: `b942c7823fd7a6e6f66516aedcae0df435120e0b`
- Date: `2026-05-20T23:42:02+02:00`
- Author: `Akir Oussama`
- Shortstat: 1 file changed, 216 insertions(+)
- Body:

```text
Multi-criteria scoring (out of 100) of every task in both research
roadmaps:
- 16 from Codex's q1_publishable_task_roadmap (Tasks 5-20)
- 11 from Claude's complementary research roadmap (M1-M3, P1-P3,
  W1-W3, F1-F2)

Rubric weighted per the user's emphasis on "extension not pivot":
Integration 25 + Impact 20 + Novelty 15 + Publishability 15 +
Citations 15 + Trends 10 = 100.

Top 5 by score:
1. Task 8 Forecastability Atlas (90) - blocked on Tasks 5+6
2. W1 AI-assisted workflow doc (89) - unblocked
3. P2 Conformal prediction (85) - unblocked
4. W2 Active labeling for audit (83) - unblocked
5. M1 Sparse autoencoders (82) - blocked on Task 14

Top 3 to do RIGHT NOW (unblocked + score >= 80): W1, P2, W2.

Includes full ranked table, path-dependence map, honorable
mentions (high-score blocked tasks), and explicit caveats on the
scoring methodology.

Refs:
- docs/research/2026-05-20_q1_publishable_task_roadmap.md (Codex)
- docs/research/2026-05-20_claude_complementary_research_roadmap.md
  (Claude)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```
- Files changed:
  - `A	docs/research/2026-05-20_consolidated_task_scoring.md`

### 108. `873e299` - feat(reports): add calibration bss reports (#7)

- Full SHA: `873e299a668fd5d33ec71507d85d3612ae80da03`
- Date: `2026-05-20T22:52:20+01:00`
- Author: `Akir Oussama`
- Shortstat: 7 files changed, 918 insertions(+), 1 deletion(-)
- Body:

```text
No real-data run; synthetic tests only; pre-Gate-C safe.

Verified-By: git diff --check
Verified-By: uv run --extra dev ruff check src/metrics/calibration.py src/metrics/__init__.py src/reports/__init__.py src/reports/calibration_skill.py scripts/make_calibration_report.py tests/test_calibration_skill_report.py
Verified-By: uv run --extra dev pytest tests/test_calibration_skill_report.py tests/test_calibration.py tests/test_leaderboard_runner.py tests/test_forecast_nulls.py (31 passed)
Verified-By: uv run --extra dev --extra torch pytest (161 passed)
```
- Files changed:
  - `A	docs/research/2026-05-20_task5_calibration_bss.md`
  - `A	scripts/make_calibration_report.py`
  - `M	src/metrics/__init__.py`
  - `M	src/metrics/calibration.py`
  - `M	src/reports/__init__.py`
  - `A	src/reports/calibration_skill.py`
  - `A	tests/test_calibration_skill_report.py`

### 109. `3320e6d` - docs(research): add fused task scoring challenge (#8)

- Full SHA: `3320e6de2b156b7c73c196dcd59eaff97cbe9f3e`
- Date: `2026-05-20T22:57:22+01:00`
- Author: `Akir Oussama`
- Shortstat: 1 file changed, 245 insertions(+)
- Body:

```text
Adds Codex counter-scores to Claude's 27-task ranking, computes 50/50 fused scores, and recommends the post-Task-5 execution sequence.

Verified-By: git diff --check
```
- Files changed:
  - `A	docs/research/2026-05-20_fused_task_scoring_codex_challenge.md`

### 110. `67108be` - feat(artifacts): add gate c registry guardrails (#9)

- Full SHA: `67108bed2f389149037fee0ae3c90a9d8ad4788a`
- Date: `2026-05-20T23:23:47+01:00`
- Author: `Akir Oussama`
- Shortstat: 8 files changed, 933 insertions(+)
- Body:

```text
No real-data freeze; synthetic tests only; Gate C remains human-gated.

Verified-By: python -m json.tool schemas/gate_c_registry.schema.json >/dev/null
Verified-By: git diff --check
Verified-By: uv run --extra dev ruff check src/artifacts/__init__.py src/artifacts/registry.py scripts/make_gate_c_registry.py scripts/verify_gate_c_registry.py scripts/make_leaderboard_row.py tests/test_gate_c_registry.py tests/test_leaderboard_runner.py
Verified-By: uv run --extra dev pytest tests/test_gate_c_registry.py tests/test_leaderboard_runner.py tests/test_leaderboard_schema.py (12 passed)
Verified-By: uv run --extra dev --extra torch pytest (165 passed)
```
- Files changed:
  - `A	docs/research/2026-05-21_task6_gate_c_registry.md`
  - `A	schemas/gate_c_registry.schema.json`
  - `A	scripts/make_gate_c_registry.py`
  - `M	scripts/make_leaderboard_row.py`
  - `A	scripts/verify_gate_c_registry.py`
  - `A	src/artifacts/__init__.py`
  - `A	src/artifacts/registry.py`
  - `A	tests/test_gate_c_registry.py`

### 111. `dcc5a0e` - feat(audit): add active label review selection (#10)

- Full SHA: `dcc5a0e8e3460d765a4fd79ceae312e9075848e2`
- Date: `2026-05-21T10:29:52+01:00`
- Author: `Akir Oussama`
- Shortstat: 5 files changed, 859 insertions(+)
- Body:

```text
Add W2 active audit target selection for Phase B clinical review prioritization.

Includes active acquisition scoring, CLI output, fail-closed prediction alignment checks, synthetic behavior tests, and a research trace. Validated with ruff and full pytest.
```
- Files changed:
  - `A	docs/research/2026-05-21_w2_active_audit_selection.md`
  - `A	scripts/select_audit_targets.py`
  - `A	src/active/__init__.py`
  - `A	src/active/audit_selection.py`
  - `A	tests/test_active_audit_selection.py`

### 112. `352d66a` - feat(calibration): add conformal risk intervals (#11)

- Full SHA: `352d66a90e1fafd45135e3eb9525f4342fc248cb`
- Date: `2026-05-21T10:36:17+01:00`
- Author: `Akir Oussama`
- Shortstat: 5 files changed, 768 insertions(+)
- Body:

```text
Add split-conformal risk interval utilities and a CLI report layer.

Supports global and patient-calibrated radii, explicit global fallback markers, synthetic coverage tests, and pre-Gate-C non-citable report guardrails. Validated with ruff and full pytest.
```
- Files changed:
  - `A	docs/research/2026-05-21_p2_conformal_risk_intervals.md`
  - `A	scripts/run_conformal_calibration.py`
  - `M	src/calibration/__init__.py`
  - `A	src/calibration/conformal.py`
  - `A	tests/test_conformal_prediction.py`

### 113. `a34e545` - feat(reports): add forecastability atlas (#12)

- Full SHA: `a34e545b1fe58a5c8dfd8ec33995705dfc8a8907`
- Date: `2026-05-21T10:43:50+01:00`
- Author: `Akir Oussama`
- Shortstat: 5 files changed, 773 insertions(+)
- Body:

```text
Add a forecastability atlas synthesis layer over leaderboard/calibration artifacts.

Classifies forecastability above null, null-overlap, underpowered, and pre-Gate-C non-citable rows; attaches reliability slope; emits CLI CSV/Markdown outputs; and validates with synthetic tests plus full pytest.
```
- Files changed:
  - `A	docs/research/2026-05-21_t8_forecastability_atlas.md`
  - `A	scripts/make_forecastability_atlas.py`
  - `M	src/reports/__init__.py`
  - `A	src/reports/forecastability_atlas.py`
  - `A	tests/test_forecastability_atlas.py`

### 114. `679b4a0` - feat(reports): add clinical utility analysis (#13)

- Full SHA: `679b4a0bbac6e82364cb0f5bc5daead6aa76060b`
- Date: `2026-05-21T10:49:20+01:00`
- Author: `Akir Oussama`
- Shortstat: 5 files changed, 651 insertions(+)
- Body:

```text
Add clinical utility decision-support analysis over threshold-sweep artifacts.

Includes configurable utility assumptions, constraints, refractory alarm suppression, CLI CSV/Markdown reports, Gate-C citable guardrails, and synthetic tests validated with full pytest.
```
- Files changed:
  - `A	docs/research/2026-05-21_t18_clinical_utility.md`
  - `A	scripts/make_clinical_utility_report.py`
  - `M	src/reports/__init__.py`
  - `A	src/reports/clinical_utility.py`
  - `A	tests/test_clinical_utility.py`

### 115. `82f71e9` - feat(features): add multiday cycle baselines (#14)

- Full SHA: `82f71e94acc4685d4b6059d87d8456f59e9553bf`
- Date: `2026-05-21T10:56:19+01:00`
- Author: `Akir Oussama`
- Shortstat: 7 files changed, 536 insertions(+), 5 deletions(-)
- Body:

```text
Add deterministic circadian/weekly/multiday cycle features and split-safe multicycle priors.

Includes rolling-origin predictions, label-permutation negative control, CLI support, timestamp phase-unit fix, synthetic tests, and full validation.
```
- Files changed:
  - `A	docs/research/2026-05-21_t9_multiday_cycle_features.md`
  - `M	scripts/run_cycle_baseline.py`
  - `M	src/baselines/__init__.py`
  - `M	src/baselines/cycle_baseline.py`
  - `M	src/features/__init__.py`
  - `A	src/features/cycle_features.py`
  - `A	tests/test_cycle_features.py`

### 116. `cbbbd12` - feat(reports): add SeizeIT2 full benchmark track (#15)

- Full SHA: `cbbbd124c82404e834818129129faba729db40f5`
- Date: `2026-05-21T11:22:12+01:00`
- Author: `Akir Oussama`
- Shortstat: 5 files changed, 894 insertions(+)
- Body:

```text
Add SeizeIT2 full-benchmark track readiness support.

Includes official split manifest guardrails, separated detection/early-warning/forecasting tracks, modality-specific track matrix, SeizeIT2 source isolation, expected-count comparison, CLI output, and synthetic tests.
```
- Files changed:
  - `A	docs/research/2026-05-21_t11_seizeit2_full_track.md`
  - `A	scripts/make_seizeit2_full_track.py`
  - `M	src/reports/__init__.py`
  - `A	src/reports/seizeit2_benchmark_track.py`
  - `A	tests/test_seizeit2_benchmark_track.py`

### 117. `d7037c7` - feat(reports): add statistical robustness layer (#16)

- Full SHA: `d7037c76904667b27cf6f0457462f0b40e7bb7b3`
- Date: `2026-05-21T11:35:30+01:00`
- Author: `Akir Oussama`
- Shortstat: 5 files changed, 993 insertions(+)
- Body:

```text
Adds patient/event bootstrap BSS intervals, paired clustered permutation tests, multiple-comparison correction, warnings, CLI exports, tests, and research trace.
```
- Files changed:
  - `A	docs/research/2026-05-21_t17_statistical_robustness.md`
  - `A	scripts/make_statistical_robustness_report.py`
  - `M	src/reports/__init__.py`
  - `A	src/reports/statistical_robustness.py`
  - `A	tests/test_statistical_robustness.py`

### 118. `3d5d154` - feat(audit): add clinical timeline workbench (#17)

- Full SHA: `3d5d154cf3c46b7f6c4841031bed48c885f792ef`
- Date: `2026-05-21T11:44:37+01:00`
- Author: `Akir Oussama`
- Shortstat: 6 files changed, 998 insertions(+), 2 deletions(-)
- Body:

```text
Adds static clinical audit workbench exports, timeline geometry, review-sheet integration, UNCERTAIN decision handling, tests, and research trace.
```
- Files changed:
  - `A	docs/research/2026-05-21_t7_clinical_timeline_audit_workbench.md`
  - `A	scripts/build_clinical_audit_workbench.py`
  - `M	src/reports/__init__.py`
  - `A	src/reports/clinical_audit_workbench.py`
  - `M	src/reports/label_audit.py`
  - `A	tests/test_clinical_audit_workbench.py`

### 119. `0290f53` - feat(features): add observability missingness layer (#18)

- Full SHA: `0290f536b9b49b0045b572f5379f0d60aade0ff9`
- Date: `2026-05-21T11:52:18+01:00`
- Author: `Akir Oussama`
- Shortstat: 10 files changed, 827 insertions(+), 6 deletions(-)
- Body:

```text
Adds sensor observability scoring, deficiency time, abstention policy, CLI/report outputs, leaderboard schema fields, tests, and research trace.
```
- Files changed:
  - `A	docs/research/2026-05-21_t12_observability_missingness.md`
  - `M	schemas/leaderboard_columns.csv`
  - `M	schemas/leaderboard_entry.schema.json`
  - `M	schemas/leaderboard_template.csv`
  - `A	scripts/compute_observability_report.py`
  - `M	scripts/make_leaderboard_row.py`
  - `M	src/features/__init__.py`
  - `A	src/features/observability.py`
  - `M	tests/test_leaderboard_schema.py`
  - `A	tests/test_observability.py`

### 120. `f40beae` - feat(baselines): add patient adaptive priors (#19)

- Full SHA: `f40beaeab616a1bf493b1cdf2fad768004189db1`
- Date: `2026-05-21T11:57:53+01:00`
- Author: `Akir Oussama`
- Shortstat: 5 files changed, 669 insertions(+)
- Body:

```text
Adds population, patient-prior, and empirical-Bayes baselines with cold/warm/rolling modes, explicit fallbacks, CLI artifacts, tests, and research trace.
```
- Files changed:
  - `A	docs/research/2026-05-21_t13_patient_adaptive_baselines.md`
  - `A	scripts/run_patient_adaptive_baseline.py`
  - `M	src/baselines/__init__.py`
  - `A	src/baselines/patient_adaptive.py`
  - `A	tests/test_patient_adaptive_baselines.py`

### 121. `5f1f7a3` - feat(models): add supervised ladder runner (#20)

- Full SHA: `5f1f7a379d1bb72ee72f2f4a897249356fea13c2`
- Date: `2026-05-21T12:31:28+01:00`
- Author: `Akir Oussama`
- Shortstat: 6 files changed, 1103 insertions(+)
- Body:

```text
Add a controlled supervised model ladder runner with mandatory null/reference comparator alignment, leakage-screened feature selection, standardized prediction outputs, deterministic multi-rung seed derivation, artifact/comparator hashes, config contract, research trace, and synthetic regression coverage.

Validation:
- uv run --extra dev ruff check src/models/supervised_ladder.py src/models/__init__.py scripts/run_supervised_model_ladder.py tests/test_supervised_ladder.py
- uv run --extra dev pytest tests/test_supervised_ladder.py tests/test_msg_tabular_training.py tests/test_leaderboard_runner.py (15 passed)
- uv run --extra dev ruff check .
- uv run --extra dev --extra torch pytest (229 passed)
```
- Files changed:
  - `A	configs/model/supervised_ladder.yaml`
  - `A	docs/research/2026-05-21_t14_supervised_model_ladder.md`
  - `A	scripts/run_supervised_model_ladder.py`
  - `M	src/models/__init__.py`
  - `A	src/models/supervised_ladder.py`
  - `A	tests/test_supervised_ladder.py`

### 122. `8476e8f` - feat(interpretability): add sparse autoencoder reports (#21)

- Full SHA: `8476e8f5b1715d5df125bbddd1edb1d96e0d827c`
- Date: `2026-05-21T12:40:20+01:00`
- Author: `Akir Oussama`
- Shortstat: 6 files changed, 1056 insertions(+)
- Body:

```text
Add a deterministic sparse autoencoder interpretability layer for hidden activation tables, including per-window SAE scores, feature dictionary, post-hoc associations, manifest hashes, CLI, config contract, documentation, and synthetic regression tests.

Validation:
- uv run --extra dev ruff check src/interpretability/__init__.py src/interpretability/sparse_autoencoder.py scripts/run_sparse_autoencoder_interpretability.py tests/test_sparse_autoencoder_interpretability.py
- uv run --extra dev pytest tests/test_sparse_autoencoder_interpretability.py (5 passed)
- uv run --extra dev --extra torch pytest tests/test_sparse_autoencoder_interpretability.py tests/test_supervised_ladder.py tests/test_models.py (17 passed)
- uv run --extra dev ruff check .
- uv run --extra dev --extra torch pytest (234 passed)
```
- Files changed:
  - `A	configs/model/sparse_autoencoder.yaml`
  - `A	docs/research/2026-05-21_m1_sparse_autoencoder_interpretability.md`
  - `A	scripts/run_sparse_autoencoder_interpretability.py`
  - `A	src/interpretability/__init__.py`
  - `A	src/interpretability/sparse_autoencoder.py`
  - `A	tests/test_sparse_autoencoder_interpretability.py`

### 123. `7db6574` - feat(adaptation): add rolling test-time score adaptation (#22)

- Full SHA: `7db65743593ed9fc3017fccae5eb04f40d767456`
- Date: `2026-05-21T12:46:14+01:00`
- Author: `Akir Oussama`
- Shortstat: 6 files changed, 766 insertions(+)
- Body:

```text
Add a leakage-safe score-level test-time adaptation layer for standardized prediction tables using rolling-origin patient-specific rank blending from past unlabeled risk scores only. Preserve original outputs, emit adapted risk scores for downstream runners, and add summary/manifest/report artifacts with documentation and synthetic leakage tests.

Validation:
- uv run --extra dev ruff check src/adaptation/__init__.py src/adaptation/test_time.py scripts/run_test_time_adaptation.py tests/test_test_time_adaptation.py
- uv run --extra dev pytest tests/test_test_time_adaptation.py (6 passed)
- uv run --extra dev pytest tests/test_test_time_adaptation.py tests/test_leaderboard_runner.py tests/test_calibration_thresholding.py tests/test_supervised_ladder.py (22 passed)
- uv run --extra dev ruff check .
- uv run --extra dev --extra torch pytest (240 passed)
```
- Files changed:
  - `A	configs/model/test_time_adaptation.yaml`
  - `A	docs/research/2026-05-21_p1_test_time_adaptation.md`
  - `A	scripts/run_test_time_adaptation.py`
  - `A	src/adaptation/__init__.py`
  - `A	src/adaptation/test_time.py`
  - `A	tests/test_test_time_adaptation.py`

### 124. `0d867c6` - feat(reports): add edge-aware ablation report (#23)

- Full SHA: `0d867c6bcc07fd020779e0c9643ef59affb26c28`
- Date: `2026-05-21T16:14:16+01:00`
- Author: `Akir Oussama`
- Shortstat: 6 files changed, 893 insertions(+)
- Body:

```text
Add an edge-aware ablation report that joins clinical metric rows with traceable edge cost profiles, validates cost/evidence fields, computes skill-per-cost and Pareto frontier outputs, and warns for pre-Gate-C clinical scores and estimated edge costs.

Validation:
- uv run --extra dev ruff check src/reports/edge_ablation.py src/reports/__init__.py scripts/make_edge_ablation_report.py tests/test_edge_ablation.py
- uv run --extra dev pytest tests/test_edge_ablation.py (5 passed)
- uv run --extra dev --extra torch pytest tests/test_edge_ablation.py tests/test_leaderboard_schema.py tests/test_leaderboard_runner.py tests/test_models.py (17 passed)
- uv run --extra dev ruff check .
- uv run --extra dev --extra torch pytest (245 passed)
```
- Files changed:
  - `A	configs/report/edge_ablation.yaml`
  - `A	docs/research/2026-05-21_t16_edge_aware_ablation.md`
  - `A	scripts/make_edge_ablation_report.py`
  - `M	src/reports/__init__.py`
  - `A	src/reports/edge_ablation.py`
  - `A	tests/test_edge_ablation.py`

### 125. `eb30601` - feat(reports): add workflow forensics report (#24)

- Full SHA: `eb30601f7c0fa6d71fdd3211aeac6ef629102dae`
- Date: `2026-05-21T16:19:53+01:00`
- Author: `Akir Oussama`
- Shortstat: 6 files changed, 715 insertions(+)
- Body:

```text
Add a workflow-forensics report that extracts descriptive methodology evidence from git history and checked-in repository docs, including commit/PR-style subjects, touched artifact classes, research docs, validation markers, guardrail markers, CLI, config, docs, and synthetic git-repository tests.

Validation:
- uv run --extra dev ruff check src/reports/workflow_forensics.py src/reports/__init__.py scripts/make_workflow_forensics_report.py tests/test_workflow_forensics.py
- uv run --extra dev pytest tests/test_workflow_forensics.py (4 passed)
- uv run --extra dev python scripts/make_workflow_forensics_report.py --repo-root . --out-dir /tmp/epitwin-w1-workflow-report --max-commits 80 --doc-globs 'docs/research/*.md,docs/*.md' (passed)
- uv run --extra dev pytest tests/test_workflow_forensics.py tests/test_edge_ablation.py tests/test_leaderboard_runner.py (13 passed)
- uv run --extra dev ruff check .
- uv run --extra dev --extra torch pytest (249 passed)
```
- Files changed:
  - `A	configs/report/workflow_forensics.yaml`
  - `A	docs/research/2026-05-21_w1_workflow_methodology_forensics.md`
  - `A	scripts/make_workflow_forensics_report.py`
  - `M	src/reports/__init__.py`
  - `A	src/reports/workflow_forensics.py`
  - `A	tests/test_workflow_forensics.py`

### 126. `de42b22` - feat(reports): add failure taxonomy report (#25)

- Full SHA: `de42b222e7ec9d2bd141e317ba3f7d9c5d12a13d`
- Date: `2026-05-21T16:25:54+01:00`
- Author: `Akir Oussama`
- Shortstat: 6 files changed, 740 insertions(+)
- Body:

```text
Add a post-hoc failure taxonomy for standardized prediction rows, assigning row-level categories, reasons, and severity with precedence for excluded rows and observability failures. Emit row, category, patient, warning, manifest, JSON, and Markdown outputs with CLI, config, docs, and tests.

Validation:
- uv run --extra dev ruff check src/reports/failure_taxonomy.py src/reports/__init__.py scripts/make_failure_taxonomy_report.py tests/test_failure_taxonomy.py
- uv run --extra dev pytest tests/test_failure_taxonomy.py (5 passed)
- uv run --extra dev pytest tests/test_failure_taxonomy.py tests/test_observability.py tests/test_clinical_utility.py tests/test_leaderboard_runner.py (20 passed)
- uv run --extra dev ruff check .
- uv run --extra dev --extra torch pytest (254 passed)
```
- Files changed:
  - `A	configs/report/failure_taxonomy.yaml`
  - `A	docs/research/2026-05-21_t19_failure_taxonomy.md`
  - `A	scripts/make_failure_taxonomy_report.py`
  - `M	src/reports/__init__.py`
  - `A	src/reports/failure_taxonomy.py`
  - `A	tests/test_failure_taxonomy.py`

### 127. `7394348` - feat(interpretability): add counterfactual probing (#26)

- Full SHA: `7394348d8bcc46532710b868ad8679557d5b8611`
- Date: `2026-05-22T00:26:24+01:00`
- Author: `Akir Oussama`
- Shortstat: 6 files changed, 864 insertions(+)
- Body:

```text
Add surrogate-based local counterfactual probing for standardized prediction rows with feature columns. Fit a leakage-screened ridge linear surrogate to model risk scores, emit counterfactual rows and top-k feature changes, and document post-hoc-not-causal guardrails.

Validation:
- uv run --extra dev ruff check src/interpretability/counterfactual.py src/interpretability/__init__.py scripts/run_counterfactual_probing.py tests/test_counterfactual_probing.py
- uv run --extra dev pytest tests/test_counterfactual_probing.py (5 passed)
- uv run --extra dev pytest tests/test_counterfactual_probing.py tests/test_sparse_autoencoder_interpretability.py tests/test_failure_taxonomy.py tests/test_supervised_ladder.py (23 passed)
- uv run --extra dev ruff check .
- uv run --extra dev --extra torch pytest (259 passed)
```
- Files changed:
  - `A	configs/report/counterfactual_probing.yaml`
  - `A	docs/research/2026-05-22_m3_counterfactual_probing.md`
  - `A	scripts/run_counterfactual_probing.py`
  - `M	src/interpretability/__init__.py`
  - `A	src/interpretability/counterfactual.py`
  - `A	tests/test_counterfactual_probing.py`

### 128. `1fee975` - feat(reports): add n1 longitudinal deep dive (#27)

- Full SHA: `1fee975277c6604f39e5640e47916538d4e6c93a`
- Date: `2026-05-22T00:37:27+01:00`
- Author: `Akir Oussama`
- Shortstat: 6 files changed, 704 insertions(+)
- Body:

```text
Add descriptive single-patient longitudinal reporting infrastructure.

Validation:
- uv run --extra dev ruff check .
- uv run --extra dev --extra torch pytest -> 264 passed
```
- Files changed:
  - `A	configs/report/longitudinal_deep_dive.yaml`
  - `A	docs/research/2026-05-22_p3_n1_longitudinal_deep_dive.md`
  - `A	scripts/make_longitudinal_deep_dive.py`
  - `M	src/reports/__init__.py`
  - `A	src/reports/longitudinal_deep_dive.py`
  - `A	tests/test_longitudinal_deep_dive.py`

### 129. `e5eb88c` - feat(reports): add external sota reproduction bridge (#28)

- Full SHA: `e5eb88cb61276fb4e249a8a28f391733c3e190f9`
- Date: `2026-05-22T00:46:18+01:00`
- Author: `Akir Oussama`
- Shortstat: 6 files changed, 1019 insertions(+)
- Body:

```text
Add a strict bridge for scoring external SOTA-family prediction tables through the EpiTwin leaderboard runner.

Validation:
- uv run --extra dev ruff check .
- uv run --extra dev --extra torch pytest -> 268 passed
```
- Files changed:
  - `A	configs/reproduction/external_sota_reproduction.yaml`
  - `A	docs/commits/2026-05-22_t10_external_sota_reproduction.md`
  - `A	scripts/run_external_sota_reproduction.py`
  - `M	src/reports/__init__.py`
  - `A	src/reports/external_sota_reproduction.py`
  - `A	tests/test_external_sota_reproduction.py`

### 130. `242afde` - feat(reports): add paper artifact package (#29)

- Full SHA: `242afde39e00ecfbe60179021b0d92638b3309c2`
- Date: `2026-05-22T00:51:41+01:00`
- Author: `Akir Oussama`
- Shortstat: 6 files changed, 735 insertions(+)
- Body:

```text
Add a paper-facing artifact package builder with claim traceability, reproducibility checklist, and Gate C citation guardrails.

Validation:
- uv run --extra dev ruff check .
- uv run --extra dev --extra torch pytest -> 273 passed
```
- Files changed:
  - `A	configs/report/paper_artifact_package.yaml`
  - `A	docs/commits/2026-05-22_t20_paper_artifact_package.md`
  - `A	scripts/build_paper_artifact_package.py`
  - `M	src/reports/__init__.py`
  - `A	src/reports/paper_artifact_package.py`
  - `A	tests/test_paper_artifact_package.py`

### 131. `d9bcc5c` - feat(features): add foundation transfer protocol (#30)

- Full SHA: `d9bcc5cd216b2de7e47cce3b6e1bb4b83abb3a69`
- Date: `2026-05-22T00:56:43+01:00`
- Author: `Akir Oussama`
- Shortstat: 6 files changed, 644 insertions(+)
- Body:

```text
Add frozen foundation embedding transfer features with provenance, license, modality, and Gate C guardrails.

Validation:
- uv run --extra dev ruff check .
- uv run --extra dev --extra torch pytest -> 278 passed
```
- Files changed:
  - `A	configs/model/foundation_transfer.yaml`
  - `A	docs/commits/2026-05-22_t15_foundation_transfer_protocol.md`
  - `A	scripts/prepare_foundation_transfer_features.py`
  - `M	src/features/__init__.py`
  - `A	src/features/foundation_transfer.py`
  - `A	tests/test_foundation_transfer.py`

### 132. `fc25214` - feat(reports): add federated benchmark protocol (#31)

- Full SHA: `fc25214923c0b65b0036dc54d0affc7b3862dd27`
- Date: `2026-05-22T01:01:03+01:00`
- Author: `Akir Oussama`
- Shortstat: 6 files changed, 593 insertions(+)
- Body:

```text
Add a federated benchmark protocol that aggregates site-level leaderboard rows without raw patient/window data.

Validation:
- uv run --extra dev ruff check .
- uv run --extra dev --extra torch pytest -> 283 passed
```
- Files changed:
  - `A	configs/report/federated_benchmark.yaml`
  - `A	docs/commits/2026-05-22_f2_federated_benchmark_protocol.md`
  - `A	scripts/make_federated_benchmark_report.py`
  - `M	src/reports/__init__.py`
  - `A	src/reports/federated_benchmark.py`
  - `A	tests/test_federated_benchmark.py`

### 133. `d7a61f7` - docs: add anti hallucination audit (#32)

- Full SHA: `d7a61f731ad2e0b2ad17155ab478408c3e66f254`
- Date: `2026-05-22T07:45:07+01:00`
- Author: `Akir Oussama`
- Shortstat: 9 files changed, 133 insertions(+), 8 deletions(-)
- Body:

```text
docs: add anti hallucination audit
```
- Files changed:
  - `M	PLAYBOOK.md`
  - `M	configs/model/foundation_transfer.yaml`
  - `M	configs/report/federated_benchmark.yaml`
  - `M	configs/report/paper_artifact_package.yaml`
  - `M	docs/CLAUDE_CODEX_WORKORDER_REREVIEW_2026-05-18.md`
  - `A	docs/commits/2026-05-22_anti_hallucination_audit.md`
  - `M	docs/commits/2026-05-22_f2_federated_benchmark_protocol.md`
  - `M	docs/commits/2026-05-22_t10_external_sota_reproduction.md`
  - `M	docs/commits/2026-05-22_t15_foundation_transfer_protocol.md`

### 134. `be7ed94` - fix: harden coherence review guardrails (#33)

- Full SHA: `be7ed949b03d268c34b2d69b520ba6473f672a98`
- Date: `2026-05-22T09:05:07+01:00`
- Author: `Akir Oussama`
- Shortstat: 12 files changed, 350 insertions(+), 46 deletions(-)
- Body:

```text
fix: harden coherence review guardrails

- fail closed for clinical utility rows with missing alarm-burden metrics
- require leaderboard prediction contract and BSS reference alignment
- require primary-source verification for source-only paper claims
- refresh roadmap/playbook/publication wording around Gate B/C and SOTA comparability

Validation:
- uv run --extra dev ruff check .
- uv run --extra dev pytest tests/test_clinical_utility.py tests/test_leaderboard_runner.py tests/test_paper_artifact_package.py tests/test_gate_c_registry.py tests/test_external_sota_reproduction.py tests/test_forecastability_atlas.py -> 32 passed
- uv run --extra dev --extra torch pytest -> 287 passed
- git diff --check
```
- Files changed:
  - `M	PLAYBOOK.md`
  - `M	README.md`
  - `M	configs/report/paper_artifact_package.yaml`
  - `M	docs/PUBLICATION_PROPOSAL.md`
  - `M	docs/ROADMAP_HIGH_LEVEL.md`
  - `A	docs/commits/2026-05-22_general_coherence_review_fixes.md`
  - `M	scripts/make_leaderboard_row.py`
  - `M	src/reports/clinical_utility.py`
  - `M	src/reports/paper_artifact_package.py`
  - `M	tests/test_clinical_utility.py`
  - `M	tests/test_leaderboard_runner.py`
  - `M	tests/test_paper_artifact_package.py`

### 135. `4475545` - docs: refresh claims surface status (#34)

- Full SHA: `44755455d87c967cdee5e1381a1846d2a1d88fa2`
- Date: `2026-05-22T09:11:54+01:00`
- Author: `Akir Oussama`
- Shortstat: 4 files changed, 68 insertions(+), 6 deletions(-)
- Body:

```text
docs: refresh claims surface status

- refresh PROJECT_STATUS for May 20-22 publishability scaffolds
- keep all scaffolds explicitly non-citable before Gate B/C
- remove remaining operational-doc hardware typo surface
- convert the old typo item into a non-regression guardrail

Validation:
- rg tibia/tibial over current operational docs -> no hits
- rg stale Gate/status phrases over current docs -> only explicit forbidden first-wearable guardrails remain
- uv run --extra dev ruff check .
- uv run --extra dev pytest tests/test_workflow_forensics.py -> 4 passed
- git diff --check
```
- Files changed:
  - `M	PLAYBOOK.md`
  - `M	PROJECT_STATUS.md`
  - `M	docs/ROADMAP_HIGH_LEVEL.md`
  - `A	docs/commits/2026-05-22_claims_surface_sweep.md`

### 136. `b3e951a` - docs: add general status roadmap synthesis (#35)

- Full SHA: `b3e951afa9d07da5e30e183d1e0b21c1cb5ef519`
- Date: `2026-05-22T09:20:57+01:00`
- Author: `Akir Oussama`
- Shortstat: 2 files changed, 508 insertions(+)
- Body:

```text
docs: add general status roadmap synthesis

- add general status / done-ongoing-to-do roadmap synthesis
- record source material and validation trace in docs/commits
- keep Gate B and Gate C blockers explicit
- avoid introducing any new benchmark or citable-result claim

Validation:
- git diff --check
- uv run --extra dev ruff check .
- rg risk/claim terms in status synthesis
- ASCII-only check on new synthesis and trace files
```
- Files changed:
  - `A	docs/commits/2026-05-22_status_synthesis.md`
  - `A	docs/research/2026-05-22_general_status_and_roadmap.md`

### 137. `1bc70e4` - feat(audit): add gate b audit package builder (#36)

- Full SHA: `1bc70e4711624a0d2a0d56048aa486747e87f9e3`
- Date: `2026-05-22T09:55:58+01:00`
- Author: `Akir Oussama`
- Shortstat: 5 files changed, 750 insertions(+)
- Body:

```text
feat(audit): add gate b audit package builder

- add package builder around active audit selection
- emit selected human review sheet, full candidates, manifest, and Markdown instructions
- keep review decisions blank and mark status pending human review
- document Gate B/C guardrails and validation trace

Validation:
- uv run --extra dev ruff check src/reports/gate_b_audit_package.py scripts/build_gate_b_audit_package.py tests/test_gate_b_audit_package.py src/reports/__init__.py
- uv run --extra dev pytest tests/test_gate_b_audit_package.py tests/test_active_audit_selection.py tests/test_label_audit.py -> 15 passed
- uv run --extra dev ruff check .
- uv run --extra dev --extra torch pytest -> 290 passed
- git diff --check
```
- Files changed:
  - `A	docs/commits/2026-05-22_gate_b_audit_acceleration.md`
  - `A	docs/research/2026-05-22_gate_b_audit_acceleration_package.md`
  - `A	scripts/build_gate_b_audit_package.py`
  - `A	src/reports/gate_b_audit_package.py`
  - `A	tests/test_gate_b_audit_package.py`

### 138. `43cb4b0` - feat(reports): add gate c dry-run diagnostics (#37)

- Full SHA: `43cb4b020e6f4e5ce39eaed6346345933b009723`
- Date: `2026-05-22T10:03:37+01:00`
- Author: `Akir Oussama`
- Shortstat: 5 files changed, 602 insertions(+)
- Body:

```text
Add dry-run diagnostics that separate structural registry verification from frozen/citable Gate C readiness.

- add JSON/Markdown/artifact-summary CLI outputs for Gate C dry-runs
- check Gate B status, freeze status, preregistration/DOI, and required artifact roles as explicit blockers
- document the dry-run guardrails and trace evidence in docs/commits

Validation:
- uv run --extra dev ruff check src/reports/gate_c_dry_run.py scripts/make_gate_c_dry_run_report.py tests/test_gate_c_dry_run.py
- uv run --extra dev pytest tests/test_gate_c_dry_run.py tests/test_gate_c_registry.py -> 7 passed
- uv run --extra dev ruff check .
- uv run --extra dev --extra torch pytest -> 293 passed
- git diff --check
```
- Files changed:
  - `A	docs/commits/2026-05-22_gate_c_dry_run_diagnostics.md`
  - `A	docs/research/2026-05-22_gate_c_dry_run_diagnostics.md`
  - `A	scripts/make_gate_c_dry_run_report.py`
  - `A	src/reports/gate_c_dry_run.py`
  - `A	tests/test_gate_c_dry_run.py`

### 139. `246a765` - feat(reports): add msg data-gap triage (#38)

- Full SHA: `246a7653720e176af5159631d3aa36528b6501db`
- Date: `2026-05-22T10:11:36+01:00`
- Author: `Akir Oussama`
- Shortstat: 5 files changed, 911 insertions(+)
- Body:

```text
Convert MSG source-data and horizon feasibility blockers into explicit pre-Gate-C triage artifacts.

- add patient triage for zero recordings, zero matched events, unmatched events, low match fraction, and large seizure clusters
- add horizon triage for low valid-window fraction, low event coverability, high right-censored unknown burden, and unmatched source events
- add CLI outputs for CSV summary tables, manifest, JSON, and Markdown
- document guardrails and validation trace in docs/commits

Validation:
- uv run --extra dev ruff check src/reports/msg_gap_triage.py scripts/build_msg_gap_triage.py tests/test_msg_gap_triage.py
- uv run --extra dev pytest tests/test_msg_gap_triage.py tests/test_event_coverage.py tests/test_horizon_viability.py -> 10 passed
- uv run --extra dev ruff check .
- uv run --extra dev --extra torch pytest -> 297 passed
- git diff --check
```
- Files changed:
  - `A	docs/commits/2026-05-22_msg_data_gap_triage.md`
  - `A	docs/research/2026-05-22_msg_data_gap_triage.md`
  - `A	scripts/build_msg_gap_triage.py`
  - `A	src/reports/msg_gap_triage.py`
  - `A	tests/test_msg_gap_triage.py`

### 140. `82b3d0a` - feat(reports): add seizeit2 cohort readiness guardrail (#39)

- Full SHA: `82b3d0a6395b342e6ca0413fa1a86fc3f46039ec`
- Date: `2026-05-22T10:17:36+01:00`
- Author: `Akir Oussama`
- Shortstat: 5 files changed, 823 insertions(+)
- Body:

```text
Add a full-cohort claim guardrail over SeizeIT2 readiness/count artifacts.

- block smoke-subset claims when Gate B/C, expected counts, official splits, required tasks, required modalities, or ready tracks are missing
- add CLI outputs for summary, blockers, warnings, manifest, JSON, and Markdown
- keep claim status explicitly pre-Gate-C and non-citable
- document guardrails and validation trace in docs/commits

Validation:
- uv run --extra dev ruff check src/reports/seizeit2_cohort_readiness.py scripts/build_seizeit2_cohort_readiness.py tests/test_seizeit2_cohort_readiness.py
- uv run --extra dev pytest tests/test_seizeit2_cohort_readiness.py tests/test_seizeit2_benchmark_track.py -> 10 passed
- uv run --extra dev ruff check .
- uv run --extra dev --extra torch pytest -> 300 passed
- git diff --check
```
- Files changed:
  - `A	docs/commits/2026-05-22_seizeit2_cohort_readiness.md`
  - `A	docs/research/2026-05-22_seizeit2_cohort_readiness.md`
  - `A	scripts/build_seizeit2_cohort_readiness.py`
  - `A	src/reports/seizeit2_cohort_readiness.py`
  - `A	tests/test_seizeit2_cohort_readiness.py`

### 141. `8ad790f` - chore(reports): run local gate guardrails (#40)

- Full SHA: `8ad790fbdfd3bdbe92fb7c4337c4602a8b895a9b`
- Date: `2026-05-22T11:48:37+01:00`
- Author: `Akir Oussama`
- Shortstat: 26 files changed, 1899 insertions(+)
- Body:

```text
Execute local MSG and SeizeIT2 guardrails on committed report artifacts and materialize a Gate B/C action checklist.

- add checklist builder with evidence, owners, priorities, and exit criteria
- add local guardrail runner that extracts structured tables from committed Markdown reports
- generate reports/local_gate_guardrails_2026-05-22 with CSV/JSON/Markdown outputs and extracted inputs
- document MSG and SeizeIT2 blockers plus Gate B/Gate C next actions

Local guardrail result:
- MSG: 3 P0 patients, 258 unmatched events, 5 horizons not main-table-ready
- SeizeIT2: local sub-125 artifact only; 20 cohort-readiness blockers
- Checklist: 8 actions total, including 3 P0 actions and Gate C freeze block

Validation:
- uv run --extra dev ruff check src/reports/gate_bc_checklist.py scripts/run_local_gate_guardrails.py tests/test_gate_bc_checklist.py
- uv run --extra dev pytest tests/test_gate_bc_checklist.py tests/test_msg_gap_triage.py tests/test_seizeit2_cohort_readiness.py -> 9 passed
- uv run --extra dev ruff check .
- uv run --extra dev --extra torch pytest -> 302 passed
- git diff --check
```
- Files changed:
  - `A	docs/commits/2026-05-22_local_gate_guardrail_execution.md`
  - `A	docs/research/2026-05-22_local_gate_guardrail_execution.md`
  - `A	reports/local_gate_guardrails_2026-05-22/gate_bc_action_checklist.csv`
  - `A	reports/local_gate_guardrails_2026-05-22/gate_bc_action_checklist.json`
  - `A	reports/local_gate_guardrails_2026-05-22/gate_bc_action_checklist.md`
  - `A	reports/local_gate_guardrails_2026-05-22/gate_bc_action_summary.csv`
  - `A	reports/local_gate_guardrails_2026-05-22/inputs/msg_event_clusters.csv`
  - `A	reports/local_gate_guardrails_2026-05-22/inputs/msg_event_coverage.csv`
  - `A	reports/local_gate_guardrails_2026-05-22/inputs/msg_horizon_viability.csv`
  - `A	reports/local_gate_guardrails_2026-05-22/inputs/seizeit2_local_count_summary.csv`
  - `A	reports/local_gate_guardrails_2026-05-22/inputs/seizeit2_local_track.csv`
  - `A	reports/local_gate_guardrails_2026-05-22/msg_gap_horizon_triage.csv`
  - `A	reports/local_gate_guardrails_2026-05-22/msg_gap_patient_triage.csv`
  - `A	reports/local_gate_guardrails_2026-05-22/msg_gap_summary.csv`
  - `A	reports/local_gate_guardrails_2026-05-22/msg_gap_triage_manifest.csv`
  - `A	reports/local_gate_guardrails_2026-05-22/msg_gap_triage_report.json`
  - `A	reports/local_gate_guardrails_2026-05-22/msg_gap_triage_report.md`
  - `A	reports/local_gate_guardrails_2026-05-22/seizeit2_cohort_readiness_blockers.csv`
  - `A	reports/local_gate_guardrails_2026-05-22/seizeit2_cohort_readiness_manifest.csv`
  - `A	reports/local_gate_guardrails_2026-05-22/seizeit2_cohort_readiness_report.json`
  - `A	reports/local_gate_guardrails_2026-05-22/seizeit2_cohort_readiness_report.md`
  - `A	reports/local_gate_guardrails_2026-05-22/seizeit2_cohort_readiness_summary.csv`
  - `A	reports/local_gate_guardrails_2026-05-22/seizeit2_cohort_readiness_warnings.csv`
  - `A	scripts/run_local_gate_guardrails.py`
  - `A	src/reports/gate_bc_checklist.py`
  - `A	tests/test_gate_bc_checklist.py`

### 142. `1ced2a6` - chore(audit): add gate b closeout ledger (#41)

- Full SHA: `1ced2a68b0fdd2c4a3332e542a2d298d3d3d26e2`
- Date: `2026-05-22T13:44:08+01:00`
- Author: `Akir Oussama`
- Shortstat: 10 files changed, 1067 insertions(+)
- Body:

```text
Add a human-reviewable Gate B closeout ledger generated from the local Gate B/C guardrail checklist.

- add closeout ledger builder and CLI
- materialize reports/gate_b_closeout_2026-05-22 with CSV/JSON/Markdown outputs
- keep all human decision columns blank and Gate B blocked pending closeout
- document required evidence, allowed human decisions, and validation trace

Local result:
- ledger rows: 8
- open rows: 8
- P0 open rows: 3
- Gate B status: blocked_pending_human_closeout

Validation:
- uv run --extra dev ruff check src/reports/gate_b_closeout.py scripts/build_gate_b_closeout_ledger.py tests/test_gate_b_closeout.py
- uv run --extra dev pytest tests/test_gate_b_closeout.py tests/test_gate_bc_checklist.py -> 5 passed
- uv run --extra dev ruff check .
- uv run --extra dev --extra torch pytest -> 305 passed
- git diff --check
```
- Files changed:
  - `A	docs/commits/2026-05-22_gate_b_closeout_ledger.md`
  - `A	docs/research/2026-05-22_gate_b_closeout_ledger.md`
  - `A	reports/gate_b_closeout_2026-05-22/gate_b_closeout_ledger.csv`
  - `A	reports/gate_b_closeout_2026-05-22/gate_b_closeout_ledger.json`
  - `A	reports/gate_b_closeout_2026-05-22/gate_b_closeout_ledger.md`
  - `A	reports/gate_b_closeout_2026-05-22/gate_b_closeout_manifest.json`
  - `A	reports/gate_b_closeout_2026-05-22/gate_b_closeout_summary.csv`
  - `A	scripts/build_gate_b_closeout_ledger.py`
  - `A	src/reports/gate_b_closeout.py`
  - `A	tests/test_gate_b_closeout.py`

### 143. `ca8d69e` - chore(audit): apply partial gate b closeout (#42)

- Full SHA: `ca8d69ec0cbf0e33e986fad0afb94ee463de0237`
- Date: `2026-05-22T14:25:18+01:00`
- Author: `Akir Oussama`
- Shortstat: 11 files changed, 487 insertions(+), 54 deletions(-)
- Body:

```text
Apply reviewer-supplied closeout decisions for GB-001 through GB-003 while keeping Gate B fail-closed.

- add reproducible decision-application CLI
- record supplied decisions in reports/gate_b_closeout_2026-05-22
- regenerate ledger, summary, manifest, JSON, and Markdown outputs
- keep GB-004 through GB-008 pending and Gate B blocked
- document that evidence URIs/hashes are reviewer-supplied attestations, not independently verified by this run

Result:
- closed rows: 3
- open rows: 5
- P0 open rows: 0
- Gate B status: blocked_pending_human_closeout

Validation:
- uv run --extra dev ruff check src/reports/gate_b_closeout.py scripts/apply_gate_b_closeout_decisions.py tests/test_gate_b_closeout.py
- uv run --extra dev pytest tests/test_gate_b_closeout.py -> 5 passed
- uv run --extra dev ruff check .
- uv run --extra dev --extra torch pytest -> 307 passed
- git diff --check
```
- Files changed:
  - `A	docs/commits/2026-05-22_gate_b_partial_closeout.md`
  - `A	docs/research/2026-05-22_gate_b_partial_closeout.md`
  - `A	reports/gate_b_closeout_2026-05-22/gate_b_closeout_decisions_partial_2026-05-22.csv`
  - `M	reports/gate_b_closeout_2026-05-22/gate_b_closeout_ledger.csv`
  - `M	reports/gate_b_closeout_2026-05-22/gate_b_closeout_ledger.json`
  - `M	reports/gate_b_closeout_2026-05-22/gate_b_closeout_ledger.md`
  - `M	reports/gate_b_closeout_2026-05-22/gate_b_closeout_manifest.json`
  - `M	reports/gate_b_closeout_2026-05-22/gate_b_closeout_summary.csv`
  - `A	scripts/apply_gate_b_closeout_decisions.py`
  - `M	src/reports/gate_b_closeout.py`
  - `M	tests/test_gate_b_closeout.py`

### 144. `7b7bd6a` - chore(audit): add simulated gate b closeout (#43)

- Full SHA: `7b7bd6a4ef3cf294cc0c5345c84bcbce8324a385`
- Date: `2026-05-22T16:11:01+01:00`
- Author: `Akir Oussama`
- Shortstat: 16 files changed, 655 insertions(+), 11 deletions(-)
- Body:

```text
Record user-provided positive simulation decisions for GB-004 through GB-008 without advancing real Gate B.

- add decision_evidence_status to closeout summary, manifest, and Markdown
- add simulation mode that reports simulation_complete_not_gate_b_evidence instead of ready_for_gate_b_validation_rerun
- generate reports/gate_b_closeout_simulation_2026-05-22
- regenerate the real partial ledger only to mark it human_attested_not_independently_verified; it remains blocked

Simulation result:
- closed rows: 8
- open rows: 0
- status: simulation_complete_not_gate_b_evidence

Real ledger state:
- closed rows: 3
- open rows: 5
- status: blocked_pending_human_closeout

Validation:
- uv run --extra dev ruff check src/reports/gate_b_closeout.py scripts/apply_gate_b_closeout_decisions.py scripts/build_gate_b_closeout_ledger.py tests/test_gate_b_closeout.py
- uv run --extra dev pytest tests/test_gate_b_closeout.py -> 6 passed
- uv run --extra dev ruff check .
- uv run --extra dev --extra torch pytest -> 308 passed
- git diff --check
```
- Files changed:
  - `A	docs/commits/2026-05-22_gate_b_simulated_closeout.md`
  - `A	docs/research/2026-05-22_gate_b_simulated_closeout.md`
  - `M	reports/gate_b_closeout_2026-05-22/gate_b_closeout_ledger.json`
  - `M	reports/gate_b_closeout_2026-05-22/gate_b_closeout_ledger.md`
  - `M	reports/gate_b_closeout_2026-05-22/gate_b_closeout_manifest.json`
  - `M	reports/gate_b_closeout_2026-05-22/gate_b_closeout_summary.csv`
  - `A	reports/gate_b_closeout_simulation_2026-05-22/gate_b_closeout_decisions_simulated_remaining_2026-05-22.csv`
  - `A	reports/gate_b_closeout_simulation_2026-05-22/gate_b_closeout_ledger.csv`
  - `A	reports/gate_b_closeout_simulation_2026-05-22/gate_b_closeout_ledger.json`
  - `A	reports/gate_b_closeout_simulation_2026-05-22/gate_b_closeout_ledger.md`
  - `A	reports/gate_b_closeout_simulation_2026-05-22/gate_b_closeout_manifest.json`
  - `A	reports/gate_b_closeout_simulation_2026-05-22/gate_b_closeout_summary.csv`
  - `M	scripts/apply_gate_b_closeout_decisions.py`
  - `M	scripts/build_gate_b_closeout_ledger.py`
  - `M	src/reports/gate_b_closeout.py`
  - `M	tests/test_gate_b_closeout.py`

### 145. `cee513e` - chore(audit): add gate b real closeout package (#44)

- Full SHA: `cee513efa04eb5e894e3d49dacfeda410ce62ee6`
- Date: `2026-05-22T21:54:17+01:00`
- Author: `Akir Oussama`
- Shortstat: 11 files changed, 937 insertions(+)
- Body:

```text
Add a real Gate B closeout package that keeps simulation rows as non-promoted hints.

This adds validation against applying simulated decisions as real closeout, writes a blank real-decision template for GB-004 through GB-008, and records the blocked real status with tests and trace docs.

Validation:
- uv run ruff check src/reports/gate_b_closeout.py scripts/build_gate_b_real_closeout_package.py tests/test_gate_b_closeout.py
- uv run pytest tests/test_gate_b_closeout.py -q
- uv run ruff check .
- uv run pytest -q
- git diff --check
```
- Files changed:
  - `A	docs/commits/2026-05-22_gate_b_real_closeout.md`
  - `A	docs/research/2026-05-22_gate_b_real_closeout.md`
  - `A	reports/gate_b_real_closeout_2026-05-22/gate_b_real_closeout.json`
  - `A	reports/gate_b_real_closeout_2026-05-22/gate_b_real_closeout.md`
  - `A	reports/gate_b_real_closeout_2026-05-22/gate_b_real_closeout_manifest.json`
  - `A	reports/gate_b_real_closeout_2026-05-22/gate_b_real_closeout_readiness.csv`
  - `A	reports/gate_b_real_closeout_2026-05-22/gate_b_real_closeout_required_decisions_template.csv`
  - `A	reports/gate_b_real_closeout_2026-05-22/gate_b_real_closeout_summary.csv`
  - `A	scripts/build_gate_b_real_closeout_package.py`
  - `M	src/reports/gate_b_closeout.py`
  - `M	tests/test_gate_b_closeout.py`

### 146. `c0eaee1` - chore(audit): add gate b validation rerun harness (#45)

- Full SHA: `c0eaee17bbb34b7bc074a11c03b757bf59e58451`
- Date: `2026-05-22T22:08:04+01:00`
- Author: `Akir Oussama`
- Shortstat: 31 files changed, 2057 insertions(+)
- Body:

```text
Add a Gate B validation rerun harness that joins fresh guardrail actions to real closeout rows.

The committed rerun remains blocked_pending_real_closeout with five open non-P0 Gate B actions, and all outputs stay non-citable before Gate C.

Validation:
- uv run ruff check src/reports/gate_b_validation.py scripts/run_gate_b_validation_rerun.py tests/test_gate_b_validation.py
- uv run pytest tests/test_gate_b_validation.py tests/test_gate_b_closeout.py tests/test_gate_bc_checklist.py -q
- uv run ruff check .
- uv run pytest -q
- git diff --check
```
- Files changed:
  - `A	docs/commits/2026-05-22_gate_b_validation_rerun.md`
  - `A	docs/research/2026-05-22_gate_b_validation_rerun.md`
  - `A	reports/gate_b_validation_rerun_2026-05-22/gate_b_validation_manifest.json`
  - `A	reports/gate_b_validation_rerun_2026-05-22/gate_b_validation_matrix.csv`
  - `A	reports/gate_b_validation_rerun_2026-05-22/gate_b_validation_rerun.json`
  - `A	reports/gate_b_validation_rerun_2026-05-22/gate_b_validation_rerun.md`
  - `A	reports/gate_b_validation_rerun_2026-05-22/gate_b_validation_summary.csv`
  - `A	reports/gate_b_validation_rerun_2026-05-22/guardrails/gate_bc_action_checklist.csv`
  - `A	reports/gate_b_validation_rerun_2026-05-22/guardrails/gate_bc_action_checklist.json`
  - `A	reports/gate_b_validation_rerun_2026-05-22/guardrails/gate_bc_action_checklist.md`
  - `A	reports/gate_b_validation_rerun_2026-05-22/guardrails/gate_bc_action_summary.csv`
  - `A	reports/gate_b_validation_rerun_2026-05-22/guardrails/inputs/msg_event_clusters.csv`
  - `A	reports/gate_b_validation_rerun_2026-05-22/guardrails/inputs/msg_event_coverage.csv`
  - `A	reports/gate_b_validation_rerun_2026-05-22/guardrails/inputs/msg_horizon_viability.csv`
  - `A	reports/gate_b_validation_rerun_2026-05-22/guardrails/inputs/seizeit2_local_count_summary.csv`
  - `A	reports/gate_b_validation_rerun_2026-05-22/guardrails/inputs/seizeit2_local_track.csv`
  - `A	reports/gate_b_validation_rerun_2026-05-22/guardrails/msg_gap_horizon_triage.csv`
  - `A	reports/gate_b_validation_rerun_2026-05-22/guardrails/msg_gap_patient_triage.csv`
  - `A	reports/gate_b_validation_rerun_2026-05-22/guardrails/msg_gap_summary.csv`
  - `A	reports/gate_b_validation_rerun_2026-05-22/guardrails/msg_gap_triage_manifest.csv`
  - `A	reports/gate_b_validation_rerun_2026-05-22/guardrails/msg_gap_triage_report.json`
  - `A	reports/gate_b_validation_rerun_2026-05-22/guardrails/msg_gap_triage_report.md`
  - `A	reports/gate_b_validation_rerun_2026-05-22/guardrails/seizeit2_cohort_readiness_blockers.csv`
  - `A	reports/gate_b_validation_rerun_2026-05-22/guardrails/seizeit2_cohort_readiness_manifest.csv`
  - `A	reports/gate_b_validation_rerun_2026-05-22/guardrails/seizeit2_cohort_readiness_report.json`
  - `A	reports/gate_b_validation_rerun_2026-05-22/guardrails/seizeit2_cohort_readiness_report.md`
  - `A	reports/gate_b_validation_rerun_2026-05-22/guardrails/seizeit2_cohort_readiness_summary.csv`
  - `A	reports/gate_b_validation_rerun_2026-05-22/guardrails/seizeit2_cohort_readiness_warnings.csv`
  - `A	scripts/run_gate_b_validation_rerun.py`
  - `A	src/reports/gate_b_validation.py`
  - `A	tests/test_gate_b_validation.py`

### 147. `23949e1` - chore(audit): add gate b real decision intake (#46)

- Full SHA: `23949e178735b07f8325d77d6d18cfb0837f60f5`
- Date: `2026-05-23T04:58:41+01:00`
- Author: `Akir Oussama`
- Shortstat: 10 files changed, 1019 insertions(+)
- Body:

```text
Add a strict Gate B real-decision intake/preflight before applying reviewer decisions.

The current generated intake remains blocked because GB-004 through GB-008 are blank template rows, with all outputs non-citable before Gate C.

Validation:
- uv run ruff check src/reports/gate_b_decision_intake.py scripts/run_gate_b_real_decision_intake.py tests/test_gate_b_decision_intake.py
- uv run pytest tests/test_gate_b_decision_intake.py tests/test_gate_b_closeout.py tests/test_gate_b_validation.py -q
- uv run ruff check .
- uv run pytest -q
- git diff --check
```
- Files changed:
  - `A	docs/commits/2026-05-23_gate_b_real_decision_intake.md`
  - `A	docs/research/2026-05-23_gate_b_real_decision_intake.md`
  - `A	reports/gate_b_real_decision_intake_2026-05-23/gate_b_real_decision_intake.json`
  - `A	reports/gate_b_real_decision_intake_2026-05-23/gate_b_real_decision_intake.md`
  - `A	reports/gate_b_real_decision_intake_2026-05-23/gate_b_real_decision_intake_manifest.json`
  - `A	reports/gate_b_real_decision_intake_2026-05-23/gate_b_real_decision_intake_rows.csv`
  - `A	reports/gate_b_real_decision_intake_2026-05-23/gate_b_real_decision_intake_summary.csv`
  - `A	scripts/run_gate_b_real_decision_intake.py`
  - `A	src/reports/gate_b_decision_intake.py`
  - `A	tests/test_gate_b_decision_intake.py`

### 148. `1f36269` - chore(audit): close gate b with human decisions (#47)

- Full SHA: `1f36269f5dec506a4dea3f2840900b602f68388d`
- Date: `2026-05-23T05:25:15+01:00`
- Author: `Akir Oussama`
- Shortstat: 50 files changed, 2222 insertions(+)
- Body:

```text
Add human-attested evidence for GB-004 through GB-008, apply the final real decisions, and rerun Gate B validation.

Result:
- intake ready_for_closeout_application
- closeout 8 closed / 0 open / 0 P0 open
- Gate B validation passed_ready_for_gate_c_dry_run
- outputs remain non-citable before Gate C

Validation:
- evidence hashes verified against local files
- uv run ruff check .
- uv run pytest -q
- git diff --check
```
- Files changed:
  - `A	docs/commits/2026-05-23_gate_b_final_human_closeout.md`
  - `A	docs/research/2026-05-23_gate_b_final_human_closeout.md`
  - `A	reports/gate_b_evidence_2026-05-23/GB-004_denominator_policy.md`
  - `A	reports/gate_b_evidence_2026-05-23/GB-005_horizon_policy.md`
  - `A	reports/gate_b_evidence_2026-05-23/GB-006_seizeit2_scope_policy.md`
  - `A	reports/gate_b_evidence_2026-05-23/GB-007_sph5_sop360_source_review_policy.md`
  - `A	reports/gate_b_evidence_2026-05-23/GB-008_negative_readiness_policy.md`
  - `A	reports/gate_b_final_human_closeout_2026-05-23/closeout/gate_b_closeout_ledger.csv`
  - `A	reports/gate_b_final_human_closeout_2026-05-23/closeout/gate_b_closeout_ledger.json`
  - `A	reports/gate_b_final_human_closeout_2026-05-23/closeout/gate_b_closeout_ledger.md`
  - `A	reports/gate_b_final_human_closeout_2026-05-23/closeout/gate_b_closeout_manifest.json`
  - `A	reports/gate_b_final_human_closeout_2026-05-23/closeout/gate_b_closeout_summary.csv`
  - `A	reports/gate_b_final_human_closeout_2026-05-23/gate_b_real_decisions_2026-05-23.csv`
  - `A	reports/gate_b_final_human_closeout_2026-05-23/intake/gate_b_real_decision_intake.json`
  - `A	reports/gate_b_final_human_closeout_2026-05-23/intake/gate_b_real_decision_intake.md`
  - `A	reports/gate_b_final_human_closeout_2026-05-23/intake/gate_b_real_decision_intake_manifest.json`
  - `A	reports/gate_b_final_human_closeout_2026-05-23/intake/gate_b_real_decision_intake_rows.csv`
  - `A	reports/gate_b_final_human_closeout_2026-05-23/intake/gate_b_real_decision_intake_summary.csv`
  - `A	reports/gate_b_final_human_closeout_2026-05-23/real_closeout/gate_b_real_closeout.json`
  - `A	reports/gate_b_final_human_closeout_2026-05-23/real_closeout/gate_b_real_closeout.md`
  - `A	reports/gate_b_final_human_closeout_2026-05-23/real_closeout/gate_b_real_closeout_manifest.json`
  - `A	reports/gate_b_final_human_closeout_2026-05-23/real_closeout/gate_b_real_closeout_readiness.csv`
  - `A	reports/gate_b_final_human_closeout_2026-05-23/real_closeout/gate_b_real_closeout_required_decisions_template.csv`
  - `A	reports/gate_b_final_human_closeout_2026-05-23/real_closeout/gate_b_real_closeout_summary.csv`
  - `A	reports/gate_b_final_human_closeout_2026-05-23/validation/gate_b_validation_manifest.json`
  - `A	reports/gate_b_final_human_closeout_2026-05-23/validation/gate_b_validation_matrix.csv`
  - `A	reports/gate_b_final_human_closeout_2026-05-23/validation/gate_b_validation_rerun.json`
  - `A	reports/gate_b_final_human_closeout_2026-05-23/validation/gate_b_validation_rerun.md`
  - `A	reports/gate_b_final_human_closeout_2026-05-23/validation/gate_b_validation_summary.csv`
  - `A	reports/gate_b_final_human_closeout_2026-05-23/validation_guardrails/gate_bc_action_checklist.csv`
  - `A	reports/gate_b_final_human_closeout_2026-05-23/validation_guardrails/gate_bc_action_checklist.json`
  - `A	reports/gate_b_final_human_closeout_2026-05-23/validation_guardrails/gate_bc_action_checklist.md`
  - `A	reports/gate_b_final_human_closeout_2026-05-23/validation_guardrails/gate_bc_action_summary.csv`
  - `A	reports/gate_b_final_human_closeout_2026-05-23/validation_guardrails/inputs/msg_event_clusters.csv`
  - `A	reports/gate_b_final_human_closeout_2026-05-23/validation_guardrails/inputs/msg_event_coverage.csv`
  - `A	reports/gate_b_final_human_closeout_2026-05-23/validation_guardrails/inputs/msg_horizon_viability.csv`
  - `A	reports/gate_b_final_human_closeout_2026-05-23/validation_guardrails/inputs/seizeit2_local_count_summary.csv`
  - `A	reports/gate_b_final_human_closeout_2026-05-23/validation_guardrails/inputs/seizeit2_local_track.csv`
  - `A	reports/gate_b_final_human_closeout_2026-05-23/validation_guardrails/msg_gap_horizon_triage.csv`
  - `A	reports/gate_b_final_human_closeout_2026-05-23/validation_guardrails/msg_gap_patient_triage.csv`
  - `A	reports/gate_b_final_human_closeout_2026-05-23/validation_guardrails/msg_gap_summary.csv`
  - `A	reports/gate_b_final_human_closeout_2026-05-23/validation_guardrails/msg_gap_triage_manifest.csv`
  - `A	reports/gate_b_final_human_closeout_2026-05-23/validation_guardrails/msg_gap_triage_report.json`
  - `A	reports/gate_b_final_human_closeout_2026-05-23/validation_guardrails/msg_gap_triage_report.md`
  - `A	reports/gate_b_final_human_closeout_2026-05-23/validation_guardrails/seizeit2_cohort_readiness_blockers.csv`
  - `A	reports/gate_b_final_human_closeout_2026-05-23/validation_guardrails/seizeit2_cohort_readiness_manifest.csv`
  - `A	reports/gate_b_final_human_closeout_2026-05-23/validation_guardrails/seizeit2_cohort_readiness_report.json`
  - `A	reports/gate_b_final_human_closeout_2026-05-23/validation_guardrails/seizeit2_cohort_readiness_report.md`
  - `A	reports/gate_b_final_human_closeout_2026-05-23/validation_guardrails/seizeit2_cohort_readiness_summary.csv`
  - `A	reports/gate_b_final_human_closeout_2026-05-23/validation_guardrails/seizeit2_cohort_readiness_warnings.csv`

### 149. `06e9f65` - chore(audit): add gate c dry-run freeze decision

- Full SHA: `06e9f65ff14f0342d822783f518a62cef69fb5f5`
- Date: `2026-05-23T05:49:33+01:00`
- Author: `Akir Oussama`
- Shortstat: 9 files changed, 367 insertions(+), 5 deletions(-)
- Body:

```text
Gate C dry-run executed after Gate B pass.

Records an explicit blocked freeze decision because frozen events, labels, splits, and DOI/preregistration are not yet present. Updates dry-run next actions so the report reflects a passed Gate B state.
```
- Files changed:
  - `A	docs/commits/2026-05-23_gate_c_dry_run_freeze.md`
  - `A	docs/research/2026-05-23_gate_c_dry_run_freeze.md`
  - `A	reports/gate_c_dry_run_freeze_2026-05-23/freeze_decision.md`
  - `A	reports/gate_c_dry_run_freeze_2026-05-23/gate_c_artifact_summary.csv`
  - `A	reports/gate_c_dry_run_freeze_2026-05-23/gate_c_dry_run.json`
  - `A	reports/gate_c_dry_run_freeze_2026-05-23/gate_c_dry_run.md`
  - `A	reports/gate_c_dry_run_freeze_2026-05-23/gate_c_prefreeze_registry.json`
  - `M	src/reports/gate_c_dry_run.py`
  - `M	tests/test_gate_c_dry_run.py`

### 150. `7b2bfde` - feat(audit): add gate c freeze package harness

- Full SHA: `7b2bfde688caee3e37f181cf5c95a8c8e23eef11`
- Date: `2026-05-23T06:21:18+01:00`
- Author: `Akir Oussama`
- Shortstat: 5 files changed, 807 insertions(+)
- Body:

```text
Add an executable Gate C freeze package harness for real events, labels, and splits artifacts.

The harness validates table contracts, split alignment, DOI/preregistration, frozen registry status, and dry-run readiness before writing citable Gate C package outputs.
```
- Files changed:
  - `A	docs/commits/2026-05-23_gate_c_freeze_harness.md`
  - `A	docs/research/2026-05-23_gate_c_freeze_harness.md`
  - `A	scripts/build_gate_c_freeze_package.py`
  - `A	src/artifacts/gate_c_freeze_package.py`
  - `A	tests/test_gate_c_freeze_package.py`

### 151. `187215e` - chore(audit): add gate c input discovery

- Full SHA: `187215e88d58527915ac8572a554abf6ea9786b6`
- Date: `2026-05-23T06:31:27+01:00`
- Author: `Akir Oussama`
- Shortstat: 8 files changed, 670 insertions(+)
- Body:

```text
Add a local scanner for Gate C freeze input candidates and record the current repository scan.

The scan confirms that current local data/reports do not contain role-ready events, labels, or splits artifacts for a citable Gate C freeze.
```
- Files changed:
  - `A	docs/commits/2026-05-23_gate_c_input_discovery.md`
  - `A	docs/research/2026-05-23_gate_c_input_discovery.md`
  - `A	reports/gate_c_input_discovery_2026-05-23/gate_c_input_candidates.csv`
  - `A	reports/gate_c_input_discovery_2026-05-23/gate_c_input_discovery.json`
  - `A	reports/gate_c_input_discovery_2026-05-23/gate_c_input_discovery.md`
  - `A	scripts/discover_gate_c_inputs.py`
  - `A	src/artifacts/gate_c_input_discovery.py`
  - `A	tests/test_gate_c_input_discovery.py`

### 152. `d789fb7` - feat(audit): add gate c input materialization

- Full SHA: `d789fb75327d7e71d43d7f6ba5fcf6257cc280b8`
- Date: `2026-05-23T08:17:41+01:00`
- Author: `Akir Oussama`
- Shortstat: 5 files changed, 659 insertions(+)
- Body:

```text
Add an executable materialization harness that converts source recordings and events into Gate C events, labels, and splits artifacts.

The harness reuses fixed-window generation, SPH/SOP labeling, leakage-aware splitting, and Gate C freeze input validation. Outputs remain non-citable until processed by the Gate C freeze package with DOI/preregistration.
```
- Files changed:
  - `A	docs/commits/2026-05-23_gate_c_input_materialization.md`
  - `A	docs/research/2026-05-23_gate_c_input_materialization.md`
  - `A	scripts/materialize_gate_c_inputs.py`
  - `A	src/artifacts/gate_c_materialize_inputs.py`
  - `A	tests/test_gate_c_materialize_inputs.py`

### 153. `fa63998` - chore(audit): add gate c source discovery

- Full SHA: `fa63998cf4f1b62d212443bbdc7b9440f3bc03e3`
- Date: `2026-05-23T08:27:59+01:00`
- Author: `Akir Oussama`
- Shortstat: 8 files changed, 596 insertions(+)
- Body:

```text
Add a scanner for source recordings/events tables required by Gate C materialization.

The committed local scan confirms the repository currently has no source-ready recordings or events tables under data/reports, so Gate C materialization remains blocked on source recovery.
```
- Files changed:
  - `A	docs/commits/2026-05-23_gate_c_source_discovery.md`
  - `A	docs/research/2026-05-23_gate_c_source_discovery.md`
  - `A	reports/gate_c_source_discovery_2026-05-23/gate_c_source_candidates.csv`
  - `A	reports/gate_c_source_discovery_2026-05-23/gate_c_source_discovery.json`
  - `A	reports/gate_c_source_discovery_2026-05-23/gate_c_source_discovery.md`
  - `A	scripts/discover_gate_c_sources.py`
  - `A	src/artifacts/gate_c_source_discovery.py`
  - `A	tests/test_gate_c_source_discovery.py`

### 154. `391bca3` - Freeze MSG Gate C source artifacts

- Full SHA: `391bca3a05d01298d31df1d165a392c15c7a2bef`
- Date: `2026-05-23T10:16:44+01:00`
- Author: `Akir Oussama`
- Shortstat: 20 files changed, 103320 insertions(+)
- Body:

```text
Freeze MSG Gate C source artifacts

- recover real MSG recordings/events from verified Zenodo source files
- materialize SPH60/SOP1440 Gate C events/labels/splits artifacts
- add registry-backed freeze package, discovery reports, and trace docs

Validation:
- full local pytest passed
- GitHub Actions pytest passed for PR #53
- Gate C registry hash verification passed
```
- Files changed:
  - `A	docs/commits/2026-05-23_gate_c_msg_source_recovery_freeze.md`
  - `A	docs/research/2026-05-23_gate_c_msg_source_recovery_freeze.md`
  - `A	reports/gate_c_msg_freeze_2026-05-23/artifacts/events.csv`
  - `A	reports/gate_c_msg_freeze_2026-05-23/artifacts/gate_c_input_materialization_manifest.json`
  - `A	reports/gate_c_msg_freeze_2026-05-23/artifacts/labels.csv`
  - `A	reports/gate_c_msg_freeze_2026-05-23/artifacts/leakage_audit.txt`
  - `A	reports/gate_c_msg_freeze_2026-05-23/artifacts/splits.csv`
  - `A	reports/gate_c_msg_freeze_2026-05-23/gate_c_artifact_summary.csv`
  - `A	reports/gate_c_msg_freeze_2026-05-23/gate_c_dry_run.json`
  - `A	reports/gate_c_msg_freeze_2026-05-23/gate_c_dry_run.md`
  - `A	reports/gate_c_msg_freeze_2026-05-23/gate_c_freeze_manifest.json`
  - `A	reports/gate_c_msg_freeze_2026-05-23/gate_c_registry.json`
  - `A	reports/gate_c_source_recovery_2026-05-23/artifacts/events.csv`
  - `A	reports/gate_c_source_recovery_2026-05-23/artifacts/recordings.csv`
  - `A	reports/gate_c_source_recovery_2026-05-23/input_discovery/gate_c_input_candidates.csv`
  - `A	reports/gate_c_source_recovery_2026-05-23/input_discovery/gate_c_input_discovery.json`
  - `A	reports/gate_c_source_recovery_2026-05-23/input_discovery/gate_c_input_discovery.md`
  - `A	reports/gate_c_source_recovery_2026-05-23/source_discovery/gate_c_source_candidates.csv`
  - `A	reports/gate_c_source_recovery_2026-05-23/source_discovery/gate_c_source_discovery.json`
  - `A	reports/gate_c_source_recovery_2026-05-23/source_discovery/gate_c_source_discovery.md`

### 155. `085323b` - Run Gate C frozen null benchmark

- Full SHA: `085323bb8854a41d4fecd005b5111f0125bd9fc2`
- Date: `2026-05-23T15:42:05+02:00`
- Author: `Oussama Akir`
- Shortstat: 56 files changed, 3478 insertions(+), 4 deletions(-)
- Body: none
- Files changed:
  - `A	docs/commits/2026-05-23_gate_c_frozen_null_benchmark.md`
  - `A	docs/research/2026-05-23_gate_c_frozen_null_benchmark.md`
  - `A	reports/gate_c_frozen_benchmark_2026-05-23/calibration/cycle_preserving_random/calibration_bootstrap.csv`
  - `A	reports/gate_c_frozen_benchmark_2026-05-23/calibration/cycle_preserving_random/calibration_reliability.csv`
  - `A	reports/gate_c_frozen_benchmark_2026-05-23/calibration/cycle_preserving_random/calibration_report.json`
  - `A	reports/gate_c_frozen_benchmark_2026-05-23/calibration/cycle_preserving_random/calibration_report.md`
  - `A	reports/gate_c_frozen_benchmark_2026-05-23/calibration/cycle_preserving_random/calibration_skill.csv`
  - `A	reports/gate_c_frozen_benchmark_2026-05-23/calibration/cycle_preserving_random/calibration_summary.csv`
  - `A	reports/gate_c_frozen_benchmark_2026-05-23/calibration/patient_prior/calibration_bootstrap.csv`
  - `A	reports/gate_c_frozen_benchmark_2026-05-23/calibration/patient_prior/calibration_reliability.csv`
  - `A	reports/gate_c_frozen_benchmark_2026-05-23/calibration/patient_prior/calibration_report.json`
  - `A	reports/gate_c_frozen_benchmark_2026-05-23/calibration/patient_prior/calibration_report.md`
  - `A	reports/gate_c_frozen_benchmark_2026-05-23/calibration/patient_prior/calibration_skill.csv`
  - `A	reports/gate_c_frozen_benchmark_2026-05-23/calibration/patient_prior/calibration_summary.csv`
  - `A	reports/gate_c_frozen_benchmark_2026-05-23/calibration/rate_matched_random/calibration_bootstrap.csv`
  - `A	reports/gate_c_frozen_benchmark_2026-05-23/calibration/rate_matched_random/calibration_reliability.csv`
  - `A	reports/gate_c_frozen_benchmark_2026-05-23/calibration/rate_matched_random/calibration_report.json`
  - `A	reports/gate_c_frozen_benchmark_2026-05-23/calibration/rate_matched_random/calibration_report.md`
  - `A	reports/gate_c_frozen_benchmark_2026-05-23/calibration/rate_matched_random/calibration_skill.csv`
  - `A	reports/gate_c_frozen_benchmark_2026-05-23/calibration/rate_matched_random/calibration_summary.csv`
  - `A	reports/gate_c_frozen_benchmark_2026-05-23/calibration/split_prevalence_prior/calibration_bootstrap.csv`
  - `A	reports/gate_c_frozen_benchmark_2026-05-23/calibration/split_prevalence_prior/calibration_reliability.csv`
  - `A	reports/gate_c_frozen_benchmark_2026-05-23/calibration/split_prevalence_prior/calibration_report.json`
  - `A	reports/gate_c_frozen_benchmark_2026-05-23/calibration/split_prevalence_prior/calibration_report.md`
  - `A	reports/gate_c_frozen_benchmark_2026-05-23/calibration/split_prevalence_prior/calibration_skill.csv`
  - `A	reports/gate_c_frozen_benchmark_2026-05-23/calibration/split_prevalence_prior/calibration_summary.csv`
  - `A	reports/gate_c_frozen_benchmark_2026-05-23/calibration_bootstrap.csv`
  - `A	reports/gate_c_frozen_benchmark_2026-05-23/calibration_reliability.csv`
  - `A	reports/gate_c_frozen_benchmark_2026-05-23/calibration_skill.csv`
  - `A	reports/gate_c_frozen_benchmark_2026-05-23/calibration_summary.csv`
  - `A	reports/gate_c_frozen_benchmark_2026-05-23/forecastability_atlas.csv`
  - `A	reports/gate_c_frozen_benchmark_2026-05-23/forecastability_atlas.md`
  - `A	reports/gate_c_frozen_benchmark_2026-05-23/frozen_benchmark_audit.md`
  - `A	reports/gate_c_frozen_benchmark_2026-05-23/frozen_benchmark_manifest.json`
  - `A	reports/gate_c_frozen_benchmark_2026-05-23/leaderboard/cycle_preserving_random.csv`
  - `A	reports/gate_c_frozen_benchmark_2026-05-23/leaderboard/cycle_preserving_random.json`
  - `A	reports/gate_c_frozen_benchmark_2026-05-23/leaderboard/cycle_preserving_random.md`
  - `A	reports/gate_c_frozen_benchmark_2026-05-23/leaderboard/patient_prior.csv`
  - `A	reports/gate_c_frozen_benchmark_2026-05-23/leaderboard/patient_prior.json`
  - `A	reports/gate_c_frozen_benchmark_2026-05-23/leaderboard/patient_prior.md`
  - `A	reports/gate_c_frozen_benchmark_2026-05-23/leaderboard/rate_matched_random.csv`
  - `A	reports/gate_c_frozen_benchmark_2026-05-23/leaderboard/rate_matched_random.json`
  - `A	reports/gate_c_frozen_benchmark_2026-05-23/leaderboard/rate_matched_random.md`
  - `A	reports/gate_c_frozen_benchmark_2026-05-23/leaderboard/split_prevalence_prior.csv`
  - `A	reports/gate_c_frozen_benchmark_2026-05-23/leaderboard/split_prevalence_prior.json`
  - `A	reports/gate_c_frozen_benchmark_2026-05-23/leaderboard/split_prevalence_prior.md`
  - `A	reports/gate_c_frozen_benchmark_2026-05-23/leaderboard_rows.csv`
  - `A	reports/gate_c_frozen_benchmark_2026-05-23/leaderboard_rows_with_ci.csv`
  - `A	reports/gate_c_frozen_benchmark_2026-05-23/predictions/cycle_preserving_random.parquet`
  - `A	reports/gate_c_frozen_benchmark_2026-05-23/predictions/patient_prior.parquet`
  - `A	reports/gate_c_frozen_benchmark_2026-05-23/predictions/rate_matched_random.parquet`
  - `A	reports/gate_c_frozen_benchmark_2026-05-23/predictions/split_prevalence_prior.parquet`
  - `M	scripts/make_leaderboard_row.py`
  - `A	scripts/run_gate_c_frozen_benchmark.py`
  - `A	src/artifacts/gate_c_frozen_benchmark.py`
  - `A	tests/test_gate_c_frozen_benchmark.py`

### 156. `4114cbc` - Merge PR #54: Run Gate C frozen null benchmark

- Full SHA: `4114cbc66383314f4a7276399c5bd32779b8e71f`
- Date: `2026-05-23T14:45:59+01:00`
- Author: `Akir Oussama`
- Shortstat: 56 files changed, 3478 insertions(+), 4 deletions(-)
- Body:

```text
Frozen-only Gate C benchmark rerun harness with first MSG null baselines, leaderboard rows, calibration reports, forecastability atlas outputs, and audit documentation.
```
- Files changed: none reported

### 157. `42a0806` - Document final delivery package

- Full SHA: `42a08068cb0717b3a3e4e4f1e14e173d00cd96a8`
- Date: `2026-05-23T16:12:24+02:00`
- Author: `Oussama Akir`
- Shortstat: 4 files changed, 705 insertions(+)
- Body: none
- Files changed:
  - `A	docs/commits/2026-05-23_final_delivery_package.md`
  - `A	docs/delivery/2026-05-23_email_to_mme_manel.md`
  - `A	docs/delivery/2026-05-23_final_delivery_brief.md`
  - `A	docs/delivery/2026-05-23_publication_strategy_and_sota.md`

### 158. `bc2695f` - Merge PR #55: Document final delivery package

- Full SHA: `bc2695ff04da73d9886d8cbc21bbc7df40c0a77c`
- Date: `2026-05-23T15:16:17+01:00`
- Author: `Akir Oussama`
- Shortstat: 4 files changed, 705 insertions(+)
- Body:

```text
Add supervisor delivery brief, publication/SOTA strategy, email draft, and delivery trace documentation.
```
- Files changed: none reported

### 159. `d189bf7` - Establish EpiBench certification standard and evidence packages

- Full SHA: `d189bf7d128456fe333137aa59f7f744f3d082b0`
- Date: `2026-05-24T15:17:10+02:00`
- Author: `Akir Oussama`
- Shortstat: 149 files changed, 15585 insertions(+)
- Body:

```text
Add normative EpiBench v1 draft schemas, YAML spec, CLI certification flow, claim gates, conformance suite, submission-readiness gate, SzCORE bridge, inter-reviewer checks, and worked evidence packages.

Add generated MSG Gate C forecasting package and CHB-MIT patient-independent null-baseline package with claim reports, Q1 paper strategy docs, governance docs, and BSEBench external reproduction runner scaffold.

Validation: pytest tests/test_epibench_standard.py -q passed with 17 tests; ruff check passed; EpiBench conformance suite passed; submission readiness passes for CHB-MIT plus MSG Gate C.
```
- Files changed:
  - `A	.github/ISSUE_TEMPLATE/epibench_dataset_proposal.md`
  - `A	.github/ISSUE_TEMPLATE/epibench_result_bundle_submission.md`
  - `A	.github/workflows/bsebench_reproduction_kit.yml`
  - `A	CHANGELOG.md`
  - `A	REPRODUCTION_KIT_README.md`
  - `A	REPRODUCTION_KIT_REPORT.md`
  - `A	bsebench-runner/bundles/bundle_calce_a123_lfp_dst_v1.0/reference_manifest.json`
  - `A	bsebench-runner/bundles/bundle_calce_a123_lfp_dst_v1.0/reproduction.yaml`
  - `A	bsebench-runner/bundles/smoke_bit_exact_v1/reference_manifest.json`
  - `A	bsebench-runner/bundles/smoke_bit_exact_v1/reproduction.yaml`
  - `A	bsebench-runner/docker/Dockerfile`
  - `A	bsebench-runner/docker/scripts/build_image.sh`
  - `A	bsebench-runner/docker/scripts/entrypoint.sh`
  - `A	bsebench-runner/docker/scripts/install_editable_repos.py`
  - `A	bsebench-runner/docker/scripts/reproduce_bundle.sh`
  - `A	bsebench-runner/repositories.example.yaml`
  - `A	bsebench-runner/runner/bsebench.py`
  - `A	configs/epibench/conformance_suite_v1.yaml`
  - `A	configs/epibench/epibench_v1.yaml`
  - `A	configs/epibench/sota_registry_v1.yaml`
  - `A	configs/epibench/submission_readiness_gate_v1.yaml`
  - `A	docs/EPIBENCH_CERTIFICATION_SOP.md`
  - `A	docs/EPIBENCH_IMPLEMENTATION_INDEX.md`
  - `A	docs/EPIBENCH_PHASE1_ADJUDICATION_EXAMPLES.md`
  - `A	docs/EPIBENCH_PHASE1_DETAILED_PLAN.md`
  - `A	docs/EPIBENCH_PHASE1_REVIEW_CHECKLIST.md`
  - `A	docs/EPIBENCH_PHASE2_SINGLE_SOURCE_OF_TRUTH.md`
  - `A	docs/EPIBENCH_PHASE3_CERTIFICATION_STANDARD.md`
  - `A	docs/EPIBENCH_PHASE4_REFERENCE_IMPLEMENTATION.md`
  - `A	docs/EPIBENCH_PHASE5_PILOT_EVIDENCE_PACKAGES.md`
  - `A	docs/EPIBENCH_PHASE6_Q1_PAPER_STRATEGY.md`
  - `A	docs/EPIBENCH_PHASE7_GOVERNANCE_ADOPTION.md`
  - `A	docs/EPIBENCH_PROTOCOL.md`
  - `A	docs/EPIBENCH_PROTOCOL_CONFORMANCE_SUITE.md`
  - `A	docs/EPIBENCH_Q1_REJECTION_AVOIDANCE_FEATURES.md`
  - `A	docs/EPIBENCH_Q1_STANDARD_ROADMAP.md`
  - `A	docs/EPIBENCH_RELEASE_CHECKLIST.md`
  - `A	docs/EPIBENCH_SPEC_V1.md`
  - `A	docs/EPIBENCH_VERSIONING_POLICY.md`
  - `A	docs/paper/EPIBENCH_FIGURE_TABLE_BLUEPRINT.md`
  - `A	docs/paper/EPIBENCH_INTER_REVIEWER_PROTOCOL.md`
  - `A	docs/paper/EPIBENCH_NPJ_COVER_LETTER_DRAFT.md`
  - `A	docs/paper/EPIBENCH_NPJ_DIGITAL_MEDICINE_DRAFT.md`
  - `A	docs/paper/EPIBENCH_REAL_EVIDENCE_PACKAGE_WORKORDER.md`
  - `A	docs/paper/EPIBENCH_REVIEWER_ATTACK_DEFENSE_MATRIX.md`
  - `A	docs/paper/EPIBENCH_SUBMISSION_READINESS_MATRIX.md`
  - `A	docs/paper/EPIBENCH_SUPPLEMENTARY_METHODS_DRAFT.md`
  - `A	docs/paper/EPIBENCH_SZCORE_COMPATIBILITY_BRIDGE.md`
  - `A	docs/paper/EPIBENCH_TO_085_READINESS_SPRINT.md`
  - `A	examples/epibench/chbmit_patient_independent_d/dataset_card.yaml`
  - `A	examples/epibench/chbmit_patient_independent_d/failure_trace.yaml`
  - `A	examples/epibench/chbmit_patient_independent_d/result_bundle.yaml`
  - `A	examples/epibench/chbmit_patient_independent_d/split_manifest.yaml`
  - `A	examples/epibench/embedded_no_hardware_demo/failure_trace.yaml`
  - `A	examples/epibench/embedded_no_hardware_demo/result_bundle.yaml`
  - `A	examples/epibench/embedded_no_hardware_demo/split_manifest.yaml`
  - `A	examples/epibench/external_requested_e4_demo/failure_trace.yaml`
  - `A	examples/epibench/external_requested_e4_demo/result_bundle.yaml`
  - `A	examples/epibench/external_validation_demo/failure_trace.yaml`
  - `A	examples/epibench/external_validation_demo/result_bundle.yaml`
  - `A	examples/epibench/external_validation_demo/split_manifest.yaml`
  - `A	examples/epibench/failure_leakage/failure_trace.yaml`
  - `A	examples/epibench/failure_leakage/result_bundle.yaml`
  - `A	examples/epibench/failure_leakage/split_manifest.yaml`
  - `A	examples/epibench/inter_reviewer_reviews.yaml`
  - `A	examples/epibench/msg_gate_c_frozen_f/dataset_card.yaml`
  - `A	examples/epibench/msg_gate_c_frozen_f/failure_trace.yaml`
  - `A	examples/epibench/msg_gate_c_frozen_f/result_bundle.yaml`
  - `A	examples/epibench/msg_gate_c_frozen_f/split_manifest.yaml`
  - `A	examples/epibench/msg_preliminary_f/dataset_card.yaml`
  - `A	examples/epibench/msg_preliminary_f/failure_trace.yaml`
  - `A	examples/epibench/msg_preliminary_f/result_bundle.yaml`
  - `A	examples/epibench/msg_preliminary_f/split_manifest.yaml`
  - `A	examples/epibench/patient_dependent_demo/failure_trace.yaml`
  - `A	examples/epibench/patient_dependent_demo/result_bundle.yaml`
  - `A	examples/epibench/patient_dependent_demo/split_manifest.yaml`
  - `A	examples/epibench/pilot_t1_eeg/dataset_card.yaml`
  - `A	examples/epibench/pilot_t1_eeg/failure_trace.yaml`
  - `A	examples/epibench/pilot_t1_eeg/result_bundle.yaml`
  - `A	examples/epibench/pilot_t1_eeg/split_manifest.yaml`
  - `A	examples/epibench/prospective_e4_demo/failure_trace.yaml`
  - `A	examples/epibench/prospective_e4_demo/result_bundle.yaml`
  - `A	examples/epibench/prospective_e4_demo/split_manifest.yaml`
  - `A	examples/epibench/seizeit2_preliminary_f/dataset_card.yaml`
  - `A	examples/epibench/seizeit2_preliminary_f/failure_trace.yaml`
  - `A	examples/epibench/seizeit2_preliminary_f/result_bundle.yaml`
  - `A	examples/epibench/seizeit2_preliminary_f/split_manifest.yaml`
  - `A	examples/epibench/szcore_bridge_demo/README.md`
  - `A	examples/epibench/szcore_bridge_demo/import_failure_trace.yaml`
  - `A	examples/epibench/szcore_bridge_demo/imported_result_bundle.yaml`
  - `A	examples/epibench/szcore_bridge_demo/result_bundle.yaml`
  - `A	examples/epibench/szcore_bridge_demo/szcore_event_metrics.yaml`
  - `A	outreach/email_template.md`
  - `M	pyproject.toml`
  - `A	reports/bsebench_runner_smoke/smoke_bit_exact_v1/outputs/result.txt`
  - `A	reports/bsebench_runner_smoke/smoke_bit_exact_v1/reproduction_report.json`
  - `A	reports/chbmit_patient_independent_null_metrics.json`
  - `A	reports/epibench_chbmit_e2pi_package_report.md`
  - `A	reports/epibench_chbmit_patient_independent_claim.json`
  - `A	reports/epibench_chbmit_patient_independent_claim.md`
  - `A	reports/epibench_conformance_result.json`
  - `A	reports/epibench_embedded_no_hardware_claim.json`
  - `A	reports/epibench_embedded_no_hardware_claim.md`
  - `A	reports/epibench_external_requested_e4_claim.json`
  - `A	reports/epibench_external_requested_e4_claim.md`
  - `A	reports/epibench_external_validation_claim.json`
  - `A	reports/epibench_external_validation_claim.md`
  - `A	reports/epibench_inter_reviewer_report.json`
  - `A	reports/epibench_leakage_claim.json`
  - `A	reports/epibench_leakage_claim.md`
  - `A	reports/epibench_local_data_inventory_2026-05-24.md`
  - `A	reports/epibench_msg_gate_c_frozen_claim.json`
  - `A	reports/epibench_msg_gate_c_frozen_claim.md`
  - `A	reports/epibench_msg_preliminary_claim.json`
  - `A	reports/epibench_msg_preliminary_claim.md`
  - `A	reports/epibench_patient_dependent_claim.json`
  - `A	reports/epibench_patient_dependent_claim.md`
  - `A	reports/epibench_pilot_claim.json`
  - `A	reports/epibench_pilot_claim.md`
  - `A	reports/epibench_prospective_e4_claim.json`
  - `A	reports/epibench_prospective_e4_claim.md`
  - `A	reports/epibench_real_evidence_gap_report.md`
  - `A	reports/epibench_seizeit2_preliminary_claim.json`
  - `A	reports/epibench_seizeit2_preliminary_claim.md`
  - `A	reports/epibench_submission_readiness_report.json`
  - `A	reports/epibench_submission_readiness_result.json`
  - `A	reports/epibench_szcore_bridge_claim.json`
  - `A	reports/epibench_szcore_bridge_claim.md`
  - `A	reports/epibench_szcore_import_claim.json`
  - `A	reports/epibench_szcore_import_claim.md`
  - `A	schemas/epibench/claim_eligibility.schema.json`
  - `A	schemas/epibench/dataset_evidence_card.schema.json`
  - `A	schemas/epibench/failure_trace.schema.json`
  - `A	schemas/epibench/result_bundle.schema.json`
  - `A	schemas/epibench/sota_registry.schema.json`
  - `A	schemas/epibench/split_manifest.schema.json`
  - `A	scripts/epibench.py`
  - `A	scripts/epibench_build_chbmit_package.py`
  - `A	scripts/epibench_build_msg_gate_c_package.py`
  - `A	src/epibench/__init__.py`
  - `A	src/epibench/certification.py`
  - `A	src/epibench/cli.py`
  - `A	src/epibench/inter_reviewer.py`
  - `A	src/epibench/scoring.py`
  - `A	src/epibench/spec.py`
  - `A	src/epibench/submission_readiness.py`
  - `A	src/epibench/szcore_bridge.py`
  - `A	src/epibench/validation.py`
  - `A	tests/test_epibench_standard.py`

### 160. `16759f0` - Add reproducible EpiBench evidence panels

- Full SHA: `16759f03de5527511295e46f046c9e8cf9346cfe`
- Date: `2026-05-24T15:21:24+02:00`
- Author: `Akir Oussama`
- Shortstat: 11 files changed, 674 insertions(+)
- Body:

```text
Generate manuscript-ready panels from certified result bundles: naive score leaderboard, claim-gated leaderboard, rank comparison, claim waterfall, failure matrix, score-axis matrix, and audit README.

The panels make the core anti-leaderboard result explicit: the highest naive Epi-Score is claim-limited to E1 by leakage, while CHB-MIT demonstrates an E2-PI evidence structure with poor null-baseline performance.

Validation: python scripts/epibench_build_evidence_panels.py; pytest tests/test_epibench_standard.py -q passed with 18 tests; ruff check passed.
```
- Files changed:
  - `M	docs/EPIBENCH_IMPLEMENTATION_INDEX.md`
  - `A	reports/epibench_evidence_panels/README.md`
  - `A	reports/epibench_evidence_panels/bundle_summary.csv`
  - `A	reports/epibench_evidence_panels/claim_gate_waterfall.csv`
  - `A	reports/epibench_evidence_panels/claim_gated_leaderboard.csv`
  - `A	reports/epibench_evidence_panels/failure_matrix.csv`
  - `A	reports/epibench_evidence_panels/naive_score_leaderboard.csv`
  - `A	reports/epibench_evidence_panels/rank_comparison.csv`
  - `A	reports/epibench_evidence_panels/score_axis_matrix.csv`
  - `A	scripts/epibench_build_evidence_panels.py`
  - `M	tests/test_epibench_standard.py`

### 161. `a17dc8b` - Add EpiBench protocol coverage audit panels

- Full SHA: `a17dc8b8d2090e3eb2645b48a8622d947f80a452`
- Date: `2026-05-24T15:24:18+02:00`
- Author: `Akir Oussama`
- Shortstat: 8 files changed, 448 insertions(+)
- Body:

```text
Generate dataset evidence and protocol coverage panels from the current certified artefacts: MTS/DSI evidence matrix, rubric coverage, use-case coverage, and explicit coverage gaps.

The audit documents that current examples cover tracks D/E/F and final claims E1 through E4, while preserving major gaps such as missing early-warning track W and weak preliminary MTS evidence for MSG/SeizeIT2.

Validation: python scripts/epibench_build_coverage_audit.py; pytest tests/test_epibench_standard.py -q passed with 19 tests; ruff check passed.
```
- Files changed:
  - `M	docs/EPIBENCH_IMPLEMENTATION_INDEX.md`
  - `A	reports/epibench_coverage_audit/README.md`
  - `A	reports/epibench_coverage_audit/coverage_gaps.csv`
  - `A	reports/epibench_coverage_audit/dataset_evidence_matrix.csv`
  - `A	reports/epibench_coverage_audit/protocol_use_case_coverage.csv`
  - `A	reports/epibench_coverage_audit/rubric_item_coverage.csv`
  - `A	scripts/epibench_build_coverage_audit.py`
  - `M	tests/test_epibench_standard.py`

### 162. `46191b2` - Cover early-warning track with claim-gated examples

- Full SHA: `46191b2310498c907f1996710f604fd808540850`
- Date: `2026-05-24T15:27:15+02:00`
- Author: `Akir Oussama`
- Shortstat: 27 files changed, 574 insertions(+), 56 deletions(-)
- Body:

```text
Add two Track W evidence packages: a valid leave-one-subject-out early-warning example reaching E2-PI and a post-event alarm failure case that keeps a high naive score but downgrades to E1.

Refresh conformance, evidence panels, and coverage audit so the protocol now covers D/E/F/W tracks and exposes POST_EVENT_ALARM as an early-warning-specific failure mode.

Validation: conformance suite passed with 14 cases; pytest tests/test_epibench_standard.py -q passed with 20 tests; ruff check passed.
```
- Files changed:
  - `M	configs/epibench/conformance_suite_v1.yaml`
  - `M	docs/EPIBENCH_IMPLEMENTATION_INDEX.md`
  - `A	examples/epibench/early_warning_post_event_failure_w/failure_trace.yaml`
  - `A	examples/epibench/early_warning_post_event_failure_w/result_bundle.yaml`
  - `A	examples/epibench/early_warning_post_event_failure_w/split_manifest.yaml`
  - `A	examples/epibench/early_warning_valid_w/failure_trace.yaml`
  - `A	examples/epibench/early_warning_valid_w/result_bundle.yaml`
  - `A	examples/epibench/early_warning_valid_w/split_manifest.yaml`
  - `M	reports/epibench_conformance_result.json`
  - `M	reports/epibench_coverage_audit/README.md`
  - `M	reports/epibench_coverage_audit/coverage_gaps.csv`
  - `M	reports/epibench_coverage_audit/dataset_evidence_matrix.csv`
  - `M	reports/epibench_coverage_audit/protocol_use_case_coverage.csv`
  - `M	reports/epibench_coverage_audit/rubric_item_coverage.csv`
  - `A	reports/epibench_early_warning_post_event_failure_claim.json`
  - `A	reports/epibench_early_warning_post_event_failure_claim.md`
  - `A	reports/epibench_early_warning_valid_claim.json`
  - `A	reports/epibench_early_warning_valid_claim.md`
  - `M	reports/epibench_evidence_panels/README.md`
  - `M	reports/epibench_evidence_panels/bundle_summary.csv`
  - `M	reports/epibench_evidence_panels/claim_gate_waterfall.csv`
  - `M	reports/epibench_evidence_panels/claim_gated_leaderboard.csv`
  - `M	reports/epibench_evidence_panels/failure_matrix.csv`
  - `M	reports/epibench_evidence_panels/naive_score_leaderboard.csv`
  - `M	reports/epibench_evidence_panels/rank_comparison.csv`
  - `M	reports/epibench_evidence_panels/score_axis_matrix.csv`
  - `M	tests/test_epibench_standard.py`

### 163. `0da0f36` - Add false-alarm burden failure evidence case

- Full SHA: `0da0f36919c80b8abb7b6a305a5b78ba785ce456`
- Date: `2026-05-24T15:30:43+02:00`
- Author: `Akir Oussama`
- Shortstat: 22 files changed, 312 insertions(+), 29 deletions(-)
- Body:

```text
Add a Track D FAR_EXPLOSION package showing a high-sensitivity detector with 216 false alarms per 24h that is downgraded to E1 despite a strong sensitivity-only profile.

Extend evidence panels with a sensitivity-only leaderboard so the manuscript can show why sensitivity alone overstates seizure-detection evidence.

Refresh conformance, claim reports, coverage audit, and panel outputs. Validation: conformance suite passed with 15 cases; pytest tests/test_epibench_standard.py -q passed with 21 tests; ruff check passed.
```
- Files changed:
  - `M	configs/epibench/conformance_suite_v1.yaml`
  - `M	docs/EPIBENCH_IMPLEMENTATION_INDEX.md`
  - `A	examples/epibench/far_explosion_failure_d/failure_trace.yaml`
  - `A	examples/epibench/far_explosion_failure_d/result_bundle.yaml`
  - `A	examples/epibench/far_explosion_failure_d/split_manifest.yaml`
  - `M	reports/epibench_conformance_result.json`
  - `M	reports/epibench_coverage_audit/README.md`
  - `M	reports/epibench_coverage_audit/dataset_evidence_matrix.csv`
  - `M	reports/epibench_coverage_audit/protocol_use_case_coverage.csv`
  - `M	reports/epibench_coverage_audit/rubric_item_coverage.csv`
  - `M	reports/epibench_evidence_panels/README.md`
  - `M	reports/epibench_evidence_panels/bundle_summary.csv`
  - `M	reports/epibench_evidence_panels/claim_gate_waterfall.csv`
  - `M	reports/epibench_evidence_panels/claim_gated_leaderboard.csv`
  - `M	reports/epibench_evidence_panels/failure_matrix.csv`
  - `M	reports/epibench_evidence_panels/naive_score_leaderboard.csv`
  - `M	reports/epibench_evidence_panels/rank_comparison.csv`
  - `M	reports/epibench_evidence_panels/score_axis_matrix.csv`
  - `A	reports/epibench_far_explosion_claim.json`
  - `A	reports/epibench_far_explosion_claim.md`
  - `M	scripts/epibench_build_evidence_panels.py`
  - `M	tests/test_epibench_standard.py`

### 164. `dcde6e8` - Add overclaim language audit report

- Full SHA: `dcde6e8843501638a64d2aad5c56449c1c26ead9`
- Date: `2026-05-24T15:39:01+02:00`
- Author: `Akir Oussama`
- Shortstat: 5 files changed, 796 insertions(+)
- Body:

```text
Scan EpiBench-facing docs, configs, examples, and reports for clinical/regulatory, SOTA, generalization, and real-time wording that needs explicit evidence boundaries.

Generate bounded-vs-review findings with category and severity summaries so manuscript language risks are visible before Q1 submission rather than hidden in prose.

Validation: python scripts/epibench_overclaim_audit.py; uv run --extra dev pytest tests/test_epibench_standard.py -q; uv run --extra dev ruff check src/epibench tests/test_epibench_standard.py scripts/epibench.py scripts/epibench_build_msg_gate_c_package.py scripts/epibench_build_chbmit_package.py scripts/epibench_build_evidence_panels.py scripts/epibench_build_coverage_audit.py scripts/epibench_overclaim_audit.py.
```
- Files changed:
  - `M	docs/EPIBENCH_IMPLEMENTATION_INDEX.md`
  - `A	reports/epibench_overclaim_audit/README.md`
  - `A	reports/epibench_overclaim_audit/overclaim_findings.csv`
  - `A	scripts/epibench_overclaim_audit.py`
  - `M	tests/test_epibench_standard.py`

### 165. `33f7cc2` - Add Q1 reviewer evidence packet

- Full SHA: `33f7cc281f91e5ec37312cc1625d803e93ef72be`
- Date: `2026-05-24T15:43:40+02:00`
- Author: `Akir Oussama`
- Shortstat: 10 files changed, 535 insertions(+), 4 deletions(-)
- Body:

```text
Generate a reviewer attack matrix from the existing evidence panels, coverage audit, overclaim audit, submission-readiness gate, and inter-reviewer report.

The packet maps each likely Q1 objection to a concrete artefact, quantitative indicator, defense status, and pre-submission action so remaining rejection risks are explicit rather than rhetorical.

Validation: python scripts/epibench_overclaim_audit.py; python scripts/epibench_build_reviewer_packet.py; uv run --extra dev pytest tests/test_epibench_standard.py -q; uv run --extra dev ruff check src/epibench tests/test_epibench_standard.py scripts/epibench.py scripts/epibench_build_msg_gate_c_package.py scripts/epibench_build_chbmit_package.py scripts/epibench_build_evidence_panels.py scripts/epibench_build_coverage_audit.py scripts/epibench_overclaim_audit.py scripts/epibench_build_reviewer_packet.py.
```
- Files changed:
  - `M	docs/EPIBENCH_IMPLEMENTATION_INDEX.md`
  - `M	docs/paper/EPIBENCH_REVIEWER_ATTACK_DEFENSE_MATRIX.md`
  - `M	reports/epibench_overclaim_audit/overclaim_findings.csv`
  - `A	reports/epibench_reviewer_packet/README.md`
  - `A	reports/epibench_reviewer_packet/evidence_index.csv`
  - `A	reports/epibench_reviewer_packet/pre_submission_action_register.csv`
  - `A	reports/epibench_reviewer_packet/reviewer_attack_matrix.csv`
  - `A	scripts/epibench_build_reviewer_packet.py`
  - `M	scripts/epibench_overclaim_audit.py`
  - `M	tests/test_epibench_standard.py`

### 166. `97b6e2e` - Add Epi-Score weight sensitivity panels

- Full SHA: `97b6e2ee05c67e735829404b23fd5beffa84fce3`
- Date: `2026-05-24T15:48:42+02:00`
- Author: `Akir Oussama`
- Shortstat: 14 files changed, 611 insertions(+), 15 deletions(-)
- Body:

```text
Generate preregistered weight perturbation scenarios from the score-axis matrix and compare score-only ranks with claim-gated ranks across every EpiBench bundle.

The panel shows score-only ranks move under plausible weight changes while claim-gated interpretation remains invariant, closing the reviewer attack that Epi-Score weights alone determine the scientific conclusion.

Validation: python scripts/epibench_build_weight_sensitivity.py; python scripts/epibench_overclaim_audit.py; python scripts/epibench_build_reviewer_packet.py; uv run --extra dev pytest tests/test_epibench_standard.py -q; uv run --extra dev ruff check src/epibench tests/test_epibench_standard.py scripts/epibench.py scripts/epibench_build_msg_gate_c_package.py scripts/epibench_build_chbmit_package.py scripts/epibench_build_evidence_panels.py scripts/epibench_build_coverage_audit.py scripts/epibench_overclaim_audit.py scripts/epibench_build_reviewer_packet.py scripts/epibench_build_weight_sensitivity.py.
```
- Files changed:
  - `M	docs/EPIBENCH_IMPLEMENTATION_INDEX.md`
  - `M	docs/paper/EPIBENCH_REVIEWER_ATTACK_DEFENSE_MATRIX.md`
  - `M	reports/epibench_overclaim_audit/overclaim_findings.csv`
  - `M	reports/epibench_reviewer_packet/README.md`
  - `M	reports/epibench_reviewer_packet/evidence_index.csv`
  - `M	reports/epibench_reviewer_packet/pre_submission_action_register.csv`
  - `M	reports/epibench_reviewer_packet/reviewer_attack_matrix.csv`
  - `A	reports/epibench_weight_sensitivity/README.md`
  - `A	reports/epibench_weight_sensitivity/weight_sensitivity_rank_stability.csv`
  - `A	reports/epibench_weight_sensitivity/weight_sensitivity_scores.csv`
  - `A	reports/epibench_weight_sensitivity/weight_sensitivity_summary.csv`
  - `M	scripts/epibench_build_reviewer_packet.py`
  - `A	scripts/epibench_build_weight_sensitivity.py`
  - `M	tests/test_epibench_standard.py`

### 167. `7628054` - Reduce false positives in overclaim audit

- Full SHA: `762805483c019141406e06311802d85765fccf13`
- Date: `2026-05-24T15:52:29+02:00`
- Author: `Akir Oussama`
- Shortstat: 8 files changed, 148 insertions(+), 122 deletions(-)
- Body:

```text
Classify line-wrapped boundary statements and explicit forbidden-language contexts as bounded without letting distant negations mask genuinely risky wording.

This drops unbounded clinical/regulatory critical findings to zero and updates the reviewer packet so the overclaim risk becomes a defended, auditable control rather than a noisy blocker.

Validation: python scripts/epibench_overclaim_audit.py; python scripts/epibench_build_reviewer_packet.py; uv run --extra dev pytest tests/test_epibench_standard.py -q; uv run --extra dev ruff check src/epibench tests/test_epibench_standard.py scripts/epibench.py scripts/epibench_build_msg_gate_c_package.py scripts/epibench_build_chbmit_package.py scripts/epibench_build_evidence_panels.py scripts/epibench_build_coverage_audit.py scripts/epibench_overclaim_audit.py scripts/epibench_build_reviewer_packet.py scripts/epibench_build_weight_sensitivity.py.
```
- Files changed:
  - `M	reports/epibench_overclaim_audit/README.md`
  - `M	reports/epibench_overclaim_audit/overclaim_findings.csv`
  - `M	reports/epibench_reviewer_packet/README.md`
  - `M	reports/epibench_reviewer_packet/evidence_index.csv`
  - `M	reports/epibench_reviewer_packet/pre_submission_action_register.csv`
  - `M	reports/epibench_reviewer_packet/reviewer_attack_matrix.csv`
  - `M	scripts/epibench_overclaim_audit.py`
  - `M	tests/test_epibench_standard.py`

### 168. `40bf9f0` - Add CHB-MIT waveform micro evidence package

- Full SHA: `40bf9f0b1662e41237c850d1c1830ab41d2bfbbf`
- Date: `2026-05-24T16:17:18+02:00`
- Author: `Akir Oussama`
- Shortstat: 33 files changed, 1329 insertions(+), 55 deletions(-)
- Body:

```text
Build a public EDF-derived CHB-MIT micro-subset package with a deterministic line-length threshold baseline, patient-independent split, generated metrics, failure trace, claim report, and manuscript panels.

The result intentionally preserves the negative outcome: the waveform baseline requests E2-PI but is claim-gated to E1 by FAR_EXPLOSION, giving the protocol a real EEG signal failure case instead of another synthetic demo.

Validation: python scripts/epibench_build_chbmit_waveform_micro_package.py; python scripts/epibench.py validate-dataset-card/split/failure-trace/result-bundle for examples/epibench/chbmit_waveform_micro_d; python scripts/epibench_build_evidence_panels.py; python scripts/epibench_build_coverage_audit.py; python scripts/epibench_build_weight_sensitivity.py; python scripts/epibench_overclaim_audit.py; python scripts/epibench_build_reviewer_packet.py; uv run --extra dev pytest tests/test_epibench_standard.py -q; uv run --extra dev ruff check src/epibench tests/test_epibench_standard.py scripts/epibench.py scripts/epibench_build_msg_gate_c_package.py scripts/epibench_build_chbmit_package.py scripts/epibench_build_chbmit_waveform_micro_package.py scripts/epibench_build_evidence_panels.py scripts/epibench_build_coverage_audit.py scripts/epibench_overclaim_audit.py scripts/epibench_build_reviewer_packet.py scripts/epibench_build_weight_sensitivity.py.
```
- Files changed:
  - `M	docs/EPIBENCH_IMPLEMENTATION_INDEX.md`
  - `A	examples/epibench/chbmit_waveform_micro_d/dataset_card.yaml`
  - `A	examples/epibench/chbmit_waveform_micro_d/failure_trace.yaml`
  - `A	examples/epibench/chbmit_waveform_micro_d/result_bundle.yaml`
  - `A	examples/epibench/chbmit_waveform_micro_d/split_manifest.yaml`
  - `A	reports/chbmit_waveform_micro_metrics.json`
  - `A	reports/epibench_chbmit_waveform_micro_claim.json`
  - `A	reports/epibench_chbmit_waveform_micro_claim.md`
  - `A	reports/epibench_chbmit_waveform_micro_report.md`
  - `M	reports/epibench_coverage_audit/README.md`
  - `M	reports/epibench_coverage_audit/dataset_evidence_matrix.csv`
  - `M	reports/epibench_coverage_audit/protocol_use_case_coverage.csv`
  - `M	reports/epibench_coverage_audit/rubric_item_coverage.csv`
  - `M	reports/epibench_evidence_panels/README.md`
  - `M	reports/epibench_evidence_panels/bundle_summary.csv`
  - `M	reports/epibench_evidence_panels/claim_gate_waterfall.csv`
  - `M	reports/epibench_evidence_panels/claim_gated_leaderboard.csv`
  - `M	reports/epibench_evidence_panels/failure_matrix.csv`
  - `M	reports/epibench_evidence_panels/naive_score_leaderboard.csv`
  - `M	reports/epibench_evidence_panels/rank_comparison.csv`
  - `M	reports/epibench_evidence_panels/score_axis_matrix.csv`
  - `A	reports/epibench_evidence_panels/sensitivity_only_leaderboard.csv`
  - `M	reports/epibench_overclaim_audit/README.md`
  - `M	reports/epibench_overclaim_audit/overclaim_findings.csv`
  - `M	reports/epibench_reviewer_packet/README.md`
  - `M	reports/epibench_reviewer_packet/evidence_index.csv`
  - `M	reports/epibench_reviewer_packet/reviewer_attack_matrix.csv`
  - `M	reports/epibench_weight_sensitivity/README.md`
  - `M	reports/epibench_weight_sensitivity/weight_sensitivity_rank_stability.csv`
  - `M	reports/epibench_weight_sensitivity/weight_sensitivity_scores.csv`
  - `A	scripts/epibench_build_chbmit_waveform_micro_package.py`
  - `M	scripts/epibench_build_reviewer_packet.py`
  - `M	tests/test_epibench_standard.py`

### 169. `44a793e` - Add real evidence progression panel

- Full SHA: `44a793e3fda6b142646f46e04d5dfd1ae39969cd`
- Date: `2026-05-24T16:20:24+02:00`
- Author: `Akir Oussama`
- Shortstat: 11 files changed, 303 insertions(+), 4 deletions(-)
- Body:

```text
Summarize the current non-demo EpiBench evidence path across CHB-MIT metadata, CHB-MIT waveform micro, MSG Gate C, and SeizeIT2 preliminary packages.

The generated matrix distinguishes structural E2-PI, waveform-derived E1 failure, patient-dependent forecasting, and preliminary wearable evidence so real-data progress is visible without overclaiming.

Validation: python scripts/epibench_build_real_evidence_progression.py; python scripts/epibench_overclaim_audit.py; python scripts/epibench_build_reviewer_packet.py; uv run --extra dev pytest tests/test_epibench_standard.py -q; uv run --extra dev ruff check src/epibench tests/test_epibench_standard.py scripts/epibench.py scripts/epibench_build_msg_gate_c_package.py scripts/epibench_build_chbmit_package.py scripts/epibench_build_chbmit_waveform_micro_package.py scripts/epibench_build_evidence_panels.py scripts/epibench_build_coverage_audit.py scripts/epibench_overclaim_audit.py scripts/epibench_build_reviewer_packet.py scripts/epibench_build_weight_sensitivity.py scripts/epibench_build_real_evidence_progression.py.
```
- Files changed:
  - `M	docs/EPIBENCH_IMPLEMENTATION_INDEX.md`
  - `M	reports/epibench_overclaim_audit/overclaim_findings.csv`
  - `A	reports/epibench_real_evidence_progression/README.md`
  - `A	reports/epibench_real_evidence_progression/next_step_register.csv`
  - `A	reports/epibench_real_evidence_progression/real_package_matrix.csv`
  - `M	reports/epibench_reviewer_packet/evidence_index.csv`
  - `M	reports/epibench_reviewer_packet/pre_submission_action_register.csv`
  - `M	reports/epibench_reviewer_packet/reviewer_attack_matrix.csv`
  - `A	scripts/epibench_build_real_evidence_progression.py`
  - `M	scripts/epibench_build_reviewer_packet.py`
  - `M	tests/test_epibench_standard.py`

### 170. `cb71e8e` - Use FAR-budgeted threshold for CHB-MIT waveform micro

- Full SHA: `cb71e8e69c5602997fd375766c52e866656699ee`
- Date: `2026-05-24T16:24:51+02:00`
- Author: `Akir Oussama`
- Shortstat: 28 files changed, 271 insertions(+), 294 deletions(-)
- Body:

```text
Select the line-length threshold on train data under a false-alarm budget instead of unconstrained window F1, preserving the patient-independent protocol without using test labels.

The waveform micro package now reaches structural E2-PI but keeps an extremely low Epi-Score and zero test sensitivity, making the result scientifically interpretable rather than alarm-storm driven.

Validation: python scripts/epibench_build_chbmit_waveform_micro_package.py; python scripts/epibench_build_evidence_panels.py; python scripts/epibench_build_coverage_audit.py; python scripts/epibench_build_weight_sensitivity.py; python scripts/epibench_build_real_evidence_progression.py; python scripts/epibench_overclaim_audit.py; python scripts/epibench_build_reviewer_packet.py; uv run --extra dev pytest tests/test_epibench_standard.py -q; uv run --extra dev ruff check src/epibench tests/test_epibench_standard.py scripts/epibench.py scripts/epibench_build_msg_gate_c_package.py scripts/epibench_build_chbmit_package.py scripts/epibench_build_chbmit_waveform_micro_package.py scripts/epibench_build_evidence_panels.py scripts/epibench_build_coverage_audit.py scripts/epibench_overclaim_audit.py scripts/epibench_build_reviewer_packet.py scripts/epibench_build_weight_sensitivity.py scripts/epibench_build_real_evidence_progression.py.
```
- Files changed:
  - `M	examples/epibench/chbmit_waveform_micro_d/failure_trace.yaml`
  - `M	examples/epibench/chbmit_waveform_micro_d/result_bundle.yaml`
  - `M	reports/chbmit_waveform_micro_metrics.json`
  - `M	reports/epibench_chbmit_waveform_micro_claim.json`
  - `M	reports/epibench_chbmit_waveform_micro_claim.md`
  - `M	reports/epibench_chbmit_waveform_micro_report.md`
  - `M	reports/epibench_coverage_audit/protocol_use_case_coverage.csv`
  - `M	reports/epibench_evidence_panels/README.md`
  - `M	reports/epibench_evidence_panels/bundle_summary.csv`
  - `M	reports/epibench_evidence_panels/claim_gate_waterfall.csv`
  - `M	reports/epibench_evidence_panels/claim_gated_leaderboard.csv`
  - `M	reports/epibench_evidence_panels/failure_matrix.csv`
  - `M	reports/epibench_evidence_panels/naive_score_leaderboard.csv`
  - `M	reports/epibench_evidence_panels/rank_comparison.csv`
  - `M	reports/epibench_evidence_panels/score_axis_matrix.csv`
  - `M	reports/epibench_evidence_panels/sensitivity_only_leaderboard.csv`
  - `M	reports/epibench_overclaim_audit/README.md`
  - `M	reports/epibench_overclaim_audit/overclaim_findings.csv`
  - `M	reports/epibench_real_evidence_progression/README.md`
  - `M	reports/epibench_real_evidence_progression/next_step_register.csv`
  - `M	reports/epibench_real_evidence_progression/real_package_matrix.csv`
  - `M	reports/epibench_reviewer_packet/evidence_index.csv`
  - `M	reports/epibench_reviewer_packet/reviewer_attack_matrix.csv`
  - `M	reports/epibench_weight_sensitivity/weight_sensitivity_rank_stability.csv`
  - `M	reports/epibench_weight_sensitivity/weight_sensitivity_scores.csv`
  - `M	scripts/epibench_build_chbmit_waveform_micro_package.py`
  - `M	scripts/epibench_build_real_evidence_progression.py`
  - `M	tests/test_epibench_standard.py`

### 171. `2267bd3` - Update reviewer action for waveform evidence

- Full SHA: `2267bd30ec37b1b203d8dde28af4e6bd2d542fc2`
- Date: `2026-05-24T16:26:00+02:00`
- Author: `Akir Oussama`
- Shortstat: 4 files changed, 4 insertions(+), 4 deletions(-)
- Body:

```text
Revise the A06 reviewer-risk action now that CHB-MIT has a waveform-derived micro package: the remaining blocker is scale and baseline strength, not the mere absence of waveform processing.

Validation: python scripts/epibench_build_reviewer_packet.py; uv run --extra dev pytest tests/test_epibench_standard.py -q; uv run --extra dev ruff check src/epibench tests/test_epibench_standard.py scripts/epibench.py scripts/epibench_build_msg_gate_c_package.py scripts/epibench_build_chbmit_package.py scripts/epibench_build_chbmit_waveform_micro_package.py scripts/epibench_build_evidence_panels.py scripts/epibench_build_coverage_audit.py scripts/epibench_overclaim_audit.py scripts/epibench_build_reviewer_packet.py scripts/epibench_build_weight_sensitivity.py scripts/epibench_build_real_evidence_progression.py.
```
- Files changed:
  - `M	reports/epibench_reviewer_packet/README.md`
  - `M	reports/epibench_reviewer_packet/pre_submission_action_register.csv`
  - `M	reports/epibench_reviewer_packet/reviewer_attack_matrix.csv`
  - `M	scripts/epibench_build_reviewer_packet.py`

### 172. `ef0cdbb` - Add EpiBench external evidence locks

- Full SHA: `ef0cdbb5f75090b402e8dc47f39c9ce6a04b9400`
- Date: `2026-05-24T18:19:42+02:00`
- Author: `Akir Oussama`
- Shortstat: 36 files changed, 1846 insertions(+), 53 deletions(-)
- Body: none
- Files changed:
  - `M	docs/EPIBENCH_IMPLEMENTATION_INDEX.md`
  - `M	examples/epibench/szcore_bridge_demo/README.md`
  - `A	examples/epibench/szcore_official_smoke/README.md`
  - `A	examples/epibench/szcore_official_smoke/hypothesis/sub-01/ses-01/eeg/sub-01_ses-01_task-demo_events.tsv`
  - `A	examples/epibench/szcore_official_smoke/reference/sub-01/ses-01/eeg/sub-01_ses-01_task-demo_events.tsv`
  - `A	examples/epibench/szcore_official_smoke/run_manifest.yaml`
  - `A	examples/epibench/szcore_official_smoke/szcore_evaluation_result.json`
  - `A	reports/epibench_clinical_review_packet/README.md`
  - `A	reports/epibench_clinical_review_packet/clinical_language_checklist.md`
  - `A	reports/epibench_clinical_review_packet/clinical_reviewer_brief.md`
  - `A	reports/epibench_clinical_review_packet/independence_and_conflict_of_interest_form.md`
  - `A	reports/epibench_clinical_review_packet/methods_reviewer_brief.md`
  - `A	reports/epibench_clinical_review_packet/review_execution_manifest.yaml`
  - `A	reports/epibench_hardware_measurement/README.md`
  - `A	reports/epibench_hardware_measurement/latency_samples.csv`
  - `A	reports/epibench_hardware_measurement/local_hardware_report.json`
  - `M	reports/epibench_overclaim_audit/README.md`
  - `M	reports/epibench_overclaim_audit/overclaim_findings.csv`
  - `A	reports/epibench_release_candidate/README.md`
  - `A	reports/epibench_release_candidate/release_manifest.json`
  - `A	reports/epibench_release_candidate/reproduced_claims/chbmit_waveform_micro_d.json`
  - `A	reports/epibench_release_candidate/reproduced_claims/far_explosion_failure_d.json`
  - `A	reports/epibench_release_candidate/reproduced_claims/msg_gate_c_frozen_f.json`
  - `A	reports/epibench_release_candidate/reproduced_claims/pilot_t1_eeg.json`
  - `A	reports/epibench_release_candidate/reproduction_result.json`
  - `M	reports/epibench_reviewer_packet/README.md`
  - `M	reports/epibench_reviewer_packet/evidence_index.csv`
  - `M	reports/epibench_reviewer_packet/pre_submission_action_register.csv`
  - `M	reports/epibench_reviewer_packet/reviewer_attack_matrix.csv`
  - `A	reports/epibench_szcore_official_contract_report.md`
  - `M	scripts/epibench_build_reviewer_packet.py`
  - `A	scripts/epibench_measure_local_hardware.py`
  - `M	scripts/epibench_overclaim_audit.py`
  - `A	scripts/epibench_reproduce_release_candidate.py`
  - `M	src/epibench/szcore_bridge.py`
  - `M	tests/test_epibench_standard.py`

### 173. `7133e4b` - Harden EpiBench against Q1 reviewer attacks

- Full SHA: `7133e4b5534f38f9ed1e3f9ddfb415bd70300041`
- Date: `2026-05-24T18:43:12+02:00`
- Author: `Akir Oussama`
- Shortstat: 31 files changed, 680 insertions(+), 114 deletions(-)
- Body: none
- Files changed:
  - `M	configs/epibench/conformance_suite_v1.yaml`
  - `M	docs/EPIBENCH_IMPLEMENTATION_INDEX.md`
  - `M	docs/paper/EPIBENCH_NPJ_DIGITAL_MEDICINE_DRAFT.md`
  - `M	docs/paper/EPIBENCH_REVIEWER_ATTACK_DEFENSE_MATRIX.md`
  - `M	docs/paper/EPIBENCH_SUBMISSION_READINESS_MATRIX.md`
  - `M	docs/paper/EPIBENCH_SZCORE_COMPATIBILITY_BRIDGE.md`
  - `M	reports/epibench_evidence_panels/bundle_summary.csv`
  - `M	reports/epibench_evidence_panels/claim_gated_leaderboard.csv`
  - `M	reports/epibench_evidence_panels/naive_score_leaderboard.csv`
  - `M	reports/epibench_evidence_panels/sensitivity_only_leaderboard.csv`
  - `M	reports/epibench_overclaim_audit/README.md`
  - `M	reports/epibench_overclaim_audit/overclaim_findings.csv`
  - `M	reports/epibench_pilot_claim.json`
  - `M	reports/epibench_pilot_claim.md`
  - `A	reports/epibench_q1_hardening_register/README.md`
  - `A	reports/epibench_q1_hardening_register/external_dependency_action_register.csv`
  - `A	reports/epibench_q1_hardening_register/q1_hardening_matrix.csv`
  - `A	reports/epibench_q1_hardening_register/q1_hardening_summary.json`
  - `M	reports/epibench_release_candidate/README.md`
  - `M	reports/epibench_release_candidate/release_manifest.json`
  - `M	reports/epibench_release_candidate/reproduced_claims/pilot_t1_eeg.json`
  - `M	reports/epibench_release_candidate/reproduction_result.json`
  - `M	reports/epibench_reviewer_packet/README.md`
  - `M	reports/epibench_reviewer_packet/evidence_index.csv`
  - `M	reports/epibench_szcore_bridge_claim.json`
  - `M	reports/epibench_szcore_bridge_claim.md`
  - `A	scripts/epibench_build_q1_hardening_register.py`
  - `M	scripts/epibench_build_reviewer_packet.py`
  - `M	scripts/epibench_reproduce_release_candidate.py`
  - `M	src/epibench/certification.py`
  - `M	tests/test_epibench_standard.py`

## Final Reading

The project history is not linear model development. It is a sequence of increasingly strict evidence gates. The practical lesson is that the repository repeatedly moved away from easy headline performance claims and toward auditable proof: first by validating data readiness, then by preserving negative evidence, then by turning the evaluation protocol itself into the scientific object. The remaining work is not more rhetoric; it is external proof: larger signal-derived EEG packages, independent clinical review, target-device hardware measurement, DOI release, and external reproduction.
