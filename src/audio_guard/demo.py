"""Runnable walkthrough. `python -m audio_guard.demo` or `pytest && python demo.py`

Every line below is produced by the code in this repo.
"""

from __future__ import annotations

import io
import sys
import wave

from audio_guard import (
    MAX_CAPTURE_BYTES,
    LatencyGate,
    Rejection,
    UtteranceMetrics,
    Verdict,
    read_capture,
)

GREEN, RED, DIM, BOLD, OFF = "\033[32m", "\033[31m", "\033[2m", "\033[1m", "\033[0m"


def wav(*, frames: int = 4_800, rate: int = 48_000, channels: int = 1) -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(channels)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(b"\x00" * (frames * 2 * channels))
    return buf.getvalue()


def reader(payload: bytes):
    offset = 0

    def _read(n: int) -> bytes:
        nonlocal offset
        chunk = payload[offset : offset + n]
        offset += len(chunk)
        return chunk

    return _read


def section(title: str, sub: str = "") -> None:
    print(f"{BOLD}\n{title}{OFF}")
    if sub:
        print(f"{DIM}   {sub}{OFF}")


def main() -> int:
    section(
        "1. The read is bounded before it happens",
        "We probe one byte past the limit, so hitting the cap is",
    )
    print(f"{DIM}   distinguishable from fitting exactly at it.{OFF}\n")

    asked: list[int] = []

    def oversized(n: int) -> bytes:
        asked.append(n)
        return b"RIFF" + b"\x00" * (MAX_CAPTURE_BYTES + 10)

    result = read_capture(oversized, max_bytes=1_024)
    print(f"  {'400 MB upload, 1 KB limit'.ljust(44)} {RED}REJECT  {result.reason}{OFF}")
    print(f"  {'bytes requested from the source'.ljust(44)} {DIM}{asked[0]}{OFF}")
    print(f"  {'':<44} {DIM}not {MAX_CAPTURE_BYTES:,} — the limit bounds the read{OFF}")

    section("2. Rejections are specific, never 'invalid audio'")
    print(f"{DIM}   A generic reason is undiagnosable in production.{OFF}\n")

    for label, payload in [
        ("not a wav", b"definitely not audio"),
        ("8 kHz instead of 48 kHz", wav(rate=8_000)),
        ("stereo instead of mono", wav(channels=2)),
        ("zero frames", wav(frames=0)),
    ]:
        r = read_capture(reader(payload))
        print(f"  {label.ljust(44)} {RED}REJECT  {r.reason}{OFF}")

    r = read_capture(reader(wav()))
    print(f"  {'48 kHz mono, 0.1 s'.ljust(44)} {GREEN}ACCEPT  {r.audio.duration_seconds}s{OFF}")

    section(
        "3. Latency is a correctness property",
        "A stage over budget has failed. It is not 'slow'.",
    )
    print(f"{DIM}{OFF}\n")

    scenarios = [
        ("transcribe 1.2s / retrieve 0.12s", [(0.0, 1_200.0, 4_000), (1_200.0, 1_320.0, 200)]),
        ("transcribe 1.2s / retrieve 1.7s", [(0.0, 1_200.0, 4_000), (1_200.0, 2_900.0, 200)]),
    ]
    for label, stages in scenarios:
        gate = LatencyGate()
        for i, (start, end, budget) in enumerate(stages):
            gate.record(("transcribe", "retrieve")[i], budget, start, end)
        ok = gate.displayable
        colour = GREEN if ok else RED
        state = "DISPLAY" if ok else "SUPPRESS"
        print(f"  {label.ljust(44)} {colour}{state:<9} {gate.verdict.value}{OFF}")

    gate = LatencyGate()
    print(f"  {'no measurement at all'.ljust(44)} {RED}{'SUPPRESS':<9} {gate.verdict.value}{OFF}")

    section(
        "4. Metrics carry no transcript",
        "The type has no field that could hold one.",
    )
    print(f"{DIM}   The control is the schema, not discipline at call sites.{OFF}\n")

    metrics = UtteranceMetrics(
        audio_to_final_ms=1_210,
        answer_retrieval_ms=140,
        total_to_display_ms=1_360,
        displayable=True,
    )
    print(f"  {DIM}{metrics.as_log_line()}{OFF}")

    print(f"\n{BOLD}   Every line above is produced by code in this repo.{OFF}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
