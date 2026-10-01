from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Final

SAMPLE_RATE_HZ: Final = 48_000
CHANNELS: Final = 1
SAMPLE_WIDTH_BYTES: Final = 2
MAX_CAPTURE_BYTES: Final = 25 * 1024 * 1024
MAX_CAPTURE_SECONDS: Final = 15


class Rejection(str, Enum):
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
