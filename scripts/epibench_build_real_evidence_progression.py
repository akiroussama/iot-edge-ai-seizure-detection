from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT_DIR = REPO_ROOT / "reports" / "epibench_real_evidence_progression"
DEFAULT_BUNDLE_SUMMARY = REPO_ROOT / "reports" / "epibench_evidence_panels" / "bundle_summary.csv"

REAL_PACKAGE_ORDER = [
    "chbmit_patient_independent_d",
    "chbmit_waveform_micro_d",
    "msg_gate_c_frozen_f",
    "seizeit2_preliminary_f",
]

PACKAGE_INTERPRETATIONS = {
    "chbmit_patient_independent_d": {
        "evidence_role": "real_eeg_metadata_denominator",
        "scientific_read": "T1 patient-independent CHB-MIT structure is certified, but the model is always-negative.",
        "next_step": "Replace null baseline with waveform-derived detector over a larger patient-independent EDF subset.",
    },
    "chbmit_waveform_micro_d": {
        "evidence_role": "real_eeg_waveform_failure_case",
        "scientific_read": "EDF-derived line-length baseline is real signal processing but fails by false-alarm burden.",
        "next_step": "Scale to more patients and add robust baselines before requesting operational E2-PI.",
    },
    "msg_gate_c_frozen_f": {
        "evidence_role": "real_forecasting_gate_c_package",
        "scientific_read": "Frozen MSG forecasting package reaches E2-PD under denominator restrictions.",
        "next_step": "Add patient-independent or external forecasting evidence before claiming E2-PI or E3.",
    },
    "seizeit2_preliminary_f": {
        "evidence_role": "wearable_inventory_preliminary",
        "scientific_read": "Wearable package remains E1 because labels/split/acquisition evidence are incomplete.",
        "next_step": "Complete label audit, acquisition provenance, and patient-independent split manifest.",
    },
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Build EpiBench real-evidence progression panels.")
    parser.add_argument("--bundle-summary", type=Path, default=DEFAULT_BUNDLE_SUMMARY)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    args = parser.parse_args()

    result = build_real_evidence_progression(bundle_summary_path=args.bundle_summary, out_dir=args.out_dir)
    print(
        "Built real-evidence progression with "
        f"{result['package_count']} packages; strongest real claim {result['strongest_claim']}"
    )
    return 0


def build_real_evidence_progression(bundle_summary_path: Path, out_dir: Path) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = _read_csv(bundle_summary_path)
    selected = _select_real_packages(rows)
    action_rows = _action_register(selected)

    _write_csv(out_dir / "real_package_matrix.csv", selected)
    _write_csv(out_dir / "next_step_register.csv", action_rows)
    (out_dir / "README.md").write_text(_render_readme(selected, action_rows), encoding="utf-8")
    return {
        "package_count": len(selected),
        "strongest_claim": _strongest_claim(row["final_claim"] for row in selected),
        "action_count": len(action_rows),
        "out_dir": str(out_dir),
    }


def _select_real_packages(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    by_dataset = {row["dataset_id"]: row for row in rows if row.get("dataset_id") in REAL_PACKAGE_ORDER}
    selected = []
    for dataset_id in REAL_PACKAGE_ORDER:
        row = by_dataset.get(dataset_id)
        if not row:
            continue
        interpretation = PACKAGE_INTERPRETATIONS[dataset_id]
        selected.append(
            {
                "dataset_id": dataset_id,
                "run_id": row["run_id"],
                "track": row["track"],
                "model_family": row["model_family"],
                "evidence_role": interpretation["evidence_role"],
                "final_claim": row["final_claim"],
                "effective_tier": row["effective_tier"],
                "split_policy": row["split_policy"],
                "label_audit": row["label_audit"],
                "epi_score": row["epi_score"],
                "event_sensitivity": row["event_sensitivity"],
                "false_alarms_per_24h": row["false_alarms_per_24h"],
                "blocking_reason_count": row["blocking_reason_count"],
                "scientific_read": interpretation["scientific_read"],
                "next_step": interpretation["next_step"],
                "bundle_path": row["bundle_path"],
            }
        )
    return selected


def _action_register(rows: list[dict[str, Any]]) -> list[dict[str, str]]:
    actions = []
    for row in rows:
        priority = "high"
        if row["dataset_id"] == "chbmit_waveform_micro_d":
            priority = "highest"
        elif row["final_claim"] in {"E2-PD", "E2-PI"}:
            priority = "medium"
        actions.append(
            {
                "dataset_id": row["dataset_id"],
                "priority": priority,
                "current_claim": row["final_claim"],
                "current_blocker": _blocker(row),
                "next_step": row["next_step"],
            }
        )
    return actions


def _blocker(row: dict[str, Any]) -> str:
    if row["dataset_id"] == "chbmit_patient_independent_d":
        return "metadata-only null baseline; no waveform-derived performance"
    if row["dataset_id"] == "chbmit_waveform_micro_d":
        return "waveform-derived baseline is blocked by false-alarm burden and tiny denominator"
    if row["dataset_id"] == "msg_gate_c_frozen_f":
        return "patient-dependent forecasting denominator; no patient-independent claim"
    if row["dataset_id"] == "seizeit2_preliminary_f":
        return "preliminary wearable evidence with incomplete labels/split/provenance"
    return "not classified"


def _render_readme(rows: list[dict[str, Any]], actions: list[dict[str, str]]) -> str:
    claim_counts = _counts(row["final_claim"] for row in rows)
    role_lines = "\n".join(
        f"- `{row['dataset_id']}`: `{row['final_claim']}`; {row['scientific_read']}" for row in rows
    )
    action_lines = "\n".join(
        f"- `{row['priority']}` `{row['dataset_id']}`: {row['next_step']}" for row in actions
    )
    return f"""# EpiBench Real-Evidence Progression

Generated from `reports/epibench_evidence_panels/bundle_summary.csv`.

## Purpose

This panel separates real-data progress from protocol demonstrations. It is intentionally conservative:
real packages are not promoted because they use public data. They are interpreted through their claim,
failure state, split policy, label audit, and denominator strength.

## Summary

- Real or preliminary real-data packages tracked: `{len(rows)}`.
- Claim distribution among these packages: `{_format_counts(claim_counts)}`.
- Strongest real-data claim currently present: `{_strongest_claim(row['final_claim'] for row in rows)}`.

## Package Interpretation

{role_lines}

## Next-Step Register

{action_lines}

## Boundary

This progression panel is not a claim that EpiBench has solved seizure detection. It shows, with
traceable artefacts, where the current repository has real evidence, where that evidence fails, and
which upgrade would most improve the scientific case.
"""


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _counts(values: Any) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        key = str(value)
        counts[key] = counts.get(key, 0) + 1
    return counts


def _format_counts(counts: dict[str, int]) -> str:
    return ", ".join(f"{key}={value}" for key, value in sorted(counts.items()))


def _strongest_claim(values: Any) -> str:
    ranks = {"E0": 0, "E1": 1, "E2-PD": 2, "E2-PI": 3, "E3": 4, "E4": 5}
    claims = list(values)
    if not claims:
        return "none"
    return max(claims, key=lambda claim: ranks.get(claim, -1))


if __name__ == "__main__":
    raise SystemExit(main())
