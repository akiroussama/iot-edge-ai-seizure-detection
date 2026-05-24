# BSEBench External Reproduction Outreach Email

Subject: Invitation to independently reproduce a BSEBench battery-estimation result bundle

Dear Professor [Name],

I hope this message finds you well.

We are preparing BSEBench, an auditable benchmark protocol for battery state estimation. The central goal is to move beyond single-score comparisons, such as RMSE-only reporting, toward reproducible evidence packages that include dataset provenance, estimator configuration, failure traces, runtime, environment metadata, and explicit claim eligibility.

Before submission, we would like to invite a small number of independent battery laboratories to run a partial external reproduction of one frozen BSEBench result bundle. The reproduction kit is designed to require minimal effort:

- Docker-based environment;
- one-command execution;
- automatic bit-exact comparison against a frozen reference manifest;
- divergence report if outputs differ.

The intended command is:

```bash
bsebench reproduce --bundle bundle_calce_a123_lfp_dst_v1.0
```

We are not asking your group to endorse the method or results. We are asking whether the bundle can be reproduced independently, and whether the protocol is clear enough for an external laboratory to audit.

Expected time commitment:

- approximately 30 minutes for the initial run;
- optional feedback by email on usability or scientific clarity.

If you are willing, we would send:

1. the frozen reproduction bundle;
2. the Docker reproduction kit;
3. the reference manifest;
4. a short feedback form.

We would be grateful to acknowledge your laboratory's assistance in the reproducibility statement, subject to your approval. No co-authorship is implied unless your team contributes substantial scientific or technical work beyond the reproduction check.

With best regards,

Oussama [Surname]  
[Affiliation]  
[Email]  
[Project or repository URL]
