from __future__ import annotations

import io
import wave

from .models import (
    CHANNELS,
    MAX_CAPTURE_BYTES,
    MAX_CAPTURE_SECONDS,
    SAMPLE_RATE_HZ,
    SAMPLE_WIDTH_BYTES,
    CapturedAudio,
    CaptureResult,
    Rejection,
)


def read_capture(
    read,
    *,
    max_bytes: int = MAX_CAPTURE_BYTES,
    max_seconds: int = MAX_CAPTURE_SECONDS,
) -> CaptureResult:
    probe = read(max_bytes + 1)
    if len(probe) > max_bytes:
        return CaptureResult(accepted=False, rejection=Rejection.TOO_LARGE)

    if len(probe) < 12 or probe[:4] != b"RIFF" or probe[8:12] != b"WAVE":
        return CaptureResult(accepted=False, rejection=Rejection.NOT_A_WAV, bytes_read=len(probe))

    try:
        with wave.open(io.BytesIO(probe), "rb") as reader:
            if reader.getcomptype() != "NONE":
                return CaptureResult(False, Rejection.COMPRESSED, bytes_read=len(probe))
            if reader.getnchannels() != CHANNELS:
                return CaptureResult(False, Rejection.WRONG_CHANNEL_COUNT, bytes_read=len(probe))
            if reader.getsampwidth() != SAMPLE_WIDTH_BYTES:
                return CaptureResult(False, Rejection.WRONG_SAMPLE_WIDTH, bytes_read=len(probe))
            if reader.getframerate() != SAMPLE_RATE_HZ:
                return CaptureResult(False, Rejection.WRONG_SAMPLE_RATE, bytes_read=len(probe))

            frames = reader.getnframes()
            if frames <= 0:
                return CaptureResult(False, Rejection.EMPTY, bytes_read=len(probe))
            if frames / reader.getframerate() > max_seconds:
                return CaptureResult(False, Rejection.TOO_LONG, bytes_read=len(probe))

            pcm = reader.readframes(frames)
    except (EOFError, OSError, wave.Error):
        return CaptureResult(False, Rejection.NOT_A_WAV, bytes_read=len(probe))

    if len(pcm) != frames * SAMPLE_WIDTH_BYTES:
        return CaptureResult(False, Rejection.TRUNCATED, bytes_read=len(probe))

    return CaptureResult(
        accepted=True,
        audio=CapturedAudio(
            pcm=pcm,
            sample_rate_hz=SAMPLE_RATE_HZ,
            duration_seconds=round(frames / SAMPLE_RATE_HZ, 3),
        ),
        bytes_read=len(probe),
    )
