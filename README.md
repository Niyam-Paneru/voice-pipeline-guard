# Voice Pipeline Guard

Imagine your AI receptionist finally delivers the perfect answer. The caller left six seconds ago. Congratulations, your microphone just heard a fantastic monologue.

Voice assistants have to deal with two problems before the clever answer matters: **is the audio valid?** and **did the response finish before the moment passed?** This Python module handles those gates. It can't make a slow model faster, but it can stop calling a late response a win.

## Two doors between “hello” and an actual answer

First, reject invalid audio. Then check the timing. A beautiful response that missed its deadline does not get a consolation prize.

```mermaid
flowchart TB
    A["Audio arrives"] --> B{"Valid WAV within limits?"}
    B -- No --> R["Reject capture"]
    B -- Yes --> C["Record processing timings"]
    C --> D{"Complete and within budget?"}
    D -- No --> S["Suppress output"]
    D -- Yes --> P["Eligible to display"]
```

The capture reader takes at most the configured size limit **plus a probe byte**; it doesn't need to swallow a huge upload before noticing it's huge.

The timing gate makes three distinctions:

| Timing result | What it means | Display eligible? |
| --- | --- | --- |
| WITHIN_BUDGET | Complete evidence; stages in budget | Yes |
| EXCEEDED_BUDGET | A stage exceeded its configured limit | No |
| INCOMPLETE | Required completion timing missing or invalid | No |

That last case matters: a missing end timestamp is not proof that the answer was fast.

The [capture code](src/audio_guard/capture.py), [latency gate](src/audio_guard/latency.py), [tests](tests/), and [timing contract](docs/latency-contract.md) are the useful starting points. Metrics include timing/drop/display metadata but deliberately **not audio bytes or transcript text**.

## What it isn't

No microphone, phone number, speech-to-text service, telephony provider, or production latency benchmark is bundled here. The test audio is synthetic, and this is a **guard module**, not an end-to-end voice receptionist.

[Verification](docs/verification.md) · [provenance](PROVENANCE.md).
