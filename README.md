# Voice Pipeline Guard

A voice assistant that takes forever to answer has become a very expensive voicemail.

This Python module handles two unglamorous problems from realtime audio work: **don't accept malformed/oversized recordings**, and **don't present an answer if the timing evidence says it was late or never finished**.

## Two doors the audio has to get through

**Door one — capture.** `read_capture()` reads only up to the configured size limit (plus a probe byte), then checks WAV structure, format, and duration. The input is either acceptable or it isn't; we don't pretend a truncated file is fine.

**Door two — timing.** A `LatencyGate` records stage timing. Missing or invalid completion times produce `INCOMPLETE`; a stage over budget produces `EXCEEDED_BUDGET`; complete, in-budget evidence produces `WITHIN_BUDGET`.

Only the last case is eligible to display. "Probably fast enough" is not a timing measurement.

`UtteranceMetrics` intentionally contains timing/drop/display metadata — **no transcript text or audio bytes**.

## What gets through

Audio has to survive the first check before the rest of the pipeline should touch it.

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

A complete processing record still has to meet the time budget.

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

See [capture.py](src/audio_guard/capture.py), [latency.py](src/audio_guard/latency.py), [the tests](tests/), and [the latency contract](docs/latency-contract.md).

### A reality check

There is no microphone, telephony provider, transport, live transcript, or production latency claim in this repository. It's a runnable guard, not an end-to-end voice assistant. The audio is synthetic, which is convenient because it doesn't complain when the tests fail. [Verification](docs/verification.md) · [Provenance](PROVENANCE.md).
