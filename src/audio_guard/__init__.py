"""Bounded audio capture, fail-closed latency, and metadata-only metrics."""

from .capture import read_capture
from .latency import LatencyGate, Stage
from .metrics import UtteranceMetrics
from .models import (
    CHANNELS,
    MAX_CAPTURE_BYTES,
    MAX_CAPTURE_SECONDS,
    SAMPLE_RATE_HZ,
    SAMPLE_WIDTH_BYTES,
    CapturedAudio,
    CaptureResult,
    Rejection,
    Verdict,
)

__all__ = [
    "CHANNELS",
    "MAX_CAPTURE_BYTES",
    "MAX_CAPTURE_SECONDS",
    "SAMPLE_RATE_HZ",
    "SAMPLE_WIDTH_BYTES",
    "CapturedAudio",
    "CaptureResult",
    "LatencyGate",
    "Rejection",
    "Stage",
    "UtteranceMetrics",
    "Verdict",
    "read_capture",
]
