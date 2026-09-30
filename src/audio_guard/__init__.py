"""Bounded capture and validation for realtime audio pipelines.

A realtime transcription pipeline has a failure mode that unit tests do not
catch: everything works, but slowly. The transcript is correct, the answer is
correct, and the user has already given up.

So this module treats *timing* as a correctness property rather than a
performance metric. A stage that overruns its budget is not "slow". It has
failed, and the pipeline must say so rather than pass a stale result forward.

The second idea is that a capture boundary has to be enforced before the read,
not after. Reading a 400 MB upload in order to discover it is over the limit is
the bug this prevents.
"""

from __future__ import annotations

import io
import wave
from dataclasses import dataclass, field
from enum import Enum
from typing import Final

SAMPLE_RATE_HZ: Final = 48_000
CHANNELS: Final = 1
SAMPLE_WIDTH_BYTES: Final = 2
MAX_CAPTURE_BYTES: Final = 25 * 1024 * 1024
MAX_CAPTURE_SECONDS: Final = 15


class Rejection(str, Enum):
    """Why a capture was refused. Every rejection names a specific reason."""

    TOO_LARGE = "too_large"
    NOT_A_WAV = "not_a_wav"
    WRONG_SAMPLE_RATE = "wrong_sample_rate"
    WRONG_CHANNEL_COUNT = "wrong_channel_count"
    WRONG_SAMPLE_WIDTH = "wrong_sample_width"
    EMPTY = "empty"
    COMPRESSED = "compressed"
    TRUNCATED = "truncated"
    TOO_LONG = "too_long"


class Verdict(str, Enum):
    """Outcome of a latency gate."""

    WITHIN_BUDGET = "within_budget"
    EXCEEDED_BUDGET = "exceeded_budget"
    INCOMPLETE = "incomplete"


@dataclass(frozen=True, slots=True)
class CapturedAudio:
    pcm: bytes
    sample_rate_hz: int
    duration_seconds: float


@dataclass(frozen=True, slots=True)
class CaptureResult:
    accepted: bool
    rejection: Rejection | None = None
    audio: CapturedAudio | None = None
    bytes_read: int = 0

    @property
    def reason(self) -> str:
        return self.rejection.value if self.rejection else "accepted"


def read_capture(
    read: "callable[[int], bytes]",
    *,
    max_bytes: int = MAX_CAPTURE_BYTES,
    max_seconds: int = MAX_CAPTURE_SECONDS,
) -> CaptureResult:
    """Accept a WAV only after validating it, and never read more than allowed.

    `read(n)` returns up to the first `n` bytes. We deliberately request
    `max_bytes + 1` so that hitting the limit is distinguishable from fitting
    exactly at the limit, without ever materialising an oversized buffer.
    """
    probe = read(max_bytes + 1)
    if len(probe) > max_bytes:
        return CaptureResult(accepted=False, rejection=Rejection.TOO_LARGE)

    if len(probe) < 12 or probe[:4] != b"RIFF" or probe[8:12] != b"WAVE":
        return CaptureResult(accepted=False, rejection=Rejection.NOT_A_WAV, bytes_read=len(probe))

    try:
        with wave.open(io.BytesIO(probe), "rb") as reader:
            if reader.getcomptype() != "NONE":
                return CaptureResult(
                    accepted=False, rejection=Rejection.COMPRESSED, bytes_read=len(probe)
                )
            if reader.getnchannels() != CHANNELS:
                return CaptureResult(
                    accepted=False,
                    rejection=Rejection.WRONG_CHANNEL_COUNT,
                    bytes_read=len(probe),
                )
            if reader.getsampwidth() != SAMPLE_WIDTH_BYTES:
                return CaptureResult(
                    accepted=False,
                    rejection=Rejection.WRONG_SAMPLE_WIDTH,
                    bytes_read=len(probe),
                )
            if reader.getframerate() != SAMPLE_RATE_HZ:
                return CaptureResult(
                    accepted=False,
                    rejection=Rejection.WRONG_SAMPLE_RATE,
                    bytes_read=len(probe),
                )
            frames = reader.getnframes()
            if frames <= 0:
                return CaptureResult(
                    accepted=False, rejection=Rejection.EMPTY, bytes_read=len(probe)
                )
            if frames / reader.getframerate() > max_seconds:
                return CaptureResult(
                    accepted=False, rejection=Rejection.TOO_LONG, bytes_read=len(probe)
                )
            pcm = reader.readframes(frames)
    except (EOFError, OSError, wave.Error):
        return CaptureResult(accepted=False, rejection=Rejection.NOT_A_WAV, bytes_read=len(probe))

    # A WAV header can promise frames the body does not contain.
    if len(pcm) != frames * SAMPLE_WIDTH_BYTES:
        return CaptureResult(
            accepted=False, rejection=Rejection.TRUNCATED, bytes_read=len(probe)
        )

    return CaptureResult(
        accepted=True,
        audio=CapturedAudio(
            pcm=pcm,
            sample_rate_hz=SAMPLE_RATE_HZ,
            duration_seconds=round(frames / SAMPLE_RATE_HZ, 3),
        ),
        bytes_read=len(probe),
    )


@dataclass(frozen=True, slots=True)
class Stage:
    name: str
    budget_ms: int
    started_at_ms: float
    completed_at_ms: float | None = None

    @property
    def elapsed_ms(self) -> int | None:
        if self.completed_at_ms is None or self.completed_at_ms < self.started_at_ms:
            return None
        return round(self.completed_at_ms - self.started_at_ms)


@dataclass
class LatencyGate:
    """Fails closed.

    A pipeline that cannot account for every stage of its own latency is not
    allowed to report a result. `UNKNOWN` is a failure, not a pass.
    """

    stages: list[Stage] = field(default_factory=list)

    def record(
        self,
        name: str,
        budget_ms: int,
        started_at_ms: float,
        completed_at_ms: float | None = None,
    ) -> None:
        """Record a stage.

        `completed_at_ms` is optional on purpose. A stage that started and never
        reported completion is a real state -- the worker died, the socket
        closed, the user hung up. Making it representable is what lets the gate
        treat it as a failure instead of silently omitting it.
        """
        self.stages.append(
            Stage(
                name=name,
                budget_ms=budget_ms,
                started_at_ms=started_at_ms,
                completed_at_ms=completed_at_ms,
            )
        )

    @property
    def verdict(self) -> Verdict:
        if not self.stages:
            return Verdict.INCOMPLETE
        if any(s.elapsed_ms is None for s in self.stages):
            return Verdict.INCOMPLETE
        if any(s.elapsed_ms > s.budget_ms for s in self.stages):
            return Verdict.EXCEEDED_BUDGET
        return Verdict.WITHIN_BUDGET

    @property
    def displayable(self) -> bool:
        """The single question the UI asks."""
        return self.verdict is Verdict.WITHIN_BUDGET

    def report(self) -> list[tuple[str, int | None, int, bool]]:
        return [
            (s.name, s.elapsed_ms, s.budget_ms, (s.elapsed_ms or 0) <= s.budget_ms)
            for s in self.stages
        ]


@dataclass(frozen=True, slots=True)
class UtteranceMetrics:
    """Metadata only.

    Durations and counts are safe to log. Transcript text, question text, and
    anything derived from them are not, and this object has no field that could
    hold them. That is the point: the type makes the leak unrepresentable
    instead of relying on discipline at each call site.
    """

    audio_to_final_ms: int | None
    answer_retrieval_ms: int | None
    total_to_display_ms: int | None
    displayable: bool
    dropped_audio_seconds: float = 0.0

    def as_log_line(self) -> str:
        # Explicit allowlist. Anything not named here cannot be logged.
        return (
            f"audio_to_final_ms={self.audio_to_final_ms} "
            f"answer_retrieval_ms={self.answer_retrieval_ms} "
            f"total_to_display_ms={self.total_to_display_ms} "
            f"displayable={str(self.displayable).lower()} "
            f"dropped_audio_seconds={self.dropped_audio_seconds}"
        )
