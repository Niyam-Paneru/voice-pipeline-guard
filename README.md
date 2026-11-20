# Voice Pipeline Guard

If a voice assistant takes forever to answer “hello,” the conversation has probably moved on. An expensive voicemail is still voicemail.

This Python module guards two parts of realtime audio work: **input quality** and **timing evidence**. It does not make a slow response fast. It makes it harder to call a slow or unfinished response successful.

## Two checks, two different failure modes

| Check | Pass | Fail |
| --- | --- | --- |
| **Capture** | WAV structure, format, duration and size are within configured bounds | Reject malformed, oversized or truncated input |
| **Timing** | Every required stage completed within its budget | Suppress incomplete or over-budget output |

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

A good answer arriving after the conversation ends is still a bad conversation. [Verification](docs/verification.md) · [provenance](PROVENANCE.md).
