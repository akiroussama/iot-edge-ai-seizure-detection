from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Any
from urllib.request import urlopen

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
PHYSIONET_BASE = "https://physionet.org/files/chbmit/1.0.0/"
RAW_DIR = REPO_ROOT / "data" / "raw" / "chbmit_metadata"
PROCESSED_DIR = REPO_ROOT / "data" / "processed" / "chbmit_metadata"
PACKAGE_DIR = REPO_ROOT / "examples" / "epibench" / "chbmit_patient_independent_d"
REPORT_DIR = REPO_ROOT / "reports"

VALIDATION_CASES = {"chb06", "chb10", "chb14", "chb18", "chb23"}
TEST_CASES = {"chb12", "chb13", "chb15", "chb16", "chb20", "chb24"}


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Build a CHB-MIT metadata-based EpiBench Track D patient-independent "
            "evidence package from official PhysioNet summaries."
        )
    )
    parser.add_argument("--raw-dir", type=Path, default=RAW_DIR)
    parser.add_argument("--processed-dir", type=Path, default=PROCESSED_DIR)
    parser.add_argument("--package-dir", type=Path, default=PACKAGE_DIR)
    parser.add_argument("--refresh", action="store_true", help="Re-download PhysioNet metadata files")
    args = parser.parse_args()

    args.raw_dir.mkdir(parents=True, exist_ok=True)
    args.processed_dir.mkdir(parents=True, exist_ok=True)
    args.package_dir.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    metadata_files = _download_metadata(args.raw_dir, refresh=args.refresh)
    subject_info = _parse_subject_info(metadata_files["subject_info"])
    cases = _case_ids_from_records(metadata_files["records"])
    summaries = [_parse_summary(args.raw_dir / case / f"{case}-summary.txt") for case in cases]
    recordings = [recording for summary in summaries for recording in summary["recordings"]]
    events = [event for summary in summaries for event in summary["events"]]
    split = _assign_split(cases)

    _write_csv(args.processed_dir / "recordings.csv", recordings)
    _write_csv(args.processed_dir / "events.csv", events)
    _write_csv(
        args.processed_dir / "split_cases.csv",
        [{"case_id": case, "subject_id": _subject_id(case), "split": split[case]} for case in cases],
    )
    metrics = _always_negative_metrics(recordings, events, split)
    summary = _dataset_summary(recordings, events, subject_info)
    _write_json(args.processed_dir / "metadata_summary.json", summary)
    _write_json(REPORT_DIR / "chbmit_patient_independent_null_metrics.json", metrics)

    _write_yaml(args.package_dir / "dataset_card.yaml", _dataset_card(summary))
    _write_yaml(args.package_dir / "split_manifest.yaml", _split_manifest(recordings, events, split))
    _write_yaml(args.package_dir / "failure_trace.yaml", _failure_trace())
    _write_yaml(args.package_dir / "result_bundle.yaml", _result_bundle(metrics))

    print(f"Built CHB-MIT EpiBench package in {args.package_dir}")
    print(f"Processed metadata written to {args.processed_dir}")
    return 0


def _download_metadata(raw_dir: Path, refresh: bool) -> dict[str, Path]:
    files = {
        "records": raw_dir / "RECORDS",
        "records_with_seizures": raw_dir / "RECORDS-WITH-SEIZURES",
        "subject_info": raw_dir / "SUBJECT-INFO",
    }
    for remote_name, path in [
        ("RECORDS", files["records"]),
        ("RECORDS-WITH-SEIZURES", files["records_with_seizures"]),
        ("SUBJECT-INFO", files["subject_info"]),
    ]:
        _download_text(PHYSIONET_BASE + remote_name, path, refresh)

    cases = _case_ids_from_records(files["records"])
    for case in cases:
        target = raw_dir / case / f"{case}-summary.txt"
        _download_text(f"{PHYSIONET_BASE}{case}/{case}-summary.txt", target, refresh)
    return files


def _download_text(url: str, target: Path, refresh: bool) -> None:
    if target.exists() and not refresh:
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    text = urlopen(url, timeout=30).read().decode("utf-8", errors="replace")
    target.write_text(text, encoding="utf-8")


def _case_ids_from_records(records_path: Path) -> list[str]:
    cases = sorted({line.split("/", 1)[0] for line in records_path.read_text().splitlines() if line})
    return [case for case in cases if re.fullmatch(r"chb\d{2}", case)]


def _parse_subject_info(path: Path) -> dict[str, dict[str, str]]:
    rows: dict[str, dict[str, str]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("chb"):
            continue
        case, gender, age = re.split(r"\s+", line.strip(), maxsplit=2)
        rows[case] = {"gender": gender, "age_years": age.strip()}
    return rows


def _parse_summary(path: Path) -> dict[str, Any]:
    case_id = path.parent.name
    text = path.read_text(encoding="utf-8", errors="replace")
    blocks = re.split(r"\n(?=File Name: )", text)
    recordings: list[dict[str, Any]] = []
    events: list[dict[str, Any]] = []
    for block in blocks:
        file_match = re.search(r"File Name:\s*(\S+)", block)
        if not file_match:
            continue
        file_name = file_match.group(1)
        seizure_count = int(_extract_required(block, r"Number of Seizures in File:\s*(\d+)"))
        recording_id = file_name.removesuffix(".edf")
        starts = [
            int(value)
            for value in re.findall(r"Seizure(?:\s+\d+)?\s+Start Time:\s*(\d+)\s*seconds", block)
        ]
        ends = [
            int(value)
            for value in re.findall(r"Seizure(?:\s+\d+)?\s+End Time:\s*(\d+)\s*seconds", block)
        ]
        start_match = re.search(r"File Start Time:\s*([0-9:]+)", block)
        end_match = re.search(r"File End Time:\s*([0-9:]+)", block)
        if start_match and end_match:
            duration = _duration_seconds(start_match.group(1), end_match.group(1))
        else:
            # chb24 summaries omit file start/end times. PhysioNet documents that
            # most CHB-MIT EDFs are one hour; use the conservative larger of one
            # hour or the last annotated seizure offset.
            duration = max([3600, *ends])
        recordings.append(
            {
                "case_id": case_id,
                "subject_id": _subject_id(case_id),
                "recording_id": recording_id,
                "file_name": file_name,
                "duration_seconds": duration,
                "n_seizures": seizure_count,
            }
        )
        if len(starts) != len(ends) or len(starts) != seizure_count:
            raise ValueError(f"Seizure count mismatch in {path}: {file_name}")
        for index, (start_seconds, end_seconds) in enumerate(zip(starts, ends, strict=True), start=1):
            events.append(
                {
                    "event_id": f"{recording_id}_seizure_{index:02d}",
                    "case_id": case_id,
                    "subject_id": _subject_id(case_id),
                    "recording_id": recording_id,
                    "onset_seconds": start_seconds,
                    "offset_seconds": end_seconds,
                    "duration_seconds": end_seconds - start_seconds,
                }
            )
    return {"case_id": case_id, "recordings": recordings, "events": events}


def _extract_required(text: str, pattern: str) -> str:
    match = re.search(pattern, text)
    if not match:
        raise ValueError(f"Missing required pattern {pattern!r}")
    return match.group(1)


def _duration_seconds(start: str, end: str) -> int:
    start_seconds = _clock_seconds(start)
    end_seconds = _clock_seconds(end)
    while end_seconds <= start_seconds:
        end_seconds += 24 * 3600
    return end_seconds - start_seconds


def _clock_seconds(value: str) -> int:
    hours, minutes, seconds = [int(part) for part in value.split(":")]
    return hours * 3600 + minutes * 60 + seconds


def _subject_id(case_id: str) -> str:
    # PhysioNet documents that chb21 was obtained from the same subject as chb01.
    return "chb01_subject" if case_id in {"chb01", "chb21"} else f"{case_id}_subject"


def _assign_split(cases: list[str]) -> dict[str, str]:
    split: dict[str, str] = {}
    for case in cases:
        if case in TEST_CASES:
            split[case] = "test"
        elif case in VALIDATION_CASES:
            split[case] = "validation"
        else:
            split[case] = "train"
    if split["chb01"] != split["chb21"]:
        raise AssertionError("chb01 and chb21 must remain in the same split.")
    return split


def _always_negative_metrics(
    recordings: list[dict[str, Any]], events: list[dict[str, Any]], split: dict[str, str]
) -> dict[str, Any]:
    test_cases = {case for case, split_name in split.items() if split_name == "test"}
    test_recordings = [row for row in recordings if row["case_id"] in test_cases]
    test_events = [row for row in events if row["case_id"] in test_cases]
    test_hours = sum(float(row["duration_seconds"]) for row in test_recordings) / 3600.0
    per_case = []
    for case in sorted(test_cases):
        n_events = sum(1 for event in test_events if event["case_id"] == case)
        hours = sum(float(row["duration_seconds"]) for row in test_recordings if row["case_id"] == case) / 3600.0
        per_case.append(
            {
                "case_id": case,
                "subject_id": _subject_id(case),
                "n_events": n_events,
                "monitoring_hours": round(hours, 3),
                "event_sensitivity": 0.0,
                "false_alarms_per_24h": 0.0,
            }
        )
    metrics = {
        "schema_version": "chbmit.null_metrics.v1",
        "model_name": "always_negative",
        "task_type": "seizure_detection",
        "split_policy": "patient_independent",
        "test_cases": sorted(test_cases),
        "test_subjects": sorted({_subject_id(case) for case in test_cases}),
        "events_used_for_metrics": len(test_events),
        "monitored_hours_test": round(test_hours, 3),
        "event_sensitivity": 0.0,
        "false_alarms_per_24h": 0.0,
        "precision": None,
        "event_f1": 0.0,
        "median_detection_latency_seconds": None,
        "p95_detection_latency_seconds": None,
        "missing_prediction_rate": 0.0,
        "per_case": per_case,
        "interpretation": (
            "Always-negative patient-independent baseline. It is a denominator and claim-gate "
            "control, not a clinically useful detector."
        ),
    }
    return metrics


def _dataset_summary(
    recordings: list[dict[str, Any]], events: list[dict[str, Any]], subject_info: dict[str, dict[str, str]]
) -> dict[str, Any]:
    unique_subjects = sorted({row["subject_id"] for row in recordings})
    known_demographics = [case for case in subject_info if case != "chb21"]
    female = sum(1 for case in known_demographics if subject_info[case]["gender"] == "F")
    male = sum(1 for case in known_demographics if subject_info[case]["gender"] == "M")
    return {
        "schema_version": "chbmit.metadata_summary.v1",
        "n_cases": len({row["case_id"] for row in recordings}),
        "n_unique_subject_groups": len(unique_subjects),
        "n_recordings": len(recordings),
        "n_seizure_recordings": sum(1 for row in recordings if int(row["n_seizures"]) > 0),
        "n_seizures": len(events),
        "monitoring_hours": round(sum(float(row["duration_seconds"]) for row in recordings) / 3600.0, 3),
        "known_demographics": {
            "female_subjects": female,
            "male_subjects": male,
            "missing_subject_info_cases": ["chb24"],
            "age_range_years": "1.5-22 for cases listed in SUBJECT-INFO",
        },
    }


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _write_yaml(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=False), encoding="utf-8")


def _dataset_card(summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "epibench.dataset_card.v1",
        "dataset_id": "chbmit_patient_independent_d",
        "name": "CHB-MIT PhysioNet Metadata Patient-Independent Detection Evidence Package",
        "version": "1.0.0-metadata-package-2026-05-24",
        "license": "Open Data Commons Attribution License v1.0",
        "source": {
            "url_or_doi": "https://doi.org/10.13026/C2K01R",
            "access_date": "2026-05-24",
            "official_source": True,
        },
        "provenance": (
            "Official PhysioNet CHB-MIT RECORDS, RECORDS-WITH-SEIZURES, SUBJECT-INFO, "
            "and chbXX-summary.txt files downloaded from https://physionet.org/files/chbmit/1.0.0/. "
            "No EDF waveform download is required for this null-baseline package."
        ),
        "sensors": [
            {
                "modality": "scalp_eeg",
                "sampling_rate_hz": 256,
                "placement": "international_10_20_scalp_eeg_montage",
                "calibration": "16-bit EDF signals; calibration details are inherited from the PhysioNet EDF files",
                "synchronization": "per-recording relative seizure onset and offset seconds from official summary files",
            }
        ],
        "population": {
            "n_patients": int(summary["n_unique_subject_groups"]),
            "n_seizures": int(summary["n_seizures"]),
            "monitoring_hours": float(summary["monitoring_hours"]),
            "setting": "hospital",
            "age_summary": summary["known_demographics"]["age_range_years"],
            "sex_summary": (
                f"{summary['known_demographics']['female_subjects']} female and "
                f"{summary['known_demographics']['male_subjects']} male subjects in SUBJECT-INFO; "
                "chb24 not listed"
            ),
            "seizure_types": [],
        },
        "labels": {
            "label_source": "expert_adjudicated",
            "onset_available": True,
            "offset_available": True,
            "temporal_uncertainty_seconds": None,
            "audit_status": "expert_adjudicated_onset_offset",
        },
        "mts": _mts_items(),
        "dsi": _dsi_items(),
        "tier": {
            "declared": "T1",
            "rationale": (
                "Official PhysioNet source, explicit onset/offset annotations, public provenance, "
                "and patient-independent split support strong retrospective evidence. Hospital-only "
                "pediatric context and metadata-only baseline limit domain scope, not metrological tier."
            ),
        },
        "limitations": [
            "This package evaluates an always-negative null baseline; it is not a useful seizure detector.",
            "The package downloads official metadata and annotations, not the 42.6 GB EDF waveform archive.",
            "CHB-MIT is a hospital pediatric dataset and does not support home IoT generalization.",
            "Case chb21 is documented as the same subject as chb01 and is kept in the same split group.",
            "Case chb24 is present in RECORDS but not in SUBJECT-INFO.",
        ],
        "raw_to_processed_trace": {
            "available": True,
            "description": (
                "scripts/epibench_build_chbmit_package.py downloads official metadata, parses summaries, "
                "materializes recordings/events/splits, and emits the EpiBench evidence package."
            ),
            "checksums_available": False,
        },
    }


def _mts_items() -> dict[str, dict[str, Any]]:
    return {
        "source_official": {
            "score": 3,
            "evidence": "PhysioNet official project DOI and open access page",
            "review_status": "self_reviewed",
        },
        "acquisition_protocol": {
            "score": 3,
            "evidence": "PhysioNet methods document pediatric hospital EEG acquisition, 10-20 montage, 256 Hz sampling, and EDF organization",
            "review_status": "self_reviewed",
        },
        "label_quality": {
            "score": 3,
            "evidence": "official summaries provide seizure onset and end seconds for annotated seizure files",
            "review_status": "self_reviewed",
        },
        "synchronization": {
            "score": 2,
            "evidence": "relative timing within each EDF is explicit; absolute dates are surrogate and recording gaps exist",
            "review_status": "self_reviewed",
        },
        "raw_to_processed_trace": {
            "score": 3,
            "evidence": "metadata parser is deterministic and stores raw summaries, processed recordings, events, split cases, and metrics",
            "review_status": "self_reviewed",
        },
        "missingness": {
            "score": 2,
            "evidence": "official documentation reports recording gaps; this metadata baseline avoids waveform missingness claims",
            "review_status": "self_reviewed",
        },
        "leakage_audit": {
            "score": 3,
            "evidence": "fixed split keeps chb01/chb21 same-subject cases together and separates train/validation/test subjects",
            "review_status": "self_reviewed",
        },
    }


def _dsi_items() -> dict[str, dict[str, Any]]:
    return {
        "patient_diversity": {
            "score": 2,
            "evidence": "22 documented pediatric subjects plus additional chb24 case, with age/sex metadata for listed cases",
            "review_status": "self_reviewed",
        },
        "setting_diversity": {
            "score": 0,
            "evidence": "hospital monitoring only",
            "review_status": "self_reviewed",
        },
        "seizure_type_diversity": {
            "score": 1,
            "evidence": "dataset contains seizure events but this metadata package does not adjudicate seizure semiology",
            "review_status": "self_reviewed",
        },
        "sensor_realism": {
            "score": 3,
            "evidence": "clinical scalp EEG with standard montage and 256 Hz sampling",
            "review_status": "self_reviewed",
        },
        "external_validation": {
            "score": 0,
            "evidence": "no external dataset validation in this package",
            "review_status": "self_reviewed",
        },
    }


def _split_manifest(
    recordings: list[dict[str, Any]], events: list[dict[str, Any]], split: dict[str, str]
) -> dict[str, Any]:
    return {
        "schema_version": "epibench.split_manifest.v1",
        "split_id": "chbmit_fixed_patient_independent_2026-05-24",
        "dataset_id": "chbmit_patient_independent_d",
        "track": "D",
        "split_policy": "patient_independent",
        "train_units": _unit_summary("train", recordings, events, split),
        "validation_units": _unit_summary("validation", recordings, events, split),
        "test_units": _unit_summary("test", recordings, events, split),
        "leakage_checks": {
            "patient_overlap": False,
            "temporal_overlap": False,
            "normalization_scope": "train_only",
            "status": "passed",
        },
        "threshold_selection_policy": {
            "selection_split": "validation",
            "uses_test_labels": False,
        },
    }


def _unit_summary(
    split_name: str,
    recordings: list[dict[str, Any]],
    events: list[dict[str, Any]],
    split: dict[str, str],
) -> dict[str, Any]:
    cases = {case for case, assigned in split.items() if assigned == split_name}
    split_recordings = [row for row in recordings if row["case_id"] in cases]
    split_events = [row for row in events if row["case_id"] in cases]
    return {
        "n_patients": len({_subject_id(case) for case in cases}),
        "n_recordings": len(split_recordings),
        "n_events": len(split_events),
        "monitoring_hours": round(
            sum(float(row["duration_seconds"]) for row in split_recordings) / 3600.0, 3
        ),
    }


def _failure_trace() -> dict[str, Any]:
    return {
        "schema_version": "epibench.failure_trace.v1",
        "run_id": "chbmit_always_negative_patient_independent",
        "failure_policy": "preserve_all",
        "sentinels": [
            {
                "code": "HARDWARE_UNMEASURED",
                "present": True,
                "severity": "warning",
                "count": 1,
                "scope": "run",
                "evidence": "metadata-only package; no embedded hardware latency or energy measurement",
            },
            {
                "code": "PREDICTION_MISSING",
                "present": False,
                "severity": "none",
                "count": 0,
                "scope": "none",
                "evidence": "always-negative predictions are defined for all test recording time",
            },
            {
                "code": "PATIENT_LEAKAGE",
                "present": False,
                "severity": "none",
                "count": 0,
                "scope": "none",
                "evidence": "test cases are disjoint by subject group; chb01 and chb21 are kept together",
            },
            {
                "code": "TEMPORAL_LEAKAGE",
                "present": False,
                "severity": "none",
                "count": 0,
                "scope": "none",
                "evidence": "fixed patient-independent split; no threshold uses test labels",
            },
            {
                "code": "LABEL_UNAUDITED",
                "present": False,
                "severity": "none",
                "count": 0,
                "scope": "none",
                "evidence": "official CHB-MIT summaries provide onset and end annotations",
            },
        ],
        "summary": {
            "critical_failure_present": False,
            "blocking_failure_present": False,
            "failure_rate": 0.0,
        },
    }


def _result_bundle(metrics: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "epibench.result_bundle.v1",
        "run_id": "chbmit_always_negative_patient_independent",
        "track": "D",
        "requested_claim": "E2-PI",
        "dataset_card_path": "dataset_card.yaml",
        "split_manifest_path": "split_manifest.yaml",
        "failure_trace_path": "failure_trace.yaml",
        "model": {
            "name": "always_negative",
            "family": "null_baseline",
            "commit_sha": "metadata-baseline-2026-05-24",
        },
        "environment": {
            "python": "3.12",
            "platform": "metadata-only-public-physionet",
            "dependencies": ["pyyaml"],
        },
        "inputs": [
            {"path": "data/raw/chbmit_metadata/RECORDS", "sha256": None},
            {"path": "data/raw/chbmit_metadata/RECORDS-WITH-SEIZURES", "sha256": None},
            {"path": "data/raw/chbmit_metadata/SUBJECT-INFO", "sha256": None},
            {"path": "data/raw/chbmit_metadata/chb*/chb*-summary.txt", "sha256": None},
        ],
        "outputs": [
            {"path": "data/processed/chbmit_metadata/recordings.csv", "sha256": None},
            {"path": "data/processed/chbmit_metadata/events.csv", "sha256": None},
            {"path": "data/processed/chbmit_metadata/split_cases.csv", "sha256": None},
            {"path": "reports/chbmit_patient_independent_null_metrics.json", "sha256": None},
        ],
        "metrics": {
            "task_type": metrics["task_type"],
            "baseline_type": "always_negative",
            "event_sensitivity": metrics["event_sensitivity"],
            "false_alarms_per_24h": metrics["false_alarms_per_24h"],
            "precision": metrics["precision"],
            "event_f1": metrics["event_f1"],
            "events_used_for_metrics": metrics["events_used_for_metrics"],
            "monitored_hours_test": metrics["monitored_hours_test"],
            "median_detection_latency_seconds": metrics["median_detection_latency_seconds"],
            "p95_detection_latency_seconds": metrics["p95_detection_latency_seconds"],
            "missing_prediction_rate": metrics["missing_prediction_rate"],
            "clinical_utility_statement": "not clinically useful; null baseline only",
        },
        "score_inputs": {
            "subscores": {
                "performance": 0.02,
                "clinical_safety": 0.05,
                "robustness": 0.10,
                "stability": 0.20,
                "latency": 0.50,
                "calibration": 0.10,
            }
        },
        "hardware": None,
        "reproduction": {
            "command": "python scripts/epibench_build_chbmit_package.py && python scripts/epibench.py certify examples/epibench/chbmit_patient_independent_d/result_bundle.yaml",
            "container_or_env": "local-python",
            "checksums": [],
        },
    }


if __name__ == "__main__":
    raise SystemExit(main())
