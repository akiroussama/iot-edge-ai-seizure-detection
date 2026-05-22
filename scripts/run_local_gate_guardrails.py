#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.reports.gate_bc_checklist import (  # noqa: E402
    build_gate_bc_action_checklist,
    gate_bc_action_checklist_markdown,
    table_records as checklist_records,
)
from src.reports.msg_gap_triage import (  # noqa: E402
    build_msg_gap_triage_report,
    msg_gap_triage_markdown,
    table_records as msg_records,
)
from src.reports.seizeit2_cohort_readiness import (  # noqa: E402
    build_seizeit2_cohort_readiness_report,
    seizeit2_cohort_readiness_markdown,
    table_records as seizeit2_records,
)
from src.utils.io import write_table  # noqa: E402


def _markdown_tables_by_heading(path: Path) -> dict[str, pd.DataFrame]:
    lines = path.read_text(encoding="utf-8").splitlines()
    tables: dict[str, pd.DataFrame] = {}
    current_heading = path.stem
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("## "):
            current_heading = line.removeprefix("## ").strip()
            i += 1
            continue
        if line.startswith("|") and i + 1 < len(lines) and lines[i + 1].strip().startswith("|"):
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i].strip())
                i += 1
            if len(table_lines) >= 2:
                tables[current_heading] = _parse_markdown_table(table_lines)
            continue
        i += 1
    return tables


def _parse_markdown_table(table_lines: list[str]) -> pd.DataFrame:
    def split_row(row: str) -> list[str]:
        return [cell.strip() for cell in row.strip().strip("|").split("|")]

    headers = split_row(table_lines[0])
    rows = [split_row(row) for row in table_lines[2:]]
    frame = pd.DataFrame(rows, columns=headers)
    for column in frame.columns:
        numeric = pd.to_numeric(frame[column], errors="coerce")
        if numeric.notna().sum() == frame[column].notna().sum():
            frame[column] = numeric
    return frame


def _first_table(path: Path) -> pd.DataFrame:
    tables = _markdown_tables_by_heading(path)
    if not tables:
        raise ValueError(f"{path} contains no Markdown table")
    return next(iter(tables.values()))


def _seizeit2_inputs_from_dataset_report(path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    tables = _markdown_tables_by_heading(path)
    if "Dataset Summary" not in tables:
        raise ValueError(f"{path} is missing a Dataset Summary table")
    summary = tables["Dataset Summary"].iloc[0]
    track = pd.DataFrame(
        [
            {
                "split_name": "unassigned",
                "task_name": "long_horizon_forecasting",
                "modality_track": "unknown_local",
                "official_split_status": "missing_official_manifest",
                "track_ready": False,
            }
        ]
    )
    counts = pd.DataFrame(
        [
            {
                "metric": "patients",
                "observed": int(float(summary["patients"])),
                "expected": None,
                "count_status": "expected_count_not_provided",
            },
            {
                "metric": "recordings",
                "observed": int(float(summary["recordings"])),
                "expected": None,
                "count_status": "expected_count_not_provided",
            },
            {
                "metric": "events",
                "observed": int(float(summary["events"])),
                "expected": None,
                "count_status": "expected_count_not_provided",
            },
            {
                "metric": "windows",
                "observed": int(float(summary["windows"])),
                "expected": None,
                "count_status": "expected_count_not_provided",
            },
        ]
    )
    return track, counts


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run local MSG and SeizeIT2 Gate B/C guardrails from committed reports."
    )
    parser.add_argument("--msg-coverage-md", default="reports/msg_event_coverage_summary.md")
    parser.add_argument("--msg-horizon-md", default="reports/msg_horizon_viability.md")
    parser.add_argument("--seizeit2-dataset-md", default="reports/seizeit2_sub125_real_check/dataset_report.md")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--gate-b-status", default="not_started")
    parser.add_argument("--gate-c-status", default="not_started")
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    out_dir = Path(args.out_dir)
    inputs_dir = out_dir / "inputs"

    msg_tables = _markdown_tables_by_heading(Path(args.msg_coverage_md))
    coverage = msg_tables["Event Coverage"]
    clusters = msg_tables["Seizure Cluster Summary"]
    viability = _first_table(Path(args.msg_horizon_md))
    write_table(coverage, inputs_dir / "msg_event_coverage.csv")
    write_table(clusters, inputs_dir / "msg_event_clusters.csv")
    write_table(viability, inputs_dir / "msg_horizon_viability.csv")

    msg_report = build_msg_gap_triage_report(coverage, clusters, viability, dataset="MSG")
    write_table(msg_report.patient_triage, out_dir / "msg_gap_patient_triage.csv")
    write_table(msg_report.horizon_triage, out_dir / "msg_gap_horizon_triage.csv")
    write_table(msg_report.summary, out_dir / "msg_gap_summary.csv")
    write_table(msg_report.manifest, out_dir / "msg_gap_triage_manifest.csv")
    _write_json(
        out_dir / "msg_gap_triage_report.json",
        {
            "metadata": msg_report.metadata,
            "summary": msg_records(msg_report.summary),
            "patient_triage": msg_records(msg_report.patient_triage),
            "horizon_triage": msg_records(msg_report.horizon_triage),
        },
    )
    (out_dir / "msg_gap_triage_report.md").write_text(
        msg_gap_triage_markdown(msg_report, title="MSG Data-Gap Triage - Local Artifacts"),
        encoding="utf-8",
    )

    seizeit2_track, seizeit2_counts = _seizeit2_inputs_from_dataset_report(
        Path(args.seizeit2_dataset_md)
    )
    write_table(seizeit2_track, inputs_dir / "seizeit2_local_track.csv")
    write_table(seizeit2_counts, inputs_dir / "seizeit2_local_count_summary.csv")
    seizeit2_report = build_seizeit2_cohort_readiness_report(
        seizeit2_track,
        seizeit2_counts,
        gate_b_status=args.gate_b_status,
        gate_c_status=args.gate_c_status,
    )
    write_table(seizeit2_report.summary, out_dir / "seizeit2_cohort_readiness_summary.csv")
    write_table(seizeit2_report.blockers, out_dir / "seizeit2_cohort_readiness_blockers.csv")
    write_table(seizeit2_report.warnings, out_dir / "seizeit2_cohort_readiness_warnings.csv")
    write_table(seizeit2_report.manifest, out_dir / "seizeit2_cohort_readiness_manifest.csv")
    _write_json(
        out_dir / "seizeit2_cohort_readiness_report.json",
        {
            "metadata": seizeit2_report.metadata,
            "summary": seizeit2_records(seizeit2_report.summary),
            "blockers": seizeit2_records(seizeit2_report.blockers),
            "warnings": seizeit2_records(seizeit2_report.warnings),
        },
    )
    (out_dir / "seizeit2_cohort_readiness_report.md").write_text(
        seizeit2_cohort_readiness_markdown(
            seizeit2_report,
            title="SeizeIT2 Cohort Readiness - Local Artifacts",
        ),
        encoding="utf-8",
    )

    checklist = build_gate_bc_action_checklist(
        msg_report.patient_triage,
        msg_report.horizon_triage,
        msg_report.summary,
        seizeit2_report.summary,
        seizeit2_report.blockers,
        seizeit2_report.warnings,
    )
    write_table(checklist.actions, out_dir / "gate_bc_action_checklist.csv")
    write_table(checklist.summary, out_dir / "gate_bc_action_summary.csv")
    _write_json(
        out_dir / "gate_bc_action_checklist.json",
        {
            "metadata": checklist.metadata,
            "summary": checklist_records(checklist.summary),
            "actions": checklist_records(checklist.actions),
        },
    )
    (out_dir / "gate_bc_action_checklist.md").write_text(
        gate_bc_action_checklist_markdown(checklist),
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "out_dir": str(out_dir),
                "msg_p0_patients": int(msg_report.summary.loc[0, "patients_p0_blocker"]),
                "msg_unmatched_events": int(msg_report.summary.loc[0, "events_unmatched"]),
                "seizeit2_blockers": int(seizeit2_report.summary.loc[0, "blockers"]),
                "checklist_actions": int(checklist.summary.loc[0, "actions_total"]),
                "claim_status": checklist.summary.loc[0, "claim_status"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
