from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class UtteranceMetrics:
    audio_to_final_ms: int | None
    answer_retrieval_ms: int | None
    total_to_display_ms: int | None
    displayable: bool
    dropped_audio_seconds: float = 0.0

    def as_log_line(self) -> str:
        return (
            f"audio_to_final_ms={self.audio_to_final_ms} "
            f"answer_retrieval_ms={self.answer_retrieval_ms} "
            f"total_to_display_ms={self.total_to_display_ms} "
            f"displayable={str(self.displayable).lower()} "
            f"dropped_audio_seconds={self.dropped_audio_seconds}"
        )
