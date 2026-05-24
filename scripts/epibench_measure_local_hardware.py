from __future__ import annotations

import argparse
import csv
import json
import os
import platform
import sys
import time
import tracemalloc
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
FEATURES_PATH = REPO_ROOT / "data" / "processed" / "chbmit_waveform_micro" / "window_features.csv"
METRICS_PATH = REPO_ROOT / "reports" / "chbmit_waveform_micro_metrics.json"
OUT_DIR = REPO_ROOT / "reports" / "epibench_hardware_measurement"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Measure local reference CPU latency for the CHB-MIT waveform micro threshold baseline."
    )
    parser.add_argument("--features", type=Path, default=FEATURES_PATH)
    parser.add_argument("--metrics", type=Path, default=METRICS_PATH)
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    parser.add_argument("--repeat", type=int, default=200)
    args = parser.parse_args()

    report = build_local_hardware_report(
        features_path=args.features,
        metrics_path=args.metrics,
        out_dir=args.out_dir,
        repeat=args.repeat,
    )
    print(
        "Measured local reference CPU latency: "
        f"batch p95 {report['latency']['batch_latency_ms_p95']:.6f} ms, "
        f"per-window p95 {report['latency']['per_window_latency_us_p95']:.6f} us"
    )
    return 0


def build_local_hardware_report(
    *,
    features_path: Path = FEATURES_PATH,
    metrics_path: Path = METRICS_PATH,
    out_dir: Path = OUT_DIR,
    repeat: int = 200,
) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    values = _load_feature_values(features_path)
    threshold = _load_threshold(metrics_path)
    if not values:
        raise ValueError(f"No feature rows found in {features_path}")
    if repeat < 10:
        raise ValueError("repeat must be at least 10 for a meaningful p95 estimate")

    tracemalloc.start()
    latencies_ms = []
    prediction_count = 0
    for _ in range(repeat):
        start = time.perf_counter_ns()
        predictions = _predict_threshold(values, threshold)
        end = time.perf_counter_ns()
        prediction_count += len(predictions)
        latencies_ms.append((end - start) / 1_000_000)
    _, peak_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    batch_p95 = _percentile(latencies_ms, 95)
    batch_median = _percentile(latencies_ms, 50)
    per_window_latencies_us = [latency / len(values) * 1000 for latency in latencies_ms]
    report = {
        "schema_version": "epibench.local_hardware_report.v1",
        "created_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "measurement_scope": "local_reference_cpu_threshold_inference_only",
        "edge_claim_authorized": False,
        "target_hardware_claim": "not_authorized_without_target_iot_device_measurement",
        "input": {
            "features_path": str(features_path),
            "metrics_path": str(metrics_path),
            "feature_column": "robust_z",
            "window_count_per_batch": len(values),
            "repeat": repeat,
            "threshold": threshold,
        },
        "hardware": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "processor": platform.processor() or "unknown",
            "python": sys.version.split()[0],
            "cpu_count": os.cpu_count(),
        },
        "latency": {
            "batch_latency_ms_median": round(batch_median, 6),
            "batch_latency_ms_p95": round(batch_p95, 6),
            "per_window_latency_us_median": round(_percentile(per_window_latencies_us, 50), 6),
            "per_window_latency_us_p95": round(_percentile(per_window_latencies_us, 95), 6),
            "predictions_per_second_median": round(len(values) / (batch_median / 1000), 3)
            if batch_median > 0
            else None,
        },
        "memory": {
            "python_tracemalloc_peak_kb": round(peak_bytes / 1024, 3),
            "ram_claim_scope": "python_process_peak_during_threshold_loop_not_full_device_ram",
        },
        "energy": {
            "measured": False,
            "energy_mj_per_inference": None,
            "reason": "No target power monitor or IoT board was available in this run.",
        },
        "claim_boundary": (
            "This is a real local CPU timing measurement for a tiny threshold inference loop. "
            "It does not authorize real-time, edge-ready, battery-life, or medical-device deployment claims."
        ),
        "prediction_count": prediction_count,
    }
    _write_json(out_dir / "local_hardware_report.json", report)
    _write_csv(out_dir / "latency_samples.csv", [{"iteration": i, "batch_latency_ms": value} for i, value in enumerate(latencies_ms)])
    (out_dir / "README.md").write_text(_render_markdown(report), encoding="utf-8")
    return report


def _load_feature_values(path: Path) -> list[float]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return [float(row["robust_z"]) for row in reader]


def _load_threshold(path: Path) -> float:
    data = json.loads(path.read_text(encoding="utf-8"))
    return float(data["threshold"])


def _predict_threshold(values: list[float], threshold: float) -> list[int]:
    return [1 if value >= threshold else 0 for value in values]


def _percentile(values: list[float], percentile: float) -> float:
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * percentile / 100
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _render_markdown(report: dict[str, Any]) -> str:
    return f"""# EpiBench Local Hardware Measurement

Status: real local reference CPU measurement; not target IoT hardware evidence.

## Scope

- measurement scope: `{report['measurement_scope']}`;
- edge claim authorized: `{report['edge_claim_authorized']}`;
- target hardware claim: `{report['target_hardware_claim']}`;
- window count per batch: `{report['input']['window_count_per_batch']}`;
- repeats: `{report['input']['repeat']}`.

## Measured Latency

- batch median latency: `{report['latency']['batch_latency_ms_median']}` ms;
- batch p95 latency: `{report['latency']['batch_latency_ms_p95']}` ms;
- per-window median latency: `{report['latency']['per_window_latency_us_median']}` us;
- per-window p95 latency: `{report['latency']['per_window_latency_us_p95']}` us.

## Memory And Energy

- Python traced peak memory: `{report['memory']['python_tracemalloc_peak_kb']}` KB;
- energy measured: `{report['energy']['measured']}`;
- energy reason: {report['energy']['reason']}

## Claim Boundary

{report['claim_boundary']}
"""


if __name__ == "__main__":
    raise SystemExit(main())
