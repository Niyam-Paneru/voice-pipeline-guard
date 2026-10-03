# Voice Pipeline Guard

A Python implementation of two realtime voice boundaries: **bound capture before accepting it**, and **suppress output when timing evidence is missing or over budget**.

**In realtime systems, “eventually” is a suspiciously expensive word.**

This is a **public sample from my private voice-system work**. The sample uses synthetic WAV inputs to make the guards easy to inspect. I can build and adapt the surrounding voice pipelines and provider integrations; live audio, transcripts, credentials, and deployment plumbing stay private.

## Capture: accept only valid, bounded audio

```mermaid
---
config:
  flowchart:
    curve: linear
    nodeSpacing: 28
    rankSpacing: 42
---
flowchart TB
    accTitle: Capture: accept only valid, bounded audio
    accDescr: Decision flow for capture: accept only valid, bounded audio.
    A["Bounded read<br/>max_bytes + 1"] --> B{"Oversized?"}
    B -- Yes --> R["Reject<br/>too_large"]
    B -- No --> C{"Valid WAV?"}
    C -- No --> X["Reject WAV<br/>invalid format or duration"]
    C -- Yes --> D["Accept<br/>CapturedAudio"]
    classDef input stroke-width:1.5px;
    classDef pass stroke-width:2.5px;
    classDef stop stroke-width:2px,stroke-dasharray:5 3;
    class A,B,C input;
    class D pass;
    class R,X stop;
```

## Timing: decide whether output may display

Callers record timing separately from capture. A complete verdict requires at least one stage with valid start and completion times.

```mermaid
---
config:
  flowchart:
    curve: linear
    nodeSpacing: 28
    rankSpacing: 42
---
flowchart TB
    accTitle: Timing: decide whether output may display
    accDescr: Decision flow for timing: decide whether output may display.
    E["Stage timings<br/>start, end, budget"] --> F{"Complete?"}
    F -- No --> S["Suppress<br/>INCOMPLETE"]
    F -- Yes --> G{"In budget?"}
    G -- No --> L["Suppress<br/>EXCEEDED_BUDGET"]
    G -- Yes --> H["Display eligible<br/>WITHIN_BUDGET"]
    classDef input stroke-width:1.5px;
    classDef pass stroke-width:2.5px;
    classDef stop stroke-width:2px,stroke-dasharray:5 3;
    class E,F,G input;
    class H pass;
    class S,L stop;
```

`UtteranceMetrics` is a separate metadata-only schema: timing, dropped audio, and displayability. It has no transcript, answer-text, or audio-bytes field. These diagrams show the public guards; provider, microphone, transcript, and transport integration belong to the surrounding system.

## What is enforced

1. **Capture/input validation** — `read_capture()` performs a bounded probe, rejects oversized input, then validates the WAV contract before returning `CapturedAudio`.
2. **Processing/timing completeness** — callers record stage start/completion times and budgets in `LatencyGate`.
3. **Display eligibility** — no stages, missing/invalid completion time, or any over-budget stage makes `displayable == False`; only `WITHIN_BUDGET` may display.
4. **Metadata-only boundary** — `UtteranceMetrics` has fields for timing, dropped audio, and displayability; it has no transcript, answer-text, or audio-bytes field.

Capture rejection reasons include `too_large`, `not_a_wav`, unsupported WAV properties, `empty`, `truncated`, and `too_long`.

## Review the implementation

- [`src/audio_guard/capture.py`](src/audio_guard/capture.py) — bounded read + WAV validation
- [`src/audio_guard/latency.py`](src/audio_guard/latency.py) — stage timing + display verdict
- [`src/audio_guard/metrics.py`](src/audio_guard/metrics.py) — metadata-only schema
- [`tests/`](tests/) — failure-path and privacy checks
- [`docs/latency-contract.md`](docs/latency-contract.md) — verdict contract

## Evidence and scope

CircleCI is configured to compile the public source, run the behavior tests, and execute the synthetic walkthrough. Exact local commands and expected checks: [docs/verification.md](docs/verification.md).

The code demonstrates guard behavior under synthetic inputs. It does not claim production latency, call quality, provider uptime, live audio wiring, or current deployment. See [`PROVENANCE.md`](PROVENANCE.md) and [`SECURITY.md`](SECURITY.md) for the public/private boundary.
