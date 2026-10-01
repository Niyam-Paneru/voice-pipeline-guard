from __future__ import annotations

from dataclasses import dataclass, field

from .models import Verdict


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
        if any(stage.elapsed_ms is None for stage in self.stages):
            return Verdict.INCOMPLETE
        if any(stage.elapsed_ms > stage.budget_ms for stage in self.stages):
            return Verdict.EXCEEDED_BUDGET
        return Verdict.WITHIN_BUDGET

    @property
    def displayable(self) -> bool:
        return self.verdict is Verdict.WITHIN_BUDGET

    def report(self) -> list[tuple[str, int | None, int, bool]]:
        return [
            (stage.name, stage.elapsed_ms, stage.budget_ms, (stage.elapsed_ms or 0) <= stage.budget_ms)
            for stage in self.stages
        ]
