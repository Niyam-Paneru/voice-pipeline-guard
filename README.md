# Voice Pipeline Guard

A Python implementation of two realtime voice boundaries: **bound capture before accepting it**, and **suppress output when timing evidence is missing or over budget**.

This public repo uses synthetic WAV inputs only. It does **not** include a live provider, microphone stream, transcript pipeline, credentials, or deployment integration.

## Run / verify

```bash
python -m compileall -q src
python -m pytest
PYTHONPATH=src python -m audio_guard.demo
```

![Data and timing pipeline](docs/workflow.svg)

## What is enforced

1. **Capture/input validation** — `read_capture()` requests a bounded probe, rejects oversized input, and validates the WAV contract before returning `CapturedAudio`.
2. **Processing/timing completeness** — callers record stage start/completion times and budgets in `LatencyGate`.
3. **Display eligibility** — no stages, missing/invalid completion time, or any over-budget stage makes `displayable == False`; only `WITHIN_BUDGET` may display.
4. **Metadata-only logging boundary** — `UtteranceMetrics` can carry timing/drop/display metadata, but its schema has no transcript, answer text, or audio-bytes field.

Capture rejection reasons include `too_large`, `not_a_wav`, unsupported WAV properties, `empty`, `truncated`, and `too_long`. The tests exercise the capture, timing, and telemetry boundaries directly.

## Review the implementation

- [`src/audio_guard/capture.py`](src/audio_guard/capture.py) — bounded read + WAV validation
- [`src/audio_guard/latency.py`](src/audio_guard/latency.py) — stage timing + display verdict
- [`src/audio_guard/metrics.py`](src/audio_guard/metrics.py) — metadata-only log schema
- [`tests/`](tests/) — failure-path and privacy checks
- [`docs/latency-contract.md`](docs/latency-contract.md) — verdict contract

## Scope

The code demonstrates guard behavior under synthetic inputs. It does not claim production latency, call quality, provider uptime, or current deployment. See [`PROVENANCE.md`](PROVENANCE.md) and [`SECURITY.md`](SECURITY.md) for the public/private boundary.
