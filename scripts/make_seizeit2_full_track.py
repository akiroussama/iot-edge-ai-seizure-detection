#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.reports.seizeit2_benchmark_track import (  # noqa: E402
    build_seizeit2_full_track_matrix,
    seizeit2_count_summary,
    seizeit2_full_track_markdown,
)
from src.utils.io import read_table, write_table  # noqa: E402


def _parse_match_columns(value: str) -> tuple[str, ...]:
    columns = tuple(column.strip() for column in value.split(",") if column.strip())
    if not columns:
        raise argparse.ArgumentTypeError("--split-match-columns cannot be empty")
    return columns


def _read_expected_counts(path: str | None) -> dict[str, int] | None:
    if path is None:
        return None
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return {str(key): int(value) for key, value in payload.items()}


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build SeizeIT2 full-benchmark track readiness tables."
    )
    parser.add_argument("--recordings", required=True)
    parser.add_argument("--events", required=True)
    parser.add_argument("--modality-availability", required=True)
    parser.add_argument("--windows", default=None)
    parser.add_argument("--official-splits", default=None)
    parser.add_argument(
        "--split-match-columns",
        type=_parse_match_columns,
        default=("patient_id", "recording_id"),
    )
    parser.add_argument("--expected-counts-json", default=None)
    parser.add_argument("--out-csv", required=True)
    parser.add_argument("--out-counts-csv", required=True)
    parser.add_argument("--out-md", required=True)
    parser.add_argument(
        "--result-status",
        choices=[
            "pre_gate_c_exploratory_not_citable",
            "gate_c_frozen_citable",
            "synthetic_smoke_test_not_citable",
        ],
        default="pre_gate_c_exploratory_not_citable",
    )
    parser.add_argument(
        "--citation-status",
        choices=["not_citable_pre_gate_c", "citable_after_gate_c", "synthetic_not_citable"],
        default="not_citable_pre_gate_c",
    )
    parser.add_argument(
        "--gate-c-status",
        choices=["not_started", "partial", "passed", "failed"],
        default="not_started",
    )
    parser.add_argument("--title", default="SeizeIT2 Full-Benchmark Track")
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    if args.citation_status == "citable_after_gate_c" and args.gate_c_status != "passed":
        raise SystemExit("citable SeizeIT2 full-track reports require --gate-c-status passed")

    recordings = read_table(args.recordings)
    events = read_table(args.events)
    availability = read_table(args.modality_availability)
    windows = read_table(args.windows) if args.windows else None
    splits = read_table(args.official_splits) if args.official_splits else None
    expected_counts = _read_expected_counts(args.expected_counts_json)

    track = build_seizeit2_full_track_matrix(
        recordings,
        events,
        availability,
        windows_df=windows,
        official_splits_df=splits,
        split_match_columns=args.split_match_columns,
        result_status=args.result_status,
        citation_status=args.citation_status,
        gate_c_status=args.gate_c_status,
    )
    counts = seizeit2_count_summary(
        recordings,
        events,
        availability,
        windows_df=windows,
        expected_counts=expected_counts,
    )
    write_table(track, args.out_csv)
    write_table(counts, args.out_counts_csv)
    out_md = Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(
        seizeit2_full_track_markdown(track, counts, title=args.title),
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "out_csv": args.out_csv,
                "out_counts_csv": args.out_counts_csv,
                "out_md": args.out_md,
                "rows": int(len(track)),
                "ready_rows": int(track["track_ready"].sum()) if not track.empty else 0,
                "official_splits": args.official_splits is not None,
                "citation_status": args.citation_status,
                "gate_c_status": args.gate_c_status,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
