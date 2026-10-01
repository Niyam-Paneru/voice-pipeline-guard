from __future__ import annotations

import io
import wave

from audio_guard import (
    MAX_CAPTURE_BYTES,
    SAMPLE_RATE_HZ,
    LatencyGate,
    Rejection,
    UtteranceMetrics,
    Verdict,
    read_capture,
)


def build_wav(
    *,
    frames: int = 4_800,
    rate: int = SAMPLE_RATE_HZ,
    channels: int = 1,
    width: int = 2,
    comptype: str = "NONE",
) -> bytes:
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as writer:
        writer.setnchannels(channels)
        writer.setsampwidth(width)
        writer.setframerate(rate)
        writer.writeframes(b"\x00" * (frames * width * channels))
    data = buffer.getvalue()
    if comptype != "NONE":
        # wave cannot write compressed PCM; patch the format tag.
        data = data[:20] + b"\x01\x00" + data[22:]
    return data


def reader_for(payload: bytes, *, cap: int | None = None):
    available = payload if cap is None else payload[:cap]
    offset = 0

    def _read(n: int) -> bytes:
        nonlocal offset
        chunk = available[offset : offset + n]
        offset += len(chunk)
        return chunk

    return _read


# --- capture validation ----------------------------------------------------


def test_accepts_a_well_formed_capture() -> None:
    payload = build_wav(frames=4_800)
    result = read_capture(reader_for(payload))
    assert result.accepted
    assert result.audio is not None
    assert result.audio.duration_seconds == pytest_approx(0.1)


def pytest_approx(value: float, tol: float = 0.001):
    class _Approx:
        def __eq__(self, other: object) -> bool:
            return abs(float(other) - value) <= tol

    return _Approx()


def test_rejects_oversized_input_without_reading_it() -> None:
    """The limit is enforced by the read call, not after materialising a buffer."""
    asked: list[int] = []

    def read(n: int) -> bytes:
        asked.append(n)
        return b"RIFF" + b"\x00" * (MAX_CAPTURE_BYTES + 10)

    result = read_capture(read, max_bytes=1_024)
    assert not result.accepted
    assert result.rejection is Rejection.TOO_LARGE
    assert asked == [1_025], "must probe exactly one byte past the limit"


def test_accepts_chunked_reader_without_treating_first_chunk_as_the_body() -> None:
    payload = build_wav(frames=4_800)
    offset = 0

    def read(n: int) -> bytes:
        nonlocal offset
        width = min(n, 7)
        chunk = payload[offset : offset + width]
        offset += len(chunk)
        return chunk

    result = read_capture(read)
    assert result.accepted
    assert result.audio is not None


def test_rejects_non_wav() -> None:
    result = read_capture(reader_for(b"this is not audio at all"))
    assert result.rejection is Rejection.NOT_A_WAV


def test_rejects_wrong_sample_rate() -> None:
    result = read_capture(reader_for(build_wav(rate=16_000)))
    assert result.rejection is Rejection.WRONG_SAMPLE_RATE


def test_rejects_stereo() -> None:
    result = read_capture(reader_for(build_wav(channels=2)))
    assert result.rejection is Rejection.WRONG_CHANNEL_COUNT


def test_rejects_a_capture_longer_than_the_bound() -> None:
    # 20 seconds at 48 kHz is inside the byte limit but over the time bound.
    result = read_capture(reader_for(build_wav(frames=48_000 * 20)), max_seconds=15)
    assert result.rejection is Rejection.TOO_LONG


def test_rejects_a_truncated_body() -> None:
    """A header can promise frames the body does not contain."""
    payload = build_wav(frames=4_800)
    truncated = payload[: len(payload) - 800]
    result = read_capture(reader_for(truncated))
    assert result.rejection in {Rejection.TRUNCATED, Rejection.NOT_A_WAV}


def test_rejects_an_empty_capture() -> None:
    result = read_capture(reader_for(build_wav(frames=0)))
    assert result.rejection is Rejection.EMPTY


def test_every_rejection_names_a_specific_reason() -> None:
    """A generic 'invalid audio' would make the failure undiagnosable in production."""
    for payload, expected in [
        (b"nope", Rejection.NOT_A_WAV),
        (build_wav(rate=8_000), Rejection.WRONG_SAMPLE_RATE),
        (build_wav(channels=2), Rejection.WRONG_CHANNEL_COUNT),
        (build_wav(frames=0), Rejection.EMPTY),
    ]:
        assert read_capture(reader_for(payload)).rejection is expected


# --- latency gate ----------------------------------------------------------


def test_gate_passes_when_every_stage_is_inside_budget() -> None:
    gate = LatencyGate()
    gate.record("transcribe", budget_ms=4_000, started_at_ms=0.0, completed_at_ms=1_200.0)
    gate.record("retrieve", budget_ms=200, started_at_ms=1_200.0, completed_at_ms=1_320.0)
    assert gate.verdict is Verdict.WITHIN_BUDGET
    assert gate.displayable


def test_gate_fails_closed_on_a_single_overrun() -> None:
    gate = LatencyGate()
    gate.record("transcribe", budget_ms=4_000, started_at_ms=0.0, completed_at_ms=1_200.0)
    gate.record("retrieve", budget_ms=200, started_at_ms=1_200.0, completed_at_ms=2_900.0)
    assert gate.verdict is Verdict.EXCEEDED_BUDGET
    assert not gate.displayable


def test_an_empty_gate_is_not_a_pass() -> None:
    """No measurement is not a good measurement."""
    gate = LatencyGate()
    assert gate.verdict is Verdict.INCOMPLETE
    assert not gate.displayable


def test_an_unfinished_stage_is_not_a_pass() -> None:
    gate = LatencyGate()
    gate.record("transcribe", budget_ms=4_000, started_at_ms=0.0)
    assert gate.verdict is Verdict.INCOMPLETE
    assert not gate.displayable


def test_report_marks_each_stage() -> None:
    gate = LatencyGate()
    gate.record("fast", budget_ms=500, started_at_ms=0.0, completed_at_ms=100.0)
    gate.record("slow", budget_ms=500, started_at_ms=100.0, completed_at_ms=900.0)
    report = gate.report()
    assert report[0] == ("fast", 100, 500, True)
    assert report[1] == ("slow", 800, 500, False)


# --- metrics ---------------------------------------------------------------


def test_metrics_cannot_carry_transcript_text() -> None:
    """The type is the control. No field exists that could hold a transcript."""
    fields = set(UtteranceMetrics.__dataclass_fields__)
    assert fields == {
        "audio_to_final_ms",
        "answer_retrieval_ms",
        "total_to_display_ms",
        "displayable",
        "dropped_audio_seconds",
    }


def test_log_line_contains_only_allowlisted_keys() -> None:
    metrics = UtteranceMetrics(
        audio_to_final_ms=1_210,
        answer_retrieval_ms=140,
        total_to_display_ms=1_360,
        displayable=True,
    )
    line = metrics.as_log_line()
    assert "audio_to_final_ms=1210" in line
    assert "displayable=true" in line
    for banned in ("transcript", "text", "question", "answer_text", "audio_bytes"):
        assert banned not in line
