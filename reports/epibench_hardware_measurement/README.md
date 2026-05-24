# EpiBench Local Hardware Measurement

Status: real local reference CPU measurement; not target IoT hardware evidence.

## Scope

- measurement scope: `local_reference_cpu_threshold_inference_only`;
- edge claim authorized: `False`;
- target hardware claim: `not_authorized_without_target_iot_device_measurement`;
- window count per batch: `2161`;
- repeats: `200`.

## Measured Latency

- batch median latency: `0.0465` ms;
- batch p95 latency: `0.09432` ms;
- per-window median latency: `0.021518` us;
- per-window p95 latency: `0.043646` us.

## Memory And Energy

- Python traced peak memory: `41.641` KB;
- energy measured: `False`;
- energy reason: No target power monitor or IoT board was available in this run.

## Claim Boundary

This is a real local CPU timing measurement for a tiny threshold inference loop. It does not authorize real-time, edge-ready, battery-life, or medical-device deployment claims.
