# Codex review prompts

Use Codex as a hostile reviewer.

## Metric audit

Review event sensitivity, FAR/day, and Time-in-Warning. Find cases where overlapping windows or alarm episodes are counted incorrectly.

## Label audit

Check SPH/SOP labeling. Create adversarial tests where seizure onset is exactly on boundary times.

## Model audit

Check that no model sees future samples when called causal. Check transformer masks and feature extraction windows.
