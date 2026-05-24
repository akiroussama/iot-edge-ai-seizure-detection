# SzCORE Bridge Demo

This example is a compatibility demonstration. It does not reimplement SzCORE.

It maps an already-produced SzCORE-style event-scoring export into an EpiBench Result Bundle:

```powershell
python scripts\epibench.py map-szcore --metrics examples\epibench\szcore_bridge_demo\szcore_event_metrics.yaml --base-bundle examples\epibench\pilot_t1_eeg\result_bundle.yaml --out examples\epibench\szcore_bridge_demo\result_bundle.yaml
python scripts\epibench.py certify examples\epibench\szcore_bridge_demo\result_bundle.yaml
```

EpiBench then adds dataset tiering, split validity, failure trace handling, badges, and claim gates around the mapped event metrics.
