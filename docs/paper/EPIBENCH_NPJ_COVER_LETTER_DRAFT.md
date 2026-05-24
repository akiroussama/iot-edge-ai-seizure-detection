# Cover Letter Draft for npj Digital Medicine

Dear Editors,

We are pleased to submit our manuscript, "EpiBench for auditable evidence in seizure AI," for consideration as an Article in npj Digital Medicine.

Artificial intelligence systems for seizure detection, early warning, and forecasting are increasingly evaluated using summary metrics such as sensitivity, F1 score, AUROC, or false alarms per day. These metrics are important, but they are not self-interpreting evidence. Their meaning depends on dataset provenance, annotation quality, seizure timing uncertainty, split design, patient independence, monitoring setting, sensor modality, missing data, failure handling, latency, and hardware feasibility. Without an auditable protocol, a leaderboard row can appear stronger than the evidence permits.

Our manuscript introduces EpiBench, an open evidence and claim-certification framework for seizure AI. EpiBench separates dataset evidence from algorithm behavior through Dataset Evidence Cards, metrological trustworthiness and domain stress rubrics, track-specific evaluation for detection, early warning, forecasting, and embedded viability, failure-preserving result bundles, and deterministic claim gates. Instead of asking only which model ranks highest, EpiBench asks what a result is scientifically allowed to claim.

We believe this work is a strong fit for npj Digital Medicine because it addresses a core problem in digital and mobile health AI: how to make algorithmic claims auditable, reproducible, and clinically bounded without overstating retrospective benchmark results. The manuscript includes a versioned specification, machine-readable schemas, a reference command-line implementation, certification reports, and worked examples showing that a high-performing but leakage-contaminated model is downgraded despite superior naive metrics.

EpiBench is explicitly not presented as clinical approval, regulatory clearance, or evidence of deployment readiness. EpiBench-certified means scientifically certified under the EpiBench evidence protocol, with a bounded claim level. This distinction is embedded in the specification, reports, and manuscript.

The framework is designed to complement, not replace, existing community resources. It adopts or maps compatible work including ILAE seizure terminology, event-based seizure scoring frameworks such as SzCORE, and clinical AI reporting guidelines including TRIPOD+AI, STARD-AI, DECIDE-AI, CONSORT-AI, and FUTURE-AI. EpiBench adds a seizure-specific evidence and claim-governance layer around these resources.

All authors have approved the manuscript. The work is original and is not under consideration elsewhere. Code, schemas, and evidence-package examples will be made publicly available with a versioned archive before publication.

Sincerely,

To be completed
