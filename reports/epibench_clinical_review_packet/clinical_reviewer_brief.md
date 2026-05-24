# Clinical Reviewer Brief

You are asked to review EpiBench Dataset Evidence Cards before model performance is interpreted.

## Your Task

For each dataset package, score the MTS and DSI items using the provided 0/1/2/3 rubric, assign a dataset
tier, and assign the maximum scientific claim ceiling the dataset could support before seeing any model
metrics.

## What To Focus On

- label provenance and whether seizure annotations are neurologist-reviewed, proxy-derived, or automatic;
- onset and offset uncertainty;
- seizure-type coverage and whether non-convulsive seizures are represented;
- recording setting: hospital, home, wearable, or mixed;
- whether monitoring duration is sufficient for false-alarm burden claims;
- whether patient independence and external validation are sufficient for generalization wording;
- whether any proposed clinical language is stronger than the evidence permits.

## What Not To Do

- Do not rank models.
- Do not inspect accuracy, F1, sensitivity, false alarms/day, or Epi-Score before dataset scoring.
- Do not raise a dataset tier because a model result looks promising.
- Do not infer clinical readiness from retrospective evidence.

## Required Output

Complete `dataset_review_form.csv` for each dataset and declare whether any wording in
`clinical_language_checklist.md` should be blocked, softened, or moved to limitations.
