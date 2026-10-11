from __future__ import annotations

from dataclasses import dataclass, field
from math import isfinite

from .models import Verdict


@dataclass(frozen=True, slots=True)
class Stage:
    name: str
    budget_ms: int
    started_at_ms: float
    completed_at_ms: float | None = None

    @property
    def elapsed_ms(self) -> float | None:
        # Never round before comparing to a hard latency budget: 100.4 > 100.
        if self.completed_at_ms is None:
            return None
        try:
            if not isfinite(self.started_at_ms) or not isfinite(self.completed_at_ms):
                return None
            elapsed = self.completed_at_ms - self.started_at_ms
            if not isfinite(elapsed) or elapsed < 0:
                return None
            return elapsed
        except (TypeError, ValueError, OverflowError):
            return None

    @property
    def budget_is_valid(self) -> bool:
        return (
            isinstance(self.budget_ms, (int, float))
            and not isinstance(self.budget_ms, bool)
            and self.budget_ms >= 0
            and (not isinstance(self.budget_ms, float) or isfinite(self.budget_ms))
        )


@dataclass
class LatencyGate:
    stages: list[Stage] = field(default_factory=list)

    def record(
        self,
        name: str,
        budget_ms: int,
        started_at_ms: float,
        completed_at_ms: float | None = None,
    ) -> None:
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
        if any(not stage.budget_is_valid or stage.elapsed_ms is None for stage in self.stages):
            return Verdict.INCOMPLETE
        if any(stage.elapsed_ms > stage.budget_ms for stage in self.stages):
            return Verdict.EXCEEDED_BUDGET
        return Verdict.WITHIN_BUDGET

    @property
    def displayable(self) -> bool:
        return self.verdict is Verdict.WITHIN_BUDGET

    def report(self) -> list[tuple[str, float | None, int, bool]]:
        return [
            (
                stage.name,
                stage.elapsed_ms,
                stage.budget_ms,
                stage.budget_is_valid
                and stage.elapsed_ms is not None
                and stage.elapsed_ms <= stage.budget_ms,
            )
            for stage in self.stages
        ]
